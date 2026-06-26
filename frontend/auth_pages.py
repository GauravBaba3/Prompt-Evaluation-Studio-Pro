"""Authentication pages."""

from __future__ import annotations

import streamlit as st

from backend.service_factory import get_services
from database.connection import init_db
from frontend.session import clear_user, set_user
from frontend.theme import page_header
from models.schemas import UserCreate, UserLogin
from utils.exceptions import AppError


def render_auth_page() -> None:
    page_header("Prompt Evaluation Studio Pro", "Professional Prompt Engineering Platform")
    init_db()

    tab_login, tab_signup = st.tabs(["🔐 Login", "📝 Sign Up"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            remember = st.checkbox("Remember session")
            submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
            if submitted:
                try:
                    with get_services() as services:
                        user, token = services.auth.login(
                            UserLogin(username=username, password=password, remember=remember)
                        )
                        set_user(user, token)
                        st.success(f"Welcome back, {user.username}!")
                        st.rerun()
                except AppError as exc:
                    st.error(exc.message)

    with tab_signup:
        with st.form("signup_form"):
            new_username = st.text_input("Choose Username")
            email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted_signup = st.form_submit_button("Create Account", use_container_width=True, type="primary")
            if submitted_signup:
                if new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    try:
                        with get_services() as services:
                            user = services.auth.register(
                                UserCreate(username=new_username, email=email, password=new_password)
                            )
                            services.prompts.seed_templates(user.id)
                            set_user(user)
                            st.success("Account created! Templates loaded.")
                            st.rerun()
                    except AppError as exc:
                        st.error(exc.message)

    st.info("Demo tip: Create an account to start experimenting with prompts. Configure your Gemini API key in Admin Settings.")
