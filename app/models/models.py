"""SQLAlchemy ORM models — 1:1 mapping with DDL tables."""

from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# ============================================================================
# TABELAS BASE
# ============================================================================


class Perfil(Base):
    __tablename__ = "perfis"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="perfil")


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(Text, nullable=False)
    perfil_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("perfis.id"), nullable=False
    )
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    perfil: Mapped["Perfil"] = relationship(back_populates="usuarios")


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    cpf_cnpj: Mapped[str | None] = mapped_column(String(18))
    telefone: Mapped[str | None] = mapped_column(String(30))
    email: Mapped[str | None] = mapped_column(String(255))
    endereco: Mapped[str | None] = mapped_column(String(255))
    numero: Mapped[str | None] = mapped_column(String(20))
    complemento: Mapped[str | None] = mapped_column(String(120))
    bairro: Mapped[str | None] = mapped_column(String(120))
    municipio: Mapped[str | None] = mapped_column(String(120))
    estado: Mapped[str | None] = mapped_column(String(2))
    cep: Mapped[str | None] = mapped_column(String(12))
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    referencia_local: Mapped[str | None] = mapped_column(String(255))
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "latitude IS NULL OR latitude BETWEEN -90 AND 90",
            name="ck_clientes_latitude",
        ),
        CheckConstraint(
            "longitude IS NULL OR longitude BETWEEN -180 AND 180",
            name="ck_clientes_longitude",
        ),
    )

    # Relationships
    propriedades: Mapped[list["Propriedade"]] = relationship(back_populates="cliente")
    ordens_servico: Mapped[list["OrdemServico"]] = relationship(
        back_populates="cliente"
    )


class Propriedade(Base):
    __tablename__ = "propriedades"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    cliente_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("clientes.id"), nullable=False
    )
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    endereco: Mapped[str | None] = mapped_column(String(255))
    numero: Mapped[str | None] = mapped_column(String(20))
    complemento: Mapped[str | None] = mapped_column(String(120))
    bairro: Mapped[str | None] = mapped_column(String(120))
    municipio: Mapped[str] = mapped_column(String(120), nullable=False)
    estado: Mapped[str] = mapped_column(String(2), nullable=False)
    cep: Mapped[str | None] = mapped_column(String(12))
    localizacao_descritiva: Mapped[str | None] = mapped_column(Text)
    referencia_local: Mapped[str | None] = mapped_column(String(255))
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    area_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint("area_total >= 0", name="ck_propriedades_area_total"),
        CheckConstraint(
            "latitude IS NULL OR latitude BETWEEN -90 AND 90",
            name="ck_propriedades_latitude",
        ),
        CheckConstraint(
            "longitude IS NULL OR longitude BETWEEN -180 AND 180",
            name="ck_propriedades_longitude",
        ),
    )

    # Relationships
    cliente: Mapped["Cliente"] = relationship(back_populates="propriedades")
    talhoes: Mapped[list["Talhao"]] = relationship(back_populates="propriedade")
    ordens_servico: Mapped[list["OrdemServico"]] = relationship(
        back_populates="propriedade"
    )


class Cultura(Base):
    __tablename__ = "culturas"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    talhoes: Mapped[list["Talhao"]] = relationship(back_populates="cultura")


class Talhao(Base):
    __tablename__ = "talhoes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    propriedade_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("propriedades.id"), nullable=False
    )
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    area_hectares: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    cultura_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("culturas.id"), nullable=False
    )
    observacoes: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    ponto_referencia: Mapped[str | None] = mapped_column(String(255))
    geojson: Mapped[dict | None] = mapped_column(JSON)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("propriedade_id", "nome", name="uq_talhoes_propriedade_nome"),
        CheckConstraint("area_hectares >= 0", name="ck_talhoes_area_hectares"),
        CheckConstraint(
            "latitude IS NULL OR latitude BETWEEN -90 AND 90",
            name="ck_talhoes_latitude",
        ),
        CheckConstraint(
            "longitude IS NULL OR longitude BETWEEN -180 AND 180",
            name="ck_talhoes_longitude",
        ),
    )

    # Relationships
    propriedade: Mapped["Propriedade"] = relationship(back_populates="talhoes")
    cultura: Mapped["Cultura"] = relationship(back_populates="talhoes")
    ordens_servico: Mapped[list["OrdemServico"]] = relationship(
        back_populates="talhao"
    )


