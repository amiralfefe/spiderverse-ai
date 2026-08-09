from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from backend.app.analytics_service import GraphAnalyticsService
from backend.app.config import Settings, settings
from backend.app.graph_store import GraphStore, load_neo4j
from backend.app.query_service import QueryService


def _canonical(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _canonical(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [_canonical(item) for item in value]
    return value


def _edge(edge: dict[str, Any]) -> dict[str, Any]:
    return _canonical(edge)


def _graph(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "focus_id": payload["focus_id"],
        "nodes": sorted(
            (_canonical(node) for node in payload["nodes"]), key=lambda node: node["id"]
        ),
        "edges": sorted((_edge(edge) for edge in payload["edges"]), key=lambda edge: edge["id"]),
    }


def _sources(values: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        (_canonical(value) for value in values),
        key=lambda value: (
            value.get("source_title", ""),
            value.get("source_type", ""),
            value.get("source_url", ""),
        ),
    )


def collect_contract(store: GraphStore) -> dict[str, Any]:
    detail = store.character_detail("miles-1610")
    if detail is None:
        raise RuntimeError("Miles Morales is missing from the backend")

    neighborhood = store.neighborhood("miles-1610", depth=1, limit=100)
    path = store.shortest_path("miles-1610", "daredevil-616")
    ask = QueryService(store).ask("Who mentored Miles Morales?")
    analytics = GraphAnalyticsService(store)

    return {
        "stats": _canonical(store.stats()),
        "search_name": [
            (node["id"], node["label"], node["type"])
            for node in store.search("Miles Morales", limit=12)
        ],
        "search_alias": [
            (node["id"], node["label"], node["type"])
            for node in store.search("Spider-Man 2099", limit=12)
        ],
        "miles_detail": {
            "character": _canonical(detail["character"]),
            "universe": _canonical(detail["universe"]),
            "powers": sorted(
                (_canonical(node) for node in detail["powers"]), key=lambda node: node["id"]
            ),
            "works": sorted(
                (_canonical(node) for node in detail["works"]), key=lambda node: node["id"]
            ),
            "relations": sorted(
                (
                    {
                        "edge": _edge(item["edge"]),
                        "node": _canonical(item["node"]),
                        "direction": item["direction"],
                    }
                    for item in detail["relations"]
                ),
                key=lambda item: item["edge"]["id"],
            ),
            "sources": _sources(detail["sources"]),
        },
        "miles_neighborhood": _graph(neighborhood),
        "earth_1610_characters": sorted(
            (
                _canonical(node)
                for node in store.list_nodes(
                    node_type="Character", universe_id="earth-1610", limit=250
                )
            ),
            key=lambda node: node["id"],
        ),
        "miles_to_daredevil": {
            "found": path["found"],
            "hops": path["hops"],
            "nodes": [_canonical(node) for node in path["nodes"]],
            "edges": [_edge(edge) for edge in path["edges"]],
        },
        "mentor_question": {
            "answer": ask["answer"],
            "strategy": ask["strategy"],
            "entities": [_canonical(node) for node in ask["entities"]],
            "graph": _graph(ask["graph"]),
            "sources": _sources(ask["sources"]),
        },
        "analytics_overview": _canonical(analytics.overview()),
        "analytics_degree": _canonical(
            analytics.centrality("degree", node_type="Character", limit=10)
        ),
        "analytics_betweenness": _canonical(
            analytics.centrality("betweenness", node_type="Character", limit=10)
        ),
        "analytics_communities": _canonical(analytics.communities(min_size=2)),
        "analytics_miles_similarity": _canonical(
            analytics.similarity("miles-1610", limit=10)
        ),
    }


def main() -> None:
    local_store = GraphStore.from_path(settings.graph_data_path)
    neo4j_settings = Settings(
        graph_backend="neo4j",
        graph_data_path=settings.graph_data_path,
        neo4j_uri=settings.neo4j_uri,
        neo4j_user=settings.neo4j_user,
        neo4j_password=settings.neo4j_password,
    )

    try:
        neo4j_store = load_neo4j(neo4j_settings)
    except Exception as exc:
        print(f"Neo4j backend unavailable: {type(exc).__name__}: {exc}")
        raise SystemExit(2) from exc

    local_contract = collect_contract(local_store)
    neo4j_contract = collect_contract(neo4j_store)
    failed = []
    for case in local_contract:
        if local_contract[case] == neo4j_contract[case]:
            print(f"{case}: PASS")
            continue
        failed.append(case)
        print(f"{case}: FAIL")
        print("JSON:", json.dumps(local_contract[case], ensure_ascii=False, sort_keys=True))
        print("Neo4j:", json.dumps(neo4j_contract[case], ensure_ascii=False, sort_keys=True))

    if failed:
        print(f"Backend parity: FAIL ({', '.join(failed)})")
        raise SystemExit(1)
    print(f"Backend parity: PASS ({len(local_contract)} deterministic cases)")


if __name__ == "__main__":
    main()
