
from mediation_engine import MediationEngine
from state import create_initial_state


POLICIES = {
    "max_budget": 5000,
    "max_hours_per_week": 40,
    "min_deadline_days": 1,
    "require_manager_approval": True,
    "require_hr_approval_for_safety_cases": True,
}


def test_engine_generates_multiple_proposals():
    engine = MediationEngine(policies=POLICIES)
    proposals = engine.generate_agreements()

    assert len(proposals) > 1
    assert len({p["id"] for p in proposals}) == len(proposals)


def test_missing_manager_approval_is_not_approved():
    engine = MediationEngine(policies=POLICIES)
    proposals = engine.generate_agreements()
    proposal = proposals[0]

    result = engine.validate_proposal(
        {**proposal, "manager_approved": False}
    )

    assert result["valid"] is False
    assert result["approved"] is False


def test_approved_feasible_proposal_passes():
    engine = MediationEngine(policies=POLICIES)
    proposal = engine.generate_agreements()[0]

    result = engine.validate_proposal({
        **proposal,
        "manager_approved": True,
    })

    assert result["valid"] is True
    assert result["approved"] is True


def test_safety_proposal_requires_hr_approval():
    engine = MediationEngine(policies=POLICIES)
    proposal = engine.generate_agreements()[0]
    state = create_initial_state(POLICIES)
    state["safety_concern"] = True

    result = engine.validate_proposal(
        {**proposal, "manager_approved": True, "hr_approved": False},
        state,
    )

    assert result["valid"] is False
    assert result["approved"] is False
