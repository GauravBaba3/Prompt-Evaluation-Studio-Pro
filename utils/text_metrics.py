"""Text metrics for scoring and analytics."""

from __future__ import annotations

import math
import re


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    words = len(re.findall(r"\w+", text))
    return max(1, int(words * 1.3))


def compute_output_length(text: str) -> int:
    return len(text or "")


def compute_readability_score(text: str) -> float:
    """Flesch Reading Ease inspired heuristic normalized to 0-100."""
    if not text or not text.strip():
        return 0.0
    sentences = max(1, len(re.findall(r"[.!?]+", text)))
    words = max(1, len(re.findall(r"\w+", text)))
    syllables = max(words, sum(max(1, len(re.findall(r"[aeiouyAEIOUY]+", word))) for word in re.findall(r"\w+", text)))
    score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
    normalized = min(100.0, max(0.0, score))
    if math.isnan(normalized):
        return 50.0
    return round(normalized, 2)


def compute_consistency_score(responses: list[str]) -> float:
    if len(responses) < 2:
        return 100.0
    token_sets = [set(re.findall(r"\w+", r.lower())) for r in responses]
    if not token_sets:
        return 0.0
    intersection = set.intersection(*token_sets)
    union = set.union(*token_sets)
    if not union:
        return 0.0
    jaccard = len(intersection) / len(union)
    return round(jaccard * 100, 2)
