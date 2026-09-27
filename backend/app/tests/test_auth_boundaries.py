"""Request-level regressions for authentication and shared desktop access."""
import datetime
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import jwt
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.main import app
from app.core.config import Settings, settings
from app.core.database import get_db_session
from app.core.dependencies import get_user_repository
from app.core.exceptions import AuthenticationError
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User, UserRole
from app.services.auth_service import AuthService


@pytest.fixture
def account():
    return User(id=uuid.uuid4(), email="candidate@example.test", hashed_password="unused", role=UserRole.MEMBER, is_active=True, is_deleted=False)


@pytest.fixture
def api(account):
    repository = SimpleNamespace(get_by_id=AsyncMock(return_value=account))
    session = AsyncMock()
    session.add = MagicMock()

    async def database():
        yield session

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_user_repository] = lambda: repository
    app.dependency_overrides[get_db_session] = database
    with TestClient(app) as client:
        yield client, repository, session
    app.dependency_overrides = previous


def bearer(account):
    return {"Authorization": f"Bearer {create_access_token(str(account.id))}"}


@pytest.mark.parametrize("method,path", [
    ("get", "/auth/me"), ("get", "/resumes"), ("get", "/applications"),
    ("get", "/applications/credentials"), ("post", "/applications/credentials"),
    ("get", "/applications/browser-status"), ("post", "/applications/launch-session"),
    ("post", "/applications/verify-login"), ("post", "/applications/apply"),
    ("post", "/applications/autonomous-run"), ("post", "/applications/sync-email"),
    ("post", "/applications/sync-emails"), ("post", "/applications/emergency-stop"),
    ("post", "/applications/example/verify-email"), ("post", "/jobpilot/agent-command"),
])
def test_anonymous_requests_are_rejected(api, method, path):
    client, repository, session = api
    options = {"json": {}} if method == "post" else {}
    response = getattr(client, method)(f"/api/v1{path}", **options)
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    repository.get_by_id.assert_not_awaited()
    session.execute.assert_not_awaited()
    session.add.assert_not_called()


@pytest.mark.parametrize("claims", [
    {"sub": str(uuid.uuid4())},  # No expiration
    {"sub": "", "exp": 9999999999},
    {"sub": "not-a-uuid", "exp": 9999999999},
    {"exp": 9999999999},
    {"sub": str(uuid.uuid4()), "exp": 1},
])
def test_invalid_claims_are_rejected_before_user_lookup(api, claims):
    client, repository, _ = api
    token = jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    assert client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401
    repository.get_by_id.assert_not_awaited()


def test_bad_signature_is_rejected(api, account):
    client, repository, _ = api
    token = jwt.encode({"sub": str(account.id), "exp": 9999999999}, "different-private-test-secret-0123456789", algorithm="HS256")
    assert client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401
    repository.get_by_id.assert_not_awaited()


def test_valid_session_returns_only_public_account_fields(api, account):
    client, _, _ = api
    response = client.get("/api/v1/auth/me", headers=bearer(account))
    assert response.status_code == 200
    assert response.json() == {"id": str(account.id), "email": account.email, "full_name": None}


@pytest.mark.parametrize("state", ["missing", "disabled", "deleted", "former_mock_identity"])
def test_unavailable_accounts_are_not_resurrected(api, account, state):
    client, repository, session = api
    if state in ("missing", "former_mock_identity"):
        repository.get_by_id.return_value = None
    elif state == "disabled":
        account.is_active = False
    else:
        account.is_deleted = True
    if state == "former_mock_identity":
        account.id = uuid.UUID(int=0)
    assert client.get("/api/v1/auth/me", headers=bearer(account)).status_code == 401
    session.add.assert_not_called()
    session.flush.assert_not_awaited()


@pytest.mark.parametrize("method,path", [
    ("get", "/applications/credentials"), ("post", "/applications/credentials"),
    ("get", "/applications/browser-status"), ("post", "/applications/launch-session"),
    ("post", "/applications/verify-login"), ("post", "/applications/apply"),
    ("post", "/applications/autonomous-run"), ("post", "/applications/sync-email"),
    ("post", "/applications/sync-emails"), ("post", "/applications/emergency-stop"),
    ("post", "/applications/example/verify-email"), ("post", "/jobpilot/agent-command"),
])
def test_shared_resources_require_the_configured_operator(api, account, monkeypatch, method, path):
    monkeypatch.setattr(settings, "DESKTOP_OPERATOR_USER_ID", uuid.uuid4())
    client, _, session = api
    options = {"json": {}} if method == "post" else {}
    response = getattr(client, method)(f"/api/v1{path}", headers=bearer(account), **options)
    assert response.status_code == 403
    session.execute.assert_not_awaited()


