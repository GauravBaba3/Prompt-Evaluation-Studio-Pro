"""Prompt Library page."""

from __future__ import annotations

import streamlit as st

from backend.service_factory import get_services
from frontend.components import category_selector, show_error
from frontend.session import get_user_id
from frontend.theme import page_header
from models.schemas import PromptCreate


def render_library() -> None:
    page_header("Prompt Library", "Search, filter, and manage your prompt collection")
    user_id = get_user_id()
    if not user_id:
        return

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        search = st.text_input("🔍 Search", placeholder="Title, tags, content...")
    with col2:
        category = category_selector("lib_category")
    with col3:
        sort_by = st.selectbox("Sort By", ["updated_at", "title", "usage_count", "success_rate", "last_used_at"])
    with col4:
        filter_type = st.selectbox("Filter", ["All", "Templates", "Favorites", "Pinned", "Recently Used"])

    try:
        with get_services() as services:
            if st.button("Load Built-in Templates"):
                count = services.prompts.seed_templates(user_id)
                st.success(f"Loaded {count} new templates.")

            prompts = services.prompts.list_prompts(
                user_id,
                search=search,
                category=category,
                templates_only=filter_type == "Templates",
                favorites_only=filter_type == "Favorites",
                pinned_only=filter_type == "Pinned",
                sort_by="last_used_at" if filter_type == "Recently Used" else sort_by,
            )

            st.metric("Total Prompts", len(prompts))

            for prompt in prompts:
                icons = ""
                if prompt.is_favorite:
                    icons += "⭐ "
                if prompt.is_pinned:
                    icons += "📌 "
                if prompt.is_template:
                    icons += "📄 "

                with st.expander(f"{icons}{prompt.title} — {prompt.category} (v{prompt.current_version})"):
                    st.markdown(f"**Tags:** {prompt.tags or 'None'}")
                    st.markdown(f"**Usage:** {prompt.usage_count} | **Success Rate:** {prompt.success_rate:.1f}%")
                    st.text_area("System", prompt.system_prompt, height=80, disabled=True, key=f"lib_sys_{prompt.id}")
                    st.text_area("User", prompt.user_prompt, height=100, disabled=True, key=f"lib_user_{prompt.id}")
                    if st.button("Open in Playground", key=f"load_{prompt.id}"):
                        st.session_state.playground_system = prompt.system_prompt
                        st.session_state.playground_user = prompt.user_prompt
                        st.session_state.current_page = "Playground"
                        services.prompts.record_usage(user_id, prompt.id, True)
                        st.rerun()

            with st.expander("➕ Create New Prompt"):
                title = st.text_input("Title", key="new_prompt_title")
                new_category = category_selector("new_cat", include_all=False)
                system = st.text_area("System Prompt", key="new_sys")
                user = st.text_area("User Prompt", key="new_user")
                if st.button("Create Prompt"):
                    if not user.strip():
                        st.error("User prompt is required.")
                    else:
                        services.prompts.create(
                            user_id,
                            PromptCreate(title=title, system_prompt=system, user_prompt=user, category=new_category),
                        )
                        st.success("Prompt created!")
                        st.rerun()

    except Exception as exc:
        show_error(exc)
