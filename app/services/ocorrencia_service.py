"""Business logic for Ocorrencia registration and listing."""

from datetime import datetime

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessRuleViolationError, EntityNotFoundError
from app.models.enums import MissaoStatus, Severidade
from app.models.models import Missao, Ocorrencia, TipoOcorrencia
from app.repositories.base_repository import PaginatedResult


class OcorrenciaService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_ocorrencia(
        self,
        missao_id: int,
        tipo_ocorrencia_id: int,
        descricao: str,
        severidade: Severidade,
        registrada_por: int,
    ) -> Ocorrencia:
        # 1. Validate mission exists
        missao = await self.db.get(Missao, missao_id)
        if missao is None:
            raise EntityNotFoundError(f"missoes com id={missao_id} não encontrado")

        # 2. Validate mission status
        if missao.status not in (MissaoStatus.EM_EXECUCAO.value, MissaoStatus.PAUSADA.value):
            raise BusinessRuleViolationError(
                "Ocorrência só pode ser registrada em missão com status EM_EXECUCAO ou PAUSADA"
            )

        # 3. Validate tipo_ocorrencia exists
        tipo = await self.db.get(TipoOcorrencia, tipo_ocorrencia_id)
        if tipo is None:
            raise EntityNotFoundError(
                f"tipos_ocorrencia com id={tipo_ocorrencia_id} não encontrado"
            )

        # 4. Create Ocorrencia
        ocorrencia = Ocorrencia(
            missao_id=missao_id,
            tipo_ocorrencia_id=tipo_ocorrencia_id,
            descricao=descricao,
            severidade=severidade.value,
            registrada_por=registrada_por,
            registrada_em=datetime.utcnow(),
        )
        self.db.add(ocorrencia)
        await self.db.flush()
        await self.db.refresh(ocorrencia)

        return ocorrencia

    async def list_ocorrencias(
        self,
        missao_id: int | None = None,
        tipo_ocorrencia_id: int | None = None,
        severidade: Severidade | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[Ocorrencia]:
        page_size = max(1, min(page_size, 100))
        page = max(1, page)

        query: Select = select(Ocorrencia)

        # Build filters
        filters = []
        if missao_id is not None:
            filters.append(Ocorrencia.missao_id == missao_id)
        if tipo_ocorrencia_id is not None:
            filters.append(Ocorrencia.tipo_ocorrencia_id == tipo_ocorrencia_id)
        if severidade is not None:
            filters.append(Ocorrencia.severidade == severidade.value)

        for f in filters:
            query = query.where(f)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Order and paginate
        query = query.order_by(Ocorrencia.id)
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return PaginatedResult(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )
