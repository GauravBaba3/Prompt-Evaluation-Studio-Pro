#!/usr/bin/env python3
"""Initialize the application database."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from database.connection import init_db
from utils.logger import get_logger

logger = get_logger(__name__)


def main() -> None:
    init_db()
    logger.info("Database initialized successfully.")


if __name__ == "__main__":
    main()