class Drone(Base):
    __tablename__ = "drones"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    identificacao: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False
    )
    modelo: Mapped[str] = mapped_column(String(120), nullable=False)
    fabricante: Mapped[str | None] = mapped_column(String(120))
    capacidade_litros: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    horas_voadas: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=0
    )
    ultima_manutencao_em: Mapped[date | None] = mapped_column(Date)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint("capacidade_litros >= 0", name="ck_drones_capacidade_litros"),
        CheckConstraint("horas_voadas >= 0", name="ck_drones_horas_voadas"),
        CheckConstraint(
            "status IN ('DISPONIVEL','EM_USO','EM_MANUTENCAO','BLOQUEADO','INATIVO')",
            name="ck_drones_status",
        ),
    )

    # Relationships
    baterias: Mapped[list["Bateria"]] = relationship(back_populates="drone")
    missoes: Mapped[list["Missao"]] = relationship(back_populates="drone")
    manutencoes: Mapped[list["Manutencao"]] = relationship(back_populates="drone")


class Bateria(Base):
    __tablename__ = "baterias"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    identificacao: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False
    )
    drone_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("drones.id"))
    ciclos: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    observacoes: Mapped[str | None] = mapped_column(Text)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint("ciclos >= 0", name="ck_baterias_ciclos"),
        CheckConstraint(
            "status IN ('DISPONIVEL','EM_USO','CARREGANDO','REPROVADA','DESCARTADA')",
            name="ck_baterias_status",
        ),
    )

    # Relationships
    drone: Mapped["Drone | None"] = relationship(back_populates="baterias")
    missao_baterias: Mapped[list["MissaoBateria"]] = relationship(
        back_populates="bateria"
    )


class Insumo(Base):
    __tablename__ = "insumos"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    fabricante: Mapped[str | None] = mapped_column(String(120))
    unidade_medida: Mapped[str] = mapped_column(String(30), nullable=False)
    saldo_atual: Mapped[Decimal] = mapped_column(
        Numeric(14, 3), nullable=False, default=0
    )
    lote: Mapped[str | None] = mapped_column(String(100))
    validade: Mapped[date | None] = mapped_column(Date)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint("saldo_atual >= 0", name="ck_insumos_saldo_atual"),
    )

    # Relationships
    reservas: Mapped[list["ReservaInsumo"]] = relationship(back_populates="insumo")
    consumos: Mapped[list["ConsumoInsumoMissao"]] = relationship(
        back_populates="insumo"
    )


class TipoOcorrencia(Base):
    __tablename__ = "tipos_ocorrencia"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    ocorrencias: Mapped[list["Ocorrencia"]] = relationship(
        back_populates="tipo_ocorrencia"
    )


class ItemChecklistPadrao(Base):
    __tablename__ = "itens_checklist_padrao"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nome_item: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    obrigatorio: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    ordem_exibicao: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "ordem_exibicao >= 0", name="ck_itens_checklist_padrao_ordem_exibicao"
        ),
    )


# ============================================================================
# ORDENS DE SERVIÇO E MISSÕES
# ============================================================================


