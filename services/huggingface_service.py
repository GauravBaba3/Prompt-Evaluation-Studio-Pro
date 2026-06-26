"""Hugging Face Inference Router API integration service."""

from __future__ import annotations

import json
import time
from typing import Any, Generator

import httpx

from config.settings import get_settings
from models.schemas import GenerationConfig, PromptRunResponse
from utils.exceptions import GeminiAPIError, JSONParseError, RateLimitError, TimeoutError
from utils.formatters import apply_variables
from utils.logger import get_logger
from utils.text_metrics import estimate_tokens

logger = get_logger(__name__)

API_URL = "https://router.huggingface.co/v1/chat/completions"


class HuggingFaceService:
    """OpenAI-compatible chat completions client for Hugging Face Router."""

    def __init__(self, api_token: str | None = None, model: str | None = None) -> None:
        settings = get_settings()
        self.api_token = settings.hf_token if api_token is None else api_token
        self.default_model = model or settings.hf_model
        self._client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        if not self.api_token:
            raise GeminiAPIError(
                "Hugging Face token is not configured. Set HF_TOKEN in .env or Admin Settings.",
                code="INVALID_API_KEY",
            )
        if self._client is None:
            self._client = httpx.Client(
                headers={"Authorization": f"Bearer {self.api_token}"},
                timeout=120.0,
            )
        return self._client

    def _build_messages(
        self,
        system_prompt: str,
        user_prompt: str,
        json_mode: bool = False,
    ) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        if system_prompt:
            content = system_prompt
            if json_mode:
                content += "\n\nRespond with valid JSON only, no markdown fences."
            messages.append({"role": "system", "content": content})
        elif json_mode:
            messages.append(
                {
                    "role": "system",
                    "content": "Respond with valid JSON only, no markdown fences.",
                },
            )
        messages.append({"role": "user", "content": user_prompt})
        return messages

    def _build_payload(
        self,
        messages: list[dict[str, str]],
        model: str,
        config: GenerationConfig,
        stream: bool = False,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": config.temperature,
            "top_p": config.top_p,
            "max_tokens": config.max_tokens,
        }
        if stream:
            payload["stream"] = True
        return payload

    def _handle_api_error(self, exc: Exception, status_code: int | None = None) -> None:
        message = str(exc).lower()
        if status_code == 429 or ("rate" in message and "limit" in message):
            raise RateLimitError(str(exc)) from exc
        if status_code == 408 or "timeout" in message or "timed out" in message:
            raise TimeoutError(str(exc)) from exc
        if status_code in (401, 403) or "unauthorized" in message or "invalid" in message and "token" in message:
            raise GeminiAPIError(str(exc), code="INVALID_API_KEY") from exc
        if "network" in message or "connection" in message:
            raise GeminiAPIError("Network error. Check your internet connection.", code="NO_INTERNET") from exc
        raise GeminiAPIError(str(exc)) from exc

    def _extract_text(self, response_data: dict[str, Any]) -> str:
        try:
            return response_data["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as exc:
            raise GeminiAPIError("Invalid response format from Hugging Face.", code="INVALID_RESPONSE") from exc

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
        messages = self._build_messages(rendered_system, rendered_user, config.json_mode)
        payload = self._build_payload(messages, selected_model, config)

        start = time.perf_counter()
        try:
            response = self.client.post(API_URL, json=payload)
            if response.status_code >= 400:
                detail = response.text
                try:
                    detail = response.json().get("error", {}).get("message", detail)
                except Exception:
                    pass
                self._handle_api_error(Exception(detail), response.status_code)

            data = response.json()
            elapsed_ms = (time.perf_counter() - start) * 1000
            text = self._extract_text(data)
            if not text.strip():
                raise GeminiAPIError("Received empty response from Hugging Face.", code="INVALID_RESPONSE")

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
        except httpx.TimeoutException as exc:
            raise TimeoutError(str(exc)) from exc
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
        messages = self._build_messages(rendered_system, rendered_user, config.json_mode)
        payload = self._build_payload(messages, selected_model, config, stream=True)

        try:
            with self.client.stream("POST", API_URL, json=payload) as response:
                if response.status_code >= 400:
                    detail = response.read().decode()
                    self._handle_api_error(Exception(detail), response.status_code)

                for line in response.iter_lines():
                    if not line.startswith("data: "):
                        continue
                    chunk = line[6:].strip()
                    if chunk == "[DONE]":
                        break
                    try:
                        data = json.loads(chunk)
                        delta = data["choices"][0].get("delta", {})
                        content = delta.get("content")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue
        except GeminiAPIError:
            raise
        except httpx.TimeoutException as exc:
            raise TimeoutError(str(exc)) from exc
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
