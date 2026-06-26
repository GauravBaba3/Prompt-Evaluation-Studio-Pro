"""
Prompt Evaluation Studio Pro
Professional Prompt Engineering Platform powered by Google Gemini.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from database.connection import init_db
from frontend.admin import render_admin
from frontend.analytics_page import render_analytics
from frontend.auth_pages import render_auth_page
from frontend.comparison import render_comparison
from frontend.dashboard import render_dashboard
from frontend.evaluation_page import render_evaluation
from frontend.experiments import render_experiments
from frontend.export_page import render_export
from frontend.library import render_library
from frontend.optimizer_page import render_optimizer
from frontend.playground import render_playground
from frontend.session import clear_user, init_session_state, require_auth
from frontend.theme import apply_theme
from frontend.versions import render_version_control

PAGES = {
    "Dashboard": render_dashboard,
    "Playground": render_playground,
    "Comparison": render_comparison,
    "Version Control": render_version_control,
    "Library": render_library,
    "Experiments": render_experiments,
    "Evaluation": render_evaluation,
    "Optimizer": render_optimizer,
    "Analytics": render_analytics,
    "Export": render_export,
    "Admin": render_admin,
}


def main() -> None:
    st.set_page_config(
        page_title="Prompt Evaluation Studio Pro",
        page_icon="🧪",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_theme()
    init_session_state()
    init_db()

    if not require_auth():
        render_auth_page()
        return

    user = st.session_state.user
    with st.sidebar:
        st.markdown("## 🧪 Prompt Studio Pro")
        st.caption(f"Logged in as **{user.username}**")
        st.divider()

        for page_name in PAGES:
            if st.button(page_name, use_container_width=True, key=f"nav_{page_name}"):
                st.session_state.current_page = page_name

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            from backend.service_factory import get_services

            with get_services() as services:
                services.auth.logout(user.id)
            clear_user()
            st.rerun()

        st.caption("Powered by Google Gemini")

    current_page = st.session_state.get("current_page", "Dashboard")
    render_fn = PAGES.get(current_page, render_dashboard)
    render_fn()


if __name__ == "__main__":
    main()