class OrdemServico(Base):
    __tablename__ = "ordens_servico"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    cliente_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("clientes.id"), nullable=False
    )
    propriedade_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("propriedades.id"), nullable=False
    )
    talhao_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("talhoes.id"), nullable=False
    )
    cultura_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("culturas.id"), nullable=False
    )
    tipo_aplicacao: Mapped[str] = mapped_column(String(120), nullable=False)
    prioridade: Mapped[str] = mapped_column(String(30), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    data_prevista: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    motivo_rejeicao: Mapped[str | None] = mapped_column(Text)
    motivo_cancelamento: Mapped[str | None] = mapped_column(Text)
    criado_por: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("usuarios.id"), nullable=False
    )
    aprovado_por: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("usuarios.id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('RASCUNHO','EM_ANALISE','APROVADA','REJEITADA','CANCELADA')",
            name="ck_ordens_servico_status",
        ),
        CheckConstraint(
            "prioridade IN ('BAIXA','MEDIA','ALTA','CRITICA')",
            name="ck_ordens_servico_prioridade",
        ),
    )

    # Relationships
    cliente: Mapped["Cliente"] = relationship(back_populates="ordens_servico")
    propriedade: Mapped["Propriedade"] = relationship(back_populates="ordens_servico")
    talhao: Mapped["Talhao"] = relationship(back_populates="ordens_servico")
    cultura: Mapped["Cultura"] = relationship()
    criador: Mapped["Usuario"] = relationship(foreign_keys=[criado_por])
    aprovador: Mapped["Usuario | None"] = relationship(foreign_keys=[aprovado_por])
    historico_status: Mapped[list["HistoricoStatusOS"]] = relationship(
        back_populates="ordem_servico", cascade="all, delete-orphan"
    )
    missoes: Mapped[list["Missao"]] = relationship(back_populates="ordem_servico")


class HistoricoStatusOS(Base):
    __tablename__ = "historico_status_os"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ordem_servico_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("ordens_servico.id", ondelete="CASCADE"), nullable=False
    )
    status_anterior: Mapped[str | None] = mapped_column(String(30))
    status_novo: Mapped[str] = mapped_column(String(30), nullable=False)
    motivo: Mapped[str | None] = mapped_column(Text)
    alterado_por: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("usuarios.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    # Relationships
    ordem_servico: Mapped["OrdemServico"] = relationship(
        back_populates="historico_status"
    )
    usuario: Mapped["Usuario"] = relationship()


class Missao(Base):
    __tablename__ = "missoes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    ordem_servico_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("ordens_servico.id"), nullable=False
    )
    piloto_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("usuarios.id"), nullable=False
    )
    tecnico_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("usuarios.id")
    )
    drone_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("drones.id"), nullable=False
    )
    data_agendada: Mapped[date] = mapped_column(Date, nullable=False)
    hora_agendada: Mapped[time] = mapped_column(Time, nullable=False)
    area_prevista: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    area_realizada: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    volume_previsto: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    volume_realizado: Mapped[Decimal | None] = mapped_column(Numeric(14, 3))
    janela_operacional: Mapped[str | None] = mapped_column(String(255))
    restricoes: Mapped[str | None] = mapped_column(Text)
    observacoes_planejamento: Mapped[str | None] = mapped_column(Text)
    observacoes_execucao: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    latitude_operacao: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    longitude_operacao: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    endereco_operacao: Mapped[str | None] = mapped_column(String(255))
    referencia_operacao: Mapped[str | None] = mapped_column(String(255))
    iniciado_em: Mapped[datetime | None] = mapped_column(DateTime)
    finalizado_em: Mapped[datetime | None] = mapped_column(DateTime)
    encerrado_tecnicamente_em: Mapped[datetime | None] = mapped_column(DateTime)
    encerrado_financeiramente_em: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint("area_prevista >= 0", name="ck_missoes_area_prevista"),
        CheckConstraint(
            "area_realizada IS NULL OR area_realizada >= 0",
            name="ck_missoes_area_realizada",
        ),
        CheckConstraint("volume_previsto >= 0", name="ck_missoes_volume_previsto"),
        CheckConstraint(
            "volume_realizado IS NULL OR volume_realizado >= 0",
            name="ck_missoes_volume_realizado",
        ),
        CheckConstraint(
            "status IN ('RASCUNHO','PLANEJADA','AGENDADA','EM_CHECKLIST','LIBERADA','EM_EXECUCAO','PAUSADA','CONCLUIDA','CANCELADA','ENCERRADA_TECNICAMENTE','ENCERRADA_FINANCEIRAMENTE')",
            name="ck_missoes_status",
        ),
        CheckConstraint(
            "latitude_operacao IS NULL OR latitude_operacao BETWEEN -90 AND 90",
            name="ck_missoes_latitude_operacao",
        ),
        CheckConstraint(
            "longitude_operacao IS NULL OR longitude_operacao BETWEEN -180 AND 180",
            name="ck_missoes_longitude_operacao",
        ),
        CheckConstraint(
            "finalizado_em IS NULL OR iniciado_em IS NULL OR finalizado_em >= iniciado_em",
            name="ck_missoes_timestamps",
        ),
    )

    # Relationships
    ordem_servico: Mapped["OrdemServico"] = relationship(back_populates="missoes")
    piloto: Mapped["Usuario"] = relationship(foreign_keys=[piloto_id])
    tecnico: Mapped["Usuario | None"] = relationship(foreign_keys=[tecnico_id])
    drone: Mapped["Drone"] = relationship(back_populates="missoes")
    historico_status: Mapped[list["HistoricoStatusMissao"]] = relationship(
        back_populates="missao", cascade="all, delete-orphan"
    )
    missao_baterias: Mapped[list["MissaoBateria"]] = relationship(
        back_populates="missao", cascade="all, delete-orphan"
    )
    reservas_insumo: Mapped[list["ReservaInsumo"]] = relationship(
        back_populates="missao", cascade="all, delete-orphan"
    )
    consumos_insumo: Mapped[list["ConsumoInsumoMissao"]] = relationship(
        back_populates="missao", cascade="all, delete-orphan"
    )
    checklist: Mapped["ChecklistMissao | None"] = relationship(
        back_populates="missao", cascade="all, delete-orphan", uselist=False
    )
    ocorrencias: Mapped[list["Ocorrencia"]] = relationship(
        back_populates="missao", cascade="all, delete-orphan"
    )
    evidencias: Mapped[list["Evidencia"]] = relationship(
        back_populates="missao", cascade="all, delete-orphan"
    )
    financeiro: Mapped["FinanceiroMissao | None"] = relationship(
        back_populates="missao", cascade="all, delete-orphan", uselist=False
    )


