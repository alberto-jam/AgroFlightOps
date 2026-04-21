"""Repository for Cliente entity with dependency check for soft-delete."""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import OrdemServicoStatus
from app.models.models import Cliente, OrdemServico
from app.repositories.base_repository import BaseRepository


class ClienteRepository(BaseRepository[Cliente]):
    """Cliente repository extending BaseRepository with active-orders check."""

    def __init__(self, db: AsyncSession):
        super().__init__(Cliente, db)

    async def has_active_orders(self, cliente_id: int) -> bool:
        """Check if the client has any OrdemServico with status != CANCELADA."""
        result = await self.db.execute(
            select(func.count())
            .select_from(OrdemServico)
            .where(
                OrdemServico.cliente_id == cliente_id,
                OrdemServico.status != OrdemServicoStatus.CANCELADA.value,
            )
        )
        count = result.scalar() or 0
        return count > 0
