
class Planner:
    """Controls mediation phases and their valid transitions."""

    PHASES = [
        "private_interview",
        "evidence_collection",
        "clarify_interests",
        "establish_rules",
        "shared_summary",
        "generate_compromise",
        "joint_negotiation",
        "validate_agreement",
        "approval",
        "document_commitments",
        "follow_up"
    ]

    def __init__(self):
        self.phase_index = 0

    def get_next_speaker(self, state):
        """Choose the speaker based on the current phase."""
        phase = state["phase"]

        if phase == "private_interview":
            if not state["milestones"]["employee_interview"]:
                return "employee"
            if not state["milestones"]["manager_interview"]:
                return "manager"

        return "mediator"

    def requires_human_escalation(self, state):
        """Escalate safety concerns or serious policy violations."""
        if state.get("escalation_reason"):
            return True

        for event in state.get("events", []):
            if event.get("type") in {
                "safety_concern",
                "serious_policy_violation"
            }:
                state["escalation_reason"] = event["type"]
                return True

        return False

    def advance(self, state):
        """Update milestones and move to the next valid phase."""
        if self.requires_human_escalation(state):
            state["status"] = "escalated"
            return state

        phase = state["phase"]
        milestones = state["milestones"]

        if phase == "private_interview":
            speaker = state.get("current_speaker")

            if speaker == "employee":
                milestones["employee_interview"] = True
                state["current_speaker"] = "manager"
                return state

            if speaker == "manager":
                milestones["manager_interview"] = True
                milestones["evidence_collected"] = False
                state["phase"] = "evidence_collection"
                state["current_speaker"] = "mediator"
                return state

        # Do not accept a rejected proposal.
        if any(
            event.get("type") == "proposal_rejected"
            for event in state.get("events", [])
        ):
            state["phase"] = "generate_compromise"
            state["current_speaker"] = "mediator"
            return state

        if phase == "evidence_collection":
            milestones["evidence_collected"] = True

        elif phase == "clarify_interests":
            milestones["interests_clarified"] = True

        elif phase == "establish_rules":
            milestones["rules_established"] = True

        elif phase == "shared_summary":
            milestones["summary_presented"] = True

        elif phase == "generate_compromise":
            milestones["compromise_generated"] = True

        elif phase == "validate_agreement":
            if state.get("agreement_valid") is not True:
                state["phase"] = "generate_compromise"
                return state

        elif phase == "approval":
            if state.get("approval_obtained") is not True:
                return state
            milestones["agreement_approved"] = True

        elif phase == "document_commitments":
            milestones["commitments_documented"] = True

        elif phase == "follow_up":
            milestones["follow_up_scheduled"] = True
            state["phase"] = "resolved"
            state["status"] = "resolved"
            return state

        # Move forward after completing the current stage.
        index = self.PHASES.index(phase)

        if index + 1 < len(self.PHASES):
            state["phase"] = self.PHASES[index + 1]

        state["current_speaker"] = "mediator"
        return state

    def check_transitions(self, state):
        """Compatibility method for the main integration loop."""
        return self.advance(state)
