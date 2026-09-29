"""
JobPilot REST API Router — Part 6 Autonomous Discovery, Intelligence & Pipeline Control.
"""
import logging
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencies import get_current_user, get_desktop_operator
from app.models.user import User
from app.models.job import JobPosting
from app.models.job_discovery import JobPipelineControl, SkillGapAggregate
from app.services.job_discovery_service import JobDiscoveryService
from app.services.job_scoring_service import JobScoringService
from app.services.skill_gap_service import SkillGapService
from app.services.job_orchestrator import JobOrchestrator
from app.services.job_scheduler import JobScheduler
from app.services.career_learning_loop import CareerLearningLoop

logger = logging.getLogger("app.api.jobpilot")
router = APIRouter(prefix="/jobpilot", tags=["JobPilot Engine"])


@router.post("/discover", status_code=status.HTTP_200_OK)
async def discover_jobs_endpoint(
    payload: dict,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    query = payload.get("query", "Software Engineer")
    sources = payload.get("sources", ["mock"])
    max_jobs = payload.get("max_jobs", 10)
    return await JobDiscoveryService.run_discovery(session, current_user, query, sources, max_jobs)


@router.get("/recommendations", status_code=status.HTTP_200_OK)
async def get_recommendations_endpoint(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> List[dict]:
    res = await session.execute(
        select(JobPosting).order_by(JobPosting.created_at.desc()).limit(20)
    )
    jobs = res.scalars().all()

    recs = []
    for j in jobs:
        gaps = await SkillGapService.evaluate_job_skill_gaps(session, current_user, j)
        scores = JobScoringService.calculate_explainable_score(
            skill_match_score=min(100.0, (gaps["matched_count"] / max(gaps["matched_count"] + gaps["missing_required_count"], 1)) * 100.0),
            experience_fit_score=85.0,
            career_fit_score=90.0,
            ats_match_score=85.0,
            matched_skills=gaps["matched_skills"],
            missing_skills=gaps["missing_required_skills"],
        )
        recs.append({
            "id": str(j.id),
            "title": j.title,
            "company": j.company,
            "location": j.location,
            "work_mode": j.work_mode,
            "priority_score": scores["final_priority_score"],
            "priority_level": scores["priority_level"],
            "matched_skills": gaps["matched_skills"],
            "missing_skills": gaps["missing_required_skills"],
            "explanation": scores["explanation"],
        })
    return recs


@router.get("/skill-gaps/top", status_code=status.HTTP_200_OK)
async def get_top_skill_gaps_endpoint(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> List[dict]:
    return await SkillGapService.aggregate_market_skill_gaps(session, current_user)


@router.post("/run", status_code=status.HTTP_200_OK)
async def run_pipeline_endpoint(
    payload: dict,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    query = payload.get("query", "Backend Engineer")
    target_limit = payload.get("limit", 10)
    return await JobScheduler.run_daily_pipeline(session, current_user, query, target_limit)


@router.post("/pause", status_code=status.HTTP_200_OK)
async def pause_pipeline_endpoint(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    return await JobScheduler.set_pause_state(session, current_user, is_paused=True)


@router.post("/resume", status_code=status.HTTP_200_OK)
async def resume_pipeline_endpoint(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    return await JobScheduler.set_pause_state(session, current_user, is_paused=False)


@router.post("/emergency-stop", status_code=status.HTTP_200_OK)
async def emergency_stop_endpoint(
    payload: dict = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    reason = payload.get("reason") if payload else "User activated Emergency Stop"
    return await JobScheduler.set_emergency_stop(session, current_user, reason=reason)


@router.post("/agent-command", status_code=status.HTTP_200_OK)
async def voice_agent_command_endpoint(
    payload: dict,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """Compatibility endpoint for the bounded, per-account assistant."""
    from app.services.career_assistant import CareerAssistant, ChatRequest
    from pydantic import ValidationError
    try:
        request = ChatRequest(message=payload.get("command") or payload.get("prompt") or "")
    except ValidationError:
        raise HTTPException(422, "Provide an instruction between 1 and 2000 characters.")
    result = await CareerAssistant.run(request, session, current_user)
    return {**result, "agent_reply": result["reply"], "logs": [step["summary"] for step in result["steps"]]}


@router.get("/dashboard", status_code=status.HTTP_200_OK)
async def get_dashboard_endpoint(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    ctrl = await JobScheduler.get_or_create_control(session, current_user)
    funnel = await CareerLearningLoop.analyze_conversion_funnel(session, current_user)
    skill_gaps = await SkillGapService.aggregate_market_skill_gaps(session, current_user)
    recs = await CareerLearningLoop.generate_career_recommendations(session, current_user)

    return {
        "pipeline_control": {
            "daily_limit": ctrl.daily_processing_limit,
            "is_paused": ctrl.is_paused,
            "is_emergency_stopped": ctrl.is_emergency_stopped,
            "emergency_stopped_at": ctrl.emergency_stopped_at.isoformat() if ctrl.emergency_stopped_at else None,
        },
        "conversion_funnel": funnel,
        "top_skill_gaps": skill_gaps[:5],
        "career_recommendations": recs,
    }
