
def update_trust(state, intents):
    """
    Update trust estimates using observable evidence.

    Unverified accusations and sentiment alone do not change trust.
    """
    speaker = state.get("current_speaker")

    if speaker not in {"employee", "manager"}:
        return state

    # Keep Beta distribution parameters for each participant.
    trust_beliefs = state.setdefault("beliefs", {}).setdefault(
        "trust_beta", {}
    )

    params = trust_beliefs.setdefault(
        speaker, {"alpha": 2.0, "beta": 2.0}
    )

    # Evidence events must be explicitly identified as verified.
    verified = intents.get("verified_events", [])

    for event in verified:
        if not event.get("verified", False):
            continue

        event_type = event.get("type")

        if event_type in {
            "commitment_fulfilled",
            "claim_supported_by_evidence"
        }:
            params["alpha"] += 1.0

        elif event_type in {
            "commitment_broken",
            "claim_contradicted_by_evidence"
        }:
            params["beta"] += 1.0

    # Posterior mean of a Beta distribution.
    alpha = params["alpha"]
    beta = params["beta"]

    state.setdefault("trust_scores", {})[speaker] = (
        alpha / (alpha + beta)
    )

    return state


def get_trust_uncertainty(state, person):
    """Return trust estimate and Beta distribution parameters."""
    params = (
        state.get("beliefs", {})
        .get("trust_beta", {})
        .get(person, {"alpha": 2.0, "beta": 2.0})
    )

    alpha = params["alpha"]
    beta = params["beta"]

    return {
        "trust_estimate": alpha / (alpha + beta),
        "alpha": alpha,
        "beta": beta,
        "observations": int(alpha + beta - 4)
    }
