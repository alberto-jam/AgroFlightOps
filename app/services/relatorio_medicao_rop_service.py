"""Business logic for Relatório de Medição ROP — preview data and report generation."""

from datetime import date, datetime
from decimal import Decimal

import boto3
from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import BusinessRuleViolationError, EntityNotFoundError
from app.models.models import Cliente, Missao, OrdemServico, Propriedade, Talhao
from app.schemas.relatorio_medicao_rop import (
    MissaoPreviewItem,
    RelatorioMedicaoGeradoResponse,
    RelatorioMedicaoPreviewResponse,
)
from app.utils.text_utils import normalize_for_path


class RelatorioMedicaoRopService:
    """Service layer for Relatório de Medição ROP operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_preview_data(
        self, missao_ids: list[int], cliente_id: int
    ) -> RelatorioMedicaoPreviewResponse:
        """Consulta dados completos das missões para preview do relatório.

        Validações:
        - Todas as missões devem pertencer ao cliente informado (via ordem_servico.cliente_id)

        Retorna:
        - RelatorioMedicaoPreviewResponse com nome do cliente, lista de missões e total de área
        """
        # 1. Validate cliente exists
        cliente = await self.db.get(Cliente, cliente_id)
        if cliente is None:
            raise EntityNotFoundError(f"Cliente com id={cliente_id} não encontrado")

        # 2. Query missions with JOINs to get propriedade, talhao, and ordem_servico data
        stmt = (
            select(
                Missao.id,
                Missao.codigo,
                Propriedade.nome.label("propriedade_nome"),
                Talhao.nome.label("talhao_nome"),
                Missao.area_realizada,
                Missao.encerrado_tecnicamente_em,
                OrdemServico.cliente_id,
            )
            .join(OrdemServico, Missao.ordem_servico_id == OrdemServico.id)
            .join(Propriedade, OrdemServico.propriedade_id == Propriedade.id)
            .join(Talhao, OrdemServico.talhao_id == Talhao.id)
            .where(Missao.id.in_(missao_ids))
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        # 3. Validate ownership — all missions must belong to the specified client
        invalid_ids = [row.id for row in rows if row.cliente_id != cliente_id]
        if invalid_ids:
            ids_str = ", ".join(str(id) for id in invalid_ids)
            raise BusinessRuleViolationError(
                f"Existem missões que não pertencem ao cliente informado: {ids_str}"
            )

        # 4. Calculate total_area (treat None as 0)
        total_area = sum(
            (row.area_realizada or Decimal("0")) for row in rows
        )

        # 5. Build response
        missoes = [
            MissaoPreviewItem(
                id=row.id,
                codigo=row.codigo,
                propriedade_nome=row.propriedade_nome,
                talhao_nome=row.talhao_nome,
                area_realizada=row.area_realizada,
                encerrado_tecnicamente_em=row.encerrado_tecnicamente_em,
            )
            for row in rows
        ]

        return RelatorioMedicaoPreviewResponse(
            cliente_nome=cliente.nome,
            missoes=missoes,
            total_area=total_area,
        )

    async def gerar_relatorio(
        self,
        missao_ids: list[int],
        cliente_id: int,
        data_inicial: date,
        data_final: date,
    ) -> RelatorioMedicaoGeradoResponse:
        """Gera PDF do relatório de medição, salva no S3 e marca missões como enviadas.

        Fluxo:
        1. Valida cliente existe
        2. Consulta missões com JOINs
        3. Valida ownership (missões pertencem ao cliente)
        4. Valida duplicidade (medicao_enviada_em IS NULL)
        5. Gera PDF
        6. Upload S3
        7. Atualiza medicao_enviada_em (somente após upload bem-sucedido)
        8. Commit

        Em caso de falha no upload S3, não atualiza banco.
        """
        from app.services.pdf_generator import MedicaoRopPdfGenerator

        # 1. Validate cliente exists
        cliente = await self.db.get(Cliente, cliente_id)
        if cliente is None:
            raise EntityNotFoundError(f"Cliente com id={cliente_id} não encontrado")

        # 2. Query missions with JOINs
        stmt = (
            select(
                Missao.id,
                Missao.codigo,
                Propriedade.nome.label("propriedade_nome"),
                Talhao.nome.label("talhao_nome"),
                Missao.area_realizada,
                Missao.encerrado_tecnicamente_em,
                Missao.medicao_enviada_em,
                OrdemServico.cliente_id,
            )
            .join(OrdemServico, Missao.ordem_servico_id == OrdemServico.id)
            .join(Propriedade, OrdemServico.propriedade_id == Propriedade.id)
            .join(Talhao, OrdemServico.talhao_id == Talhao.id)
            .where(Missao.id.in_(missao_ids))
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        # 3. Validate ownership — all missions must belong to the specified client
        invalid_ids = [row.id for row in rows if row.cliente_id != cliente_id]
        if invalid_ids:
            ids_str = ", ".join(str(id) for id in invalid_ids)
            raise BusinessRuleViolationError(
                f"Existem missões que não pertencem ao cliente informado: {ids_str}"
            )

        # 4. Validate no duplicates — all missions must have medicao_enviada_em IS NULL
        already_sent_ids = [
            row.id for row in rows if row.medicao_enviada_em is not None
        ]
        if already_sent_ids:
            ids_str = ", ".join(str(id) for id in already_sent_ids)
            raise BusinessRuleViolationError(
                f"Existem missões já incluídas em relatório anterior: {ids_str}"
            )

        # 5. Calculate total_area and prepare missoes data for PDF
        total_area = sum((row.area_realizada or Decimal("0")) for row in rows)

        missoes_data = [
            {
                "codigo": row.codigo,
                "propriedade_nome": row.propriedade_nome,
                "talhao_nome": row.talhao_nome,
                "area_realizada": row.area_realizada,
                "encerrado_tecnicamente_em": row.encerrado_tecnicamente_em,
            }
            for row in rows
        ]

        # 6. Generate PDF
        pdf_generator = MedicaoRopPdfGenerator()
        pdf_bytes = pdf_generator.gerar(
            cliente_nome=cliente.nome,
            data_inicial=data_inicial,
            data_final=data_final,
            missoes=missoes_data,
            total_area=total_area,
        )

        # 7. Compose S3 key
        cliente_nome_normalizado = normalize_for_path(cliente.nome)
        s3_key = (
            f"MEDICAO/{cliente_nome_normalizado}/"
            f"Medicao_{data_inicial.strftime('%Y%m%d')}_{data_final.strftime('%Y%m%d')}.pdf"
        )

        # 8. Upload to S3 (must succeed before updating DB)
        try:
            s3_client = boto3.client("s3", region_name=settings.S3_REGION)
            s3_client.put_object(
                Bucket=settings.S3_DOCUMENTS_BUCKET,
                Key=s3_key,
                Body=pdf_bytes,
                ContentType="application/pdf",
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail="Falha ao salvar documento no S3",
            ) from e

        # 9. Only AFTER successful upload: update medicao_enviada_em
        now = datetime.utcnow()
        await self.db.execute(
            update(Missao)
            .where(Missao.id.in_(missao_ids))
            .values(medicao_enviada_em=now)
        )

        # 10. Commit the transaction
        await self.db.commit()

        return RelatorioMedicaoGeradoResponse(
            s3_key=s3_key,
            mensagem="Relatório gerado com sucesso",
        )
