# SpiderVerse AI

**Knowledge Graph & GraphRAG Explorer**

SpiderVerse AI is a graph-first exploration tool for characters, variants, universes, works, events, teams, powers, and their sourced relationships. The V1 deliberately focuses on clean graph data, deterministic queries, API design, and interactive exploration before introducing an LLM.

## What is included

- A deterministic seed dataset with 59 characters, 18 universes, 50 works, 10 events, teams, powers, and 574 relationships.
- Dataset validation for IDs, duplicates, dangling edges, universe references, variants, and relation provenance.
- A FastAPI service with local JSON storage by default and an optional Neo4j adapter.
- Search, entity details, neighborhood expansion, universe filtering, and shortest-path queries.
- A graph-grounded `Ask` endpoint that answers from retrieved graph facts without an LLM.
- A React + TypeScript + Cytoscape.js explorer with character, universe, and path-finder views.
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

## Important data note

This repository ships a **demonstration seed**, not an authoritative Marvel canon database. Core relationships have recognizable work-level provenance. Scale-building associations are explicitly marked `verified: false` and surface as demo evidence in the UI. They are suitable for software and graph demonstrations, not canonical research.

See [architecture](docs/architecture.md), [data model](docs/data-model.md), [reference Cypher](docs/reference-cypher.md), and [roadmap](docs/roadmap.md).
