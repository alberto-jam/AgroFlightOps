"""Schemas for operational and financial reports."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class RelatorioFiltro(BaseModel):
    """Common filter for report endpoints."""

    data_inicio: date
    data_fim: date


class MissoesPorStatusItem(BaseModel):
    """Single row in the missions-by-status report."""

    status: str
    total: int


class MissoesPorStatusResponse(BaseModel):
    """Report: missions grouped by status within a period."""

    data_inicio: date
    data_fim: date
    items: list[MissoesPorStatusItem]
    total_geral: int


class AreaPorClienteItem(BaseModel):
    """Single row in the sprayed-area-by-client report."""

    cliente_id: int
    cliente_nome: str
    area_total_pulverizada: Decimal


class AreaPorClienteResponse(BaseModel):
    """Report: total sprayed area by client within a period."""

    data_inicio: date
    data_fim: date
    items: list[AreaPorClienteItem]


class FinanceiroResumoResponse(BaseModel):
    """Report: financial summary within a period (only ENCERRADA_FINANCEIRAMENTE)."""

    data_inicio: date
    data_fim: date
    total_custo_estimado: Decimal
    total_custo_realizado: Decimal
    total_valor_faturado: Decimal
    total_missoes: int


class UtilizacaoDroneItem(BaseModel):
    """Single row in the drone utilization report."""

    drone_id: int
    drone_identificacao: str
    drone_modelo: str
    horas_voadas_periodo: Decimal
    total_missoes: int


class UtilizacaoDroneResponse(BaseModel):
    """Report: drone utilization (flight hours) within a period."""

    data_inicio: date
    data_fim: date
    items: list[UtilizacaoDroneItem]
