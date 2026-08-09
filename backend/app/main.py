from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.app.analytics_service import CentralityMetric, GraphAnalyticsService
from backend.app.config import settings
from backend.app.graph_store import GraphStore, build_store
from backend.app.models import (
    AnalyticsOverview,
    AskRequest,
    AskResponse,
    CentralityPayload,
    CharacterDetail,
    CommunitiesPayload,
    GraphNode,
    GraphPayload,
    PathPayload,
    SimilarityPayload,
    StatsPayload,
)
from backend.app.query_service import QueryService


def create_app(store: GraphStore | None = None) -> FastAPI:
    graph_store = store or build_store(settings)
    query_service = QueryService(graph_store)
    analytics_service = GraphAnalyticsService(graph_store)
    app = FastAPI(
        title="SpiderVerse AI API",
        version="0.1.0",
        description="Graph-first retrieval API for the SpiderVerse AI demonstration dataset.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "backend": settings.graph_backend}

    @app.get("/api/stats", response_model=StatsPayload)
    def stats() -> dict:
        return graph_store.stats()

    @app.get("/api/search", response_model=list[GraphNode])
    def search(
        q: str = Query(min_length=1, max_length=100),
        node_type: str | None = None,
        limit: int = Query(default=12, ge=1, le=50),
    ) -> list[dict]:
        types = {node_type} if node_type else None
        return graph_store.search(q, node_types=types, limit=limit)

    @app.get("/api/characters", response_model=list[GraphNode])
    def characters(
        q: str | None = None,
        universe_id: str | None = None,
        limit: int = Query(default=100, ge=1, le=250),
    ) -> list[dict]:
        return graph_store.list_nodes(
            node_type="Character", universe_id=universe_id, query=q, limit=limit
        )

    @app.get("/api/characters/{character_id}", response_model=CharacterDetail)
    def character(character_id: str) -> dict:
        result = graph_store.character_detail(character_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Character not found")
        return result

    @app.get("/api/characters/{character_id}/relations", response_model=GraphPayload)
    def character_relations(
        character_id: str,
        depth: int = Query(default=1, ge=1, le=3),
        limit: int = Query(default=80, ge=2, le=250),
    ) -> dict:
        if graph_store.get_node(character_id) is None:
            raise HTTPException(status_code=404, detail="Character not found")
        return graph_store.neighborhood(character_id, depth=depth, limit=limit)

    @app.get("/api/universes", response_model=list[GraphNode])
    def universes() -> list[dict]:
        result = graph_store.list_nodes(node_type="Universe", limit=100)
        counts = {
            universe["id"]: sum(
                node.get("type") == "Character" and node.get("universe_id") == universe["id"]
                for node in graph_store.nodes
            )
            for universe in result
        }
        return [{**universe, "character_count": counts[universe["id"]]} for universe in result]

    @app.get("/api/graph", response_model=GraphPayload)
    def graph(
        focus_id: str | None = None,
        depth: int = Query(default=1, ge=1, le=3),
        limit: int = Query(default=80, ge=2, le=250),
        universe_id: str | None = None,
        node_types: str | None = None,
        relation_types: str | None = None,
    ) -> dict:
        types = set(node_types.split(",")) if node_types else None
        relations = set(relation_types.split(",")) if relation_types else None
        result = graph_store.neighborhood(
            focus_id,
            depth=depth,
            limit=limit,
            node_types=types,
            relation_types=relations,
            universe_id=universe_id,
        )
        if focus_id and not result["nodes"]:
            raise HTTPException(status_code=404, detail="Focus node not found")
        return result

    @app.get("/api/path", response_model=PathPayload)
    def path(start_id: str, end_id: str) -> dict:
        return graph_store.shortest_path(start_id, end_id)

    @app.post("/api/ask", response_model=AskResponse)
    def ask(payload: AskRequest) -> dict:
        return query_service.ask(payload.question)

    @app.get("/api/analytics/overview", response_model=AnalyticsOverview)
    def analytics_overview() -> dict:
        return analytics_service.overview()

    @app.get("/api/analytics/centrality", response_model=CentralityPayload)
    def analytics_centrality(
        metric: CentralityMetric,
        node_type: str | None = None,
        limit: int = Query(default=10, ge=1, le=100),
    ) -> dict:
        return analytics_service.centrality(metric, node_type=node_type, limit=limit)

    @app.get("/api/analytics/communities", response_model=CommunitiesPayload)
    def analytics_communities(
        min_size: int = Query(default=2, ge=1, le=100),
    ) -> dict:
        return analytics_service.communities(min_size=min_size)

    @app.get("/api/analytics/similarity/{character_id}", response_model=SimilarityPayload)
    def analytics_similarity(
        character_id: str,
        limit: int = Query(default=10, ge=1, le=100),
    ) -> dict:
        character = graph_store.get_node(character_id)
        if character is None or character["type"] != "Character":
            raise HTTPException(status_code=404, detail="Character not found")
        return analytics_service.similarity(character_id, limit=limit)

    app.state.graph_store = graph_store
    app.state.analytics_service = analytics_service
    return app


app = create_app()
