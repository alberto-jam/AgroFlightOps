"""Pydantic schemas for Usuario entity."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UsuarioBase(BaseModel):
    nome: str = Field(..., max_length=200)
    email: EmailStr = Field(..., max_length=255)
    perfil_id: int


class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=6)


class UsuarioUpdate(BaseModel):
    nome: str | None = Field(None, max_length=200)
    email: EmailStr | None = Field(None, max_length=255)
    perfil_id: int | None = None
    senha: str | None = Field(None, min_length=6)


class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: str
    perfil_id: int
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
