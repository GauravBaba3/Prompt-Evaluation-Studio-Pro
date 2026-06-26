"""Prompt Comparison page."""

from __future__ import annotations

import streamlit as st

from backend.service_factory import get_services
from frontend.components import (
    generation_config_form,
    input_variables_editor,
    model_selector,
    results_dataframe,
    show_error,
)
from frontend.session import get_user_id
from frontend.theme import page_header
from models.schemas import ComparisonPrompt, ComparisonRequest


def render_comparison() -> None:
    page_header("Prompt Comparison", "Compare 2-5 prompts with the same input and model")
    user_id = get_user_id()
    if not user_id:
        return

    num_prompts = st.slider("Number of prompts to compare", 2, 5, 2)
    input_variables = input_variables_editor("compare_vars")
    model = model_selector("compare_model")
    config = generation_config_form("cmp_")

    prompts: list[ComparisonPrompt] = []
    for index in range(num_prompts):
        with st.expander(f"Prompt {index + 1}", expanded=index < 2):
            label = st.text_input(f"Label {index + 1}", value=f"Variant {index + 1}", key=f"cmp_label_{index}")
            system = st.text_area(f"System Prompt {index + 1}", height=80, key=f"cmp_sys_{index}")
            user = st.text_area(
                f"User Prompt {index + 1}",
                value=f"Write a professional summary about {{topic}} for a {{audience}} audience.",
                height=100,
                key=f"cmp_user_{index}",
            )
            prompts.append(ComparisonPrompt(label=label, system_prompt=system, user_prompt=user))

    if st.button("🔬 Run Comparison", type="primary", use_container_width=True):
        try:
            with get_services() as services:
                with st.spinner("Running comparison across all prompts..."):
                    results = services.comparison.compare(
                        ComparisonRequest(
                            prompts=prompts,
                            input_variables=input_variables,
                            model=model,
                            config=config,
                        )
                    )
                result_dicts = [r.model_dump() for r in results]
                st.session_state.comparison_results = result_dicts

                services.analytics.record_event(
                    user_id,
                    event_type="comparison",
                    model_used=model,
                    success=True,
                    metadata={"prompt_count": len(prompts)},
                )
        except Exception as exc:
            show_error(exc)

    if st.session_state.get("comparison_results"):
        st.subheader("📊 Comparison Results")
        results_dataframe(st.session_state.comparison_results)

        for result in st.session_state.comparison_results:
            with st.expander(f"Response: {result['label']}"):
                st.markdown(result["response_text"])

        if st.button("Export Comparison PDF"):
            try:
                with get_services() as services:
                    path = services.export.export_comparison_pdf(st.session_state.comparison_results)
                    st.success(f"Exported to {path}")
            except Exception as exc:
                show_error(exc)
