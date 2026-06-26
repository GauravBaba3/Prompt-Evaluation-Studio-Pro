"""Hugging Face service tests with mocking."""

from unittest.mock import MagicMock, patch

import pytest

from models.schemas import GenerationConfig, PromptRunResponse
from services.huggingface_service import HuggingFaceService
from utils.exceptions import GeminiAPIError


def test_empty_prompt_raises():
    service = HuggingFaceService(api_token="test-token")
    with pytest.raises(GeminiAPIError) as exc:
        service.generate("", "   ")
    assert exc.value.code == "EMPTY_PROMPT"


def test_missing_token_raises():
    service = HuggingFaceService(api_token="")
    with pytest.raises(GeminiAPIError) as exc:
        _ = service.client
    assert exc.value.code == "INVALID_API_KEY"


@patch("services.huggingface_service.httpx.Client")
def test_generate_success(mock_client_class):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Hello World"}}],
    }
    mock_client_class.return_value.post.return_value = mock_response

    service = HuggingFaceService(api_token="test-token")
    result = service.generate("System", "User prompt", config=GenerationConfig())

    assert isinstance(result, PromptRunResponse)
    assert result.text == "Hello World"
    assert result.success is True
    assert result.execution_time_ms >= 0


@patch("services.huggingface_service.httpx.Client")
def test_generate_json(mock_client_class):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": '{"quality_score": 85}'}}],
    }
    mock_client_class.return_value.post.return_value = mock_response

    service = HuggingFaceService(api_token="test-token")
    result = service.generate_json("System", "Score this")
    assert result["quality_score"] == 85
