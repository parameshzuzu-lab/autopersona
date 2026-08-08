# AutoPersona AI 🤖⚡

An autonomous AI and tech persona that continuously discovers, evaluates, filters, writes, and publishes tech & AI insights without manual prompting.

## Architecture Overview

- **Backend**: FastAPI, Python 3.11+, APScheduler, PostgreSQL, SQLAlchemy ORM, Google Gemini API
- **Frontend**: React 18, TypeScript, Vite, TailwindCSS (Dark Mode + Glassmorphism UI), Framer Motion, Recharts
- **Authentication**: JWT Bearer Tokens
- **Autonomous Loop**:
  1. **News Discovery Engine**: Queries tech RSS feeds, search APIs, and live news triggers.
  2. **Editorial Evaluator**: Scores content against criteria, rejects low-quality/off-topic posts.
  3. **Voice & Memory Writer**: Synthesizes posts using persistent editorial persona voice & long-term memory.
  4. **Scheduler & 48h Simulation Engine**: Manages cron intervals & fast-forward simulation.

## Directory Structure

Refer to the complete directory layout in `backend/` and `frontend/`.

## Run locally

From the project root, run the launcher below in PowerShell. It starts the API and the production frontend as background processes, waits for both to respond, and opens the dashboard.

```powershell
powershell -ExecutionPolicy Bypass -File .\start-local.ps1
```

The dashboard is available at `http://127.0.0.1:5173`.

## Deploy on Render

This project includes a Render Blueprint in `render.yaml`. It deploys the React dashboard and FastAPI API together as one Docker web service, with a managed Render Postgres database. Serving both from one origin keeps browser API calls and client-side routes reliable.

1. Push this folder to a GitHub, GitLab, or Bitbucket repository.
2. In Render, choose **New > Blueprint**, then select that repository.
3. Confirm the generated `autopersona` service and `autopersona-postgres` database.
4. Add `GEMINI_API_KEY` in Render if live content generation is required. `OPENAI_API_KEY` is optional for the current configuration.
5. Deploy and open the generated `onrender.com` URL.

The Blueprint defaults to Render's free tier for an inexpensive demo. Free web services spin down after 15 minutes with no inbound traffic, so use a paid web service for dependable background scheduling.
