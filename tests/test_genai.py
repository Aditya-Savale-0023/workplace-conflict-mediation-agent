
from agents.genai_llm import generate_response


def test_employee_response():
    response = generate_response("employee", "My workload is too high.")
    assert "workload is too high" in response


def test_manager_response():
    response = generate_response("manager", "The deadline must be met.")
    assert "deadline must be met" in response


def test_mediator_response():
    response = generate_response("mediator", "We disagree.")
    assert "fair solution" in response


def test_unknown_role():
    response = generate_response("unknown", "Help")
    assert response
