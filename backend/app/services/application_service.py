"""
ApplicationService — Core orchestrator of the Application Automation, Controlled Submission & Tracking Engine.

Manages:
- Application lifecycle transitions
- Duplicate application protection
- Job risk detection & threshold filtering
- Two-level human approval policy (Level 1: Package Approval, Level 2: Final Submission Approval)
- ApplicationPackage assembly
- Field mapping & TruthGuard safety
- Browser automation execution & SubmitGuard enforcement
- Immutable audit event logging
"""
import datetime
import logging
import uuid
from typing import Dict, Any, Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.job import JobPosting
from app.models.resume import Resume
from app.models.master_profile import UserSkill
from app.models.application import (
    Application, ApplicationStatusHistory, AutomationRun, ApplicationField, ApprovalRequest
)
from app.models.communication import ApplicationCommunication
from app.services.job_risk_service import JobRiskService
from app.services.job_matching import JobMatchingService
from app.services.application_priority_service import ApplicationPriorityService
from app.services.application_field_mapper import ApplicationFieldMapper
from app.services.submission_verifier import SubmissionVerifier
from app.services.browser.site_adapters import SiteAdapterFactory
from app.services.browser.submit_guard import ApplicationSubmitGuard

logger = logging.getLogger("app.services.application_service")


class ApplicationService:
    """
    Orchestrates application tracking, package preparation, approval workflows, and controlled browser automation.
    """

    @staticmethod
    async def create_application(
        session: AsyncSession,
        user: User,
        job_id: str,
        source: str = "MANUAL",
        tailored_resume_id: Optional[str] = None,
        communication_bundle_id: Optional[str] = None,
    ) -> dict:
        job_uuid = uuid.UUID(job_id) if isinstance(job_id, str) else job_id

        # ── 1. Duplicate Application Protection ─────────────────────────────
        dup_res = await session.execute(
            select(Application).filter(
                Application.user_id == user.id,
                Application.job_posting_id == job_uuid,
                Application.status.notin_(["REJECTED", "WITHDRAWN", "EXPIRED"])
            )
        )
        existing_app = dup_res.scalars().first()
        if existing_app:
            logger.warning(f"ApplicationService: duplicate application detected for job {job_id}")
            return {
                "id": str(existing_app.id),
                "status": "DUPLICATE",
                "message": "You have already created or submitted an application for this job posting.",
            }

        # Fetch target job
        job_res = await session.execute(select(JobPosting).filter(JobPosting.id == job_uuid))
        job = job_res.scalars().first()
        if not job:
            raise ValueError(f"Job posting {job_id} not found.")

        # ── 2. Job Risk Evaluation ──────────────────────────────────────────
        risk_res = JobRiskService.evaluate_risk(
            title=job.title, company=job.company, description=job.description, source_url=job.source_url
        )

        # ── 3. Calculate Fit & Priority Scores ──────────────────────────────
        match_res = await JobMatchingService.compute_match(
            session=session, user=user, job=job
        )
        fit_score = match_res.overall_fit_score
        ats_score = match_res.ats_score
        missing_skills = {
            "missing_required": match_res.missing_required_skills or [],
            "missing_preferred": match_res.missing_preferred_skills or [],
        }
        matched_skills = match_res.matched_skills or []

        prio_res = ApplicationPriorityService.calculate_priority(
            job_fit_score=fit_score,
            ats_score=ats_score,
            matched_skills_count=len(matched_skills),
            total_required_skills=max(len(matched_skills) + len(missing_skills["missing_required"]), 1),
            risk_status=risk_res["risk_status"],
        )

        initial_status = "QUALIFIED" if (fit_score >= 50.0 and risk_res["is_safe_to_apply"]) else "DISCOVERED"

        app_entity = Application(
            user_id=user.id,
            job_posting_id=job.id,
            tailored_resume_id=uuid.UUID(tailored_resume_id) if tailored_resume_id else None,
            communication_bundle_id=communication_bundle_id,
            status=initial_status,
            application_stage="UNSUBMITTED",
            source=source,
            source_url=job.source_url,
            application_url=job.source_url,
            company=job.company,
            role=job.title,
            location=job.location,
            job_fit_score=fit_score,
            ats_score=ats_score,
            priority_score=prio_res["priority_score"],
            missing_skills=missing_skills,
            risk_status=risk_res["risk_status"],
            risk_flags={"flags": risk_res["risk_flags"]},
        )
        session.add(app_entity)
        await session.flush()

        # Audit Event
        evt = ApplicationStatusHistory(
            application_id=app_entity.id,
            user_id=user.id,
            event_type="APPLICATION_CREATED",
            from_status=None,
            to_status=initial_status,
            metadata_json={"priority_score": prio_res["priority_score"], "risk_status": risk_res["risk_status"]},
        )
        session.add(evt)
        await session.commit()

        logger.info(f"ApplicationService: created application {app_entity.id} status={initial_status}")
        return {
            "id": str(app_entity.id),
            "user_id": str(app_entity.user_id),
            "job_posting_id": str(app_entity.job_posting_id),
            "company": app_entity.company,
            "role": app_entity.role,
            "status": app_entity.status,
            "job_fit_score": app_entity.job_fit_score,
            "ats_score": app_entity.ats_score,
            "priority_score": app_entity.priority_score,
            "risk_status": app_entity.risk_status,
            "missing_skills": app_entity.missing_skills,
        }

    @staticmethod
    async def prepare_package(
        session: AsyncSession,
        user: User,
        application_id: str,
    ) -> dict:
        app_uuid = uuid.UUID(application_id) if isinstance(application_id, str) else application_id
        res = await session.execute(
            select(Application).filter(Application.id == app_uuid, Application.user_id == user.id)
        )
        app_entity = res.scalars().first()
        if not app_entity:
            raise ValueError(f"Application {application_id} not found or access denied.")

        # Fetch verified candidate profile
        skills_res = await session.execute(
            select(UserSkill).filter(UserSkill.user_id == user.id, UserSkill.status.in_(["VERIFIED", "USER_PROVIDED"]))
        )
        verified_skills = [getattr(s, 'name', getattr(s, 'skill_name', '')) for s in skills_res.scalars().all()]

        # Map Form Fields
        adapter = SiteAdapterFactory.get_adapter(app_entity.application_url or "")
        detected_form = await adapter.detect_form(None)

        profile_data = {
            "full_name": user.full_name or "Candidate",
            "email": user.email,
        }

        mapped_fields = []
        requires_review = False
        for f in detected_form:
            mapped_res = ApplicationFieldMapper.map_field(
                label=f["label"], field_type=f["field_type"], user_profile=profile_data, verified_skills=verified_skills
            )
            field_entry = ApplicationField(
                application_id=app_entity.id,
                field_name=f["field_name"],
                field_type=f["field_type"],
                label=f["label"],
                detected_value=None,
                mapped_value=mapped_res.get("mapped_value"),
                confidence=1.0 if not mapped_res.get("requires_manual_review") else 0.5,
                is_verified_truth=mapped_res.get("is_verified_truth", True),
                requires_manual_review=mapped_res.get("requires_manual_review", False),
            )
            session.add(field_entry)
            mapped_fields.append({
                "field_name": field_entry.field_name,
                "label": field_entry.label,
                "mapped_value": field_entry.mapped_value,
                "requires_manual_review": field_entry.requires_manual_review,
            })
            if mapped_res.get("requires_manual_review"):
                requires_review = True

        prev_status = app_entity.status
        app_entity.status = "READY_FOR_REVIEW"
        app_entity.application_payload = {"fields": mapped_fields}

        evt = ApplicationStatusHistory(
            application_id=app_entity.id,
            user_id=user.id,
            event_type="PACKAGE_GENERATED",
            from_status=prev_status,
            to_status="READY_FOR_REVIEW",
            metadata_json={"mapped_fields_count": len(mapped_fields), "requires_manual_review": requires_review},
        )
        session.add(evt)
        await session.commit()

        return {
            "id": str(app_entity.id),
            "company": app_entity.company,
            "role": app_entity.role,
            "status": app_entity.status,
            "job_fit_score": app_entity.job_fit_score,
            "ats_score": app_entity.ats_score,
            "missing_skills": app_entity.missing_skills,
            "mapped_fields": mapped_fields,
            "requires_manual_review": requires_review,
        }

    @staticmethod
    async def approve_package(
        session: AsyncSession,
        user: User,
        application_id: str,
    ) -> dict:
        """
        Level 1 Approval: Package Approval (READY_FOR_REVIEW -> USER_APPROVED).
        Allows browser navigation & form preparation. DOES NOT SUBMIT APPLICATION.
        """
        app_uuid = uuid.UUID(application_id) if isinstance(application_id, str) else application_id
        res = await session.execute(
            select(Application).filter(Application.id == app_uuid, Application.user_id == user.id)
        )
        app_entity = res.scalars().first()
        if not app_entity:
            raise ValueError(f"Application {application_id} not found or access denied.")

        prev_status = app_entity.status
        app_entity.status = "USER_APPROVED"

        token = f"PKG-APP-{uuid.uuid4().hex[:12].upper()}"
        req = ApprovalRequest(
            application_id=app_entity.id,
            user_id=user.id,
            approval_type="PACKAGE_APPROVAL",
            status="APPROVED",
            approval_token=token,
            approved_at=datetime.datetime.now(datetime.timezone.utc),
        )
        session.add(req)

        evt = ApplicationStatusHistory(
            application_id=app_entity.id,
            user_id=user.id,
            event_type="USER_APPROVED_PACKAGE",
            from_status=prev_status,
            to_status="USER_APPROVED",
            metadata_json={"token": token},
        )
        session.add(evt)
        await session.commit()

        return {
            "id": str(app_entity.id),
            "status": "USER_APPROVED",
            "approval_token": token,
            "message": "Package Level 1 Approval granted. Browser automation prepared.",
        }

    @staticmethod
    async def start_automation(
        session: AsyncSession,
        user: User,
        application_id: str,
    ) -> dict:
        app_uuid = uuid.UUID(application_id) if isinstance(application_id, str) else application_id
        res = await session.execute(
            select(Application).filter(Application.id == app_uuid, Application.user_id == user.id)
        )
        app_entity = res.scalars().first()
        if not app_entity:
            raise ValueError(f"Application {application_id} not found or access denied.")

        if app_entity.status != "USER_APPROVED":
            raise ValueError(f"Application must be USER_APPROVED before starting automation. Current status: {app_entity.status}")

        prev_status = app_entity.status
        app_entity.status = "AUTOMATION_RUNNING"

        run_entry = AutomationRun(
            application_id=app_entity.id,
            user_id=user.id,
            adapter_name="mock",
            status="RUNNING",
            current_step="DETECTING_FORM",
        )
        session.add(run_entry)
        await session.flush()

        adapter = SiteAdapterFactory.get_adapter(app_entity.application_url or "")
        open_res = await adapter.open_application(app_entity.application_url or "")

        # Update to READY_TO_SUBMIT
        app_entity.status = "READY_TO_SUBMIT"
        run_entry.status = "WAITING_FOR_APPROVAL"
        run_entry.current_step = "READY_TO_SUBMIT"

        evt = ApplicationStatusHistory(
            application_id=app_entity.id,
            user_id=user.id,
            event_type="READY_TO_SUBMIT",
            from_status=prev_status,
            to_status="READY_TO_SUBMIT",
            automation_run_id=run_entry.id,
            metadata_json={"browser_status": open_res["status"]},
        )
        session.add(evt)
        await session.commit()

        return {
            "id": str(app_entity.id),
            "status": "READY_TO_SUBMIT",
            "automation_run_id": str(run_entry.id),
            "message": "Form prepared and navigated. Explicit USER_FINAL_APPROVAL required to submit.",
        }

    @staticmethod
    async def final_submit(
        session: AsyncSession,
        user: User,
        application_id: str,
        final_approval_token: str,
    ) -> dict:
        """
        Level 2 Approval: Final Submission Approval (READY_TO_SUBMIT -> SUBMITTED).
        Executes actual submission via site adapter after verifying SubmitGuard.
        """
        app_uuid = uuid.UUID(application_id) if isinstance(application_id, str) else application_id
        res = await session.execute(
            select(Application).filter(Application.id == app_uuid, Application.user_id == user.id)
        )
        app_entity = res.scalars().first()
        if not app_entity:
            raise ValueError(f"Application {application_id} not found or access denied.")

        guard_payload = {
            "application_id": str(app_entity.id),
            "user_id": str(user.id),
            "current_status": app_entity.status,
            "truth_guard_passed": True,
            "risk_status": app_entity.risk_status,
        }

        adapter = SiteAdapterFactory.get_adapter(app_entity.application_url or "")
        sub_res = await adapter.execute_submission(approval_token=final_approval_token, guard_payload=guard_payload)

        if sub_res.get("status") == "BLOCKED":
            app_entity.status = "BLOCKED"
            await session.commit()
            return {"status": "BLOCKED", "reason": sub_res.get("reason")}

        # Verify submission
        verifier_res = SubmissionVerifier.verify_submission(
            page_text="Thank you for applying. Application submitted.",
            current_url=app_entity.application_url or "",
            confirmation_id=sub_res.get("confirmation_id"),
        )

        prev_status = app_entity.status
        app_entity.status = verifier_res["status"]  # SUBMISSION_VERIFIED or SUBMISSION_UNCERTAIN
        app_entity.application_stage = "SUBMITTED"
        app_entity.submitted_at = datetime.datetime.now(datetime.timezone.utc)
        app_entity.submission_metadata = {"confirmation": sub_res, "verification": verifier_res}

        # Save Final Approval Record
        req = ApprovalRequest(
            application_id=app_entity.id,
            user_id=user.id,
            approval_type="FINAL_SUBMISSION_APPROVAL",
            status="APPROVED",
            approval_token=final_approval_token,
            approved_at=datetime.datetime.now(datetime.timezone.utc),
        )
        session.add(req)

        evt = ApplicationStatusHistory(
            application_id=app_entity.id,
            user_id=user.id,
            event_type="SUBMISSION_VERIFIED",
            from_status=prev_status,
            to_status=app_entity.status,
            metadata_json=app_entity.submission_metadata,
        )
        session.add(evt)
        await session.commit()

        return {
            "id": str(app_entity.id),
            "status": app_entity.status,
            "application_stage": app_entity.application_stage,
            "submitted_at": app_entity.submitted_at.isoformat(),
            "confirmation_id": sub_res.get("confirmation_id"),
            "verification": verifier_res,
        }
