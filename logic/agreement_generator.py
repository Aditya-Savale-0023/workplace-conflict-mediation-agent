
from itertools import product


def generate_candidates(policies):
    """Generate candidate agreements within configured numeric limits."""

    max_budget = int(policies.get("max_budget", 5000))
    max_hours = int(policies.get("max_hours_per_week", 40))
    min_deadline = int(policies.get("min_deadline_days", 1))

    budget_options = sorted(set([
        min(2000, max_budget),
        min(3000, max_budget),
        min(4000, max_budget),
        max_budget,
    ]))

    hour_options = sorted(set([
        min(25, max_hours),
        min(30, max_hours),
        min(35, max_hours),
        max_hours,
    ]))

    deadline_options = sorted(set([
        min_deadline,
        max(min_deadline, 3),
        max(min_deadline, 5),
        max(min_deadline, 8),
    ]))

    candidates = []
    number = 1

    for budget, hours, deadline in product(
        budget_options, hour_options, deadline_options
    ):
        candidates.append({
            "id": f"proposal_{number:03d}",
            "name": f"Proposal {number}",
            "description": (
                f"Budget ₹{budget:,}, workload {hours} hours/week, "
                f"deadline {deadline} days."
            ),
            "budget": budget,
            "hours_per_week": hours,
            "deadline_days": deadline,
            "responsibilities_assigned": True,
            "manager_approved": False,
        })
        number += 1

    return candidates
