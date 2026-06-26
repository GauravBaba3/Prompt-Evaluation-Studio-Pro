"""Application settings loaded from environment variables and Streamlit Secrets."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Streamlit is optional (works locally and on Streamlit Cloud)
try:
    import streamlit as st
except ImportError:
    st = None

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load local .env if available
load_dotenv(PROJECT_ROOT / ".env")


def get_env(key: str, default: str = "") -> str:
    """
    Read configuration in this order:
    1. Environment variables (.env / OS)
    2. Streamlit Secrets
    3. Default value
    """

    value = os.getenv(key)

    if value not in (None, ""):
        return value

    if st is not None:
        try:
            value = st.secrets.get(key)
            if value not in (None, ""):
                return str(value)
        except Exception:
            pass

    return default


class Settings(BaseModel):
    """Central application configuration."""

    app_title: str = Field(default="Prompt Evaluation Studio Pro")
    llm_provider: str = Field(default="huggingface")

    gemini_api_key: str = Field(default="")
    gemini_model: str = Field(default="gemini-2.0-flash")

    hf_token: str = Field(default="")
    hf_model: str = Field(default="meta-llama/Llama-3.1-8B-Instruct:novita")

    database_url: str = Field(default=f"sqlite:///{PROJECT_ROOT / 'data' / 'prompt_studio.db'}")

    secret_key: str = Field(default="prompt-studio-dev-secret-change-in-production")

    log_level: str = Field(default="INFO")

    project_root: Path = Field(default=PROJECT_ROOT)
    data_dir: Path = Field(default=PROJECT_ROOT / "data")
    logs_dir: Path = Field(default=PROJECT_ROOT / "logs")
    exports_dir: Path = Field(default=PROJECT_ROOT / "exports")
    backups_dir: Path = Field(default=PROJECT_ROOT / "backups")

    model_config = {"arbitrary_types_allowed": True}

    def ensure_directories(self) -> None:
        for directory in (
            self.data_dir,
            self.logs_dir,
            self.exports_dir,
            self.backups_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""

    settings = Settings(
        app_title=get_env("APP_TITLE", "Prompt Evaluation Studio Pro"),

        llm_provider=get_env("LLM_PROVIDER", "huggingface").lower(),

        gemini_api_key=get_env("GEMINI_API_KEY", ""),
        gemini_model=get_env("GEMINI_MODEL", "gemini-2.0-flash"),

        hf_token=get_env("HF_TOKEN", ""),
        hf_model=get_env(
            "HF_MODEL",
            "meta-llama/Llama-3.1-8B-Instruct:novita",
        ),

        database_url=get_env(
            "DATABASE_URL",
            f"sqlite:///{PROJECT_ROOT / 'data' / 'prompt_studio.db'}",
        ),

        secret_key=get_env(
            "SECRET_KEY",
            "prompt-studio-dev-secret-change-in-production",
        ),

        log_level=get_env("LOG_LEVEL", "INFO"),
    )

    settings.ensure_directories()

    return settings
```
