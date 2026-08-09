from __future__ import annotations

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass
from functools import lru_cache
from time import perf_counter
from typing import Any, Literal, Protocol

import numpy as np
from numpy.typing import NDArray

from backend.app.config import Settings
from backend.app.graph_store import GraphStore, lexical_score, normalize

SearchMode = Literal["lexical", "semantic", "hybrid"]

LEXICAL_MIN_SCORE = 0.34
@dataclass(frozen=True)
class SearchDocument:
    entity_id: str
    node: dict[str, Any]
    text: str


class EmbeddingEncoder(Protocol):
    model_name: str
    model_revision: str

    def encode_documents(self, texts: Sequence[str]) -> NDArray[np.float32]: ...

    def encode_query(self, text: str) -> NDArray[np.float32]: ...


class SentenceTransformerEncoder:
    def __init__(self, model_name: str, model_revision: str) -> None:
        self.model_name = model_name
        self.model_revision = model_revision

    @staticmethod
    @lru_cache(maxsize=4)
    def _load_model(model_name: str, model_revision: str) -> Any:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(
            model_name,
            revision=model_revision,
            device="cpu",
            trust_remote_code=False,
        )

    @property
    def model(self) -> Any:
        return self._load_model(self.model_name, self.model_revision)

    def encode_documents(self, texts: Sequence[str]) -> NDArray[np.float32]:
        embeddings = self.model.encode_document(
            list(texts),
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return np.asarray(embeddings, dtype=np.float32)

    def encode_query(self, text: str) -> NDArray[np.float32]:
        embedding = self.model.encode_query(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return np.asarray(embedding, dtype=np.float32)


def build_index_document(store: GraphStore, node: dict[str, Any]) -> SearchDocument:
    lines = [f"Entity type: {node['type']}", f"Name: {node['label']}"]
    aliases = sorted(node.get("aliases", []), key=lambda value: value.casefold())
    if aliases:
        lines.append(f"Aliases: {', '.join(aliases)}")

    if node.get("description"):
        lines.append(f"Description: {str(node['description']).strip()}")
    if node.get("designation"):
        lines.append(f"Designation: {node['designation']}")
    if node.get("status"):
        lines.append(f"Status: {node['status']}")
    if node.get("power_profile"):
        lines.append(f"Power profile: {node['power_profile']}")
    if node.get("work_type"):
        lines.append(f"Work type: {node['work_type']}")

    universe = store.get_node(node.get("universe_id", ""))
    if universe:
        universe_text = universe["label"]
        if universe.get("designation") and universe["designation"] != universe["label"]:
            universe_text += f" ({universe['designation']})"
        lines.append(f"Universe: {universe_text}")
        if universe.get("description"):
            lines.append(f"Universe description: {universe['description']}")

    return SearchDocument(entity_id=node["id"], node=node, text="\n".join(lines))


class SearchService:
    def __init__(
        self,
        store: GraphStore,
        settings: Settings,
        *,
        encoder: EmbeddingEncoder | None = None,
    ) -> None:
        if not 0.0 <= settings.search_hybrid_lexical_weight <= 1.0:
            raise ValueError("SEARCH_HYBRID_LEXICAL_WEIGHT must be between 0 and 1")
        started = perf_counter()
        self.store = store
        self.settings = settings
        self.documents = tuple(
            build_index_document(store, node)
            for node in sorted(store.nodes, key=lambda item: item["id"])
        )
        self.document_build_seconds = perf_counter() - started
        self.encoder = encoder or SentenceTransformerEncoder(
            settings.search_embedding_model,
            settings.search_embedding_revision,
        )
        self._embeddings: NDArray[np.float32] | None = None
        self.index_build_seconds: float | None = None

    @property
    def hybrid_lexical_weight(self) -> float:
        return self.settings.search_hybrid_lexical_weight

    @property
    def hybrid_semantic_weight(self) -> float:
        return 1.0 - self.hybrid_lexical_weight

    def corpus_signature(self) -> str:
        digest = hashlib.sha256()
        for document in self.documents:
            digest.update(document.entity_id.encode("utf-8"))
            digest.update(b"\0")
            digest.update(document.text.encode("utf-8"))
            digest.update(b"\0")
        return digest.hexdigest()

    def _ensure_index(self) -> NDArray[np.float32]:
        if self._embeddings is None:
            started = perf_counter()
            embeddings = self.encoder.encode_documents(
                [document.text for document in self.documents]
            )
            if embeddings.ndim != 2 or embeddings.shape[0] != len(self.documents):
                raise RuntimeError("Embedding model returned an invalid corpus matrix")
            self._embeddings = embeddings
            self.index_build_seconds = perf_counter() - started
        return self._embeddings

    def index_metadata(self) -> dict[str, Any]:
        embeddings = self._ensure_index()
        return {
            "model": self.encoder.model_name,
            "revision": self.encoder.model_revision,
            "entities": len(self.documents),
            "dimensions": int(embeddings.shape[1]),
            "bytes": int(embeddings.nbytes),
            "document_build_seconds": round(self.document_build_seconds, 6),
            "index_build_seconds": round(self.index_build_seconds or 0.0, 6),
            "normalized": True,
            "similarity": "cosine_via_normalized_dot_product",
        }

    def search(
        self,
        query: str,
        *,
        mode: SearchMode = "lexical",
        node_types: set[str] | None = None,
        limit: int = 12,
    ) -> list[dict[str, Any]]:
        if mode not in {"lexical", "semantic", "hybrid"}:
            raise ValueError(f"Unsupported search mode: {mode}")
        if not normalize(query):
            return []

        lexical_scores = {
            document.entity_id: lexical_score(query, document.node)
            for document in self.documents
        }
        semantic_scores: dict[str, tuple[float, float]] = {}
        if mode in {"semantic", "hybrid"}:
            query_embedding = self.encoder.encode_query(query)
            raw_scores = self._ensure_index() @ query_embedding
            semantic_scores = {
                document.entity_id: (
                    self._normalize_cosine(float(raw_score)),
                    float(raw_score),
                )
                for document, raw_score in zip(self.documents, raw_scores, strict=True)
            }

        results = []
        for document in self.documents:
            node = document.node
            if node_types and node["type"] not in node_types:
                continue
            lexical = lexical_scores[document.entity_id]
            if mode == "lexical" and lexical < LEXICAL_MIN_SCORE:
                continue
            semantic, cosine = semantic_scores.get(document.entity_id, (None, None))
            if mode == "lexical":
                final_score = lexical
            elif mode == "semantic":
                final_score = semantic or 0.0
            else:
                final_score = (
                    self.hybrid_lexical_weight * lexical
                    + self.hybrid_semantic_weight * (semantic or 0.0)
                )
            results.append(
                {
                    **node,
                    "universe_label": self._universe_label(node),
                    "search_mode": mode,
                    "score": self._round(final_score),
                    "lexical_score": self._round(lexical),
                    "semantic_score": self._round(semantic) if semantic is not None else None,
                    "semantic_cosine": self._round(cosine) if cosine is not None else None,
                }
            )

        if mode == "lexical":
            results.sort(key=lambda item: (-item["score"], item["label"], item["id"]))
        else:
            results.sort(
                key=lambda item: (-item["score"], item["label"].casefold(), item["id"])
            )
        return results[:limit]

    def _universe_label(self, node: dict[str, Any]) -> str | None:
        universe = self.store.get_node(node.get("universe_id", ""))
        return str(universe["label"]) if universe else None

    @staticmethod
    def _normalize_cosine(score: float) -> float:
        return min(1.0, max(0.0, (score + 1.0) / 2.0))

    @staticmethod
    def _round(value: float) -> float:
        return round(float(value), 12)
