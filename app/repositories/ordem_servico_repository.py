"""Repository for OrdemServico entity with filtered listing."""

import uuid
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import OrdemServicoStatus, Prioridade
from app.models.models import HistoricoStatusOS, OrdemServico
from app.repositories.base_repository import BaseRepository, PaginatedResult


class OrdemServicoRepository(BaseRepository[OrdemServico]):
    """OrdemServico repository extending BaseRepository with filtered listing."""

    def __init__(self, db: AsyncSession):
        super().__init__(OrdemServico, db)

    def _generate_codigo(self) -> str:
        """Generate a unique OS code."""
        return f"OS-{uuid.uuid4().hex[:8].upper()}"

    async def create_ordem_servico(
        self,
        cliente_id: int,
        propriedade_id: int,
        talhao_id: int,
        cultura_id: int,
        tipo_aplicacao: str,
        prioridade: str,
        descricao: str | None,
        data_prevista: date,
        criado_por: int,
    ) -> OrdemServico:
        """Create a new OrdemServico with generated code and initial status RASCUNHO."""
        codigo = self._generate_codigo()
        return await self.create(
            codigo=codigo,
            cliente_id=cliente_id,
            propriedade_id=propriedade_id,
            talhao_id=talhao_id,
            cultura_id=cultura_id,
            tipo_aplicacao=tipo_aplicacao,
            prioridade=prioridade,
            descricao=descricao,
            data_prevista=data_prevista,
            status=OrdemServicoStatus.RASCUNHO.value,
            criado_por=criado_por,
        )

    async def list_filtered(
        self,
        page: int = 1,
        page_size: int = 20,
        status: OrdemServicoStatus | None = None,
        cliente_id: int | None = None,
        propriedade_id: int | None = None,
        prioridade: Prioridade | None = None,
        data_prevista: date | None = None,
    ) -> PaginatedResult[OrdemServico]:
        """List OrdemServico with optional filters."""
        filters: list[Any] = []

        if status is not None:
            filters.append(OrdemServico.status == status.value)
        if cliente_id is not None:
            filters.append(OrdemServico.cliente_id == cliente_id)
        if propriedade_id is not None:
            filters.append(OrdemServico.propriedade_id == propriedade_id)
        if prioridade is not None:
            filters.append(OrdemServico.prioridade == prioridade.value)
        if data_prevista is not None:
            filters.append(OrdemServico.data_prevista == data_prevista)

        return await self.list_paginated(
            page=page,
            page_size=page_size,
            filters=filters if filters else None,
            order_by=OrdemServico.id.desc(),
        )

    async def create_historico(
        self,
        ordem_servico_id: int,
        status_anterior: str | None,
        status_novo: str,
        motivo: str | None,
        alterado_por: int,
    ) -> HistoricoStatusOS:
        """Create a history record for a status transition."""
        historico = HistoricoStatusOS(
            ordem_servico_id=ordem_servico_id,
            status_anterior=status_anterior,
            status_novo=status_novo,
            motivo=motivo,
            alterado_por=alterado_por,
        )
        self.db.add(historico)
        await self.db.flush()
        await self.db.refresh(historico)
        return historico

    async def list_historico(self, ordem_servico_id: int) -> list[HistoricoStatusOS]:
        """List all history records for an OrdemServico ordered by created_at."""
        result = await self.db.execute(
            select(HistoricoStatusOS)
            .where(HistoricoStatusOS.ordem_servico_id == ordem_servico_id)
            .order_by(HistoricoStatusOS.created_at)
        )
        return list(result.scalars().all())
