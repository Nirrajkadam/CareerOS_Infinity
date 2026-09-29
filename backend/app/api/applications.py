"""
Job Applications REST API Router — Part 5

Endpoints:
- POST /api/v1/applications
- GET /api/v1/applications
- GET /api/v1/applications/analytics
- GET /api/v1/applications/skill-gaps
- GET /api/v1/applications/{id}
- PATCH /api/v1/applications/{id}
- DELETE /api/v1/applications/{id}
- POST /api/v1/applications/{id}/prepare
- POST /api/v1/applications/{id}/approve (Level 1 Package Approval)
- POST /api/v1/applications/{id}/start (Start Browser Automation)
- POST /api/v1/applications/{id}/final-submit (Level 2 Final Submission Approval)
- POST /api/v1/applications/{id}/pause
- POST /api/v1/applications/{id}/resume
- POST /api/v1/applications/{id}/skip
- POST /api/v1/applications/{id}/cancel
- GET /api/v1/applications/{id}/events
- POST /api/v1/applications/{id}/manual-action-complete

Application records are scoped to their owner. Shared desktop resources require the configured operator.
"""
import logging
import uuid
import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencies import get_current_user, get_desktop_operator
from app.models.user import User
from app.models.application import Application, ApplicationStatusHistory
from app.services.application_service import ApplicationService
from app.services.application_analytics_service import ApplicationAnalyticsService

