import logging
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.core.security import verify_token_subject
from app.core.exceptions import AuthenticationError, PermissionDenied
from app.repositories.user_repository import UserRepository
from app.models.user import User, UserRole

logger = logging.getLogger("app.core.dependencies")

def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    """
    Dependency returning an active instance of the UserRepository class.
    """
    return UserRepository(session)

async def get_current_user(
    token_subject: str = Depends(verify_token_subject),
    user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    """
    Dependency resolving the active authenticated user object from valid JWT token.
    Raises HTTP 401 Unauthorized if token is invalid, expired, or missing.
    """
    from uuid import UUID
    from fastapi import HTTPException, status
    try:
        user_id = UUID(token_subject)
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(status_code=401, detail="Invalid user identity", headers={"WWW-Authenticate": "Bearer"})
    user = await user_repo.get_by_id(user_id)
    if not user or not user.is_active or user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User identity is unavailable",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_desktop_operator(current_user: User = Depends(get_current_user)) -> User:
    """Limit shared browser profiles and inbox credentials to their configured owner."""
    from app.core.config import settings
    if settings.DESKTOP_OPERATOR_USER_ID != current_user.id:
        raise PermissionDenied("Desktop automation is available only to the configured operator.")
    return current_user


class RoleChecker:
    """
    Role verification dependency checking if the user holds required access permissions.
    """
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        logger.info(f"RoleChecker: checking user role: {current_user.role} against allowed: {self.allowed_roles}")
        if current_user.role not in self.allowed_roles:
            logger.warning(f"User ID: {current_user.id} role: {current_user.role} denied access.")
            raise PermissionDenied("Insufficient permissions to access this resource.")
        return current_user
