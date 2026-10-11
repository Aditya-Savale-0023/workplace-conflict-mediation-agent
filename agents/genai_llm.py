
def generate_response(role, statement="", context=None):
    """Generate a role-specific response as plain text."""
    context = context or {}

    if isinstance(statement, dict):
        state = statement
        statement = (
            state.get("issue")
            or state.get("conflict_description")
            or state.get("summary")
            or ""
        )
        context = {**state, **context}

    if not isinstance(statement, str):
        statement = str(statement)

    statement = statement.strip()

    if role == "employee":
        return (
            f"My concern is: {statement}"
            if statement
            else "I would like to explain my workplace concerns."
        )

    if role == "manager":
        return (
            f"My priority is to meet project requirements while considering: {statement}"
            if statement
            else "I want to meet project requirements while considering employee concerns."
        )

    if role == "mediator":
        tactic = context.get("tactic")
        phase = context.get("phase", "")

        if tactic == "ask_clarifying_question":
            return "Could each participant clarify their main concern and desired outcome?"

        if tactic == "request_evidence" or phase == "evidence_collection":
            return "Let us review the relevant facts and evidence before drawing conclusions."

        if tactic == "acknowledge_concerns":
            return "Both participants' concerns deserve consideration."

        if tactic == "propose_compromise":
            return "Let us explore a balanced solution with clear responsibilities and realistic deadlines."

        if phase == "clarify_interests":
            return "Let us clarify each participant's needs and priorities."

        return "Let us focus on the facts, each person's needs, and a fair solution."

    return "This is not a supported participant."


def generate_dialogue(role, state, context=None):
    """Legacy interface returning the expected speaker/message dictionary."""
    supported_roles = {"employee", "manager", "mediator"}

    if role not in supported_roles:
        return {
            "speaker": role,
            "message": "This is not a supported participant.",
        }

    state = state if isinstance(state, dict) else {}
    merged_context = {**state, **(context or {})}

    message = generate_response(role, state, merged_context)

    return {
        "speaker": role,
        "message": message,
    }
