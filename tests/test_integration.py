
from state import create_initial_state
from agents.genai_llm import generate_dialogue


def test_employee_dialogue():
    state = create_initial_state()
    result = generate_dialogue("employee", state)
    assert result["speaker"] == "employee"
    assert result["message"]


def test_manager_dialogue():
    state = create_initial_state()
    result = generate_dialogue("manager", state)
    assert result["speaker"] == "manager"
    assert result["message"]


def test_mediator_dialogue():
    state = create_initial_state()
    state["phase"] = "evidence_collection"
    result = generate_dialogue("mediator", state)
    assert "evidence" in result["message"].lower()


def test_unsupported_speaker():
    state = create_initial_state()
    result = generate_dialogue("unknown", state)
    assert "not a supported participant" in result["message"]


from strategy.evaluator import evaluate_agreement


def test_feasible_agreement_evaluation():
    policies = {
        "max_budget": 5000,
        "max_hours_per_week": 40,
        "min_deadline_days": 1,
        "require_manager_approval": True,
        "require_hr_approval_for_safety_cases": True
    }

    agreement = {
        "budget": 4000,
        "hours_per_week": 35,
        "deadline_days": 5,
        "responsibilities_assigned": True,
        "manager_approved": True,
        "hr_approved": True,
        "employee_utility": 0.8,
        "manager_utility": 0.7
    }

    result = evaluate_agreement(agreement, policies)

    assert result["feasible"] is True
    assert result["fairness_score"] == 0.9
    assert 0 <= result["overall_score"] <= 1


def test_infeasible_agreement():
    policies = {
        "max_budget": 5000,
        "max_hours_per_week": 40,
        "min_deadline_days": 1,
        "require_manager_approval": True
    }

    agreement = {
        "budget": 8000,
        "hours_per_week": 35,
        "deadline_days": 5,
        "responsibilities_assigned": True,
        "manager_approved": True
    }

    result = evaluate_agreement(agreement, policies)

    assert result["feasible"] is False
    assert result["violations"]


def test_unresolved_concerns():
    policies = {
        "max_budget": 5000,
        "max_hours_per_week": 40,
        "min_deadline_days": 1,
        "require_manager_approval": True
    }

    agreement = {
        "budget": 4000,
        "hours_per_week": 35,
        "deadline_days": 5,
        "responsibilities_assigned": True,
        "manager_approved": True
    }

    state = {
        "unresolved_issues": [
            "Workload fairness",
            "Recognition"
        ]
    }

    result = evaluate_agreement(
        agreement, policies, state
    )

    assert result["unresolved_concerns"] == 2
    assert abs(result["concern_score"] - 1 / 3) < 0.001