logger = logging.getLogger("app.api.applications")
router = APIRouter(prefix="/applications", tags=["Job Applications Engine"], dependencies=[Depends(get_current_user)])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_application_endpoint(
    payload: dict,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    job_id = payload.get("job_posting_id") or payload.get("job_id")
    if not job_id:
        raise HTTPException(status_code=400, detail="job_posting_id is required.")

    try:
        return await ApplicationService.create_application(
            session=session,
            user=current_user,
            job_id=job_id,
            source=payload.get("source", "MANUAL"),
            tailored_resume_id=payload.get("tailored_resume_id"),
            communication_bundle_id=payload.get("communication_bundle_id"),
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.get("", status_code=status.HTTP_200_OK)
async def list_applications_endpoint(
    status_filter: Optional[str] = None,
    stage_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> List[dict]:
    query = select(Application).filter(Application.user_id == current_user.id)
    if status_filter:
        query = query.filter(Application.status == status_filter)
    if stage_filter:
        query = query.filter(Application.application_stage == stage_filter)

    query = query.order_by(Application.priority_score.desc(), Application.created_at.desc()).limit(20)
    res = await session.execute(query)
    apps = res.scalars().all()

    app_list = [
        {
            "id": str(a.id),
            "job_posting_id": str(a.job_posting_id) if a.job_posting_id else None,
            "company": a.company,
            "role": a.role,
            "location": a.location,
            "status": a.status,
            "application_stage": a.application_stage,
            "job_fit_score": a.job_fit_score,
            "ats_score": a.ats_score,
            "priority_score": a.priority_score,
            "risk_status": a.risk_status,
            "logs": a.logs if hasattr(a, "logs") and a.logs else [
                f"Application status: {a.status}",
                f"Stage: {a.application_stage or 'INGESTED'}",
                f"Priority score: {a.priority_score if a.priority_score is not None else 'unavailable'}"
            ],
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "submitted_at": a.submitted_at.isoformat() if a.submitted_at else None,
            "applied_at": a.submitted_at.isoformat() if a.submitted_at else None,
        }
        for a in apps
    ]

    # Include GraphNode APPLICATION entities (used by autonomous job hunter agent live scraper), strictly scoped to current_user
    try:
        from app.models.graph import GraphNode
        q_graph = select(GraphNode.id, GraphNode.properties, GraphNode.created_at).filter(GraphNode.entity_type == "APPLICATION", GraphNode.properties["user_id"].astext == str(current_user.id)).order_by(GraphNode.created_at.desc()).limit(50)
        res_graph = await session.execute(q_graph)
        graph_rows = res_graph.all()

        existing_ids = {a["id"] for a in app_list}
        for g_id_val, g_props, g_created_at in graph_rows:
            props = g_props or {}
            # Legacy nodes without an explicit owner must not be exposed to every user.
            node_user_id = props.get("user_id")
            if str(node_user_id) != str(current_user.id):
                continue
            g_id = props.get("id") or g_id_val
            if g_id not in existing_ids:
                app_list.append({
                    "id": str(g_id),
                    "company": props.get("company", "Target Company"),
                    "role": props.get("role", "Target Role"),
                    "status": props.get("status", "UNKNOWN"),
                    "logs": props.get("logs", ["Application pipeline active."]),
                    "tailored_resume": props.get("tailored_resume", ""),
                    "created_at": g_created_at.isoformat() if g_created_at else None,
                    "applied_at": props.get("applied_at"),
                    "submitted_at": props.get("submitted_at"),
                    "ats_score": props.get("ats_score"),
                })
                existing_ids.add(g_id)
    except Exception as g_err:
        logger.warning(f"Error fetching GraphNode application entities: {g_err}")

    return app_list


@router.get("/analytics", status_code=status.HTTP_200_OK)
async def get_analytics_endpoint(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    return await ApplicationAnalyticsService.get_analytics(session=session, user=current_user)


@router.get("/skill-gaps", status_code=status.HTTP_200_OK)
async def get_market_skill_gaps_endpoint(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> List[dict]:
    return await ApplicationAnalyticsService.get_market_skill_gaps(session=session, user=current_user)


# ── Portal Vault & Browser Session Endpoints (Static Paths before /{app_id}) ─

@router.post("/launch-session", status_code=status.HTTP_200_OK)
async def launch_session_endpoint(payload: dict, current_user: User = Depends(get_desktop_operator)):
    """
    Launches a headful Playwright browser session for candidate manual login/OTP/Captcha solving.
    """
    portal = payload.get("portal", "general")
    try:
        from app.services.browser_automation import BrowserAutomationService
        asyncio.create_task(BrowserAutomationService.launch_headful_session(portal))
        return {"status": "ok", "message": f"Headful browser window launching for {portal}"}
    except Exception as e:
        logger.error(f"Failed to launch browser session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/credentials", status_code=status.HTTP_200_OK)
async def save_credentials_endpoint(
    payload: dict,
    current_user: User = Depends(get_desktop_operator),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Encrypts and stores portal login credentials in the Graph Vault.
    """
    from app.services.credential_vault import CredentialVault
    portal = payload.get("portal")
    username = payload.get("username")
    password = payload.get("password")
    if not portal or not username or not password:
        raise HTTPException(status_code=400, detail="portal, username, and password are required")

    clean_portal = portal.lower().strip()
    await CredentialVault.save_portal_credentials(session, clean_portal, username, password)
    return {"status": "ok", "message": f"Credentials stored for {portal}"}


@router.get("/credentials", status_code=status.HTTP_200_OK)
async def get_credentials_endpoint(
    current_user: User = Depends(get_desktop_operator),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Lists stored portal usernames and session active states for frontend status mapping.
    """
    from app.services.credential_vault import CredentialVault
    from app.services.browser.browser_manager import BrowserManager

    usernames = await CredentialVault.get_all_stored_usernames(session)
    
    portals = ['linkedin', 'indeed', 'naukri', 'foundit', 'shine', 'timesjobs', 'internshala', 'wellfound', 'glassdoor', 'apna', 'workindia', 'hired', 'cutshort', 'instahyre', 'placementindia', 'freshersworld', 'freejobalert', 'firstjob', 'upwork']
    sessions = {p: BrowserManager.check_session_active(p) for p in portals}

    clean_creds = {}
    for k, v in usernames.items():
        clean_key = k.lower().strip()
        clean_creds[clean_key] = v

    return {
        "credentials": usernames,
        "sessions": sessions
    }


@router.get("/browser-status", status_code=status.HTTP_200_OK)
async def get_browser_status_endpoint(current_user: User = Depends(get_desktop_operator)):
    """
    Returns empirical backend Playwright browser context connection status and profile states.
    """
    from app.services.browser_automation import BrowserAutomationService
    return BrowserAutomationService.get_browser_status()


@router.post("/verify-login", status_code=status.HTTP_200_OK)
async def verify_login_endpoint(payload: dict = None, current_user: User = Depends(get_desktop_operator)):
    """
    Re-checks authentication status inside active headful browser window when candidate clicks 'I HAVE LOGGED IN'.
    """
    portal = payload.get("portal", "linkedin") if payload else "linkedin"
    from app.services.browser_automation import BrowserAutomationService
    return await BrowserAutomationService.verify_active_session_login(portal)


@router.post("/apply", status_code=status.HTTP_200_OK)
async def apply_single_portal_endpoint(
    payload: dict,
    current_user: User = Depends(get_desktop_operator),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Prepares a candidate-owned record for the manual portal workflow.
    """
    company = payload.get("company")
    role = payload.get("role")
    portal_url = payload.get("portal_url")
    if not company or not role or not portal_url:
        raise HTTPException(status_code=400, detail="company, role, and portal_url are required")

    from app.services.browser_automation import BrowserAutomationService
    application_id = await BrowserAutomationService.run_auto_apply(
        session=session,
        user_id=str(current_user.id),
        company=company,
        role=role,
        portal_url=portal_url,
        optimized_resume_path="",
    )
    return {
        "status": "READY_TO_SUBMIT",
        "message": "Application record prepared. Employer submission has not occurred.",
        "application_id": application_id,
    }


@router.post("/autonomous-run", status_code=status.HTTP_200_OK)
async def autonomous_run_endpoint(
    payload: dict,
    current_user: User = Depends(get_desktop_operator),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Rejects the legacy sample feed until it is replaced with verified listings.
    """
    raise HTTPException(
        status_code=409,
        detail="The legacy autonomous feed contains sample listings. Use verified job discovery and approve each application.",
    )


@router.post("/sync-email", status_code=status.HTTP_200_OK)
async def sync_email_endpoint(
    payload: dict = None,
    current_user: User = Depends(get_desktop_operator),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Syncs employer confirmation emails & response status updates via live IMAP or simulation.
    """
    payload_dict = payload or {}
    email_address = payload_dict.get("email_address")
    app_password = payload_dict.get("app_password")
    company = payload_dict.get("company")

    try:
        from app.services.email_service import EmailSyncService
        synced = await EmailSyncService.sync_confirmation_emails(
            session=session,
            user_id=str(current_user.id),
            email_address=email_address,
            app_password=app_password,
            company_filter=company
        )
        return {
            "status": "ok",
            "verified": len(synced) > 0,
            "message": f"Successfully synced {len(synced)} employer confirmation emails",
            "synced_count": len(synced),
            "emails_matched": len(synced),
            "emails": synced
        }
    except Exception as e:
        logger.error(f"Email sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-emails", status_code=status.HTTP_200_OK)
async def sync_emails_alias_endpoint(
    payload: dict = None,
    current_user: User = Depends(get_desktop_operator),
    session: AsyncSession = Depends(get_db_session)
):
    return await sync_email_endpoint(payload=payload, current_user=current_user, session=session)


@router.post("/emergency-stop", status_code=status.HTTP_200_OK)
async def emergency_stop_applications_endpoint(
    payload: dict = None,
    current_user: User = Depends(get_desktop_operator),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Emergency Stop trigger for all active application automation runs.
    """
    reason = payload.get("reason") if payload else "User activated Emergency Stop"
    from app.services.job_scheduler import JobScheduler
    from app.services.browser_automation import BrowserAutomationService
    BrowserAutomationService.set_emergency_stop(True)
    return await JobScheduler.set_emergency_stop(session, current_user, reason=reason)


@router.post("/{app_id}/verify-email", status_code=status.HTTP_200_OK)
async def verify_application_email_endpoint(
    app_id: str,
    current_user: User = Depends(get_desktop_operator),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Checks mailbox specifically for confirmation matching a single target application.
    """
    from app.models.graph import GraphNode
    from app.services.email_service import EmailSyncService
    
    node_id = f"application:{app_id}" if not app_id.startswith("application:") else app_id
    res = await session.execute(select(GraphNode).filter(GraphNode.id == node_id))
    node = res.scalar_one_or_none()
    if not node or str((node.properties or {}).get("user_id")) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Application record not found")
        
    synced = await EmailSyncService.sync_confirmation_emails(
        session=session,
        user_id=str(current_user.id)
    )
    
    props = dict(node.properties) if node.properties else {}
    email_status = props.get("email_confirmation_status", "UNKNOWN")
    
    return {
        "status": "ok",
        "application_id": app_id,
        "email_confirmation_status": email_status,
        "synced_count": len(synced)
    }


@router.get("/{app_id}", status_code=status.HTTP_200_OK)
async def get_application_detail_endpoint(
    app_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    from app.models.graph import GraphNode
    raw_id = app_id.removeprefix("application:")
    try:
        a_uuid = uuid.UUID(raw_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid application ID format.")

    res = await session.execute(
        select(Application).filter(Application.id == a_uuid, Application.user_id == current_user.id)
    )
    a = res.scalars().first()
    if not a:
        graph_res = await session.execute(select(GraphNode).filter(
            GraphNode.id == f"application:{raw_id}",
            GraphNode.entity_type == "APPLICATION",
            GraphNode.properties["user_id"].astext == str(current_user.id),
        ))
        node = graph_res.scalars().first()
        if not node or str((node.properties or {}).get("user_id")) != str(current_user.id):
            raise HTTPException(status_code=404, detail="Application record not found or access denied.")
        props = node.properties or {}
        return {
            "id": raw_id, "company": props.get("company"), "role": props.get("role"),
            "status": props.get("status", "UNKNOWN"), "logs": props.get("logs", []),
            "created_at": node.created_at.isoformat() if node.created_at else None,
            "submitted_at": props.get("submitted_at"),
            "email_confirmation_status": props.get("email_confirmation_status", "UNKNOWN"),
        }

    return {
        "id": str(a.id),
        "user_id": str(a.user_id),
        "job_posting_id": str(a.job_posting_id),
        "tailored_resume_id": str(a.tailored_resume_id) if a.tailored_resume_id else None,
        "communication_bundle_id": a.communication_bundle_id,
        "status": a.status,
        "application_stage": a.application_stage,
        "source": a.source,
        "source_url": a.source_url,
        "application_url": a.application_url,
        "company": a.company,
        "role": a.role,
        "location": a.location,
        "job_fit_score": a.job_fit_score,
        "ats_score": a.ats_score,
        "priority_score": a.priority_score,
        "missing_skills": a.missing_skills or {},
        "application_payload": a.application_payload or {},
        "submission_metadata": a.submission_metadata or {},
        "risk_status": a.risk_status,
        "risk_flags": a.risk_flags or {},
        "created_at": a.created_at.isoformat(),
        "submitted_at": a.submitted_at.isoformat() if a.submitted_at else None,
    }


@router.post("/{app_id}/prepare", status_code=status.HTTP_200_OK)
async def prepare_package_endpoint(
    app_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    try:
        return await ApplicationService.prepare_package(session=session, user=current_user, application_id=app_id)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.post("/{app_id}/approve", status_code=status.HTTP_200_OK)
async def approve_package_endpoint(
    app_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    try:
        return await ApplicationService.approve_package(session=session, user=current_user, application_id=app_id)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.post("/{app_id}/start", status_code=status.HTTP_200_OK)
async def start_automation_endpoint(
    app_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    try:
        return await ApplicationService.start_automation(session=session, user=current_user, application_id=app_id)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.post("/{app_id}/final-submit", status_code=status.HTTP_200_OK)
async def final_submit_endpoint(
    app_id: str,
    payload: dict,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    token = payload.get("final_approval_token")
    if not token:
        raise HTTPException(status_code=400, detail="final_approval_token is required for explicit final submission approval.")

    try:
        return await ApplicationService.final_submit(
            session=session, user=current_user, application_id=app_id, final_approval_token=token
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.get("/{app_id}/events", status_code=status.HTTP_200_OK)
async def get_application_events_endpoint(
    app_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> List[dict]:
    try:
        a_uuid = uuid.UUID(app_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid application ID format.")

    res = await session.execute(
        select(Application).filter(Application.id == a_uuid, Application.user_id == current_user.id)
    )
    if not res.scalars().first():
        raise HTTPException(status_code=404, detail="Application record not found or access denied.")

    h_res = await session.execute(
        select(ApplicationStatusHistory).filter(ApplicationStatusHistory.application_id == a_uuid).order_by(ApplicationStatusHistory.created_at.desc())
    )
    events = h_res.scalars().all()

    return [
        {
            "id": str(e.id),
            "event_type": e.event_type,
            "from_status": e.from_status,
            "to_status": e.to_status,
            "metadata": e.metadata_json or {},
            "created_at": e.created_at.isoformat(),
        }
        for e in events
    ]


@router.delete("/{app_id}", status_code=status.HTTP_200_OK)
async def delete_application_endpoint(
    app_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    try:
        a_uuid = uuid.UUID(app_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid application ID format.")

    res = await session.execute(
        select(Application).filter(Application.id == a_uuid, Application.user_id == current_user.id)
    )
    app_entity = res.scalars().first()
    if not app_entity:
        raise HTTPException(status_code=404, detail="Application record not found or access denied.")

    await session.delete(app_entity)
    await session.commit()

    return {"status": "ok", "message": "Application record deleted successfully", "id": app_id}