class HistoricoStatusMissao(Base):
    __tablename__ = "historico_status_missao"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    missao_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("missoes.id", ondelete="CASCADE"), nullable=False
    )
    status_anterior: Mapped[str | None] = mapped_column(String(40))
    status_novo: Mapped[str] = mapped_column(String(40), nullable=False)
    motivo: Mapped[str | None] = mapped_column(Text)
    alterado_por: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("usuarios.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    # Relationships
    missao: Mapped["Missao"] = relationship(back_populates="historico_status")
    usuario: Mapped["Usuario"] = relationship()


class MissaoBateria(Base):
    __tablename__ = "missao_baterias"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    missao_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("missoes.id", ondelete="CASCADE"), nullable=False
    )
    bateria_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("baterias.id"), nullable=False
    )
    ordem_uso: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("missao_id", "bateria_id", name="uq_missao_baterias"),
        UniqueConstraint("missao_id", "ordem_uso", name="uq_missao_baterias_ordem"),
        CheckConstraint("ordem_uso > 0", name="ck_missao_baterias_ordem_uso"),
    )

    # Relationships
    missao: Mapped["Missao"] = relationship(back_populates="missao_baterias")
    bateria: Mapped["Bateria"] = relationship(back_populates="missao_baterias")


class ReservaInsumo(Base):
    __tablename__ = "reservas_insumo"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    missao_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("missoes.id", ondelete="CASCADE"), nullable=False
    )
    insumo_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("insumos.id"), nullable=False
    )
    quantidade_prevista: Mapped[Decimal] = mapped_column(
        Numeric(14, 3), nullable=False
    )
    unidade_medida: Mapped[str] = mapped_column(String(30), nullable=False)
    justificativa_excesso: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "quantidade_prevista >= 0", name="ck_reservas_insumo_quantidade_prevista"
        ),
    )

    # Relationships
    missao: Mapped["Missao"] = relationship(back_populates="reservas_insumo")
    insumo: Mapped["Insumo"] = relationship(back_populates="reservas")


