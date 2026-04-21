"""Business logic for Drone CRUD operations."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    DependencyActiveError,
    DuplicateEntityError,
)
from app.models.enums import DroneStatus
from app.models.models import Drone
from app.repositories.base_repository import PaginatedResult
from app.repositories.drone_repository import DroneRepository
from app.schemas.drone import DroneCreate, DroneUpdate
from app.services.auditoria_service import AuditoriaService, entity_to_dict

ENTIDADE = "DRONE"


class DroneService:
    """Service layer for Drone operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = DroneRepository(db)
        self.auditoria = AuditoriaService(db)

    async def create_drone(self, data: DroneCreate, usuario_id: int | None = None) -> Drone:
        """Create a new drone with status DISPONIVEL."""
        result = await self.repo.create(
            identificacao=data.identificacao,
            modelo=data.modelo,
            fabricante=data.fabricante,
            capacidade_litros=data.capacidade_litros,
            status=DroneStatus.DISPONIVEL.value,
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

    async def get_drone(self, drone_id: int) -> Drone:
        """Get a drone by ID."""
        return await self.repo.get_by_id(drone_id)

    async def list_drones(
        self,
        page: int = 1,
        page_size: int = 20,
        status: DroneStatus | None = None,
        modelo: str | None = None,
        ativo: bool | None = None,
    ) -> PaginatedResult[Drone]:
        """List drones with optional filters by status and modelo."""
        filters: list[Any] = []
        if status is not None:
            filters.append(Drone.status == status.value)
        if modelo is not None:
            filters.append(Drone.modelo.ilike(f"%{modelo}%"))
        if ativo is not None:
            filters.append(Drone.ativo == ativo)

        return await self.repo.list_paginated(
            page=page,
            page_size=page_size,
            filters=filters if filters else None,
        )

    async def update_drone(self, drone_id: int, data: DroneUpdate, usuario_id: int | None = None) -> Drone:
        """Update a drone. Validates identificacao uniqueness and status change rules."""
        old_instance = await self.repo.get_by_id(drone_id)
        old_values = entity_to_dict(old_instance)

        kwargs: dict[str, Any] = {}

        if data.identificacao is not None:
            existing = await self.repo.get_by_identificacao(data.identificacao)
            if existing and existing.id != drone_id:
                raise DuplicateEntityError(
                    "Drone com esta identificação já existe"
                )
            kwargs["identificacao"] = data.identificacao

        if data.modelo is not None:
            kwargs["modelo"] = data.modelo
        if data.fabricante is not None:
            kwargs["fabricante"] = data.fabricante
        if data.capacidade_litros is not None:
            kwargs["capacidade_litros"] = data.capacidade_litros

        if data.status is not None:
            # Check if transitioning to INATIVO or EM_MANUTENCAO
            if data.status in (DroneStatus.INATIVO, DroneStatus.EM_MANUTENCAO):
                if await self.repo.has_active_missions(drone_id):
                    raise DependencyActiveError(
                        "Drone possui Missões EM_EXECUCAO ou AGENDADA"
                    )
            kwargs["status"] = data.status.value

        result = await self.repo.update(drone_id, **kwargs)
        if usuario_id is not None:
            await self.auditoria.registrar(
                entidade=ENTIDADE,
                entidade_id=drone_id,
                acao="ATUALIZACAO",
                valor_anterior=old_values,
                valor_novo=entity_to_dict(result),
                usuario_id=usuario_id,
            )
        return result

    async def delete_drone(self, drone_id: int, usuario_id: int | None = None) -> Drone:
        """Soft-delete a drone. Raises DependencyActiveError if it has active missions."""
        await self.repo.get_by_id(drone_id)

        if await self.repo.has_active_missions(drone_id):
            raise DependencyActiveError(
                "Drone possui Missões EM_EXECUCAO ou AGENDADA"
            )

        old_instance = await self.repo.get_by_id(drone_id)
        old_values = entity_to_dict(old_instance)
        result = await self.repo.soft_delete(drone_id)
        if usuario_id is not None:
            await self.auditoria.registrar(
                entidade=ENTIDADE,
                entidade_id=drone_id,
                acao="EXCLUSAO",
                valor_anterior=old_values,
                valor_novo=entity_to_dict(result),
                usuario_id=usuario_id,
            )
        return result
