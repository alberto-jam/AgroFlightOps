"""Repository for Missao entity with filtered listing."""

import uuid
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import MissaoStatus
from app.models.models import ConsumoInsumoMissao, HistoricoStatusMissao, Missao, MissaoBateria, ReservaInsumo
from app.repositories.base_repository import BaseRepository, PaginatedResult


class MissaoRepository(BaseRepository[Missao]):
    """Missao repository extending BaseRepository with filtered listing."""

    def __init__(self, db: AsyncSession):
        super().__init__(Missao, db)

    def _generate_codigo(self) -> str:
        """Generate a unique Missao code."""
        return f"MS-{uuid.uuid4().hex[:8].upper()}"

    async def create_missao(
        self,
        ordem_servico_id: int,
        piloto_id: int,
        drone_id: int,
        data_agendada: date,
        hora_agendada: Any,
        area_prevista: Any,
        volume_previsto: Any,
        tecnico_id: int | None = None,
        janela_operacional: str | None = None,
        restricoes: str | None = None,
        observacoes_planejamento: str | None = None,
        latitude_operacao: Any | None = None,
        longitude_operacao: Any | None = None,
        endereco_operacao: str | None = None,
        referencia_operacao: str | None = None,
    ) -> Missao:
        """Create a new Missao with generated code and initial status RASCUNHO."""
        codigo = self._generate_codigo()
        return await self.create(
            codigo=codigo,
            ordem_servico_id=ordem_servico_id,
            piloto_id=piloto_id,
            tecnico_id=tecnico_id,
            drone_id=drone_id,
            data_agendada=data_agendada,
            hora_agendada=hora_agendada,
            area_prevista=area_prevista,
            volume_previsto=volume_previsto,
            janela_operacional=janela_operacional,
            restricoes=restricoes,
            observacoes_planejamento=observacoes_planejamento,
            latitude_operacao=latitude_operacao,
            longitude_operacao=longitude_operacao,
            endereco_operacao=endereco_operacao,
            referencia_operacao=referencia_operacao,
            status=MissaoStatus.RASCUNHO.value,
        )

    async def list_filtered(
        self,
        page: int = 1,
        page_size: int = 20,
        status: MissaoStatus | None = None,
        piloto_id: int | None = None,
        drone_id: int | None = None,
        data_agendada: date | None = None,
        ordem_servico_id: int | None = None,
    ) -> PaginatedResult[Missao]:
        """List Missoes with optional filters."""
        filters: list[Any] = []

        if status is not None:
            filters.append(Missao.status == status.value)
        if piloto_id is not None:
            filters.append(Missao.piloto_id == piloto_id)
        if drone_id is not None:
            filters.append(Missao.drone_id == drone_id)
        if data_agendada is not None:
            filters.append(Missao.data_agendada == data_agendada)
        if ordem_servico_id is not None:
            filters.append(Missao.ordem_servico_id == ordem_servico_id)

        return await self.list_paginated(
            page=page,
            page_size=page_size,
            filters=filters if filters else None,
            order_by=Missao.id.desc(),
        )

    async def create_historico(
        self,
        missao_id: int,
        status_anterior: str | None,
        status_novo: str,
        motivo: str | None,
        alterado_por: int,
    ) -> HistoricoStatusMissao:
        """Create a history record for a status transition."""
        historico = HistoricoStatusMissao(
            missao_id=missao_id,
            status_anterior=status_anterior,
            status_novo=status_novo,
            motivo=motivo,
            alterado_por=alterado_por,
        )
        self.db.add(historico)
        await self.db.flush()
        await self.db.refresh(historico)
        return historico

    async def list_historico(self, missao_id: int) -> list[HistoricoStatusMissao]:
        """List all history records for a Missao ordered by created_at."""
        result = await self.db.execute(
            select(HistoricoStatusMissao)
            .where(HistoricoStatusMissao.missao_id == missao_id)
            .order_by(HistoricoStatusMissao.created_at)
        )
        return list(result.scalars().all())

    async def create_missao_bateria(
        self, missao_id: int, bateria_id: int, ordem_uso: int
    ) -> MissaoBateria:
        """Create a battery association for a mission."""
        mb = MissaoBateria(
            missao_id=missao_id, bateria_id=bateria_id, ordem_uso=ordem_uso
        )
        self.db.add(mb)
        await self.db.flush()
        await self.db.refresh(mb)
        return mb

    async def list_missao_baterias(self, missao_id: int) -> list[MissaoBateria]:
        """List all battery associations for a mission."""
        result = await self.db.execute(
            select(MissaoBateria)
            .where(MissaoBateria.missao_id == missao_id)
            .order_by(MissaoBateria.ordem_uso)
        )
        return list(result.scalars().all())

    async def create_reserva_insumo(
        self, missao_id: int, insumo_id: int, quantidade_prevista: Any, unidade_medida: str
    ) -> ReservaInsumo:
        """Create an insumo reservation for a mission."""
        reserva = ReservaInsumo(
            missao_id=missao_id,
            insumo_id=insumo_id,
            quantidade_prevista=quantidade_prevista,
            unidade_medida=unidade_medida,
        )
        self.db.add(reserva)
        await self.db.flush()
        await self.db.refresh(reserva)
        return reserva

    async def list_reservas_insumo(self, missao_id: int) -> list[ReservaInsumo]:
        """List all insumo reservations for a mission."""
        result = await self.db.execute(
            select(ReservaInsumo)
            .where(ReservaInsumo.missao_id == missao_id)
            .order_by(ReservaInsumo.id)
        )
        return list(result.scalars().all())

    async def create_consumo_insumo(
        self,
        missao_id: int,
        insumo_id: int,
        quantidade_realizada: Any,
        unidade_medida: str,
        observacoes: str | None = None,
        justificativa_excesso: str | None = None,
    ) -> ConsumoInsumoMissao:
        """Create a consumo insumo record for a mission."""
        consumo = ConsumoInsumoMissao(
            missao_id=missao_id,
            insumo_id=insumo_id,
            quantidade_realizada=quantidade_realizada,
            unidade_medida=unidade_medida,
            observacoes=observacoes,
            justificativa_excesso=justificativa_excesso,
        )
        self.db.add(consumo)
        await self.db.flush()
        await self.db.refresh(consumo)
        return consumo

    async def list_consumos_insumo(self, missao_id: int) -> list[ConsumoInsumoMissao]:
        """List all consumo insumo records for a mission."""
        result = await self.db.execute(
            select(ConsumoInsumoMissao)
            .where(ConsumoInsumoMissao.missao_id == missao_id)
            .order_by(ConsumoInsumoMissao.id)
        )
        return list(result.scalars().all())
