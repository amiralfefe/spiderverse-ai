# SpiderVerse AI

**Knowledge Graph & GraphRAG Explorer**

SpiderVerse AI is a graph-first exploration tool for characters, variants, universes, works, events, teams, powers, and their sourced relationships. The V1 deliberately focuses on clean graph data, deterministic queries, API design, and interactive exploration before introducing an LLM.

## What is included

- A deterministic seed dataset with 59 characters, 18 universes, 50 works, 10 events, teams, powers, and 574 relationships.
- Dataset validation for IDs, duplicates, dangling edges, universe references, variants, and relation provenance.
- A FastAPI service with local JSON storage by default and an optional Neo4j adapter.
- Lexical, semantic, and hybrid entity search with transparent ranking scores.
- Entity details, neighborhood expansion, universe filtering, and shortest-path queries.
- A graph-grounded `Ask` endpoint that answers from retrieved graph facts without an LLM.
- A React + TypeScript + Cytoscape.js explorer with character, universe, and path-finder views.
- Deterministic graph analytics for degree, betweenness, communities, and structural character similarity.
- A dedicated React Analytics view with rankings, community membership, and shared-neighbor evidence.
- Docker Compose for frontend, backend, and Neo4j.
- Backend tests, frontend checks, and GitHub Actions CI.

## Quick start

### 1. Generate and validate the dataset

```powershell
python scripts/generate_dataset.py
python scripts/validate_graph.py
```

### 2. Start the backend

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev,neo4j]"
.\.venv\Scripts\python -m uvicorn backend.app.main:app --reload --port 8000
```

### 3. Start the frontend

```powershell
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

## Docker

```powershell
docker compose up --build
```

The frontend is served on `http://127.0.0.1:5173`, FastAPI on `http://127.0.0.1:8000`, and Neo4j Browser on `http://127.0.0.1:7474`.

## Neo4j mode

JSON is the safe default so the project works immediately. To use Neo4j, set:

```text
GRAPH_BACKEND=neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=spiderverse-local
```

Then seed the database:

```powershell
python scripts/seed_neo4j.py
```

Run the deterministic backend conformance suite while Neo4j is available:

```powershell
python scripts/compare_backends.py
```

The API contract stays the same in both modes. The reference integrity and traversal queries
are documented in [docs/reference-cypher.md](docs/reference-cypher.md).

## Graph analytics

Phase 5 computes analytics from the same `GraphStore` snapshot used by the JSON and Neo4j
backends. It uses an undirected simple projection, so parallel relationships between the same
two entities count once in structural metrics while the original relationship count remains
available in the overview.

Available endpoints:

- `GET /api/analytics/overview`
- `GET /api/analytics/centrality?metric=degree&node_type=Character&limit=10`
- `GET /api/analytics/centrality?metric=betweenness&node_type=Character&limit=10`
- `GET /api/analytics/communities?min_size=2`
- `GET /api/analytics/similarity/miles-1610?limit=10`

Implementation choices, measured V1 results, limitations, and reproduction commands are in
[the Phase 5 report](reports/phase5_graph_analytics.md).

## Semantic search

Phase 6 derives one deterministic search document per graph entity and keeps the Knowledge Graph
as the source of truth. The API preserves the V1 lexical default while exposing three explicit
modes:

- `GET /api/search?q=Miles%20Morales&mode=lexical`
- `GET /api/search?q=Spider-Man%20from%20the%20future&mode=semantic`
- `GET /api/search?q=symbiote%20enemy&mode=hybrid`

Semantic search uses the local, non-generative
[`sentence-transformers/multi-qa-MiniLM-L6-cos-v1`](https://huggingface.co/sentence-transformers/multi-qa-MiniLM-L6-cos-v1)
model at an immutable revision. The 384-dimensional normalized embeddings stay in a small
in-memory matrix; no vector database, API key, LLM, or persisted model/index artifact is required.
The first semantic request downloads the model into the user cache when it is not already present.

Run the deterministic 15-query comparison:

```powershell
python scripts/benchmark_search.py
```

The measured ranking, architecture, JSON/Neo4j parity, performance, validation, and limitations
are documented in [the Phase 6 report](reports/phase6_semantic_search.md).

## Important data note

This repository ships a **demonstration seed**, not an authoritative Marvel canon database. Core relationships have recognizable work-level provenance. Scale-building associations are explicitly marked `verified: false` and surface as demo evidence in the UI. They are suitable for software and graph demonstrations, not canonical research.

See [architecture](docs/architecture.md), [data model](docs/data-model.md), [reference Cypher](docs/reference-cypher.md), and [roadmap](docs/roadmap.md).
