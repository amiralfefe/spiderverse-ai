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


settings = Settings()
