# Roadmap

## Delivered milestones

### V1 — Knowledge Graph core

- deterministic dataset generation and validation;
- JSON and Neo4j 5.26 adapters;
- search, details, neighborhood exploration, universe browsing, and path finding;
- deterministic graph-grounded Ask;
- React/Cytoscape interface, tests, Docker, CI, and JSON ↔ Neo4j parity.

Frozen at annotated tag `spiderverse-v1`.

### Phase 5 — Graph Analytics

- degree and betweenness centrality;
- deterministic greedy-modularity communities;
- Jaccard structural character similarity;
- evidence-backed React Analytics view;
- JSON ↔ Neo4j analytics parity.

Frozen at annotated tag `spiderverse-phase5`.

### Phase 6 — Semantic Search

- deterministic search-document builder;
- pinned 384-dimensional Sentence Transformer embeddings;
- Lexical, Semantic, and Hybrid ranking;
- versioned 15-query benchmark;
- score transparency and JSON ↔ Neo4j search parity.

Frozen at annotated tag `spiderverse-phase6`.

## Current portfolio milestone

- recruiter-oriented technical landing page;
- durable final application screenshots;
- architecture-as-code documentation;
- presentation QA and reproducibility refresh.

This milestone does not change the dataset, API behavior, analytics, or search engine.

## Future work — Grounded GraphRAG

Grounded GraphRAG is intentionally postponed and is not part of the delivered application. A future phase would require:

- bounded relevant-subgraph retrieval before generation;
- structured evidence and provenance in every supported answer;
- a provider abstraction rather than LLM logic inside routes;
- abstention for missing, ambiguous, or unsupported graph evidence;
- anti-hallucination and prompt-injection benchmarks;
- JSON ↔ Neo4j retrieval parity before generation;
- real-provider validation before claiming completion.

Before expanding the graph itself, the next data milestone would be a source-review workflow with canonical URLs, issue-level evidence, contradiction notes, and review history.
