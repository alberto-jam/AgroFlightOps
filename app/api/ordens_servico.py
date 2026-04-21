"""API routes for OrdemServico CRUD — restricted to Administrador and Coordenador Operacional."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_perfil
from app.models.enums import OrdemServicoStatus, Prioridade
from app.models.models import Usuario
from app.schemas.base import PaginatedResponse
from app.schemas.ordem_servico import (
    HistoricoStatusOSResponse,
    OrdemServicoCreate,
    OrdemServicoResponse,
    OrdemServicoTransicao,
    OrdemServicoUpdate,
)
from app.services.ordem_servico_service import OrdemServicoService

router = APIRouter(
    prefix="/ordens-servico",
    tags=["Ordens de Serviço"],
    dependencies=[Depends(require_perfil("ADMINISTRADOR", "COORDENADOR_OPERACIONAL"))],
)


@router.post("", response_model=OrdemServicoResponse, status_code=201)
async def create_ordem_servico(
    body: OrdemServicoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Create a new Ordem de Serviço."""
    service = OrdemServicoService(db)
    return await service.create_ordem_servico(body, criado_por=current_user.id)


@router.get("", response_model=PaginatedResponse[OrdemServicoResponse])
async def list_ordens_servico(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: OrdemServicoStatus | None = Query(None),
    cliente_id: int | None = Query(None),
    propriedade_id: int | None = Query(None),
    prioridade: Prioridade | None = Query(None),
    data_prevista: date | None = Query(None),
):
    """List Ordens de Serviço with pagination and optional filters."""
    service = OrdemServicoService(db)
    result = await service.list_ordens_servico(
        page=page,
        page_size=page_size,
        status=status,
        cliente_id=cliente_id,
        propriedade_id=propriedade_id,
        prioridade=prioridade,
        data_prevista=data_prevista,
    )
    return PaginatedResponse(
        items=[OrdemServicoResponse.model_validate(os) for os in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        pages=result.pages,
    )


@router.get("/{os_id}", response_model=OrdemServicoResponse)
async def get_ordem_servico(
    os_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get an Ordem de Serviço by ID."""
    service = OrdemServicoService(db)
    return await service.get_ordem_servico(os_id)


@router.put("/{os_id}", response_model=OrdemServicoResponse)
async def update_ordem_servico(
    os_id: int,
    body: OrdemServicoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Update an Ordem de Serviço."""
    service = OrdemServicoService(db)
    return await service.update_ordem_servico(os_id, body, usuario_id=current_user.id)


@router.patch("/{os_id}", response_model=OrdemServicoResponse)
async def patch_ordem_servico(
    os_id: int,
    body: OrdemServicoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Partially update an Ordem de Serviço."""
    service = OrdemServicoService(db)
    return await service.update_ordem_servico(os_id, body, usuario_id=current_user.id)


@router.patch("/{os_id}/transicao", response_model=OrdemServicoResponse)
async def transicionar_ordem_servico(
    os_id: int,
    body: OrdemServicoTransicao,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Transition an Ordem de Serviço to a new status."""
    service = OrdemServicoService(db)
    return await service.transicionar_status(
        os_id=os_id,
        status_novo=body.status_novo,
        motivo=body.motivo,
        usuario_id=current_user.id,
    )


@router.get("/{os_id}/historico", response_model=list[HistoricoStatusOSResponse])
async def list_historico_ordem_servico(
    os_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List status transition history for an Ordem de Serviço."""
    service = OrdemServicoService(db)
    return await service.list_historico(os_id)
