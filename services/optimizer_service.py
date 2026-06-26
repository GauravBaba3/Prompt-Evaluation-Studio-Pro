"""Prompt optimizer service."""

from __future__ import annotations

from models.schemas import OptimizerRequest, OptimizerResponse, OptimizedVersion
from prompts.templates import OPTIMIZER_SYSTEM_PROMPT, OPTIMIZER_USER_TEMPLATE
from services.gemini_service import GeminiService
from utils.exceptions import JSONParseError, ValidationError
from utils.logger import get_logger

logger = get_logger(__name__)


class OptimizerService:
    def __init__(self, gemini: GeminiService | None = None) -> None:
        self.gemini = gemini or GeminiService()

    def optimize(self, request: OptimizerRequest) -> OptimizerResponse:
        if not request.prompt_text.strip():
            raise ValidationError("Prompt text is required for optimization.")

        user_message = OPTIMIZER_USER_TEMPLATE.format(
            prompt_text=request.prompt_text,
            system_prompt=request.system_prompt or "None",
            goal=request.goal,
            num_versions=request.num_versions,
        )

        raw = self.gemini.generate_json(
            system_prompt=OPTIMIZER_SYSTEM_PROMPT,
            user_prompt=user_message,
        )

        versions_raw = raw.get("versions", [])
        if not versions_raw:
            raise JSONParseError("Optimizer did not return any versions.")

        versions: list[OptimizedVersion] = []
        for item in versions_raw[: request.num_versions]:
            improvements = item.get("improvements", [])
            if isinstance(improvements, str):
                improvements = [improvements]
            versions.append(
                OptimizedVersion(
                    title=str(item.get("title", "Optimized Version")),
                    optimized_prompt=str(item.get("optimized_prompt", "")),
                    system_prompt=str(item.get("system_prompt", "")),
                    improvements=[str(i) for i in improvements],
                )
            )

        response = OptimizerResponse(
            original_prompt=request.prompt_text,
            versions=versions,
            summary=str(raw.get("summary", "Prompt optimization completed.")),
        )
        logger.info("Generated %s optimized versions", len(versions))
        return response
