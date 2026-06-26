"""UI theme and styling."""

from __future__ import annotations

import streamlit as st

CUSTOM_CSS = """
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #6366F1, #8B5CF6, #EC4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #1E293B 0%, #334155 100%);
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid #475569;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #6366F1;
    }
    .stat-label {
        font-size: 0.875rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .winner-badge {
        background: linear-gradient(90deg, #F59E0B, #EAB308);
        color: #1E293B;
        padding: 4px 12px;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.75rem;
    }
    .status-success { color: #22C55E; font-weight: 600; }
    .status-error { color: #EF4444; font-weight: 600; }
    .status-running { color: #3B82F6; font-weight: 600; }
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
    }
    .block-container { padding-top: 1.5rem; }
</style>
"""


def apply_theme() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "") -> None:
    st.markdown(f'<p class="main-header">{title}</p>', unsafe_allow_html=True)
    if subtitle:
        st.caption(subtitle)


def metric_card(label: str, value: str, delta: str = "") -> None:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-label">{label}</div>
            <div class="stat-value">{value}</div>
            {f'<div style="color:#94A3B8;font-size:0.8rem;">{delta}</div>' if delta else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_indicator(success: bool, message: str) -> None:
    css_class = "status-success" if success else "status-error"
    icon = "✅" if success else "❌"
    st.markdown(f'<span class="{css_class}">{icon} {message}</span>', unsafe_allow_html=True)
