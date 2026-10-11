
import json
import streamlit as st

from logic.agreement_report import create_agreement_record


def render_agreement_builder(candidates):
    st.subheader("📄 Agreement Contract Builder")
    st.caption(
        "Generate a structured record after both participants accept "
        "a feasible proposal."
    )

    if not candidates:
        st.info("Analyse a conflict and generate candidate agreements first.")
        return

    options = [
        candidate for candidate in candidates
        if candidate.get("feasible", False)
    ]

    if not options:
        st.warning("No feasible agreements are available.")
        return

    selected = st.selectbox(
        "Select a feasible agreement",
        options,
        format_func=lambda item: item["name"],
    )

    st.write(selected["description"])
    st.write(
        f"Budget: {selected['budget']:,} | "
        f"Hours/week: {selected['hours_per_week']} | "
        f"Deadline: {selected['deadline_days']} days"
    )

    with st.form("agreement_contract_form"):
        employee_name = st.text_input(
            "Employee name", value="Employee"
        )
        manager_name = st.text_input(
            "Manager name", value="Manager"
        )

        employee_commitment = st.text_area(
            "Employee responsibility",
            placeholder="Example: Complete the assigned testing tasks.",
        )
        manager_commitment = st.text_area(
            "Manager responsibility",
            placeholder="Example: Redistribute tasks and review workload.",
        )

        follow_up_days = st.number_input(
            "Follow-up after (days)",
            min_value=1,
            max_value=90,
            value=7,
        )

        employee_accepted = st.checkbox(
            "Employee has explicitly accepted this proposal"
        )
        manager_accepted = st.checkbox(
            "Manager has explicitly accepted this proposal"
        )

        submitted = st.form_submit_button(
            "Generate agreement record"
        )

    if submitted:
        if not employee_accepted or not manager_accepted:
            st.error(
                "Both participants must explicitly accept the proposal."
            )
            return

        try:
            record = create_agreement_record(
                selected,
                employee_name,
                manager_name,
                employee_commitment,
                manager_commitment,
                follow_up_days,
            )
        except (ValueError, KeyError, TypeError) as error:
            st.error(f"Could not generate agreement: {error}")
            return

        record["approvals"]["employee_accepted"] = True
        record["approvals"]["manager_accepted"] = True

        st.session_state["agreement_record"] = record
        st.success("Agreement record generated successfully.")

    record = st.session_state.get("agreement_record")

    if record:
        st.subheader("Generated agreement")
        st.json(record)

        st.download_button(
            "⬇️ Download agreement JSON",
            data=json.dumps(record, indent=2),
            file_name=f"{record['agreement_id']}.json",
            mime="application/json",
        )
