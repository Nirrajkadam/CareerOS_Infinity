import logging
import datetime
import hashlib
from typing import Optional
import jwt
from jwt import PyJWTError
import bcrypt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

logger = logging.getLogger("app.core.security")

# Crypt context for hashing passwords
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compare raw input password against stored hash safely.
    Pre-hashes with SHA-256 to ensure length is exactly 64 chars (< 72 bytes).
    """
    logger.info("Verifying password comparison.")
    safe_pw = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    try:
        return bcrypt.checkpw(safe_pw.encode("ascii"), hashed_password.encode("ascii"))
    except (ValueError, UnicodeError):
        return False

def get_password_hash(password: str) -> str:
    """
    Generate secure salted hash for store password.
    Pre-hashes with SHA-256 to ensure length is exactly 64 chars (< 72 bytes).
    """
    logger.info("Generating password hash.")
    safe_pw = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return bcrypt.hashpw(safe_pw.encode("ascii"), bcrypt.gensalt()).decode("ascii")

def create_access_token(subject: str, expires_delta: Optional[datetime.timedelta] = None) -> str:
    """
    Generates signed JWT access token for authentication sessions.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    if expires_delta is not None:
        expire = now + expires_delta
    else:
        expire = now + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.info(f"JWT access token generated successfully for subject: {subject}")
    return encoded_jwt

async def verify_token_subject(token: Optional[str] = Depends(oauth2_scheme)) -> str:
    """
    FastAPI dependency validating authentication token signatures.
    Missing, invalid, or expired credentials always fail closed.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], options={"require": ["exp", "sub"]})
        subject: Optional[str] = payload.get("sub")
        if not isinstance(subject, str) or not subject.strip():
            logger.warning("JWT payload contains no subject claim.")
            raise credentials_exception
        return subject
    except PyJWTError as e:
        logger.error(f"JWT verification failed: {e}")
        raise credentials_exception
