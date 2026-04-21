"""Business logic for Insumo CRUD operations."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessRuleViolationError
from app.models.models import Insumo
from app.repositories.base_repository import PaginatedResult
from app.repositories.insumo_repository import InsumoRepository
from app.schemas.insumo import InsumoCreate, InsumoUpdate
from app.services.auditoria_service import AuditoriaService, entity_to_dict

ENTIDADE = "INSUMO"


class InsumoService:
    """Service layer for Insumo operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = InsumoRepository(db)
        self.auditoria = AuditoriaService(db)

    async def create_insumo(self, data: InsumoCreate, usuario_id: int | None = None) -> Insumo:
        """Create a new insumo. Validates saldo_atual >= 0."""
        if data.saldo_atual < 0:
            raise BusinessRuleViolationError("saldo_atual deve ser >= 0")

        result = await self.repo.create(
            nome=data.nome,
            fabricante=data.fabricante,
            unidade_medida=data.unidade_medida,
            saldo_atual=data.saldo_atual,
            lote=data.lote,
            validade=data.validade,
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

    async def get_insumo(self, insumo_id: int) -> Insumo:
        """Get an insumo by ID."""
        return await self.repo.get_by_id(insumo_id)

    async def list_insumos(
        self,
        page: int = 1,
        page_size: int = 20,
        nome: str | None = None,
        lote: str | None = None,
        ativo: bool | None = None,
    ) -> PaginatedResult[Insumo]:
        """List insumos with optional filters by nome, lote, and ativo."""
        filters: list[Any] = []
        if nome is not None:
            filters.append(Insumo.nome.ilike(f"%{nome}%"))
        if lote is not None:
            filters.append(Insumo.lote == lote)
        if ativo is not None:
            filters.append(Insumo.ativo == ativo)

        return await self.repo.list_paginated(
            page=page,
            page_size=page_size,
            filters=filters if filters else None,
        )

    async def update_insumo(self, insumo_id: int, data: InsumoUpdate, usuario_id: int | None = None) -> Insumo:
        """Update an insumo. Validates saldo_atual >= 0 if provided."""
        old_instance = await self.repo.get_by_id(insumo_id)
        old_values = entity_to_dict(old_instance)

        kwargs: dict[str, Any] = {}

        if data.nome is not None:
            kwargs["nome"] = data.nome
        if data.fabricante is not None:
            kwargs["fabricante"] = data.fabricante
        if data.unidade_medida is not None:
            kwargs["unidade_medida"] = data.unidade_medida
        if data.saldo_atual is not None:
            if data.saldo_atual < 0:
                raise BusinessRuleViolationError("saldo_atual deve ser >= 0")
            kwargs["saldo_atual"] = data.saldo_atual
        if data.lote is not None:
            kwargs["lote"] = data.lote
        if data.validade is not None:
            kwargs["validade"] = data.validade

        result = await self.repo.update(insumo_id, **kwargs)
        if usuario_id is not None:
            await self.auditoria.registrar(
                entidade=ENTIDADE,
                entidade_id=insumo_id,
                acao="ATUALIZACAO",
                valor_anterior=old_values,
                valor_novo=entity_to_dict(result),
                usuario_id=usuario_id,
            )
        return result

    async def delete_insumo(self, insumo_id: int, usuario_id: int | None = None) -> Insumo:
        """Soft-delete an insumo (set ativo=False)."""
        old_instance = await self.repo.get_by_id(insumo_id)
        old_values = entity_to_dict(old_instance)
        result = await self.repo.soft_delete(insumo_id)
        if usuario_id is not None:
            await self.auditoria.registrar(
                entidade=ENTIDADE,
                entidade_id=insumo_id,
                acao="EXCLUSAO",
                valor_anterior=old_values,
                valor_novo=entity_to_dict(result),
                usuario_id=usuario_id,
            )
        return result
