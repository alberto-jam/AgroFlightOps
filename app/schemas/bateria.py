"""Pydantic schemas for Bateria entity."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import BateriaStatus


class BateriaBase(BaseModel):
    identificacao: str = Field(..., max_length=120)
    drone_id: int | None = None
    status: BateriaStatus = BateriaStatus.DISPONIVEL
    observacoes: str | None = None


class BateriaCreate(BateriaBase):
    pass


class BateriaUpdate(BaseModel):
    identificacao: str | None = Field(None, max_length=120)
    drone_id: int | None = None
    status: BateriaStatus | None = None
    observacoes: str | None = None


class BateriaResponse(BateriaBase):
    id: int
    ciclos: int
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
