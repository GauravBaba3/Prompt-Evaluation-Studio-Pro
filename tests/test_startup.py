"""Application startup tests."""

import importlib
import sys
from pathlib import Path


def test_project_imports():
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    modules = [
        "app",
        "config.settings",
        "database.connection",
        "database.models",
        "services.gemini_service",
        "services.auth_service",
        "services.prompt_service",
        "services.evaluation_service",
        "services.optimizer_service",
        "services.comparison_service",
        "services.analytics_service",
        "services.export_service",
        "frontend.dashboard",
        "frontend.playground",
    ]
    for module in modules:
        importlib.import_module(module)


def test_database_init():
    from database.connection import init_db, get_engine

    init_db()
    engine = get_engine()
    assert engine is not None
