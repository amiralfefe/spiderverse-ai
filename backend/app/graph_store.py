from __future__ import annotations

import json
import re
from collections import Counter, defaultdict, deque
from collections.abc import Iterable
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from backend.app.config import Settings

EXCLUDED_PATH_RELATIONS = {
    "APPEARS_IN",
    "HAS_POWER",
    "SET_IN_UNIVERSE",
    "DEPICTS_EVENT",
    "OCCURRED_IN",
    "BELONGS_TO_UNIVERSE",
}


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


class GraphStore:
    def __init__(self, data: dict[str, Any]) -> None:
        self.meta = data.get("meta", {})
        self.nodes = data["nodes"]
        self.edges = data["edges"]
        self.node_by_id = {node["id"]: node for node in self.nodes}
        self.edges_by_node: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for edge in self.edges:
            self.edges_by_node[edge["source"]].append(edge)
            self.edges_by_node[edge["target"]].append(edge)

    @classmethod
    def from_path(cls, path: Path) -> GraphStore:
        return cls(json.loads(path.read_text(encoding="utf-8")))

    def stats(self) -> dict[str, Any]:
        by_type = Counter(node["type"] for node in self.nodes)
        verified = sum(bool(edge.get("properties", {}).get("verified")) for edge in self.edges)
        return {
            "nodes": len(self.nodes),
            "relationships": len(self.edges),
            "by_type": dict(sorted(by_type.items())),
            "verified_relationships": verified,
            "demo_relationships": len(self.edges) - verified,
        }

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        return self.node_by_id.get(node_id)

    def search(
        self, query: str, *, node_types: set[str] | None = None, limit: int = 12
    ) -> list[dict[str, Any]]:
        needle = normalize(query)
        if not needle:
            return []
        matches: list[tuple[float, dict[str, Any]]] = []
        for node in self.nodes:
            if node_types and node["type"] not in node_types:
                continue
            names = [node["label"], *node.get("aliases", [])]
            normalized_names = [normalize(name) for name in names]
            exact = needle in normalized_names
            contains = any(needle in name for name in normalized_names)
            ratio = max(SequenceMatcher(None, needle, name).ratio() for name in normalized_names)
            score = 1.0 if exact else 0.85 if contains else ratio * 0.7
            if score >= 0.34:
                matches.append((score, node))
        matches.sort(key=lambda item: (-item[0], item[1]["label"], item[1]["id"]))
        return [node for _, node in matches[:limit]]

    def list_nodes(
        self,
        *,
        node_type: str | None = None,
        universe_id: str | None = None,
        query: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        if query:
            node_types = {node_type} if node_type else None
            result = self.search(query, node_types=node_types, limit=limit)
        else:
            result = [node for node in self.nodes if not node_type or node["type"] == node_type]
        if universe_id:
            result = [node for node in result if node.get("universe_id") == universe_id]
        return sorted(result, key=lambda node: (node["label"], node["id"]))[:limit]

    def neighborhood(
        self,
        focus_id: str | None,
        *,
        depth: int = 1,
        limit: int = 80,
        node_types: set[str] | None = None,
        relation_types: set[str] | None = None,
        universe_id: str | None = None,
    ) -> dict[str, Any]:
        if focus_id is None:
            selected_nodes = self.nodes[:limit]
            selected_ids = {node["id"] for node in selected_nodes}
            selected_edges = [
                edge
                for edge in self.edges
                if edge["source"] in selected_ids and edge["target"] in selected_ids
            ]
            return {"nodes": selected_nodes, "edges": selected_edges, "focus_id": None}
        if focus_id not in self.node_by_id:
            return {"nodes": [], "edges": [], "focus_id": focus_id}

        visited = {focus_id}
        queue = deque([(focus_id, 0)])
        candidate_edges: dict[str, dict[str, Any]] = {}
        while queue and len(visited) < limit:
            current, current_depth = queue.popleft()
            if current_depth >= depth:
                continue
            for edge in self.edges_by_node[current]:
                if relation_types and edge["type"] not in relation_types:
                    continue
                other = edge["target"] if edge["source"] == current else edge["source"]
                other_node = self.node_by_id[other]
                if node_types and other_node["type"] not in node_types and other != focus_id:
                    continue
                if universe_id and other_node["type"] == "Character":
                    if other_node.get("universe_id") != universe_id and other != focus_id:
                        continue
                candidate_edges[edge["id"]] = edge
                if other not in visited and len(visited) < limit:
                    visited.add(other)
                    queue.append((other, current_depth + 1))

        nodes = [self.node_by_id[node_id] for node_id in visited]
        nodes.sort(key=lambda node: (node["id"] != focus_id, node["type"], node["label"]))
        edges = [
            edge
            for edge in candidate_edges.values()
            if edge["source"] in visited and edge["target"] in visited
        ]
        return {"nodes": nodes, "edges": edges, "focus_id": focus_id}

    def character_detail(self, character_id: str) -> dict[str, Any] | None:
        character = self.node_by_id.get(character_id)
        if not character or character["type"] != "Character":
            return None
        relations: list[dict[str, Any]] = []
        powers: list[dict[str, Any]] = []
        works: list[dict[str, Any]] = []
        sources: dict[tuple[str, str], dict[str, Any]] = {}
        universe = self.node_by_id.get(character.get("universe_id"))
        for edge in self.edges_by_node[character_id]:
            other_id = edge["target"] if edge["source"] == character_id else edge["source"]
            other = self.node_by_id[other_id]
            direction = "outgoing" if edge["source"] == character_id else "incoming"
            relations.append({"edge": edge, "node": other, "direction": direction})
            if edge["type"] == "HAS_POWER":
                powers.append(other)
            elif edge["type"] == "APPEARS_IN":
                works.append(other)
            provenance = edge.get("properties", {})
            key = (provenance.get("source_title", ""), provenance.get("source_type", ""))
            if key[0]:
                sources[key] = provenance
        relations.sort(key=lambda item: (item["edge"]["type"], item["node"]["label"]))
        return {
            "character": character,
            "universe": universe,
            "powers": sorted(powers, key=lambda node: node["label"]),
            "works": sorted(works, key=lambda node: node["label"]),
            "relations": relations,
            "sources": list(sources.values()),
        }

    def shortest_path(self, start_id: str, end_id: str) -> dict[str, Any]:
        if start_id not in self.node_by_id or end_id not in self.node_by_id:
            return {"found": False, "nodes": [], "edges": [], "hops": None}
        queue = deque([start_id])
        previous: dict[str, tuple[str, dict[str, Any]] | None] = {start_id: None}
        while queue:
            current = queue.popleft()
            if current == end_id:
                break
            for edge in self.edges_by_node[current]:
                if edge["type"] in EXCLUDED_PATH_RELATIONS:
                    continue
                other = edge["target"] if edge["source"] == current else edge["source"]
                if other not in previous:
                    previous[other] = (current, edge)
                    queue.append(other)
        if end_id not in previous:
            return {"found": False, "nodes": [], "edges": [], "hops": None}
        node_ids: list[str] = []
        path_edges: list[dict[str, Any]] = []
        cursor = end_id
        while cursor != start_id:
            node_ids.append(cursor)
            parent, edge = previous[cursor]  # type: ignore[misc]
            path_edges.append(edge)
            cursor = parent
        node_ids.append(start_id)
        node_ids.reverse()
        path_edges.reverse()
        return {
            "found": True,
            "nodes": [self.node_by_id[node_id] for node_id in node_ids],
            "edges": path_edges,
            "hops": len(path_edges),
        }

    def sources_for_edges(self, edges: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
        sources: dict[tuple[str, str], dict[str, Any]] = {}
        for edge in edges:
            provenance = edge.get("properties", {})
            key = (provenance.get("source_title", ""), provenance.get("source_type", ""))
            if key[0]:
                sources[key] = provenance
        return list(sources.values())


def load_neo4j(settings: Settings) -> GraphStore:
    try:
        from neo4j import GraphDatabase
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Install the 'neo4j' project extra to use GRAPH_BACKEND=neo4j") from exc

    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
        connection_timeout=5.0,
    )
    try:
        with driver.session() as session:
            records = session.run(
                "MATCH (n:Entity) RETURN properties(n) AS props, "
                "[label IN labels(n) WHERE label <> 'Entity'][0] AS node_type "
                "ORDER BY props.id"
            )
            nodes = []
            for record in records:
                props = dict(record["props"])
                props["type"] = record["node_type"]
                nodes.append(props)
            rel_records = session.run(
                "MATCH (a)-[r]->(b) RETURN a.id AS source, b.id AS target, "
                "type(r) AS rel_type, properties(r) AS props ORDER BY props.id"
            )
            edges = []
            for index, record in enumerate(rel_records, start=1):
                props = dict(record["props"])
                edge_id = props.pop("id", f"neo4j-rel-{index}")
                edges.append(
                    {
                        "id": edge_id,
                        "source": record["source"],
                        "target": record["target"],
                        "type": record["rel_type"],
                        "properties": props,
                    }
                )
        return GraphStore({"meta": {"backend": "neo4j"}, "nodes": nodes, "edges": edges})
    finally:
        driver.close()


def build_store(settings: Settings) -> GraphStore:
    if settings.graph_backend == "neo4j":
        return load_neo4j(settings)
    return GraphStore.from_path(settings.graph_data_path)
