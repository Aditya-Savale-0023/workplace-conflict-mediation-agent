
import json
from pathlib import Path

import streamlit as st

from agents.nlu_parser import extract_intents
from logic.agreement_generator import generate_candidates
from logic.csp_solver import validate_agreement
from mediation_engine import MediationEngine
from state import create_initial_state
from strategy.rl_policy import MediationRLPolicy


BASE_DIR = Path(__file__).resolve().parent

with open(BASE_DIR / "data" / "org_policies.json", "r", encoding="utf-8") as file:
    POLICIES = json.load(file)

st.set_page_config(
    page_title="Workplace Conflict Mediation AI",
    page_icon="🤝",
    layout="wide",
)

st.title("🤝 Socially Intelligent Workplace Conflict-Mediation Agent")
st.caption(
    "A prototype combining NLU, reinforcement learning, "
    "Bayesian trust estimation, planning and agreement validation."
)

if "mediation_policy" not in st.session_state:
    st.session_state.mediation_policy = MediationRLPolicy(epsilon=0)

policy = st.session_state.mediation_policy

if "mediation_engine" not in st.session_state:
    st.session_state.mediation_engine = MediationEngine(
        policies=POLICIES,
        rl_policy=policy,
    )

engine = st.session_state.mediation_engine

tab1, tab2, tab3, tab4 = st.tabs(
    ["Mediator Strategy", "Agreement Builder", "Evaluation", "Full Mediation"]
)


# --------------------------------------------------
# TAB 1: MEDIATOR STRATEGY
# --------------------------------------------------
with tab1:
    st.subheader("Analyze a Workplace Conflict")

    statement = st.text_area(
        "Describe the conflict",
        placeholder="Example: I have too many tasks and feel overloaded.",
        height=120,
        key="strategy_statement",
    )

    if st.button("Analyze Conflict", key="analyze_strategy"):
        if not statement.strip():
            st.warning("Please enter a conflict description.")
        else:
            nlu = extract_intents(statement)
            lower = statement.lower()

            topics = (
                ["workload"]
                if any(term in lower for term in [
                    "workload", "too many tasks", "overloaded",
                    "burnout", "unequal work", "unfair workload"
                ])
                else []
            )

            state = {
                "extracted_intents": [{**nlu, "topics": topics}],
                "trust_scores": {"employee": 0.5, "manager": 0.5},
                "events": [],
            }

            if nlu["safety_flag"]:
                state["safety_concern"] = True
                state["events"].append({"type": "safety_concern"})

            st.session_state.strategy_nlu = nlu
            st.session_state.strategy_state_key = policy.get_state_key(state)
            st.session_state.strategy_tactic = policy.choose_mediator_tactic(state)

    if "strategy_tactic" in st.session_state:
        st.write("**Detected intent:**", st.session_state.strategy_nlu["intent"])
        st.write(
            "**Safety concern:**",
            "Yes" if st.session_state.strategy_nlu["safety_flag"] else "No",
        )
        st.write("**RL state:**", st.session_state.strategy_state_key)
        st.write("**Recommended tactic:**", st.session_state.strategy_tactic)

        if st.session_state.strategy_tactic == "escalate_to_human":
            st.warning("Refer the potential safety concern to an authorized human.")

        with st.expander("View NLU details"):
            st.json(st.session_state.strategy_nlu)

        st.caption("The Q-table starts untrained; recommendations are prototype outputs.")


# --------------------------------------------------
# TAB 2: AGREEMENT BUILDER
# --------------------------------------------------
with tab2:
    st.subheader("Generate and Validate Agreement Proposals")
    candidates = generate_candidates(POLICIES)

    if not candidates:
        st.warning("No proposals were generated.")
    else:
        selected_id = st.selectbox(
            "Select a proposal",
            options=[candidate["id"] for candidate in candidates],
            format_func=lambda proposal_id: next(
                f'{c["name"]} — ₹{c["budget"]:,}, '
                f'{c["hours_per_week"]} hours/week, '
                f'{c["deadline_days"]} days'
                for c in candidates if c["id"] == proposal_id
            ),
            key="builder_proposal",
        )

        selected = next(c for c in candidates if c["id"] == selected_id)
        st.write(selected["description"])

        col1, col2, col3 = st.columns(3)
        col1.metric("Maximum budget", f'₹{POLICIES.get("max_budget", 0):,}')
        col2.metric("Maximum hours/week", POLICIES.get("max_hours_per_week", 0))
        col3.metric("Minimum deadline", f'{POLICIES.get("min_deadline_days", 1)} day(s)')

        manager_approved = st.checkbox(
            "Manager approval obtained", key=f"builder_manager_{selected_id}"
        )
        hr_approved = st.checkbox(
            "HR approval obtained, if required", key=f"builder_hr_{selected_id}"
        )
        safety_case = st.checkbox(
            "This case involves a potential safety concern",
            key=f"builder_safety_{selected_id}",
        )

        if st.button("Validate Agreement", key="validate_builder"):
            state = create_initial_state(POLICIES)
            if safety_case:
                state["safety_concern"] = True
                state["events"].append({"type": "safety_concern"})

            agreement = {
                **selected,
                "manager_approved": manager_approved,
                "hr_approved": hr_approved,
            }

            st.session_state.builder_result = validate_agreement(
                agreement, POLICIES, state
            )
            st.session_state.builder_result_id = selected_id

        if (
            "builder_result" in st.session_state
            and st.session_state.builder_result_id == selected_id
        ):
            result = st.session_state.builder_result

            if result["valid"]:
                st.success("Configured validation checks passed.")
            else:
                st.error("The proposal has validation issues.")

            for violation in result["violations"]:
                st.warning(f'{violation["constraint"]}: {violation["message"]}')

            st.caption("Passing constraints does not prove participant consent.")


