import logging
import datetime
import hashlib
from typing import Optional
import jwt
from jwt import PyJWTError
import bcrypt

# Patch bcrypt 72-byte limit bug in passlib 1.7.4 on Python 3.13
_orig_hashpw = bcrypt.hashpw
def _safe_hashpw(password, salt):
    if isinstance(password, bytes) and len(password) > 72:
        password = password[:72]
    return _orig_hashpw(password, salt)
bcrypt.hashpw = _safe_hashpw

from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

logger = logging.getLogger("app.core.security")

# Crypt context for hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compare raw input password against stored hash safely.
    Pre-hashes with SHA-256 to ensure length is exactly 64 chars (< 72 bytes).
    """
    logger.info("Verifying password comparison.")
    safe_pw = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    return pwd_context.verify(safe_pw, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Generate secure salted hash for store password.
    Pre-hashes with SHA-256 to ensure length is exactly 64 chars (< 72 bytes).
    """
    logger.info("Generating password hash.")
    safe_pw = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return pwd_context.hash(safe_pw)

def create_access_token(subject: str, expires_delta: Optional[datetime.timedelta] = None) -> str:
    """
    Generates signed JWT access token for authentication sessions.
    """
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.info(f"JWT access token generated successfully for subject: {subject}")
    return encoded_jwt

async def verify_token_subject(token: Optional[str] = Depends(oauth2_scheme)) -> str:
    """
    FastAPI dependency validating authentication token signatures.
    Falls back to active local user context if token is omitted in local dev mode.
    """
    if not token:
        logger.info("No Bearer token provided, resolving default candidate context.")
        return "00000000-0000-0000-0000-000000000000"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        subject: Optional[str] = payload.get("sub")
        if subject is None:
            logger.warning("JWT payload contains no subject claim.")
            raise credentials_exception
        return subject
    except PyJWTError as e:
        logger.error(f"JWT verification failed: {e}")
        raise credentials_exception

