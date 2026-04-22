"""Repository for TipoOcorrencia entity with nome uniqueness and dependency checks."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateEntityError
from app.models.models import Ocorrencia, TipoOcorrencia
from app.repositories.base_repository import BaseRepository


class TipoOcorrenciaRepository(BaseRepository[TipoOcorrencia]):
    """TipoOcorrencia repository with nome lookup and ocorrência dependency check."""

    def __init__(self, db: AsyncSession):
        super().__init__(TipoOcorrencia, db)

    async def get_by_nome(self, nome: str) -> TipoOcorrencia | None:
        result = await self.db.execute(
            select(TipoOcorrencia).where(TipoOcorrencia.nome == nome)
        )
        return result.scalar_one_or_none()

    async def has_active_ocorrencias(self, tipo_id: int) -> bool:
        result = await self.db.execute(
            select(func.count())
            .select_from(Ocorrencia)
            .where(Ocorrencia.tipo_ocorrencia_id == tipo_id)
        )
        return (result.scalar() or 0) > 0

    async def create(self, **kwargs) -> TipoOcorrencia:
        existing = await self.get_by_nome(kwargs.get("nome", ""))
        if existing:
            raise DuplicateEntityError("Tipo de ocorrência com este nome já existe")
        return await super().create(**kwargs)
