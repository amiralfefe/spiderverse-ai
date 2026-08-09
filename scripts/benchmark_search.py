from __future__ import annotations

import json
from pathlib import Path
from statistics import fmean
from time import perf_counter
from typing import Any

from backend.app.config import ROOT_DIR, settings
from backend.app.graph_store import GraphStore
from backend.app.search_service import SearchMode, SearchService

BENCHMARK_PATH = ROOT_DIR / "data" / "fixtures" / "search_benchmark.json"
MODES: tuple[SearchMode, ...] = ("lexical", "semantic", "hybrid")


def load_benchmark(path: Path = BENCHMARK_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rank(results: list[dict[str, Any]], relevant_ids: list[str]) -> int | None:
    positions = [
        index
        for index, result in enumerate(results, start=1)
        if result["id"] in relevant_ids
    ]
    return min(positions, default=None)


def evaluate_search(
    service: SearchService,
    benchmark: dict[str, Any],
) -> dict[str, Any]:
    top_k = int(benchmark["top_k"])
    rows: list[dict[str, Any]] = []
    durations: dict[str, list[float]] = {mode: [] for mode in MODES}

    for case in benchmark["cases"]:
        row = {
            "id": case["id"],
            "category": case["category"],
            "query": case["query"],
            "relevant_ids": case["relevant_ids"],
            "ranks": {},
            "top_ids": {},
        }
        for mode in MODES:
            started = perf_counter()
            results = service.search(case["query"], mode=mode, limit=top_k)
            durations[mode].append(perf_counter() - started)
            row["ranks"][mode] = _rank(results, case["relevant_ids"])
            row["top_ids"][mode] = [result["id"] for result in results]
        rows.append(row)

    metrics = {}
    total = len(rows)
    for mode in MODES:
        ranks = [row["ranks"][mode] for row in rows]
        metrics[mode] = {
            "top_1": sum(rank == 1 for rank in ranks) / total,
            "hit_at_3": sum(rank is not None and rank <= 3 for rank in ranks) / total,
            "mrr": sum(1 / rank for rank in ranks if rank is not None) / total,
            "mean_query_ms": fmean(durations[mode]) * 1000,
        }
    return {"top_k": top_k, "cases": total, "rows": rows, "metrics": metrics}


def _percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def main() -> None:
    service = SearchService(GraphStore.from_path(settings.graph_data_path), settings)
    index = service.index_metadata()
    evaluation = evaluate_search(service, load_benchmark())

    print(
        "Model: {model}@{revision} | entities={entities} | dimensions={dimensions} | "
        "index={bytes} bytes | build={index_build_seconds:.6f}s".format(**index)
    )
    print("Query | Expected | Lexical | Semantic | Hybrid")
    for row in evaluation["rows"]:
        ranks = row["ranks"]
        print(
            f"{row['query']} | {', '.join(row['relevant_ids'])} | "
            f"{ranks['lexical'] or '-'} | {ranks['semantic'] or '-'} | "
            f"{ranks['hybrid'] or '-'}"
        )
    print("Mode | Top-1 | Hit@3 | MRR | Mean query")
    for mode in MODES:
        values = evaluation["metrics"][mode]
        print(
            f"{mode} | {_percent(values['top_1'])} | "
            f"{_percent(values['hit_at_3'])} | {values['mrr']:.3f} | "
            f"{values['mean_query_ms']:.3f} ms"
        )


if __name__ == "__main__":
    main()
