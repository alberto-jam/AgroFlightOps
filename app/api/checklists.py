"""API routes for Checklist de Missão — Piloto (preenchimento), Técnico (aprovação)."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_perfil
from app.models.models import Usuario
from app.schemas.checklist import (
    ChecklistMissaoResponse,
    ItemChecklistMissaoResponse,
    ItemChecklistMissaoUpdate,
)
from app.services.checklist_service import ChecklistService

router = APIRouter(
    prefix="/missoes/{missao_id}/checklist",
    tags=["Checklists"],
)


@router.get("", response_model=ChecklistMissaoResponse)
async def get_checklist(
    missao_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        Usuario,
        Depends(
            require_perfil("ADMINISTRADOR", "COORDENADOR_OPERACIONAL", "PILOTO", "TECNICO")
        ),
    ],
):
    """Get checklist for a mission."""
    service = ChecklistService(db)
    return await service.get_checklist_by_missao(missao_id)


@router.patch(
    "/itens/{item_id}",
    response_model=ItemChecklistMissaoResponse,
)
async def update_item_checklist(
    missao_id: int,
    item_id: int,
    body: ItemChecklistMissaoUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        Usuario,
        Depends(require_perfil("ADMINISTRADOR", "PILOTO")),
    ],
):
    """Update a checklist item status (Piloto)."""
    service = ChecklistService(db)
    return await service.update_item(
        item_id=item_id,
        status_item=body.status_item,
        observacao=body.observacao,
    )


@router.post("/concluir", response_model=ChecklistMissaoResponse)
async def concluir_checklist(
    missao_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        Usuario,
        Depends(require_perfil("ADMINISTRADOR", "PILOTO")),
    ],
):
    """Mark checklist as CONCLUIDO (Piloto)."""
    service = ChecklistService(db)
    checklist = await service.get_checklist_by_missao(missao_id)
    return await service.concluir_checklist(checklist.id, current_user.id)


@router.post("/aprovar", response_model=ChecklistMissaoResponse)
async def aprovar_checklist(
    missao_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        Usuario,
        Depends(require_perfil("ADMINISTRADOR", "TECNICO")),
    ],
):
    """Approve checklist (Técnico) — transitions mission to LIBERADA."""
    service = ChecklistService(db)
    checklist = await service.get_checklist_by_missao(missao_id)
    return await service.aprovar_checklist(checklist.id, current_user.id)
