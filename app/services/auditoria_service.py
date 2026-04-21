"""Centralized audit service for recording CUD operations on main entities."""

import math
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.inspection import inspect

from app.models.models import Auditoria


def entity_to_dict(instance: Any) -> dict[str, Any] | None:
    """Convert a SQLAlchemy model instance to a JSON-serializable dict.

    Handles Decimal, datetime, date, time conversions.
    """
    if instance is None:
        return None

    mapper = inspect(type(instance))
    result: dict[str, Any] = {}
    for col in mapper.columns:
        value = getattr(instance, col.key, None)
        if isinstance(value, Decimal):
            value = float(value)
        elif isinstance(value, datetime):
            value = value.isoformat()
        elif isinstance(value, date):
            value = value.isoformat()
        elif isinstance(value, time):
            value = value.isoformat()
        result[col.key] = value
    return result


class AuditoriaService:
    """Service for recording and querying audit trail entries."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def registrar(
        self,
        entidade: str,
        entidade_id: int,
        acao: str,
        valor_anterior: dict[str, Any] | None,
        valor_novo: dict[str, Any] | None,
        usuario_id: int,
    ) -> Auditoria:
        """Create an audit record in the same transaction."""
        registro = Auditoria(
            entidade=entidade,
            entidade_id=entidade_id,
            acao=acao,
            valor_anterior=valor_anterior,
            valor_novo=valor_novo,
            usuario_id=usuario_id,
        )
        self.db.add(registro)
        await self.db.flush()
        return registro

    async def list_auditoria(
        self,
        page: int = 1,
        page_size: int = 20,
        entidade: str | None = None,
        entidade_id: int | None = None,
        usuario_id: int | None = None,
        data_inicio: datetime | None = None,
        data_fim: datetime | None = None,
    ) -> dict[str, Any]:
        """List audit records with optional filters and pagination."""
        page_size = max(1, min(page_size, 100))
        page = max(1, page)

        query = select(Auditoria)
        filters: list[Any] = []

        if entidade is not None:
            filters.append(Auditoria.entidade == entidade)
        if entidade_id is not None:
            filters.append(Auditoria.entidade_id == entidade_id)
        if usuario_id is not None:
            filters.append(Auditoria.usuario_id == usuario_id)
        if data_inicio is not None:
            filters.append(Auditoria.created_at >= data_inicio)
        if data_fim is not None:
            filters.append(Auditoria.created_at <= data_fim)

        for f in filters:
            query = query.where(f)

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Order and paginate
        query = query.order_by(Auditoria.created_at.desc())
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": math.ceil(total / page_size) if page_size > 0 else 0,
        }
