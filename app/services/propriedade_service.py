"""Business logic for Propriedade CRUD operations."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BusinessRuleViolationError,
    DependencyActiveError,
    EntityNotFoundError,
)
from app.models.models import Propriedade
from app.repositories.base_repository import PaginatedResult
from app.repositories.cliente_repository import ClienteRepository
from app.repositories.propriedade_repository import PropriedadeRepository
from app.schemas.propriedade import PropriedadeCreate, PropriedadeUpdate
from app.services.auditoria_service import AuditoriaService, entity_to_dict

ENTIDADE = "PROPRIEDADE"


class PropriedadeService:
    """Service layer for Propriedade operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PropriedadeRepository(db)
        self.cliente_repo = ClienteRepository(db)
        self.auditoria = AuditoriaService(db)

    async def _validate_cliente_exists(self, cliente_id: int) -> None:
        """Validate that the referenced cliente exists and is active."""
        cliente = await self.cliente_repo.get_by_id(cliente_id)
        if not cliente.ativo:
            raise BusinessRuleViolationError(
                "Cliente informado está inativo"
            )

    async def create_propriedade(self, data: PropriedadeCreate, usuario_id: int | None = None) -> Propriedade:
        """Create a new property associated with an existing client."""
        await self._validate_cliente_exists(data.cliente_id)

        result = await self.repo.create(
            cliente_id=data.cliente_id,
            nome=data.nome,
            endereco=data.endereco,
            numero=data.numero,
            complemento=data.complemento,
            bairro=data.bairro,
            municipio=data.municipio,
            estado=data.estado,
            cep=data.cep,
            localizacao_descritiva=data.localizacao_descritiva,
            referencia_local=data.referencia_local,
            latitude=data.latitude,
            longitude=data.longitude,
            area_total=data.area_total,
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

    async def get_propriedade(self, propriedade_id: int) -> Propriedade:
        """Get a property by ID."""
        return await self.repo.get_by_id(propriedade_id)

    async def list_propriedades(
        self,
        page: int = 1,
        page_size: int = 20,
        cliente_id: int | None = None,
        municipio: str | None = None,
        estado: str | None = None,
        ativo: bool | None = None,
    ) -> PaginatedResult[Propriedade]:
        """List properties with optional filters."""
        filters: list[Any] = []
        if cliente_id is not None:
            filters.append(Propriedade.cliente_id == cliente_id)
        if municipio is not None:
            filters.append(Propriedade.municipio.ilike(f"%{municipio}%"))
        if estado is not None:
            filters.append(Propriedade.estado == estado.upper())
        if ativo is not None:
            filters.append(Propriedade.ativo == ativo)

        return await self.repo.list_paginated(
            page=page,
            page_size=page_size,
            filters=filters if filters else None,
        )

    async def update_propriedade(
        self, propriedade_id: int, data: PropriedadeUpdate, usuario_id: int | None = None
    ) -> Propriedade:
        """Update a property."""
        old_instance = await self.repo.get_by_id(propriedade_id)
        old_values = entity_to_dict(old_instance)

        kwargs: dict[str, Any] = {}

        if data.nome is not None:
            kwargs["nome"] = data.nome
        if data.endereco is not None:
            kwargs["endereco"] = data.endereco
        if data.numero is not None:
            kwargs["numero"] = data.numero
        if data.complemento is not None:
            kwargs["complemento"] = data.complemento
        if data.bairro is not None:
            kwargs["bairro"] = data.bairro
        if data.municipio is not None:
            kwargs["municipio"] = data.municipio
        if data.estado is not None:
            kwargs["estado"] = data.estado
        if data.cep is not None:
            kwargs["cep"] = data.cep
        if data.localizacao_descritiva is not None:
            kwargs["localizacao_descritiva"] = data.localizacao_descritiva
        if data.referencia_local is not None:
            kwargs["referencia_local"] = data.referencia_local
        if data.latitude is not None:
            kwargs["latitude"] = data.latitude
        if data.longitude is not None:
            kwargs["longitude"] = data.longitude
        if data.area_total is not None:
            kwargs["area_total"] = data.area_total

        result = await self.repo.update(propriedade_id, **kwargs)
        if usuario_id is not None:
            await self.auditoria.registrar(
                entidade=ENTIDADE,
                entidade_id=propriedade_id,
                acao="ATUALIZACAO",
                valor_anterior=old_values,
                valor_novo=entity_to_dict(result),
                usuario_id=usuario_id,
            )
        return result

    async def delete_propriedade(self, propriedade_id: int, usuario_id: int | None = None) -> Propriedade:
        """Soft-delete a property. Raises DependencyActiveError if it has active orders."""
        await self.repo.get_by_id(propriedade_id)

        if await self.repo.has_active_orders(propriedade_id):
            raise DependencyActiveError(
                "Propriedade possui Ordens de Serviço não canceladas"
            )

        old_instance = await self.repo.get_by_id(propriedade_id)
        old_values = entity_to_dict(old_instance)
        result = await self.repo.soft_delete(propriedade_id)
        if usuario_id is not None:
            await self.auditoria.registrar(
                entidade=ENTIDADE,
                entidade_id=propriedade_id,
                acao="EXCLUSAO",
                valor_anterior=old_values,
                valor_novo=entity_to_dict(result),
                usuario_id=usuario_id,
            )
        return result
