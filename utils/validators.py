"""Input validation helpers."""

from __future__ import annotations

import re


EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def validate_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.match(email.strip()))


def validate_prompt_not_empty(prompt: str) -> bool:
    return bool(prompt and prompt.strip())
