
from datetime import datetime, timedelta, timezone
import uuid


def create_agreement_record(
    candidate,
    employee_name,
    manager_name,
    employee_commitment,
    manager_commitment,
    follow_up_days,
):
    """Create a structured record for an accepted candidate."""

    required_fields = [
        "name",
        "description",
        "budget",
        "hours_per_week",
        "deadline_days",
    ]

    for field in required_fields:
        if field not in candidate:
            raise ValueError(f"Candidate is missing: {field}")

    if not candidate.get("feasible", False):
        raise ValueError("An infeasible candidate cannot be recorded.")

    if not employee_name.strip() or not manager_name.strip():
        raise ValueError("Both participant names are required.")

    if not employee_commitment.strip():
        raise ValueError("Employee responsibility is required.")

    if not manager_commitment.strip():
        raise ValueError("Manager responsibility is required.")

    if not 1 <= int(follow_up_days) <= 90:
        raise ValueError("Follow-up must be between 1 and 90 days.")

    now = datetime.now(timezone.utc)

    return {
        "agreement_id": f"AGR-{uuid.uuid4().hex[:8].upper()}",
        "created_at": now.isoformat(),
        "proposal": {
            "name": candidate["name"],
            "description": candidate["description"],
        },
        "participants": {
            "employee": employee_name.strip(),
            "manager": manager_name.strip(),
        },
        "resources": {
            "budget": candidate["budget"],
            "hours_per_week": candidate["hours_per_week"],
            "deadline_days": candidate["deadline_days"],
        },
        "responsibilities": {
            "employee": employee_commitment.strip(),
            "manager": manager_commitment.strip(),
        },
        "follow_up": {
            "after_days": int(follow_up_days),
            "due_date": (
                now + timedelta(days=int(follow_up_days))
            ).date().isoformat(),
        },
        "approvals": {
            "employee_accepted": False,
            "manager_accepted": False,
            "authorised_review": "pending",
        },
        "status": "awaiting_authorised_review",
    }
