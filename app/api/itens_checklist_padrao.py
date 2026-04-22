"""API routes for ItemChecklistPadrao CRUD."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_perfil
from app.models.models import Usuario
from app.schemas.base import PaginatedResponse
from app.schemas.checklist_padrao import (
    ItemChecklistPadraoCreate, ItemChecklistPadraoResponse, ItemChecklistPadraoUpdate,
)
from app.services.item_checklist_padrao_service import ItemChecklistPadraoService

router = APIRouter(
    prefix="/itens-checklist-padrao",
    tags=["Itens Checklist Padrão"],
    dependencies=[Depends(require_perfil("ADMINISTRADOR", "COORDENADOR_OPERACIONAL"))],
)


@router.post("", response_model=ItemChecklistPadraoResponse, status_code=201)
async def create(
    body: ItemChecklistPadraoCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    service = ItemChecklistPadraoService(db)
    return await service.create(body, usuario_id=current_user.id)


@router.get("", response_model=PaginatedResponse[ItemChecklistPadraoResponse])
async def list_all(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    ativo: bool | None = Query(None),
):
    service = ItemChecklistPadraoService(db)
    result = await service.list(page=page, page_size=page_size, ativo=ativo)
    return PaginatedResponse(
        items=[ItemChecklistPadraoResponse.model_validate(i) for i in result.items],
        total=result.total, page=result.page, page_size=result.page_size, pages=result.pages,
    )


@router.get("/{item_id}", response_model=ItemChecklistPadraoResponse)
async def get(item_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    service = ItemChecklistPadraoService(db)
    return await service.get(item_id)


@router.put("/{item_id}", response_model=ItemChecklistPadraoResponse)
async def update(
    item_id: int, body: ItemChecklistPadraoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    service = ItemChecklistPadraoService(db)
    return await service.update(item_id, body, usuario_id=current_user.id)


@router.patch("/{item_id}", response_model=ItemChecklistPadraoResponse)
async def patch(
    item_id: int, body: ItemChecklistPadraoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    service = ItemChecklistPadraoService(db)
    return await service.update(item_id, body, usuario_id=current_user.id)


@router.delete("/{item_id}", response_model=ItemChecklistPadraoResponse)
async def delete(
    item_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
):
    service = ItemChecklistPadraoService(db)
    return await service.delete(item_id, usuario_id=current_user.id)
