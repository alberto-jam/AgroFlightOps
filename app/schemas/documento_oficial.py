"""Pydantic schemas for DocumentoOficial entity."""

from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.enums import DocumentoEntidade, DocumentoStatus


class DocumentoOficialBase(BaseModel):
    entidade: DocumentoEntidade
    entidade_id: int
    tipo_documento: str = Field(..., max_length=120)
    descricao: str | None = Field(None, max_length=255)
    nome_arquivo: str = Field(..., max_length=255)
    content_type: str = Field(..., max_length=120)
    s3_key: str
    bucket_s3: str | None = Field(None, max_length=255)
    data_emissao: date | None = None
    data_validade: date | None = None


class DocumentoOficialCreate(DocumentoOficialBase):
    pass


class DocumentoOficialUpdate(BaseModel):
    descricao: str | None = Field(None, max_length=255)
    data_emissao: date | None = None
    data_validade: date | None = None
    status: DocumentoStatus | None = None


class DocumentoOficialResponse(DocumentoOficialBase):
    id: int
    status: DocumentoStatus
    enviado_por: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
