from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    graph_backend: str = os.getenv("GRAPH_BACKEND", "local").lower()
    graph_data_path: Path = Path(
        os.getenv("GRAPH_DATA_PATH", str(ROOT_DIR / "data" / "processed" / "graph.json"))
    )
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "spiderverse-local")
    search_embedding_model: str = os.getenv(
        "SEARCH_EMBEDDING_MODEL", "sentence-transformers/multi-qa-MiniLM-L6-cos-v1"
    )
    search_embedding_revision: str = os.getenv(
        "SEARCH_EMBEDDING_REVISION", "b207367332321f8e44f96e224ef15bc607f4dbf0"
    )
    search_hybrid_lexical_weight: float = float(
        os.getenv("SEARCH_HYBRID_LEXICAL_WEIGHT", "0.22")
    )


settings = Settings()
