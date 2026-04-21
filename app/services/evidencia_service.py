"""Business logic for Evidencia upload and listing."""

import uuid
from decimal import Decimal

import boto3
from fastapi import UploadFile
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import BusinessRuleViolationError, EntityNotFoundError
from app.models.enums import MissaoStatus
from app.models.models import Evidencia, Missao
from app.repositories.base_repository import PaginatedResult


class EvidenciaService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upload_evidencia(
        self,
        missao_id: int,
        file: UploadFile,
        enviado_por: int,
        latitude: Decimal | None = None,
        longitude: Decimal | None = None,
    ) -> Evidencia:
        """Upload an evidence file to S3 and register metadata in DB."""
        # 1. Validate mission exists
        missao = await self.db.get(Missao, missao_id)
        if missao is None:
            raise EntityNotFoundError(f"missoes com id={missao_id} não encontrado")

        # 2. Validate mission status is EM_EXECUCAO
        if missao.status != MissaoStatus.EM_EXECUCAO.value:
            raise BusinessRuleViolationError(
                "Upload de evidência só é permitido quando a missão está EM_EXECUCAO"
            )

        # 3. Generate S3 key and upload
        file_ext = ""
        if file.filename:
            parts = file.filename.rsplit(".", 1)
            if len(parts) > 1:
                file_ext = f".{parts[1]}"
        s3_key = f"evidencias/missao-{missao_id}/{uuid.uuid4().hex}{file_ext}"

        s3_client = boto3.client("s3", region_name=settings.S3_REGION)
        file_content = await file.read()
        s3_client.put_object(
            Bucket=settings.S3_BUCKET,
            Key=s3_key,
            Body=file_content,
            ContentType=file.content_type or "application/octet-stream",
        )

        # 4. Build the URL
        url_arquivo = f"https://{settings.S3_BUCKET}.s3.{settings.S3_REGION}.amazonaws.com/{s3_key}"

        # 5. Create DB record
        evidencia = Evidencia(
            missao_id=missao_id,
            nome_arquivo=file.filename or "unnamed",
            url_arquivo=url_arquivo,
            tipo_arquivo=file.content_type,
            latitude=latitude,
            longitude=longitude,
            enviado_por=enviado_por,
        )
        self.db.add(evidencia)
        await self.db.flush()
        await self.db.refresh(evidencia)

        return evidencia

    async def list_evidencias(
        self,
        missao_id: int | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResult[Evidencia]:
        """List evidence files with optional mission filter."""
        page_size = max(1, min(page_size, 100))
        page = max(1, page)

        query: Select = select(Evidencia)
        if missao_id is not None:
            query = query.where(Evidencia.missao_id == missao_id)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Evidencia.id)
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return PaginatedResult(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )
