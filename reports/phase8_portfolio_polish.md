# SpiderVerse AI — Portfolio Polish / Phase 8

Validation date: 2026-08-09

Branch: `phase8-portfolio-polish`

Immutable technical baseline: annotated tag `spiderverse-phase6` at `2caeff7820f7772b16c0921f77bb5218d221ad93`.

## Initial state

The initial Git gate passed before any file was changed:

- current branch: `phase7-graphrag`;
- `HEAD`: `2caeff7820f7772b16c0921f77bb5218d221ad93`;
- `main` and `origin/main`: `2caeff7820f7772b16c0921f77bb5218d221ad93`;
- `spiderverse-v1^{}`: `d1b40b3dd0361a770cfc004d79202b126a6b22b5`;
- `spiderverse-phase5^{}`: `2478705dfc1aa86631dc44c6b60b27b859f0defd`;
- `spiderverse-phase6^{}`: `2caeff7820f7772b16c0921f77bb5218d221ad93`;
- local and remote `phase7-graphrag`: `2caeff7820f7772b16c0921f77bb5218d221ad93`;
- worktree: clean.

The portfolio branch was then created directly from `spiderverse-phase6`, not from Phase 7. No Phase 7 file or commit was reused or changed.

## README changes

The README was retained as a technical landing page rather than rebuilt as a marketing site. Existing accurate setup and backend information was preserved and reorganized around a faster recruiter reading path:

1. clear `Knowledge Graph & Semantic Search Explorer` positioning;
2. visible 164/574/59/18/50 dataset facts;
3. real application screenshot near the hero;
4. concise project rationale and delivered features;
5. current Mermaid architecture without an active LLM;
6. entity and relationship data-model summary;
7. measured Graph Analytics results;
8. Phase 6 Search benchmark and retained Hobie Brown limitation;
9. JSON ↔ Neo4j parity evidence;
10. compact technology stack, Quick Start, validation, structure, limitations, roadmap, and portfolio skills.

The real `.github/workflows/ci.yml` workflow is the only source used for the CI badge. Eleven local README links were checked; broken links: 0.

GraphRAG is stated only as planned future work. Deterministic `POST /api/ask` is explicitly described as graph-grounded and non-LLM.

## Final screenshots

All images were captured from the running React application against the local JSON backend. The configured test viewports were 1440 × 1000 for Desktop and 390 × 844 for Mobile. The in-app browser's captured content area excludes its own chrome, producing the pixel dimensions recorded below.

| File | Captured pixels | Screen and real validation |
| --- | ---: | --- |
| `docs/assets/graph-explorer-desktop.png` | 1236 × 990 | Miles Morales neighborhood, loaded graph, filters, inspector, no overlay |
| `docs/assets/semantic-search-desktop.png` | 1236 × 990 | Semantic query `Spider-Man from the future`; Miguel O'Hara visible at rank 1 |
| `docs/assets/analytics-desktop.png` | 1236 × 990 | Overview plus Degree/Betweenness rankings; Peter Parker visible at rank 1 |
| `docs/assets/path-finder-desktop.png` | 1248 × 1000 | Miles Morales → Avengers → Matt Murdock, 2 hops |
| `docs/assets/mobile-overview.png` | 375 × 812 | 390 × 844 test viewport, Miles context, filter panel opened through the real toggle |

No mockup, DevTools surface, error overlay, cursor treatment, or fabricated result appears in these files. The older design concept remains under `docs/design/` and is not presented as product evidence.

## Architecture presentation

`docs/architecture.md` now documents the real active system:

```text
React / Cytoscape.js
        ↓
FastAPI
        ↓
QueryService + SearchService + GraphAnalyticsService
        ↓
GraphStore
        ↓
JSONGraphStore / Neo4jGraphStore
```

A second Mermaid diagram explains deterministic document construction, 384-dimensional embeddings, cosine similarity, and the Hybrid ranker. Mermaid was selected as a documentation-first UML-like component view because GitHub renders the source directly and the surrounding module tables provide a text fallback. Both diagrams use a vertical reading order suitable for narrow layouts.

The obsolete roadmap was corrected to show V1, Graph Analytics, and Semantic/Hybrid Search as delivered. Grounded GraphRAG is kept in a separate Future Work section and is not part of the active architecture.

## Metrics presented

Only measured Phase 5 and Phase 6 results are exposed:

- 164 nodes, 574 relationships, and 567 unique structural connections;
- 6 connected components and a 159-node largest component;
- 12 communities and modularity 0.3604;
- Peter Parker (`peter-616`) as the leading Character for Degree and Betweenness;
- Lexical Top-1 40.0%, Hit@3 40.0%, MRR 0.400;
- Semantic Top-1 60.0%, Hit@3 93.3%, MRR 0.733;
- Hybrid Top-1 73.3%, Hit@3 93.3%, MRR 0.822;
- 18/18 deterministic JSON ↔ Neo4j Phase 6 contracts.

