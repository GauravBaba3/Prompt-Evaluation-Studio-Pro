# Deployment Guide

## Local Deployment

```bash
streamlit run app.py --server.port 8501
```

## Docker Deployment

### Build and run

```bash
docker-compose up --build -d
```

Access at **http://localhost:8501**

### Environment variables

Set in `.env` or `docker-compose.yml`:
- `GEMINI_API_KEY` (required)
- `GEMINI_MODEL` (optional, default: gemini-2.0-flash)
- `SECRET_KEY` (required for production)

### Persistent volumes

Docker Compose mounts:
- `./data` — SQLite database
- `./logs` — Application logs
- `./exports` — Export files
- `./backups` — Database backups

## Streamlit Cloud Deployment

1. Push repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect GitHub repository
4. Set main file: `app.py`
5. Add secrets in Streamlit Cloud dashboard:

```toml
GEMINI_API_KEY = "your-key"
GEMINI_MODEL = "gemini-2.0-flash"
SECRET_KEY = "your-secret"
DATABASE_URL = "sqlite:///./data/prompt_studio.db"
```

6. Deploy

### Streamlit Cloud notes

- Free tier has resource limits
- SQLite persists within session; use backup feature regularly
- For production, consider external PostgreSQL

## Production Checklist

- [ ] Change `SECRET_KEY` to random value
- [ ] Set strong user passwords
- [ ] Configure API rate limiting awareness
- [ ] Enable regular database backups (Admin → Backup)
- [ ] Monitor logs in `logs/app.log`
- [ ] Use HTTPS (handled by Streamlit Cloud / reverse proxy)

## Reverse Proxy (Optional)

Use nginx to proxy to Streamlit:

```nginx
location / {
    proxy_pass http://127.0.0.1:8501;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```
