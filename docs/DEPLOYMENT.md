# GitHub Pages and API deployment

GitHub Pages serves the frontend files. The Python API, PostgreSQL and Redis run separately. Publishing the frontend cannot start or resume the API.

## 1. Restore the API

The repository's Vercel configuration lists `https://careeros-backend.onrender.com` as its backend. On 2026-09-30, `/health` returned HTTP 503 with `x-render-routing: suspend-by-user`. Confirm this is your Render service and resume it in the Render dashboard. Review any billing requirement before enabling a paid service.

Deploy the reviewed backend code with its database configuration and private `SECRET_KEY`. Run `alembic upgrade head` before API startup. Back up and reconcile any database created outside Alembic before migrating it. Set:

```text
CORS_ORIGINS=["https://nirrajkadam.github.io"]
COOKIE_SECURE=true
```

CORS uses the origin only, without `/CareerOS_Infinity`. Configure `GEMINI_API_KEY` for conversational AI and optional Azure Speech settings as described in [VOICE_ASSISTANT.md](VOICE_ASSISTANT.md). Keep keys in the backend's environment, never in frontend variables.

Confirm `GET /health` returns 200 and test sign-in, authenticated data access and browser CORS before considering the API ready. A successful health response alone does not verify the database or AI provider.

## 2. Configure the frontend build

In the GitHub repository, open **Settings → Secrets and variables → Actions → Variables → New repository variable**:

| Name | Value |
|---|---|
| `NEXT_PUBLIC_API_URL` | Your verified public HTTPS backend origin, optionally ending in `/api/v1` |

Use `https://careeros-backend.onrender.com` only if that is the resumed service you control. This URL is public configuration, not an API key. The Pages build stops if this variable is absent or points to localhost or plain HTTP.

In **Settings → Pages → Build and deployment → Source**, select **GitHub Actions**. After the changes are merged into `master`, the Pages workflow builds with `STATIC_EXPORT=true` and the repository name as `NEXT_PUBLIC_BASE_PATH`, then uploads and deploys `frontend/out` using GitHub's official Pages actions. It also supports manual **Actions → Deploy Frontend to GitHub Pages → Run workflow** on `master` after the workflow reaches the default branch. Only the deploy job receives Pages deployment permissions; it uses the `github-pages` environment and its protection rules.

This replaces the old workflow that only pushed files to `gh-pages`. Commits made with a workflow's `GITHUB_TOKEN` do not trigger another Pages build, so pushing generated files alone is insufficient. See [GitHub's publishing-source documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages).

Changing `NEXT_PUBLIC_API_URL` requires another frontend build. Retrying an old deployment without rebuilding will retain the old URL.

## Routing and local verification

Detail pages use `/jobs/detail/?id=...` and `/applications/detail/?id=...`. Query parameters let records created after deployment open and reload on a static host. Previous `/jobs/<id>` and `/applications/<id>` bookmarks must be reopened from their lists. Assistant links use Next.js navigation so the repository path is preserved.

```bash
cd frontend
npm ci
npm test
STATIC_EXPORT=true NEXT_PUBLIC_BASE_PATH=/CareerOS_Infinity NEXT_PUBLIC_API_URL=https://api.example.com npm run build
```

`api.example.com` is a build-test placeholder, not a live backend. `out/` must include the homepage, both detail-page directories and `_next/` assets. Normal `npm run build` / `npm start` continues to support Node hosting without static-export settings.

## Live acceptance checks

- Open the homepage and a nested route directly; verify scripts load under `/CareerOS_Infinity/_next/`.
- Create a test account, sign in, reload and sign out.
- Load resumes, jobs and applications; errors must remain visible without fabricated records.
- Open an application from both the tracker and KAI; reload the detail URL and verify it retains the same record.
- Test typed assistant requests, then microphone input and voice playback on the intended device.

Passing CI verifies code and exported files; it cannot resume Render, configure provider keys or prove that live integrations are working.
