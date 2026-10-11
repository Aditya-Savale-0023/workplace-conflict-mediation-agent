
import pytest
from logic.agreement_report import create_agreement_record


def valid_candidate():
    return {
        "name": "A — Redistribute workload",
        "description": "Redistribute tasks while retaining the deadline.",
        "budget": 4000,
        "hours_per_week": 35,
        "deadline_days": 5,
        "feasible": True,
    }


def test_create_agreement_record():
    record = create_agreement_record(
        valid_candidate(),
        "Employee",
        "Manager",
        "Complete assigned testing tasks.",
        "Redistribute tasks and review workload.",
        7,
    )

    assert record["agreement_id"].startswith("AGR-")
    assert record["status"] == "awaiting_authorised_review"
    assert record["approvals"]["authorised_review"] == "pending"
    assert record["follow_up"]["after_days"] == 7


def test_reject_infeasible_candidate():
    candidate = valid_candidate()
    candidate["feasible"] = False

    with pytest.raises(ValueError):
        create_agreement_record(
            candidate, "Employee", "Manager",
            "Complete testing.", "Redistribute tasks.", 7
        )


def test_responsibilities_are_required():
    with pytest.raises(ValueError):
        create_agreement_record(
            valid_candidate(), "Employee", "Manager",
            "", "Redistribute tasks.", 7
        )