class ConsumoInsumoMissao(Base):
    __tablename__ = "consumos_insumo_missao"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    missao_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("missoes.id", ondelete="CASCADE"), nullable=False
    )
    insumo_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("insumos.id"), nullable=False
    )
    quantidade_realizada: Mapped[Decimal] = mapped_column(
        Numeric(14, 3), nullable=False
    )
    unidade_medida: Mapped[str] = mapped_column(String(30), nullable=False)
    observacoes: Mapped[str | None] = mapped_column(Text)
    justificativa_excesso: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "quantidade_realizada >= 0",
            name="ck_consumos_insumo_missao_quantidade_realizada",
        ),
    )

    # Relationships
    missao: Mapped["Missao"] = relationship(back_populates="consumos_insumo")
    insumo: Mapped["Insumo"] = relationship(back_populates="consumos")


# ============================================================================
# CHECKLISTS
# ============================================================================


class ChecklistMissao(Base):
    __tablename__ = "checklists_missao"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    missao_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("missoes.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    status_geral: Mapped[str] = mapped_column(String(30), nullable=False)
    preenchido_por: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("usuarios.id"), nullable=False
    )
    revisado_por: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("usuarios.id")
    )
    preenchido_em: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revisado_em: Mapped[datetime | None] = mapped_column(DateTime)
    observacoes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "status_geral IN ('PENDENTE','EM_PREENCHIMENTO','CONCLUIDO','REPROVADO','APROVADO')",
            name="ck_checklists_missao_status_geral",
        ),
        CheckConstraint(
            "revisado_em IS NULL OR revisado_em >= preenchido_em",
            name="ck_checklists_missao_revisado_em",
        ),
    )

    # Relationships
    missao: Mapped["Missao"] = relationship(back_populates="checklist")
    preenchedor: Mapped["Usuario"] = relationship(foreign_keys=[preenchido_por])
    revisor: Mapped["Usuario | None"] = relationship(foreign_keys=[revisado_por])
    itens: Mapped[list["ItemChecklistMissao"]] = relationship(
        back_populates="checklist", cascade="all, delete-orphan"
    )


class ItemChecklistMissao(Base):
    __tablename__ = "itens_checklist_missao"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    checklist_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("checklists_missao.id", ondelete="CASCADE"),
        nullable=False,
    )
    nome_item: Mapped[str] = mapped_column(String(200), nullable=False)
    obrigatorio: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status_item: Mapped[str] = mapped_column(String(20), nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "status_item IN ('PENDENTE','APROVADO','REPROVADO','NAO_APLICAVEL')",
            name="ck_itens_checklist_missao_status_item",
        ),
    )

    # Relationships
    checklist: Mapped["ChecklistMissao"] = relationship(back_populates="itens")


# ============================================================================
# OCORRÊNCIAS E EVIDÊNCIAS
# ============================================================================


class Ocorrencia(Base):
    __tablename__ = "ocorrencias"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    missao_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("missoes.id", ondelete="CASCADE"), nullable=False
    )
    tipo_ocorrencia_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("tipos_ocorrencia.id"), nullable=False
    )
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    severidade: Mapped[str] = mapped_column(String(20), nullable=False)
    registrada_por: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("usuarios.id"), nullable=False
    )
    registrada_em: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "severidade IN ('BAIXA','MEDIA','ALTA','CRITICA')",
            name="ck_ocorrencias_severidade",
        ),
    )

    # Relationships
    missao: Mapped["Missao"] = relationship(back_populates="ocorrencias")
    tipo_ocorrencia: Mapped["TipoOcorrencia"] = relationship(
        back_populates="ocorrencias"
    )
    registrador: Mapped["Usuario"] = relationship()


class Evidencia(Base):
    __tablename__ = "evidencias"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    missao_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("missoes.id", ondelete="CASCADE"), nullable=False
    )
    nome_arquivo: Mapped[str] = mapped_column(String(255), nullable=False)
    url_arquivo: Mapped[str | None] = mapped_column(Text)
    tipo_arquivo: Mapped[str | None] = mapped_column(String(80))
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7))
    enviado_por: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("usuarios.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "latitude IS NULL OR latitude BETWEEN -90 AND 90",
            name="ck_evidencias_latitude",
        ),
        CheckConstraint(
            "longitude IS NULL OR longitude BETWEEN -180 AND 180",
            name="ck_evidencias_longitude",
        ),
    )

    # Relationships
    missao: Mapped["Missao"] = relationship(back_populates="evidencias")
    enviador: Mapped["Usuario"] = relationship()


