# CareerOS Infinity

A career-workflow prototype built with **Next.js, FastAPI, PostgreSQL/pgvector, Redis and Playwright**. It includes resume processing, job discovery integrations, application records, and shared desktop portal-session tools.

## Current status

The application is under active development. Profile and job-detail screens still contain clearly labeled preview data. Browser/application preparation is not proof of employer submission. The legacy autonomous API rejects its sample listing feed.

See [the engineering review](docs/REVIEW_2026-09-27.md) and [runtime verification follow-up](docs/VERIFICATION_2026-09-28.md) for fixes, verification scope and upgrade notes.

## Local development

### Backend

Use Python 3.12 and **PostgreSQL with the pgvector extension installed** (for example, the `pgvector/pgvector:pg16` image). Alembic initializes the schema and enables the vector extension; the migration account needs permission to create it. Redis is needed for worker-backed functionality.

```bash
cd backend
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell instead:
# .venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Put the generated value in `SECRET_KEY` inside `.env`, then configure `DATABASE_URL` and `REDIS_URL`. On Windows, use `Copy-Item .env.example .env` in place of `cp` if needed.

```bash
python -m alembic upgrade head
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Frontend

```bash
cd frontend
npm ci
cp .env.example .env.local
npm run dev
```

Visit `http://localhost:3000`, create an account and sign in. API documentation is at `http://localhost:8000/docs`.

### Shared desktop functions

Portal browser profiles, the credential vault and IMAP settings are currently shared server resources. Only the account configured by `DESKTOP_OPERATOR_USER_ID` can access them. Leave this setting absent to keep those functions disabled.

1. Sign in and read your account UUID through `GET /api/v1/auth/me` using its bearer token.
2. Set `DESKTOP_OPERATOR_USER_ID` in the backend environment and restart the backend.
3. For interactive browser sessions, install Playwright Chromium and run the backend in a desktop environment.

```bash
python -m playwright install chromium
```

Do not run `autonomous_job_hunter.py` against real portals: its legacy feed includes invented listings. Preparing an application record does not send an application.

## Voice assistant

Use **Ask KAI** for typed or spoken instructions in Indian English or Hindi. With Gemini configured, it can search stored jobs, compare your profile and prepare application records automatically. Optional Azure Speech provides an Indian female neural voice; device speech is the fallback. See [setup, examples and supported actions](docs/VOICE_ASSISTANT.md).

## Configuration

| Setting | Purpose |
|---|---|
| `SECRET_KEY` | Required private random key, at least 32 characters. Also currently used by the legacy vault. |
| `DATABASE_URL` | PostgreSQL connection URL. Standard provider URLs are normalized to the asyncpg driver. |
| `REDIS_URL` | Redis broker/cache connection. |
| `CORS_ORIGINS` | JSON array of exact frontend origins. Defaults to local port 3000 origins. |
| `COOKIE_SECURE` | Defaults to `true`; use `false` only for local HTTP development. |
| `DESKTOP_OPERATOR_USER_ID` | Optional UUID permitted to use shared desktop/credential/inbox functions. |
| `ENABLE_SANDBOX_ATS` | Defaults to `false`; enable only for isolated development/test servers. |
| `GEMINI_API_KEY` | Optional provider key for AI features. |
| `NEXT_PUBLIC_API_URL` | Frontend build-time API origin, optionally ending in `/api/v1`. |

Rotating `SECRET_KEY` invalidates access tokens and makes existing vault entries unreadable. Re-enter those credentials under the new key. Legacy records without a verified owner are not automatically assigned to a new account.

## Verification

Focused backend regressions run without PostgreSQL, live AI calls or job-portal actions:

```bash
cd backend
PYTHONPATH=. python -m pytest app/tests/test_auth_boundaries.py app/tests/test_resume_fallback.py app/tests/test_stability_sprint.py app/tests/test_sandbox_ats_e2e.py -q
```

In PowerShell, set `$env:PYTHONPATH = "."` before invoking `python -m pytest` with the same paths. For the full suite, set `DATABASE_URL` to a separate disposable test database, `COOKIE_SECURE=false` and `CAREEROS_DATABASE_TESTS=1`, run `python -m alembic upgrade head`, then `python -m pytest app/tests -q`. These tests write data; never target a production database.

```bash
cd frontend
npm test
npm run build
```

GitHub Actions migrates a fresh PostgreSQL/pgvector database, runs the full backend suite, and runs frontend tests and the production build. They do not certify live portal automation or deployment readiness.

## Deployment notes

Set the frontend API URL **before** its production build, allow that frontend origin on the backend, and use HTTPS. `render.yaml` contains service configuration; run migrations before starting the API. Existing databases created manually outside Alembic need their schema and revision history reconciled before upgrading; take a backup first. The GitHub Pages workflow builds a static export with project-relative navigation and requires the `NEXT_PUBLIC_API_URL` repository variable. Follow the [deployment and recovery guide](docs/DEPLOYMENT.md), including live acceptance checks.

## License

Privately developed for CareerOS Infinity Platform. All rights reserved.
