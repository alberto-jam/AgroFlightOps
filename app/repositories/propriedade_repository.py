"""Repository for Propriedade entity with dependency check for soft-delete."""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Propriedade, OrdemServico
from app.models.enums import OrdemServicoStatus
from app.repositories.base_repository import BaseRepository


class PropriedadeRepository(BaseRepository[Propriedade]):
    """Propriedade repository extending BaseRepository with active-orders check."""

    def __init__(self, db: AsyncSession):
        super().__init__(Propriedade, db)

    async def has_active_orders(self, propriedade_id: int) -> bool:
        """Check if the property has any OrdemServico with status != CANCELADA."""
        result = await self.db.execute(
            select(func.count())
            .select_from(OrdemServico)
            .where(
                OrdemServico.propriedade_id == propriedade_id,
                OrdemServico.status != OrdemServicoStatus.CANCELADA.value,
            )
        )
        count = result.scalar() or 0
        return count > 0
