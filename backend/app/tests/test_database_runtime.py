"""Request regressions against an Alembic-migrated, disposable PostgreSQL DB.

Run with CAREEROS_DATABASE_TESTS=1 and DATABASE_URL pointing at a test database.
Only external AI calls are replaced; authentication and persistence are real.
"""
import os
import json
import uuid
from unittest.mock import AsyncMock

import httpx
import pytest
import pytest_asyncio
from sqlalchemy import delete, select

from app.main import app
from app.core.ai_gateway import AIGateway
from app.core.database import AsyncSessionLocal, Base, engine
from app.models.job import JobPosting
from app.models.job_intelligence import JobMatch
from app.models.user import User

pytestmark = [pytest.mark.asyncio, pytest.mark.skipif(
    os.environ.get("CAREEROS_DATABASE_TESTS") != "1",
    reason="Requires an explicitly enabled disposable database",
)]


@pytest_asyncio.fixture
async def client(monkeypatch):
    monkeypatch.setattr(AIGateway, "generate_response", AsyncMock(side_effect=RuntimeError("AI offline")))
    monkeypatch.setattr(AIGateway, "generate_embeddings", AsyncMock(side_effect=RuntimeError("AI offline")))
    # Release pools on their creating loop, including on assertion failure.
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        yield client
    await engine.dispose()


@pytest_asyncio.fixture
async def account(client):
    payload = {"email": f"runtime-{uuid.uuid4().hex}@example.com", "password": "Runtime-test-password-123"}
    registered = await client.post("/api/v1/auth/register", json=payload)
    assert registered.status_code == 201, registered.text
    user_id = registered.json()["user_id"]
    login = await client.post("/api/v1/auth/login", json=payload)
    assert login.status_code == 200, login.text
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    try:
        yield payload, user_id, headers
    finally:
        async with AsyncSessionLocal() as session:
            await session.execute(delete(User).where(User.id == uuid.UUID(user_id)))
            await session.commit()


async def test_migrations_supply_every_model_column(client):
    async with AsyncSessionLocal() as session:
        for table in Base.metadata.sorted_tables:
            await session.execute(select(table).limit(0))


async def test_register_login_refresh_and_logout(client, account):
    payload, user_id, headers = account
    assert (await client.get("/api/v1/auth/me")).status_code == 401
    me = await client.get("/api/v1/auth/me", headers=headers)
    assert me.json() == {"id": user_id, "email": payload["email"], "full_name": None}
    assert (await client.post("/api/v1/auth/register", json=payload)).status_code == 401
    assert (await client.post("/api/v1/auth/login", json={**payload, "password": "incorrect"})).status_code == 401
    refresh_token = client.cookies.get("refresh_token")
    assert refresh_token
    assert (await client.post("/api/v1/auth/refresh")).status_code == 200
    assert (await client.post("/api/v1/auth/logout")).status_code == 200
    client.cookies.set("refresh_token", refresh_token)
    assert (await client.post("/api/v1/auth/refresh")).status_code == 401


async def test_resume_fallback_persistence_lineage_and_ownership(client, account):
    _, _, headers = account
    first = await client.post("/api/v1/resumes/upload", headers=headers,
                              files={"file": ("accountant.txt", b"Office administration and payroll.", "text/plain")})
    assert first.status_code == 201, first.text
    master = (await client.get("/api/v1/resumes/master", headers=headers)).json()
    assert master["resume_json"]["competencies"] == []
    assert master["version"] == 1
    second = await client.post("/api/v1/resumes/upload", headers=headers,
                               files={"file": ("developer.txt", b"Python and JavaScript experience", "text/plain")})
    assert second.status_code == 201, second.text
    versions = (await client.get("/api/v1/resumes", headers=headers)).json()
    assert len(versions) == 2
    assert sum(item["is_master"] for item in versions) == 1
    assert {item["lifecycle_status"] for item in versions} == {"ACTIVE", "ARCHIVED"}
    assert versions[0]["version"] == 2
    assert set(versions[0]["skills"]) == {"Python", "JavaScript"}
    other = {"email": f"other-{uuid.uuid4().hex}@example.com", "password": "Runtime-test-password-123"}
    other_id = (await client.post("/api/v1/auth/register", json=other)).json()["user_id"]
    try:
        login = await client.post("/api/v1/auth/login", json=other)
        other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        assert (await client.get("/api/v1/resumes", headers=other_headers)).json() == []
        assert (await client.get(f"/api/v1/resumes/{master['id']}/tailoring", headers=other_headers)).status_code == 404
    finally:
        async with AsyncSessionLocal() as session:
            await session.execute(delete(User).where(User.id == uuid.UUID(other_id)))
            await session.commit()


