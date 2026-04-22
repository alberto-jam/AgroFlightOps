"""Business logic for ItemChecklistPadrao CRUD."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateEntityError
from app.models.models import ItemChecklistPadrao
from app.repositories.base_repository import PaginatedResult
from app.repositories.item_checklist_padrao_repository import ItemChecklistPadraoRepository
from app.schemas.checklist_padrao import ItemChecklistPadraoCreate, ItemChecklistPadraoUpdate
from app.services.auditoria_service import AuditoriaService, entity_to_dict

ENTIDADE = "ITEM_CHECKLIST_PADRAO"


class ItemChecklistPadraoService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ItemChecklistPadraoRepository(db)
        self.auditoria = AuditoriaService(db)

    async def create(self, data: ItemChecklistPadraoCreate, usuario_id: int | None = None) -> ItemChecklistPadrao:
        result = await self.repo.create(
            nome_item=data.nome_item, descricao=data.descricao,
            obrigatorio=data.obrigatorio, ordem_exibicao=data.ordem_exibicao,
        )
        if usuario_id:
            await self.auditoria.registrar(
                entidade=ENTIDADE, entidade_id=result.id, acao="CRIACAO",
                valor_anterior=None, valor_novo=entity_to_dict(result), usuario_id=usuario_id,
            )
        return result

    async def get(self, item_id: int) -> ItemChecklistPadrao:
        return await self.repo.get_by_id(item_id)

    async def list(self, page: int = 1, page_size: int = 20, ativo: bool | None = None) -> PaginatedResult[ItemChecklistPadrao]:
        filters: list[Any] = []
        if ativo is not None:
            filters.append(ItemChecklistPadrao.ativo == ativo)
        return await self.repo.list_paginated(
            page=page, page_size=page_size,
            filters=filters if filters else None,
        )

    async def update(self, item_id: int, data: ItemChecklistPadraoUpdate, usuario_id: int | None = None) -> ItemChecklistPadrao:
        old = await self.repo.get_by_id(item_id)
        old_values = entity_to_dict(old)
        kwargs: dict[str, Any] = {}
        if data.nome_item is not None:
            existing = await self.repo.get_by_nome(data.nome_item)
            if existing and existing.id != item_id:
                raise DuplicateEntityError("Item de checklist padrão com este nome já existe")
            kwargs["nome_item"] = data.nome_item
        if data.descricao is not None:
            kwargs["descricao"] = data.descricao
        if data.obrigatorio is not None:
            kwargs["obrigatorio"] = data.obrigatorio
        if data.ordem_exibicao is not None:
            kwargs["ordem_exibicao"] = data.ordem_exibicao
        result = await self.repo.update(item_id, **kwargs)
        if usuario_id:
            await self.auditoria.registrar(
                entidade=ENTIDADE, entidade_id=item_id, acao="ATUALIZACAO",
                valor_anterior=old_values, valor_novo=entity_to_dict(result), usuario_id=usuario_id,
            )
        return result

    async def delete(self, item_id: int, usuario_id: int | None = None) -> ItemChecklistPadrao:
        old = await self.repo.get_by_id(item_id)
        old_values = entity_to_dict(old)
        result = await self.repo.soft_delete(item_id)
        if usuario_id:
            await self.auditoria.registrar(
                entidade=ENTIDADE, entidade_id=item_id, acao="EXCLUSAO",
                valor_anterior=old_values, valor_novo=entity_to_dict(result), usuario_id=usuario_id,
            )
        return result
