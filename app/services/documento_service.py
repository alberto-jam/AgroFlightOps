"""Business logic for DocumentoOficial upload, download, listing and status management."""

import uuid
from datetime import date

import boto3
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.enums import DocumentoEntidade, DocumentoStatus
from app.models.models import DocumentoOficial
from app.repositories.base_repository import PaginatedResult
from app.repositories.documento_oficial_repository import DocumentoOficialRepository
from app.services.auditoria_service import AuditoriaService, entity_to_dict

ENTIDADE = "DOCUMENTO_OFICIAL"


class DocumentoService:
    """Service layer for DocumentoOficial operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = DocumentoOficialRepository(db)
        self.auditoria = AuditoriaService(db)

    async def upload_documento(
        self,
        file: UploadFile,
        entidade: DocumentoEntidade,
        entidade_id: int,
        tipo_documento: str,
        enviado_por: int,
        descricao: str | None = None,
        data_emissao: date | None = None,
        data_validade: date | None = None,
    ) -> DocumentoOficial:
        """Upload a document to S3 and register metadata in DB.

        - Marks previous active document of same tipo/entidade as SUBSTITUIDO
        - Stores file in S3 with generated key
        """
        # 1. Mark previous active document as SUBSTITUIDO (Req 15.5)
        existing = await self.repo.find_active_by_tipo_entidade(
            tipo_documento=tipo_documento,
            entidade=entidade.value,
            entidade_id=entidade_id,
        )
        if existing is not None:
            existing.status = DocumentoStatus.SUBSTITUIDO.value
            await self.db.flush()

        # 2. Generate S3 key and upload file
        file_ext = ""
        if file.filename:
            parts = file.filename.rsplit(".", 1)
            if len(parts) > 1:
                file_ext = f".{parts[1]}"
        s3_key = f"documentos-oficiais/{entidade.value}/{entidade_id}/{uuid.uuid4().hex}{file_ext}"

        s3_client = boto3.client("s3", region_name=settings.S3_REGION)
        file_content = await file.read()
        content_type = file.content_type or "application/octet-stream"
        s3_client.put_object(
            Bucket=settings.S3_BUCKET,
            Key=s3_key,
            Body=file_content,
            ContentType=content_type,
        )

        # 3. Determine initial status (check if already expired)
        status = DocumentoStatus.ATIVO.value
        if data_validade is not None and data_validade < date.today():
            status = DocumentoStatus.VENCIDO.value

        # 4. Create DB record
        documento = await self.repo.create(
            entidade=entidade.value,
            entidade_id=entidade_id,
            tipo_documento=tipo_documento,
            descricao=descricao,
            nome_arquivo=file.filename or "unnamed",
            content_type=content_type,
            s3_key=s3_key,
            bucket_s3=settings.S3_BUCKET,
            data_emissao=data_emissao,
            data_validade=data_validade,
            status=status,
            enviado_por=enviado_por,
        )

        await self.auditoria.registrar(
            entidade=ENTIDADE,
            entidade_id=documento.id,
            acao="CRIACAO",
            valor_anterior=None,
            valor_novo=entity_to_dict(documento),
            usuario_id=enviado_por,
        )

        return documento

    async def get_documento(self, documento_id: int) -> DocumentoOficial:
        """Get a document by ID. Also checks and updates expiration status."""
        doc = await self.repo.get_by_id(documento_id)
        # Check expiration on access (Req 15.4)
        if (
            doc.status == DocumentoStatus.ATIVO.value
            and doc.data_validade is not None
            and doc.data_validade < date.today()
        ):
            doc.status = DocumentoStatus.VENCIDO.value
            await self.db.flush()
            await self.db.refresh(doc)
        return doc

    async def get_download_url(self, documento_id: int) -> str:
        """Generate a pre-signed S3 URL for downloading the document (Req 15.7)."""
        doc = await self.repo.get_by_id(documento_id)

        s3_client = boto3.client("s3", region_name=settings.S3_REGION)
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": doc.bucket_s3 or settings.S3_BUCKET,
                "Key": doc.s3_key,
            },
            ExpiresIn=settings.S3_PRESIGNED_URL_EXPIRATION,
        )
        return url

    async def list_documentos(
        self,
        page: int = 1,
        page_size: int = 20,
        entidade: str | None = None,
        entidade_id: int | None = None,
        tipo_documento: str | None = None,
        status: str | None = None,
    ) -> PaginatedResult[DocumentoOficial]:
        """List documents with optional filters. Marks expired docs before listing (Req 15.4)."""
        # Mark expired documents before listing
        await self.repo.mark_expired_documents()

        return await self.repo.list_filtered(
            page=page,
            page_size=page_size,
            entidade=entidade,
            entidade_id=entidade_id,
            tipo_documento=tipo_documento,
            status=status,
        )

    async def update_status(
        self, documento_id: int, status: DocumentoStatus, usuario_id: int | None = None
    ) -> DocumentoOficial:
        """Manually update document status (e.g., mark as INATIVO)."""
        doc = await self.repo.get_by_id(documento_id)
        old_values = entity_to_dict(doc)
        doc.status = status.value
        await self.db.flush()
        await self.db.refresh(doc)
        if usuario_id is not None:
            await self.auditoria.registrar(
                entidade=ENTIDADE,
                entidade_id=documento_id,
                acao="ATUALIZACAO",
                valor_anterior=old_values,
                valor_novo=entity_to_dict(doc),
                usuario_id=usuario_id,
            )
        return doc