No metric, benchmark fixture, relationship, graph entity, Hybrid weight, or search algorithm changed in this portfolio lot.

## QA desktop/mobile

### Environment

- Browser: Codex in-app Browser, available and used directly;
- URL: `http://127.0.0.1:5173/`;
- backend: FastAPI on `127.0.0.1:8000`, `backend=local`;
- configured viewports: 1440 × 1000 and 390 × 844.

### Executed Desktop flows

- page identity and meaningful first render;
- Graph Explorer loaded on Miles Morales;
- Characters displayed 59 entities;
- Universes displayed 18 realities;
- Semantic Search returned Miguel O'Hara first for the future Spider-Man query;
- Hybrid Search returned its real scored ordering without alteration;
- Analytics loaded overview, rankings, communities, and similarity data;
- Path Finder returned Miles Morales → Avengers → Matt Murdock in 2 hops;
- deterministic Ask returned `The graph links Miles Morales to Peter B. Parker via MENTORED_BY.`;
- selecting Gwen Stacy from graph evidence refocused the explorer.

### Executed Mobile flows

- primary navigation remained usable;
- filter toggle changed `aria-expanded` from `false` to `true`;
- Explorer and Analytics rendered without horizontal overflow;
- Lexical alias search `Ghost-Spider` returned Gwen Stacy first at score 1.000;
- body/document width remained 375 px inside the configured 390 px viewport.

### Browser result

- blank page: 0;
- framework/error overlay: 0;
- application alerts: 0;
- console warnings/errors: 0;
- desktop horizontal overflow: 0;
- mobile horizontal overflow: 0.

No frontend code or visual correction was necessary.

## Regression validation

| Check | Executed result |
| --- | --- |
| Dataset generation | PASS — deterministic generator completed |
| Dataset validation | PASS — 164 nodes, 574 edges, 59 Characters |
| Dataset SHA-256 | PASS — `22E72CC202EE3206136715D87DBCB5285D830BAD394C38408B6F275BDDA9383B` |
| Full backend tests | PASS — 21 tests, one known Starlette deprecation warning |
| Ruff | PASS — `All checks passed!` |
| ESLint | PASS — zero warnings allowed |
| TypeScript | PASS — `tsc --noEmit -p tsconfig.app.json` |
| Vite production build | PASS — 1,592 modules, 7.99 s |
| Search benchmark | PASS — Lexical/Semantic/Hybrid metrics unchanged |
| Docker Compose config | PASS |
| Docker / Compose | PASS — Docker 29.6.2, Compose v5.3.1 |
| Real Neo4j | PASS — running, healthy, Bolt reachable, HTTP 200, zero blocking log lines |
| Neo4j seed | PASS — 164 nodes and 574 relationships |
| JSON ↔ Neo4j parity | PASS — 18/18 deterministic cases |

The first sandboxed Search benchmark attempt could not perform Hugging Face HEAD checks, and the first sandboxed Vite build could not write below `node_modules/.vite-temp`. Authorized local reruns passed. These were execution-sandbox restrictions, not product failures.

## Dataset integrity

The dataset was regenerated and validated during this lot. Its SHA-256 remains exactly `22E72CC202EE3206136715D87DBCB5285D830BAD394C38408B6F275BDDA9383B`, proving that portfolio work did not change graph content.

## Git hygiene

- `.env.local` is ignored, untracked, and never used by this phase;
- no `OPENAI_API_KEY` value or other secret value appears in any tracked/staged artifact;
- no environment file, key, token, Hugging Face cache, model weight, virtual environment, dependency directory, build output, Neo4j volume, browser temporary file, or local log is intended for the commit;
- durable PNG files under `docs/assets/` are the only new binary artifacts;
- `main`, `phase7-graphrag`, and all three historical tags remain unchanged;
- no force-push, merge, tag creation, deployment, LLM call, or GraphRAG work occurred.

## Known limitations

- The 164-entity graph is a deliberately limited, non-canonical demonstration seed.
- Semantic retrieval quality depends on graph descriptions and a generic English embedding model.
- The Search benchmark contains only 15 queries and does not establish broad generalization.
- Hybrid misses the documented Hobie Brown query at Hit@3.
- The exact in-memory embedding matrix is sized for the current corpus.
- First Semantic use downloads the pinned public model.
- Grounded GraphRAG is not implemented or validated.

## Future work

Grounded GraphRAG remains future work. It must retrieve a bounded subgraph before generation, expose relation-level provenance, abstain on insufficient evidence, and pass anti-hallucination plus JSON ↔ Neo4j retrieval-parity tests before it can be presented as delivered.

## Status

**SpiderVerse AI Portfolio Polish — validated on branch `phase8-portfolio-polish`.**
