"""Business logic for Missao CRUD operations."""

from datetime import date, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
    InsufficientStockError,
    InvalidStateTransitionError,
)
from app.models.enums import BateriaStatus, ChecklistStatusGeral, DroneStatus, FinanceiroStatus, MissaoStatus, OrdemServicoStatus
from app.models.models import Bateria, ChecklistMissao, ConsumoInsumoMissao, Drone, FinanceiroMissao, HistoricoStatusMissao, Insumo, Missao, MissaoBateria, ReservaInsumo
from app.repositories.base_repository import PaginatedResult
from app.repositories.missao_repository import MissaoRepository
from app.repositories.ordem_servico_repository import OrdemServicoRepository
from app.schemas.missao import MissaoCreate, MissaoUpdate
from app.services.auditoria_service import AuditoriaService, entity_to_dict

ENTIDADE = "MISSAO"

# Valid transitions: (from_status) -> set of allowed to_statuses
TRANSICOES_VALIDAS_MISSAO: dict[MissaoStatus, set[MissaoStatus]] = {
    MissaoStatus.RASCUNHO: {MissaoStatus.PLANEJADA, MissaoStatus.CANCELADA},
    MissaoStatus.PLANEJADA: {MissaoStatus.AGENDADA, MissaoStatus.CANCELADA},
    MissaoStatus.AGENDADA: {MissaoStatus.EM_CHECKLIST, MissaoStatus.CANCELADA},
    MissaoStatus.EM_CHECKLIST: {MissaoStatus.LIBERADA},
    MissaoStatus.LIBERADA: {MissaoStatus.EM_EXECUCAO},
    MissaoStatus.EM_EXECUCAO: {MissaoStatus.PAUSADA, MissaoStatus.CONCLUIDA},
    MissaoStatus.PAUSADA: {MissaoStatus.EM_EXECUCAO},
    MissaoStatus.CONCLUIDA: {MissaoStatus.ENCERRADA_TECNICAMENTE},
    MissaoStatus.ENCERRADA_TECNICAMENTE: {MissaoStatus.ENCERRADA_FINANCEIRAMENTE},
    MissaoStatus.CANCELADA: set(),
    MissaoStatus.ENCERRADA_FINANCEIRAMENTE: set(),
}


