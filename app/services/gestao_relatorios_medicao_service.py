"""Business logic for Gestão de Relatórios de Medição — listing, download, delete, send."""

import logging
import re
from datetime import date, datetime
from math import ceil

import boto3
from fastapi import HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.config import settings
from app.core.exceptions import BusinessRuleViolationError, EntityNotFoundError
from app.models.models import (
    Cliente,
    Missao,
    RelatorioMedicao,
    RelatorioMedicaoMissao,
)
from app.services.ses_email_service import SesEmailService

logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class PaginatedResult:
    """Simple paginated result container."""

    def __init__(self, items: list, total: int, page: int, page_size: int):
        self.items = items
        self.total = total
        self.page = page
        self.page_size = page_size
        self.pages = ceil(total / page_size) if page_size > 0 else 0


class GestaoRelatoriosMedicaoService:
    """Service for managing generated measurement reports."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def listar_relatorios(
        self,
        cliente_id: int | None = None,
        data_inicial: date | None = None,
        data_final: date | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult:
        """List reports with filters, pagination and ordering by gerado_em desc."""
        # Base query
        stmt = (
            select(RelatorioMedicao)
            .options(joinedload(RelatorioMedicao.cliente))
        )

        # Apply filters
        if status is not None:
            stmt = stmt.where(RelatorioMedicao.status == status)
        else:
            # Default: return ATIVO and ENVIADO (exclude only EXCLUIDO)
            stmt = stmt.where(RelatorioMedicao.status.in_(["ATIVO", "ENVIADO"]))

        if cliente_id is not None:
            stmt = stmt.where(RelatorioMedicao.cliente_id == cliente_id)

        if data_inicial is not None:
            stmt = stmt.where(RelatorioMedicao.data_inicial >= data_inicial)

        if data_final is not None:
            stmt = stmt.where(RelatorioMedicao.data_final <= data_final)

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Order and paginate
        stmt = stmt.order_by(RelatorioMedicao.gerado_em.desc())
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        result = await self.db.execute(stmt)
        relatorios = result.scalars().unique().all()

        return PaginatedResult(
            items=relatorios,
            total=total,
            page=page,
            page_size=page_size,
        )

    async def download_relatorio(self, relatorio_id: int) -> str:
        """Generate presigned URL for downloading a report (60min expiration).

        Returns the presigned URL string.
        Raises EntityNotFoundError if report not found or not in a downloadable status.
        """
        relatorio = await self.db.get(RelatorioMedicao, relatorio_id)

        if relatorio is None:
            raise EntityNotFoundError(
                f"Relatório com id={relatorio_id} não encontrado"
            )

        if relatorio.status not in ("ATIVO", "ENVIADO"):
            raise EntityNotFoundError(
                "Relatório não está mais disponível"
            )

        try:
            s3_client = boto3.client("s3", region_name=settings.S3_REGION)
            url = s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": settings.S3_DOCUMENTS_BUCKET,
                    "Key": relatorio.s3_key,
                },
                ExpiresIn=settings.S3_PRESIGNED_URL_EXPIRATION,
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail="Falha ao gerar URL de download",
            ) from e

        return url

    async def excluir_relatorio(
        self,
        relatorio_id: int,
        enviar_cancelamento: bool = False,
        forcar_exclusao: bool = False,
        user_email: str | None = None,
    ) -> None:
        """Soft delete a report with optional cancellation email.

        If enviar_cancelamento=True and the report has recipients (enviado_para),
        a cancellation email is sent before deletion. If SES fails and
        forcar_exclusao=False, raises HTTPException(502) without modifying the report.

        Raises EntityNotFoundError if not found.
        Raises BusinessRuleViolationError if already deleted.
        Raises HTTPException(502) if cancellation email fails and forcar_exclusao is False.
        """
        relatorio = await self.db.get(
            RelatorioMedicao,
            relatorio_id,
            options=[joinedload(RelatorioMedicao.cliente)],
        )

        if relatorio is None:
            raise EntityNotFoundError(
                f"Relatório com id={relatorio_id} não encontrado"
            )

        if relatorio.status == "EXCLUIDO":
            raise BusinessRuleViolationError(
                "Relatório já foi excluído anteriormente"
            )

        if relatorio.status not in ("ATIVO", "ENVIADO"):
            raise BusinessRuleViolationError(
                "Relatório não está em um status válido para exclusão"
            )

        # Cancellation email orchestration
        if enviar_cancelamento and relatorio.enviado_para:
            cliente_nome = relatorio.cliente.nome
            data_inicial_fmt = relatorio.data_inicial.strftime("%d/%m/%Y")
            data_final_fmt = relatorio.data_final.strftime("%d/%m/%Y")
            enviado_em_fmt = relatorio.enviado_em.strftime("%d/%m/%Y %H:%M")

            subject = (
                f"Cancelamento do relatório Relatório de Medição - "
                f"{cliente_nome} - {data_inicial_fmt} a {data_final_fmt}"
            )

            body_text = (
                "O relatório abaixo foi cancelado pelo remetente, favor desconsiderá-lo.\n\n"
                f"Relatório: Relatório de Medição - {cliente_nome} - "
                f"{data_inicial_fmt} a {data_final_fmt}\n"
                f"Data do Envio: {enviado_em_fmt}\n\n"
                "Em caso de dúvidas, entrar em contato.\n\n"
                "Atenciosamente"
            )

            to_addresses = [e.strip() for e in relatorio.enviado_para.split(",")]
            cc_addresses = [user_email] if user_email else None

            try:
                ses_service = SesEmailService()
                ses_service.send_cancellation_email(
                    to_addresses=to_addresses,
                    subject=subject,
                    body_text=body_text,
                    cc_addresses=cc_addresses,
                )
            except Exception as e:
                if not forcar_exclusao:
                    raise HTTPException(
                        status_code=502,
                        detail="Falha no envio do e-mail de cancelamento. Deseja prosseguir com a exclusão?",
                    ) from e
                logger.warning(
                    f"Falha no envio do e-mail de cancelamento para relatório id={relatorio_id}. "
                    "Prosseguindo com exclusão forçada."
                )

        # 1. Soft delete
        relatorio.status = "EXCLUIDO"

        # 2. Clear medicao_enviada_em for linked missions
        linked_stmt = select(RelatorioMedicaoMissao.missao_id).where(
            RelatorioMedicaoMissao.relatorio_id == relatorio_id
        )
        linked_result = await self.db.execute(linked_stmt)
        missao_ids = [row[0] for row in linked_result.all()]

        if missao_ids:
            await self.db.execute(
                update(Missao)
                .where(Missao.id.in_(missao_ids))
                .values(medicao_enviada_em=None)
            )

        # 3. Try to remove from S3 (resilient — failure doesn't block operation)
        try:
            s3_client = boto3.client("s3", region_name=settings.S3_REGION)
            s3_client.delete_object(
                Bucket=settings.S3_DOCUMENTS_BUCKET,
                Key=relatorio.s3_key,
            )
        except Exception:
            logger.warning(
                f"Falha ao remover arquivo S3 (key={relatorio.s3_key}). "
                "O soft delete prossegue normalmente."
            )

        await self.db.commit()

    async def enviar_relatorio(
        self,
        relatorio_id: int,
        emails: list[str],
        mensagem: str | None = None,
    ) -> None:
        """Send report download link via email using SES.

        Validates emails, generates presigned URL (72h), sends via SES,
        then updates enviado_em and enviado_para.
        """
        # Validate emails format
        invalid_emails = [e for e in emails if not EMAIL_REGEX.match(e.strip())]
        if invalid_emails:
            raise BusinessRuleViolationError(
                f"Endereços de e-mail inválidos: {', '.join(invalid_emails)}"
            )

        # Find active report
        relatorio = await self.db.get(
            RelatorioMedicao, relatorio_id, options=[joinedload(RelatorioMedicao.cliente)]
        )

        if relatorio is None or relatorio.status != "ATIVO":
            raise EntityNotFoundError(
                f"Relatório com id={relatorio_id} não encontrado"
            )

        # Generate presigned URL (72h)
        try:
            s3_client = boto3.client("s3", region_name=settings.S3_REGION)
            download_url = s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": settings.S3_DOCUMENTS_BUCKET,
                    "Key": relatorio.s3_key,
                },
                ExpiresIn=settings.S3_PRESIGNED_URL_EMAIL_EXPIRATION,
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail="Falha ao gerar URL de download",
            ) from e

        # Compose subject
        subject = (
            f"Relatório de Medição - {relatorio.cliente.nome} - "
            f"{relatorio.data_inicial.strftime('%d/%m/%Y')} a "
            f"{relatorio.data_final.strftime('%d/%m/%Y')}"
        )

        # Send via SES
        try:
            ses_service = SesEmailService()
            ses_service.send_relatorio_email(
                to_addresses=[e.strip() for e in emails],
                subject=subject,
                download_url=download_url,
                mensagem_personalizada=mensagem,
            )
        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail="Falha no serviço de envio de e-mail",
            ) from e

        # Update report metadata
        relatorio.status = "ENVIADO"
        relatorio.enviado_em = datetime.utcnow()
        relatorio.enviado_para = ",".join(e.strip() for e in emails)
        await self.db.commit()
