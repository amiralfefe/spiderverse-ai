from fastapi.testclient import TestClient

from backend.app.config import settings
from backend.app.graph_store import GraphStore
from backend.app.main import create_app

client = TestClient(create_app(GraphStore.from_path(settings.graph_data_path)))


def test_health_and_stats() -> None:
    assert client.get("/api/health").status_code == 200
    stats = client.get("/api/stats")
    assert stats.status_code == 200
    assert stats.json()["relationships"] >= 500


def test_character_and_relations() -> None:
    detail = client.get("/api/characters/miles-1610")
    assert detail.status_code == 200
    assert detail.json()["character"]["label"] == "Miles Morales"
    graph = client.get("/api/graph", params={"focus_id": "miles-1610", "depth": 1})
    assert graph.status_code == 200
    assert graph.json()["focus_id"] == "miles-1610"


def test_path_and_ask() -> None:
    path = client.get("/api/path", params={"start_id": "miles-1610", "end_id": "daredevil-616"})
    assert path.status_code == 200
    assert path.json()["found"] is True
    answer = client.post("/api/ask", json={"question": "Who mentored Miles Morales?"})
    assert answer.status_code == 200
    assert answer.json()["strategy"] == "entity_neighborhood"
