
def rank_agreements(candidates, policies):
    """Rank feasible agreements using illustrative utility assumptions."""

    ranked = []

    for candidate in candidates:
        budget = candidate["budget"]
        hours = candidate["hours_per_week"]
        deadline = candidate["deadline_days"]

        violations = []

        if budget < 0 or budget > policies.get("max_budget", 5000):
            violations.append("budget_limit")

        if hours < 0 or hours > policies.get("max_hours_per_week", 40):
            violations.append("working_hours_limit")

        if deadline < policies.get("min_deadline_days", 1):
            violations.append("valid_deadline")

        if not candidate.get("responsibilities_assigned", False):
            violations.append("assigned_responsibilities")

        if (
            policies.get("require_manager_approval", True)
            and not candidate.get("manager_approved", False)
        ):
            violations.append("manager_approval")

        if violations:
            ranked.append({
                **candidate,
                "feasible": False,
                "violations": violations,
                "employee_utility": 0.0,
                "manager_utility": 0.0,
                "fairness": 0.0,
                "ranking_score": 0.0,
            })
            continue

        # Illustrative scores, not actual participant preferences.
        employee_utility = max(0.0, min(1.0, 1 - (hours - 20) / 40))
        manager_utility = max(0.0, min(1.0, 1 - (deadline - 1) / 14))

        fairness = 1 - abs(employee_utility - manager_utility)
        average_utility = (employee_utility + manager_utility) / 2

        ranking_score = (
            0.50 * average_utility
            + 0.50 * fairness
        )

        ranked.append({
            **candidate,
            "feasible": True,
            "violations": [],
            "employee_utility": round(employee_utility, 3),
            "manager_utility": round(manager_utility, 3),
            "fairness": round(fairness, 3),
            "ranking_score": round(ranking_score, 3),
        })

    return sorted(
        ranked,
        key=lambda item: (
            item["feasible"],
            item["ranking_score"],
        ),
        reverse=True,
    )