class MissaoService:
    """Service layer for Missao operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = MissaoRepository(db)
        self.os_repo = OrdemServicoRepository(db)
        self.auditoria = AuditoriaService(db)

    async def create_missao(self, data: MissaoCreate, usuario_id: int) -> Missao:
        """Create a new Missao. OS must have status APROVADA."""
        # Validate OS exists and has status APROVADA
        ordem = await self.os_repo.get_by_id(data.ordem_servico_id)
        if ordem.status != OrdemServicoStatus.APROVADA.value:
            raise BusinessRuleViolationError(
                "Missão só pode ser criada para Ordem de Serviço com status APROVADA"
            )

        missao = await self.repo.create_missao(
            ordem_servico_id=data.ordem_servico_id,
            piloto_id=data.piloto_id,
            drone_id=data.drone_id,
            data_agendada=data.data_agendada,
            hora_agendada=data.hora_agendada,
            area_prevista=data.area_prevista,
            volume_previsto=data.volume_previsto,
            tecnico_id=data.tecnico_id,
            janela_operacional=data.janela_operacional,
            restricoes=data.restricoes,
            observacoes_planejamento=data.observacoes_planejamento,
            latitude_operacao=data.latitude_operacao,
            longitude_operacao=data.longitude_operacao,
            endereco_operacao=data.endereco_operacao,
            referencia_operacao=data.referencia_operacao,
        )

        # Record initial status in history
        await self.repo.create_historico(
            missao_id=missao.id,
            status_anterior=None,
            status_novo=MissaoStatus.RASCUNHO.value,
            motivo=None,
            alterado_por=usuario_id,
        )

        await self.auditoria.registrar(
            entidade=ENTIDADE,
            entidade_id=missao.id,
            acao="CRIACAO",
            valor_anterior=None,
            valor_novo=entity_to_dict(missao),
            usuario_id=usuario_id,
        )

        return missao

    async def get_missao(self, missao_id: int) -> Missao:
        """Get a Missao by ID."""
        return await self.repo.get_by_id(missao_id)

    async def list_missoes(
        self,
        page: int = 1,
        page_size: int = 20,
        status: MissaoStatus | None = None,
        piloto_id: int | None = None,
        drone_id: int | None = None,
        data_agendada: date | None = None,
        ordem_servico_id: int | None = None,
    ) -> PaginatedResult[Missao]:
        """List Missoes with optional filters."""
        return await self.repo.list_filtered(
            page=page,
            page_size=page_size,
            status=status,
            piloto_id=piloto_id,
            drone_id=drone_id,
            data_agendada=data_agendada,
            ordem_servico_id=ordem_servico_id,
        )

    async def update_missao(
        self, missao_id: int, data: MissaoUpdate, usuario_id: int | None = None
    ) -> Missao:
        """Update a Missao's allowed fields."""
        old_instance = await self.repo.get_by_id(missao_id)
        old_values = entity_to_dict(old_instance)

        kwargs: dict[str, Any] = {}

        if data.piloto_id is not None:
            kwargs["piloto_id"] = data.piloto_id
        if data.tecnico_id is not None:
            kwargs["tecnico_id"] = data.tecnico_id
        if data.drone_id is not None:
            kwargs["drone_id"] = data.drone_id
        if data.data_agendada is not None:
            kwargs["data_agendada"] = data.data_agendada
        if data.hora_agendada is not None:
            kwargs["hora_agendada"] = data.hora_agendada
        if data.area_prevista is not None:
            kwargs["area_prevista"] = data.area_prevista
        if data.area_realizada is not None:
            kwargs["area_realizada"] = data.area_realizada
        if data.volume_previsto is not None:
            kwargs["volume_previsto"] = data.volume_previsto
        if data.volume_realizado is not None:
            kwargs["volume_realizado"] = data.volume_realizado
        if data.janela_operacional is not None:
            kwargs["janela_operacional"] = data.janela_operacional
        if data.restricoes is not None:
            kwargs["restricoes"] = data.restricoes
        if data.observacoes_planejamento is not None:
            kwargs["observacoes_planejamento"] = data.observacoes_planejamento
        if data.observacoes_execucao is not None:
            kwargs["observacoes_execucao"] = data.observacoes_execucao
        if data.latitude_operacao is not None:
            kwargs["latitude_operacao"] = data.latitude_operacao
        if data.longitude_operacao is not None:
            kwargs["longitude_operacao"] = data.longitude_operacao
        if data.endereco_operacao is not None:
            kwargs["endereco_operacao"] = data.endereco_operacao
        if data.referencia_operacao is not None:
            kwargs["referencia_operacao"] = data.referencia_operacao

        result = await self.repo.update(missao_id, **kwargs)
        if usuario_id is not None:
            await self.auditoria.registrar(
                entidade=ENTIDADE,
                entidade_id=missao_id,
                acao="ATUALIZACAO",
                valor_anterior=old_values,
                valor_novo=entity_to_dict(result),
                usuario_id=usuario_id,
            )
        return result

    async def registrar_execucao(
        self,
        missao_id: int,
        area_realizada: Any | None = None,
        volume_realizado: Any | None = None,
        observacoes_execucao: str | None = None,
    ) -> Missao:
        """Register execution data. Mission must be EM_EXECUCAO."""
        missao = await self.repo.get_by_id(missao_id)

        if missao.status != MissaoStatus.EM_EXECUCAO.value:
            raise BusinessRuleViolationError(
                "Registro de execução só é permitido quando a missão está EM_EXECUCAO"
            )

        update_kwargs: dict[str, Any] = {}
        if area_realizada is not None:
            update_kwargs["area_realizada"] = area_realizada
        if volume_realizado is not None:
            update_kwargs["volume_realizado"] = volume_realizado
        if observacoes_execucao is not None:
            update_kwargs["observacoes_execucao"] = observacoes_execucao

        if update_kwargs:
            return await self.repo.update(missao_id, **update_kwargs)

        return missao

    async def transicionar_status(
        self,
        missao_id: int,
        status_novo: MissaoStatus,
        motivo: str | None,
        usuario_id: int,
    ) -> Missao:
        """Transition a Missao to a new status following the state machine rules."""
        missao = await self.repo.get_by_id(missao_id)
        old_values = entity_to_dict(missao)
        status_atual = MissaoStatus(missao.status)

        # Validate transition
        transicoes_permitidas = TRANSICOES_VALIDAS_MISSAO.get(status_atual, set())
        if status_novo not in transicoes_permitidas:
            raise InvalidStateTransitionError(
                f"Transição de {status_atual.value} para {status_novo.value} não é permitida"
            )

        # Build update kwargs
        update_kwargs: dict[str, Any] = {"status": status_novo.value}

        # Side effects for EM_CHECKLIST: auto-create checklist
        if status_novo == MissaoStatus.EM_CHECKLIST:
            from app.services.checklist_service import ChecklistService

            checklist_service = ChecklistService(self.db)
            await checklist_service.create_checklist_for_missao(
                missao_id=missao_id, preenchido_por=usuario_id
            )

        # Side effects for LIBERADA: validate checklist is APROVADO
        if status_novo == MissaoStatus.LIBERADA:
            from sqlalchemy import select

            result = await self.db.execute(
                select(ChecklistMissao).where(ChecklistMissao.missao_id == missao_id)
            )
            checklist = result.scalar_one_or_none()
            if checklist is None or checklist.status_geral != ChecklistStatusGeral.APROVADO.value:
                raise BusinessRuleViolationError(
                    "Checklist deve estar APROVADO para liberar a missão"
                )

        # Side effects for EM_EXECUCAO
        if status_novo == MissaoStatus.EM_EXECUCAO:
            update_kwargs["iniciado_em"] = datetime.utcnow()
            drone = await self.db.get(Drone, missao.drone_id)
            if drone:
                drone.status = DroneStatus.EM_USO.value

        # Side effects for CONCLUIDA
        if status_novo == MissaoStatus.CONCLUIDA:
            # Validate execution data is filled
            if missao.area_realizada is None or missao.volume_realizado is None:
                raise BusinessRuleViolationError(
                    "area_realizada e volume_realizado devem estar preenchidos para concluir a missão"
                )
            now = datetime.utcnow()
            if missao.iniciado_em and now < missao.iniciado_em:
                raise BusinessRuleViolationError(
                    "finalizado_em deve ser posterior ou igual a iniciado_em"
                )
            update_kwargs["finalizado_em"] = now
            drone = await self.db.get(Drone, missao.drone_id)
            if drone:
                drone.status = DroneStatus.DISPONIVEL.value

        # Side effects for ENCERRADA_TECNICAMENTE
        if status_novo == MissaoStatus.ENCERRADA_TECNICAMENTE:
            update_kwargs["encerrado_tecnicamente_em"] = datetime.utcnow()
            financeiro = FinanceiroMissao(
                missao_id=missao_id,
                custo_estimado=0,
                custo_realizado=0,
                valor_faturado=0,
                status_financeiro=FinanceiroStatus.PENDENTE.value,
            )
            self.db.add(financeiro)
            await self.db.flush()

        # Apply update
        for key, value in update_kwargs.items():
            setattr(missao, key, value)
        await self.db.flush()
        await self.db.refresh(missao)

        # Record history
        await self.repo.create_historico(
            missao_id=missao_id,
            status_anterior=status_atual.value,
            status_novo=status_novo.value,
            motivo=motivo,
            alterado_por=usuario_id,
        )

        await self.auditoria.registrar(
            entidade=ENTIDADE,
            entidade_id=missao_id,
            acao="ATUALIZACAO",
            valor_anterior=old_values,
            valor_novo=entity_to_dict(missao),
            usuario_id=usuario_id,
        )

        return missao

    async def list_historico(self, missao_id: int) -> list[HistoricoStatusMissao]:
        """List status transition history for a Missao."""
        await self.repo.get_by_id(missao_id)
        return await self.repo.list_historico(missao_id)

    async def associar_bateria(
        self, missao_id: int, bateria_id: int, ordem_uso: int
    ) -> MissaoBateria:
        """Associate a battery to a mission. Battery must not be REPROVADA or DESCARTADA."""
        await self.repo.get_by_id(missao_id)

        bateria = await self.db.get(Bateria, bateria_id)
        if bateria is None:
            raise EntityNotFoundError(f"baterias com id={bateria_id} não encontrado")

        if bateria.status in (
            BateriaStatus.REPROVADA.value,
            BateriaStatus.DESCARTADA.value,
        ):
            raise BusinessRuleViolationError(
                f"Bateria com status {bateria.status} não pode ser associada a uma missão"
            )

        return await self.repo.create_missao_bateria(missao_id, bateria_id, ordem_uso)

    async def list_baterias_missao(self, missao_id: int) -> list[MissaoBateria]:
        """List batteries associated with a mission."""
        await self.repo.get_by_id(missao_id)
        return await self.repo.list_missao_baterias(missao_id)

    async def criar_reserva_insumo(
        self, missao_id: int, insumo_id: int, quantidade_prevista: Any, unidade_medida: str
    ) -> ReservaInsumo:
        """Create an insumo reservation for a mission."""
        await self.repo.get_by_id(missao_id)

        insumo = await self.db.get(Insumo, insumo_id)
        if insumo is None:
            raise EntityNotFoundError(f"insumos com id={insumo_id} não encontrado")

        return await self.repo.create_reserva_insumo(
            missao_id=missao_id,
            insumo_id=insumo_id,
            quantidade_prevista=quantidade_prevista,
            unidade_medida=unidade_medida,
        )

    async def list_reservas_insumo(self, missao_id: int) -> list[ReservaInsumo]:
        """List insumo reservations for a mission."""
        await self.repo.get_by_id(missao_id)
        return await self.repo.list_reservas_insumo(missao_id)

    async def registrar_consumo_insumo(
        self,
        missao_id: int,
        insumo_id: int,
        quantidade_realizada: Any,
        unidade_medida: str,
        observacoes: str | None = None,
        justificativa_excesso: str | None = None,
    ) -> ConsumoInsumoMissao:
        """Register insumo consumption during a mission.

        Validates mission is EM_EXECUCAO, checks stock, requires justificativa
        when consumption exceeds the reservation, and debits the insumo balance.
        """
        missao = await self.repo.get_by_id(missao_id)

        if missao.status != MissaoStatus.EM_EXECUCAO.value:
            raise BusinessRuleViolationError(
                "Registro de consumo só é permitido quando a missão está EM_EXECUCAO"
            )

        insumo = await self.db.get(Insumo, insumo_id)
        if insumo is None:
            raise EntityNotFoundError(f"insumos com id={insumo_id} não encontrado")

        # Check if there's a reservation and validate justificativa_excesso
        from sqlalchemy import select

        result = await self.db.execute(
            select(ReservaInsumo).where(
                ReservaInsumo.missao_id == missao_id,
                ReservaInsumo.insumo_id == insumo_id,
            )
        )
        reserva = result.scalar_one_or_none()

        if reserva is not None:
            if quantidade_realizada > reserva.quantidade_prevista:
                if not justificativa_excesso:
                    raise BusinessRuleViolationError(
                        "justificativa_excesso é obrigatória quando quantidade_realizada excede quantidade_prevista"
                    )

        # Validate stock
        if insumo.saldo_atual < quantidade_realizada:
            raise InsufficientStockError(
                f"Saldo insuficiente para o insumo {insumo.nome}. "
                f"Saldo atual: {insumo.saldo_atual}, quantidade solicitada: {quantidade_realizada}"
            )

        # Debit insumo balance
        insumo.saldo_atual -= quantidade_realizada
        await self.db.flush()

        # Create consumo record
        return await self.repo.create_consumo_insumo(
            missao_id=missao_id,
            insumo_id=insumo_id,
            quantidade_realizada=quantidade_realizada,
            unidade_medida=unidade_medida,
            observacoes=observacoes,
            justificativa_excesso=justificativa_excesso,
        )

    async def list_consumos_insumo(self, missao_id: int) -> list[ConsumoInsumoMissao]:
        """List insumo consumptions for a mission."""
        await self.repo.get_by_id(missao_id)
        return await self.repo.list_consumos_insumo(missao_id)
