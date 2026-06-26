"""Prompt CRUD and version control service."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from database.models import Prompt, PromptVersion
from models.schemas import PromptCreate, PromptOut, PromptUpdate, PromptVersionOut
from utils.exceptions import DatabaseError, ValidationError
from utils.formatters import diff_text, format_tags, parse_tags
from utils.logger import get_logger

logger = get_logger(__name__)


class PromptService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, user_id: int, data: PromptCreate) -> PromptOut:
        if not data.user_prompt.strip():
            raise ValidationError("User prompt cannot be empty.")
        prompt = Prompt(
            user_id=user_id,
            title=data.title.strip(),
            description=data.description,
            system_prompt=data.system_prompt,
            user_prompt=data.user_prompt,
            category=data.category,
            tags=format_tags(data.tags),
            is_template=data.is_template,
            is_favorite=data.is_favorite,
            is_pinned=data.is_pinned,
            current_version=1,
        )
        self.session.add(prompt)
        self.session.flush()
        version = PromptVersion(
            prompt_id=prompt.id,
            version_number=1,
            system_prompt=prompt.system_prompt,
            user_prompt=prompt.user_prompt,
            change_note="Initial version",
            tags=prompt.tags,
        )
        self.session.add(version)
        self.session.flush()
        logger.info("Created prompt %s for user %s", prompt.id, user_id)
        return PromptOut.model_validate(prompt)

    def get_by_id(self, user_id: int, prompt_id: int) -> PromptOut | None:
        prompt = (
            self.session.query(Prompt)
            .filter(Prompt.id == prompt_id, Prompt.user_id == user_id)
            .first()
        )
        return PromptOut.model_validate(prompt) if prompt else None

    def list_prompts(
        self,
        user_id: int,
        search: str = "",
        category: str | None = None,
        templates_only: bool = False,
        favorites_only: bool = False,
        pinned_only: bool = False,
        sort_by: str = "updated_at",
        ascending: bool = False,
    ) -> list[PromptOut]:
        query = self.session.query(Prompt).filter(Prompt.user_id == user_id)
        if search:
            pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Prompt.title.ilike(pattern),
                    Prompt.description.ilike(pattern),
                    Prompt.user_prompt.ilike(pattern),
                    Prompt.tags.ilike(pattern),
                )
            )
        if category and category != "All":
            query = query.filter(Prompt.category == category)
        if templates_only:
            query = query.filter(Prompt.is_template.is_(True))
        if favorites_only:
            query = query.filter(Prompt.is_favorite.is_(True))
        if pinned_only:
            query = query.filter(Prompt.is_pinned.is_(True))

        sort_column = {
            "title": Prompt.title,
            "created_at": Prompt.created_at,
            "usage_count": Prompt.usage_count,
            "success_rate": Prompt.success_rate,
            "last_used_at": Prompt.last_used_at,
        }.get(sort_by, Prompt.updated_at)
        query = query.order_by(sort_column.asc() if ascending else desc(sort_column))
        return [PromptOut.model_validate(p) for p in query.all()]

    def update(self, user_id: int, prompt_id: int, data: PromptUpdate) -> PromptOut:
        prompt = (
            self.session.query(Prompt)
            .filter(Prompt.id == prompt_id, Prompt.user_id == user_id)
            .first()
        )
        if not prompt:
            raise DatabaseError("Prompt not found.")
        updates = data.model_dump(exclude_unset=True)
        if "tags" in updates and updates["tags"] is not None:
            updates["tags"] = format_tags(updates["tags"])
        for key, value in updates.items():
            setattr(prompt, key, value)
        prompt.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return PromptOut.model_validate(prompt)

    def create_version(self, user_id: int, prompt_id: int, change_note: str = "") -> PromptVersionOut:
        prompt = (
            self.session.query(Prompt)
            .filter(Prompt.id == prompt_id, Prompt.user_id == user_id)
            .first()
        )
        if not prompt:
            raise DatabaseError("Prompt not found.")
        new_version_number = prompt.current_version + 1
        version = PromptVersion(
            prompt_id=prompt.id,
            version_number=new_version_number,
            system_prompt=prompt.system_prompt,
            user_prompt=prompt.user_prompt,
            change_note=change_note or f"Version {new_version_number}",
            tags=prompt.tags,
        )
        prompt.current_version = new_version_number
        prompt.updated_at = datetime.now(timezone.utc)
        self.session.add(version)
        self.session.flush()
        return PromptVersionOut.model_validate(version)

    def duplicate(self, user_id: int, prompt_id: int) -> PromptOut:
        original = (
            self.session.query(Prompt)
            .filter(Prompt.id == prompt_id, Prompt.user_id == user_id)
            .first()
        )
        if not original:
            raise DatabaseError("Prompt not found.")
        duplicate_data = PromptCreate(
            title=f"{original.title} (Copy)",
            description=original.description,
            system_prompt=original.system_prompt,
            user_prompt=original.user_prompt,
            category=original.category,
            tags=parse_tags(original.tags),
            is_template=original.is_template,
            is_favorite=False,
            is_pinned=False,
        )
        return self.create(user_id, duplicate_data)

    def restore_version(self, user_id: int, prompt_id: int, version_id: int) -> PromptOut:
        prompt = (
            self.session.query(Prompt)
            .filter(Prompt.id == prompt_id, Prompt.user_id == user_id)
            .first()
        )
        version = (
            self.session.query(PromptVersion)
            .filter(PromptVersion.id == version_id, PromptVersion.prompt_id == prompt_id)
            .first()
        )
        if not prompt or not version:
            raise DatabaseError("Prompt or version not found.")
        prompt.system_prompt = version.system_prompt
        prompt.user_prompt = version.user_prompt
        prompt.tags = version.tags
        prompt.updated_at = datetime.now(timezone.utc)
        self.create_version(user_id, prompt_id, f"Restored from version {version.version_number}")
        self.session.flush()
        return PromptOut.model_validate(prompt)

    def list_versions(self, user_id: int, prompt_id: int) -> list[PromptVersionOut]:
        prompt = (
            self.session.query(Prompt)
            .filter(Prompt.id == prompt_id, Prompt.user_id == user_id)
            .first()
        )
        if not prompt:
            raise DatabaseError("Prompt not found.")
        versions = (
            self.session.query(PromptVersion)
            .filter(PromptVersion.prompt_id == prompt_id)
            .order_by(desc(PromptVersion.version_number))
            .all()
        )
        return [PromptVersionOut.model_validate(v) for v in versions]

    def get_version_diff(self, user_id: int, prompt_id: int, version_id: int) -> list[tuple[str, str]]:
        versions = self.list_versions(user_id, prompt_id)
        target = next((v for v in versions if v.id == version_id), None)
        current = self.get_by_id(user_id, prompt_id)
        if not target or not current:
            raise DatabaseError("Version not found.")
        return diff_text(target.user_prompt, current.user_prompt)

    def record_usage(self, user_id: int, prompt_id: int, success: bool) -> None:
        prompt = (
            self.session.query(Prompt)
            .filter(Prompt.id == prompt_id, Prompt.user_id == user_id)
            .first()
        )
        if not prompt:
            return
        prompt.usage_count += 1
        prompt.last_used_at = datetime.now(timezone.utc)
        total = prompt.usage_count
        previous_successes = int(prompt.success_rate * (total - 1) / 100) if total > 1 else 0
        new_successes = previous_successes + (1 if success else 0)
        prompt.success_rate = round((new_successes / total) * 100, 2)
        self.session.flush()

    def delete(self, user_id: int, prompt_id: int) -> None:
        prompt = (
            self.session.query(Prompt)
            .filter(Prompt.id == prompt_id, Prompt.user_id == user_id)
            .first()
        )
        if not prompt:
            raise DatabaseError("Prompt not found.")
        self.session.delete(prompt)
        self.session.flush()

    def seed_templates(self, user_id: int) -> int:
        from prompts.templates import PROMPT_TEMPLATES

        count = 0
        for template in PROMPT_TEMPLATES:
            existing = (
                self.session.query(Prompt)
                .filter(Prompt.user_id == user_id, Prompt.title == template["title"], Prompt.is_template.is_(True))
                .first()
            )
            if existing:
                continue
            self.create(
                user_id,
                PromptCreate(
                    title=template["title"],
                    description=f"Built-in template: {template['title']}",
                    system_prompt=template["system_prompt"],
                    user_prompt=template["user_prompt"],
                    category=template["category"],
                    tags=template["tags"],
                    is_template=True,
                ),
            )
            count += 1
        return count
