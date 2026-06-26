# Prompt Engineering Guide

## Techniques Used in This Project

### 1. Role Prompting

System prompts assign a specific expert role:

```
You are an expert Prompt Engineering Evaluator and AI Quality Analyst.
```

Used in: Evaluation Engine, Optimizer, Comparison scoring.

### 2. Structured JSON Output

Evaluation and optimization prompts require strict JSON schemas:

```json
{
  "scores": { "accuracy": 0, "overall_score": 0 },
  "explanation": "...",
  "optimized_prompt": "..."
}
```

Benefits: Parseable, validated, database-storable.

### 3. Chain of Thought (Internal)

Optimizer system prompt references CoT for internal reasoning without exposing it in output.

### 4. Few-Shot Examples

Built-in prompt templates in the Library serve as few-shot patterns users can adapt.

### 5. Prompt Chaining

Playground → Evaluation → Optimizer → Playground forms a refinement chain.

### 6. Output Validation

- Pydantic schemas validate all inputs
- JSON parsing with fallback and error recovery
- Empty response detection

### 7. Error Recovery

If JSON parsing fails, evaluation service retries with raw text parsing.

### 8. Prompt Templates

Reusable templates with `{{variable}}` substitution for dynamic inputs.

### 9. Constraint Specification

Optimizer prompts include explicit goals:
- Reduce hallucinations
- Improve clarity
- Increase accuracy

### 10. Weighted Scoring

Comparison overall score uses weighted criteria:
- Quality: 35%
- Consistency: 25%
- Readability: 20%
- Response time: 10%
- Quality proxy: 10%

## Best Practices Demonstrated

1. Separate system and user prompts
2. Use variables for reusable templates
3. Configure temperature per use case (0.2 for scoring, 0.7 for creative)
4. Enable JSON mode for structured outputs
5. Version control prompts like code
6. Evaluate outputs systematically
7. Document prompt changes with version notes

## Evaluation Criteria Explained

| Criterion | What It Measures |
|-----------|-----------------|
| Accuracy | Factual correctness |
| Completeness | Coverage of requirements |
| Hallucination Risk | Fabrication likelihood |
| Grammar | Language correctness |
| Structure | Logical organization |
| Professionalism | Tone appropriateness |
| Formatting | Visual clarity |
| Readability | Ease of understanding |
| Prompt Effectiveness | Prompt-response alignment |

## Optimization Strategies

The Optimizer generates versions with different strategies:
1. **Clarity-Focused** — Simpler instructions
2. **Constraint-Heavy** — Explicit boundaries
3. **Structure-Optimized** — Step-by-step format

## Further Reading

- Google AI Prompt Design Guide
- OpenAI Prompt Engineering Best Practices
- Anthropic Prompt Library
