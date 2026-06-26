"""Prompt Playground page."""

from __future__ import annotations

import streamlit as st

from backend.service_factory import get_services
from frontend.components import (
    generation_config_form,
    input_variables_editor,
    model_selector,
    response_viewer,
    show_error,
)
from frontend.session import get_user_id
from frontend.theme import page_header, status_indicator
from models.schemas import ExperimentCreate, PromptRunRequest
from utils.exceptions import AppError
from utils.formatters import highlight_variables


def render_playground() -> None:
    page_header("Prompt Playground", "Create, configure, and run prompts with your LLM")
    user_id = get_user_id()
    if not user_id:
        return

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("✏️ Prompt Editor")
        system_prompt = st.text_area(
            "System Prompt",
            value="You are a helpful, accurate, and professional AI assistant.",
            height=120,
        )
        user_prompt = st.text_area(
            "User Prompt",
            value="Explain prompt engineering best practices in 5 bullet points.",
            height=200,
        )
        detected_vars = highlight_variables(user_prompt + system_prompt)
        if detected_vars:
            st.caption(f"Detected variables: {', '.join(set(detected_vars))}")

        input_variables = input_variables_editor("playground_vars")
        model = model_selector("playground_model")
        config = generation_config_form("pg_")

    with col_right:
        st.subheader("📤 Response")
        response_placeholder = st.empty()
        metrics_placeholder = st.empty()

        col_run, col_stop = st.columns(2)
        with col_run:
            run_clicked = st.button("▶️ Run Prompt", type="primary", use_container_width=True)
        with col_stop:
            if st.button("⏹️ Stop Generation", use_container_width=True):
                st.session_state.stop_generation = True

        if run_clicked:
            st.session_state.stop_generation = False
            if not user_prompt.strip():
                st.error("User prompt cannot be empty.")
            else:
                try:
                    with get_services() as services:
                        request = PromptRunRequest(
                            system_prompt=system_prompt,
                            user_prompt=user_prompt,
                            input_variables=input_variables,
                            model=model,
                            config=config,
                        )

                        if config.stream:
                            full_response = ""
                            with st.spinner("Streaming response..."):
                                try:
                                    for chunk in services.gemini.generate_stream(
                                        system_prompt=request.system_prompt,
                                        user_prompt=request.user_prompt,
                                        input_variables=request.input_variables,
                                        model=request.model,
                                        config=request.config,
                                    ):
                                        if st.session_state.stop_generation:
                                            break
                                        full_response += chunk
                                        response_placeholder.markdown(full_response)
                                except AppError as exc:
                                    show_error(exc)
                                    full_response = ""

                            result_text = full_response
                            exec_time = 0.0
                            tokens = len(full_response.split())
                            success = bool(full_response.strip())
                        else:
                            with st.spinner("Generating response..."):
                                result = services.gemini.generate(
                                    system_prompt=request.system_prompt,
                                    user_prompt=request.user_prompt,
                                    input_variables=request.input_variables,
                                    model=request.model,
                                    config=request.config,
                                )
                            result_text = result.text
                            exec_time = result.execution_time_ms
                            tokens = result.token_usage
                            success = result.success
                            status_indicator(success, "Generation completed" if success else "Generation failed")

                        st.session_state.last_response = result_text
                        metrics_placeholder.metric("Execution Time", f"{exec_time:.0f} ms")
                        metrics_placeholder.metric("Token Usage (est.)", tokens)

                        services.experiments.create(
                            user_id,
                            ExperimentCreate(
                                title=f"Playground Run - {user_prompt[:40]}",
                                notes="Auto-saved from Playground",
                                status="completed" if success else "failed",
                                model_used=model,
                                input_variables=input_variables,
                                system_prompt=system_prompt,
                                user_prompt=user_prompt,
                                response_text=result_text,
                                temperature=config.temperature,
                                top_p=config.top_p,
                                top_k=config.top_k,
                                max_tokens=config.max_tokens,
                                execution_time_ms=exec_time,
                                token_usage=tokens,
                                success=success,
                            ),
                        )
                        services.analytics.record_event(
                            user_id,
                            event_type="playground_run",
                            model_used=model,
                            execution_time_ms=exec_time,
                            token_usage=tokens,
                            success=success,
                        )

                except AppError as exc:
                    show_error(exc)

        if st.session_state.get("last_response"):
            response_viewer(st.session_state.last_response, "playground")

        with st.expander("💾 Save to Library"):
            save_title = st.text_input("Prompt Title", value="My Playground Prompt")
            save_category = st.selectbox(
                "Category",
                ["General", "Coding", "Creative Writing", "Data Analysis", "Customer Support", "Marketing"],
            )
            if st.button("Save Prompt"):
                try:
                    from models.schemas import PromptCreate

                    with get_services() as services:
                        services.prompts.create(
                            user_id,
                            PromptCreate(
                                title=save_title,
                                system_prompt=system_prompt,
                                user_prompt=user_prompt,
                                category=save_category,
                            ),
                        )
                        st.success("Prompt saved to library!")
                except AppError as exc:
                    show_error(exc)
