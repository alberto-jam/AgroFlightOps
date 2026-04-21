"""Repository for Drone entity with identificacao uniqueness and mission dependency checks."""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateEntityError
from app.models.enums import MissaoStatus
from app.models.models import Drone, Missao
from app.repositories.base_repository import BaseRepository


class DroneRepository(BaseRepository[Drone]):
    """Drone repository extending BaseRepository with identificacao lookup and mission check."""

    def __init__(self, db: AsyncSession):
        super().__init__(Drone, db)

    async def get_by_identificacao(self, identificacao: str) -> Drone | None:
        """Find a drone by identificacao. Returns None if not found."""
        result = await self.db.execute(
            select(Drone).where(Drone.identificacao == identificacao)
        )
        return result.scalar_one_or_none()

    async def has_active_missions(self, drone_id: int) -> bool:
        """Check if the drone has any Missão with status EM_EXECUCAO or AGENDADA."""
        result = await self.db.execute(
            select(func.count())
            .select_from(Missao)
            .where(
                Missao.drone_id == drone_id,
                Missao.status.in_([
                    MissaoStatus.EM_EXECUCAO.value,
                    MissaoStatus.AGENDADA.value,
                ]),
            )
        )
        count = result.scalar() or 0
        return count > 0

    async def create(self, **kwargs) -> Drone:
        """Create a drone, raising DuplicateEntityError if identificacao already exists."""
        existing = await self.get_by_identificacao(kwargs.get("identificacao", ""))
        if existing:
            raise DuplicateEntityError(
                "Drone com esta identificação já existe"
            )
        return await super().create(**kwargs)