def test_operator_can_read_browser_status_without_launching(api, account, monkeypatch):
    monkeypatch.setattr(settings, "DESKTOP_OPERATOR_USER_ID", account.id)
    client, _, _ = api
    assert client.get("/api/v1/applications/browser-status", headers=bearer(account)).status_code == 200


def test_sample_autonomous_feed_cannot_launch_real_applications(api, account, monkeypatch):
    monkeypatch.setattr(settings, "DESKTOP_OPERATOR_USER_ID", account.id)
    client, _, _ = api
    response = client.post("/api/v1/applications/autonomous-run", json={}, headers=bearer(account))
    assert response.status_code == 409
    assert "sample listings" in response.json()["detail"]


def test_logout_revokes_refresh_token_in_database(api):
    client, _, session = api
    client.cookies.set("refresh_token", "test-refresh-token")
    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    statement = session.execute.await_args.args[0]
    assert statement.compile().params == {"token_1": "test-refresh-token", "is_revoked": True}
    assert 'Max-Age=0' in response.headers['set-cookie']


@pytest.mark.asyncio
async def test_disabled_account_cannot_login(monkeypatch, account):
    account.is_active = False
    monkeypatch.setattr("app.services.auth_service.UserRepository.get_by_email", AsyncMock(return_value=account))
    with pytest.raises(AuthenticationError):
        await AuthService.authenticate_user(AsyncMock(), account.email, "password")


@pytest.mark.asyncio
async def test_deleted_account_cannot_refresh(monkeypatch, account):
    account.is_deleted = True
    session = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.first.return_value = SimpleNamespace(user_id=account.id)
    session.execute.return_value = result
    monkeypatch.setattr("app.services.auth_service.UserRepository.get_by_id", AsyncMock(return_value=account))
    with pytest.raises(AuthenticationError):
        await AuthService.refresh_access_session(session, "refresh-token")


def test_long_passwords_are_not_truncated():
    password = "x" * 100 + "one"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("x" * 100 + "two", hashed)
    assert not verify_password(password, "invalid-hash")


def test_explicit_zero_token_lifetime_expires(api, account):
    client, _, _ = api
    token = create_access_token(str(account.id), datetime.timedelta(0))
    assert client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_settings_reject_published_secret_and_wildcard_cors():
    with pytest.raises(ValidationError):
        Settings(SECRET_KEY="super_secret_jwt_sign_key_rotating_32_bytes_len", _env_file=None)
    with pytest.raises(ValidationError):
        Settings(CORS_ORIGINS=["*"], _env_file=None)


def test_application_feed_excludes_unowned_and_foreign_graph_records(api, account):
    client, _, session = api
    relational = MagicMock()
    relational.scalars.return_value.all.return_value = []
    graph = MagicMock()
    now = datetime.datetime.now(datetime.timezone.utc)
    graph.all.return_value = [
        ("application:mine", {"user_id": str(account.id), "company": "Mine"}, now),
        ("application:foreign", {"user_id": str(uuid.uuid4()), "company": "Foreign"}, now),
        ("application:unowned", {"company": "Unowned"}, now),
    ]
    session.execute.side_effect = [relational, graph]
    response = client.get("/api/v1/applications", headers=bearer(account))
    assert response.status_code == 200
    assert [entry["company"] for entry in response.json()] == ["Mine"]
    assert response.json()[0]["status"] == "UNKNOWN"
    assert response.json()[0]["submitted_at"] is None


