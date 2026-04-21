"""API routes for Usuario CRUD — restricted to Administrador profile."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_perfil
from app.models.models import Usuario
from app.schemas.base import PaginatedResponse
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioUpdate
from app.services.usuario_service import UsuarioService

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"],
    dependencies=[Depends(require_perfil("ADMINISTRADOR"))],
)


@router.post("", response_model=UsuarioResponse, status_code=201)
async def create_usuario(
    body: UsuarioCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Create a new user."""
    service = UsuarioService(db)
    usuario = await service.create_usuario(body, usuario_id=current_user.id)
    return usuario


@router.get("", response_model=PaginatedResponse[UsuarioResponse])
async def list_usuarios(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    perfil_id: int | None = Query(None),
    ativo: bool | None = Query(None),
):
    """List users with pagination and optional filters."""
    service = UsuarioService(db)
    result = await service.list_usuarios(
        page=page,
        page_size=page_size,
        perfil_id=perfil_id,
        ativo=ativo,
    )
    return PaginatedResponse(
        items=[UsuarioResponse.model_validate(u) for u in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        pages=result.pages,
    )


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def get_usuario(
    usuario_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a user by ID."""
    service = UsuarioService(db)
    return await service.get_usuario(usuario_id)


@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def update_usuario(
    usuario_id: int,
    body: UsuarioUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Update a user."""
    service = UsuarioService(db)
    return await service.update_usuario(usuario_id, body, current_user_id=current_user.id)


@router.patch("/{usuario_id}", response_model=UsuarioResponse)
async def patch_usuario(
    usuario_id: int,
    body: UsuarioUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Partially update a user."""
    service = UsuarioService(db)
    return await service.update_usuario(usuario_id, body, current_user_id=current_user.id)


@router.delete("/{usuario_id}", response_model=UsuarioResponse)
async def delete_usuario(
    usuario_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Soft-delete a user (set ativo=False)."""
    service = UsuarioService(db)
    return await service.delete_usuario(usuario_id, current_user_id=current_user.id)
