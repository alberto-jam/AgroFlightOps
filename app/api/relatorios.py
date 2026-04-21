"""API routes for operational and financial reports — Administrador and Financeiro."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_perfil
from app.schemas.relatorio import (
    AreaPorClienteResponse,
    FinanceiroResumoResponse,
    MissoesPorStatusResponse,
    UtilizacaoDroneResponse,
)
from app.services.relatorio_service import RelatorioService

router = APIRouter(
    prefix="/relatorios",
    tags=["Relatórios"],
    dependencies=[Depends(require_perfil("ADMINISTRADOR", "FINANCEIRO"))],
)


@router.get("/missoes-por-status", response_model=MissoesPorStatusResponse)
async def relatorio_missoes_por_status(
    db: Annotated[AsyncSession, Depends(get_db)],
    data_inicio: date = Query(..., description="Data início do período"),
    data_fim: date = Query(..., description="Data fim do período"),
):
    """Report: total missions grouped by status within a period."""
    service = RelatorioService(db)
    return await service.missoes_por_status(data_inicio, data_fim)


@router.get("/area-por-cliente", response_model=AreaPorClienteResponse)
async def relatorio_area_por_cliente(
    db: Annotated[AsyncSession, Depends(get_db)],
    data_inicio: date = Query(..., description="Data início do período"),
    data_fim: date = Query(..., description="Data fim do período"),
):
    """Report: total sprayed area by client within a period."""
    service = RelatorioService(db)
    return await service.area_por_cliente(data_inicio, data_fim)


@router.get("/financeiro", response_model=FinanceiroResumoResponse)
async def relatorio_financeiro(
    db: Annotated[AsyncSession, Depends(get_db)],
    data_inicio: date = Query(..., description="Data início do período"),
    data_fim: date = Query(..., description="Data fim do período"),
):
    """Report: financial summary (only ENCERRADA_FINANCEIRAMENTE missions) within a period."""
    service = RelatorioService(db)
    return await service.financeiro_resumo(data_inicio, data_fim)


@router.get("/utilizacao-drones", response_model=UtilizacaoDroneResponse)
async def relatorio_utilizacao_drones(
    db: Annotated[AsyncSession, Depends(get_db)],
    data_inicio: date = Query(..., description="Data início do período"),
    data_fim: date = Query(..., description="Data fim do período"),
):
    """Report: drone utilization (flight hours) within a period."""
    service = RelatorioService(db)
    return await service.utilizacao_drones(data_inicio, data_fim)
