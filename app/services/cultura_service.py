"""Business logic for Cultura CRUD operations."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DependencyActiveError, DuplicateEntityError
from app.models.models import Cultura
from app.repositories.base_repository import PaginatedResult
from app.repositories.cultura_repository import CulturaRepository
from app.schemas.cultura import CulturaCreate, CulturaUpdate
from app.services.auditoria_service import AuditoriaService, entity_to_dict

ENTIDADE = "CULTURA"


class CulturaService:
    """Service layer for Cultura operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CulturaRepository(db)
        self.auditoria = AuditoriaService(db)

    async def create_cultura(self, data: CulturaCreate, usuario_id: int | None = None) -> Cultura:
        """Create a new cultura."""
        result = await self.repo.create(
            nome=data.nome,
            descricao=data.descricao,
        )
        if usuario_id is not None:
            await self.auditoria.registrar(
                entidade=ENTIDADE,
                entidade_id=result.id,
                acao="CRIACAO",
                valor_anterior=None,
                valor_novo=entity_to_dict(result),
                usuario_id=usuario_id,
            )
        return result

    async def get_cultura(self, cultura_id: int) -> Cultura:
        """Get a cultura by ID."""
        return await self.repo.get_by_id(cultura_id)

    async def list_culturas(
        self,
        page: int = 1,
        page_size: int = 20,
        ativo: bool | None = None,
    ) -> PaginatedResult[Cultura]:
        """List culturas with optional filter for status."""
        filters: list[Any] = []
        if ativo is not None:
            filters.append(Cultura.ativo == ativo)

        return await self.repo.list_paginated(
            page=page,
            page_size=page_size,
            filters=filters if filters else None,
        )

    async def update_cultura(self, cultura_id: int, data: CulturaUpdate, usuario_id: int | None = None) -> Cultura:
        """Update a cultura. Checks nome uniqueness if changed."""
        old_instance = await self.repo.get_by_id(cultura_id)
        old_values = entity_to_dict(old_instance)

        kwargs: dict[str, Any] = {}

        if data.nome is not None:
            existing = await self.repo.get_by_nome(data.nome)
            if existing and existing.id != cultura_id:
                raise DuplicateEntityError("Cultura com este nome já existe")
            kwargs["nome"] = data.nome

        if data.descricao is not None:
            kwargs["descricao"] = data.descricao

        result = await self.repo.update(cultura_id, **kwargs)
        if usuario_id is not None:
            await self.auditoria.registrar(
                entidade=ENTIDADE,
                entidade_id=cultura_id,
                acao="ATUALIZACAO",
                valor_anterior=old_values,
                valor_novo=entity_to_dict(result),
                usuario_id=usuario_id,
            )
        return result

    async def delete_cultura(self, cultura_id: int, usuario_id: int | None = None) -> Cultura:
        """Soft-delete a cultura (set ativo=False). Raises DependencyActiveError if cultura has active talhões."""
        await self.repo.get_by_id(cultura_id)

        if await self.repo.has_active_talhoes(cultura_id):
            raise DependencyActiveError(
                "Cultura possui Talhões ativos"
            )

        old_instance = await self.repo.get_by_id(cultura_id)
        old_values = entity_to_dict(old_instance)
        result = await self.repo.soft_delete(cultura_id)
        if usuario_id is not None:
            await self.auditoria.registrar(
                entidade=ENTIDADE,
                entidade_id=cultura_id,
                acao="EXCLUSAO",
                valor_anterior=old_values,
                valor_novo=entity_to_dict(result),
                usuario_id=usuario_id,
            )
        return result
