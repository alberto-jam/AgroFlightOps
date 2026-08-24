"""Business logic for Medição ROP — validates filters and delegates to repository."""

from datetime import date, datetime, time

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessRuleViolationError, EntityNotFoundError
from app.models.models import Cliente, Propriedade
from app.repositories.base_repository import PaginatedResult
from app.repositories.medicao_rop_repository import MedicaoRopMissaoRow, MedicaoRopRepository


class MedicaoRopService:
    """Service layer for Medição ROP operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = MedicaoRopRepository(db)

    async def list_missoes_elegiveis(
        self,
        cliente_id: int,
        data_inicial: date,
        data_final: date,
        propriedade_id: int | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[MedicaoRopMissaoRow]:
        """Consulta missões elegíveis para medição.

        Validações:
        - data_final >= data_inicial
        - cliente_id existe
        - propriedade_id (se informado) pertence ao cliente
        """
        # 1. Validate date range
        if data_final < data_inicial:
            raise BusinessRuleViolationError(
                "Período inválido: data final deve ser maior ou igual à data inicial"
            )

        # 2. Validate cliente exists
        cliente = await self.db.get(Cliente, cliente_id)
        if cliente is None:
            raise EntityNotFoundError(f"Cliente com id={cliente_id} não encontrado")

        # 3. Validate propriedade belongs to cliente (if provided)
        if propriedade_id is not None:
            propriedade = await self.db.get(Propriedade, propriedade_id)
            if propriedade is None:
                raise EntityNotFoundError(
                    f"Propriedade com id={propriedade_id} não encontrada"
                )
            if propriedade.cliente_id != cliente_id:
                raise BusinessRuleViolationError(
                    f"Propriedade id={propriedade_id} não pertence ao cliente id={cliente_id}"
                )

        # 4. Convert dates to datetime with appropriate times
        data_inicial_dt = datetime.combine(data_inicial, time.min)  # 00:00:00
        data_final_dt = datetime.combine(data_final, time(23, 59, 59))  # 23:59:59

        # 5. Delegate to repository
        return await self.repo.list_missoes_elegiveis(
            cliente_id=cliente_id,
            data_inicial=data_inicial_dt,
            data_final=data_final_dt,
            propriedade_id=propriedade_id,
            page=page,
            page_size=page_size,
        )
