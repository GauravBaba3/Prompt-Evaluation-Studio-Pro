"""Gemini service tests with mocking."""

from unittest.mock import MagicMock, patch

import pytest

from models.schemas import GenerationConfig, PromptRunResponse
from services.gemini_service import GeminiService
from utils.exceptions import GeminiAPIError


class MockResponse:
    def __init__(self, text: str):
        self.text = text


def test_empty_prompt_raises():
    service = GeminiService(api_key="test-key")
    with pytest.raises(GeminiAPIError) as exc:
        service.generate("", "   ")
    assert exc.value.code == "EMPTY_PROMPT"


def test_missing_api_key_raises():
    service = GeminiService(api_key="")
    with pytest.raises(GeminiAPIError) as exc:
        _ = service.client
    assert exc.value.code == "INVALID_API_KEY"


@patch("services.gemini_service.genai.Client")
def test_generate_success(mock_client_class):
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = MockResponse("Hello World")
    mock_client_class.return_value = mock_client

    service = GeminiService(api_key="test-key")
    result = service.generate("System", "User prompt", config=GenerationConfig())

    assert isinstance(result, PromptRunResponse)
    assert result.text == "Hello World"
    assert result.success is True
    assert result.execution_time_ms >= 0


@patch("services.gemini_service.genai.Client")
def test_generate_json(mock_client_class):
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = MockResponse('{"quality_score": 85}')
    mock_client_class.return_value = mock_client

    service = GeminiService(api_key="test-key")
    result = service.generate_json("System", "Score this")
    assert result["quality_score"] == 85
