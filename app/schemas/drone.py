"""Pydantic schemas for Drone entity."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.enums import DroneStatus


class DroneBase(BaseModel):
    identificacao: str = Field(..., max_length=120)
    modelo: str = Field(..., max_length=120)
    fabricante: str | None = Field(None, max_length=120)
    capacidade_litros: Decimal = Field(..., ge=0)
    status: DroneStatus = DroneStatus.DISPONIVEL


class DroneCreate(DroneBase):
    pass


class DroneUpdate(BaseModel):
    identificacao: str | None = Field(None, max_length=120)
    modelo: str | None = Field(None, max_length=120)
    fabricante: str | None = Field(None, max_length=120)
    capacidade_litros: Decimal | None = Field(None, ge=0)
    status: DroneStatus | None = None


class DroneResponse(DroneBase):
    id: int
    horas_voadas: Decimal
    ultima_manutencao_em: date | None
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
