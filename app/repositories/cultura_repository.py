"""Repository for Cultura entity with nome uniqueness and dependency checks."""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateEntityError
from app.models.models import Cultura, Talhao
from app.repositories.base_repository import BaseRepository


class CulturaRepository(BaseRepository[Cultura]):
    """Cultura repository extending BaseRepository with nome lookup and talhão check."""

    def __init__(self, db: AsyncSession):
        super().__init__(Cultura, db)

    async def get_by_nome(self, nome: str) -> Cultura | None:
        """Find a cultura by nome. Returns None if not found."""
        result = await self.db.execute(
            select(Cultura).where(Cultura.nome == nome)
        )
        return result.scalar_one_or_none()

    async def has_active_talhoes(self, cultura_id: int) -> bool:
        """Check if the cultura has any Talhão with ativo=True."""
        result = await self.db.execute(
            select(func.count())
            .select_from(Talhao)
            .where(
                Talhao.cultura_id == cultura_id,
                Talhao.ativo == True,
            )
        )
        count = result.scalar() or 0
        return count > 0

    async def create(self, **kwargs) -> Cultura:
        """Create a cultura, raising DuplicateEntityError if nome already exists."""
        existing = await self.get_by_nome(kwargs.get("nome", ""))
        if existing:
            raise DuplicateEntityError("Cultura com este nome já existe")
        return await super().create(**kwargs)
