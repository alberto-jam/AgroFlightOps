"""Pydantic schemas for Relatório de Medição ROP."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class RelatorioMedicaoPreviewRequest(BaseModel):
    missao_ids: list[int]
    cliente_id: int


class MissaoPreviewItem(BaseModel):
    id: int
    codigo: str
    propriedade_nome: str
    talhao_nome: str
    area_realizada: Decimal | None
    encerrado_tecnicamente_em: datetime

    model_config = {"from_attributes": True}


class RelatorioMedicaoPreviewResponse(BaseModel):
    cliente_nome: str
    missoes: list[MissaoPreviewItem]
    total_area: Decimal


class GerarRelatorioMedicaoRequest(BaseModel):
    missao_ids: list[int]
    cliente_id: int
    data_inicial: date
    data_final: date


class RelatorioMedicaoGeradoResponse(BaseModel):
    s3_key: str
    mensagem: str
    relatorio_id: int | None = None
