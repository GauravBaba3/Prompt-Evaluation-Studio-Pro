"""AI evaluation engine service."""

from __future__ import annotations

import json

from sqlalchemy.orm import Session

from database.models import Evaluation
from models.schemas import EvaluationRequest, EvaluationResponse, EvaluationScores
from prompts.templates import EVALUATION_SYSTEM_PROMPT, EVALUATION_USER_TEMPLATE
from services.gemini_service import GeminiService
from utils.exceptions import JSONParseError, ValidationError
from utils.logger import get_logger

logger = get_logger(__name__)


class EvaluationService:
    def __init__(self, session: Session, gemini: GeminiService | None = None) -> None:
        self.session = session
        self.gemini = gemini or GeminiService()

    def evaluate(self, user_id: int, request: EvaluationRequest) -> EvaluationResponse:
        if not request.prompt_text.strip() or not request.response_text.strip():
            raise ValidationError("Prompt and response text are required for evaluation.")

        user_message = EVALUATION_USER_TEMPLATE.format(
            prompt_text=request.prompt_text,
            response_text=request.response_text,
            context=request.context or "No additional context provided.",
        )

        try:
            raw = self.gemini.generate_json(
                system_prompt=EVALUATION_SYSTEM_PROMPT,
                user_prompt=user_message,
            )
        except JSONParseError:
            fallback = self.gemini.generate(
                system_prompt=EVALUATION_SYSTEM_PROMPT,
                user_prompt=user_message,
            )
            try:
                raw = json.loads(fallback.text)
            except json.JSONDecodeError as exc:
                raise JSONParseError(f"Evaluation returned invalid JSON: {exc}") from exc

        scores_data = raw.get("scores", raw)
        scores = EvaluationScores(
            accuracy=float(scores_data.get("accuracy", 0)),
            completeness=float(scores_data.get("completeness", 0)),
            hallucination_risk=float(scores_data.get("hallucination_risk", 0)),
            grammar=float(scores_data.get("grammar", 0)),
            structure=float(scores_data.get("structure", 0)),
            professionalism=float(scores_data.get("professionalism", 0)),
            formatting=float(scores_data.get("formatting", 0)),
            readability=float(scores_data.get("readability", 0)),
            prompt_effectiveness=float(scores_data.get("prompt_effectiveness", 0)),
            overall_score=float(scores_data.get("overall_score", 0)),
        )

        if scores.overall_score == 0:
            positive_scores = [
                scores.accuracy,
                scores.completeness,
                100 - scores.hallucination_risk,
                scores.grammar,
                scores.structure,
                scores.professionalism,
                scores.formatting,
                scores.readability,
                scores.prompt_effectiveness,
            ]
            scores.overall_score = round(sum(positive_scores) / len(positive_scores), 2)

        response = EvaluationResponse(
            scores=scores,
            explanation=str(raw.get("explanation", "")),
            suggested_prompt=str(raw.get("suggested_prompt", "")),
            optimized_prompt=str(raw.get("optimized_prompt", "")),
            raw=raw,
        )

        evaluation = Evaluation(
            user_id=user_id,
            experiment_id=request.experiment_id,
            prompt_text=request.prompt_text,
            response_text=request.response_text,
            overall_score=scores.overall_score,
            accuracy=scores.accuracy,
            completeness=scores.completeness,
            hallucination_risk=scores.hallucination_risk,
            grammar=scores.grammar,
            structure=scores.structure,
            professionalism=scores.professionalism,
            formatting=scores.formatting,
            readability=scores.readability,
            prompt_effectiveness=scores.prompt_effectiveness,
            explanation=response.explanation,
            suggested_prompt=response.suggested_prompt,
            optimized_prompt=response.optimized_prompt,
            raw_json=json.dumps(raw),
        )
        self.session.add(evaluation)
        self.session.flush()
        logger.info("Evaluation saved with score %.2f for user %s", scores.overall_score, user_id)
        return response

    def list_evaluations(self, user_id: int, limit: int = 50) -> list[Evaluation]:
        return (
            self.session.query(Evaluation)
            .filter(Evaluation.user_id == user_id)
            .order_by(Evaluation.created_at.desc())
            .limit(limit)
            .all()
        )