def test_application_prepare_returns_real_id_and_authenticated_owner(api, account, monkeypatch):
    monkeypatch.setattr(settings, "DESKTOP_OPERATOR_USER_ID", account.id)
    prepare = AsyncMock(return_value="application-id")
    monkeypatch.setattr("app.services.browser_automation.BrowserAutomationService.run_auto_apply", prepare)
    client, _, session = api
    response = client.post('/api/v1/applications/apply', headers=bearer(account), json={
        "company": "Example", "role": "Engineer", "portal_url": "https://example.test/job",
    })
    assert response.status_code == 200
    assert response.json()["application_id"] == "application-id"
    assert response.json()["status"] == "READY_TO_SUBMIT"
    assert prepare.await_args.kwargs["user_id"] == str(account.id)
    assert prepare.await_args.kwargs["session"] is session


@pytest.mark.parametrize("owner_matches", [True, False])
def test_graph_detail_only_returns_requested_owned_application(api, account, owner_matches):
    client, _, session = api
    app_id = str(uuid.uuid4())
    relational = MagicMock()
    relational.scalars.return_value.first.return_value = None
    graph = MagicMock()
    graph.scalars.return_value.first.return_value = SimpleNamespace(
        properties={"user_id": str(account.id if owner_matches else uuid.uuid4()), "role": "Engineer", "company": "Example"},
        created_at=datetime.datetime.now(datetime.timezone.utc),
    )
    session.execute.side_effect = [relational, graph]
    response = client.get(f'/api/v1/applications/{app_id}', headers=bearer(account))
    assert response.status_code == (200 if owner_matches else 404)
    if owner_matches:
        assert response.json()["id"] == app_id
        assert response.json()["status"] == "UNKNOWN"


@pytest.mark.asyncio
async def test_prepared_browser_record_preserves_owner_without_claiming_submission(monkeypatch, account):
    import asyncio
    from app.services.browser_automation import BrowserAutomationService
    repository = AsyncMock()
    monkeypatch.setattr('app.services.browser_automation.PostgreSQLGraphRepository', lambda session: repository)
    monkeypatch.setattr(BrowserAutomationService, '_session_lock', asyncio.Lock())
    monkeypatch.setattr(BrowserAutomationService, '_application_registry', {})
    monkeypatch.setattr(BrowserAutomationService, '_application_sessions', {})
    monkeypatch.setattr(BrowserAutomationService, '_emergency_stopped', False)
    app_id = await BrowserAutomationService.run_auto_apply(AsyncMock(), str(account.id), 'Example', 'Engineer', 'https://example.test/job', '')
    props = repository.add_entity_node.await_args.kwargs['properties']
    assert props['user_id'] == str(account.id)
    assert props['id'] == app_id
    assert props['status'] == 'READY_TO_SUBMIT'
    assert props['submitted_at'] is None
    assert props['applied_at'] is None
    assert BrowserAutomationService._application_registry[app_id]['authentication_status'] == 'UNKNOWN'


@pytest.mark.asyncio
async def test_email_sync_cannot_verify_other_users_or_blank_companies(monkeypatch, account):
    from app.services.email_service import EmailSyncService
    nodes = [SimpleNamespace(id=f'application:{index}', properties=props) for index, props in enumerate([
        {'user_id': str(account.id), 'company': 'Example'},
        {'user_id': str(uuid.uuid4()), 'company': 'Example'},
        {'user_id': str(account.id), 'company': ''},
        {'company': 'Example'},
    ])]
    repository = AsyncMock()
    repository.get_entities_by_type.return_value = nodes
    monkeypatch.setattr('app.services.email_service.PostgreSQLGraphRepository', lambda session: repository)
    mailbox = MagicMock()
    mailbox.search.return_value = ('OK', [b'1'])
    mailbox.fetch.return_value = ('OK', [(b'1', b'Subject: Example application received\r\nFrom: recruiter@example.test\r\n\r\nReceived')])
    monkeypatch.setattr('app.services.email_service.imaplib.IMAP4_SSL', lambda server: mailbox)
    session = AsyncMock()
    session.add = MagicMock()
    await EmailSyncService.sync_confirmation_emails(session, str(account.id), email_address='candidate@example.test', app_password='test')
    session.add.assert_called_once_with(nodes[0])
    assert nodes[0].properties['status'] == 'SUBMITTED_VERIFIED'
    assert all('status' not in node.properties for node in nodes[1:])


def test_provider_database_urls_use_async_driver():
    config = Settings(DATABASE_URL='postgres://user:password@localhost/database', _env_file=None)
    assert config.DATABASE_URL == 'postgresql+asyncpg://user:password@localhost/database'
