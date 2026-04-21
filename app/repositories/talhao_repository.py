"""Repository for Talhao entity with uniqueness check and dependency protection."""

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateEntityError
from app.models.models import Talhao, OrdemServico
from app.models.enums import OrdemServicoStatus
from app.repositories.base_repository import BaseRepository


class TalhaoRepository(BaseRepository[Talhao]):
    """Talhao repository extending BaseRepository with composite uniqueness and active-orders check."""

    def __init__(self, db: AsyncSession):
        super().__init__(Talhao, db)

    async def get_by_propriedade_and_nome(
        self, propriedade_id: int, nome: str
    ) -> Talhao | None:
        """Find a talhão by (propriedade_id, nome). Returns None if not found."""
        result = await self.db.execute(
            select(Talhao).where(
                and_(
                    Talhao.propriedade_id == propriedade_id,
                    Talhao.nome == nome,
                )
            )
        )
        return result.scalar_one_or_none()

    async def has_active_orders(self, talhao_id: int) -> bool:
        """Check if the talhão has any OrdemServico with status != CANCELADA."""
        result = await self.db.execute(
            select(func.count())
            .select_from(OrdemServico)
            .where(
                OrdemServico.talhao_id == talhao_id,
                OrdemServico.status != OrdemServicoStatus.CANCELADA.value,
            )
        )
        count = result.scalar() or 0
        return count > 0

    async def create(self, **kwargs) -> Talhao:
        """Create a talhão, raising DuplicateEntityError if (propriedade_id, nome) already exists."""
        existing = await self.get_by_propriedade_and_nome(
            kwargs.get("propriedade_id", 0), kwargs.get("nome", "")
        )
        if existing:
            raise DuplicateEntityError(
                "Talhão com este nome já existe nesta propriedade"
            )
        return await super().create(**kwargs)
