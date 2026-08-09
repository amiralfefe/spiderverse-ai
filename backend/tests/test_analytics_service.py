from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app.analytics_service import GraphAnalyticsService
from backend.app.config import settings
from backend.app.graph_store import GraphStore
from backend.app.main import create_app


def make_store(
    nodes: list[tuple[str, str, str]], edges: list[tuple[str, str, str]]
) -> GraphStore:
    return GraphStore(
        {
            "nodes": [
                {"id": node_id, "label": label, "type": node_type}
                for node_id, label, node_type in nodes
            ],
            "edges": [
                {
                    "id": f"edge-{index}",
                    "source": source,
                    "target": target,
                    "type": relation_type,
                    "properties": {},
                }
                for index, (source, target, relation_type) in enumerate(edges, start=1)
            ],
        }
    )


def test_degree_and_betweenness_on_path_graph() -> None:
    store = make_store(
        [("a", "Alpha", "Character"), ("b", "Beta", "Character"), ("c", "Gamma", "Character")],
        [("a", "b", "RELATED_TO"), ("b", "c", "RELATED_TO")],
    )
    service = GraphAnalyticsService(store)

    degree = service.centrality("degree", node_type="Character", limit=3)
    betweenness = service.centrality("betweenness", node_type="Character", limit=3)

    assert [(item["node"]["id"], item["score"], item["degree"]) for item in degree["results"]] == [
        ("b", 1.0, 2),
        ("a", 0.5, 1),
        ("c", 0.5, 1),
    ]
    assert betweenness["results"][0]["node"]["id"] == "b"
    assert betweenness["results"][0]["score"] == 1.0
    assert service.overview() == {
        "nodes": 3,
        "relationships": 2,
        "unique_connections": 2,
        "density": 0.666666666667,
        "average_degree": 1.333333333333,
        "connected_components": 1,
        "largest_component": 3,
        "communities": 1,
        "community_algorithm": "greedy_modularity",
    }


def test_communities_are_real_and_deterministic() -> None:
    nodes = [(letter, letter.upper(), "Character") for letter in "abcdef"]
    edges = [
        ("a", "b", "RELATED_TO"),
        ("b", "c", "RELATED_TO"),
        ("c", "a", "RELATED_TO"),
        ("d", "e", "RELATED_TO"),
        ("e", "f", "RELATED_TO"),
        ("f", "d", "RELATED_TO"),
        ("c", "d", "RELATED_TO"),
    ]
    store = make_store(nodes, edges)

    first = GraphAnalyticsService(store).communities()
    second = GraphAnalyticsService(store).communities()

    assert first == second
    assert first["algorithm"] == "greedy_modularity"
    assert first["count"] == 2
    assert [[member["id"] for member in group["members"]] for group in first["communities"]] == [
        ["a", "b", "c"],
        ["d", "e", "f"],
    ]


def test_character_similarity_uses_jaccard_neighbors() -> None:
    store = make_store(
        [
            ("miles", "Miles", "Character"),
            ("peer", "Peer", "Character"),
            ("low", "Low", "Character"),
            ("power-1", "Power 1", "Power"),
            ("power-2", "Power 2", "Power"),
            ("power-3", "Power 3", "Power"),
        ],
        [
            ("miles", "power-1", "HAS_POWER"),
            ("miles", "power-2", "HAS_POWER"),
            ("miles", "power-3", "HAS_POWER"),
            ("peer", "power-1", "HAS_POWER"),
            ("peer", "power-2", "HAS_POWER"),
            ("low", "power-1", "HAS_POWER"),
        ],
    )
    service = GraphAnalyticsService(store)

    result = service.similarity("miles", limit=2)

    assert result["metric"] == "jaccard_direct_neighbors"
    assert result["results"][0]["node"]["id"] == "peer"
    assert result["results"][0]["score"] == 0.666666666667
    assert [node["id"] for node in result["results"][0]["shared_neighbors"]] == [
        "power-1",
        "power-2",
    ]
    with pytest.raises(ValueError, match="Character not found"):
        service.similarity("missing")


def test_production_analytics_are_reproducible() -> None:
    store = GraphStore.from_path(settings.graph_data_path)
    first = GraphAnalyticsService(store)
    second = GraphAnalyticsService(store)

    assert first.overview() == second.overview()
    assert first.centrality("degree", node_type="Character") == second.centrality(
        "degree", node_type="Character"
    )
    assert first.communities() == second.communities()
    assert first.similarity("miles-1610") == second.similarity("miles-1610")


def test_analytics_api_contract_and_errors() -> None:
    client = TestClient(create_app(GraphStore.from_path(settings.graph_data_path)))

    overview = client.get("/api/analytics/overview")
    degree = client.get(
        "/api/analytics/centrality",
        params={"metric": "degree", "node_type": "Character", "limit": 5},
    )
    communities = client.get("/api/analytics/communities", params={"min_size": 2})
    similarity = client.get("/api/analytics/similarity/miles-1610", params={"limit": 5})

    assert overview.status_code == 200
    assert overview.json()["nodes"] == 164
    assert degree.status_code == 200
    assert degree.json()["results"][0]["node"]["id"] == "peter-616"
    assert communities.status_code == 200
    assert communities.json()["algorithm"] == "greedy_modularity"
    assert similarity.status_code == 200
    assert similarity.json()["source"]["id"] == "miles-1610"
    assert client.get("/api/analytics/centrality", params={"metric": "invalid"}).status_code == 422
    assert client.get("/api/analytics/similarity/missing").status_code == 404
