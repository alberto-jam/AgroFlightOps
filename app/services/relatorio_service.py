"""Service for operational and financial reports."""

from datetime import date
from decimal import Decimal

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Cliente, Drone, FinanceiroMissao, Missao, OrdemServico


class RelatorioService:
    """Generates aggregated reports for missions, area, finances and drone utilization."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def missoes_por_status(
        self, data_inicio: date, data_fim: date
    ) -> dict:
        """Count missions grouped by status within a date range (based on data_agendada)."""
        stmt = (
            select(Missao.status, func.count().label("total"))
            .where(
                and_(
                    Missao.data_agendada >= data_inicio,
                    Missao.data_agendada <= data_fim,
                )
            )
            .group_by(Missao.status)
        )
        result = await self.db.execute(stmt)
        rows = result.all()

        items = [{"status": row.status, "total": row.total} for row in rows]
        total_geral = sum(item["total"] for item in items)

        return {
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "items": items,
            "total_geral": total_geral,
        }

    async def area_por_cliente(
        self, data_inicio: date, data_fim: date
    ) -> dict:
        """Sum area_realizada grouped by client within a date range.

        Joins Missao → OrdemServico → Cliente. Only missions with area_realizada filled.
        """
        stmt = (
            select(
                Cliente.id.label("cliente_id"),
                Cliente.nome.label("cliente_nome"),
                func.coalesce(func.sum(Missao.area_realizada), Decimal("0")).label(
                    "area_total_pulverizada"
                ),
            )
            .join(OrdemServico, Missao.ordem_servico_id == OrdemServico.id)
            .join(Cliente, OrdemServico.cliente_id == Cliente.id)
            .where(
                and_(
                    Missao.data_agendada >= data_inicio,
                    Missao.data_agendada <= data_fim,
                    Missao.area_realizada.isnot(None),
                )
            )
            .group_by(Cliente.id, Cliente.nome)
            .order_by(Cliente.nome)
        )
        result = await self.db.execute(stmt)
        rows = result.all()

        items = [
            {
                "cliente_id": row.cliente_id,
                "cliente_nome": row.cliente_nome,
                "area_total_pulverizada": row.area_total_pulverizada,
            }
            for row in rows
        ]

        return {
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "items": items,
        }

    async def financeiro_resumo(
        self, data_inicio: date, data_fim: date
    ) -> dict:
        """Financial summary for missions with status ENCERRADA_FINANCEIRAMENTE within a period."""
        stmt = (
            select(
                func.coalesce(func.sum(FinanceiroMissao.custo_estimado), Decimal("0")).label(
                    "total_custo_estimado"
                ),
                func.coalesce(func.sum(FinanceiroMissao.custo_realizado), Decimal("0")).label(
                    "total_custo_realizado"
                ),
                func.coalesce(func.sum(FinanceiroMissao.valor_faturado), Decimal("0")).label(
                    "total_valor_faturado"
                ),
                func.count().label("total_missoes"),
            )
            .join(Missao, FinanceiroMissao.missao_id == Missao.id)
            .where(
                and_(
                    Missao.status == "ENCERRADA_FINANCEIRAMENTE",
                    Missao.data_agendada >= data_inicio,
                    Missao.data_agendada <= data_fim,
                )
            )
        )
        result = await self.db.execute(stmt)
        row = result.one()

        return {
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "total_custo_estimado": row.total_custo_estimado,
            "total_custo_realizado": row.total_custo_realizado,
            "total_valor_faturado": row.total_valor_faturado,
            "total_missoes": row.total_missoes,
        }

    async def utilizacao_drones(
        self, data_inicio: date, data_fim: date
    ) -> dict:
        """Drone utilization report: flight hours per drone within a period.

        Calculates hours from completed missions (those with iniciado_em and finalizado_em)
        within the date range.
        """
        # Calculate hours from missions that have both timestamps (MySQL TIMESTAMPDIFF)
        from sqlalchemy import literal_column

        hours_expr = func.coalesce(
            func.sum(
                func.timestampdiff(
                    literal_column("SECOND"), Missao.iniciado_em, Missao.finalizado_em
                )
            )
            / 3600,
            Decimal("0"),
        )

        stmt = (
            select(
                Drone.id.label("drone_id"),
                Drone.identificacao.label("drone_identificacao"),
                Drone.modelo.label("drone_modelo"),
                hours_expr.label("horas_voadas_periodo"),
                func.count(Missao.id).label("total_missoes"),
            )
            .join(Missao, Drone.id == Missao.drone_id)
            .where(
                and_(
                    Missao.data_agendada >= data_inicio,
                    Missao.data_agendada <= data_fim,
                    Missao.iniciado_em.isnot(None),
                    Missao.finalizado_em.isnot(None),
                )
            )
            .group_by(Drone.id, Drone.identificacao, Drone.modelo)
            .order_by(Drone.identificacao)
        )
        result = await self.db.execute(stmt)
        rows = result.all()

        items = [
            {
                "drone_id": row.drone_id,
                "drone_identificacao": row.drone_identificacao,
                "drone_modelo": row.drone_modelo,
                "horas_voadas_periodo": row.horas_voadas_periodo,
                "total_missoes": row.total_missoes,
            }
            for row in rows
        ]

        return {
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "items": items,
        }
