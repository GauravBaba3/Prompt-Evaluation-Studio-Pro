"""Analytics and dashboard service."""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from database.models import AnalyticsRecord, Evaluation, Experiment, Prompt
from models.schemas import AnalyticsSummary, DashboardStats, ExperimentOut
from services.experiment_service import ExperimentService
from utils.logger import get_logger

logger = get_logger(__name__)


class AnalyticsService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.experiment_service = ExperimentService(session)

    def record_event(
        self,
        user_id: int,
        event_type: str,
        category: str = "General",
        model_used: str = "",
        execution_time_ms: float = 0.0,
        score: float = 0.0,
        token_usage: int = 0,
        success: bool = True,
        metadata: dict | None = None,
    ) -> None:
        record = AnalyticsRecord(
            user_id=user_id,
            event_type=event_type,
            category=category,
            model_used=model_used,
            execution_time_ms=execution_time_ms,
            score=score,
            token_usage=token_usage,
            success=success,
            metadata_json=json.dumps(metadata or {}),
        )
        self.session.add(record)
        self.session.flush()

    def get_dashboard_stats(self, user_id: int) -> DashboardStats:
        total_prompts = self.session.query(Prompt).filter(Prompt.user_id == user_id).count()
        total_experiments = self.session.query(Experiment).filter(Experiment.user_id == user_id).count()
        avg_response_time = self.experiment_service.get_average_execution_time(user_id)
        success_rate = self.experiment_service.get_success_rate(user_id)

        prompts = self.session.query(Prompt).filter(Prompt.user_id == user_id).all()
        categories: dict[str, int] = defaultdict(int)
        for prompt in prompts:
            categories[prompt.category] += 1

        recent = self.experiment_service.list_experiments(user_id, limit=5)
        return DashboardStats(
            total_prompts=total_prompts,
            total_experiments=total_experiments,
            avg_response_time_ms=avg_response_time,
            success_rate=success_rate,
            categories=dict(categories),
            recent_experiments=recent,
        )

    def get_analytics_summary(self, user_id: int) -> AnalyticsSummary:
        records = (
            self.session.query(AnalyticsRecord)
            .filter(AnalyticsRecord.user_id == user_id)
            .order_by(AnalyticsRecord.created_at.desc())
            .all()
        )
        experiments = self.session.query(Experiment).filter(Experiment.user_id == user_id).all()
        evaluations = self.session.query(Evaluation).filter(Evaluation.user_id == user_id).all()
        prompts = self.session.query(Prompt).filter(Prompt.user_id == user_id).all()

        daily_usage: dict[str, int] = defaultdict(int)
        category_distribution: dict[str, int] = defaultdict(int)
        execution_trends: dict[str, float] = defaultdict(float)
        execution_counts: dict[str, int] = defaultdict(int)
        response_times: dict[str, list[float]] = defaultdict(list)
        average_scores: dict[str, list[float]] = defaultdict(list)

        for record in records:
            day = record.created_at.strftime("%Y-%m-%d") if record.created_at else "unknown"
            daily_usage[day] += 1
            category_distribution[record.category] += 1
            if record.execution_time_ms > 0:
                execution_trends[day] += record.execution_time_ms
                execution_counts[day] += 1
                response_times[record.model_used or "unknown"].append(record.execution_time_ms)
            if record.score > 0:
                average_scores[record.event_type].append(record.score)

        for experiment in experiments:
            day = experiment.created_at.strftime("%Y-%m-%d") if experiment.created_at else "unknown"
            daily_usage[day] += 1
            if experiment.execution_time_ms > 0:
                response_times[experiment.model_used].append(experiment.execution_time_ms)

        for prompt in prompts:
            category_distribution[prompt.category] += prompt.usage_count

        best_prompt = "N/A"
        worst_prompt = "N/A"
        if prompts:
            sorted_prompts = sorted(prompts, key=lambda p: p.success_rate, reverse=True)
            best_prompt = sorted_prompts[0].title
            worst_prompt = sorted_prompts[-1].title if len(sorted_prompts) > 1 else sorted_prompts[0].title

        for evaluation in evaluations:
            average_scores["evaluation"].append(evaluation.overall_score)

        top_categories = sorted(category_distribution.items(), key=lambda x: x[1], reverse=True)[:5]

        return AnalyticsSummary(
            daily_usage=dict(daily_usage),
            category_distribution=dict(category_distribution),
            execution_trends={
                day: round(execution_trends[day] / max(execution_counts[day], 1), 2)
                for day in execution_trends
            },
            response_times={
                model: round(sum(times) / len(times), 2) for model, times in response_times.items() if times
            },
            average_scores={
                key: round(sum(values) / len(values), 2) for key, values in average_scores.items() if values
            },
            best_prompt=best_prompt,
            worst_prompt=worst_prompt,
            top_categories=top_categories,
        )

    def export_analytics(self, user_id: int) -> dict:
        summary = self.get_analytics_summary(user_id)
        return summary.model_dump()
