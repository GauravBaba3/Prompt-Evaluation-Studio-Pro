"""Application-wide constants."""

from __future__ import annotations

DEFAULT_CATEGORIES: list[str] = [
    "General",
    "Coding",
    "Creative Writing",
    "Data Analysis",
    "Customer Support",
    "Marketing",
    "Research",
    "Education",
    "Summarization",
    "Translation",
]

DEFAULT_TAGS: list[str] = [
    "production",
    "draft",
    "experimental",
    "optimized",
    "template",
    "favorite",
]

EXPERIMENT_STATUSES: list[str] = [
    "draft",
    "running",
    "completed",
    "failed",
    "archived",
]

GEMINI_MODELS: list[str] = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]

HF_MODELS: list[str] = [
    "meta-llama/Llama-3.1-8B-Instruct:novita",
    "meta-llama/Llama-3.1-70B-Instruct:novita",
    "meta-llama/Meta-Llama-3-8B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct:novita",
    "mistralai/Mistral-7B-Instruct-v0.3:novita",
]

SAFETY_LEVELS: list[str] = ["BLOCK_NONE", "BLOCK_ONLY_HIGH", "BLOCK_MEDIUM_AND_ABOVE", "BLOCK_LOW_AND_ABOVE"]

EVALUATION_CRITERIA: list[str] = [
    "accuracy",
    "completeness",
    "hallucination_risk",
    "grammar",
    "structure",
    "professionalism",
    "formatting",
    "readability",
    "prompt_effectiveness",
]

MAX_COMPARISON_PROMPTS: int = 5
MIN_COMPARISON_PROMPTS: int = 2
DEFAULT_MAX_TOKENS: int = 2048
DEFAULT_TEMPERATURE: float = 0.7
DEFAULT_TOP_P: float = 0.95
DEFAULT_TOP_K: int = 40
