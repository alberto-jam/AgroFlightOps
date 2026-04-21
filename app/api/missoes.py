"""API routes for Missao CRUD — restricted to Administrador, Coordenador Operacional, Piloto and Técnico."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_perfil
from app.models.enums import MissaoStatus
from app.models.models import Usuario
from app.schemas.base import PaginatedResponse
from app.schemas.missao import (
    HistoricoStatusMissaoResponse,
    MissaoCreate,
    MissaoRegistroExecucao,
    MissaoResponse,
    MissaoTransicao,
    MissaoUpdate,
)
from app.schemas.missao_bateria import MissaoBateriaCreate, MissaoBateriaResponse
from app.schemas.reserva_insumo import (
    ConsumoInsumoMissaoCreate,
    ConsumoInsumoMissaoResponse,
    ReservaInsumoCreate,
    ReservaInsumoResponse,
)
from app.services.missao_service import MissaoService

router = APIRouter(
    prefix="/missoes",
    tags=["Missões"],
    dependencies=[
        Depends(
            require_perfil(
                "ADMINISTRADOR",
                "COORDENADOR_OPERACIONAL",
                "PILOTO",
                "TECNICO",
            )
        )
    ],
)


@router.post("", response_model=MissaoResponse, status_code=201)
async def create_missao(
    body: MissaoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Create a new Missão."""
    service = MissaoService(db)
    return await service.create_missao(body, usuario_id=current_user.id)


@router.get("", response_model=PaginatedResponse[MissaoResponse])
async def list_missoes(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: MissaoStatus | None = Query(None),
    piloto_id: int | None = Query(None),
    drone_id: int | None = Query(None),
    data_agendada: date | None = Query(None),
    ordem_servico_id: int | None = Query(None),
):
    """List Missões with pagination and optional filters."""
    service = MissaoService(db)
    result = await service.list_missoes(
        page=page,
        page_size=page_size,
        status=status,
        piloto_id=piloto_id,
        drone_id=drone_id,
        data_agendada=data_agendada,
        ordem_servico_id=ordem_servico_id,
    )
    return PaginatedResponse(
        items=[MissaoResponse.model_validate(m) for m in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        pages=result.pages,
    )


@router.get("/{missao_id}", response_model=MissaoResponse)
async def get_missao(
    missao_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a Missão by ID."""
    service = MissaoService(db)
    return await service.get_missao(missao_id)


@router.put("/{missao_id}", response_model=MissaoResponse)
async def update_missao(
    missao_id: int,
    body: MissaoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Update a Missão."""
    service = MissaoService(db)
    return await service.update_missao(missao_id, body, usuario_id=current_user.id)


@router.patch("/{missao_id}", response_model=MissaoResponse)
async def patch_missao(
    missao_id: int,
    body: MissaoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Partially update a Missão."""
    service = MissaoService(db)
    return await service.update_missao(missao_id, body, usuario_id=current_user.id)


@router.patch("/{missao_id}/transicao", response_model=MissaoResponse)
async def transicionar_missao(
    missao_id: int,
    body: MissaoTransicao,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Transition a Missão to a new status."""
    service = MissaoService(db)
    return await service.transicionar_status(
        missao_id=missao_id,
        status_novo=body.status_novo,
        motivo=body.motivo,
        usuario_id=current_user.id,
    )


@router.patch("/{missao_id}/execucao", response_model=MissaoResponse)
async def registrar_execucao_missao(
    missao_id: int,
    body: MissaoRegistroExecucao,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Register execution data for a Missão (only when EM_EXECUCAO)."""
    service = MissaoService(db)
    return await service.registrar_execucao(
        missao_id=missao_id,
        area_realizada=body.area_realizada,
        volume_realizado=body.volume_realizado,
        observacoes_execucao=body.observacoes_execucao,
    )


@router.get("/{missao_id}/historico", response_model=list[HistoricoStatusMissaoResponse])
async def list_historico_missao(
    missao_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List status transition history for a Missão."""
    service = MissaoService(db)
    return await service.list_historico(missao_id)


@router.post(
    "/{missao_id}/baterias",
    response_model=MissaoBateriaResponse,
    status_code=201,
)
async def associar_bateria_missao(
    missao_id: int,
    body: MissaoBateriaCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Associate a battery to a mission."""
    service = MissaoService(db)
    return await service.associar_bateria(
        missao_id=missao_id,
        bateria_id=body.bateria_id,
        ordem_uso=body.ordem_uso,
    )


@router.get(
    "/{missao_id}/baterias",
    response_model=list[MissaoBateriaResponse],
)
async def list_baterias_missao(
    missao_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List batteries associated with a mission."""
    service = MissaoService(db)
    return await service.list_baterias_missao(missao_id)


@router.post(
    "/{missao_id}/reservas-insumo",
    response_model=ReservaInsumoResponse,
    status_code=201,
)
async def criar_reserva_insumo(
    missao_id: int,
    body: ReservaInsumoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create an insumo reservation for a mission."""
    service = MissaoService(db)
    return await service.criar_reserva_insumo(
        missao_id=missao_id,
        insumo_id=body.insumo_id,
        quantidade_prevista=body.quantidade_prevista,
        unidade_medida=body.unidade_medida,
    )


@router.get(
    "/{missao_id}/reservas-insumo",
    response_model=list[ReservaInsumoResponse],
)
async def list_reservas_insumo(
    missao_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List insumo reservations for a mission."""
    service = MissaoService(db)
    return await service.list_reservas_insumo(missao_id)


@router.post(
    "/{missao_id}/consumos-insumo",
    response_model=ConsumoInsumoMissaoResponse,
    status_code=201,
)
async def registrar_consumo_insumo(
    missao_id: int,
    body: ConsumoInsumoMissaoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Register insumo consumption during a mission."""
    service = MissaoService(db)
    return await service.registrar_consumo_insumo(
        missao_id=missao_id,
        insumo_id=body.insumo_id,
        quantidade_realizada=body.quantidade_realizada,
        unidade_medida=body.unidade_medida,
        observacoes=body.observacoes,
        justificativa_excesso=body.justificativa_excesso,
    )


@router.get(
    "/{missao_id}/consumos-insumo",
    response_model=list[ConsumoInsumoMissaoResponse],
)
async def list_consumos_insumo(
    missao_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List insumo consumptions for a mission."""
    service = MissaoService(db)
    return await service.list_consumos_insumo(missao_id)
