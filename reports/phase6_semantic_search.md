# SpiderVerse AI — Phase 6 Semantic Search

Validation date: 2026-08-09

Branch: `phase6-semantic-search`

Immutable input: annotated tag `spiderverse-phase5` at
`2478705dfc1aa86631dc44c6b60b27b859f0defd`

## Architecture

Phase 6 is search-only. It does not add an LLM, GraphRAG, generated answers, Natural Language to
Cypher, a vector database, or new graph data.

```text
GET /api/search?mode=lexical|semantic|hybrid
                    ↓
               SearchService
          ┌─────────┴─────────┐
          ↓                   ↓
 V1 lexical score     normalized embeddings
          └─────────┬─────────┘
                    ↓
             weighted ranker
                    ↓
                GraphStore
               /          \
            JSON          Neo4j
```

`SearchService` owns document construction, lazy index construction, ranking, score transparency,
and stable tie-breaking. FastAPI validates the mode and limits but contains no embedding or ranking
logic. Both storage backends still normalize into the existing `GraphStore`, so the search layer is
not a parallel persistence architecture.

### Lexical pipeline

The V1 name/alias behavior is retained exactly. Input is case-folded, punctuation becomes spaces,
and surrounding/repeated non-alphanumeric separators collapse. Each entity receives the best of:

- exact normalized name or alias: `1.0`;
- query contained in a normalized name or alias: `0.85`;
- otherwise `0.7 × SequenceMatcher ratio`.

Only lexical scores of at least `0.34` are returned. V1 ordering remains final score descending,
then entity label and stable ID. API requests without `mode` remain lexical for V1 compatibility.

### Semantic pipeline

