
def validate_agreement(agreement, policies, state=None):
    """Validate agreement constraints and required approvals."""
    agreement = agreement or {}
    policies = policies or {}
    state = state or {}

    violations = []

    budget = agreement.get("budget", 0)
    hours = agreement.get("hours_per_week", 0)
    deadline = agreement.get("deadline_days", 0)

    max_budget = policies.get("max_budget", 5000)
    max_hours = policies.get("max_hours_per_week", 40)
    min_deadline = policies.get("min_deadline_days", 1)

    if not isinstance(budget, (int, float)) or budget < 0 or budget > max_budget:
        violations.append({
            "constraint": "budget_limit",
            "message": f"Budget must be between 0 and {max_budget}."
        })

    if not isinstance(hours, (int, float)) or hours < 0 or hours > max_hours:
        violations.append({
            "constraint": "working_hours_limit",
            "message": f"Weekly hours must be between 0 and {max_hours}."
        })

    if not isinstance(deadline, (int, float)) or deadline < min_deadline:
        violations.append({
            "constraint": "valid_deadline",
            "message": f"Deadline must be at least {min_deadline} day(s)."
        })

    if not agreement.get("responsibilities_assigned", False):
        violations.append({
            "constraint": "assigned_responsibilities",
            "message": "Responsibilities must be assigned."
        })

    safety_case = (
        bool(state.get("safety_concern", False))
        or bool(state.get("escalation_reason"))
        or any(
            event.get("type") == "safety_concern"
            for event in state.get("events", [])
        )
    )

    manager_required = policies.get("require_manager_approval", True)
    manager_approved = agreement.get("manager_approved") is True

    hr_required = (
        safety_case
        and policies.get("require_hr_approval_for_safety_cases", True)
    )
    hr_approved = agreement.get("hr_approved") is True

    if manager_required and not manager_approved:
        violations.append({
            "constraint": "manager_approval",
            "message": "Manager approval is missing."
        })

    if hr_required and not hr_approved:
        violations.append({
            "constraint": "hr_approval",
            "message": "HR approval is missing for this safety case."
        })

    approval_complete = (
        (not manager_required or manager_approved)
        and (not hr_required or hr_approved)
    )

    return {
        "valid": len(violations) == 0,
        "violations": violations,
        "manager_approval_required": manager_required,
        "manager_approved": manager_approved,
        "hr_approval_required": hr_required,
        "hr_approved": hr_approved,
        "approval_complete": approval_complete,
    }
