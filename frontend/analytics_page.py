"""Analytics Dashboard page."""

from __future__ import annotations

import plotly.express as px
import streamlit as st

from backend.service_factory import get_services
from frontend.components import show_error
from frontend.session import get_user_id
from frontend.theme import page_header


def render_analytics() -> None:
    page_header("Analytics Dashboard", "Visualize usage trends and prompt performance")
    user_id = get_user_id()
    if not user_id:
        return

    try:
        with get_services() as services:
            summary = services.analytics.get_analytics_summary(user_id)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Best Prompt", summary.best_prompt)
            with col2:
                st.metric("Needs Improvement", summary.worst_prompt)

            if summary.daily_usage:
                st.subheader("📈 Daily Usage")
                fig = px.bar(
                    x=list(summary.daily_usage.keys()),
                    y=list(summary.daily_usage.values()),
                    labels={"x": "Date", "y": "Events"},
                    title="Daily Activity",
                )
                fig.update_layout(template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

            col_a, col_b = st.columns(2)
            with col_a:
                if summary.category_distribution:
                    st.subheader("📂 Prompt Categories")
                    fig_cat = px.pie(
                        names=list(summary.category_distribution.keys()),
                        values=list(summary.category_distribution.values()),
                        title="Category Distribution",
                    )
                    fig_cat.update_layout(template="plotly_dark")
                    st.plotly_chart(fig_cat, use_container_width=True)

            with col_b:
                if summary.response_times:
                    st.subheader("⏱️ Response Times by Model")
                    fig_time = px.bar(
                        x=list(summary.response_times.keys()),
                        y=list(summary.response_times.values()),
                        labels={"x": "Model", "y": "Avg Time (ms)"},
                    )
                    fig_time.update_layout(template="plotly_dark")
                    st.plotly_chart(fig_time, use_container_width=True)

            if summary.execution_trends:
                st.subheader("📊 Execution Trends")
                fig_trend = px.line(
                    x=list(summary.execution_trends.keys()),
                    y=list(summary.execution_trends.values()),
                    labels={"x": "Date", "y": "Avg Execution Time (ms)"},
                )
                fig_trend.update_layout(template="plotly_dark")
                st.plotly_chart(fig_trend, use_container_width=True)

            if summary.average_scores:
                st.subheader("🎯 Average Scores")
                st.bar_chart(summary.average_scores)

            if summary.top_categories:
                st.subheader("🏆 Top Categories")
                for category, count in summary.top_categories:
                    st.markdown(f"- **{category}**: {count} events")

            if st.button("📤 Export Analytics (JSON)"):
                data = services.analytics.export_analytics(user_id)
                path = services.export.export_json(data, "analytics")
                st.success(f"Analytics exported to {path}")

    except Exception as exc:
        show_error(exc)
