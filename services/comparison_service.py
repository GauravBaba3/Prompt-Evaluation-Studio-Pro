"""Prompt comparison service."""

from __future__ import annotations

from models.schemas import ComparisonRequest, ComparisonResult, GenerationConfig
from prompts.templates import COMPARISON_QUALITY_PROMPT
from services.gemini_service import GeminiService
from utils.exceptions import ValidationError
from utils.logger import get_logger
from utils.text_metrics import compute_output_length, compute_readability_score, estimate_tokens

logger = get_logger(__name__)


class ComparisonService:
    def __init__(self, gemini: GeminiService | None = None) -> None:
        self.gemini = gemini or GeminiService()

    def compare(self, request: ComparisonRequest) -> list[ComparisonResult]:
        if len(request.prompts) < 2:
            raise ValidationError("At least 2 prompts are required for comparison.")
        if len(request.prompts) > 5:
            raise ValidationError("Maximum 5 prompts can be compared at once.")

        results: list[ComparisonResult] = []
        all_responses: list[str] = []

        for item in request.prompts:
            if not item.user_prompt.strip():
                raise ValidationError(f"Prompt '{item.label}' cannot be empty.")

            run_result = self.gemini.generate(
                system_prompt=item.system_prompt,
                user_prompt=item.user_prompt,
                input_variables=request.input_variables,
                model=request.model,
                config=request.config or GenerationConfig(),
            )
            all_responses.append(run_result.text)

            quality_scores = self._score_quality(item.user_prompt, run_result.text)
            readability = compute_readability_score(run_result.text)

            results.append(
                ComparisonResult(
                    label=item.label,
                    response_text=run_result.text,
                    execution_time_ms=run_result.execution_time_ms,
                    output_length=compute_output_length(run_result.text),
                    token_usage=run_result.token_usage or estimate_tokens(run_result.text),
                    quality_score=quality_scores["quality_score"],
                    consistency_score=quality_scores["consistency_score"],
                    readability_score=readability,
                    overall_score=0.0,
                )
            )

        avg_time = sum(r.execution_time_ms for r in results) / len(results)
        for result in results:
            time_score = max(0.0, 100 - abs(result.execution_time_ms - avg_time) / max(avg_time, 1) * 20)
            inverted_hallucination_proxy = result.quality_score
            result.overall_score = round(
                (
                    result.quality_score * 0.35
                    + result.consistency_score * 0.25
                    + result.readability_score * 0.2
                    + time_score * 0.1
                    + inverted_hallucination_proxy * 0.1
                ),
                2,
            )

        winner_index = max(range(len(results)), key=lambda i: results[i].overall_score)
        for index, result in enumerate(results):
            result.is_winner = index == winner_index

        logger.info("Compared %s prompts. Winner: %s", len(results), results[winner_index].label)
        return results

    def _score_quality(self, prompt_text: str, response_text: str) -> dict[str, float]:
        try:
            raw = self.gemini.generate_json(
                system_prompt="You score AI outputs. Return JSON only.",
                user_prompt=COMPARISON_QUALITY_PROMPT.format(
                    prompt_text=prompt_text,
                    response_text=response_text,
                ),
                config=GenerationConfig(max_tokens=256, temperature=0.2, json_mode=True),
            )
            return {
                "quality_score": float(raw.get("quality_score", 70)),
                "consistency_score": float(raw.get("consistency_score", 70)),
                "readability_score": float(raw.get("readability_score", compute_readability_score(response_text))),
            }
        except Exception:
            readability = compute_readability_score(response_text)
            return {
                "quality_score": min(100.0, readability + 10),
                "consistency_score": 75.0,
                "readability_score": readability,
            }
