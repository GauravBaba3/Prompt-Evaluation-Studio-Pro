"""Pytest configuration."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def test_env(tmp_path, monkeypatch):
    """Use isolated database for each test."""
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("HF_TOKEN", "test-token")
    monkeypatch.setenv("LLM_PROVIDER", "huggingface")
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    from config.settings import get_settings

    get_settings.cache_clear()
    from database.connection import get_engine, init_db

    global _engine, _SessionLocal
    import database.connection as conn

    conn._engine = None
    conn._SessionLocal = None
    init_db()
    yield
    get_settings.cache_clear()
