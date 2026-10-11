
from state import create_initial_state
from logic.csp_solver import validate_agreement


POLICIES = {
    "max_budget": 5000,
    "max_hours_per_week": 40,
    "min_deadline_days": 1,
    "require_manager_approval": True,
    "require_hr_approval_for_safety_cases": True
}


def valid_agreement():
    return {
        "budget": 4000,
        "hours_per_week": 35,
        "deadline_days": 5,
        "responsibilities_assigned": True,
        "manager_approved": True,
        "hr_approved": True
    }


def test_valid_agreement():
    result = validate_agreement(valid_agreement(), POLICIES)
    assert result["valid"] is True


def test_budget_violation():
    agreement = valid_agreement()
    agreement["budget"] = 6000

    result = validate_agreement(agreement, POLICIES)

    assert result["valid"] is False
    assert any(
        v["constraint"] == "budget_limit"
        for v in result["violations"]
    )


def test_hours_violation():
    agreement = valid_agreement()
    agreement["hours_per_week"] = 45

    result = validate_agreement(agreement, POLICIES)

    assert result["valid"] is False


def test_missing_responsibilities():
    agreement = valid_agreement()
    agreement["responsibilities_assigned"] = False

    result = validate_agreement(agreement, POLICIES)

    assert result["valid"] is False


def test_missing_manager_approval():
    agreement = valid_agreement()
    agreement["manager_approved"] = False

    result = validate_agreement(agreement, POLICIES)

    assert result["valid"] is False


def test_safety_case_requires_hr():
    agreement = valid_agreement()
    agreement["hr_approved"] = False

    result = validate_agreement(
        agreement, POLICIES, {"safety_concern": True}
    )

    assert result["valid"] is False
