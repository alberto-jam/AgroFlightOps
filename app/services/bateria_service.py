"""Business logic for Bateria CRUD operations."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateEntityError
from app.models.enums import BateriaStatus
from app.models.models import Bateria
from app.repositories.base_repository import PaginatedResult
from app.repositories.bateria_repository import BateriaRepository
from app.schemas.bateria import BateriaCreate, BateriaUpdate
from app.services.auditoria_service import AuditoriaService, entity_to_dict

ENTIDADE = "BATERIA"


class BateriaService:
    """Service layer for Bateria operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = BateriaRepository(db)
        self.auditoria = AuditoriaService(db)

    async def create_bateria(self, data: BateriaCreate, usuario_id: int | None = None) -> Bateria:
        """Create a new bateria with ciclos=0 and status DISPONIVEL."""
        result = await self.repo.create(
            identificacao=data.identificacao,
            drone_id=data.drone_id,
            ciclos=0,
            status=BateriaStatus.DISPONIVEL.value,
            observacoes=data.observacoes,
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

    async def get_bateria(self, bateria_id: int) -> Bateria:
        """Get a bateria by ID."""
        return await self.repo.get_by_id(bateria_id)

    async def list_baterias(
        self,
        page: int = 1,
        page_size: int = 20,
        status: BateriaStatus | None = None,
        drone_id: int | None = None,
        ativo: bool | None = None,
    ) -> PaginatedResult[Bateria]:
        """List baterias with optional filters by status and drone_id."""
        filters: list[Any] = []
        if status is not None:
            filters.append(Bateria.status == status.value)
        if drone_id is not None:
            filters.append(Bateria.drone_id == drone_id)
        if ativo is not None:
            filters.append(Bateria.ativo == ativo)

        return await self.repo.list_paginated(
            page=page,
            page_size=page_size,
            filters=filters if filters else None,
        )

    async def update_bateria(self, bateria_id: int, data: BateriaUpdate, usuario_id: int | None = None) -> Bateria:
        """Update a bateria. Validates identificacao uniqueness."""
        old_instance = await self.repo.get_by_id(bateria_id)
        old_values = entity_to_dict(old_instance)

        kwargs: dict[str, Any] = {}

        if data.identificacao is not None:
            existing = await self.repo.get_by_identificacao(data.identificacao)
            if existing and existing.id != bateria_id:
                raise DuplicateEntityError(
                    "Bateria com esta identificação já existe"
                )
            kwargs["identificacao"] = data.identificacao

        if data.drone_id is not None:
            kwargs["drone_id"] = data.drone_id
        if data.status is not None:
            kwargs["status"] = data.status.value
        if data.observacoes is not None:
            kwargs["observacoes"] = data.observacoes

        result = await self.repo.update(bateria_id, **kwargs)
        if usuario_id is not None:
            await self.auditoria.registrar(
                entidade=ENTIDADE,
                entidade_id=bateria_id,
                acao="ATUALIZACAO",
                valor_anterior=old_values,
                valor_novo=entity_to_dict(result),
                usuario_id=usuario_id,
            )
        return result

    async def delete_bateria(self, bateria_id: int, usuario_id: int | None = None) -> Bateria:
        """Soft-delete a bateria (set ativo=False)."""
        old_instance = await self.repo.get_by_id(bateria_id)
        old_values = entity_to_dict(old_instance)
        result = await self.repo.soft_delete(bateria_id)
        if usuario_id is not None:
            await self.auditoria.registrar(
                entidade=ENTIDADE,
                entidade_id=bateria_id,
                acao="EXCLUSAO",
                valor_anterior=old_values,
                valor_novo=entity_to_dict(result),
                usuario_id=usuario_id,
            )
        return result
