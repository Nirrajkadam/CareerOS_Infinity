# Runtime verification follow-up — 2026-09-28

This follows the initial review and changes on PR #1. The prototype still needs live deployment and provider validation.

## Repairs

- Fresh Alembic installs now enable pgvector, create the missing base resumes table, align the user schema with the authentication model, and create refresh-token, audit and graph tables. All runtime model modules are registered with Alembic.
- Registration supports an omitted full name. Registration and login propagate persistence errors instead of hiding failed audit/session writes.
- Resume parsing without AI only records skills actually mentioned in the document. It does not invent proficiency levels or default technical skills.
- Application creation uses the job model's source URL and the matching service's actual arguments and return object. Stored application scores and missing skills come from the computed match.
- CI now provisions PostgreSQL 16 with pgvector, applies every migration from an empty database, repeats the upgrade, and runs the full backend suite.

## Verification scope

Local focused regressions pass (89 tests). Four new database request tests exercise model-column availability, registration/login/refresh/logout, resume fallback persistence and ownership, version archival, application creation, computed score persistence, deduplication and dashboard/profile reads. Local database checks use PGlite with pgvector; the scratch harness terminates connections explicitly to accommodate its socket-close behavior. Native PostgreSQL verification runs in GitHub Actions.

A Chromium smoke test against the production Next.js build passed account creation/sign-in, the dashboard empty state, applications and resume navigation, mobile viewport overflow checks, and logout, with no browser page errors.

The database tests use disposable accounts and replace only external AI calls. They do not send email, contact employers or submit job applications.

## Upgrade and remaining limits

Run `alembic upgrade head` before starting the backend on a fresh database. Existing databases initialized manually or using incomplete legacy migrations need a schema/revision reconciliation and backup before upgrading. Do not blindly stamp an existing database or run these tests against production.

AI provider availability and model configuration, live job portals, desktop browser sessions, email integration and deployed hosting remain unverified. Profile and job-detail screens still include labeled previews. The GitHub Pages workflow still expects a static export absent from this dynamic Next.js app. Application preparation is not proof of submission.
