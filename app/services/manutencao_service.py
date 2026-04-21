"""Business logic for Manutencao CRUD operations."""

from datetime import date
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessRuleViolationError
from app.models.enums import DroneStatus
from app.models.models import Manutencao
from app.repositories.base_repository import PaginatedResult
from app.repositories.drone_repository import DroneRepository
from app.repositories.manutencao_repository import ManutencaoRepository
from app.schemas.manutencao import ManutencaoCreate, ManutencaoUpdate


class ManutencaoService:
    """Service layer for Manutencao operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ManutencaoRepository(db)
        self.drone_repo = DroneRepository(db)

    async def create_manutencao(self, data: ManutencaoCreate) -> Manutencao:
        """Create a maintenance record.

        - Validates drone exists
        - Validates proxima_manutencao >= data_manutencao
        - Updates drone.ultima_manutencao_em
        - Changes drone status to EM_MANUTENCAO if no active missions
        """
        drone = await self.drone_repo.get_by_id(data.drone_id)

        if data.proxima_manutencao is not None and data.proxima_manutencao < data.data_manutencao:
            raise BusinessRuleViolationError(
                "proxima_manutencao deve ser maior ou igual a data_manutencao"
            )

        manutencao = await self.repo.create(
            drone_id=data.drone_id,
            tipo=data.tipo,
            descricao=data.descricao,
            data_manutencao=data.data_manutencao,
            proxima_manutencao=data.proxima_manutencao,
            horas_na_data=data.horas_na_data,
        )

        # Update drone ultima_manutencao_em
        drone.ultima_manutencao_em = data.data_manutencao

        # Change drone status to EM_MANUTENCAO if applicable
        if not await self.drone_repo.has_active_missions(drone.id):
            drone.status = DroneStatus.EM_MANUTENCAO.value

        await self.db.flush()
        await self.db.refresh(manutencao)

        return manutencao

    async def get_manutencao(self, manutencao_id: int) -> Manutencao:
        """Get a maintenance record by ID."""
        return await self.repo.get_by_id(manutencao_id)

    async def list_manutencoes(
        self,
        page: int = 1,
        page_size: int = 20,
        drone_id: int | None = None,
        data_inicio: date | None = None,
        data_fim: date | None = None,
    ) -> PaginatedResult[Manutencao]:
        """List maintenance records with optional filters."""
        return await self.repo.list_filtered(
            page=page,
            page_size=page_size,
            drone_id=drone_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
        )

    async def update_manutencao(
        self, manutencao_id: int, data: ManutencaoUpdate
    ) -> Manutencao:
        """Update a maintenance record.

        - Re-validates proxima_manutencao >= data_manutencao
        - Updates drone.ultima_manutencao_em if data_manutencao changed
        """
        existing = await self.repo.get_by_id(manutencao_id)

        # Determine effective dates for validation
        effective_data_manutencao = (
            data.data_manutencao if data.data_manutencao is not None else existing.data_manutencao
        )
        effective_proxima = (
            data.proxima_manutencao if data.proxima_manutencao is not None else existing.proxima_manutencao
        )

        if effective_proxima is not None and effective_proxima < effective_data_manutencao:
            raise BusinessRuleViolationError(
                "proxima_manutencao deve ser maior ou igual a data_manutencao"
            )

        kwargs: dict[str, Any] = {}
        if data.tipo is not None:
            kwargs["tipo"] = data.tipo
        if data.descricao is not None:
            kwargs["descricao"] = data.descricao
        if data.data_manutencao is not None:
            kwargs["data_manutencao"] = data.data_manutencao
        if data.proxima_manutencao is not None:
            kwargs["proxima_manutencao"] = data.proxima_manutencao
        if data.horas_na_data is not None:
            kwargs["horas_na_data"] = data.horas_na_data

        manutencao = await self.repo.update(manutencao_id, **kwargs)

        # Update drone ultima_manutencao_em if data_manutencao changed
        if data.data_manutencao is not None:
            drone = await self.drone_repo.get_by_id(existing.drone_id)
            drone.ultima_manutencao_em = data.data_manutencao
            await self.db.flush()

        return manutencao
