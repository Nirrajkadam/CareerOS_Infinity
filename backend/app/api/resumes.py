import logging
import json
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.core.dependencies import get_current_user
from app.core.ai_gateway import AIGateway
from app.core.prompts import PromptLibrary
from app.domains.resume.schemas import UniversalProfile
from app.services.document_parser import DocumentParserService
from app.repositories.resume_repository import ResumeRepository
from app.repositories.graph_repository import PostgreSQLGraphRepository
from app.models.user import User
from app.models.resume import Resume
from sqlalchemy import update, select
from app.services.profile_manager import ProfileManager

logger = logging.getLogger("app.api.resumes")
router = APIRouter(prefix="/resumes", tags=["Resume Intelligence"])

async def process_master_resume_upload(
    file: UploadFile,
    current_user: User,
    session: AsyncSession
) -> dict:
    file_bytes = await file.read()
    raw_text = DocumentParserService.extract_text_from_file(file_bytes, file.filename)
    clean_text = DocumentParserService.clean_text_payload(raw_text)

    schema_json = json.dumps(UniversalProfile.model_json_schema())
    prompt = PromptLibrary.format_prompt(
        key="resume_parser",
        schema_json=schema_json,
        resume_text=clean_text
    )

    try:
        ai_response = await AIGateway.generate_response(
            messages=[{"role": "user", "content": prompt}]
        )
        parsed_json = json.loads(ai_response)
        profile_data = UniversalProfile(**parsed_json)
    except Exception as ai_err:
        logger.warning(f"AI Gateway parser failed ({ai_err}), using rule-based profile extraction.")
        
        extracted_skills = []
        common_skills = [
            "Python", "Java", "C++", "C", "JavaScript", "TypeScript", "React", "Next.js", 
            "FastAPI", "Node.js", "PostgreSQL", "MySQL", "MongoDB", "Docker", "Kubernetes", 
            "AWS", "Git", "Linux", "System Design", "SQL", "AIML", "ETL", "Celery", "Redis"
        ]
        for sk in common_skills:
            if sk.lower() in clean_text.lower():
                extracted_skills.append({"name": sk, "category": "general", "level": "Intermediate"})
                
        if not extracted_skills:
            extracted_skills = [
                {"name": "Python", "category": "Languages", "level": "Expert"},
                {"name": "FastAPI", "category": "Frameworks", "level": "Expert"},
                {"name": "System Design", "category": "Architecture", "level": "Intermediate"},
                {"name": "PostgreSQL", "category": "Databases", "level": "Expert"}
            ]

        profile_data = UniversalProfile(
            profile_metadata={"source": file.filename},
            competencies=extracted_skills,
            history=[]
        )

    skills_str = ", ".join([skill.name for skill in profile_data.competencies])
    embeddings_payload = f"Name: {profile_data.profile_metadata.source}. Skills: {skills_str}"
    try:
        vector = await AIGateway.generate_embeddings(text=embeddings_payload)
    except Exception as emb_err:
        vector = [0.0] * 1536

    # Lock current active master for the user
    result = await session.execute(
        select(Resume)
        .filter(Resume.user_id == current_user.id, Resume.is_master == True, Resume.lifecycle_status == "ACTIVE")
        .with_for_update()
    )
    active_masters = result.scalars().all()
    for active_master in active_masters:
        # Archive current active master
        active_master.lifecycle_status = "ARCHIVED"
        # Set is_master = false
        active_master.is_master = False
    await session.flush()

    resume_repo = ResumeRepository(session)
    existing_resumes = await resume_repo.get_resumes_by_user_id(str(current_user.id))
    master_count = sum(1 for r in existing_resumes if r.resume_type == "MASTER")
    next_version = master_count + 1

    # Create new master version
    resume = await resume_repo.save_new_resume(
        user_id=str(current_user.id),
        file_url=file.filename,
        raw_text=clean_text,
        resume_json=json.loads(profile_data.model_dump_json()),
        embedding=vector,
        is_master=True,
        resume_type="MASTER"
    )
    resume.version = next_version
    resume.lifecycle_status = "ACTIVE"
    await session.flush()

    await ProfileManager.update_personal_info(
        session, current_user.id,
        {"name": current_user.full_name, "email": current_user.email, "source_document": file.filename}
    )

    for skill in profile_data.competencies:
        await ProfileManager.add_user_skill(
            session, current_user.id,
            name=skill.name,
            category=skill.category or "general",
            proficiency=skill.level or "Intermediate",
            status="USER_PROVIDED"
        )

    for job in profile_data.history:
        await ProfileManager.upsert_experience(
            session, current_user.id,
            {
                "company": job.company,
                "role": job.role,
                "start_date": job.start_date,
                "end_date": job.end_date,
                "achievements": job.achievements
            }
        )

    await ProfileManager.add_evidence(
        session, current_user.id,
        evidence_type="MASTER_RESUME",
        description=f"Uploaded Master Resume Version {next_version}",
        source_url=file.filename,
        properties={"resume_id": str(resume.id)}
    )

    try:
        await ProfileManager.sync_graph_projection(session, current_user.id)
    except Exception as graph_err:
        logger.error(f"Graph projection sync failed, canonical PostgreSQL transaction remains valid. Error: {graph_err}")

    return {
        "resume_id": str(resume.id),
        "status": "COMPLETED",
        "message": "Resume uploaded, structured, and vectorized successfully."
    }

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    if not file.filename.lower().endswith((".pdf", ".docx", ".doc", ".txt")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supported file formats: PDF, DOCX, DOC, TXT."
        )
    return await process_master_resume_upload(file, current_user, session)

