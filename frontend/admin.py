"""Admin Settings page."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from backend.service_factory import get_services
from config.constants import GEMINI_MODELS, HF_MODELS
from frontend.components import show_error
from frontend.session import get_user_id
from frontend.theme import page_header, status_indicator


def render_admin() -> None:
    page_header("Admin Settings", "Configure API, theme, database backup and restore")
    user_id = get_user_id()
    if not user_id:
        return

    try:
        with get_services() as services:
            provider = services.settings.get_llm_provider()

            if provider == "gemini":
                st.subheader("🔑 Gemini API Configuration")
                current_key = services.settings.get_gemini_api_key()
                masked_key = ("*" * (len(current_key) - 4) + current_key[-4:]) if len(current_key) > 4 else "Not set"
                st.caption(f"Current key: {masked_key}")

                api_key = st.text_input("Gemini API Key", type="password", placeholder="Enter your API key")
                model = st.selectbox(
                    "Default Model",
                    GEMINI_MODELS,
                    index=GEMINI_MODELS.index(services.settings.get_gemini_model())
                    if services.settings.get_gemini_model() in GEMINI_MODELS
                    else 0,
                )

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Save API Configuration", type="primary"):
                        if api_key.strip():
                            services.settings.save_gemini_config(api_key.strip(), model)
                            st.success("API configuration saved!")
                        else:
                            st.warning("Enter a valid API key.")
                with col2:
                    if st.button("🔗 Test Connection"):
                        from services.gemini_service import GeminiService

                        test_service = services.llm
                        if api_key.strip():
                            test_service = GeminiService(api_key=api_key.strip(), model=model)
                        success, message = test_service.test_connection()
                        status_indicator(success, message)
            else:
                st.subheader("🤗 Hugging Face API Configuration")
                current_token = services.settings.get_hf_token()
                masked_token = (
                    "*" * (len(current_token) - 4) + current_token[-4:]
                ) if len(current_token) > 4 else "Not set"
                st.caption(f"Current token: {masked_token}")
                st.caption(f"Model: {services.settings.get_hf_model()}")

                hf_token = st.text_input("Hugging Face Token", type="password", placeholder="Enter your HF token")
                hf_model = st.selectbox(
                    "Default Model",
                    HF_MODELS,
                    index=HF_MODELS.index(services.settings.get_hf_model())
                    if services.settings.get_hf_model() in HF_MODELS
                    else 0,
                )

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Save API Configuration", type="primary"):
                        if hf_token.strip():
                            services.settings.save_hf_config(hf_token.strip(), hf_model)
                            st.success("API configuration saved!")
                        else:
                            st.warning("Enter a valid Hugging Face token.")
                with col2:
                    if st.button("🔗 Test Connection"):
                        from services.huggingface_service import HuggingFaceService

                        test_service = services.llm
                        if hf_token.strip():
                            test_service = HuggingFaceService(api_token=hf_token.strip(), model=hf_model)
                        success, message = test_service.test_connection()
                        status_indicator(success, message)

            st.caption(f"Active provider: **{provider}** (set `LLM_PROVIDER` in `.env` to switch)")

            st.divider()
            st.subheader("🎨 Theme")
            theme = st.radio("Application Theme", ["dark", "light"], horizontal=True)
            if st.button("Apply Theme"):
                services.auth.update_theme(user_id, theme)
                st.session_state.dark_mode = theme == "dark"
                st.success(f"Theme set to {theme}")

            st.divider()
            st.subheader("💾 Database Backup & Restore")
            backups = services.settings.list_backups()

            if st.button("Create Backup"):
                path = services.settings.backup_database()
                st.success(f"Backup created: {path}")

            if backups:
                backup_names = [b.name for b in backups]
                selected_backup = st.selectbox("Available Backups", backup_names)
                if st.button("Restore Selected Backup"):
                    services.settings.restore_database(services.settings.settings.backups_dir / selected_backup)
                    st.success("Database restored! Please refresh the page.")
            else:
                st.info("No backups available yet.")

            st.divider()
            st.subheader("⚠️ Danger Zone")
            confirm = st.checkbox("I understand this will delete all data")
            if st.button("🗑️ Clear Database", type="secondary") and confirm:
                services.settings.clear_database()
                st.warning("Database cleared and reinitialized.")

    except Exception as exc:
        show_error(exc)
