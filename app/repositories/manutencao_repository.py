"""Repository for Manutencao entity with drone-based and date-period filters."""

from datetime import date
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Manutencao
from app.repositories.base_repository import BaseRepository, PaginatedResult


class ManutencaoRepository(BaseRepository[Manutencao]):
    """Manutencao repository extending BaseRepository with filtered listing."""

    def __init__(self, db: AsyncSession):
        super().__init__(Manutencao, db)

    async def list_filtered(
        self,
        page: int = 1,
        page_size: int = 20,
        drone_id: int | None = None,
        data_inicio: date | None = None,
        data_fim: date | None = None,
    ) -> PaginatedResult[Manutencao]:
        """List manutencoes with optional filters by drone_id and date period."""
        filters: list[Any] = []
        if drone_id is not None:
            filters.append(Manutencao.drone_id == drone_id)
        if data_inicio is not None:
            filters.append(Manutencao.data_manutencao >= data_inicio)
        if data_fim is not None:
            filters.append(Manutencao.data_manutencao <= data_fim)

        return await self.list_paginated(
            page=page,
            page_size=page_size,
            filters=filters if filters else None,
            order_by=Manutencao.data_manutencao.desc(),
        )
