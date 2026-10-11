
from mediation_engine import MediationEngine
from state import create_initial_state


def test_engine_processes_both_statements():
    engine = MediationEngine()
    result = engine.run(
        "I have too many tasks and feel overloaded.",
        "We must finish the project on time.",
    )

    assert len(result["state"]["transcript"]) == 3
    assert result["tactic"] in engine.rl_policy.ACTIONS
    assert result["mediator_response"]


def test_engine_escalates_safety_concern():
    engine = MediationEngine()
    result = engine.run(
        "I was threatened by my colleague.",
        "I want to discuss the disagreement.",
    )

    assert result["safety_detected"] is True
    assert result["tactic"] == "escalate_to_human"
    assert result["state"]["status"] == "requires_human_review"


def test_engine_requires_both_statements():
    engine = MediationEngine()

    try:
        engine.run("I have a concern.", "")
        assert False, "Expected ValueError for missing manager statement."
    except ValueError:
        pass
