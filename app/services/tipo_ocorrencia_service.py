"""Business logic for TipoOcorrencia CRUD operations."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DependencyActiveError, DuplicateEntityError
from app.models.models import TipoOcorrencia
from app.repositories.base_repository import PaginatedResult
from app.repositories.tipo_ocorrencia_repository import TipoOcorrenciaRepository
from app.schemas.tipo_ocorrencia import TipoOcorrenciaCreate, TipoOcorrenciaUpdate
from app.services.auditoria_service import AuditoriaService, entity_to_dict

ENTIDADE = "TIPO_OCORRENCIA"


class TipoOcorrenciaService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = TipoOcorrenciaRepository(db)
        self.auditoria = AuditoriaService(db)

    async def create(self, data: TipoOcorrenciaCreate, usuario_id: int | None = None) -> TipoOcorrencia:
        result = await self.repo.create(nome=data.nome, descricao=data.descricao)
        if usuario_id:
            await self.auditoria.registrar(
                entidade=ENTIDADE, entidade_id=result.id, acao="CRIACAO",
                valor_anterior=None, valor_novo=entity_to_dict(result), usuario_id=usuario_id,
            )
        return result

    async def get(self, tipo_id: int) -> TipoOcorrencia:
        return await self.repo.get_by_id(tipo_id)

    async def list(self, page: int = 1, page_size: int = 20, ativo: bool | None = None) -> PaginatedResult[TipoOcorrencia]:
        filters: list[Any] = []
        if ativo is not None:
            filters.append(TipoOcorrencia.ativo == ativo)
        return await self.repo.list_paginated(page=page, page_size=page_size, filters=filters if filters else None)

    async def update(self, tipo_id: int, data: TipoOcorrenciaUpdate, usuario_id: int | None = None) -> TipoOcorrencia:
        old = await self.repo.get_by_id(tipo_id)
        old_values = entity_to_dict(old)
        kwargs: dict[str, Any] = {}
        if data.nome is not None:
            existing = await self.repo.get_by_nome(data.nome)
            if existing and existing.id != tipo_id:
                raise DuplicateEntityError("Tipo de ocorrência com este nome já existe")
            kwargs["nome"] = data.nome
        if data.descricao is not None:
            kwargs["descricao"] = data.descricao
        result = await self.repo.update(tipo_id, **kwargs)
        if usuario_id:
            await self.auditoria.registrar(
                entidade=ENTIDADE, entidade_id=tipo_id, acao="ATUALIZACAO",
                valor_anterior=old_values, valor_novo=entity_to_dict(result), usuario_id=usuario_id,
            )
        return result

    async def delete(self, tipo_id: int, usuario_id: int | None = None) -> TipoOcorrencia:
        await self.repo.get_by_id(tipo_id)
        if await self.repo.has_active_ocorrencias(tipo_id):
            raise DependencyActiveError("Tipo de ocorrência possui ocorrências registradas")
        old = await self.repo.get_by_id(tipo_id)
        old_values = entity_to_dict(old)
        result = await self.repo.soft_delete(tipo_id)
        if usuario_id:
            await self.auditoria.registrar(
                entidade=ENTIDADE, entidade_id=tipo_id, acao="EXCLUSAO",
                valor_anterior=old_values, valor_novo=entity_to_dict(result), usuario_id=usuario_id,
            )
        return result
