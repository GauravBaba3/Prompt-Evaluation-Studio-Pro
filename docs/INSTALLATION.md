# Installation Guide

## Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))

## Step-by-Step Installation

### 1. Download the project

```bash
git clone https://github.com/yourusername/prompt-evaluation-studio-pro.git
cd prompt-evaluation-studio-pro
```

### 2. Create virtual environment

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:
```
GEMINI_API_KEY=your_actual_api_key
GEMINI_MODEL=gemini-2.0-flash
DATABASE_URL=sqlite:///./data/prompt_studio.db
SECRET_KEY=generate-a-random-secret
LOG_LEVEL=INFO
```

### 5. Initialize database

```bash
python scripts/init_db.py
```

### 6. Run application

```bash
streamlit run app.py
```

Navigate to **http://localhost:8501**

### 7. First-time setup

1. Click **Sign Up** and create an account
2. Go to **Admin** in sidebar
3. Enter your Gemini API key and click **Save**
4. Click **Test Connection** to verify
5. Go to **Library** → **Load Built-in Templates**

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Ensure virtual env is activated and dependencies installed |
| `INVALID_API_KEY` | Verify API key in `.env` or Admin Settings |
| Database errors | Run `python scripts/init_db.py` |
| Port in use | `streamlit run app.py --server.port 8502` |

## Verify Installation

```bash
pytest tests/ -v
```

All tests should pass.
