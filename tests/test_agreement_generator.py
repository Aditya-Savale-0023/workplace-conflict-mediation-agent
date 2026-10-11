
from logic.agreement_generator import generate_candidates


POLICIES = {
    "max_budget": 5000,
    "max_hours_per_week": 40,
    "min_deadline_days": 1,
}


def test_candidates_are_generated():
    candidates = generate_candidates(POLICIES)
    assert len(candidates) > 3


def test_candidate_ids_are_unique():
    candidates = generate_candidates(POLICIES)
    ids = [candidate["id"] for candidate in candidates]
    assert len(ids) == len(set(ids))


def test_candidates_respect_budget_limit():
    candidates = generate_candidates(POLICIES)
    assert all(
        candidate["budget"] <= POLICIES["max_budget"]
        for candidate in candidates
    )


def test_candidates_respect_hours_limit():
    candidates = generate_candidates(POLICIES)
    assert all(
        candidate["hours_per_week"] <= POLICIES["max_hours_per_week"]
        for candidate in candidates
    )


def test_candidates_respect_minimum_deadline():
    candidates = generate_candidates(POLICIES)
    assert all(
        candidate["deadline_days"] >= POLICIES["min_deadline_days"]
        for candidate in candidates
    )
