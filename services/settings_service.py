"""Application settings and backup service."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from config.settings import get_settings
from database.connection import drop_all_tables, init_db
from database.models import AppSetting
from utils.logger import get_logger

logger = get_logger(__name__)


class SettingsService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.settings = get_settings()

    def get_setting(self, key: str, default: str = "") -> str:
        record = self.session.query(AppSetting).filter(AppSetting.key == key).first()
        return record.value if record else default

    def set_setting(self, key: str, value: str) -> None:
        record = self.session.query(AppSetting).filter(AppSetting.key == key).first()
        if record:
            record.value = value
            record.updated_at = datetime.now(timezone.utc)
        else:
            record = AppSetting(key=key, value=value)
            self.session.add(record)
        self.session.flush()
        logger.info("Setting updated: %s", key)

    def get_all_settings(self) -> dict[str, str]:
        records = self.session.query(AppSetting).all()
        return {record.key: record.value for record in records}

    def get_gemini_api_key(self) -> str:
        db_key = self.get_setting("gemini_api_key")
        return db_key or self.settings.gemini_api_key

    def get_gemini_model(self) -> str:
        return self.get_setting("gemini_model", self.settings.gemini_model)

    def get_llm_provider(self) -> str:
        return self.get_setting("llm_provider", self.settings.llm_provider).lower()

    def get_hf_token(self) -> str:
        db_token = self.get_setting("hf_token")
        return db_token or self.settings.hf_token

    def get_hf_model(self) -> str:
        return self.get_setting("hf_model", self.settings.hf_model)

    def save_gemini_config(self, api_key: str, model: str) -> None:
        self.set_setting("gemini_api_key", api_key.strip())
        self.set_setting("gemini_model", model.strip())

    def save_hf_config(self, token: str, model: str) -> None:
        self.set_setting("hf_token", token.strip())
        self.set_setting("hf_model", model.strip())

    def backup_database(self) -> Path:
        self.settings.ensure_directories()
        db_path = self.settings.data_dir / "prompt_studio.db"
        if not db_path.exists():
            init_db()
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_path = self.settings.backups_dir / f"prompt_studio_backup_{timestamp}.db"
        shutil.copy2(db_path, backup_path)

        settings_backup = self.settings.backups_dir / f"settings_backup_{timestamp}.json"
        settings_backup.write_text(json.dumps(self.get_all_settings(), indent=2), encoding="utf-8")
        logger.info("Database backed up to %s", backup_path)
        return backup_path

    def restore_database(self, backup_file: Path) -> None:
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_file}")
        db_path = self.settings.data_dir / "prompt_studio.db"
        shutil.copy2(backup_file, db_path)
        logger.info("Database restored from %s", backup_file)

    def clear_database(self) -> None:
        drop_all_tables()
        init_db()
        logger.warning("Database cleared and reinitialized")

    def list_backups(self) -> list[Path]:
        return sorted(self.settings.backups_dir.glob("*.db"), reverse=True)
