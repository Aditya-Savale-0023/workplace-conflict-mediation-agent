
import json
from pathlib import Path

import streamlit as st

from state import create_initial_state
from agents.genai_llm import generate_dialogue
from agents.nlu_parser import extract_intents
from strategy.bayes_trust import update_trust
from strategy.rl_policy import MediationRLPolicy
from strategy.evaluator import evaluate_agreement
from logic.csp_solver import validate_agreement


BASE_DIR = Path(__file__).parent


def load_json(filename):
    with open(BASE_DIR / filename, "r", encoding="utf-8") as file:
        return json.load(file)


st.set_page_config(
    page_title="Workplace Conflict Mediator",
    page_icon="🤝",
    layout="wide"
)

st.title("🤝 AI Workplace Conflict Mediation")
st.write(
    "A prototype for analysing workplace conflicts and "
    "evaluating possible agreements."
)

policies = load_json("data/org_policies.json")
scenarios = load_json("data/scenarios.json")

scenario_titles = [s["title"] for s in scenarios]

selected_title = st.selectbox(
    "Select a conflict scenario",
    scenario_titles
)

scenario = next(
    s for s in scenarios if s["title"] == selected_title
)

st.subheader("Conflict details")
st.write("**Issue:**", scenario["issue"])
st.write("**Employee's position:**", scenario["employee_public_position"])
st.write("**Manager's position:**", scenario["manager_public_position"])

if st.button("Run Mediation Simulation", type="primary"):
    state = create_initial_state(policies)
    policy = MediationRLPolicy()

    st.subheader("1. Participant dialogue")

    for speaker in ["employee", "manager"]:
        state["current_speaker"] = speaker
        response = generate_dialogue(speaker, state)
        message = response["message"]

        state["transcript"].append({
            "speaker": speaker,
            "message": message
        })

        intents = extract_intents(message)
        state["extracted_intents"].append({
            "speaker": speaker,
            **intents
        })

        if intents["safety_flag"]:
            state["events"].append({
                "type": "safety_concern",
                "source": speaker
            })

        update_trust(state, intents)

        with st.chat_message(speaker):
            st.write(message)
            st.caption(f"Detected intent: {intents['intent']}")

    st.subheader("2. Mediator's recommended tactic")
    state["current_speaker"] = "mediator"
    tactic = policy.choose_mediator_tactic(state)
    state["mediator_tactic"] = tactic
    st.info(tactic.replace("_", " ").title())

    agreement = {
        "budget": scenario["budget"],
        "hours_per_week": 35,
        "deadline_days": 5,
        "responsibilities_assigned": True,
        "manager_approved": True,
        "hr_approved": False,
        "employee_utility": 0.8,
        "manager_utility": 0.7
    }

    state["proposed_agreement"] = agreement
    state["safety_concern"] = any(
        event["type"] == "safety_concern"
        for event in state["events"]
    )

    st.subheader("3. Proposed agreement")

    col1, col2 = st.columns(2)
    col1.metric("Budget", f"{agreement['budget']:,}")
    col2.metric("Hours per week", agreement["hours_per_week"])

    st.write(f"**Deadline:** {agreement['deadline_days']} days")
    st.write("**Responsibilities assigned:** Yes")
    st.write("**Manager approval:** Yes (simulated)")
    st.caption(
        "This is a demonstration agreement, not an actual negotiated decision."
    )

    if state["safety_concern"]:
        state["status"] = "escalated"
        state["escalation_reason"] = "Potential safety concern"
        st.error(
            "Human review required. The agreement has not been approved."
        )
    else:
        validation = validate_agreement(
            agreement, policies, state
        )

        st.subheader("4. Constraint validation")

        if validation["valid"]:
            st.success("The sample agreement passes the configured checks.")
        else:
            st.error("The sample agreement violates one or more constraints.")
            for violation in validation["violations"]:
                st.write(f"- {violation}")

        evaluation = evaluate_agreement(
            agreement, policies, state
        )

        st.subheader("5. Evaluation results")

        c1, c2, c3 = st.columns(3)
        c1.metric("Fairness", evaluation["fairness_score"])
        c2.metric("Average utility", evaluation["utility_score"])
        c3.metric("Overall score", evaluation["overall_score"])

        st.write("**Trust estimates**")
        st.json(state["trust_scores"])

        st.write("**Detailed evaluation**")
        st.json(evaluation)

        st.caption(
            "Scores use illustrative inputs and prototype formulas. "
            "They are not validated measures of actual fairness or satisfaction."
        )
