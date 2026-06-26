# Architecture — Prompt Evaluation Studio Pro

## Overview

Prompt Evaluation Studio Pro follows a **modular layered architecture** separating presentation, business logic, data access, and external API integration.

## Layers

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                    │
│  (Dashboard, Playground, Comparison, Analytics, etc.)   │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                   Backend Service Factory                │
│              (ServiceContainer + get_services)           │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                      Services Layer                      │
│  Auth │ Prompts │ Experiments │ Gemini │ Evaluation     │
│  Optimizer │ Comparison │ Analytics │ Export │ Settings  │
└──────────┬──────────────────────────────┬───────────────┘
           │                              │
┌──────────▼──────────┐        ┌──────────▼──────────┐
│   SQLAlchemy ORM    │        │   Google Gemini API  │
│      (SQLite)       │        │   (google-genai SDK) │
└─────────────────────┘        └─────────────────────┘
```

## Design Principles

1. **Separation of Concerns** — UI logic in `frontend/`, business rules in `services/`, data models in `database/`.
2. **Dependency Injection** — `ServiceContainer` injects shared session and Gemini client.
3. **Pydantic Validation** — All inputs validated via schemas in `models/schemas.py`.
4. **Prompt Templates** — Evaluation and optimization prompts isolated in `prompts/templates.py`.
5. **Error Handling** — Custom exceptions with error codes for user-friendly messages.

## Data Flow — Prompt Execution

1. User configures prompt in Playground UI
2. Frontend calls `GeminiService.generate()` via service factory
3. Variables applied via `apply_variables()`
4. Request sent to Gemini with safety settings and generation config
5. Response stored as Experiment + Analytics event
6. Optional: Evaluation engine scores output

## Data Flow — Evaluation

1. User submits prompt + response
2. `EvaluationService` builds structured evaluation prompt
3. Gemini returns JSON with 9 criteria scores
4. Scores persisted to `evaluations` table
5. UI displays metrics, explanation, and optimized prompt

## Security

- Passwords hashed with **bcrypt**
- API keys stored in database settings (override `.env`)
- Session managed via Streamlit session state
- SQLite local storage (no external DB exposure)

## Scalability Notes

- SQLite suitable for portfolio/demo; swap `DATABASE_URL` for PostgreSQL in production
- Gemini service is stateless and horizontally scalable
- Export files written to local `exports/` directory

## Folder Structure Diagram

See `assets/diagrams/folder_structure.mmd` for the full Mermaid diagram.
