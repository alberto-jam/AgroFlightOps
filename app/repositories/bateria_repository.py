"""Repository for Bateria entity with identificacao uniqueness and mission availability checks."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateEntityError
from app.models.enums import BateriaStatus
from app.models.models import Bateria
from app.repositories.base_repository import BaseRepository


class BateriaRepository(BaseRepository[Bateria]):
    """Bateria repository extending BaseRepository with identificacao lookup and mission availability."""

    def __init__(self, db: AsyncSession):
        super().__init__(Bateria, db)

    async def get_by_identificacao(self, identificacao: str) -> Bateria | None:
        """Find a bateria by identificacao. Returns None if not found."""
        result = await self.db.execute(
            select(Bateria).where(Bateria.identificacao == identificacao)
        )
        return result.scalar_one_or_none()

    def is_available_for_mission(self, bateria: Bateria) -> bool:
        """Check if a bateria can be associated to a mission.

        Returns False if status is REPROVADA or DESCARTADA.
        """
        return bateria.status not in (
            BateriaStatus.REPROVADA.value,
            BateriaStatus.DESCARTADA.value,
        )

    async def create(self, **kwargs) -> Bateria:
        """Create a bateria, raising DuplicateEntityError if identificacao already exists."""
        existing = await self.get_by_identificacao(kwargs.get("identificacao", ""))
        if existing:
            raise DuplicateEntityError(
                "Bateria com esta identificação já existe"
            )
        return await super().create(**kwargs)
