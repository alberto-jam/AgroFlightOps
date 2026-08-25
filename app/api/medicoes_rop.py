"""API routes for Medição ROP — restricted to Administrador and Financeiro."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_perfil
from app.schemas.base import PaginatedResponse
from app.schemas.gestao_relatorios_medicao import (
    EnviarRelatorioRequest,
    EnviarRelatorioResponse,
    ExcluirRelatorioResponse,
    RelatorioDownloadResponse,
    RelatorioMedicaoListItem,
)
from app.schemas.medicao_rop import MedicaoRopMissaoResponse
from app.schemas.relatorio_medicao_rop import (
    GerarRelatorioMedicaoRequest,
    RelatorioMedicaoGeradoResponse,
    RelatorioMedicaoPreviewRequest,
    RelatorioMedicaoPreviewResponse,
)
from app.services.gestao_relatorios_medicao_service import GestaoRelatoriosMedicaoService
from app.services.medicao_rop_service import MedicaoRopService
from app.services.relatorio_medicao_rop_service import RelatorioMedicaoRopService

router = APIRouter(
    prefix="/medicoes-rop",
    tags=["Medição ROP"],
    dependencies=[Depends(require_perfil("ADMINISTRADOR", "FINANCEIRO"))],
)


@router.get("", response_model=PaginatedResponse[MedicaoRopMissaoResponse])
async def list_missoes_medicao_rop(
    db: Annotated[AsyncSession, Depends(get_db)],
    cliente_id: int = Query(..., description="ID do cliente (obrigatório)"),
    data_inicial: date = Query(..., description="Data inicial do período (obrigatório)"),
    data_final: date = Query(..., description="Data final do período (obrigatório)"),
    propriedade_id: int | None = Query(None, description="ID da propriedade (None = todas)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List eligible missions for ROP measurement within the given filters."""
    service = MedicaoRopService(db)
    result = await service.list_missoes_elegiveis(
        cliente_id=cliente_id,
        data_inicial=data_inicial,
        data_final=data_final,
        propriedade_id=propriedade_id,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        items=[MedicaoRopMissaoResponse.model_validate(m) for m in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        pages=result.pages,
    )


@router.post("/preview", response_model=RelatorioMedicaoPreviewResponse)
async def preview_relatorio_medicao(
    body: RelatorioMedicaoPreviewRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RelatorioMedicaoPreviewResponse:
    """Retorna dados formatados para preview do relatório de medição."""
    service = RelatorioMedicaoRopService(db)
    return await service.get_preview_data(
        missao_ids=body.missao_ids,
        cliente_id=body.cliente_id,
    )


@router.post("/gerar-relatorio", response_model=RelatorioMedicaoGeradoResponse)
async def gerar_relatorio_medicao(
    body: GerarRelatorioMedicaoRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RelatorioMedicaoGeradoResponse:
    """Gera PDF do relatório, salva no S3 e marca missões como enviadas."""
    service = RelatorioMedicaoRopService(db)
    return await service.gerar_relatorio(
        missao_ids=body.missao_ids,
        cliente_id=body.cliente_id,
        data_inicial=body.data_inicial,
        data_final=body.data_final,
    )



# ============================================================================
# Gestão de Relatórios de Medição — endpoints
# ============================================================================


@router.get("/relatorios", response_model=PaginatedResponse[RelatorioMedicaoListItem])
async def listar_relatorios(
    db: Annotated[AsyncSession, Depends(get_db)],
    cliente_id: int | None = Query(None, description="Filtrar por cliente"),
    data_inicial: date | None = Query(None, description="Filtrar por data_inicial >= valor"),
    data_final: date | None = Query(None, description="Filtrar por data_final <= valor"),
    status: str | None = Query(None, description="Filtrar por status (ATIVO ou EXCLUIDO)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List generated reports with filters and pagination."""
    service = GestaoRelatoriosMedicaoService(db)
    # Default to ATIVO when status not specified
    effective_status = status if status is not None else "ATIVO"
    result = await service.listar_relatorios(
        cliente_id=cliente_id,
        data_inicial=data_inicial,
        data_final=data_final,
        status=effective_status,
        page=page,
        page_size=page_size,
    )
    items = [
        RelatorioMedicaoListItem(
            id=r.id,
            cliente_nome=r.cliente.nome,
            data_inicial=r.data_inicial,
            data_final=r.data_final,
            total_area=r.total_area,
            qtd_missoes=r.qtd_missoes,
            gerado_em=r.gerado_em,
            status=r.status,
            enviado_em=r.enviado_em,
        )
        for r in result.items
    ]
    return PaginatedResponse(
        items=items,
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        pages=result.pages,
    )


@router.get("/relatorios/{relatorio_id}/download", response_model=RelatorioDownloadResponse)
async def download_relatorio(
    relatorio_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Generate a presigned URL to download a report PDF."""
    service = GestaoRelatoriosMedicaoService(db)
    url = await service.download_relatorio(relatorio_id)
    return RelatorioDownloadResponse(download_url=url)


@router.delete("/relatorios/{relatorio_id}", response_model=ExcluirRelatorioResponse)
async def excluir_relatorio(
    relatorio_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Soft-delete a report: marks as EXCLUIDO, clears missions, removes S3 file."""
    service = GestaoRelatoriosMedicaoService(db)
    await service.excluir_relatorio(relatorio_id)
    return ExcluirRelatorioResponse(mensagem="Relatório excluído com sucesso")


@router.post("/relatorios/{relatorio_id}/enviar", response_model=EnviarRelatorioResponse)
async def enviar_relatorio(
    relatorio_id: int,
    body: EnviarRelatorioRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Send report download link to specified email addresses via SES."""
    service = GestaoRelatoriosMedicaoService(db)
    await service.enviar_relatorio(
        relatorio_id=relatorio_id,
        emails=body.emails,
        mensagem=body.mensagem,
    )
    return EnviarRelatorioResponse(mensagem="Relatório enviado com sucesso")