async def test_application_creation_preserves_computed_scores_and_deduplicates(client, account):
    _, user_id, headers = account
    async with AsyncSessionLocal() as session:
        job = JobPosting(title="Python Developer", company="Runtime Test Company",
                         description="Build and maintain Python web applications with a collaborative engineering team.",
                         source_url="https://example.com/jobs/runtime", jd_intelligence={"required_skills": ["Python"]})
        session.add(job)
        await session.commit()
        job_id = job.id
    try:
        response = await client.post("/api/v1/applications", headers=headers, json={"job_posting_id": str(job_id)})
        assert response.status_code == 201, response.text
        application = response.json()
        async with AsyncSessionLocal() as session:
            match = (await session.execute(select(JobMatch).where(
                JobMatch.user_id == uuid.UUID(user_id), JobMatch.job_id == job_id))).scalar_one()
            assert application["job_fit_score"] == match.overall_fit_score
            assert application["ats_score"] == match.ats_score
            assert application["missing_skills"]["missing_required"] == match.missing_required_skills
        again = await client.post("/api/v1/applications", headers=headers, json={"job_posting_id": str(job_id)})
        assert again.json()["status"] == "DUPLICATE"
        listed = (await client.get("/api/v1/applications", headers=headers)).json()
        assert [item["id"] for item in listed] == [application["id"]]
        assert listed[0]["submitted_at"] is None
        assert listed[0]["application_stage"] == "UNSUBMITTED"
        for path in ("/applications/analytics", "/career/profile", "/career/skills"):
            result = await client.get(f"/api/v1{path}", headers=headers)
            assert result.status_code == 200, result.text
    finally:
        async with AsyncSessionLocal() as session:
            await session.execute(delete(JobPosting).where(JobPosting.id == job_id))
            await session.commit()


async def test_assistant_search_compare_prepare_and_owner_scoping(client, account, monkeypatch):
    from app.core.config import settings
    from app.models.application import Application
    from app.services.career_assistant import CareerAssistant
    from app.tests.test_assistant import answer

    _, user_id, headers = account
    other_id = uuid.uuid4()
    async with AsyncSessionLocal() as session:
        job = JobPosting(title='DevOps Verification Engineer', company='Assistant Test',
                         description='Build reliable deployment pipelines with Python and Docker alongside our engineering team.',
                         jd_intelligence={'required_skills': ['Python', 'Docker']})
        session.add(job)
        session.add(User(id=other_id, email=f'assistant-other-{other_id}@example.com', hashed_password='unused'))
        await session.flush()
        job_id = job.id
        session.add(Application(user_id=other_id, job_posting_id=job.id, company='Other user private company', role='Private role'))
        await session.commit()
    monkeypatch.setattr(settings, 'GEMINI_API_KEY', 'test-only-model-mocked')
    monkeypatch.setattr(CareerAssistant, 'complete', AsyncMock(side_effect=[
        answer(calls=[('get_profile', {}), ('search_jobs', {'query': 'DevOps Verification', 'limit': 1})]),
        answer(calls=[('match_job', {'job_id': str(job_id)})]),
        answer(calls=[('prepare_application', {'job_id': str(job_id)}), ('list_applications', {})]),
        answer('Prepared your local application record. Nothing was submitted to the employer.'),
    ]))
    try:
        response = await client.post('/api/v1/assistant/chat', headers=headers,
                                     json={'message': 'Find DevOps Verification jobs, compare my fit and prepare the best one.'})
        assert response.status_code == 200, response.text
        result = response.json()
        assert result['mode'] == 'ai'
        assert len(result['steps']) == 5
        assert all(step['status'] == 'completed' for step in result['steps'])
        transcript = CareerAssistant.complete.call_args.args[0]
        tool_data = [json.loads(item['content']) for item in transcript if item['role'] == 'tool']
        listed = next(item for item in tool_data if 'applications' in item)
        assert len(listed['applications']) == 1
        assert listed['applications'][0]['company'] == 'Assistant Test'
        async with AsyncSessionLocal() as session:
            saved = (await session.execute(select(Application).where(Application.user_id == uuid.UUID(user_id)))).scalar_one()
            assert saved.source == 'ASSISTANT'
            assert saved.application_stage == 'UNSUBMITTED'
            assert saved.submitted_at is None
            assert any(link['url'] == f'/applications/{saved.id}' for link in result['links'])
    finally:
        async with AsyncSessionLocal() as session:
            await session.execute(delete(JobPosting).where(JobPosting.id == job_id))
            await session.execute(delete(User).where(User.id == other_id))
            await session.commit()
