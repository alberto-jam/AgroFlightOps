"""Business logic for FinanceiroMissao operations."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessRuleViolationError, EntityNotFoundError
from app.models.enums import MissaoStatus
from app.models.models import FinanceiroMissao, Missao
from app.repositories.missao_repository import MissaoRepository
from app.schemas.financeiro import FinanceiroMissaoUpdate


class FinanceiroService:
    """Service layer for FinanceiroMissao operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = MissaoRepository(db)

    async def _get_financeiro(self, missao_id: int) -> FinanceiroMissao:
        """Get the FinanceiroMissao record for a mission."""
        result = await self.db.execute(
            select(FinanceiroMissao).where(FinanceiroMissao.missao_id == missao_id)
        )
        financeiro = result.scalar_one_or_none()
        if financeiro is None:
            raise EntityNotFoundError(
                f"Registro financeiro para missão id={missao_id} não encontrado"
            )
        return financeiro

    async def get_financeiro_by_missao(self, missao_id: int) -> FinanceiroMissao:
        """Get the financial record for a mission."""
        # Validate mission exists
        await self.repo.get_by_id(missao_id)
        return await self._get_financeiro(missao_id)

    async def update_financeiro(
        self, missao_id: int, data: FinanceiroMissaoUpdate
    ) -> FinanceiroMissao:
        """Update financial data for a mission."""
        await self.repo.get_by_id(missao_id)
        financeiro = await self._get_financeiro(missao_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "status_financeiro" and value is not None:
                setattr(financeiro, field, value.value)
            else:
                setattr(financeiro, field, value)

        await self.db.flush()
        await self.db.refresh(financeiro)
        return financeiro

    async def encerrar_financeiramente(
        self, missao_id: int, usuario_id: int
    ) -> FinanceiroMissao:
        """Close the mission financially.

        Mission must be ENCERRADA_TECNICAMENTE. Sets mission status to
        ENCERRADA_FINANCEIRAMENTE, records timestamps and fechado_por.
        """
        missao = await self.repo.get_by_id(missao_id)

        if missao.status != MissaoStatus.ENCERRADA_TECNICAMENTE.value:
            raise BusinessRuleViolationError(
                "Missão deve estar ENCERRADA_TECNICAMENTE para encerramento financeiro"
            )

        financeiro = await self._get_financeiro(missao_id)

        now = datetime.utcnow()

        # Update mission status
        missao.status = MissaoStatus.ENCERRADA_FINANCEIRAMENTE.value
        missao.encerrado_financeiramente_em = now

        # Update financeiro record
        financeiro.fechado_por = usuario_id
        financeiro.fechado_em = now

        await self.db.flush()

        # Record status transition in history
        await self.repo.create_historico(
            missao_id=missao_id,
            status_anterior=MissaoStatus.ENCERRADA_TECNICAMENTE.value,
            status_novo=MissaoStatus.ENCERRADA_FINANCEIRAMENTE.value,
            motivo=None,
            alterado_por=usuario_id,
        )

        await self.db.refresh(financeiro)
        return financeiro
