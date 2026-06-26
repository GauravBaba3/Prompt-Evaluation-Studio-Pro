# Release Notes — v1.0.0

**Release Date:** June 26, 2026

## Highlights

First public release of Prompt Evaluation Studio Pro — a complete Prompt Engineering platform.

## New Features

### Core Platform
- Streamlit web application with sidebar navigation
- Local authentication with bcrypt and session management
- SQLite database with SQLAlchemy ORM

### Prompt Tools
- Playground with streaming, JSON mode, and safety settings
- Comparison of 2-5 prompt variants with winner selection
- Version control with diff viewer and restore
- Library with search, filters, templates, and favorites

### AI Features
- Evaluation Engine with 9-criteria scoring (0-100)
- Prompt Optimizer with multi-version output
- Built-in prompt templates for common use cases

### Data & Analytics
- Experiment manager with status tracking
- Analytics dashboard with Plotly charts
- Export to PDF, CSV, Markdown, JSON, HTML

### Admin
- Gemini API configuration
- Database backup and restore
- Theme selection

## Technical

- Python 3.12+ with full type hints
- google-genai SDK for Gemini integration
- Pydantic v2 schemas
- 23 pytest tests (all passing)
- Docker and docker-compose support

## Documentation

- 10+ markdown documentation files
- Interview guide with 50 Q&A
- Portfolio content and project report
- Presentation with speaker notes
- Architecture and ER diagrams

## Known Limitations

- SQLite for local storage (PostgreSQL recommended for production)
- Single-user sessions (no team collaboration yet)
- Gemini-only (multi-LLM planned for v2.0)

## Upgrade Notes

Initial release — no migration needed.

## Installation

```bash
pip install -r requirements.txt
cp .env.example .env
python scripts/init_db.py
streamlit run app.py
```
