
from logic.csp_solver import validate_agreement


def evaluate_agreement(agreement, policies, state=None):
    """Evaluate feasibility, fairness, utility, and unresolved concerns."""

    state = state or {}

    # 1. Check organisational constraints.
    validation = validate_agreement(
        agreement, policies, state
    )

    violations = validation["violations"]

    # 2. Estimate each participant's utility.
    # Scores are illustrative until connected to a real utility model.
    employee_utility = agreement.get("employee_utility", 0.5)
    manager_utility = agreement.get("manager_utility", 0.5)

    employee_utility = max(0.0, min(1.0, employee_utility))
    manager_utility = max(0.0, min(1.0, manager_utility))

    # 3. Measure fairness as the similarity of both utilities.
    fairness = 1.0 - abs(
        employee_utility - manager_utility
    )

    # 4. Count unresolved concerns.
    unresolved = state.get("unresolved_issues", [])
    unresolved_count = len(unresolved)

    # 5. Calculate a simple overall score.
    feasibility_score = 1.0 if validation["valid"] else 0.0
    utility_score = (
        employee_utility + manager_utility
    ) / 2

    concern_score = 1.0 / (1 + unresolved_count)

    overall_score = (
        0.40 * feasibility_score
        + 0.25 * fairness
        + 0.25 * utility_score
        + 0.10 * concern_score
    )

    return {
        "feasible": validation["valid"],
        "violations": violations,
        "employee_utility": employee_utility,
        "manager_utility": manager_utility,
        "fairness_score": round(fairness, 3),
        "utility_score": round(utility_score, 3),
        "unresolved_concerns": unresolved_count,
        "concern_score": round(concern_score, 3),
        "overall_score": round(overall_score, 3)
    }
