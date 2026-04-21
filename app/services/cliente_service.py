"""Business logic for Cliente CRUD operations."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DependencyActiveError, EntityNotFoundError
from app.models.models import Cliente
from app.repositories.base_repository import PaginatedResult
from app.repositories.cliente_repository import ClienteRepository
from app.schemas.cliente import ClienteCreate, ClienteUpdate
from app.services.auditoria_service import AuditoriaService, entity_to_dict

ENTIDADE = "CLIENTE"


class ClienteService:
    """Service layer for Cliente operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ClienteRepository(db)
        self.auditoria = AuditoriaService(db)

    async def create_cliente(self, data: ClienteCreate, usuario_id: int | None = None) -> Cliente:
        """Create a new client."""
        result = await self.repo.create(
            nome=data.nome,
            cpf_cnpj=data.cpf_cnpj,
            telefone=data.telefone,
            email=data.email,
            endereco=data.endereco,
            numero=data.numero,
            complemento=data.complemento,
            bairro=data.bairro,
            municipio=data.municipio,
            estado=data.estado,
            cep=data.cep,
            latitude=data.latitude,
            longitude=data.longitude,
            referencia_local=data.referencia_local,
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

    async def get_cliente(self, cliente_id: int) -> Cliente:
        """Get a client by ID."""
        return await self.repo.get_by_id(cliente_id)

    async def list_clientes(
        self,
        page: int = 1,
        page_size: int = 20,
        nome: str | None = None,
        cpf_cnpj: str | None = None,
        ativo: bool | None = None,
    ) -> PaginatedResult[Cliente]:
        """List clients with optional filters for nome, cpf_cnpj and status."""
        filters: list[Any] = []
        if nome is not None:
            filters.append(Cliente.nome.ilike(f"%{nome}%"))
        if cpf_cnpj is not None:
            filters.append(Cliente.cpf_cnpj.ilike(f"%{cpf_cnpj}%"))
        if ativo is not None:
            filters.append(Cliente.ativo == ativo)

        return await self.repo.list_paginated(
            page=page,
            page_size=page_size,
            filters=filters if filters else None,
        )

    async def update_cliente(self, cliente_id: int, data: ClienteUpdate, usuario_id: int | None = None) -> Cliente:
        """Update a client."""
        old_instance = await self.repo.get_by_id(cliente_id)
        old_values = entity_to_dict(old_instance)

        kwargs: dict[str, Any] = {}

        if data.nome is not None:
            kwargs["nome"] = data.nome
        if data.cpf_cnpj is not None:
            kwargs["cpf_cnpj"] = data.cpf_cnpj
        if data.telefone is not None:
            kwargs["telefone"] = data.telefone
        if data.email is not None:
            kwargs["email"] = data.email
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
        if data.latitude is not None:
            kwargs["latitude"] = data.latitude
        if data.longitude is not None:
            kwargs["longitude"] = data.longitude
        if data.referencia_local is not None:
            kwargs["referencia_local"] = data.referencia_local

        result = await self.repo.update(cliente_id, **kwargs)
        if usuario_id is not None:
            await self.auditoria.registrar(
                entidade=ENTIDADE,
                entidade_id=cliente_id,
                acao="ATUALIZACAO",
                valor_anterior=old_values,
                valor_novo=entity_to_dict(result),
                usuario_id=usuario_id,
            )
        return result

    async def delete_cliente(self, cliente_id: int, usuario_id: int | None = None) -> Cliente:
        """Soft-delete a client (set ativo=False). Raises DependencyActiveError if client has non-CANCELADA orders."""
        await self.repo.get_by_id(cliente_id)

        if await self.repo.has_active_orders(cliente_id):
            raise DependencyActiveError(
                "Cliente possui Ordens de Serviço não canceladas"
            )

        old_instance = await self.repo.get_by_id(cliente_id)
        old_values = entity_to_dict(old_instance)
        result = await self.repo.soft_delete(cliente_id)
        if usuario_id is not None:
            await self.auditoria.registrar(
                entidade=ENTIDADE,
                entidade_id=cliente_id,
                acao="EXCLUSAO",
                valor_anterior=old_values,
                valor_novo=entity_to_dict(result),
                usuario_id=usuario_id,
            )
        return result