# --------------------------------------------------
# TAB 3: EVALUATION
# --------------------------------------------------
with tab3:
    st.subheader("Prototype Evaluation")
    st.write("Enter results from completed test scenarios.")

    col1, col2 = st.columns(2)

    with col1:
        tested = st.number_input("Scenarios tested", min_value=0, value=0, step=1)
        agreements = st.number_input("Agreements reached", min_value=0, value=0, step=1)

    with col2:
        compliant = st.number_input(
            "Agreements passing constraints", min_value=0, value=0, step=1
        )
        unresolved = st.number_input(
            "Unresolved cases", min_value=0, value=0, step=1
        )

    if tested > 0:
        st.metric("Agreement rate", f"{100 * agreements / tested:.1f}%")
        st.metric("Constraint-compliance rate", f"{100 * compliant / tested:.1f}%")
    else:
        st.info("Enter the number of tested scenarios to calculate rates.")

    st.metric("Unresolved cases", unresolved)
    st.caption(
        "Also evaluate fairness, utility, trust, commitment extraction, "
        "transparency and resistance to manipulation."
    )


# --------------------------------------------------
# TAB 4: FULL MEDIATION AND AGREEMENT SELECTION
# --------------------------------------------------
with tab4:
    st.subheader("Run a Mediation Session")

    employee_statement = st.text_area(
        "Employee statement",
        placeholder="I have too many tasks and need a fairer workload.",
        height=100,
        key="full_employee_statement",
    )

    manager_statement = st.text_area(
        "Manager statement",
        placeholder="We must meet the project deadline within the available budget.",
        height=100,
        key="full_manager_statement",
    )

    if st.button("Run Mediation", type="primary", key="run_full_mediation"):
        if not employee_statement.strip() or not manager_statement.strip():
            st.warning("Please provide both statements.")
        else:
            try:
                result = engine.run(employee_statement, manager_statement)
                st.session_state.full_mediation_result = result
                st.session_state.full_mediation_agreement_result = None
            except Exception as exc:
                st.error(f"Mediation failed: {exc}")

    if "full_mediation_result" in st.session_state:
        result = st.session_state.full_mediation_result
        state = result["state"]

        st.divider()
        st.subheader("Mediation Results")

        col1, col2, col3 = st.columns(3)
        col1.metric("Conflict topic", ", ".join(result["topic"]) or "General")
        col2.metric(
            "Safety concern",
            "Detected" if result["safety_detected"] else "Not detected",
        )
        col3.metric("Selected tactic", result["tactic"].replace("_", " ").title())

        if state["status"] == "requires_human_review":
            st.error(result["mediator_response"])
            st.warning("Agreement generation is disabled pending human review.")
        else:
            st.info("Mediator response")
            st.write(result["mediator_response"])

            st.write("**Planner phase:**", result["planner_phase"])

            with st.expander("Trust estimates"):
                st.json(result["trust_summary"])

            with st.expander("Employee NLU output"):
                st.json(result["employee_nlu"])

            with st.expander("Manager NLU output"):
                st.json(result["manager_nlu"])

            with st.expander("Session transcript"):
                for turn in state["transcript"]:
                    st.markdown(f'**{turn["speaker"].title()}:** {turn["text"]}')

            st.divider()
            st.subheader("Choose and Validate a Proposed Agreement")

            proposals = engine.generate_agreements()

            if proposals:
                proposal_id = st.selectbox(
                    "Select a candidate",
                    options=[p["id"] for p in proposals],
                    format_func=lambda pid: next(
                        f'{p["name"]} — ₹{p["budget"]:,}, '
                        f'{p["hours_per_week"]} hours/week, '
                        f'{p["deadline_days"]} days'
                        for p in proposals if p["id"] == pid
                    ),
                    key="full_proposal_id",
                )

                proposal = next(p for p in proposals if p["id"] == proposal_id)
                st.write(proposal["description"])

                manager_ok = st.checkbox(
                    "Manager approval obtained",
                    key=f"full_manager_ok_{proposal_id}",
                )
                hr_ok = st.checkbox(
                    "HR approval obtained, if required",
                    key=f"full_hr_ok_{proposal_id}",
                )

                agreement = {
                    **proposal,
                    "manager_approved": manager_ok,
                    "hr_approved": hr_ok,
                }

                if st.button("Validate Selected Proposal", key="validate_full_proposal"):
                    validation = engine.validate_proposal(agreement, state)
                    st.session_state.full_mediation_agreement_result = {
                        "proposal_id": proposal_id,
                        "result": validation,
                    }

                saved = st.session_state.get("full_mediation_agreement_result")

                if saved and saved["proposal_id"] == proposal_id:
                    validation = saved["result"]

                    if validation["valid"]:
                        st.success("The proposal passes configured constraints.")
                    else:
                        st.error("The proposal has outstanding validation issues.")

                    for violation in validation["violations"]:
                        st.warning(
                            f'{violation["constraint"]}: {violation["message"]}'
                        )

                    if validation["approved"]:
                        st.success("Required configured approvals are present.")
                    else:
                        st.info("The proposal is not yet approved.")

                    st.caption(validation["note"])

    st.caption(
        "This prototype does not automatically settle disputes. Participants "
        "must review proposals, and safety concerns require authorized human review."
    )
