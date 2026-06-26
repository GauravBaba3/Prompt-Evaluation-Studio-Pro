"""Text metrics tests."""

from utils.formatters import apply_variables, format_tags, parse_tags
from utils.text_metrics import compute_output_length, compute_readability_score, estimate_tokens


def test_estimate_tokens():
    assert estimate_tokens("Hello world this is a test") > 0
    assert estimate_tokens("") == 0


def test_readability_score():
    score = compute_readability_score("This is a simple sentence. It is easy to read.")
    assert 0 <= score <= 100


def test_apply_variables():
    result = apply_variables("Hello {{name}}!", {"name": "World"})
    assert result == "Hello World!"


def test_tags_formatting():
    tags = format_tags(["a", "b", "c"])
    assert parse_tags(tags) == ["a", "b", "c"]


def test_output_length():
    assert compute_output_length("abc") == 3
