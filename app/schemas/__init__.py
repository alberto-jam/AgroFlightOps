"""Pydantic schemas package."""

from app.schemas.auditoria import AuditoriaResponse
from app.schemas.base import PaginatedResponse, TimestampMixin
from app.schemas.bateria import BateriaCreate, BateriaResponse, BateriaUpdate
from app.schemas.checklist import (
    ChecklistMissaoResponse,
    ItemChecklistMissaoResponse,
    ItemChecklistMissaoUpdate,
)
from app.schemas.checklist_padrao import (
    ItemChecklistPadraoCreate,
    ItemChecklistPadraoResponse,
    ItemChecklistPadraoUpdate,
)
from app.schemas.cliente import ClienteCreate, ClienteResponse, ClienteUpdate
from app.schemas.cultura import CulturaCreate, CulturaResponse, CulturaUpdate
from app.schemas.documento_oficial import (
    DocumentoOficialCreate,
    DocumentoOficialResponse,
    DocumentoOficialUpdate,
)
from app.schemas.drone import DroneCreate, DroneResponse, DroneUpdate
from app.schemas.evidencia import EvidenciaCreate, EvidenciaResponse
from app.schemas.financeiro import (
    FinanceiroMissaoResponse,
    FinanceiroMissaoUpdate,
)
from app.schemas.insumo import InsumoCreate, InsumoResponse, InsumoUpdate
from app.schemas.manutencao import ManutencaoCreate, ManutencaoResponse, ManutencaoUpdate
from app.schemas.missao import (
    HistoricoStatusMissaoResponse,
    MissaoCreate,
    MissaoResponse,
    MissaoTransicao,
    MissaoUpdate,
)
from app.schemas.missao_bateria import MissaoBateriaCreate, MissaoBateriaResponse
from app.schemas.ocorrencia import OcorrenciaCreate, OcorrenciaResponse
from app.schemas.ordem_servico import (
    HistoricoStatusOSResponse,
    OrdemServicoCreate,
    OrdemServicoResponse,
    OrdemServicoTransicao,
    OrdemServicoUpdate,
)
from app.schemas.perfil import PerfilCreate, PerfilResponse, PerfilUpdate
from app.schemas.propriedade import (
    PropriedadeCreate,
    PropriedadeResponse,
    PropriedadeUpdate,
)
from app.schemas.reserva_insumo import (
    ConsumoInsumoMissaoCreate,
    ConsumoInsumoMissaoResponse,
    ReservaInsumoCreate,
    ReservaInsumoResponse,
)
from app.schemas.talhao import TalhaoCreate, TalhaoResponse, TalhaoUpdate
from app.schemas.telemetria import (
    AnomaliaResponse,
    InsightResponse,
    TelemetriaResumoResponse,
    TelemetriaUploadResponse,
)
from app.schemas.tipo_ocorrencia import (
    TipoOcorrenciaCreate,
    TipoOcorrenciaResponse,
    TipoOcorrenciaUpdate,
)
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioUpdate

__all__ = [
    # Base
    "PaginatedResponse",
    "TimestampMixin",
    # Perfil
    "PerfilCreate",
    "PerfilUpdate",
    "PerfilResponse",
    # Usuario
    "UsuarioCreate",
    "UsuarioUpdate",
    "UsuarioResponse",
    # Cliente
    "ClienteCreate",
    "ClienteUpdate",
    "ClienteResponse",
    # Propriedade
    "PropriedadeCreate",
    "PropriedadeUpdate",
    "PropriedadeResponse",
    # Talhao
    "TalhaoCreate",
    "TalhaoUpdate",
    "TalhaoResponse",
    # Cultura
    "CulturaCreate",
    "CulturaUpdate",
    "CulturaResponse",
    # Drone
    "DroneCreate",
    "DroneUpdate",
    "DroneResponse",
    # Bateria
    "BateriaCreate",
    "BateriaUpdate",
    "BateriaResponse",
    # Insumo
    "InsumoCreate",
    "InsumoUpdate",
    "InsumoResponse",
    # TipoOcorrencia
    "TipoOcorrenciaCreate",
    "TipoOcorrenciaUpdate",
    "TipoOcorrenciaResponse",
    # ItemChecklistPadrao
    "ItemChecklistPadraoCreate",
    "ItemChecklistPadraoUpdate",
    "ItemChecklistPadraoResponse",
    # OrdemServico
    "OrdemServicoCreate",
    "OrdemServicoUpdate",
    "OrdemServicoTransicao",
    "OrdemServicoResponse",
    "HistoricoStatusOSResponse",
    # Missao
    "MissaoCreate",
    "MissaoUpdate",
    "MissaoTransicao",
    "MissaoResponse",
    "HistoricoStatusMissaoResponse",
    # MissaoBateria
    "MissaoBateriaCreate",
    "MissaoBateriaResponse",
    # ReservaInsumo / Consumo
    "ReservaInsumoCreate",
    "ReservaInsumoResponse",
    "ConsumoInsumoMissaoCreate",
    "ConsumoInsumoMissaoResponse",
    # Checklist
    "ChecklistMissaoResponse",
    "ItemChecklistMissaoResponse",
    "ItemChecklistMissaoUpdate",
    # Ocorrencia
    "OcorrenciaCreate",
    "OcorrenciaResponse",
    # Evidencia
    "EvidenciaCreate",
    "EvidenciaResponse",
    # Manutencao
    "ManutencaoCreate",
    "ManutencaoUpdate",
    "ManutencaoResponse",
    # Financeiro
    "FinanceiroMissaoUpdate",
    "FinanceiroMissaoResponse",
    # Auditoria
    "AuditoriaResponse",
    # DocumentoOficial
    "DocumentoOficialCreate",
    "DocumentoOficialUpdate",
    "DocumentoOficialResponse",
    # Telemetria
    "TelemetriaUploadResponse",
    "TelemetriaResumoResponse",
    "AnomaliaResponse",
    "InsightResponse",
]
