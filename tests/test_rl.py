
from strategy.rl_policy import MediationRLPolicy
from state import create_initial_state


def test_policy_returns_valid_action():
    policy = MediationRLPolicy(epsilon=0)
    state = create_initial_state()

    action = policy.choose_mediator_tactic(state)

    assert action in policy.ACTIONS


def test_safety_concern_escalates():
    policy = MediationRLPolicy()
    state = create_initial_state()
    state["safety_concern"] = True

    assert (
        policy.choose_mediator_tactic(state)
        == "escalate_to_human"
    )


def test_workload_state_detection():
    policy = MediationRLPolicy()
    state = create_initial_state()
    state["extracted_intents"] = [
        {"topics": ["workload"]}
    ]

    assert policy.get_state_key(state) == "workload_conflict"


def test_q_value_updates():
    policy = MediationRLPolicy(learning_rate=0.5)
    state = create_initial_state()
    next_state = create_initial_state()

    policy.update(
        state,
        "ask_clarifying_question",
        reward=1.0,
        next_state=next_state,
        terminal=True,
    )

    key = policy.get_state_key(state)
    assert policy.q_table[key]["ask_clarifying_question"] == 0.5


def test_negative_reward_updates_q_value():
    policy = MediationRLPolicy(learning_rate=0.5)
    state = create_initial_state()
    next_state = create_initial_state()

    policy.update(
        state,
        "request_evidence",
        reward=-1.0,
        next_state=next_state,
        terminal=True,
    )

    key = policy.get_state_key(state)
    assert policy.q_table[key]["request_evidence"] == -0.5

