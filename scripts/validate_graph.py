from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = ROOT / "data" / "processed" / "graph.json"
REQUIRED_PROVENANCE = {"source_title", "source_type", "verified"}


def validate_graph(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    node_ids = [node.get("id") for node in nodes]
    edge_ids = [edge.get("id") for edge in edges]
    known = set(node_ids)

    for label, values in (("node", node_ids), ("edge", edge_ids)):
        missing = [index for index, value in enumerate(values) if not value]
        if missing:
            errors.append(f"{label} IDs missing at indexes {missing[:10]}")
        duplicates = [value for value, count in Counter(values).items() if value and count > 1]
        if duplicates:
            errors.append(f"duplicate {label} IDs: {duplicates[:10]}")

    universe_ids = {node["id"] for node in nodes if node.get("type") == "Universe"}
    for node in nodes:
        if node.get("type") == "Character" and node.get("universe_id") not in universe_ids:
            errors.append(f"character {node.get('id')} references unknown universe")

    variant_sources: set[str] = set()
    for edge in edges:
        if edge.get("source") not in known or edge.get("target") not in known:
            errors.append(f"edge {edge.get('id')} has a dangling endpoint")
        provenance = edge.get("properties", {})
        missing = REQUIRED_PROVENANCE - set(provenance)
        if missing:
            errors.append(f"edge {edge.get('id')} lacks provenance keys {sorted(missing)}")
        if not provenance.get("source_title"):
            errors.append(f"edge {edge.get('id')} has an empty source title")
        if edge.get("type") == "VARIANT_OF":
            variant_sources.add(edge.get("source"))

    for node in nodes:
        aliases = node.get("aliases", [])
        if node.get("type") == "Character" and any("Spider" in alias for alias in aliases):
            if node["id"] not in variant_sources:
                errors.append(f"spider identity {node['id']} has no VARIANT_OF edge")

    if sum(node.get("type") == "Character" for node in nodes) < 50:
        errors.append("MVP requires at least 50 characters")
    if len(edges) < 500:
        errors.append("MVP requires at least 500 relationships")
    return errors


def main() -> None:
    data = json.loads(DEFAULT_PATH.read_text(encoding="utf-8"))
    errors = validate_graph(data)
    if errors:
        print("Graph validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print(
        f"Graph valid: {len(data['nodes'])} nodes, {len(data['edges'])} edges, "
        f"{sum(node['type'] == 'Character' for node in data['nodes'])} characters."
    )


if __name__ == "__main__":
    main()
