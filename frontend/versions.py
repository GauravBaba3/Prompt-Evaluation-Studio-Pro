"""Prompt Version Control page."""

from __future__ import annotations

import streamlit as st

from backend.service_factory import get_services
from frontend.components import category_selector, show_error
from frontend.session import get_user_id
from frontend.theme import page_header
from models.schemas import PromptCreate, PromptUpdate


def render_version_control() -> None:
    page_header("Version Control", "Manage prompt versions, tags, and favorites")
    user_id = get_user_id()
    if not user_id:
        return

    try:
        with get_services() as services:
            prompts = services.prompts.list_prompts(user_id)
            if not prompts:
                st.info("No prompts in library. Create one in the Playground or Library.")
                return

            prompt_options = {f"{p.title} (v{p.current_version})": p.id for p in prompts}
            selected_label = st.selectbox("Select Prompt", list(prompt_options.keys()))
            prompt_id = prompt_options[selected_label]
            prompt = services.prompts.get_by_id(user_id, prompt_id)

            if not prompt:
                st.error("Prompt not found.")
                return

            col1, col2 = st.columns(2)
            with col1:
                st.text_area("System Prompt", prompt.system_prompt, height=120, disabled=True, key="vc_sys")
                st.text_area("User Prompt", prompt.user_prompt, height=150, disabled=True, key="vc_user")
            with col2:
                new_title = st.text_input("Title", prompt.title)
                new_category = category_selector("vc_cat", include_all=False)
                if new_category != prompt.category:
                    st.session_state.vc_new_cat = new_category
                tags = st.text_input("Tags (comma-separated)", prompt.tags)
                col_fav, col_pin = st.columns(2)
                with col_fav:
                    is_favorite = st.checkbox("⭐ Favorite", prompt.is_favorite)
                with col_pin:
                    is_pinned = st.checkbox("📌 Pinned", prompt.is_pinned)

                if st.button("Update Metadata"):
                    services.prompts.update(
                        user_id,
                        prompt_id,
                        PromptUpdate(
                            title=new_title,
                            category=st.session_state.get("vc_new_cat", prompt.category),
                            tags=[t.strip() for t in tags.split(",") if t.strip()],
                            is_favorite=is_favorite,
                            is_pinned=is_pinned,
                        ),
                    )
                    st.success("Metadata updated!")
                    st.rerun()

            st.divider()
            action_col1, action_col2, action_col3, action_col4 = st.columns(4)
            with action_col1:
                if st.button("📸 Create Version"):
                    note = st.text_input("Change note", value="Manual version snapshot")
                    services.prompts.create_version(user_id, prompt_id, note)
                    st.success("New version created!")
                    st.rerun()
            with action_col2:
                if st.button("📋 Duplicate"):
                    dup = services.prompts.duplicate(user_id, prompt_id)
                    st.success(f"Duplicated as '{dup.title}'")
            with action_col3:
                versions = services.prompts.list_versions(user_id, prompt_id)
                version_options = {f"v{v.version_number} - {v.change_note}": v.id for v in versions}
                selected_version = st.selectbox("Restore Version", list(version_options.keys()))
                if st.button("⏪ Restore"):
                    services.prompts.restore_version(user_id, prompt_id, version_options[selected_version])
                    st.success("Version restored!")
                    st.rerun()
            with action_col4:
                if st.button("🗑️ Delete Prompt"):
                    services.prompts.delete(user_id, prompt_id)
                    st.warning("Prompt deleted.")
                    st.rerun()

            st.subheader("📜 Version History")
            versions = services.prompts.list_versions(user_id, prompt_id)
            for version in versions:
                with st.expander(f"Version {version.version_number} — {version.change_note}"):
                    st.code(version.user_prompt, language="markdown")
                    if st.button(f"View Diff v{version.version_number}", key=f"diff_{version.id}"):
                        diff = services.prompts.get_version_diff(user_id, prompt_id, version.id)
                        for status, line in diff:
                            if status == "added":
                                st.markdown(f":green[+ {line}]")
                            elif status == "removed":
                                st.markdown(f":red[- {line}]")
                            else:
                                st.text(line)

    except Exception as exc:
        show_error(exc)