The selected embedding model is
[`sentence-transformers/multi-qa-MiniLM-L6-cos-v1`](https://huggingface.co/sentence-transformers/multi-qa-MiniLM-L6-cos-v1)
at revision `b207367332321f8e44f96e224ef15bc607f4dbf0`, loaded on CPU with
`sentence-transformers==5.7.0`. It is a compact, non-generative, English retrieval model designed
for semantic search and produces 384-dimensional normalized embeddings.

Documents and queries are L2-normalized. The matrix dot product is therefore cosine similarity.
For combination with the `[0, 1]` lexical score, cosine is mapped with
`semantic_score = clamp((cosine + 1) / 2, 0, 1)`. Responses expose both the mapped search score and
the raw cosine value; neither is described as probability or confidence.

### Hybrid pipeline

The measured formula is:

```text
hybrid_score = 0.22 × lexical_score + 0.78 × semantic_score
```

The lexical coefficient is centralized in `SEARCH_HYBRID_LEXICAL_WEIGHT` and validated within
`[0, 1]`. The value `0.22` was selected from a small global sweep after comparing Top-1, Hit@3,
and MRR; no benchmark query or entity is hardcoded in the engine. Hybrid improves the benchmark
and keeps the exact/alias cases at rank 1, so the React control defaults to Hybrid. The API default
remains Lexical to avoid silently changing existing clients.

## Embeddings

| Property | Value |
| --- | --- |
| Model | `sentence-transformers/multi-qa-MiniLM-L6-cos-v1` |
| Immutable revision | `b207367332321f8e44f96e224ef15bc607f4dbf0` |
| Runtime | `sentence-transformers==5.7.0`, PyTorch CPU |
| Dimensions | 384 |
| Normalization | L2 on documents and queries |
| Similarity | cosine through normalized dot product |
| Generation | none |
| External inference API | none |

The Docker image explicitly installs `torch==2.13.0+cpu` from the PyTorch CPU index. This avoids
pulling Linux CUDA runtime libraries for a CPU-only feature.

## Index

The index contains one document for each of the 164 existing graph entities, sorted by ID. A
document uses only present properties: type, label, sorted aliases, description, designation,
status, power profile, work type, universe label/designation, and universe description. Including
the real Earth-928 description — “The future setting associated with 2099.” — makes the future
Spider-Man query grounded rather than hardcoded.

The same builder runs over JSON and Neo4j snapshots. The final corpus SHA-256 signature is
`b3485105a3e7eaa1c91086e95b05b133ec2d666b0e0c3a3274dae2c8e1464116` for both backends.

The embeddings are built lazily and retained only in memory. The `164 × 384` float32 matrix uses
251,904 bytes. No vector database, generated index file, model weight, Hugging Face cache, or Torch
cache is versioned. A clean installation downloads the pinned model once into the user cache and
reconstructs the matrix from the graph.

## Ranking

Every API result includes entity ID, label, type, aliases when present, universe label when
available, final search score, lexical score, semantic score, and raw cosine. The frontend shows
the selected mode's final score and keeps the component scores available through the API for
testing and debugging.

Semantic and Hybrid stable ordering is `score DESC`, `label.casefold() ASC`, `id ASC`; Lexical
retains the V1 `score DESC`, `label ASC`, `id ASC` ordering. Unit tests cover exact ties.

## Benchmark

`data/fixtures/search_benchmark.json` contains 15 evaluation queries only; it does not extend or
modify `graph.json`. A rank is the best rank among the listed relevant IDs, which lets the
deliberately broad “symbiote enemy” case accept either Venom or Carnage.

| Query | Expected | Lexical rank | Semantic rank | Hybrid rank |
| --- | --- | ---: | ---: | ---: |
| Miles Morales | `miles-1610` | 1 | 3 | 1 |
| Ghost-Spider | `gwen-65` | 1 | 2 | 1 |
| Spider-Man 2099 | `miguel-928` | 1 | 1 | 1 |
| SP//dr | `peni-14512` | 1 | 1 | 1 |
| geneticist Spider-Man from 2099 | `miguel-928` | 1 | 1 | 1 |
| pilot linked to a spider-powered mech | `peni-14512` | — | 1 | 1 |
| scientist who creates interdimensional portals | `spot-616` | — | 1 | 1 |
| journalist bonded to an alien symbiote | `venom-616` | — | 3 | 3 |
| lawyer and street-level vigilante | `daredevil-616` | — | 1 | 1 |
| rebellious Spider-Man fighting oppressive systems | `hobie-138` | — | 3 | — |
| motorcycle-riding Spider-Woman from Earth-332 | `spider-woman-332` | — | 1 | 1 |
| digital Spider hero in virtual reality | `spider-byte-22191` | — | 1 | 1 |
| Myles Moralez | `miles-1610` | 1 | — | 1 |
| Spider-Man from the future | `miguel-928` | — | 1 | 2 |
| symbiote enemy | `venom-616` or `carnage-616` | — | 2 | 2 |

| Mode | Top-1 | Hit@3 | MRR |
| --- | ---: | ---: | ---: |
| Lexical | 40.0% | 40.0% | 0.400 |
| Semantic | 60.0% | 93.3% | 0.733 |
| Hybrid | 73.3% | 93.3% | 0.822 |

Hybrid improves Top-1 by 33.3 percentage points and MRR by 0.422 over V1 lexical search. The
benchmark also preserves a visible failure: Hobie Brown is rank 3 in Semantic but outside Hybrid's
top three because name-oriented lexical noise promotes work titles. No result was altered to hide
that limitation.

## Backend parity

The real Neo4j `5.26-community` container was healthy on ports 7474 and 7687. The seed completed
with 164 nodes and 574 relationships. `scripts/compare_backends.py` passed 18 deterministic cases:

- the 13 V1 + Analytics contracts;
- corpus entity count;
- ordered entity IDs;
- every normalized index document;
- corpus signature;
- lexical, semantic, and hybrid top-3 results and scores for all benchmark queries.

JSON and Neo4j produced identical search corpora and top-k results using the same pinned model and
parameters.

## Performance

Measured locally on CPU with the model already cached:

| Measure | Result |
| --- | ---: |
| Document count | 164 |
| Matrix dimensions | `164 × 384` |
| Matrix bytes | 251,904 |
| Model load + index build | 4.818 s |
| Mean Lexical query | 4.162 ms |
| Mean Semantic query | 8.622 ms |
| Mean Hybrid query | 8.472 ms |

The first clean semantic request also pays the one-time model download. Timings are indicative for
this machine, not cross-hardware guarantees.

## Validation

| Check | Result |
| --- | --- |
| Dataset generation and validation | PASS — 164 nodes, 574 relationships, 59 Characters |
| Dataset SHA-256 | PASS — `22E72CC202EE3206136715D87DBCB5285D830BAD394C38408B6F275BDDA9383B` |
| Full backend tests | PASS — 21 tests; one dependency deprecation warning |
| Search tests | PASS — deterministic docs, lexical, real model, hybrid, scores, API, benchmark |
| Analytics regression tests | PASS |
| Ruff | PASS |
| ESLint | PASS |
| TypeScript | PASS through `tsc --noEmit -p tsconfig.app.json` |
| Vite production build | PASS |
| Docker Compose config | PASS |
| Docker backend image | PASS — explicit PyTorch CPU wheel |
| Docker frontend image | PASS |
| Neo4j and seed | PASS — healthy, seed exit 0 |
| JSON ↔ Neo4j parity | PASS — 18/18 |
| Browser desktop | PASS — 1440×1000 |
| Browser mobile | PASS — 390×844, no horizontal overflow |
| Browser console | PASS — 0 warnings/errors |

Browser QA exercised exact Miles Morales search, Ghost-Spider alias search, the future Spider-Man
semantic query, Lexical/Semantic/Hybrid switching, opening Miguel O'Hara into the graph and entity
inspector, the graph-grounded mentor question, Miles-to-Daredevil Path Finder at two hops, Analytics,
and the responsive mobile filter panel. No framework overlay appeared.

Two non-blocking dependency/runtime notices remain visible outside the browser: Starlette warns that
its current `httpx` TestClient bridge is deprecated, and the first containerized model download
notes that unauthenticated Hugging Face requests have lower rate limits. Neither requires or uses a
secret, and both validations complete successfully.

## Reproduction

From the repository root in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev,neo4j]"
.\.venv\Scripts\python.exe scripts\generate_dataset.py
.\.venv\Scripts\python.exe scripts\validate_graph.py
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check backend scripts
.\.venv\Scripts\python.exe scripts\benchmark_search.py

