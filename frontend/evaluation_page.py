"""AI Evaluation Engine page."""

from __future__ import annotations

import streamlit as st

from backend.service_factory import get_services
from config.constants import EVALUATION_CRITERIA
from frontend.components import show_error
from frontend.session import get_user_id
from frontend.theme import page_header


def render_evaluation() -> None:
    page_header("AI Evaluation Engine", "Automatically score prompt outputs using Gemini")
    user_id = get_user_id()
    if not user_id:
        return

    st.markdown("**Evaluation Criteria:** " + ", ".join(c.replace("_", " ").title() for c in EVALUATION_CRITERIA))

    prompt_text = st.text_area(
        "Original Prompt",
        value=st.session_state.get("eval_prompt", "Explain quantum computing to a beginner."),
        height=120,
    )
    response_text = st.text_area(
        "AI Response",
        value=st.session_state.get("last_response", "Quantum computing uses qubits that can exist in superposition..."),
        height=200,
    )
    context = st.text_area("Additional Context (optional)", height=80)

    if st.button("🔍 Evaluate Output", type="primary", use_container_width=True):
        try:
            from models.schemas import EvaluationRequest

            with get_services() as services:
                with st.spinner("Running AI evaluation..."):
                    result = services.evaluation.evaluate(
                        user_id,
                        EvaluationRequest(
                            prompt_text=prompt_text,
                            response_text=response_text,
                            context=context,
                        ),
                    )

                st.session_state.eval_result = result
                services.analytics.record_event(
                    user_id,
                    event_type="evaluation",
                    score=result.scores.overall_score,
                    success=True,
                )
        except Exception as exc:
            show_error(exc)

    if st.session_state.get("eval_result"):
        result = st.session_state.eval_result
        st.subheader(f"Overall Score: {result.scores.overall_score:.1f} / 100")

        cols = st.columns(3)
        score_items = [
            ("Accuracy", result.scores.accuracy),
            ("Completeness", result.scores.completeness),
            ("Hallucination Risk", result.scores.hallucination_risk),
            ("Grammar", result.scores.grammar),
            ("Structure", result.scores.structure),
            ("Professionalism", result.scores.professionalism),
            ("Formatting", result.scores.formatting),
            ("Readability", result.scores.readability),
            ("Prompt Effectiveness", result.scores.prompt_effectiveness),
        ]
        for index, (label, score) in enumerate(score_items):
            cols[index % 3].metric(label, f"{score:.1f}")

        st.subheader("📋 Detailed Explanation")
        st.markdown(result.explanation)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("💡 Suggested Prompt")
            st.code(result.suggested_prompt, language="markdown")
        with col2:
            st.subheader("✨ Optimized Prompt")
            st.code(result.optimized_prompt, language="markdown")

        if st.button("Apply Optimized Prompt to Playground"):
            st.session_state.playground_user = result.optimized_prompt
            st.session_state.current_page = "Playground"
            st.rerun()
