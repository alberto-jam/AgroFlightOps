"""Pydantic schemas for MissaoBateria entity."""

from datetime import datetime

from pydantic import BaseModel, Field


class MissaoBateriaBase(BaseModel):
    missao_id: int
    bateria_id: int
    ordem_uso: int = Field(..., gt=0)


class MissaoBateriaCreate(MissaoBateriaBase):
    pass


class MissaoBateriaResponse(MissaoBateriaBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
