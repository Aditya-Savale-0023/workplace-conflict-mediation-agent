
from agents.genai_llm import generate_response
from agents.nlu_parser import extract_intents
from logic.planner import Planner
from logic.agreement_generator import generate_candidates
from logic.csp_solver import validate_agreement
from state import create_initial_state
from strategy.bayes_trust import update_trust, get_trust_uncertainty
from strategy.rl_policy import MediationRLPolicy


class MediationEngine:
    """Coordinates mediation, trust estimation and agreement validation."""

    def __init__(self, policies=None, rl_policy=None):
        self.policies = policies or {}
        self.rl_policy = rl_policy or MediationRLPolicy(epsilon=0)
        self.planner = Planner()

    def run(self, employee_statement, manager_statement):
        if not employee_statement.strip() or not manager_statement.strip():
            raise ValueError("Both participant statements are required.")

        state = create_initial_state(self.policies)

        employee_nlu = extract_intents(employee_statement)
        manager_nlu = extract_intents(manager_statement)

        state["transcript"] = [
            {"speaker": "employee", "text": employee_statement.strip()},
            {"speaker": "manager", "text": manager_statement.strip()},
        ]

        state["extracted_intents"] = [
            {"speaker": "employee", **employee_nlu},
            {"speaker": "manager", **manager_nlu},
        ]

        combined_text = (
            employee_statement + " " + manager_statement
        ).lower()

        workload_terms = [
            "workload", "too many tasks", "overloaded",
            "burnout", "unequal work", "unfair workload",
        ]
        topics = (
            ["workload"]
            if any(term in combined_text for term in workload_terms)
            else []
        )

        for item in state["extracted_intents"]:
            item["topics"] = topics.copy()

        # Update trust only from explicitly verified events.
        state["current_speaker"] = "employee"
        update_trust(state, employee_nlu)

        state["current_speaker"] = "manager"
        update_trust(state, manager_nlu)

        trust_summary = {
            person: get_trust_uncertainty(state, person)
            for person in ("employee", "manager")
        }

        safety_detected = (
            employee_nlu.get("safety_flag", False)
            or manager_nlu.get("safety_flag", False)
        )

        if safety_detected:
            state["safety_concern"] = True
            state["events"].append({"type": "safety_concern"})
            state["escalation_reason"] = (
                "Potential safety concern requires authorized human review."
            )
            self.planner.requires_human_escalation(state)
            state["status"] = "requires_human_review"

            tactic = "escalate_to_human"
            response = (
                "A potential safety concern was detected. Automated "
                "mediation is paused pending review by an authorized human."
            )
        else:
            # Record completion of both private interviews.
            state["current_speaker"] = "employee"
            self.planner.advance(state)
            state["current_speaker"] = "manager"
            self.planner.advance(state)

            state["current_speaker"] = "mediator"
            tactic = self.rl_policy.choose_mediator_tactic(state)
            response = generate_response(
                "mediator",
                f"Employee perspective: {employee_statement.strip()} "
                f"Manager perspective: {manager_statement.strip()}",
                context={"tactic": tactic},
            )

        state["mediator_tactic"] = tactic
        state["transcript"].append({
            "speaker": "mediator",
            "text": response,
        })
        state["turn_count"] = 2

        return {
            "state": state,
            "employee_nlu": employee_nlu,
            "manager_nlu": manager_nlu,
            "tactic": tactic,
            "mediator_response": response,
            "safety_detected": safety_detected,
            "topic": topics,
            "trust_summary": trust_summary,
            "planner_phase": state["phase"],
            "milestones": state["milestones"].copy(),
        }

    def generate_agreements(self):
        """Generate candidate agreements; candidates are not approvals."""
        return generate_candidates(self.policies)

    def validate_proposal(self, proposal, state=None):
        """Validate constraints and report approval status separately."""
        state = state or create_initial_state(self.policies)

        result = validate_agreement(
            proposal,
            self.policies,
            state,
        )

        return {
            **result,
            "proposal_id": proposal.get("id"),
            "approved": (
                result.get("valid", False)
                and result.get("approval_complete", False)
            ),
            "note": (
                "Constraint validity does not establish participant consent. "
                "Required approvals must be obtained before finalizing."
            ),
        }
