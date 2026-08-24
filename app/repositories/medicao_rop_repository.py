"""Repository for Medição ROP — queries eligible missions for measurement reports."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Missao, OrdemServico, Propriedade, Talhao
from app.repositories.base_repository import PaginatedResult


@dataclass
class MedicaoRopMissaoRow:
    """DTO carrying joined mission data for the measurement listing."""

    id: int
    codigo: str
    propriedade_nome: str
    talhao_nome: str
    encerrado_tecnicamente_em: datetime
    area_realizada: Decimal | None
    status: str


class MedicaoRopRepository:
    """Repository for querying missions eligible for ROP measurement."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_missoes_elegiveis(
        self,
        cliente_id: int,
        data_inicial: datetime,
        data_final: datetime,
        propriedade_id: int | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[MedicaoRopMissaoRow]:
        """Query missions eligible for measurement.

        Filters:
        - encerrado_tecnicamente_em BETWEEN data_inicial AND data_final
        - medicao_enviada_em IS NULL
        - ordens_servico.cliente_id = cliente_id
        - (optional) ordens_servico.propriedade_id = propriedade_id

        Returns paginated result with MedicaoRopMissaoRow items.
        """
        page_size = max(1, min(page_size, 100))
        page = max(1, page)

        # Base query selecting specific columns with JOINs
        base_query = (
            select(
                Missao.id,
                Missao.codigo,
                Propriedade.nome.label("propriedade_nome"),
                Talhao.nome.label("talhao_nome"),
                Missao.encerrado_tecnicamente_em,
                Missao.area_realizada,
                Missao.status,
            )
            .join(OrdemServico, Missao.ordem_servico_id == OrdemServico.id)
            .join(Propriedade, OrdemServico.propriedade_id == Propriedade.id)
            .join(Talhao, OrdemServico.talhao_id == Talhao.id)
            .where(
                Missao.encerrado_tecnicamente_em >= data_inicial,
                Missao.encerrado_tecnicamente_em <= data_final,
                Missao.medicao_enviada_em.is_(None),
                OrdemServico.cliente_id == cliente_id,
            )
        )

        # Optional property filter
        if propriedade_id is not None:
            base_query = base_query.where(OrdemServico.propriedade_id == propriedade_id)

        # Count total matching rows
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply ordering and pagination
        offset = (page - 1) * page_size
        data_query = (
            base_query.order_by(Missao.encerrado_tecnicamente_em.desc())
            .offset(offset)
            .limit(page_size)
        )

        result = await self.db.execute(data_query)
        rows = result.all()

        # Map raw rows to dataclass DTOs
        items = [
            MedicaoRopMissaoRow(
                id=row.id,
                codigo=row.codigo,
                propriedade_nome=row.propriedade_nome,
                talhao_nome=row.talhao_nome,
                encerrado_tecnicamente_em=row.encerrado_tecnicamente_em,
                area_realizada=row.area_realizada,
                status=row.status,
            )
            for row in rows
        ]

        return PaginatedResult(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )
