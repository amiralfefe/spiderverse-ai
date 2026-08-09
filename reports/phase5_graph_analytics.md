# SpiderVerse AI — Phase 5 Graph Analytics

Validation date: 2026-08-09

Branch: `phase5-graph-analytics`

Immutable input: annotated tag `spiderverse-v1` at
`d1b40b3dd0361a770cfc004d79202b126a6b22b5`

## Scope and architecture

Phase 5 adds structural graph analysis only. It does not add or modify entities, relationships,
embeddings, generative models, graph-grounded generation, or the conceptual data model.

The implementation follows the existing backend boundary:

```text
FastAPI analytics routes
        ↓
GraphAnalyticsService
        ↓
deterministic NetworkX projection
        ↓
GraphStore snapshot
        ↓
JSON file or Neo4j adapter
```

Both storage modes therefore run the same algorithms over the same normalized node and edge
contract. The routes contain validation and response mapping, not analytics algorithms.

NetworkX `3.6.1` is pinned as the single new runtime dependency. The dataset remains byte-for-byte
identical to V1 after regeneration (SHA-256
`22E72CC202EE3206136715D87DBCB5285D830BAD394C38408B6F275BDDA9383B`).

## Graph projection

All analytics use an unweighted, undirected simple projection of the complete V1 graph:

- all 164 nodes and all relationship types are eligible;
- relationship direction is ignored for structural traversal;
- parallel relationships connecting the same pair collapse to one connection;
- self-loops are excluded from the projection;
- the original 574 relationship count is retained in overview responses;
- results are sorted by descending score, then case-insensitive label and stable entity ID.

This produces 567 unique connections. The projection matches the product's undirected exploration
semantics while avoiding artificial centrality inflation from multiple typed edges between one pair.

## Algorithms

### Degree centrality

NetworkX degree centrality is computed as `degree(v) / (n - 1)` on the full simple projection.
The response also exposes the raw unique-neighbor degree. Scores are rounded to 12 decimal places.

### Betweenness centrality

Exact normalized, unweighted betweenness is computed for every node with NetworkX's Brandes
implementation. There is no sampling or random component. The current graph size favors exactness
and clarity over approximate optimization.

### Community detection

Communities are calculated with greedy modularity maximization at NetworkX's default resolution
of `1`. The algorithm has no random seed. Nodes and edges enter the graph in sorted order, community
members are sorted, and final groups are ordered by descending size then stable IDs. Repeated runs
on the same dependency version and dataset are identical.

The API reports all detected groups and applies a display filter of `min_size=2` by default. Group
names such as `community-01` are structural identifiers; no Marvel faction name is hardcoded.

### Structural similarity

Character similarity is Jaccard overlap on direct-neighbor ID sets:

```text
J(A, B) = |neighbors(A) ∩ neighbors(B)| / |neighbors(A) ∪ neighbors(B)|
```

Candidates are Character nodes, while shared neighbors may be any entity type. Each result includes
the score, shared/union counts, and the actual shared nodes as minimal evidence. No embeddings are
used.

## API

| Endpoint | Purpose |
| --- | --- |
| `GET /api/analytics/overview` | Size, density, components, average degree, and community count |
| `GET /api/analytics/centrality` | Degree or betweenness ranking, optionally filtered by node type |
| `GET /api/analytics/communities` | Deterministic community partition with member/type evidence |
| `GET /api/analytics/similarity/{character_id}` | Jaccard ranking and shared-neighbor evidence |

Pydantic response models cover every payload. `metric` accepts only `degree` or `betweenness`,
limits and community sizes are bounded, and a missing or non-Character similarity target returns
HTTP 404.

## Measured V1 results

### Overview

| Metric | Result |
| --- | ---: |
| Nodes | 164 |
| Relationships | 574 |
| Unique connections | 567 |
| Density | 0.042421068382 |
| Average degree | 6.914634146341 |
| Connected components | 6 |
| Largest component | 159 nodes |
| Communities, including singletons | 12 |
| Communities with at least two nodes | 7 |
| Greedy-modularity score | 0.3604 |

### Centrality leaders among Characters

| Metric | Rank | Character | ID | Score | Unique neighbors |
| --- | ---: | --- | --- | ---: | ---: |
| Degree | 1 | Peter Parker | `peter-616` | 0.177914110429 | 29 |
| Degree | 2 | Miles Morales | `miles-1610` | 0.122699386503 | 20 |
| Betweenness | 1 | Peter Parker | `peter-616` | 0.057509744110 | 29 |
| Betweenness | 2 | Miles Morales | `miles-1610` | 0.052010618589 | 20 |

### Miles Morales structural similarity

| Rank | Character | ID | Jaccard score |
| --- | --- | --- | ---: |
| 1 | Peter Parker | `peter-1610` | 0.240000000000 |
| 2 | Rio Morales | `rio-1610` | 0.238095238095 |
| 3 | Billy Braddock | `spider-uk-833` | 0.200000000000 |

These values describe connectivity in the demonstration seed. They are not statements about canon,
story importance, or an exhaustive Marvel network.

## Frontend

The existing header now exposes an `Analytics` view. It keeps the V1 visual language and presents:

- four overview measures with visible values;
- degree and betweenness rankings with normalized bars, scores, universe IDs, and raw degree;
- computed community cards with member-type counts and representative members;
- a Character selector whose similarity results expose shared neighbors;
- an explicit projection/canon caveat.

The view is lazy-loaded and its four independent overview requests run in parallel. Mobile uses the
same evidence order in a single-column layout, without hover-only information.

## Tests and executed validation

| Check | Result |
| --- | --- |
| Dataset generation and validation | PASS — 164 nodes, 574 edges, 59 Characters; SHA-256 unchanged |
| Full backend tests | PASS — 14 tests |
| Analytics-specific tests | PASS — 5 tests |
| Ruff | PASS |
| ESLint | PASS |
| TypeScript | PASS |
| Vite production build | PASS |
| JSON ↔ Neo4j contract | PASS — 13 deterministic cases |
| Browser desktop | PASS — 1440×1000 |
| Browser mobile | PASS — 390×844, no horizontal overflow |
| Browser console | PASS — 0 warnings/errors |

The analytic tests cover exact degree and betweenness on a path graph, deterministic greedy
communities, Jaccard evidence, repeatability on the production seed, stable ordering for tied scores,
API response/error behavior, and the shared JSON/Neo4j contract.

The real Neo4j `5.26-community` container was healthy on ports 7474 and 7687. The conformance script
loaded the actual Neo4j snapshot and passed all eight V1 cases plus overview, degree, betweenness,
communities, and Miles similarity.

Browser QA loaded every analytics endpoint from the running FastAPI backend with HTTP 200, verified
the Miles results, changed the selector to Gwen Stacy, observed a recalculated top match of Jessica
Drew (`earth-332`) at 41.18%, and found no application console messages or framework overlay.

## Reproduction

From the repository root in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev,neo4j]"
.\.venv\Scripts\python.exe scripts\generate_dataset.py
.\.venv\Scripts\python.exe scripts\validate_graph.py
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m pytest backend\tests\test_analytics_service.py
.\.venv\Scripts\python.exe -m ruff check backend scripts

docker compose up -d neo4j
.\.venv\Scripts\python.exe scripts\seed_neo4j.py
.\.venv\Scripts\python.exe scripts\compare_backends.py

Set-Location frontend
npm.cmd run lint
.\node_modules\.bin\tsc.cmd --noEmit -p tsconfig.app.json
npm.cmd run build
```

For browser verification, run FastAPI on `127.0.0.1:8000`, Vite on `127.0.0.1:5173`, open the
Analytics view, and check both a 1440×1000 and 390×844 viewport.

## Limitations

- Direction and relationship semantics are intentionally flattened; influence and narrative flow
  should not be inferred from these scores.
- Parallel relation types collapse to one connection for structural metrics.
- All relation types contribute equally; high-frequency work, power, and universe links can shape
  communities and similarity.
- Greedy modularity is a heuristic, not a unique ground-truth partition.
- Five nodes form singleton components in this demonstration seed.
- Exact betweenness is appropriate for 164 nodes but would need reconsideration for a much larger
  graph.
- Results are reproducible for the pinned NetworkX version and the immutable V1 dataset.
