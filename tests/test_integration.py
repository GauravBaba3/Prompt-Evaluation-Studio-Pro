"""Integration tests for services."""

from unittest.mock import MagicMock, patch

from backend.service_factory import get_services
from models.schemas import ComparisonPrompt, ComparisonRequest, ExperimentCreate, UserCreate
from services.gemini_service import GeminiService


def test_experiment_service():
    with get_services() as services:
        user = services.auth.register(
            UserCreate(username="expuser", email="exp@example.com", password="password123")
        )
        experiment = services.experiments.create(
            user.id,
            ExperimentCreate(
                title="Test Experiment",
                model_used="gemini-2.0-flash",
                user_prompt="Test",
                response_text="Response",
                execution_time_ms=100.0,
                success=True,
                status="completed",
            ),
        )
        assert experiment.id is not None
        listed = services.experiments.list_experiments(user.id)
        assert len(listed) >= 1
        assert services.experiments.get_success_rate(user.id) == 100.0


def test_analytics_dashboard():
    with get_services() as services:
        user = services.auth.register(
            UserCreate(username="analyticsuser", email="analytics@example.com", password="password123")
        )
        services.analytics.record_event(user.id, event_type="test", execution_time_ms=50.0, success=True)
        stats = services.analytics.get_dashboard_stats(user.id)
        assert stats.total_prompts == 0
        assert stats.total_experiments == 0


@patch.object(GeminiService, "generate")
def test_comparison_service(mock_generate):
    mock_generate.return_value = MagicMock(
        text="Sample response",
        execution_time_ms=120.0,
        token_usage=50,
        success=True,
    )

    with get_services() as services:
        from services.comparison_service import ComparisonService

        comparison = ComparisonService(GeminiService(api_key="test"))
        results = comparison.compare(
            ComparisonRequest(
                prompts=[
                    ComparisonPrompt(label="A", user_prompt="Prompt A"),
                    ComparisonPrompt(label="B", user_prompt="Prompt B"),
                ]
            )
        )
        assert len(results) == 2
        assert sum(1 for r in results if r.is_winner) == 1


def test_export_service():
    with get_services() as services:
        data = [{"title": "Test", "value": 1}]
        json_path = services.export.export_json(data, "test")
        assert json_path.exists()
        csv_path = services.export.export_csv(data, "test")
        assert csv_path.exists()
