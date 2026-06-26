# Service Layer API Reference

## ServiceContainer

Access all services via context manager:

```python
from backend.service_factory import get_services

with get_services() as services:
    user = services.auth.register(UserCreate(...))
    result = services.gemini.generate(system_prompt, user_prompt)
```

## AuthService

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `register` | `UserCreate` | `UserOut` | Create new user |
| `login` | `UserLogin` | `(UserOut, token\|None)` | Authenticate user |
| `logout` | `user_id: int` | `None` | Clear remember token |
| `update_theme` | `user_id, theme` | `UserOut` | Update UI theme |

## PromptService

| Method | Description |
|--------|-------------|
| `create(user_id, PromptCreate)` | Create prompt + v1 |
| `list_prompts(user_id, filters...)` | Search/filter/sort |
| `update(user_id, prompt_id, PromptUpdate)` | Update metadata |
| `create_version(user_id, prompt_id, note)` | Snapshot version |
| `duplicate(user_id, prompt_id)` | Clone prompt |
| `restore_version(user_id, prompt_id, version_id)` | Restore old version |
| `list_versions(user_id, prompt_id)` | Version history |
| `get_version_diff(...)` | Line diff |
| `record_usage(user_id, prompt_id, success)` | Track usage |
| `seed_templates(user_id)` | Load built-in templates |

## GeminiService

| Method | Description |
|--------|-------------|
| `generate(...)` | Single completion |
| `generate_stream(...)` | Streaming completion |
| `generate_json(...)` | JSON mode response |
| `test_connection()` | API health check |

**Errors:** `GeminiAPIError`, `RateLimitError`, `TimeoutError`, `JSONParseError`

## EvaluationService

| Method | Description |
|--------|-------------|
| `evaluate(user_id, EvaluationRequest)` | Score output 0-100 |

Returns `EvaluationResponse` with 9 criteria scores, explanation, suggested/optimized prompts.

## OptimizerService

| Method | Description |
|--------|-------------|
| `optimize(OptimizerRequest)` | Generate 1-5 optimized versions |

## ComparisonService

| Method | Description |
|--------|-------------|
| `compare(ComparisonRequest)` | Run 2-5 prompts, score, pick winner |

## ExperimentService

| Method | Description |
|--------|-------------|
| `create`, `list_experiments`, `update_status`, `update_notes` | CRUD |
| `export_history(user_id)` | Export all experiments |
| `get_success_rate`, `get_average_execution_time` | Metrics |

## AnalyticsService

| Method | Description |
|--------|-------------|
| `record_event(...)` | Log analytics event |
| `get_dashboard_stats(user_id)` | Dashboard data |
| `get_analytics_summary(user_id)` | Chart data |
| `export_analytics(user_id)` | JSON export |

## ExportService

| Method | Formats |
|--------|---------|
| `export_json` | JSON |
| `export_csv` | CSV |
| `export_markdown` | Markdown |
| `export_html` | HTML |
| `export_pdf_report` | PDF |
| `export_comparison_pdf` | PDF |

## SettingsService

| Method | Description |
|--------|-------------|
| `get/set_setting` | Key-value settings |
| `save_gemini_config` | API key + model |
| `backup_database` | Create .db backup |
| `restore_database` | Restore from backup |
| `clear_database` | Reset all tables |

## Pydantic Schemas

All request/response models defined in `models/schemas.py`.
