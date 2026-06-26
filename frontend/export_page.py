"""Export page."""

from __future__ import annotations

import streamlit as st

from backend.service_factory import get_services
from frontend.components import show_error
from frontend.session import get_user_id
from frontend.theme import page_header


def render_export() -> None:
    page_header("Export Center", "Export reports in PDF, CSV, Markdown, JSON, and HTML")
    user_id = get_user_id()
    if not user_id:
        return

    export_type = st.selectbox(
        "Export Type",
        ["Experiment History", "Analytics Summary", "Comparison Results", "Evaluation Report", "Custom Markdown"],
    )

    try:
        with get_services() as services:
            if export_type == "Experiment History":
                format_choice = st.multiselect("Formats", ["JSON", "CSV", "Markdown", "HTML", "PDF"], default=["JSON"])
                if st.button("Export Experiments"):
                    data = services.experiments.export_history(user_id)
                    paths = []
                    if "JSON" in format_choice:
                        paths.append(str(services.export.export_json(data, "experiments")))
                    if "CSV" in format_choice:
                        paths.append(str(services.export.export_csv(data, "experiments")))
                    if "Markdown" in format_choice:
                        md = services.export.build_experiment_markdown(data)
                        paths.append(str(services.export.export_markdown(md, "experiments")))
                    if "HTML" in format_choice:
                        body = services.export.build_experiment_markdown(data).replace("\n", "<br>")
                        paths.append(str(services.export.export_html("Experiment History", body, "experiments")))
                    if "PDF" in format_choice:
                        sections = [(item.get("title", "Experiment"), item.get("response_text", "")) for item in data[:10]]
                        paths.append(str(services.export.export_pdf_report("Experiment History", sections, "experiments")))
                    st.success("Exported files:\n" + "\n".join(paths))

            elif export_type == "Analytics Summary":
                if st.button("Export Analytics"):
                    data = services.analytics.export_analytics(user_id)
                    json_path = services.export.export_json(data, "analytics")
                    html_body = "<br>".join(f"<b>{k}:</b> {v}" for k, v in data.items())
                    html_path = services.export.export_html("Analytics Summary", html_body, "analytics")
                    st.success(f"JSON: {json_path}\nHTML: {html_path}")

            elif export_type == "Comparison Results":
                if not st.session_state.get("comparison_results"):
                    st.warning("Run a comparison first to export results.")
                elif st.button("Export Comparison"):
                    results = st.session_state.comparison_results
                    json_path = services.export.export_json(results, "comparison")
                    pdf_path = services.export.export_comparison_pdf(results, "comparison")
                    st.success(f"JSON: {json_path}\nPDF: {pdf_path}")

            elif export_type == "Evaluation Report":
                if not st.session_state.get("eval_result"):
                    st.warning("Run an evaluation first.")
                elif st.button("Export Evaluation"):
                    result = st.session_state.eval_result
                    data = result.model_dump()
                    json_path = services.export.export_json(data, "evaluation")
                    md = f"# Evaluation Report\n\n**Overall Score:** {result.scores.overall_score}\n\n{result.explanation}"
                    md_path = services.export.export_markdown(md, "evaluation")
                    st.success(f"JSON: {json_path}\nMarkdown: {md_path}")

            elif export_type == "Custom Markdown":
                custom_md = st.text_area("Markdown Content", height=300, value="# My Prompt Report\n\nContent here...")
                if st.button("Export Custom Markdown"):
                    path = services.export.export_markdown(custom_md, "custom")
                    st.success(f"Exported to {path}")

    except Exception as exc:
        show_error(exc)
