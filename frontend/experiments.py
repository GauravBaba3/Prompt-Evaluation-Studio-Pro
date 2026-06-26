"""Experiment Manager page."""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from backend.service_factory import get_services
from config.constants import EXPERIMENT_STATUSES
from frontend.components import show_error
from frontend.session import get_user_id
from frontend.theme import page_header


def render_experiments() -> None:
    page_header("Experiment Manager", "Track, annotate, and export your prompt experiments")
    user_id = get_user_id()
    if not user_id:
        return

    status_filter = st.selectbox("Filter by Status", ["All"] + EXPERIMENT_STATUSES)

    try:
        with get_services() as services:
            experiments = services.experiments.list_experiments(
                user_id,
                status=status_filter if status_filter != "All" else None,
            )

            if experiments:
                df = pd.DataFrame(
                    [
                        {
                            "ID": e.id,
                            "Title": e.title,
                            "Status": e.status,
                            "Model": e.model_used,
                            "Time (ms)": e.execution_time_ms,
                            "Tokens": e.token_usage,
                            "Success": "✅" if e.success else "❌",
                            "Created": str(e.created_at)[:19] if e.created_at else "",
                        }
                        for e in experiments
                    ]
                )
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No experiments found.")

            selected_id = st.number_input("Experiment ID for details", min_value=1, value=1, step=1)
            experiment = services.experiments.get_by_id(user_id, int(selected_id))

            if experiment:
                st.subheader(f"📝 {experiment.title}")
                col1, col2, col3 = st.columns(3)
                col1.metric("Execution Time", f"{experiment.execution_time_ms:.0f} ms")
                col2.metric("Token Usage", experiment.token_usage)
                col3.metric("Success Rate", "Pass" if experiment.success else "Fail")

                new_status = st.selectbox("Update Status", EXPERIMENT_STATUSES, index=EXPERIMENT_STATUSES.index(experiment.status) if experiment.status in EXPERIMENT_STATUSES else 0)
                new_notes = st.text_area("Experiment Notes", experiment.notes, height=120)

                if st.button("Save Changes"):
                    services.experiments.update_status(user_id, experiment.id, new_status)
                    services.experiments.update_notes(user_id, experiment.id, new_notes)
                    st.success("Experiment updated!")
                    st.rerun()

                with st.expander("View Full Details"):
                    st.markdown(f"**Model:** {experiment.model_used}")
                    st.markdown(f"**System Prompt:**\n```\n{experiment.system_prompt}\n```")
                    st.markdown(f"**User Prompt:**\n```\n{experiment.user_prompt}\n```")
                    st.markdown(f"**Response:**\n{experiment.response_text}")
                    try:
                        st.json(json.loads(experiment.input_variables))
                    except json.JSONDecodeError:
                        st.text(experiment.input_variables)

            export_col1, export_col2 = st.columns(2)
            with export_col1:
                if st.button("📤 Export History (JSON)"):
                    data = services.experiments.export_history(user_id)
                    path = services.export.export_json(data, "experiments")
                    st.success(f"Exported to {path}")
            with export_col2:
                if st.button("📤 Export History (CSV)"):
                    data = services.experiments.export_history(user_id)
                    path = services.export.export_csv(data, "experiments")
                    st.success(f"Exported to {path}")

    except Exception as exc:
        show_error(exc)
