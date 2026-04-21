"""Business logic for OrdemServico CRUD operations."""

from datetime import date
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessRuleViolationError, InvalidStateTransitionError
from app.models.enums import OrdemServicoStatus, Prioridade
from app.models.models import HistoricoStatusOS, OrdemServico
from app.repositories.base_repository import PaginatedResult
from app.repositories.ordem_servico_repository import OrdemServicoRepository
from app.schemas.ordem_servico import OrdemServicoCreate, OrdemServicoUpdate
from app.services.auditoria_service import AuditoriaService, entity_to_dict

ENTIDADE = "ORDEM_SERVICO"

# Valid transitions: (from_status) -> set of allowed to_statuses
TRANSICOES_VALIDAS: dict[OrdemServicoStatus, set[OrdemServicoStatus]] = {
    OrdemServicoStatus.RASCUNHO: {
        OrdemServicoStatus.EM_ANALISE,
        OrdemServicoStatus.CANCELADA,
    },
    OrdemServicoStatus.EM_ANALISE: {
        OrdemServicoStatus.APROVADA,
        OrdemServicoStatus.REJEITADA,
        OrdemServicoStatus.CANCELADA,
    },
    OrdemServicoStatus.APROVADA: {
        OrdemServicoStatus.CANCELADA,
    },
    OrdemServicoStatus.REJEITADA: set(),
    OrdemServicoStatus.CANCELADA: set(),
}


class OrdemServicoService:
    """Service layer for OrdemServico operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = OrdemServicoRepository(db)
        self.auditoria = AuditoriaService(db)

    async def create_ordem_servico(
        self, data: OrdemServicoCreate, criado_por: int
    ) -> OrdemServico:
        """Create a new Ordem de Serviço with status RASCUNHO."""
        result = await self.repo.create_ordem_servico(
            cliente_id=data.cliente_id,
            propriedade_id=data.propriedade_id,
            talhao_id=data.talhao_id,
            cultura_id=data.cultura_id,
            tipo_aplicacao=data.tipo_aplicacao,
            prioridade=data.prioridade.value,
            descricao=data.descricao,
            data_prevista=data.data_prevista,
            criado_por=criado_por,
        )
        await self.auditoria.registrar(
            entidade=ENTIDADE,
            entidade_id=result.id,
            acao="CRIACAO",
            valor_anterior=None,
            valor_novo=entity_to_dict(result),
            usuario_id=criado_por,
        )
        return result

    async def get_ordem_servico(self, os_id: int) -> OrdemServico:
        """Get an Ordem de Serviço by ID."""
        return await self.repo.get_by_id(os_id)

    async def list_ordens_servico(
        self,
        page: int = 1,
        page_size: int = 20,
        status: OrdemServicoStatus | None = None,
        cliente_id: int | None = None,
        propriedade_id: int | None = None,
        prioridade: Prioridade | None = None,
        data_prevista: date | None = None,
    ) -> PaginatedResult[OrdemServico]:
        """List Ordens de Serviço with optional filters."""
        return await self.repo.list_filtered(
            page=page,
            page_size=page_size,
            status=status,
            cliente_id=cliente_id,
            propriedade_id=propriedade_id,
            prioridade=prioridade,
            data_prevista=data_prevista,
        )

    async def update_ordem_servico(
        self, os_id: int, data: OrdemServicoUpdate, usuario_id: int | None = None
    ) -> OrdemServico:
        """Update an Ordem de Serviço."""
        old_instance = await self.repo.get_by_id(os_id)
        old_values = entity_to_dict(old_instance)

        kwargs: dict[str, Any] = {}

        if data.tipo_aplicacao is not None:
            kwargs["tipo_aplicacao"] = data.tipo_aplicacao
        if data.prioridade is not None:
            kwargs["prioridade"] = data.prioridade.value
        if data.descricao is not None:
            kwargs["descricao"] = data.descricao
        if data.data_prevista is not None:
            kwargs["data_prevista"] = data.data_prevista

        result = await self.repo.update(os_id, **kwargs)
        if usuario_id is not None:
            await self.auditoria.registrar(
                entidade=ENTIDADE,
                entidade_id=os_id,
                acao="ATUALIZACAO",
                valor_anterior=old_values,
                valor_novo=entity_to_dict(result),
                usuario_id=usuario_id,
            )
        return result

    async def transicionar_status(
        self,
        os_id: int,
        status_novo: OrdemServicoStatus,
        motivo: str | None,
        usuario_id: int,
    ) -> OrdemServico:
        """Transition an Ordem de Serviço to a new status following the state machine rules."""
        ordem = await self.repo.get_by_id(os_id)
        old_values = entity_to_dict(ordem)
        status_atual = OrdemServicoStatus(ordem.status)

        # Validate transition
        transicoes_permitidas = TRANSICOES_VALIDAS.get(status_atual, set())
        if status_novo not in transicoes_permitidas:
            raise InvalidStateTransitionError(
                f"Transição de {status_atual.value} para {status_novo.value} não é permitida"
            )

        # Validate required motivo for REJEITADA
        if status_novo == OrdemServicoStatus.REJEITADA and not motivo:
            raise BusinessRuleViolationError(
                "Motivo de rejeição é obrigatório para rejeitar uma OS"
            )

        # Validate required motivo for CANCELADA
        if status_novo == OrdemServicoStatus.CANCELADA and not motivo:
            raise BusinessRuleViolationError(
                "Motivo de cancelamento é obrigatório para cancelar uma OS"
            )

        # Update the OS fields
        update_kwargs: dict[str, Any] = {"status": status_novo.value}

        if status_novo == OrdemServicoStatus.REJEITADA:
            update_kwargs["motivo_rejeicao"] = motivo
        elif status_novo == OrdemServicoStatus.CANCELADA:
            update_kwargs["motivo_cancelamento"] = motivo
        elif status_novo == OrdemServicoStatus.APROVADA:
            update_kwargs["aprovado_por"] = usuario_id

        # Apply update using setattr directly (bypass None check in base update)
        for key, value in update_kwargs.items():
            setattr(ordem, key, value)
        await self.db.flush()
        await self.db.refresh(ordem)

        # Record history
        await self.repo.create_historico(
            ordem_servico_id=os_id,
            status_anterior=status_atual.value,
            status_novo=status_novo.value,
            motivo=motivo,
            alterado_por=usuario_id,
        )

        await self.auditoria.registrar(
            entidade=ENTIDADE,
            entidade_id=os_id,
            acao="ATUALIZACAO",
            valor_anterior=old_values,
            valor_novo=entity_to_dict(ordem),
            usuario_id=usuario_id,
        )

        return ordem

    async def list_historico(self, os_id: int) -> list[HistoricoStatusOS]:
        """List status transition history for an Ordem de Serviço."""
        # Ensure the OS exists (raises EntityNotFoundError if not)
        await self.repo.get_by_id(os_id)
        return await self.repo.list_historico(os_id)
