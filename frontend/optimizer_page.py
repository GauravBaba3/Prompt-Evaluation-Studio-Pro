"""Prompt Optimizer page."""

from __future__ import annotations

import streamlit as st

from backend.service_factory import get_services
from frontend.components import show_error
from frontend.session import get_user_id
from frontend.theme import page_header
from models.schemas import OptimizerRequest


def render_optimizer() -> None:
    page_header("Prompt Optimizer", "Rewrite and improve prompts professionally")
    user_id = get_user_id()
    if not user_id:
        return

    prompt_text = st.text_area(
        "Prompt to Optimize",
        value="tell me about ai and make it good",
        height=120,
    )
    system_prompt = st.text_area("Current System Prompt (optional)", height=80)
    goal = st.text_input(
        "Optimization Goal",
        value="Improve clarity, accuracy, and structure while reducing hallucinations.",
    )
    num_versions = st.slider("Number of Optimized Versions", 1, 5, 3)

    if st.button("✨ Optimize Prompt", type="primary", use_container_width=True):
        try:
            with get_services() as services:
                with st.spinner("Generating optimized versions..."):
                    result = services.optimizer.optimize(
                        OptimizerRequest(
                            prompt_text=prompt_text,
                            system_prompt=system_prompt,
                            goal=goal,
                            num_versions=num_versions,
                        )
                    )
                st.session_state.optimizer_result = result
                services.analytics.record_event(user_id, event_type="optimization", success=True)
        except Exception as exc:
            show_error(exc)

    if st.session_state.get("optimizer_result"):
        result = st.session_state.optimizer_result
        st.success(result.summary)

        for index, version in enumerate(result.versions):
            with st.expander(f"📦 {version.title}", expanded=index == 0):
                st.subheader("Optimized Prompt")
                st.code(version.optimized_prompt, language="markdown")
                if version.system_prompt:
                    st.subheader("Recommended System Prompt")
                    st.code(version.system_prompt, language="markdown")
                st.subheader("Improvements")
                for improvement in version.improvements:
                    st.markdown(f"- {improvement}")
                if st.button(f"Use Version {index + 1} in Playground", key=f"use_opt_{index}"):
                    st.session_state.playground_user = version.optimized_prompt
                    if version.system_prompt:
                        st.session_state.playground_system = version.system_prompt
                    st.session_state.current_page = "Playground"
                    st.rerun()
