"""Pydantic schemas for API and service layer."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    email: str = Field(min_length=5, max_length=120)
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    username: str
    password: str
    remember: bool = False


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    is_admin: bool
    theme: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class PromptCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    system_prompt: str = ""
    user_prompt: str = Field(min_length=1)
    category: str = "General"
    tags: list[str] = Field(default_factory=list)
    is_template: bool = False
    is_favorite: bool = False
    is_pinned: bool = False


class PromptUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    system_prompt: str | None = None
    user_prompt: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    is_template: bool | None = None
    is_favorite: bool | None = None
    is_pinned: bool | None = None


class PromptOut(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    system_prompt: str
    user_prompt: str
    category: str
    tags: str
    is_template: bool
    is_favorite: bool
    is_pinned: bool
    current_version: int
    usage_count: int
    success_rate: float
    last_used_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class PromptVersionOut(BaseModel):
    id: int
    prompt_id: int
    version_number: int
    system_prompt: str
    user_prompt: str
    change_note: str
    tags: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class GenerationConfig(BaseModel):
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.95, ge=0.0, le=1.0)
    top_k: int = Field(default=40, ge=1, le=100)
    max_tokens: int = Field(default=2048, ge=1, le=8192)
    safety_level: str = "BLOCK_ONLY_HIGH"
    json_mode: bool = False
    stream: bool = False

    @field_validator("safety_level")
    @classmethod
    def validate_safety(cls, value: str) -> str:
        allowed = {"BLOCK_NONE", "BLOCK_ONLY_HIGH", "BLOCK_MEDIUM_AND_ABOVE", "BLOCK_LOW_AND_ABOVE"}
        if value not in allowed:
            raise ValueError(f"Invalid safety level: {value}")
        return value


class PromptRunRequest(BaseModel):
    system_prompt: str = ""
    user_prompt: str = Field(min_length=1)
    input_variables: dict[str, str] = Field(default_factory=dict)
    model: str = "meta-llama/Llama-3.1-8B-Instruct:novita"
    config: GenerationConfig = Field(default_factory=GenerationConfig)


class PromptRunResponse(BaseModel):
    text: str
    execution_time_ms: float
    token_usage: int
    model: str
    success: bool
    error_message: str = ""


class ComparisonPrompt(BaseModel):
    label: str
    system_prompt: str = ""
    user_prompt: str


class ComparisonRequest(BaseModel):
    prompts: list[ComparisonPrompt] = Field(min_length=2, max_length=5)
    input_variables: dict[str, str] = Field(default_factory=dict)
    model: str = "gemini-2.0-flash"
    config: GenerationConfig = Field(default_factory=GenerationConfig)


class ComparisonResult(BaseModel):
    label: str
    response_text: str
    execution_time_ms: float
    output_length: int
    token_usage: int
    quality_score: float
    consistency_score: float
    readability_score: float
    overall_score: float
    is_winner: bool = False


class EvaluationRequest(BaseModel):
    prompt_text: str = Field(min_length=1)
    response_text: str = Field(min_length=1)
    context: str = ""
    experiment_id: int | None = None


class EvaluationScores(BaseModel):
    accuracy: float
    completeness: float
    hallucination_risk: float
    grammar: float
    structure: float
    professionalism: float
    formatting: float
    readability: float
    prompt_effectiveness: float
    overall_score: float


class EvaluationResponse(BaseModel):
    scores: EvaluationScores
    explanation: str
    suggested_prompt: str
    optimized_prompt: str
    raw: dict[str, Any] = Field(default_factory=dict)


class OptimizerRequest(BaseModel):
    prompt_text: str = Field(min_length=1)
    system_prompt: str = ""
    goal: str = "Improve clarity, accuracy, and structure while reducing hallucinations."
    num_versions: int = Field(default=3, ge=1, le=5)


class OptimizedVersion(BaseModel):
    title: str
    optimized_prompt: str
    system_prompt: str
    improvements: list[str]


class OptimizerResponse(BaseModel):
    original_prompt: str
    versions: list[OptimizedVersion]
    summary: str


class ExperimentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    notes: str = ""
    prompt_id: int | None = None
    status: str = "draft"
    model_used: str = "gemini-2.0-flash"
    input_variables: dict[str, str] = Field(default_factory=dict)
    system_prompt: str = ""
    user_prompt: str = ""
    response_text: str = ""
    temperature: float = 0.7
    top_p: float = 0.95
    top_k: int = 40
    max_tokens: int = 2048
    execution_time_ms: float = 0.0
    token_usage: int = 0
    success: bool = False
    error_message: str = ""


class ExperimentOut(BaseModel):
    id: int
    user_id: int
    prompt_id: int | None
    title: str
    notes: str
    status: str
    model_used: str
    input_variables: str
    system_prompt: str
    user_prompt: str
    response_text: str
    temperature: float
    top_p: float
    top_k: int
    max_tokens: int
    execution_time_ms: float
    token_usage: int
    success: bool
    error_message: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class DashboardStats(BaseModel):
    total_prompts: int
    total_experiments: int
    avg_response_time_ms: float
    success_rate: float
    categories: dict[str, int]
    recent_experiments: list[ExperimentOut]


class AnalyticsSummary(BaseModel):
    daily_usage: dict[str, int]
    category_distribution: dict[str, int]
    execution_trends: dict[str, float]
    response_times: dict[str, float]
    average_scores: dict[str, float]
    best_prompt: str
    worst_prompt: str
    top_categories: list[tuple[str, int]]