# ============================================================================
# MANUTENÇÕES E FINANCEIRO
# ============================================================================


class Manutencao(Base):
    __tablename__ = "manutencoes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    drone_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("drones.id", ondelete="CASCADE"), nullable=False
    )
    tipo: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text)
    data_manutencao: Mapped[date] = mapped_column(Date, nullable=False)
    proxima_manutencao: Mapped[date | None] = mapped_column(Date)
    horas_na_data: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "horas_na_data IS NULL OR horas_na_data >= 0",
            name="ck_manutencoes_horas_na_data",
        ),
        CheckConstraint(
            "proxima_manutencao IS NULL OR proxima_manutencao >= data_manutencao",
            name="ck_manutencoes_proxima_data",
        ),
    )

    # Relationships
    drone: Mapped["Drone"] = relationship(back_populates="manutencoes")


class FinanceiroMissao(Base):
    __tablename__ = "financeiro_missao"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    missao_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("missoes.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    custo_estimado: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=0
    )
    custo_realizado: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=0
    )
    valor_faturado: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=0
    )
    status_financeiro: Mapped[str] = mapped_column(String(30), nullable=False)
    observacoes: Mapped[str | None] = mapped_column(Text)
    fechado_por: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("usuarios.id")
    )
    fechado_em: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "custo_estimado >= 0", name="ck_financeiro_missao_custo_estimado"
        ),
        CheckConstraint(
            "custo_realizado >= 0", name="ck_financeiro_missao_custo_realizado"
        ),
        CheckConstraint(
            "valor_faturado >= 0", name="ck_financeiro_missao_valor_faturado"
        ),
        CheckConstraint(
            "status_financeiro IN ('PENDENTE','EM_FATURAMENTO','FATURADO','RECEBIDO','CANCELADO')",
            name="ck_financeiro_missao_status_financeiro",
        ),
    )

    # Relationships
    missao: Mapped["Missao"] = relationship(back_populates="financeiro")
    fechador: Mapped["Usuario | None"] = relationship()


# ============================================================================
# AUDITORIA E DOCUMENTOS
# ============================================================================


class Auditoria(Base):
    __tablename__ = "auditoria"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    entidade: Mapped[str] = mapped_column(String(120), nullable=False)
    entidade_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    acao: Mapped[str] = mapped_column(String(120), nullable=False)
    valor_anterior: Mapped[dict | None] = mapped_column(JSON)
    valor_novo: Mapped[dict | None] = mapped_column(JSON)
    usuario_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("usuarios.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    # Relationships
    usuario: Mapped["Usuario"] = relationship()


class DocumentoOficial(Base):
    __tablename__ = "documentos_oficiais"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    entidade: Mapped[str] = mapped_column(String(80), nullable=False)
    entidade_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tipo_documento: Mapped[str] = mapped_column(String(120), nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(255))
    nome_arquivo: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(120), nullable=False)
    s3_key: Mapped[str] = mapped_column(Text, nullable=False)
    bucket_s3: Mapped[str | None] = mapped_column(String(255))
    data_emissao: Mapped[date | None] = mapped_column(Date)
    data_validade: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="ATIVO")
    enviado_por: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("usuarios.id")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "entidade IN ('DRONE','MANUTENCAO','USUARIO','CLIENTE','PROPRIEDADE','INSUMO','MISSAO')",
            name="ck_documentos_oficiais_entidade",
        ),
        CheckConstraint(
            "status IN ('ATIVO','SUBSTITUIDO','VENCIDO','INATIVO')",
            name="ck_documentos_oficiais_status",
        ),
        CheckConstraint(
            "data_validade IS NULL OR data_emissao IS NULL OR data_validade >= data_emissao",
            name="ck_documentos_oficiais_validade",
        ),
    )

    # Relationships
    enviador: Mapped["Usuario | None"] = relationship()
