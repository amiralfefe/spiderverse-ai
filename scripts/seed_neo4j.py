from __future__ import annotations

import json
import os
from pathlib import Path

from neo4j import GraphDatabase

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "graph.json"
ALLOWED_NODE_TYPES = {"Character", "Universe", "Work", "Event", "Team", "Power", "Concept"}
ALLOWED_RELATION_TYPES = {
    "ALLY_OF",
    "APPEARS_IN",
    "BELONGS_TO_UNIVERSE",
    "CHILD_OF",
    "CONFLICT_WITH",
    "DEPICTS_EVENT",
    "ENEMY_OF",
    "FAMILY_OF",
    "FRIEND_OF",
    "HAS_POWER",
    "INSPIRED_BY",
    "MEMBER_OF",
    "MENTORED_BY",
    "OCCURRED_IN",
    "PARENT_OF",
    "PARTICIPATED_IN",
    "RELATED_TO",
    "ROMANTIC_RELATIONSHIP_WITH",
    "SET_IN_UNIVERSE",
    "SIBLING_OF",
    "VARIANT_OF",
    "WORKS_FOR",
}


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "spiderverse-local")
    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        with driver.session() as session:
            session.run(
                "CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (n:Entity) REQUIRE n.id IS UNIQUE"
            )
            session.run("MATCH (n:Entity) DETACH DELETE n")
            for node_type in ALLOWED_NODE_TYPES:
                batch = [node for node in data["nodes"] if node["type"] == node_type]
                if not batch:
                    continue
                payload = [
                    {key: value for key, value in node.items() if key != "type"} for node in batch
                ]
                session.run(
                    f"UNWIND $nodes AS props CREATE (n:Entity:{node_type}) SET n = props",
                    nodes=payload,
                )
            for relation_type in ALLOWED_RELATION_TYPES:
                batch = [edge for edge in data["edges"] if edge["type"] == relation_type]
                if not batch:
                    continue
                payload = [
                    {
                        "id": edge["id"],
                        "source": edge["source"],
                        "target": edge["target"],
                        "properties": {"id": edge["id"], **edge["properties"]},
                    }
                    for edge in batch
                ]
                session.run(
                    f"UNWIND $edges AS edge MATCH (a:Entity {{id: edge.source}}), "
                    f"(b:Entity {{id: edge.target}}) CREATE (a)-[r:{relation_type}]->(b) "
                    "SET r = edge.properties",
                    edges=payload,
                )
        print(
            f"Seeded Neo4j with {len(data['nodes'])} nodes and {len(data['edges'])} relationships."
        )
    finally:
        driver.close()


if __name__ == "__main__":
    main()
