
from state import create_initial_state
from strategy.bayes_trust import (
    update_trust,
    get_trust_uncertainty
)


def test_initial_trust():
    state = create_initial_state()

    assert state["trust_scores"]["employee"] == 0.5


def test_verified_commitment_increases_trust():
    state = create_initial_state()
    state["current_speaker"] = "employee"

    update_trust(state, {
        "verified_events": [{
            "type": "commitment_fulfilled",
            "verified": True
        }]
    })

    assert state["trust_scores"]["employee"] == 0.6


def test_unverified_event_does_not_change_trust():
    state = create_initial_state()
    state["current_speaker"] = "employee"

    update_trust(state, {
        "verified_events": [{
            "type": "commitment_broken",
            "verified": False
        }]
    })

    assert state["trust_scores"]["employee"] == 0.5


def test_trust_uncertainty():
    state = create_initial_state()

    result = get_trust_uncertainty(state, "employee")

    assert result["trust_estimate"] == 0.5
    assert result["alpha"] == 2.0
    assert result["beta"] == 2.0
