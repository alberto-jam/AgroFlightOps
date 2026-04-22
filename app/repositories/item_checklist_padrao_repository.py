"""Repository for ItemChecklistPadrao entity."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateEntityError
from app.models.models import ItemChecklistPadrao
from app.repositories.base_repository import BaseRepository


class ItemChecklistPadraoRepository(BaseRepository[ItemChecklistPadrao]):
    def __init__(self, db: AsyncSession):
        super().__init__(ItemChecklistPadrao, db)

    async def get_by_nome(self, nome_item: str) -> ItemChecklistPadrao | None:
        result = await self.db.execute(
            select(ItemChecklistPadrao).where(ItemChecklistPadrao.nome_item == nome_item)
        )
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> ItemChecklistPadrao:
        existing = await self.get_by_nome(kwargs.get("nome_item", ""))
        if existing:
            raise DuplicateEntityError("Item de checklist padrão com este nome já existe")
        return await super().create(**kwargs)
