from __future__ import annotations

from typing import Any

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
