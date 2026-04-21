"""Security utilities — JWT token management and bcrypt password hashing."""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt with salt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    usuario_id: int,
    perfil: str,
    email: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token with standard claims.

    Claims: sub (usuario_id), perfil, email, exp, iat.
    """
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.JWT_EXPIRATION_MINUTES))
    payload = {
        "sub": str(usuario_id),
        "perfil": perfil,
        "email": email,
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token.

    Returns the payload dict on success.
    Raises JWTError on invalid/expired tokens.
    """
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
