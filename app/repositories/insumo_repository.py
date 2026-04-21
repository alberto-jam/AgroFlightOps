"""Repository for Insumo entity."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Insumo
from app.repositories.base_repository import BaseRepository


class InsumoRepository(BaseRepository[Insumo]):
    """Insumo repository extending BaseRepository."""

    def __init__(self, db: AsyncSession):
        super().__init__(Insumo, db)
