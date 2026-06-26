"""Backend helpers and service factory."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from database.connection import get_session
from services.analytics_service import AnalyticsService
from services.auth_service import AuthService
from services.comparison_service import ComparisonService
from services.evaluation_service import EvaluationService
from services.experiment_service import ExperimentService
from services.export_service import ExportService
from services.gemini_service import GeminiService
from services.huggingface_service import HuggingFaceService
from services.optimizer_service import OptimizerService
from services.prompt_service import PromptService
from services.settings_service import SettingsService


class ServiceContainer:
    """Lazy service container bound to a database session."""

    def __init__(self, session) -> None:
        self.session = session
        self._llm: GeminiService | HuggingFaceService | None = None

    @property
    def auth(self) -> AuthService:
        return AuthService(self.session)

    @property
    def prompts(self) -> PromptService:
        return PromptService(self.session)

    @property
    def experiments(self) -> ExperimentService:
        return ExperimentService(self.session)

    @property
    def analytics(self) -> AnalyticsService:
        return AnalyticsService(self.session)

    @property
    def settings(self) -> SettingsService:
        return SettingsService(self.session)

    @property
    def export(self) -> ExportService:
        return ExportService()

    def _create_llm_service(self) -> GeminiService | HuggingFaceService:
        settings_service = self.settings
        if settings_service.get_llm_provider() == "gemini":
            return GeminiService(
                api_key=settings_service.get_gemini_api_key(),
                model=settings_service.get_gemini_model(),
            )
        return HuggingFaceService(
            api_token=settings_service.get_hf_token(),
            model=settings_service.get_hf_model(),
        )

    @property
    def llm(self) -> GeminiService | HuggingFaceService:
        if self._llm is None:
            self._llm = self._create_llm_service()
        return self._llm

    @property
    def gemini(self) -> GeminiService | HuggingFaceService:
        return self.llm

    @property
    def evaluation(self) -> EvaluationService:
        return EvaluationService(self.session, self.gemini)

    @property
    def optimizer(self) -> OptimizerService:
        return OptimizerService(self.gemini)

    @property
    def comparison(self) -> ComparisonService:
        return ComparisonService(self.gemini)


@contextmanager
def get_services() -> Generator[ServiceContainer, None, None]:
    with get_session() as session:
        yield ServiceContainer(session)
