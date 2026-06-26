#!/usr/bin/env python3
"""Generate PDF documents from markdown sources."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from config.settings import get_settings


def markdown_to_pdf(md_path: Path, pdf_path: Path, title: str) -> None:
    settings = get_settings()
    settings.ensure_directories()
    content = md_path.read_text(encoding="utf-8")
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph(title, styles["Title"]), Spacer(1, 12)]
    for line in content.split("\n"):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 6))
            continue
        if line.startswith("# "):
            story.append(Paragraph(line[2:], styles["Heading1"]))
        elif line.startswith("## "):
            story.append(Paragraph(line[3:], styles["Heading2"]))
        elif line.startswith("### "):
            story.append(Paragraph(line[4:], styles["Heading3"]))
        else:
            safe = line.replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(safe, styles["Normal"]))
    doc.build(story)


def main() -> None:
    settings = get_settings()
    docs_dir = ROOT / "docs"
    pdf_dir = ROOT / "assets" / "pdfs"
    pdf_dir.mkdir(parents=True, exist_ok=True)

    sources = [
        ("portfolio_content.md", "Portfolio - Prompt Evaluation Studio Pro"),
        ("PROJECT_REPORT.md", "Project Report - Prompt Evaluation Studio Pro"),
        ("INTERVIEW_GUIDE.md", "Interview Guide - Prompt Evaluation Studio Pro"),
    ]

    for filename, title in sources:
        md_path = docs_dir / filename if (docs_dir / filename).exists() else ROOT / filename
        if not md_path.exists():
            md_path = docs_dir / filename.replace(".md", ".md")
        alt_paths = [ROOT / filename, docs_dir / filename, ROOT / "docs" / filename]
        source = next((p for p in alt_paths if p.exists()), None)
        if source:
            pdf_path = pdf_dir / filename.replace(".md", ".pdf")
            markdown_to_pdf(source, pdf_path, title)
            print(f"Generated: {pdf_path}")


if __name__ == "__main__":
    main()
