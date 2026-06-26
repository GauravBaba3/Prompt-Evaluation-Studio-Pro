"""SQLAlchemy ORM models."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, relationship


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    theme = Column(String(20), default="light")
    remember_token = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utcnow)
    last_login = Column(DateTime, nullable=True)

    prompts = relationship("Prompt", back_populates="owner", cascade="all, delete-orphan")
    experiments = relationship("Experiment", back_populates="owner", cascade="all, delete-orphan")
    evaluations = relationship("Evaluation", back_populates="owner", cascade="all, delete-orphan")
    analytics = relationship("AnalyticsRecord", back_populates="owner", cascade="all, delete-orphan")


class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    system_prompt = Column(Text, default="")
    user_prompt = Column(Text, nullable=False)
    category = Column(String(80), default="General")
    tags = Column(Text, default="")
    is_template = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)
    current_version = Column(Integer, default=1)
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    last_used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    owner = relationship("User", back_populates="prompts")
    versions = relationship("PromptVersion", back_populates="prompt", cascade="all, delete-orphan")
    experiments = relationship("Experiment", back_populates="prompt", cascade="all, delete-orphan")


class PromptVersion(Base):
    __tablename__ = "prompt_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    system_prompt = Column(Text, default="")
    user_prompt = Column(Text, nullable=False)
    change_note = Column(Text, default="")
    tags = Column(Text, default="")
    created_at = Column(DateTime, default=utcnow)

    prompt = relationship("Prompt", back_populates="versions")


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=True, index=True)
    title = Column(String(200), nullable=False)
    notes = Column(Text, default="")
    status = Column(String(30), default="draft")
    model_used = Column(String(80), default="gemini-2.0-flash")
    input_variables = Column(Text, default="{}")
    system_prompt = Column(Text, default="")
    user_prompt = Column(Text, default="")
    response_text = Column(Text, default="")
    temperature = Column(Float, default=0.7)
    top_p = Column(Float, default=0.95)
    top_k = Column(Integer, default=40)
    max_tokens = Column(Integer, default=2048)
    execution_time_ms = Column(Float, default=0.0)
    token_usage = Column(Integer, default=0)
    success = Column(Boolean, default=False)
    error_message = Column(Text, default="")
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    owner = relationship("User", back_populates="experiments")
    prompt = relationship("Prompt", back_populates="experiments")
    evaluations = relationship("Evaluation", back_populates="experiment", cascade="all, delete-orphan")


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=True, index=True)
    prompt_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)
    overall_score = Column(Float, default=0.0)
    accuracy = Column(Float, default=0.0)
    completeness = Column(Float, default=0.0)
    hallucination_risk = Column(Float, default=0.0)
    grammar = Column(Float, default=0.0)
    structure = Column(Float, default=0.0)
    professionalism = Column(Float, default=0.0)
    formatting = Column(Float, default=0.0)
    readability = Column(Float, default=0.0)
    prompt_effectiveness = Column(Float, default=0.0)
    explanation = Column(Text, default="")
    suggested_prompt = Column(Text, default="")
    optimized_prompt = Column(Text, default="")
    raw_json = Column(Text, default="")
    created_at = Column(DateTime, default=utcnow)

    owner = relationship("User", back_populates="evaluations")
    experiment = relationship("Experiment", back_populates="evaluations")


class AnalyticsRecord(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    event_type = Column(String(80), nullable=False, index=True)
    category = Column(String(80), default="General")
    model_used = Column(String(80), default="")
    execution_time_ms = Column(Float, default=0.0)
    score = Column(Float, default=0.0)
    token_usage = Column(Integer, default=0)
    success = Column(Boolean, default=True)
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=utcnow, index=True)

    owner = relationship("User", back_populates="analytics")


class AppSetting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, default="")
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
