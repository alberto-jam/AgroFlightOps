"""Repository for DocumentoOficial entity with filtered listing."""

from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import DocumentoStatus
from app.models.models import DocumentoOficial
from app.repositories.base_repository import BaseRepository, PaginatedResult


class DocumentoOficialRepository(BaseRepository[DocumentoOficial]):
    """DocumentoOficial repository extending BaseRepository with filtered listing."""

    def __init__(self, db: AsyncSession):
        super().__init__(DocumentoOficial, db)

    async def list_filtered(
        self,
        page: int = 1,
        page_size: int = 20,
        entidade: str | None = None,
        entidade_id: int | None = None,
        tipo_documento: str | None = None,
        status: str | None = None,
    ) -> PaginatedResult[DocumentoOficial]:
        """List documentos oficiais with optional filters."""
        filters: list[Any] = []
        if entidade is not None:
            filters.append(DocumentoOficial.entidade == entidade)
        if entidade_id is not None:
            filters.append(DocumentoOficial.entidade_id == entidade_id)
        if tipo_documento is not None:
            filters.append(DocumentoOficial.tipo_documento == tipo_documento)
        if status is not None:
            filters.append(DocumentoOficial.status == status)

        return await self.list_paginated(
            page=page,
            page_size=page_size,
            filters=filters if filters else None,
            order_by=DocumentoOficial.created_at.desc(),
        )

    async def find_active_by_tipo_entidade(
        self,
        tipo_documento: str,
        entidade: str,
        entidade_id: int,
    ) -> DocumentoOficial | None:
        """Find an active document with the same tipo_documento and entidade/entidade_id."""
        result = await self.db.execute(
            select(DocumentoOficial).where(
                DocumentoOficial.tipo_documento == tipo_documento,
                DocumentoOficial.entidade == entidade,
                DocumentoOficial.entidade_id == entidade_id,
                DocumentoOficial.status == DocumentoStatus.ATIVO.value,
            )
        )
        return result.scalar_one_or_none()

    async def mark_expired_documents(self) -> int:
        """Mark documents with data_validade < today as VENCIDO. Returns count updated."""
        today = date.today()
        result = await self.db.execute(
            select(DocumentoOficial).where(
                DocumentoOficial.status == DocumentoStatus.ATIVO.value,
                DocumentoOficial.data_validade.isnot(None),
                DocumentoOficial.data_validade < today,
            )
        )
        docs = list(result.scalars().all())
        for doc in docs:
            doc.status = DocumentoStatus.VENCIDO.value
        await self.db.flush()
        return len(docs)
