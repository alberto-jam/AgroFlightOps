"""API routes for FinanceiroMissao — restricted to Financeiro and Administrador."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_perfil
from app.models.models import Usuario
from app.schemas.financeiro import FinanceiroMissaoResponse, FinanceiroMissaoUpdate
from app.services.financeiro_service import FinanceiroService

router = APIRouter(
    prefix="/missoes",
    tags=["Financeiro"],
    dependencies=[Depends(require_perfil("FINANCEIRO", "ADMINISTRADOR"))],
)


@router.get(
    "/{missao_id}/financeiro",
    response_model=FinanceiroMissaoResponse,
)
async def get_financeiro_missao(
    missao_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get the financial record for a mission."""
    service = FinanceiroService(db)
    return await service.get_financeiro_by_missao(missao_id)


@router.patch(
    "/{missao_id}/financeiro",
    response_model=FinanceiroMissaoResponse,
)
async def update_financeiro_missao(
    missao_id: int,
    body: FinanceiroMissaoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update financial data for a mission."""
    service = FinanceiroService(db)
    return await service.update_financeiro(missao_id, body)


@router.post(
    "/{missao_id}/financeiro/encerrar",
    response_model=FinanceiroMissaoResponse,
)
async def encerrar_financeiramente(
    missao_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    """Close a mission financially."""
    service = FinanceiroService(db)
    return await service.encerrar_financeiramente(missao_id, current_user.id)
