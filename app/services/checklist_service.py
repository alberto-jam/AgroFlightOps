"""Business logic for Checklist de Missão operations."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
)
from app.models.enums import ChecklistStatusGeral, ItemChecklistStatus, MissaoStatus
from app.models.models import ChecklistMissao, ItemChecklistMissao, ItemChecklistPadrao, Missao


class ChecklistService:
    """Service layer for Checklist operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_checklist_for_missao(
        self, missao_id: int, preenchido_por: int
    ) -> ChecklistMissao:
        """Create a checklist with PENDENTE status, copying active standard items."""
        # Get active standard checklist items
        result = await self.db.execute(
            select(ItemChecklistPadrao)
            .where(ItemChecklistPadrao.ativo == True)
            .order_by(ItemChecklistPadrao.ordem_exibicao)
        )
        itens_padrao = list(result.scalars().all())

        # Create checklist
        checklist = ChecklistMissao(
            missao_id=missao_id,
            status_geral=ChecklistStatusGeral.PENDENTE.value,
            preenchido_por=preenchido_por,
            preenchido_em=datetime.utcnow(),
        )
        self.db.add(checklist)
        await self.db.flush()

        # Copy standard items to checklist
        for item_padrao in itens_padrao:
            item = ItemChecklistMissao(
                checklist_id=checklist.id,
                nome_item=item_padrao.nome_item,
                obrigatorio=item_padrao.obrigatorio,
                status_item=ItemChecklistStatus.PENDENTE.value,
            )
            self.db.add(item)

        await self.db.flush()
        await self.db.refresh(checklist)
        return checklist

    async def get_checklist_by_missao(self, missao_id: int) -> ChecklistMissao:
        """Get checklist with items for a mission."""
        result = await self.db.execute(
            select(ChecklistMissao)
            .options(selectinload(ChecklistMissao.itens))
            .where(ChecklistMissao.missao_id == missao_id)
        )
        checklist = result.scalar_one_or_none()
        if checklist is None:
            raise EntityNotFoundError(
                f"Checklist para missão id={missao_id} não encontrado"
            )
        return checklist

    async def update_item(
        self, item_id: int, status_item: ItemChecklistStatus, observacao: str | None
    ) -> ItemChecklistMissao:
        """Update an item's status. Validate observation for mandatory REPROVADO items."""
        item = await self.db.get(ItemChecklistMissao, item_id)
        if item is None:
            raise EntityNotFoundError(
                f"Item de checklist com id={item_id} não encontrado"
            )

        # Validate: mandatory item marked as REPROVADO requires observation
        if (
            item.obrigatorio
            and status_item == ItemChecklistStatus.REPROVADO
            and (not observacao or not observacao.strip())
        ):
            raise BusinessRuleViolationError(
                "Item obrigatório reprovado exige preenchimento da observação"
            )

        item.status_item = status_item.value
        item.observacao = observacao

        # Update checklist status_geral to EM_PREENCHIMENTO if still PENDENTE
        checklist = await self.db.get(ChecklistMissao, item.checklist_id)
        if checklist and checklist.status_geral == ChecklistStatusGeral.PENDENTE.value:
            checklist.status_geral = ChecklistStatusGeral.EM_PREENCHIMENTO.value

        await self.db.flush()
        await self.db.refresh(item)
        return item

    async def concluir_checklist(
        self, checklist_id: int, usuario_id: int
    ) -> ChecklistMissao:
        """Set status_geral to CONCLUIDO. Validate all mandatory items are APROVADO or NAO_APLICAVEL."""
        checklist = await self.db.get(ChecklistMissao, checklist_id)
        if checklist is None:
            raise EntityNotFoundError(
                f"Checklist com id={checklist_id} não encontrado"
            )

        # Load items
        result = await self.db.execute(
            select(ItemChecklistMissao).where(
                ItemChecklistMissao.checklist_id == checklist_id
            )
        )
        itens = list(result.scalars().all())

        # Validate all mandatory items are APROVADO or NAO_APLICAVEL
        for item in itens:
            if item.obrigatorio and item.status_item not in (
                ItemChecklistStatus.APROVADO.value,
                ItemChecklistStatus.NAO_APLICAVEL.value,
            ):
                raise BusinessRuleViolationError(
                    "Todos os itens obrigatórios devem estar APROVADO ou NAO_APLICAVEL para concluir o checklist"
                )

        checklist.status_geral = ChecklistStatusGeral.CONCLUIDO.value
        await self.db.flush()
        await self.db.refresh(checklist)
        return checklist

    async def aprovar_checklist(
        self, checklist_id: int, usuario_id: int
    ) -> ChecklistMissao:
        """Approve checklist: set APROVADO, record reviewer, transition mission to LIBERADA."""
        checklist = await self.db.get(ChecklistMissao, checklist_id)
        if checklist is None:
            raise EntityNotFoundError(
                f"Checklist com id={checklist_id} não encontrado"
            )

        # Load items to validate
        result = await self.db.execute(
            select(ItemChecklistMissao).where(
                ItemChecklistMissao.checklist_id == checklist_id
            )
        )
        itens = list(result.scalars().all())

        # Validate no mandatory items are REPROVADO
        for item in itens:
            if item.obrigatorio and item.status_item == ItemChecklistStatus.REPROVADO.value:
                raise BusinessRuleViolationError(
                    "Não é possível aprovar checklist com itens obrigatórios reprovados"
                )

        # Set checklist as APROVADO
        checklist.status_geral = ChecklistStatusGeral.APROVADO.value
        checklist.revisado_por = usuario_id
        checklist.revisado_em = datetime.utcnow()

        await self.db.flush()

        # Transition mission to LIBERADA
        missao = await self.db.get(Missao, checklist.missao_id)
        if missao and missao.status == MissaoStatus.EM_CHECKLIST.value:
            from app.services.missao_service import MissaoService

            missao_service = MissaoService(self.db)
            await missao_service.transicionar_status(
                missao_id=missao.id,
                status_novo=MissaoStatus.LIBERADA,
                motivo="Checklist aprovado",
                usuario_id=usuario_id,
            )

        await self.db.refresh(checklist)
        return checklist
