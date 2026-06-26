"""Formatting utilities."""

from __future__ import annotations

import html
import re

import markdown


def format_tags(tags: list[str]) -> str:
    cleaned = [tag.strip() for tag in tags if tag.strip()]
    return ",".join(cleaned)


def parse_tags(tags: str) -> list[str]:
    if not tags:
        return []
    return [tag.strip() for tag in tags.split(",") if tag.strip()]


def render_markdown_safe(text: str) -> str:
    rendered = markdown.markdown(text or "", extensions=["fenced_code", "tables", "nl2br"])
    return html.unescape(rendered)


def apply_variables(template: str, variables: dict[str, str]) -> str:
    result = template
    for key, value in variables.items():
        result = result.replace(f"{{{{{key}}}}}", value)
        result = result.replace(f"{{{key}}}", value)
    return result


def diff_text(old_text: str, new_text: str) -> list[tuple[str, str]]:
    """Return line-level diff tuples (status, line)."""
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()
    diff: list[tuple[str, str]] = []
    max_len = max(len(old_lines), len(new_lines))
    for index in range(max_len):
        old_line = old_lines[index] if index < len(old_lines) else None
        new_line = new_lines[index] if index < len(new_lines) else None
        if old_line == new_line:
            if old_line is not None:
                diff.append(("same", old_line))
        elif old_line is None:
            diff.append(("added", new_line or ""))
        elif new_line is None:
            diff.append(("removed", old_line))
        else:
            diff.append(("removed", old_line))
            diff.append(("added", new_line))
    return diff


def highlight_variables(text: str) -> list[str]:
    return re.findall(r"\{\{?\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}?\}", text)