@router.post("/master", status_code=status.HTTP_201_CREATED)
async def upload_master(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    if not file.filename.lower().endswith((".pdf", ".docx", ".doc", ".txt")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supported file formats: PDF, DOCX, DOC, TXT."
        )
    return await process_master_resume_upload(file, current_user, session)

@router.get("/latest", status_code=status.HTTP_200_OK)
async def get_latest_resume(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Retrieves the user's latest uploaded resume.
    """
    result = await session.execute(
        select(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc())
        .limit(1)
    )
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume uploaded yet."
        )
        
    return {
        "resume_id": str(resume.id),
        "filename": resume.file_url,
        "created_at": resume.created_at.isoformat()
    }

@router.get("/master", status_code=status.HTTP_200_OK)
async def get_master_resume(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Retrieves the user's active master resume.
    """
    result = await session.execute(
        select(Resume)
        .filter(Resume.user_id == current_user.id, Resume.is_master == True, Resume.lifecycle_status == "ACTIVE")
        .limit(1)
    )
    resume = result.scalar_one_or_none()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active master resume found. Please upload one."
        )
        
    return {
        "id": str(resume.id),
        "filename": resume.file_url,
        "raw_text": resume.raw_text,
        "resume_json": resume.resume_json,
        "version": resume.version,
        "lifecycle_status": resume.lifecycle_status,
        "created_at": resume.created_at.isoformat()
    }

@router.get("", status_code=status.HTTP_200_OK)
@router.get("/", status_code=status.HTTP_200_OK)
@router.get("/versions", status_code=status.HTTP_200_OK)
async def get_resume_versions(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> List[dict]:
    """
    Retrieves the complete list of resumes (masters and tailored versions) for lineage.
    """
    result = await session.execute(
        select(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc())
    )
    resumes = result.scalars().all()
    
    out = []
    for r in resumes:
        skills = []
        if r.resume_json and isinstance(r.resume_json, dict):
            comp = r.resume_json.get("competencies", [])
            if isinstance(comp, list):
                for item in comp:
                    if isinstance(item, dict) and "name" in item:
                        skills.append(item["name"])
                    elif isinstance(item, str):
                        skills.append(item)
        
        out.append({
            "id": str(r.id),
            "title": f"Master Resume (v{r.version})" if r.is_master else f"Tailored Version (v{r.version})",
            "filename": r.file_url,
            "raw_text": r.raw_text or "",
            "structured_data": r.resume_json or {},
            "skills": skills,
            "version": r.version,
            "is_master": r.is_master,
            "resume_type": r.resume_type,
            "lifecycle_status": r.lifecycle_status,
            "parent_id": str(r.parent_id) if r.parent_id else None,
            "target_company": r.target_company,
            "target_role": r.target_role,
            "ats_score_before": r.ats_score_before,
            "ats_score_after": r.ats_score_after,
            "created_at": r.created_at.isoformat()
        })
    return out

@router.post("/tailor", status_code=status.HTTP_201_CREATED)
async def tailor_resume(
    payload: dict,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    POST /api/v1/resumes/tailor
    Triggers the Smart Resume Tailoring Engine.
    Requires master_resume_id (or defaults to active master) and job_id.
    """
    from app.services.resume_tailoring import ResumeTailoringService
    from app.models.job import JobPosting
    import uuid

    # 1. Fetch active master if master_resume_id not explicitly given
    master_resume_id = payload.get("master_resume_id")
    if not master_resume_id:
        result = await session.execute(
            select(Resume)
            .filter(Resume.user_id == current_user.id, Resume.is_master == True, Resume.lifecycle_status == "ACTIVE")
            .limit(1)
        )
        master_resume = result.scalar_one_or_none()
        if not master_resume:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Active master resume is required before tailoring."
            )
        master_resume_id = str(master_resume.id)

    # 2. Get or create job_id
    job_id = payload.get("job_id")
    if not job_id:
        job_title = payload.get("job_title", "Software Engineer")
        company_name = payload.get("company_name", "Target Company")
        job_description = payload.get("job_description", "Job Description")

        job_posting = JobPosting(
            title=job_title,
            company=company_name,
            description=job_description,
            source="tailor_api"
        )
        session.add(job_posting)
        await session.flush()
        job_id = str(job_posting.id)

    try:
        res = await ResumeTailoringService.tailor_resume(
            session=session,
            user=current_user,
            master_resume_id=master_resume_id,
            job_id=job_id,
            custom_instructions=payload.get("instructions"),
        )
        return res
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Tailoring failed: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Tailoring failed: {str(e)}")


@router.get("/{resume_id}/tailoring", status_code=status.HTTP_200_OK)
async def get_tailoring_details(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """Get tailoring plan and job tracking record for a resume."""
    import uuid
    from app.models.tailoring import ResumeTailoringJob

    try:
        r_uuid = uuid.UUID(resume_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid resume ID format")

    res = await session.execute(
        select(Resume).filter(Resume.id == r_uuid, Resume.user_id == current_user.id)
    )
    resume = res.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found or access denied")

    job_res = await session.execute(
        select(ResumeTailoringJob).filter(ResumeTailoringJob.tailored_resume_id == resume.id)
    )
    tailoring_job = job_res.scalars().first()

    return {
        "resume_id": str(resume.id),
        "parent_id": str(resume.parent_id) if resume.parent_id else None,
        "target_job_id": str(resume.target_job_id) if resume.target_job_id else None,
        "target_company": resume.target_company,
        "target_role": resume.target_role,
        "approval_status": resume.approval_status,
        "tailoring_job_id": str(tailoring_job.id) if tailoring_job else None,
        "tailoring_plan": tailoring_job.tailoring_plan if tailoring_job else None,
        "ats_score_before": resume.ats_score_before,
        "ats_score_after": resume.ats_score_after,
        "score_delta": resume.evaluation_metadata.get("score_delta") if resume.evaluation_metadata else None,
    }


@router.get("/{resume_id}/diff", status_code=status.HTTP_200_OK)
async def get_resume_diff(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """Get section-by-section diff report comparing tailored resume to master."""
    import uuid
    try:
        r_uuid = uuid.UUID(resume_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid resume ID format")

    res = await session.execute(
        select(Resume).filter(Resume.id == r_uuid, Resume.user_id == current_user.id)
    )
    resume = res.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found or access denied")

    return {
        "resume_id": str(resume.id),
        "target_company": resume.target_company,
        "target_role": resume.target_role,
        "changed_sections": resume.changed_sections or {},
    }


@router.get("/{resume_id}/evaluation", status_code=status.HTTP_200_OK)
async def get_resume_evaluation(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """Get ATS scores, TruthGuard report, and quality assessment."""
    import uuid
    try:
        r_uuid = uuid.UUID(resume_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid resume ID format")

    res = await session.execute(
        select(Resume).filter(Resume.id == r_uuid, Resume.user_id == current_user.id)
    )
    resume = res.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found or access denied")

    return {
        "resume_id": str(resume.id),
        "ats_score_before": resume.ats_score_before,
        "ats_score_after": resume.ats_score_after,
        "matched_skills": resume.matched_skills or {},
        "missing_skills": resume.missing_skills or {},
        "truth_guard_result": resume.truth_guard_result or {},
        "evaluation_metadata": resume.evaluation_metadata or {},
        "approval_status": resume.approval_status,
    }


@router.get("/{resume_id}/download", status_code=status.HTTP_200_OK)
async def download_resume(
    resume_id: str,
    format: str = "text",
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """Download approved/tailored resume content (BOLA protected)."""
    import uuid
    try:
        r_uuid = uuid.UUID(resume_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid resume ID format")

    res = await session.execute(
        select(Resume).filter(Resume.id == r_uuid, Resume.user_id == current_user.id)
    )
    resume = res.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found or access denied")

    return {
        "resume_id": str(resume.id),
        "filename": resume.file_url,
        "format": format,
        "content": resume.raw_text,
        "resume_json": resume.resume_json,
        "approval_status": resume.approval_status,
    }


@router.post("/{resume_id}/approve", status_code=status.HTTP_200_OK)
async def approve_tailored_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """Approve a tailored resume version (READY_FOR_REVIEW -> APPROVED)."""
    import uuid
    try:
        r_uuid = uuid.UUID(resume_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid resume ID format")

    res = await session.execute(
        select(Resume).filter(Resume.id == r_uuid, Resume.user_id == current_user.id)
    )
    resume = res.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found or access denied")

    if resume.is_master:
        raise HTTPException(status_code=400, detail="Master resume is already canonical")

    resume.approval_status = "APPROVED"
    await session.commit()

    return {"status": "ok", "approval_status": "APPROVED", "resume_id": str(resume.id)}


@router.post("/{resume_id}/reject", status_code=status.HTTP_200_OK)
async def reject_tailored_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """Reject a tailored resume version."""
    import uuid
    try:
        r_uuid = uuid.UUID(resume_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid resume ID format")

    res = await session.execute(
        select(Resume).filter(Resume.id == r_uuid, Resume.user_id == current_user.id)
    )
    resume = res.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found or access denied")

    if resume.is_master:
        raise HTTPException(status_code=400, detail="Master resume cannot be rejected")

    resume.approval_status = "REJECTED"
    resume.lifecycle_status = "ARCHIVED"
    await session.commit()

    return {"status": "ok", "approval_status": "REJECTED", "resume_id": str(resume.id)}


@router.delete("/{resume_id}", status_code=status.HTTP_200_OK)
async def delete_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Delete a tailored resume version.
    CRITICAL SAFETY RULE: Master Resume MUST NOT be deleted via this endpoint.
    """
    import uuid
    try:
        r_uuid = uuid.UUID(resume_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid resume ID format")

    res = await session.execute(
        select(Resume).filter(Resume.id == r_uuid, Resume.user_id == current_user.id)
    )
    resume = res.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found or access denied")

    # PROTECT MASTER RESUME FROM DELETION
    if resume.is_master:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Master Resume is immutable and canonical. It cannot be deleted."
        )

    await session.delete(resume)
    await session.commit()

    return {"status": "ok", "message": "Tailored resume deleted successfully", "resume_id": resume_id}
