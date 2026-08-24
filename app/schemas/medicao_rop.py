"""Pydantic schemas for Medição ROP."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from app.models.enums import MissaoStatus


class MedicaoRopMissaoResponse(BaseModel):
    id: int
    codigo: str
    propriedade_nome: str
    talhao_nome: str
    encerrado_tecnicamente_em: datetime
    area_realizada: Decimal | None
    status: MissaoStatus

    model_config = {"from_attributes": True}


class MedicaoRopFiltros(BaseModel):
    cliente_id: int
    data_inicial: date
    data_final: date
    propriedade_id: int | None = None
