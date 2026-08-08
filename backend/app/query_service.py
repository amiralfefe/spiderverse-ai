from __future__ import annotations

from typing import Any

from backend.app.graph_store import GraphStore, normalize

RELATION_HINTS = {
    "mentor": "MENTORED_BY",
    "mentored": "MENTORED_BY",
    "alli": "ALLY_OF",
    "friend": "FRIEND_OF",
    "ami": "FRIEND_OF",
    "enemy": "ENEMY_OF",
    "ennemi": "ENEMY_OF",
    "power": "HAS_POWER",
    "pouvoir": "HAS_POWER",
    "appear": "APPEARS_IN",
    "oeuvre": "APPEARS_IN",
    "œuvre": "APPEARS_IN",
    "universe": "BELONGS_TO_UNIVERSE",
    "univers": "BELONGS_TO_UNIVERSE",
    "team": "MEMBER_OF",
    "équipe": "MEMBER_OF",
}


class QueryService:
    def __init__(self, store: GraphStore) -> None:
        self.store = store

    def _extract_entities(self, question: str) -> list[dict[str, Any]]:
        normalized_question = normalize(question)
        candidates: list[tuple[int, dict[str, Any]]] = []
        for node in self.store.nodes:
            if node["type"] not in {"Character", "Universe", "Event", "Team", "Concept"}:
                continue
            names = [node["label"], *node.get("aliases", [])]
            if any(
                normalize(name) in normalized_question for name in names if len(normalize(name)) > 2
            ):
                candidates.append((max(len(normalize(name)) for name in names), node))
        candidates.sort(key=lambda item: -item[0])
        entities: list[dict[str, Any]] = []
        seen: set[str] = set()
        for _, node in candidates:
            if node["id"] not in seen:
                entities.append(node)
                seen.add(node["id"])
        return entities[:4]

    def ask(self, question: str) -> dict[str, Any]:
        normalized_question = normalize(question)
        entities = self._extract_entities(question)
        asks_path = any(
            term in normalized_question for term in ("path", "chemin", "link between", "lien entre")
        )
        if asks_path and len(entities) >= 2:
            path = self.store.shortest_path(entities[0]["id"], entities[1]["id"])
            if path["found"]:
                labels = " → ".join(node["label"] for node in path["nodes"])
                answer = f"Shortest graph path ({path['hops']} hops): {labels}."
            else:
                answer = "No path was found in the current demonstration graph."
            return {
                "answer": answer,
                "strategy": "shortest_path",
                "entities": entities[:2],
                "graph": {
                    "nodes": path["nodes"],
                    "edges": path["edges"],
                    "focus_id": entities[0]["id"],
                },
                "sources": self.store.sources_for_edges(path["edges"]),
            }

        if not entities:
            suggestions = self.store.search(question, node_types={"Character", "Universe"}, limit=5)
            if suggestions:
                names = ", ".join(node["label"] for node in suggestions)
                answer = f"I could not resolve an exact entity. Closest graph matches: {names}."
            else:
                answer = (
                    "I could not resolve an entity in the current graph. "
                    "Try a character, universe, team, or event name."
                )
            return {
                "answer": answer,
                "strategy": "entity_resolution",
                "entities": suggestions,
                "graph": {"nodes": suggestions, "edges": [], "focus_id": None},
                "sources": [],
            }

        focus = entities[0]
        requested_relation = next(
            (relation for hint, relation in RELATION_HINTS.items() if hint in normalized_question),
            None,
        )
        graph = self.store.neighborhood(
            focus["id"],
            depth=1,
            limit=40,
            relation_types={requested_relation} if requested_relation else None,
        )
        edges = graph["edges"]
        neighbors = [node for node in graph["nodes"] if node["id"] != focus["id"]]
        if requested_relation and neighbors:
            answer = (
                f"The graph links {focus['label']} to "
                f"{', '.join(node['label'] for node in neighbors[:8])} via {requested_relation}."
            )
        elif neighbors:
            relation_counts: dict[str, int] = {}
            for edge in edges:
                relation_counts[edge["type"]] = relation_counts.get(edge["type"], 0) + 1
            summary = ", ".join(
                f"{key} ({value})" for key, value in sorted(relation_counts.items())
            )
            answer = f"{focus['label']} has {len(edges)} retrieved relationships: {summary}."
        else:
            answer = (
                f"No matching relationships were found for {focus['label']} in the current seed."
            )
        return {
            "answer": answer,
            "strategy": "entity_neighborhood",
            "entities": entities,
            "graph": graph,
            "sources": self.store.sources_for_edges(edges),
        }
