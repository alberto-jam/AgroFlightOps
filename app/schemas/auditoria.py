"""Pydantic schemas for Auditoria entity."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AuditoriaResponse(BaseModel):
    id: int
    entidade: str
    entidade_id: int
    acao: str
    valor_anterior: dict[str, Any] | None
    valor_novo: dict[str, Any] | None
    usuario_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
