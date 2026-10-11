
import random


class MediationRLPolicy:
    """Small tabular Q-learning policy for mediation tactic selection."""

    ACTIONS = [
        "ask_clarifying_question",
        "request_evidence",
        "acknowledge_concerns",
        "propose_compromise",
        "escalate_to_human",
    ]

    def __init__(
        self,
        learning_rate=0.1,
        discount_factor=0.9,
        epsilon=0.1,
    ):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.q_table = {}

    def get_state_key(self, state):
        """Convert mediation context into a compact discrete state."""
        intents = state.get("extracted_intents", [])
        topics = {
            topic
            for item in intents
            for topic in item.get("topics", [])
        }

        safety = bool(
            state.get("safety_concern", False)
            or state.get("escalation_reason")
            or any(
                event.get("type") == "safety_concern"
                for event in state.get("events", [])
            )
        )

        contradictions = any(
            event.get("type") == "contradiction"
            for event in state.get("events", [])
        )

        trust = state.get("trust_scores", {})
        average_trust = sum(trust.values()) / max(len(trust), 1)

        if safety:
            return "safety_concern"
        if contradictions:
            return "contradiction"
        if "workload" in topics:
            return "workload_conflict"
        if average_trust < 0.4:
            return "low_trust"
        return "general_conflict"

    def choose_mediator_tactic(self, state):
        state_key = self.get_state_key(state)

        # Potential safety concerns must be escalated for human review.
        if state_key == "safety_concern":
            return "escalate_to_human"

        values = self.q_table.setdefault(
            state_key,
            {action: 0.0 for action in self.ACTIONS},
        )

        if random.random() < self.epsilon:
            return random.choice(self.ACTIONS[:-1])

        # Deterministic tie-breaking makes the initial policy predictable.
        return max(self.ACTIONS[:-1], key=lambda action: values[action])

    def update(
        self,
        state,
        action,
        reward,
        next_state,
        terminal=False,
    ):
        """Update Q(s,a) using a one-step Q-learning update."""
        state_key = self.get_state_key(state)
        next_key = self.get_state_key(next_state)

        current = self.q_table.setdefault(
            state_key,
            {item: 0.0 for item in self.ACTIONS},
        )
        future = self.q_table.setdefault(
            next_key,
            {item: 0.0 for item in self.ACTIONS},
        )

        old_value = current[action]
        best_future = 0.0 if terminal else max(future.values())

        target = reward + self.discount_factor * best_future

        current[action] = old_value + self.learning_rate * (
            target - old_value
        )

    def set_reward(self, state, action, reward, next_state):
        """Convenience method for a non-terminal training transition."""
        self.update(state, action, reward, next_state)

