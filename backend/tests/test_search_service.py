from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pytest
from fastapi.testclient import TestClient
from numpy.typing import NDArray

from backend.app.config import Settings, settings
from backend.app.graph_store import GraphStore
from backend.app.main import create_app
from backend.app.search_service import SearchService, build_index_document
from scripts.benchmark_search import evaluate_search, load_benchmark


class TargetEncoder:
    model_name = "test/target-encoder"
    model_revision = "test-revision"

    def encode_documents(self, texts: Sequence[str]) -> NDArray[np.float32]:
        return np.asarray(
            [[1.0, 0.0] if "Miguel O'Hara" in text else [0.0, 1.0] for text in texts],
            dtype=np.float32,
        )

    def encode_query(self, text: str) -> NDArray[np.float32]:
        del text
        return np.asarray([1.0, 0.0], dtype=np.float32)


class TieEncoder:
    model_name = "test/tie-encoder"
    model_revision = "test-revision"

    def encode_documents(self, texts: Sequence[str]) -> NDArray[np.float32]:
        return np.ones((len(texts), 2), dtype=np.float32) / np.sqrt(2)

    def encode_query(self, text: str) -> NDArray[np.float32]:
        del text
        return np.ones(2, dtype=np.float32) / np.sqrt(2)


@pytest.fixture
def store() -> GraphStore:
    return GraphStore.from_path(settings.graph_data_path)


@pytest.fixture
def target_service(store: GraphStore) -> SearchService:
    return SearchService(store, Settings(), encoder=TargetEncoder())


def test_document_is_grounded_deterministic_and_backend_order_independent(
    store: GraphStore,
) -> None:
    miguel = store.get_node("miguel-928")
    assert miguel is not None
    assert build_index_document(store, miguel).text == (
        "Entity type: Character\n"
        "Name: Miguel O'Hara\n"
        "Aliases: Spider-Man 2099\n"
        "Description: A geneticist and Spider-Man of the year 2099.\n"
        "Status: Active\n"
        "Power profile: miguel\n"
        "Universe: Earth-928 (928)\n"
        "Universe description: The future setting associated with 2099."
    )

    reversed_store = GraphStore(
        {"nodes": list(reversed(store.nodes)), "edges": list(reversed(store.edges))}
    )
    original = SearchService(store, Settings(), encoder=TargetEncoder())
    reversed_service = SearchService(reversed_store, Settings(), encoder=TargetEncoder())
    assert original.corpus_signature() == reversed_service.corpus_signature()
    assert [document.entity_id for document in original.documents] == [
        document.entity_id for document in reversed_service.documents
    ]


def test_lexical_mode_preserves_v1_exact_alias_partial_case_and_spacing(
    store: GraphStore,
) -> None:
    service = SearchService(store, Settings(), encoder=TargetEncoder())
    queries = ("Miles Morales", "spider-man 2099", "  GHOST spider  ", "Miles")
    for query in queries:
        expected = [node["id"] for node in store.search(query, limit=12)]
        actual = [node["id"] for node in service.search(query, mode="lexical", limit=12)]
        assert actual == expected


def test_semantic_hybrid_scores_normalization_and_top_k(
    target_service: SearchService,
) -> None:
    semantic = target_service.search("future Spider-Man", mode="semantic", limit=2)
    assert len(semantic) == 2
    assert semantic[0]["id"] == "miguel-928"
    assert semantic[0]["semantic_cosine"] == 1.0
    assert semantic[0]["semantic_score"] == 1.0
    assert 0.0 <= semantic[1]["semantic_score"] <= 1.0

    hybrid = target_service.search("Spider-Man 2099", mode="hybrid", limit=1)
    assert hybrid[0]["id"] == "miguel-928"
    expected = (
        target_service.hybrid_lexical_weight * hybrid[0]["lexical_score"]
        + target_service.hybrid_semantic_weight * hybrid[0]["semantic_score"]
    )
    assert hybrid[0]["score"] == pytest.approx(expected, abs=1e-10)


def test_empty_missing_type_invalid_mode_and_stable_ties(
    target_service: SearchService,
) -> None:
    assert target_service.search("   ", mode="semantic") == []
    assert target_service.search("anything", mode="semantic", node_types={"Missing"}) == []
    with pytest.raises(ValueError, match="Unsupported search mode"):
        target_service.search("Miles", mode="invalid")  # type: ignore[arg-type]

    tie_store = GraphStore(
        {
            "nodes": [
                {"id": "z", "label": "Beta", "type": "Concept"},
                {"id": "a", "label": "alpha", "type": "Concept"},
            ],
            "edges": [],
        }
    )
    tie_service = SearchService(tie_store, Settings(), encoder=TieEncoder())
    assert [item["id"] for item in tie_service.search("query", mode="semantic")] == [
        "a",
        "z",
    ]


def test_search_api_is_compatible_validated_and_explainable(store: GraphStore) -> None:
    app = create_app(store)
    app.state.search_service.encoder = TargetEncoder()
    client = TestClient(app)

    lexical = client.get("/api/search", params={"q": "Miles Morales"})
    assert lexical.status_code == 200
    assert lexical.json()[0]["id"] == "miles-1610"
    assert lexical.json()[0]["search_mode"] == "lexical"

    semantic = client.get(
        "/api/search", params={"q": "future Spider-Man", "mode": "semantic", "limit": 1}
    )
    assert semantic.status_code == 200
    assert semantic.json()[0]["id"] == "miguel-928"
    assert semantic.json()[0]["semantic_score"] == 1.0

    assert client.get("/api/search", params={"q": "Miles", "mode": "unknown"}).status_code == 422
    assert client.get("/api/search", params={"q": "", "mode": "lexical"}).status_code == 422


def test_real_embedding_model_and_benchmark(store: GraphStore) -> None:
    service = SearchService(store, settings)
    metadata = service.index_metadata()
    assert metadata["entities"] == 164
    assert metadata["dimensions"] == 384
    assert metadata["model"] == "sentence-transformers/multi-qa-MiniLM-L6-cos-v1"
    assert metadata["revision"] == "b207367332321f8e44f96e224ef15bc607f4dbf0"

    future = service.search("Spider-Man from the future", mode="semantic", limit=3)
    assert future[0]["id"] == "miguel-928"

    evaluation = evaluate_search(service, load_benchmark())
    lexical = evaluation["metrics"]["lexical"]
    semantic = evaluation["metrics"]["semantic"]
    hybrid = evaluation["metrics"]["hybrid"]
    assert semantic["top_1"] > lexical["top_1"]
    assert hybrid["top_1"] > lexical["top_1"]
    assert hybrid["hit_at_3"] >= 0.90
    assert hybrid["mrr"] > lexical["mrr"]
