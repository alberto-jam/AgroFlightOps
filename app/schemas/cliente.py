"""Pydantic schemas for Cliente entity."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class ClienteBase(BaseModel):
    nome: str = Field(..., max_length=200)
    cpf_cnpj: str | None = Field(None, max_length=18)
    telefone: str | None = Field(None, max_length=30)
    email: str | None = Field(None, max_length=255)
    endereco: str | None = Field(None, max_length=255)
    numero: str | None = Field(None, max_length=20)
    complemento: str | None = Field(None, max_length=120)
    bairro: str | None = Field(None, max_length=120)
    municipio: str | None = Field(None, max_length=120)
    estado: str | None = Field(None, max_length=2)
    cep: str | None = Field(None, max_length=12)
    latitude: Decimal | None = Field(None, ge=-90, le=90)
    longitude: Decimal | None = Field(None, ge=-180, le=180)
    referencia_local: str | None = Field(None, max_length=255)


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nome: str | None = Field(None, max_length=200)
    cpf_cnpj: str | None = Field(None, max_length=18)
    telefone: str | None = Field(None, max_length=30)
    email: str | None = Field(None, max_length=255)
    endereco: str | None = Field(None, max_length=255)
    numero: str | None = Field(None, max_length=20)
    complemento: str | None = Field(None, max_length=120)
    bairro: str | None = Field(None, max_length=120)
    municipio: str | None = Field(None, max_length=120)
    estado: str | None = Field(None, max_length=2)
    cep: str | None = Field(None, max_length=12)
    latitude: Decimal | None = Field(None, ge=-90, le=90)
    longitude: Decimal | None = Field(None, ge=-180, le=180)
    referencia_local: str | None = Field(None, max_length=255)


class ClienteResponse(ClienteBase):
    id: int
    ativo: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
