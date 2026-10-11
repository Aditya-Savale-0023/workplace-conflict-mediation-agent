
from strategy.agreement_ranker import rank_agreements


POLICIES = {
    "max_budget": 5000,
    "max_hours_per_week": 40,
    "min_deadline_days": 1,
    "require_manager_approval": True,
}


def test_unapproved_proposal_is_infeasible():
    candidates = [{
        "id": "p1",
        "budget": 3000,
        "hours_per_week": 30,
        "deadline_days": 5,
        "responsibilities_assigned": True,
        "manager_approved": False,
    }]

    ranked = rank_agreements(candidates, POLICIES)
    assert ranked[0]["feasible"] is False
    assert "manager_approval" in ranked[0]["violations"]


def test_approved_feasible_proposal_is_ranked():
    candidates = [{
        "id": "p1",
        "budget": 3000,
        "hours_per_week": 30,
        "deadline_days": 5,
        "responsibilities_assigned": True,
        "manager_approved": True,
    }]

    ranked = rank_agreements(candidates, POLICIES)
    assert ranked[0]["feasible"] is True
    assert 0 <= ranked[0]["ranking_score"] <= 1


def test_feasible_proposal_ranks_above_infeasible():
    candidates = [
        {
            "id": "bad",
            "budget": 6000,
            "hours_per_week": 30,
            "deadline_days": 5,
            "responsibilities_assigned": True,
            "manager_approved": True,
        },
        {
            "id": "good",
            "budget": 3000,
            "hours_per_week": 30,
            "deadline_days": 5,
            "responsibilities_assigned": True,
            "manager_approved": True,
        },
    ]

    ranked = rank_agreements(candidates, POLICIES)
    assert ranked[0]["id"] == "good"
