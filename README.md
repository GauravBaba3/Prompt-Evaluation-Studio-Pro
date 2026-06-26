# Prompt Evaluation Studio Pro

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B.svg)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini-4285F4.svg)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Prompt Evaluation Studio Pro** is a production-quality Prompt Engineering platform for creating, comparing, evaluating, optimizing, and managing AI prompts using the **Google Gemini API**.

Built for developers and AI enthusiasts who want to demonstrate real prompt engineering skills — not just API integration.

---

## Features

| Module | Capabilities |
|--------|-------------|
| **Authentication** | Local signup/login, SQLite storage, bcrypt hashing, remember session |
| **Dashboard** | Stats cards, recent experiments, categories, search, dark mode |
| **Playground** | Full prompt editor, variables, generation config, streaming, JSON mode |
| **Comparison** | Compare 2–5 prompts with scoring and winner badge |
| **Version Control** | Versions, duplicate, restore, diff viewer, tags, favorites |
| **Library** | Search, filter, templates, sorting, pinned prompts |
| **Experiments** | Save runs, notes, status tracking, export history |
| **Evaluation Engine** | 9-criteria AI scoring out of 100 with optimization suggestions |
| **Optimizer** | Multi-version prompt rewriting with improvement explanations |
| **Analytics** | Plotly charts, trends, export analytics |
| **Export** | PDF, CSV, Markdown, JSON, HTML |
| **Admin** | API config, model selection, backup/restore, clear database |

---

## Tech Stack

- **Python 3.12+** · **Streamlit** · **Google Gemini API** (`google-genai`)
- **SQLite** · **SQLAlchemy** · **Pydantic** · **Pandas** · **Plotly**
- **Docker** · **pytest** · **ReportLab** (PDF export)

---

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/yourusername/prompt-evaluation-studio-pro.git
cd prompt-evaluation-studio-pro
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and set GEMINI_API_KEY=your_key_here
```

### 3. Initialize database

```bash
python scripts/init_db.py
```

### 4. Run the application

```bash
streamlit run app.py
```

Open **http://localhost:8501** → Sign up → Configure API key in **Admin** → Start experimenting.

---

## Docker

```bash
docker-compose up --build
```

---

## Project Structure

```
prompt-evaluation-studio-pro/
├── app.py                  # Main Streamlit entry point
├── frontend/               # UI pages and components
├── backend/                # Service factory
├── services/               # Business logic (Gemini, auth, evaluation, etc.)
├── database/               # SQLAlchemy models and connection
├── models/                 # Pydantic schemas
├── prompts/                # Prompt templates for evaluation/optimization
├── config/                 # Settings and constants
├── utils/                  # Helpers, logging, validators
├── tests/                  # pytest suite
├── docs/                   # Full documentation
├── scripts/                # DB init, PDF generation
├── assets/                 # Diagrams, screenshots, PDFs
├── Dockerfile
└── docker-compose.yml
```

---

## Testing

```bash
pytest tests/ -v
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [INSTALLATION.md](docs/INSTALLATION.md) | Detailed setup guide |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design |
| [DATABASE.md](docs/DATABASE.md) | Schema reference |
| [API.md](docs/API.md) | Service layer API |
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | Docker & Streamlit Cloud |
| [TESTING.md](docs/TESTING.md) | Test strategy |
| [INTERVIEW_GUIDE.md](docs/INTERVIEW_GUIDE.md) | Interview prep |
| [PROMPT_ENGINEERING_GUIDE.md](docs/PROMPT_ENGINEERING_GUIDE.md) | Techniques used |

---

## GitHub Topics

`prompt-engineering` `google-gemini` `streamlit` `python` `sqlite` `ai-evaluation` `llm` `portfolio-project` `machine-learning` `nlp`

---

## License

MIT License — see [LICENSE](LICENSE).

---

## Author

Built as a portfolio project demonstrating Prompt Engineering, full-stack Python development, and AI application architecture.
