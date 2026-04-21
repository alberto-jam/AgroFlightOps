"""Authentication service — login validation and token generation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import create_access_token, verify_password
from app.models.models import Usuario

# Generic error message — never reveals which field (email or password) is wrong
INVALID_CREDENTIALS_MSG = "Credenciais inválidas"


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> dict:
    """Validate email + password, check active status, return JWT token and user info.

    Raises ValueError with a generic message for any authentication failure.
    """
    result = await db.execute(
        select(Usuario)
        .options(selectinload(Usuario.perfil))
        .where(Usuario.email == email)
    )
    usuario = result.scalar_one_or_none()

    # User not found — generic error (don't reveal that email doesn't exist)
    if usuario is None:
        raise ValueError(INVALID_CREDENTIALS_MSG)

    # Wrong password — same generic error
    if not verify_password(password, usuario.senha_hash):
        raise ValueError(INVALID_CREDENTIALS_MSG)

    # Inactive user — same generic error
    if not usuario.ativo:
        raise ValueError(INVALID_CREDENTIALS_MSG)

    token = create_access_token(
        usuario_id=usuario.id,
        perfil=usuario.perfil.nome,
        email=usuario.email,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "perfil": usuario.perfil.nome,
        },
    }


async def refresh_token(current_user: Usuario) -> dict:
    """Generate a new JWT token for an already-authenticated user."""
    token = create_access_token(
        usuario_id=current_user.id,
        perfil=current_user.perfil.nome,
        email=current_user.email,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": current_user.id,
            "nome": current_user.nome,
            "email": current_user.email,
            "perfil": current_user.perfil.nome,
        },
    }
