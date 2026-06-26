"""Dashboard page."""

from __future__ import annotations

import streamlit as st

from backend.service_factory import get_services
from config.constants import DEFAULT_CATEGORIES
from frontend.components import show_error
from frontend.session import get_user_id
from frontend.theme import metric_card, page_header


def render_dashboard() -> None:
    page_header("Dashboard", "Overview of your prompt engineering workspace")
    user_id = get_user_id()
    if not user_id:
        st.warning("Please log in.")
        return

    search = st.text_input("🔍 Search prompts and experiments", placeholder="Search by title, category, or content...")

    try:
        with get_services() as services:
            stats = services.analytics.get_dashboard_stats(user_id)
            prompts = services.prompts.list_prompts(user_id, search=search)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                metric_card("Total Prompts", str(stats.total_prompts))
            with col2:
                metric_card("Experiments", str(stats.total_experiments))
            with col3:
                metric_card("Avg Response Time", f"{stats.avg_response_time_ms:.0f} ms")
            with col4:
                metric_card("Success Rate", f"{stats.success_rate:.1f}%")

            st.divider()
            col_a, col_b = st.columns(2)

            with col_a:
                st.subheader("📊 Prompt Categories")
                if stats.categories:
                    st.bar_chart(stats.categories)
                else:
                    st.info("No category data yet. Create prompts to see distribution.")

            with col_b:
                st.subheader("🕐 Recent Experiments")
                if stats.recent_experiments:
                    for exp in stats.recent_experiments:
                        status_icon = "✅" if exp.success else "❌"
                        st.markdown(
                            f"**{exp.title}** {status_icon}  \n"
                            f"Model: `{exp.model_used}` | Time: `{exp.execution_time_ms:.0f}ms` | Status: `{exp.status}`"
                        )
                else:
                    st.info("No experiments yet. Run prompts in the Playground.")

            if search and prompts:
                st.subheader("🔍 Search Results")
                for prompt in prompts[:10]:
                    st.markdown(f"**{prompt.title}** — {prompt.category} (v{prompt.current_version})")

            dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.get("dark_mode", True))
            if dark_mode != st.session_state.get("dark_mode"):
                st.session_state.dark_mode = dark_mode
                theme = "dark" if dark_mode else "light"
                with get_services() as services:
                    services.auth.update_theme(user_id, theme)

    except Exception as exc:
        show_error(exc)
