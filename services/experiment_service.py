"""Experiment management service."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import desc
from sqlalchemy.orm import Session

from database.models import Experiment
from models.schemas import ExperimentCreate, ExperimentOut
from utils.exceptions import DatabaseError
from utils.logger import get_logger

logger = get_logger(__name__)


class ExperimentService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, user_id: int, data: ExperimentCreate) -> ExperimentOut:
        experiment = Experiment(
            user_id=user_id,
            prompt_id=data.prompt_id,
            title=data.title.strip(),
            notes=data.notes,
            status=data.status,
            model_used=data.model_used,
            input_variables=json.dumps(data.input_variables),
            system_prompt=data.system_prompt,
            user_prompt=data.user_prompt,
            response_text=data.response_text,
            temperature=data.temperature,
            top_p=data.top_p,
            top_k=data.top_k,
            max_tokens=data.max_tokens,
            execution_time_ms=data.execution_time_ms,
            token_usage=data.token_usage,
            success=data.success,
            error_message=data.error_message,
        )
        self.session.add(experiment)
        self.session.flush()
        logger.info("Created experiment %s for user %s", experiment.id, user_id)
        return ExperimentOut.model_validate(experiment)

    def get_by_id(self, user_id: int, experiment_id: int) -> ExperimentOut | None:
        experiment = (
            self.session.query(Experiment)
            .filter(Experiment.id == experiment_id, Experiment.user_id == user_id)
            .first()
        )
        return ExperimentOut.model_validate(experiment) if experiment else None

    def list_experiments(
        self,
        user_id: int,
        status: str | None = None,
        limit: int = 100,
    ) -> list[ExperimentOut]:
        query = self.session.query(Experiment).filter(Experiment.user_id == user_id)
        if status and status != "All":
            query = query.filter(Experiment.status == status)
        experiments = query.order_by(desc(Experiment.created_at)).limit(limit).all()
        return [ExperimentOut.model_validate(e) for e in experiments]

    def update_status(self, user_id: int, experiment_id: int, status: str) -> ExperimentOut:
        experiment = (
            self.session.query(Experiment)
            .filter(Experiment.id == experiment_id, Experiment.user_id == user_id)
            .first()
        )
        if not experiment:
            raise DatabaseError("Experiment not found.")
        experiment.status = status
        experiment.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return ExperimentOut.model_validate(experiment)

    def update_notes(self, user_id: int, experiment_id: int, notes: str) -> ExperimentOut:
        experiment = (
            self.session.query(Experiment)
            .filter(Experiment.id == experiment_id, Experiment.user_id == user_id)
            .first()
        )
        if not experiment:
            raise DatabaseError("Experiment not found.")
        experiment.notes = notes
        experiment.updated_at = datetime.now(timezone.utc)
        self.session.flush()
        return ExperimentOut.model_validate(experiment)

    def delete(self, user_id: int, experiment_id: int) -> None:
        experiment = (
            self.session.query(Experiment)
            .filter(Experiment.id == experiment_id, Experiment.user_id == user_id)
            .first()
        )
        if not experiment:
            raise DatabaseError("Experiment not found.")
        self.session.delete(experiment)
        self.session.flush()

    def export_history(self, user_id: int) -> list[dict]:
        experiments = self.list_experiments(user_id, limit=1000)
        return [e.model_dump(mode="json") for e in experiments]

    def get_success_rate(self, user_id: int) -> float:
        experiments = self.session.query(Experiment).filter(Experiment.user_id == user_id).all()
        if not experiments:
            return 0.0
        successes = sum(1 for e in experiments if e.success)
        return round((successes / len(experiments)) * 100, 2)

    def get_average_execution_time(self, user_id: int) -> float:
        experiments = (
            self.session.query(Experiment)
            .filter(Experiment.user_id == user_id, Experiment.success.is_(True))
            .all()
        )
        if not experiments:
            return 0.0
        return round(sum(e.execution_time_ms for e in experiments) / len(experiments), 2)
