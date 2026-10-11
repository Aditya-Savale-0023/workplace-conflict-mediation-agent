
from state import create_initial_state
from logic.planner import Planner


def test_initial_state():
    state = create_initial_state()
    assert state["phase"] == "private_interview"
    assert state["status"] == "running"


def test_employee_speaks_first():
    planner = Planner()
    state = create_initial_state()

    assert planner.get_next_speaker(state) == "employee"


def test_manager_speaks_second():
    planner = Planner()
    state = create_initial_state()

    state["milestones"]["employee_interview"] = True

    assert planner.get_next_speaker(state) == "manager"


def test_interviews_complete():
    planner = Planner()
    state = create_initial_state()

    state["current_speaker"] = "employee"
    planner.advance(state)

    state["current_speaker"] = "manager"
    planner.advance(state)

    assert state["milestones"]["employee_interview"]
    assert state["milestones"]["manager_interview"]
    assert state["phase"] == "evidence_collection"


def test_safety_escalation():
    planner = Planner()
    state = create_initial_state()

    state["events"].append({
        "type": "safety_concern"
    })

    planner.advance(state)

    assert state["status"] == "escalated"
