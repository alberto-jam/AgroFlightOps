"""FastAPI dependencies for authentication and role-based authorization."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import decode_token
from app.models.models import Usuario

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Usuario:
    """Extract and validate JWT from Authorization header, return the active user."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido",
        )

    try:
        payload = decode_token(credentials.credentials)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )

    usuario_id = payload.get("sub")
    if usuario_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )

    result = await db.execute(
        select(Usuario)
        .options(selectinload(Usuario.perfil))
        .where(Usuario.id == int(usuario_id))
    )
    usuario = result.scalar_one_or_none()

    if usuario is None or not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )

    return usuario


def require_perfil(*perfis: str):
    """Dependency factory that checks if the current user has one of the allowed profiles.

    Usage: Depends(require_perfil("ADMINISTRADOR", "COORDENADOR_OPERACIONAL"))
    Returns 403 if the user's profile is not in the allowed list.
    """

    async def _check_perfil(
        current_user: Annotated[Usuario, Depends(get_current_user)],
    ) -> Usuario:
        if current_user.perfil.nome not in perfis:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado: perfil não autorizado",
            )
        return current_user

    return _check_perfil
