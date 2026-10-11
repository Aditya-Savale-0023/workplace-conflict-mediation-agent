
from typing import Any
from copy import deepcopy


def create_initial_state(policies: dict | None = None) -> dict:
    """Create the shared state for one mediation simulation."""
    return {
        "phase": "private_interview",
        "current_speaker": "employee",
        "transcript": [],
        "extracted_intents": [],
        "trust_scores": {
            "employee": 0.5,
            "manager": 0.5
        },
        "beliefs": {},
        "org_constraints": deepcopy(policies or {}),
        "proposed_agreement": None,
        "evidence": [],
        "unresolved_issues": [],
        "mediator_tactic": None,
        "events": [],
        "milestones": {
            "employee_interview": False,
            "manager_interview": False,
            "evidence_collected": False,
            "interests_clarified": False,
            "rules_established": False,
            "summary_presented": False,
            "compromise_generated": False,
            "agreement_approved": False,
            "commitments_documented": False,
            "follow_up_scheduled": False
        },
        "status": "running",
        "escalation_reason": None,
        "turn_count": 0
    }
