import logging
import uuid as uuid_mod
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import BaseRepository
from app.models.resume import Resume

logger = logging.getLogger("app.repositories.resume_repository")

class ResumeRepository(BaseRepository[Resume]):
    """
    Resume repository executing relational query operations for parsed resumes.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(Resume, session)

    def _to_uuid(self, val):
        if isinstance(val, uuid_mod.UUID):
            return val
        try:
            return uuid_mod.UUID(str(val))
        except (ValueError, TypeError):
            return val

    async def get_resumes_by_user_id(self, user_id) -> List[Resume]:
        uid = self._to_uuid(user_id)
        logger.info(f"ResumeRepository: querying resumes list for user ID: {uid}")
        query = select(Resume).filter(Resume.user_id == uid)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def save_new_resume(
        self,
        user_id,
        file_url: str,
        raw_text: str,
        resume_json: dict,
        embedding: list,
        is_master: bool = False,
        resume_type: str = "TAILORED",
        parent_id = None
    ) -> Resume:
        uid = self._to_uuid(user_id)
        pid = self._to_uuid(parent_id) if parent_id else None
        logger.info(f"ResumeRepository: saving new parsed resume instance for user ID: {uid}")
        resume = Resume(
            user_id=uid,
            file_url=file_url,
            raw_text=raw_text,
            resume_json=resume_json,
            embedding=embedding,
            is_master=is_master,
            resume_type=resume_type,
            parent_id=pid
        )
        self.session.add(resume)
        await self.session.flush()
        return resume
