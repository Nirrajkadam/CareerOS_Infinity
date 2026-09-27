import logging
import datetime
import uuid
from typing import Optional, Tuple
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.exceptions import AuthenticationError
from app.models.user import User, UserRole
from app.models.auth import RefreshToken
from app.models.audit import AuditLog
from app.repositories.user_repository import UserRepository

logger = logging.getLogger("app.services.auth_service")

class AuthService:
    """
    Identity & Auth service coordinating user registration, credential checks, and token generation.
    """
    @staticmethod
    async def register_user(
        session: AsyncSession,
        email: str,
        password: str,
        full_name: Optional[str] = None
    ) -> User:
        logger.info(f"AuthService: attempting registration for email: {email}")
        user_repo = UserRepository(session)
        
        # Check if email is already taken
        existing_user = await user_repo.get_by_email(email)
        if existing_user:
            logger.warning(f"Registration failed, email already taken: {email}")
            raise AuthenticationError("Email already registered.")
            
        hashed = get_password_hash(password)
        new_user = User(
            email=email,
            hashed_password=hashed,
            full_name=full_name,
            role=UserRole.MEMBER
        )
        await user_repo.create(new_user)
        logger.info(f"AuthService: user registered successfully with ID: {new_user.id}")
        return new_user

    @staticmethod
    async def authenticate_user(
        session: AsyncSession,
        email: str,
        password: str
    ) -> Tuple[User, str]:
        logger.info(f"AuthService: authenticating user email: {email}")
        user_repo = UserRepository(session)
        user = await user_repo.get_by_email(email)
        
        if not user or not user.is_active or user.is_deleted or not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed for email: {email}")
            raise AuthenticationError("Incorrect email or password.")
            
        # Generate token
        token = create_access_token(subject=str(user.id))
        return user, token

    @staticmethod
    async def create_session_refresh_token(
        session: AsyncSession,
        user_id: uuid.UUID
    ) -> str:
        logger.info(f"AuthService: creating refresh token for user ID: {user_id}")
        token_str = str(uuid.uuid4())
        expires = datetime.datetime.utcnow() + datetime.timedelta(days=30)
        
        ref_token = RefreshToken(
            user_id=user_id,
            token=token_str,
            expires_at=expires
        )
        session.add(ref_token)
        await session.flush()
        return token_str

    @staticmethod
    async def refresh_access_session(
        session: AsyncSession,
        token_str: str
    ) -> str:
        logger.info("AuthService: attempting refresh session with token.")
        query = select(RefreshToken).filter(
            RefreshToken.token == token_str,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.datetime.utcnow()
        )
        result = await session.execute(query)
        ref_token = result.scalars().first()
        
        if not ref_token:
            logger.warning("Session refresh failed: invalid or expired refresh token.")
            raise AuthenticationError("Invalid or expired session refresh token.")
            
        user = await UserRepository(session).get_by_id(ref_token.user_id)
        if not user or not user.is_active or user.is_deleted:
            raise AuthenticationError("User identity is unavailable.")

        # Issue new access token
        access_token = create_access_token(subject=str(ref_token.user_id))
        return access_token

    @staticmethod
    async def revoke_refresh_token(session: AsyncSession, token_str: str) -> None:
        await session.execute(
            update(RefreshToken).where(RefreshToken.token == token_str).values(is_revoked=True)
        )
        await session.flush()

    @staticmethod
    async def write_audit_log(
        session: AsyncSession,
        action: str,
        user_id: Optional[uuid.UUID] = None,
        ip_address: Optional[str] = None,
        details: Optional[str] = None
    ) -> None:
        logger.info(f"AuthService: writing audit log: {action}")
        audit = AuditLog(
            user_id=user_id,
            action=action,
            ip_address=ip_address,
            details=details
        )
        session.add(audit)
        await session.flush()
