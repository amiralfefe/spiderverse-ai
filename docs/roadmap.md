# Roadmap

## V1 — Knowledge Graph core (current)

- deterministic dataset generation and validation;
- local and Neo4j adapters;
- search, details, neighborhood exploration, universe browsing, and path finding;
- graph-grounded deterministic question routing;
- React/Cytoscape interface, tests, Docker, and CI.

## V2 — Semantic retrieval

- replace fuzzy matching with a versioned embedding index;
- introduce entity-resolution evaluation fixtures;
- add hybrid keyword/vector ranking and confidence reporting;
- retain exact graph traversal after semantic resolution.

## V3 — GraphRAG

- question classification and constrained intent schema;
- relevant-subgraph retrieval budgets;
- deterministic context builder with edge-level citations;
- optional LLM response generation behind a provider interface;
- answer verification against retrieved relationship IDs.

## V4 — Graph intelligence

- centrality and community analysis;
- multiverse map and timeline;
- character comparison and work recommendations;
- reproducible analytics notebooks.

Before expanding the dataset, the next data milestone is a source-review workflow with canonical URLs, issue-level evidence, contradiction notes, and review history.
