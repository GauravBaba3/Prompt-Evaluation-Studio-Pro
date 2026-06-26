"""Reusable Streamlit components."""

from __future__ import annotations

import json
from typing import Any

import pandas as pd
import streamlit as st

from config.constants import DEFAULT_CATEGORIES, GEMINI_MODELS, HF_MODELS
from config.settings import get_settings
from models.schemas import GenerationConfig
from utils.exceptions import AppError
from utils.formatters import render_markdown_safe


def show_error(error: Exception) -> None:
    if isinstance(error, AppError):
        st.error(f"**{error.code}**: {error.message}")
    else:
        st.error(str(error))


def generation_config_form(prefix: str = "") -> GenerationConfig:
    col1, col2, col3 = st.columns(3)
    with col1:
        temperature = st.slider(f"{prefix}Temperature", 0.0, 2.0, 0.7, 0.1)
        top_p = st.slider(f"{prefix}Top P", 0.0, 1.0, 0.95, 0.01)
    with col2:
        top_k = st.slider(f"{prefix}Top K", 1, 100, 40)
        max_tokens = st.number_input(f"{prefix}Max Tokens", 256, 8192, 2048, 256)
    with col3:
        safety_level = st.selectbox(
            f"{prefix}Safety Settings",
            ["BLOCK_ONLY_HIGH", "BLOCK_MEDIUM_AND_ABOVE", "BLOCK_LOW_AND_ABOVE", "BLOCK_NONE"],
        )
        json_mode = st.checkbox(f"{prefix}Structured JSON Mode", value=False)
        stream_mode = st.checkbox(f"{prefix}Streaming Mode", value=False)
    return GenerationConfig(
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        max_tokens=max_tokens,
        safety_level=safety_level,
        json_mode=json_mode,
        stream=stream_mode,
    )


def model_selector(key: str = "model") -> str:
    settings = get_settings()
    models = GEMINI_MODELS if settings.llm_provider == "gemini" else HF_MODELS
    default_model = settings.gemini_model if settings.llm_provider == "gemini" else settings.hf_model
    index = models.index(default_model) if default_model in models else 0
    return st.selectbox("Model", models, index=index, key=key)


def category_selector(key: str = "category", include_all: bool = True) -> str:
    options = (["All"] + DEFAULT_CATEGORIES) if include_all else DEFAULT_CATEGORIES
    return st.selectbox("Category", options, key=key)


def input_variables_editor(key: str = "input_vars") -> dict[str, str]:
    st.subheader("Input Variables")
    raw = st.text_area(
        "Variables (JSON format)",
        value='{"name": "World", "topic": "AI"}',
        height=100,
        key=key,
    )
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return {str(k): str(v) for k, v in parsed.items()}
        st.warning("Variables must be a JSON object.")
    except json.JSONDecodeError:
        st.warning("Invalid JSON. Using empty variables.")
    return {}


def response_viewer(response_text: str, key_prefix: str = "resp") -> None:
    tab1, tab2, tab3 = st.tabs(["Rendered", "Raw", "Actions"])
    with tab1:
        st.markdown(render_markdown_safe(response_text), unsafe_allow_html=True)
    with tab2:
        st.code(response_text, language="markdown")
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Copy Response", key=f"{key_prefix}_copy"):
                st.session_state[f"{key_prefix}_clipboard"] = response_text
                st.toast("Response copied to session clipboard!")
            if f"{key_prefix}_clipboard" in st.session_state:
                st.text_area("Clipboard", st.session_state[f"{key_prefix}_clipboard"], height=100)
        with col2:
            st.download_button(
                "⬇️ Download Response",
                data=response_text,
                file_name="response.md",
                mime="text/markdown",
                key=f"{key_prefix}_download",
            )


def results_dataframe(results: list[dict[str, Any]], highlight_winner: bool = True) -> None:
    if not results:
        st.info("No results to display.")
        return
    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True, hide_index=True)
    if highlight_winner:
        winners = [r for r in results if r.get("is_winner")]
        for winner in winners:
            st.markdown(
                f'<span class="winner-badge">🏆 Winner: {winner.get("label", "Unknown")}</span>',
                unsafe_allow_html=True,
            )
