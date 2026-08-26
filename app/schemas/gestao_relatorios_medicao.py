"""Pydantic schemas for Gestão de Relatórios de Medição endpoints."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, field_validator


class ExcluirRelatorioRequest(BaseModel):
    """Body para o endpoint DELETE com opções de cancelamento."""

    enviar_cancelamento: bool = False
    forcar_exclusao: bool = False


class RelatorioMedicaoListItem(BaseModel):
    id: int
    cliente_nome: str
    data_inicial: date
    data_final: date
    total_area: Decimal
    qtd_missoes: int
    gerado_em: datetime
    status: str
    enviado_em: datetime | None = None
    enviado_para: str | None = None

    model_config = {"from_attributes": True}


class RelatorioDownloadResponse(BaseModel):
    download_url: str


class ExcluirRelatorioResponse(BaseModel):
    mensagem: str


class EnviarRelatorioRequest(BaseModel):
    emails: list[str]
    mensagem: str | None = None

    @field_validator("emails")
    @classmethod
    def validate_emails_not_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("É necessário informar pelo menos um e-mail")
        return v


class EnviarRelatorioResponse(BaseModel):
    mensagem: str
