
from logic.search_graph import EvidenceGraph


def build_graph():
    graph = EvidenceGraph()

    graph.add_claim(
        "claim1", "employee",
        "The access request was submitted on Monday."
    )
    graph.add_evidence(
        "evidence1", "Access request timestamp: Monday",
        source="access_log"
    )
    graph.add_evidence(
        "evidence2", "Access was granted on Wednesday",
        source="system_log"
    )

    graph.link_evidence("claim1", "evidence1", supports=True)
    graph.link_evidence("claim1", "evidence2", supports=False)

    graph.add_commitment(
        "commitment1", "manager",
        "Provide system access by Monday"
    )

    return graph


def test_find_supporting_evidence():
    graph = build_graph()
    evidence = graph.find_related_evidence("claim1")

    assert any(item["relation"] == "supports" for item in evidence)


def test_find_contradictions():
    graph = build_graph()

    contradictions = graph.get_contradictions("claim1")

    assert len(contradictions) == 1
    assert contradictions[0]["id"] == "evidence2"


def test_find_previous_commitments():
    graph = build_graph()

    commitments = graph.find_commitments("manager")

    assert len(commitments) == 1
    assert commitments[0]["id"] == "commitment1"


def test_bfs_search():
    graph = build_graph()

    results = graph.search("evidence1")

    assert any(item["id"] == "claim1" for item in results)


def test_missing_claim():
    graph = build_graph()

    assert graph.find_related_evidence("unknown") == []
