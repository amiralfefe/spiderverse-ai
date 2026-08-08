from backend.app.config import settings
from backend.app.graph_store import GraphStore
from backend.app.query_service import QueryService


def store() -> GraphStore:
    return GraphStore.from_path(settings.graph_data_path)


def test_mvp_counts() -> None:
    stats = store().stats()
    assert stats["by_type"]["Character"] >= 50
    assert stats["by_type"]["Universe"] >= 10
    assert stats["relationships"] >= 500


def test_search_resolves_alias_and_semantic_neighbor() -> None:
    graph = store()
    assert graph.search("Miles Morales")[0]["id"] == "miles-1610"
    assert any(node["id"] == "miguel-928" for node in graph.search("Spider-Man 2099"))


def test_character_detail_contains_graph_facts() -> None:
    detail = store().character_detail("miles-1610")
    assert detail is not None
    assert detail["universe"]["id"] == "earth-1610"
    assert {power["label"] for power in detail["powers"]} >= {"Venom Blast", "Camouflage"}
    assert any(item["edge"]["type"] == "MENTORED_BY" for item in detail["relations"])


def test_shortest_path_is_graph_backed() -> None:
    path = store().shortest_path("miles-1610", "daredevil-616")
    assert path["found"] is True
    assert path["nodes"][0]["id"] == "miles-1610"
    assert path["nodes"][-1]["id"] == "daredevil-616"
    assert path["hops"] == len(path["edges"])


def test_ask_filters_mentor_relation() -> None:
    result = QueryService(store()).ask("Who mentored Miles Morales?")
    assert result["strategy"] == "entity_neighborhood"
    assert "Peter B. Parker" in result["answer"]
    assert all(edge["type"] == "MENTORED_BY" for edge in result["graph"]["edges"])
