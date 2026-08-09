from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray

from backend.app.config import settings
from backend.app.graph_store import GraphStore
from scripts.compare_backends import collect_contract, collect_search_contract


class ContractEncoder:
    model_name = "test/contract-encoder"
    model_revision = "test-revision"

    def encode_documents(self, texts: Sequence[str]) -> NDArray[np.float32]:
        return np.ones((len(texts), 2), dtype=np.float32) / np.sqrt(2)

    def encode_query(self, text: str) -> NDArray[np.float32]:
        del text
        return np.ones(2, dtype=np.float32) / np.sqrt(2)


def test_json_backend_conformance_contract() -> None:
    contract = collect_contract(GraphStore.from_path(settings.graph_data_path))

    assert contract["stats"] == {
        "by_type": {
            "Character": 59,
            "Concept": 2,
            "Event": 10,
            "Power": 17,
            "Team": 8,
            "Universe": 18,
            "Work": 50,
        },
        "demo_relationships": 547,
        "nodes": 164,
        "relationships": 574,
        "verified_relationships": 27,
    }
    assert contract["search_name"][0][0] == "miles-1610"
    assert any(item[0] == "miguel-928" for item in contract["search_alias"])
    assert contract["miles_detail"]["character"]["id"] == "miles-1610"
    assert contract["miles_detail"]["universe"]["id"] == "earth-1610"
    assert len(contract["miles_neighborhood"]["nodes"]) == 21
    assert len(contract["miles_neighborhood"]["edges"]) == 21
    assert len(contract["earth_1610_characters"]) == 7
    assert contract["miles_to_daredevil"]["found"] is True
    assert contract["miles_to_daredevil"]["nodes"][0]["id"] == "miles-1610"
    assert contract["miles_to_daredevil"]["nodes"][-1]["id"] == "daredevil-616"
    assert contract["mentor_question"]["answer"] == (
        "The graph links Miles Morales to Peter B. Parker via MENTORED_BY."
    )
    assert contract["analytics_overview"]["nodes"] == 164
    assert contract["analytics_overview"]["relationships"] == 574
    assert contract["analytics_degree"]["results"][0]["node"]["id"] == "peter-616"
    assert contract["analytics_betweenness"]["results"][0]["node"]["id"] == (
        "peter-616"
    )
    assert contract["analytics_communities"]["algorithm"] == "greedy_modularity"
    assert contract["analytics_miles_similarity"]["source"]["id"] == "miles-1610"


def test_search_contract_is_reproducible_for_equivalent_backends() -> None:
    first = GraphStore.from_path(settings.graph_data_path)
    second = GraphStore(
        {"nodes": list(reversed(first.nodes)), "edges": list(reversed(first.edges))}
    )
    assert collect_search_contract(first, settings, ContractEncoder()) == collect_search_contract(
        second, settings, ContractEncoder()
    )
