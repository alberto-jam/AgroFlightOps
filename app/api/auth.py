"""Authentication routes — login and token refresh."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.models import Usuario
from app.services.auth_service import authenticate_user, refresh_token

router = APIRouter(prefix="/auth", tags=["Autenticação"])


# --- Request / Response schemas (local to auth) ---


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    usuario: dict


# --- Endpoints ---


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Authenticate with email and password, receive a JWT token."""
    try:
        result = await authenticate_user(db, body.email, body.senha)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
        )
    return result


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Refresh the JWT token for an authenticated user."""
    return await refresh_token(current_user)
