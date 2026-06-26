# Database Schema — Prompt Evaluation Studio Pro

## Entity Relationship Overview

```
users ──┬── prompts ──── prompt_versions
        ├── experiments ── evaluations
        ├── analytics
        └── (settings stored in app_settings via user context)

settings (global key-value store)
```

## Tables

### users

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Auto-increment ID |
| username | VARCHAR(80) UNIQUE | Login username |
| email | VARCHAR(120) UNIQUE | Email address |
| password_hash | VARCHAR(255) | bcrypt hash |
| is_admin | BOOLEAN | Admin flag |
| theme | VARCHAR(20) | light/dark |
| remember_token | VARCHAR(255) | Session persistence |
| created_at | DATETIME | Registration time |
| last_login | DATETIME | Last login time |

### prompts

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Prompt ID |
| user_id | FK → users | Owner |
| title | VARCHAR(200) | Display title |
| description | TEXT | Description |
| system_prompt | TEXT | System instruction |
| user_prompt | TEXT | User prompt template |
| category | VARCHAR(80) | Category label |
| tags | TEXT | Comma-separated tags |
| is_template | BOOLEAN | Built-in template flag |
| is_favorite | BOOLEAN | Favorite flag |
| is_pinned | BOOLEAN | Pinned flag |
| current_version | INTEGER | Latest version number |
| usage_count | INTEGER | Times used |
| success_rate | FLOAT | Success percentage |
| last_used_at | DATETIME | Last usage |
| created_at / updated_at | DATETIME | Timestamps |

### prompt_versions

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Version ID |
| prompt_id | FK → prompts | Parent prompt |
| version_number | INTEGER | Version number |
| system_prompt | TEXT | Snapshot system prompt |
| user_prompt | TEXT | Snapshot user prompt |
| change_note | TEXT | Version description |
| tags | TEXT | Tags at version time |
| created_at | DATETIME | Created timestamp |

### experiments

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Experiment ID |
| user_id | FK → users | Owner |
| prompt_id | FK → prompts (nullable) | Linked prompt |
| title | VARCHAR(200) | Experiment title |
| notes | TEXT | User notes |
| status | VARCHAR(30) | draft/running/completed/failed/archived |
| model_used | VARCHAR(80) | Gemini model |
| input_variables | TEXT | JSON string |
| system_prompt / user_prompt | TEXT | Prompts used |
| response_text | TEXT | AI response |
| temperature, top_p, top_k, max_tokens | Various | Generation config |
| execution_time_ms | FLOAT | Response time |
| token_usage | INTEGER | Token count |
| success | BOOLEAN | Success flag |
| error_message | TEXT | Error details |

### evaluations

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Evaluation ID |
| user_id | FK → users | Owner |
| experiment_id | FK → experiments (nullable) | Linked experiment |
| prompt_text / response_text | TEXT | Evaluated content |
| overall_score | FLOAT | 0-100 score |
| accuracy … prompt_effectiveness | FLOAT | Individual criteria |
| explanation | TEXT | AI explanation |
| suggested_prompt / optimized_prompt | TEXT | Recommendations |
| raw_json | TEXT | Full JSON response |

### analytics

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Record ID |
| user_id | FK → users | Owner |
| event_type | VARCHAR(80) | Event name |
| category | VARCHAR(80) | Prompt category |
| model_used | VARCHAR(80) | Model |
| execution_time_ms | FLOAT | Timing |
| score | FLOAT | Optional score |
| token_usage | INTEGER | Tokens |
| success | BOOLEAN | Success flag |
| metadata_json | TEXT | Extra data |
| created_at | DATETIME | Timestamp |

### settings

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | Setting ID |
| key | VARCHAR(100) UNIQUE | Setting key |
| value | TEXT | Setting value |
| updated_at | DATETIME | Last update |

## Indexes

- `users.username`, `users.email`
- `prompts.user_id`
- `experiments.user_id`, `experiments.prompt_id`
- `analytics.user_id`, `analytics.event_type`, `analytics.created_at`

## ER Diagram

See `assets/diagrams/er_diagram.mmd`