docker compose config --quiet
docker compose build backend frontend
docker compose up -d backend frontend
.\.venv\Scripts\python.exe scripts\compare_backends.py

Set-Location frontend
npm.cmd run lint
.\node_modules\.bin\tsc.cmd --noEmit -p tsconfig.app.json
npm.cmd run build
```

The first command that loads semantic search needs network access to download the pinned public
model. Later executions can use the local Hugging Face cache.

## Limitations

- The demonstration graph is small and non-canonical; benchmark metrics do not generalize to a
  comprehensive Marvel corpus.
- Retrieval quality depends on the descriptions already present in the graph and on a generic
  English embedding model.
- Hybrid misses Hobie Brown at Hit@3 for one descriptive query; Semantic ranks him third.
- The future Spider-Man example is rank 1 in Semantic and rank 2 in Hybrid, not rank 1 in both.
- Venom is rank 3 for its long descriptive query; the broad symbiote query returns a relevant
  symbiote entity at rank 2.
- Semantic mode always returns the best-ranked entities even for an unrelated query; scores are
  ranking signals, not calibrated relevance thresholds, confidence, or probability.
- First use requires downloading the pinned model; Windows without symlink support may use more
  Hugging Face cache disk space.
- The public model download is intentionally unauthenticated and can therefore be subject to lower
  Hugging Face rate limits.
- The in-memory exact matrix is appropriate for 164 entities and would need reevaluation at much
  larger scale.
- There is intentionally no LLM, GraphRAG, generative answer, external vector service, or Phase 7
  behavior.
