"""API routes for Medição ROP — restricted to Administrador and Financeiro."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_perfil
from app.schemas.base import PaginatedResponse
from app.schemas.medicao_rop import MedicaoRopMissaoResponse
from app.services.medicao_rop_service import MedicaoRopService

router = APIRouter(
    prefix="/medicoes-rop",
    tags=["Medição ROP"],
    dependencies=[Depends(require_perfil("ADMINISTRADOR", "FINANCEIRO"))],
)


@router.get("", response_model=PaginatedResponse[MedicaoRopMissaoResponse])
async def list_missoes_medicao_rop(
    db: Annotated[AsyncSession, Depends(get_db)],
    cliente_id: int = Query(..., description="ID do cliente (obrigatório)"),
    data_inicial: date = Query(..., description="Data inicial do período (obrigatório)"),
    data_final: date = Query(..., description="Data final do período (obrigatório)"),
    propriedade_id: int | None = Query(None, description="ID da propriedade (None = todas)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List eligible missions for ROP measurement within the given filters."""
    service = MedicaoRopService(db)
    result = await service.list_missoes_elegiveis(
        cliente_id=cliente_id,
        data_inicial=data_inicial,
        data_final=data_final,
        propriedade_id=propriedade_id,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        items=[MedicaoRopMissaoResponse.model_validate(m) for m in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        pages=result.pages,
    )
