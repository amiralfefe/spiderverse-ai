from __future__ import annotations

from collections import Counter
from functools import cached_property
from typing import Any, Literal

import networkx as nx

from backend.app.graph_store import GraphStore

CentralityMetric = Literal["degree", "betweenness"]


class GraphAnalyticsService:
    """Deterministic, backend-agnostic analytics over a GraphStore snapshot."""

    community_algorithm = "greedy_modularity"
    similarity_metric = "jaccard_direct_neighbors"

    def __init__(self, store: GraphStore) -> None:
        self.store = store

    @cached_property
    def graph(self) -> nx.Graph:
        graph = nx.Graph()
        graph.add_nodes_from(sorted(self.store.node_by_id))
        graph.add_edges_from(
            sorted(
                (edge["source"], edge["target"])
                for edge in self.store.edges
                if edge["source"] != edge["target"]
            )
        )
        return graph

    @cached_property
    def _degree_scores(self) -> dict[str, float]:
        return nx.degree_centrality(self.graph)

    @cached_property
    def _betweenness_scores(self) -> dict[str, float]:
        return nx.betweenness_centrality(self.graph, normalized=True)

    @cached_property
    def _community_partition(self) -> tuple[tuple[str, ...], ...]:
        if self.graph.number_of_edges() == 0:
            groups = [(node_id,) for node_id in self.graph.nodes]
        else:
            groups = [
                tuple(sorted(group))
                for group in nx.community.greedy_modularity_communities(self.graph)
            ]
        return tuple(sorted(groups, key=lambda group: (-len(group), group)))

    def overview(self) -> dict[str, Any]:
        node_count = self.graph.number_of_nodes()
        unique_connections = self.graph.number_of_edges()
        components = list(nx.connected_components(self.graph))
        return {
            "nodes": len(self.store.nodes),
            "relationships": len(self.store.edges),
            "unique_connections": unique_connections,
            "density": self._round(nx.density(self.graph)),
            "average_degree": self._round(
                (2 * unique_connections / node_count) if node_count else 0.0
            ),
            "connected_components": len(components),
            "largest_component": max((len(component) for component in components), default=0),
            "communities": len(self._community_partition),
            "community_algorithm": self.community_algorithm,
        }

    def centrality(
        self,
        metric: CentralityMetric,
        *,
        node_type: str | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        scores = self._degree_scores if metric == "degree" else self._betweenness_scores
        candidates = [
            node
            for node in self.store.nodes
            if node_type is None or node["type"] == node_type
        ]
        candidates.sort(
            key=lambda node: (-scores[node["id"]], node["label"].casefold(), node["id"])
        )
        results = [
            {
                "rank": rank,
                "node": node,
                "score": self._round(scores[node["id"]]),
                "degree": self.graph.degree[node["id"]],
            }
            for rank, node in enumerate(candidates[:limit], start=1)
        ]
        return {
            "metric": metric,
            "node_type": node_type,
            "total_considered": len(candidates),
            "results": results,
        }

    def communities(self, *, min_size: int = 2) -> dict[str, Any]:
        partition = [set(group) for group in self._community_partition]
        modularity = (
            nx.community.modularity(self.graph, partition)
            if self.graph.number_of_edges() and partition
            else 0.0
        )
        visible_groups = [group for group in self._community_partition if len(group) >= min_size]
        communities = []
        for index, group in enumerate(visible_groups, start=1):
            members = sorted(
                (self.store.node_by_id[node_id] for node_id in group),
                key=lambda node: (node["type"], node["label"].casefold(), node["id"]),
            )
            communities.append(
                {
                    "id": f"community-{index:02d}",
                    "size": len(members),
                    "member_types": dict(
                        sorted(Counter(node["type"] for node in members).items())
                    ),
                    "members": members,
                }
            )
        return {
            "algorithm": self.community_algorithm,
            "modularity": self._round(modularity),
            "count": len(communities),
            "total_count": len(self._community_partition),
            "min_size": min_size,
            "communities": communities,
        }

    def similarity(self, character_id: str, *, limit: int = 10) -> dict[str, Any]:
        source = self.store.get_node(character_id)
        if source is None or source["type"] != "Character":
            raise ValueError("Character not found")

        source_neighbors = set(self.graph.neighbors(character_id))
        results = []
        for candidate in self.store.nodes:
            if candidate["type"] != "Character" or candidate["id"] == character_id:
                continue
            candidate_neighbors = set(self.graph.neighbors(candidate["id"]))
            shared_ids = source_neighbors & candidate_neighbors
            union_ids = source_neighbors | candidate_neighbors
            results.append(
                {
                    "node": candidate,
                    "score": self._round(len(shared_ids) / len(union_ids) if union_ids else 0.0),
                    "shared_neighbor_count": len(shared_ids),
                    "union_neighbor_count": len(union_ids),
                    "shared_neighbors": sorted(
                        (self.store.node_by_id[node_id] for node_id in shared_ids),
                        key=lambda node: (node["label"].casefold(), node["id"]),
                    ),
                }
            )
        results.sort(
            key=lambda result: (
                -result["score"],
                result["node"]["label"].casefold(),
                result["node"]["id"],
            )
        )
        return {
            "source": source,
            "metric": self.similarity_metric,
            "compared_type": "Character",
            "results": results[:limit],
        }

    @staticmethod
    def _round(value: float) -> float:
        return round(float(value), 12)
