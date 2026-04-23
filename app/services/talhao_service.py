"""Business logic for Talhao CRUD operations."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BusinessRuleViolationError,
    DependencyActiveError,
    DuplicateEntityError,
)
from app.models.models import Talhao
from app.repositories.base_repository import PaginatedResult
from app.repositories.cultura_repository import CulturaRepository
from app.repositories.propriedade_repository import PropriedadeRepository
from app.repositories.talhao_repository import TalhaoRepository
from app.schemas.talhao import TalhaoCreate, TalhaoUpdate
from app.services.auditoria_service import AuditoriaService, entity_to_dict

ENTIDADE = "TALHAO"


class TalhaoService:
    """Service layer for Talhao operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = TalhaoRepository(db)
        self.propriedade_repo = PropriedadeRepository(db)
        self.cultura_repo = CulturaRepository(db)
        self.auditoria = AuditoriaService(db)

    async def _validate_propriedade(self, propriedade_id: int) -> None:
        """Validate that the referenced propriedade exists and is active."""
        propriedade = await self.propriedade_repo.get_by_id(propriedade_id)
        if not propriedade.ativo:
            raise BusinessRuleViolationError(
                "Propriedade informada está inativa"
            )

    async def _validate_cultura(self, cultura_id: int) -> None:
        """Validate that the referenced cultura exists and is active."""
        cultura = await self.cultura_repo.get_by_id(cultura_id)
        if not cultura.ativo:
            raise BusinessRuleViolationError(
                "Cultura informada está inativa"
            )

    async def create_talhao(self, data: TalhaoCreate, usuario_id: int | None = None) -> Talhao:
        """Create a new talhão associated with a propriedade and cultura."""
        await self._validate_propriedade(data.propriedade_id)
        await self._validate_cultura(data.cultura_id)

        result = await self.repo.create(
            propriedade_id=data.propriedade_id,
            nome=data.nome,
            area_hectares=data.area_hectares,
            cultura_id=data.cultura_id,
            observacoes=data.observacoes,
            latitude=data.latitude,
            longitude=data.longitude,
            ponto_referencia=data.ponto_referencia,
            geojson=data.geojson,
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

    async def get_talhao(self, talhao_id: int) -> Talhao:
        """Get a talhão by ID."""
        return await self.repo.get_by_id(talhao_id)

    async def list_talhoes(
        self,
        page: int = 1,
        page_size: int = 20,
        propriedade_id: int | None = None,
        cultura_id: int | None = None,
        ativo: bool | None = None,
    ) -> PaginatedResult[Talhao]:
        """List talhões with optional filters."""
        filters: list[Any] = []
        if propriedade_id is not None:
            filters.append(Talhao.propriedade_id == propriedade_id)
        if cultura_id is not None:
            filters.append(Talhao.cultura_id == cultura_id)
        if ativo is not None:
            filters.append(Talhao.ativo == ativo)

        return await self.repo.list_paginated(
            page=page,
            page_size=page_size,
            filters=filters if filters else None,
        )

    async def update_talhao(
        self, talhao_id: int, data: TalhaoUpdate, usuario_id: int | None = None
    ) -> Talhao:
        """Update a talhão. Checks composite uniqueness if nome is changed."""
        talhao = await self.repo.get_by_id(talhao_id)
        old_values = entity_to_dict(talhao)
        kwargs: dict[str, Any] = {}

        if data.propriedade_id is not None:
            kwargs["propriedade_id"] = data.propriedade_id

        if data.nome is not None:
            existing = await self.repo.get_by_propriedade_and_nome(
                talhao.propriedade_id, data.nome
            )
            if existing and existing.id != talhao_id:
                raise DuplicateEntityError(
                    "Talhão com este nome já existe nesta propriedade"
                )
            kwargs["nome"] = data.nome

        if data.cultura_id is not None:
            await self._validate_cultura(data.cultura_id)
            kwargs["cultura_id"] = data.cultura_id

        if data.area_hectares is not None:
            kwargs["area_hectares"] = data.area_hectares
        if data.observacoes is not None:
            kwargs["observacoes"] = data.observacoes
        if data.latitude is not None:
            kwargs["latitude"] = data.latitude
        if data.longitude is not None:
            kwargs["longitude"] = data.longitude
        if data.ponto_referencia is not None:
            kwargs["ponto_referencia"] = data.ponto_referencia
        if data.geojson is not None:
            kwargs["geojson"] = data.geojson
        if data.ativo is not None:
            kwargs["ativo"] = data.ativo

        result = await self.repo.update(talhao_id, **kwargs)
        if usuario_id is not None:
            await self.auditoria.registrar(
                entidade=ENTIDADE,
                entidade_id=talhao_id,
                acao="ATUALIZACAO",
                valor_anterior=old_values,
                valor_novo=entity_to_dict(result),
                usuario_id=usuario_id,
            )
        return result

    async def delete_talhao(self, talhao_id: int, usuario_id: int | None = None) -> Talhao:
        """Soft-delete a talhão. Raises DependencyActiveError if it has active orders."""
        await self.repo.get_by_id(talhao_id)

        if await self.repo.has_active_orders(talhao_id):
            raise DependencyActiveError(
                "Talhão possui Ordens de Serviço não canceladas"
            )

        old_instance = await self.repo.get_by_id(talhao_id)
        old_values = entity_to_dict(old_instance)
        result = await self.repo.soft_delete(talhao_id)
        if usuario_id is not None:
            await self.auditoria.registrar(
                entidade=ENTIDADE,
                entidade_id=talhao_id,
                acao="EXCLUSAO",
                valor_anterior=old_values,
                valor_novo=entity_to_dict(result),
                usuario_id=usuario_id,
            )
        return result
