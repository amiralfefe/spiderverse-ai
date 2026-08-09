from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class GraphNode(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    label: str
    type: str


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    type: str
    properties: dict[str, Any] = Field(default_factory=dict)


class GraphPayload(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    focus_id: str | None = None


class CharacterDetail(BaseModel):
    character: GraphNode
    universe: GraphNode | None = None
    powers: list[GraphNode] = Field(default_factory=list)
    works: list[GraphNode] = Field(default_factory=list)
    relations: list[dict[str, Any]] = Field(default_factory=list)
    sources: list[dict[str, Any]] = Field(default_factory=list)


class PathPayload(BaseModel):
    found: bool
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
    hops: int | None = None


class AskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=500)


class AskResponse(BaseModel):
    answer: str
    strategy: str
    entities: list[GraphNode] = Field(default_factory=list)
    graph: GraphPayload
    sources: list[dict[str, Any]] = Field(default_factory=list)


class StatsPayload(BaseModel):
    nodes: int
    relationships: int
    by_type: dict[str, int]
    verified_relationships: int
    demo_relationships: int


class SearchResult(GraphNode):
    universe_label: str | None = None
    search_mode: Literal["lexical", "semantic", "hybrid"]
    score: float
    lexical_score: float
    semantic_score: float | None = None
    semantic_cosine: float | None = None


class AnalyticsOverview(BaseModel):
    nodes: int
    relationships: int
    unique_connections: int
    density: float
    average_degree: float
    connected_components: int
    largest_component: int
    communities: int
    community_algorithm: str


class CentralityResult(BaseModel):
    rank: int
    node: GraphNode
    score: float
    degree: int


class CentralityPayload(BaseModel):
    metric: Literal["degree", "betweenness"]
    node_type: str | None = None
    total_considered: int
    results: list[CentralityResult]


class CommunityResult(BaseModel):
    id: str
    size: int
    member_types: dict[str, int]
    members: list[GraphNode]


class CommunitiesPayload(BaseModel):
    algorithm: str
    modularity: float
    count: int
    total_count: int
    min_size: int
    communities: list[CommunityResult]


class SimilarityResult(BaseModel):
    node: GraphNode
    score: float
    shared_neighbor_count: int
    union_neighbor_count: int
    shared_neighbors: list[GraphNode]


class SimilarityPayload(BaseModel):
    source: GraphNode
    metric: Literal["jaccard_direct_neighbors"]
    compared_type: Literal["Character"]
    results: list[SimilarityResult]
