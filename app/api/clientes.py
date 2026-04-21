"""API routes for Cliente CRUD — restricted to Administrador and Coordenador Operacional."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_perfil
from app.models.models import Usuario
from app.schemas.base import PaginatedResponse
from app.schemas.cliente import ClienteCreate, ClienteResponse, ClienteUpdate
from app.services.cliente_service import ClienteService

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"],
    dependencies=[Depends(require_perfil("ADMINISTRADOR", "COORDENADOR_OPERACIONAL"))],
)


@router.post("", response_model=ClienteResponse, status_code=201)
async def create_cliente(
    body: ClienteCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Create a new client."""
    service = ClienteService(db)
    return await service.create_cliente(body, usuario_id=current_user.id)


@router.get("", response_model=PaginatedResponse[ClienteResponse])
async def list_clientes(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    nome: str | None = Query(None),
    cpf_cnpj: str | None = Query(None),
    ativo: bool | None = Query(None),
):
    """List clients with pagination and optional filters."""
    service = ClienteService(db)
    result = await service.list_clientes(
        page=page,
        page_size=page_size,
        nome=nome,
        cpf_cnpj=cpf_cnpj,
        ativo=ativo,
    )
    return PaginatedResponse(
        items=[ClienteResponse.model_validate(c) for c in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        pages=result.pages,
    )


@router.get("/{cliente_id}", response_model=ClienteResponse)
async def get_cliente(
    cliente_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a client by ID."""
    service = ClienteService(db)
    return await service.get_cliente(cliente_id)


@router.put("/{cliente_id}", response_model=ClienteResponse)
async def update_cliente(
    cliente_id: int,
    body: ClienteUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Update a client."""
    service = ClienteService(db)
    return await service.update_cliente(cliente_id, body, usuario_id=current_user.id)


@router.patch("/{cliente_id}", response_model=ClienteResponse)
async def patch_cliente(
    cliente_id: int,
    body: ClienteUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Partially update a client."""
    service = ClienteService(db)
    return await service.update_cliente(cliente_id, body, usuario_id=current_user.id)


@router.delete("/{cliente_id}", response_model=ClienteResponse)
async def delete_cliente(
    cliente_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Soft-delete a client (set ativo=False)."""
    service = ClienteService(db)
    return await service.delete_cliente(cliente_id, usuario_id=current_user.id)
