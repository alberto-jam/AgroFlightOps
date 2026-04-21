"""Business logic for Usuario CRUD operations."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateEntityError, EntityNotFoundError
from app.core.security import hash_password
from app.models.models import Usuario
from app.repositories.base_repository import PaginatedResult
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.services.auditoria_service import AuditoriaService, entity_to_dict

ENTIDADE = "USUARIO"


class UsuarioService:
    """Service layer for Usuario operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UsuarioRepository(db)
        self.auditoria = AuditoriaService(db)

    async def create_usuario(self, data: UsuarioCreate, usuario_id: int | None = None) -> Usuario:
        """Create a new user with hashed password."""
        result = await self.repo.create(
            nome=data.nome,
            email=data.email,
            senha_hash=hash_password(data.senha),
            perfil_id=data.perfil_id,
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

    async def get_usuario(self, usuario_id: int) -> Usuario:
        """Get a user by ID."""
        return await self.repo.get_by_id(usuario_id)

    async def list_usuarios(
        self,
        page: int = 1,
        page_size: int = 20,
        perfil_id: int | None = None,
        ativo: bool | None = None,
    ) -> PaginatedResult[Usuario]:
        """List users with optional filters for perfil and status."""
        filters: list[Any] = []
        if perfil_id is not None:
            filters.append(Usuario.perfil_id == perfil_id)
        if ativo is not None:
            filters.append(Usuario.ativo == ativo)

        return await self.repo.list_paginated(
            page=page,
            page_size=page_size,
            filters=filters if filters else None,
        )

    async def update_usuario(self, usuario_id: int, data: UsuarioUpdate, current_user_id: int | None = None) -> Usuario:
        """Update a user. Hashes password if changed, checks email uniqueness if changed."""
        old_instance = await self.repo.get_by_id(usuario_id)
        old_values = entity_to_dict(old_instance)

        kwargs: dict[str, Any] = {}

        if data.email is not None:
            existing = await self.repo.get_by_email(data.email)
            if existing and existing.id != usuario_id:
                raise DuplicateEntityError("Email já cadastrado")
            kwargs["email"] = data.email

        if data.nome is not None:
            kwargs["nome"] = data.nome

        if data.perfil_id is not None:
            kwargs["perfil_id"] = data.perfil_id

        if data.senha is not None:
            kwargs["senha_hash"] = hash_password(data.senha)

        result = await self.repo.update(usuario_id, **kwargs)
        if current_user_id is not None:
            await self.auditoria.registrar(
                entidade=ENTIDADE,
                entidade_id=usuario_id,
                acao="ATUALIZACAO",
                valor_anterior=old_values,
                valor_novo=entity_to_dict(result),
                usuario_id=current_user_id,
            )
        return result

    async def delete_usuario(self, usuario_id: int, current_user_id: int | None = None) -> Usuario:
        """Soft-delete a user (set ativo=False)."""
        old_instance = await self.repo.get_by_id(usuario_id)
        old_values = entity_to_dict(old_instance)
        result = await self.repo.soft_delete(usuario_id)
        if current_user_id is not None:
            await self.auditoria.registrar(
                entidade=ENTIDADE,
                entidade_id=usuario_id,
                acao="EXCLUSAO",
                valor_anterior=old_values,
                valor_novo=entity_to_dict(result),
                usuario_id=current_user_id,
            )
        return result
