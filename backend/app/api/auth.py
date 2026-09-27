import logging
from typing import Optional
from fastapi import APIRouter, Depends, Response, Request, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr, Field
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.models.user import User
from app.core.database import get_db_session
from app.services.auth_service import AuthService

logger = logging.getLogger("app.api.auth")
router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=1024)
    full_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Registers a new user, hashes their credentials, and logs the registration.
    """
    logger.info(f"API Register: user registration request: {payload.email}")
    user = await AuthService.register_user(
        session=session,
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name
    )
    try:
        await AuthService.write_audit_log(
            session=session,
            action="USER_REGISTRATION",
            user_id=user.id,
            details=f"Email: {user.email}"
        )
    except Exception as audit_err:
        logger.warning(f"Audit log write skipped: {audit_err}")
    return {"user_id": str(user.id), "email": user.email, "message": "User registered successfully."}

@router.post("/login", status_code=status.HTTP_200_OK)
@router.post("/token", status_code=status.HTTP_200_OK)
async def login(
    payload: LoginRequest,
    response: Response,
    request: Request,
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Validates user credentials, issues JWT access token, and sets secure refresh token cookie.
    """
    logger.info(f"API Login: user token request: {payload.email}")
    user, access_token = await AuthService.authenticate_user(
        session=session,
        email=payload.email,
        password=payload.password
    )
    
    # Create and write refresh token
    try:
        refresh_token = await AuthService.create_session_refresh_token(
            session=session,
            user_id=user.id
        )
        
        # Set HttpOnly cookie for session security
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite="strict",
            max_age=30 * 86400  # 30 days
        )
        
        await AuthService.write_audit_log(
            session=session,
            action="USER_LOGIN_SUCCESS",
            user_id=user.id,
            ip_address=request.client.host if request.client else None
        )
    except Exception as sess_err:
        logger.warning(f"Session refresh token / audit write skipped: {sess_err}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh(
    request: Request,
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Validates refresh token cookie and issues new access token.
    """
    logger.info("API Refresh: session token refresh request.")
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        logger.warning("Session refresh failed: missing refresh_token cookie.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session refresh token is missing."
        )
        
    access_token = await AuthService.refresh_access_session(
        session=session,
        token_str=refresh_token
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    request: Request,
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Revokes the active user session and clears authentication cookies.
    """
    logger.info("API Logout: logging user session out.")
    token = request.cookies.get("refresh_token")
    if token:
        await AuthService.revoke_refresh_token(session, token)
    response.delete_cookie(key="refresh_token", secure=settings.COOKIE_SECURE, httponly=True, samesite="strict")
    return {"message": "Logged out successfully."}


@router.get("/me")
async def current_user_profile(user: User = Depends(get_current_user)) -> dict:
    return {"id": str(user.id), "email": user.email, "full_name": user.full_name}
