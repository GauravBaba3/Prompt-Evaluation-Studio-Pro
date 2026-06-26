"""Streamlit session state management."""

from __future__ import annotations

import streamlit as st

from models.schemas import UserOut


def init_session_state() -> None:
    defaults = {
        "authenticated": False,
        "user": None,
        "remember_token": None,
        "dark_mode": True,
        "current_page": "Dashboard",
        "stop_generation": False,
        "last_response": "",
        "selected_prompt_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def set_user(user: UserOut, remember_token: str | None = None) -> None:
    st.session_state.authenticated = True
    st.session_state.user = user
    st.session_state.remember_token = remember_token
    st.session_state.dark_mode = user.theme == "dark"


def clear_user() -> None:
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.remember_token = None


def get_user_id() -> int | None:
    user = st.session_state.get("user")
    return user.id if user else None


def require_auth() -> bool:
    return bool(st.session_state.get("authenticated") and st.session_state.get("user"))
