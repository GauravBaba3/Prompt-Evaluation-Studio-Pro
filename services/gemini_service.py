"""Google Gemini API integration service."""

from __future__ import annotations

import json
import time
from typing import Any, Generator

from google import genai
from google.genai import types

from config.settings import get_settings
from models.schemas import GenerationConfig, PromptRunRequest, PromptRunResponse
from utils.exceptions import GeminiAPIError, JSONParseError, RateLimitError, TimeoutError
from utils.formatters import apply_variables
from utils.logger import get_logger
from utils.text_metrics import estimate_tokens

logger = get_logger(__name__)


class GeminiService:
    """Wrapper around google-genai SDK with error handling."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        settings = get_settings()
        self.api_key = settings.gemini_api_key if api_key is None else api_key
        self.default_model = model or settings.gemini_model
        self._client: genai.Client | None = None

    @property
    def client(self) -> genai.Client:
        if not self.api_key:
            raise GeminiAPIError(
                "Gemini API key is not configured. Set GEMINI_API_KEY in .env or Admin Settings.",
                code="INVALID_API_KEY",
            )
        if self._client is None:
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def _build_safety_settings(self, level: str) -> list[types.SafetySetting]:
        threshold_map = {
            "BLOCK_NONE": types.HarmBlockThreshold.BLOCK_NONE,
            "BLOCK_ONLY_HIGH": types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            "BLOCK_MEDIUM_AND_ABOVE": types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            "BLOCK_LOW_AND_ABOVE": types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        }
        threshold = threshold_map.get(level, types.HarmBlockThreshold.BLOCK_ONLY_HIGH)
        categories = [
            types.HarmCategory.HARM_CATEGORY_HARASSMENT,
            types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        ]
        return [types.SafetySetting(category=cat, threshold=threshold) for cat in categories]

    def _build_config(self, config: GenerationConfig) -> types.GenerateContentConfig:
        generation_config = types.GenerateContentConfig(
            temperature=config.temperature,
            top_p=config.top_p,
            top_k=config.top_k,
            max_output_tokens=config.max_tokens,
            safety_settings=self._build_safety_settings(config.safety_level),
        )
        if config.json_mode:
            generation_config.response_mime_type = "application/json"
        return generation_config

    def _handle_api_error(self, exc: Exception) -> None:
        message = str(exc).lower()
        if "rate" in message and "limit" in message:
            raise RateLimitError(str(exc)) from exc
        if "timeout" in message or "timed out" in message:
            raise TimeoutError(str(exc)) from exc
        if "api key" in message or "invalid" in message and "key" in message:
            raise GeminiAPIError(str(exc), code="INVALID_API_KEY") from exc
        if "network" in message or "connection" in message or "internet" in message:
            raise GeminiAPIError("Network error. Check your internet connection.", code="NO_INTERNET") from exc
        raise GeminiAPIError(str(exc)) from exc

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        input_variables: dict[str, str] | None = None,
        model: str | None = None,
        config: GenerationConfig | None = None,
    ) -> PromptRunResponse:
        if not user_prompt or not user_prompt.strip():
            raise GeminiAPIError("Prompt cannot be empty.", code="EMPTY_PROMPT")

        config = config or GenerationConfig()
        variables = input_variables or {}
        rendered_user = apply_variables(user_prompt, variables)
        rendered_system = apply_variables(system_prompt, variables) if system_prompt else ""
        selected_model = model or self.default_model

        contents: list[types.Content] = []
        if rendered_system:
            contents.append(
                types.Content(role="user", parts=[types.Part(text=rendered_system)]),
            )
            contents.append(
                types.Content(role="model", parts=[types.Part(text="Understood. I will follow these instructions.")]),
            )
        contents.append(types.Content(role="user", parts=[types.Part(text=rendered_user)]))

        start = time.perf_counter()
        try:
            response = self.client.models.generate_content(
                model=selected_model,
                contents=contents,
                config=self._build_config(config),
            )
            elapsed_ms = (time.perf_counter() - start) * 1000
            text = response.text or ""
            if not text.strip():
                raise GeminiAPIError("Received empty response from Gemini.", code="INVALID_RESPONSE")

            usage = estimate_tokens(rendered_system + rendered_user + text)
            return PromptRunResponse(
                text=text,
                execution_time_ms=round(elapsed_ms, 2),
                token_usage=usage,
                model=selected_model,
                success=True,
            )
        except GeminiAPIError:
            raise
        except Exception as exc:
            self._handle_api_error(exc)
            raise

    def generate_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        input_variables: dict[str, str] | None = None,
        model: str | None = None,
        config: GenerationConfig | None = None,
    ) -> Generator[str, None, None]:
        config = config or GenerationConfig(stream=True)
        variables = input_variables or {}
        rendered_user = apply_variables(user_prompt, variables)
        rendered_system = apply_variables(system_prompt, variables) if system_prompt else ""
        selected_model = model or self.default_model

        contents: list[types.Content] = []
        if rendered_system:
            contents.append(types.Content(role="user", parts=[types.Part(text=rendered_system)]))
            contents.append(
                types.Content(role="model", parts=[types.Part(text="Understood. I will follow these instructions.")]),
            )
        contents.append(types.Content(role="user", parts=[types.Part(text=rendered_user)]))

        try:
            stream = self.client.models.generate_content_stream(
                model=selected_model,
                contents=contents,
                config=self._build_config(config),
            )
            for chunk in stream:
                if chunk.text:
                    yield chunk.text
        except Exception as exc:
            self._handle_api_error(exc)

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        input_variables: dict[str, str] | None = None,
        model: str | None = None,
        config: GenerationConfig | None = None,
    ) -> dict[str, Any]:
        json_config = (config or GenerationConfig()).model_copy(update={"json_mode": True})
        result = self.generate(system_prompt, user_prompt, input_variables, model, json_config)
        try:
            return json.loads(result.text)
        except json.JSONDecodeError as exc:
            cleaned = result.text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[-1]
                if cleaned.endswith("```"):
                    cleaned = cleaned.rsplit("```", 1)[0]
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError as inner:
                raise JSONParseError(f"Failed to parse JSON: {inner}") from inner

    def test_connection(self) -> tuple[bool, str]:
        try:
            response = self.generate(
                system_prompt="You are a test assistant.",
                user_prompt="Reply with exactly: OK",
                config=GenerationConfig(max_tokens=10, temperature=0.0),
            )
            if response.success:
                return True, "Connection successful"
            return False, "Connection failed"
        except GeminiAPIError as exc:
            return False, exc.message
