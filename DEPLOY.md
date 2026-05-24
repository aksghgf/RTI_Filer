# Deployment Guide

Two supported paths: **Docker Compose** (local/VPS) and **Render** (managed cloud).

## Prerequisites

- `GROQ_API_KEY` and `GEMINI_API_KEY`
- Docker Desktop (for Compose) or a [Render](https://render.com) account

---

## Option A — Docker Compose (fastest local production test)

1. Copy env file at repo root:

```bash
cp .env.example .env
```

2. Edit `.env` and add your API keys.

3. Start everything:

```bash
docker compose up --build
```

4. Open:
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:8000
   - Swagger: http://localhost:8000/docs

Postgres runs on port `5432` and auto-applies `RTI_Filer/database/schema.sql` on first boot.

---

## Option B — Render (free tier cloud)

1. Push this repo to GitHub.

2. On Render: **New → Blueprint** → connect the repo (`render.yaml` is included).

3. When prompted, set secret env vars:
   - `GEMINI_API_KEY`
   - `GROQ_API_KEY`

4. After deploy finishes, open the **rti-backend** service and set:

```
CORS_ORIGINS=https://YOUR-FRONTEND-URL.onrender.com
```

Replace with the exact URL shown for **rti-frontend**.

5. Redeploy the backend (or use **Manual Deploy**) so CORS picks up the frontend URL.

6. Visit your **rti-frontend** URL — the build injects the backend host automatically via `API_URL`.

### Render notes

- Free web services spin down after inactivity; first request may take ~30s.
- PDF files are stored on ephemeral disk; use external storage for long-term PDF retention in production.
- Database tables are created automatically on backend startup.

---

## Environment variables

| Variable | Service | Description |
|---|---|---|
| `GROQ_API_KEY` | Backend | Groq LLM API key |
| `GEMINI_API_KEY` | Backend | Google Gemini API key |
| `DATABASE_URL` | Backend | PostgreSQL connection string |
| `CORS_ORIGINS` | Backend | Comma-separated frontend URLs |
| `API_URL` | Frontend build | Backend URL (auto-set on Render) |

See `RTI_Filer/.env.example` for a full backend template.
