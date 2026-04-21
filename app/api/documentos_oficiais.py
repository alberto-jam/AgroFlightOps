"""API routes for DocumentoOficial upload, download and listing."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_perfil
from app.models.enums import DocumentoEntidade, DocumentoStatus
from app.models.models import Usuario
from app.schemas.base import PaginatedResponse
from app.schemas.documento_oficial import DocumentoOficialResponse
from app.services.documento_service import DocumentoService

router = APIRouter(
    prefix="/documentos-oficiais",
    tags=["Documentos Oficiais"],
)


@router.post(
    "",
    response_model=DocumentoOficialResponse,
    status_code=201,
    dependencies=[Depends(require_perfil("ADMINISTRADOR"))],
)
async def upload_documento(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Usuario, Depends(get_current_user)],
    file: UploadFile = File(...),
    entidade: DocumentoEntidade = Form(...),
    entidade_id: int = Form(...),
    tipo_documento: str = Form(...),
    descricao: str | None = Form(None),
    data_emissao: date | None = Form(None),
    data_validade: date | None = Form(None),
):
    """Upload a new official document to S3 with metadata stored in DB."""
    service = DocumentoService(db)
    documento = await service.upload_documento(
        file=file,
        entidade=entidade,
        entidade_id=entidade_id,
        tipo_documento=tipo_documento,
        enviado_por=current_user.id,
        descricao=descricao,
        data_emissao=data_emissao,
        data_validade=data_validade,
    )
    return documento


@router.get(
    "",
    response_model=PaginatedResponse[DocumentoOficialResponse],
    dependencies=[Depends(get_current_user)],
)
async def list_documentos(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    entidade: DocumentoEntidade | None = Query(None),
    entidade_id: int | None = Query(None),
    tipo_documento: str | None = Query(None),
    status: DocumentoStatus | None = Query(None),
):
    """List official documents with pagination and optional filters."""
    service = DocumentoService(db)
    result = await service.list_documentos(
        page=page,
        page_size=page_size,
        entidade=entidade.value if entidade else None,
        entidade_id=entidade_id,
        tipo_documento=tipo_documento,
        status=status.value if status else None,
    )
    return PaginatedResponse(
        items=[DocumentoOficialResponse.model_validate(d) for d in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        pages=result.pages,
    )


@router.get(
    "/{documento_id}",
    response_model=DocumentoOficialResponse,
    dependencies=[Depends(get_current_user)],
)
async def get_documento(
    documento_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a document by ID."""
    service = DocumentoService(db)
    return await service.get_documento(documento_id)


@router.get(
    "/{documento_id}/download",
    dependencies=[Depends(get_current_user)],
)
async def download_documento(
    documento_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a pre-signed S3 URL for downloading the document."""
    service = DocumentoService(db)
    url = await service.get_download_url(documento_id)
    return {"url": url, "expires_in": settings.S3_PRESIGNED_URL_EXPIRATION}
