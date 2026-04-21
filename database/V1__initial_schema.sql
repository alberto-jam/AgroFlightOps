-- ============================================================================
-- Flyway Migration V1: Initial Schema
-- Sistema de Gestão de Serviços de Pulverização por Drones "AgroFlightOps"
-- Compatível com Amazon RDS for MySQL 8.0 / Aurora MySQL
--
-- Baseado em: database/AgroFlightOps_RDS_MySQL_ddl.sql
-- Convenção Flyway: V{versao}__{descricao}.sql
--
-- NOTA: Este script usa CREATE TABLE IF NOT EXISTS para idempotência.
--       Adequado para primeira execução do Flyway em bancos novos ou existentes.
-- ============================================================================

-- ============================================================================
-- TABELAS BASE
-- ============================================================================

CREATE TABLE IF NOT EXISTS perfis (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(80) NOT NULL UNIQUE,
    descricao TEXT,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS usuarios (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    perfil_id BIGINT UNSIGNED NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuarios_perfil_id FOREIGN KEY (perfil_id) REFERENCES perfis(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS clientes (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    cpf_cnpj VARCHAR(18),
    telefone VARCHAR(30),
    email VARCHAR(255),
    endereco VARCHAR(255),
    numero VARCHAR(20),
    complemento VARCHAR(120),
    bairro VARCHAR(120),
    municipio VARCHAR(120),
    estado CHAR(2),
    cep VARCHAR(12),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    referencia_local VARCHAR(255),
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT ck_clientes_latitude CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90),
    CONSTRAINT ck_clientes_longitude CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS propriedades (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    cliente_id BIGINT UNSIGNED NOT NULL,
    nome VARCHAR(200) NOT NULL,
    endereco VARCHAR(255),
    numero VARCHAR(20),
    complemento VARCHAR(120),
    bairro VARCHAR(120),
    municipio VARCHAR(120) NOT NULL,
    estado CHAR(2) NOT NULL,
    cep VARCHAR(12),
    localizacao_descritiva TEXT,
    referencia_local VARCHAR(255),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    area_total DECIMAL(14,2) NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT ck_propriedades_area_total CHECK (area_total >= 0),
    CONSTRAINT ck_propriedades_latitude CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90),
    CONSTRAINT ck_propriedades_longitude CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180),
    CONSTRAINT fk_propriedades_cliente_id FOREIGN KEY (cliente_id) REFERENCES clientes(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS culturas (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL UNIQUE,
    descricao TEXT,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS talhoes (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    propriedade_id BIGINT UNSIGNED NOT NULL,
    nome VARCHAR(150) NOT NULL,
    area_hectares DECIMAL(14,2) NOT NULL,
    cultura_id BIGINT UNSIGNED NOT NULL,
    observacoes TEXT,
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    ponto_referencia VARCHAR(255),
    geojson JSON,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_talhoes_propriedade_nome UNIQUE (propriedade_id, nome),
    CONSTRAINT ck_talhoes_area_hectares CHECK (area_hectares >= 0),
    CONSTRAINT ck_talhoes_latitude CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90),
    CONSTRAINT ck_talhoes_longitude CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180),
    CONSTRAINT fk_talhoes_propriedade_id FOREIGN KEY (propriedade_id) REFERENCES propriedades(id),
    CONSTRAINT fk_talhoes_cultura_id FOREIGN KEY (cultura_id) REFERENCES culturas(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS drones (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    identificacao VARCHAR(120) NOT NULL UNIQUE,
    modelo VARCHAR(120) NOT NULL,
    fabricante VARCHAR(120),
    capacidade_litros DECIMAL(10,2) NOT NULL,
    status VARCHAR(30) NOT NULL,
    horas_voadas DECIMAL(12,2) NOT NULL DEFAULT 0,
    ultima_manutencao_em DATE,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT ck_drones_capacidade_litros CHECK (capacidade_litros >= 0),
    CONSTRAINT ck_drones_horas_voadas CHECK (horas_voadas >= 0),
    CONSTRAINT ck_drones_status CHECK (status IN ('DISPONIVEL','EM_USO','EM_MANUTENCAO','BLOQUEADO','INATIVO'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS baterias (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    identificacao VARCHAR(120) NOT NULL UNIQUE,
    drone_id BIGINT UNSIGNED,
    ciclos INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(30) NOT NULL,
    observacoes TEXT,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT ck_baterias_ciclos CHECK (ciclos >= 0),
    CONSTRAINT ck_baterias_status CHECK (status IN ('DISPONIVEL','EM_USO','CARREGANDO','REPROVADA','DESCARTADA')),
    CONSTRAINT fk_baterias_drone_id FOREIGN KEY (drone_id) REFERENCES drones(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS insumos (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    fabricante VARCHAR(120),
    unidade_medida VARCHAR(30) NOT NULL,
    saldo_atual DECIMAL(14,3) NOT NULL DEFAULT 0,
    lote VARCHAR(100),
    validade DATE,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT ck_insumos_saldo_atual CHECK (saldo_atual >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tipos_ocorrencia (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL UNIQUE,
    descricao TEXT,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS itens_checklist_padrao (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome_item VARCHAR(200) NOT NULL,
    descricao TEXT,
    obrigatorio BOOLEAN NOT NULL DEFAULT TRUE,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    ordem_exibicao INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_itens_checklist_padrao_nome_item UNIQUE (nome_item),
    CONSTRAINT ck_itens_checklist_padrao_ordem_exibicao CHECK (ordem_exibicao >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ordens_servico (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    cliente_id BIGINT UNSIGNED NOT NULL,
    propriedade_id BIGINT UNSIGNED NOT NULL,
    talhao_id BIGINT UNSIGNED NOT NULL,
    cultura_id BIGINT UNSIGNED NOT NULL,
    tipo_aplicacao VARCHAR(120) NOT NULL,
    prioridade VARCHAR(30) NOT NULL,
    descricao TEXT,
    data_prevista DATE NOT NULL,
    status VARCHAR(30) NOT NULL,
    motivo_rejeicao TEXT,
    motivo_cancelamento TEXT,
    criado_por BIGINT UNSIGNED NOT NULL,
    aprovado_por BIGINT UNSIGNED,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT ck_ordens_servico_status CHECK (status IN ('RASCUNHO','EM_ANALISE','APROVADA','REJEITADA','CANCELADA')),
    CONSTRAINT ck_ordens_servico_prioridade CHECK (prioridade IN ('BAIXA','MEDIA','ALTA','CRITICA')),
    CONSTRAINT ck_ordens_servico_motivo_rejeicao CHECK (status <> 'REJEITADA' OR motivo_rejeicao IS NOT NULL),
    CONSTRAINT ck_ordens_servico_motivo_cancelamento CHECK (status <> 'CANCELADA' OR motivo_cancelamento IS NOT NULL),
    CONSTRAINT fk_ordens_servico_cliente_id FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    CONSTRAINT fk_ordens_servico_propriedade_id FOREIGN KEY (propriedade_id) REFERENCES propriedades(id),
    CONSTRAINT fk_ordens_servico_talhao_id FOREIGN KEY (talhao_id) REFERENCES talhoes(id),
    CONSTRAINT fk_ordens_servico_cultura_id FOREIGN KEY (cultura_id) REFERENCES culturas(id),
    CONSTRAINT fk_ordens_servico_criado_por FOREIGN KEY (criado_por) REFERENCES usuarios(id),
    CONSTRAINT fk_ordens_servico_aprovado_por FOREIGN KEY (aprovado_por) REFERENCES usuarios(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS historico_status_os (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    ordem_servico_id BIGINT UNSIGNED NOT NULL,
    status_anterior VARCHAR(30),
    status_novo VARCHAR(30) NOT NULL,
    motivo TEXT,
    alterado_por BIGINT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_historico_status_os_status_anterior CHECK (status_anterior IS NULL OR status_anterior IN ('RASCUNHO','EM_ANALISE','APROVADA','REJEITADA','CANCELADA')),
    CONSTRAINT ck_historico_status_os_status_novo CHECK (status_novo IN ('RASCUNHO','EM_ANALISE','APROVADA','REJEITADA','CANCELADA')),
    CONSTRAINT fk_historico_status_os_ordem_servico_id FOREIGN KEY (ordem_servico_id) REFERENCES ordens_servico(id) ON DELETE CASCADE,
    CONSTRAINT fk_historico_status_os_alterado_por FOREIGN KEY (alterado_por) REFERENCES usuarios(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS missoes (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    ordem_servico_id BIGINT UNSIGNED NOT NULL,
    piloto_id BIGINT UNSIGNED NOT NULL,
    tecnico_id BIGINT UNSIGNED,
    drone_id BIGINT UNSIGNED NOT NULL,
    data_agendada DATE NOT NULL,
    hora_agendada TIME NOT NULL,
    area_prevista DECIMAL(14,2) NOT NULL,
    area_realizada DECIMAL(14,2),
    volume_previsto DECIMAL(14,3) NOT NULL,
    volume_realizado DECIMAL(14,3),
    janela_operacional VARCHAR(255),
    restricoes TEXT,
    observacoes_planejamento TEXT,
    observacoes_execucao TEXT,
    status VARCHAR(40) NOT NULL,
    latitude_operacao DECIMAL(10,7),
    longitude_operacao DECIMAL(10,7),
    endereco_operacao VARCHAR(255),
    referencia_operacao VARCHAR(255),
    iniciado_em TIMESTAMP,
    finalizado_em TIMESTAMP,
    encerrado_tecnicamente_em TIMESTAMP,
    encerrado_financeiramente_em TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT ck_missoes_area_prevista CHECK (area_prevista >= 0),
    CONSTRAINT ck_missoes_area_realizada CHECK (area_realizada IS NULL OR area_realizada >= 0),
    CONSTRAINT ck_missoes_volume_previsto CHECK (volume_previsto >= 0),
    CONSTRAINT ck_missoes_volume_realizado CHECK (volume_realizado IS NULL OR volume_realizado >= 0),
    CONSTRAINT ck_missoes_status CHECK (status IN ('RASCUNHO','PLANEJADA','AGENDADA','EM_CHECKLIST','LIBERADA','EM_EXECUCAO','PAUSADA','CONCLUIDA','CANCELADA','ENCERRADA_TECNICAMENTE','ENCERRADA_FINANCEIRAMENTE')),
    CONSTRAINT ck_missoes_latitude_operacao CHECK (latitude_operacao IS NULL OR latitude_operacao BETWEEN -90 AND 90),
    CONSTRAINT ck_missoes_longitude_operacao CHECK (longitude_operacao IS NULL OR longitude_operacao BETWEEN -180 AND 180),
    CONSTRAINT ck_missoes_timestamps CHECK (
                finalizado_em IS NULL OR iniciado_em IS NULL OR finalizado_em >= iniciado_em
            ),
    CONSTRAINT fk_missoes_ordem_servico_id FOREIGN KEY (ordem_servico_id) REFERENCES ordens_servico(id),
    CONSTRAINT fk_missoes_piloto_id FOREIGN KEY (piloto_id) REFERENCES usuarios(id),
    CONSTRAINT fk_missoes_drone_id FOREIGN KEY (drone_id) REFERENCES drones(id),
    CONSTRAINT fk_missoes_tecnico_id FOREIGN KEY (tecnico_id) REFERENCES usuarios(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS historico_status_missao (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    missao_id BIGINT UNSIGNED NOT NULL,
    status_anterior VARCHAR(40),
    status_novo VARCHAR(40) NOT NULL,
    motivo TEXT,
    alterado_por BIGINT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_historico_status_missao_status_anterior CHECK (status_anterior IS NULL OR status_anterior IN ('RASCUNHO','PLANEJADA','AGENDADA','EM_CHECKLIST','LIBERADA','EM_EXECUCAO','PAUSADA','CONCLUIDA','CANCELADA','ENCERRADA_TECNICAMENTE','ENCERRADA_FINANCEIRAMENTE')),
    CONSTRAINT ck_historico_status_missao_status_novo CHECK (status_novo IN ('RASCUNHO','PLANEJADA','AGENDADA','EM_CHECKLIST','LIBERADA','EM_EXECUCAO','PAUSADA','CONCLUIDA','CANCELADA','ENCERRADA_TECNICAMENTE','ENCERRADA_FINANCEIRAMENTE')),
    CONSTRAINT fk_historico_status_missao_missao_id FOREIGN KEY (missao_id) REFERENCES missoes(id) ON DELETE CASCADE,
    CONSTRAINT fk_historico_status_missao_alterado_por FOREIGN KEY (alterado_por) REFERENCES usuarios(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS missao_baterias (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    missao_id BIGINT UNSIGNED NOT NULL,
    bateria_id BIGINT UNSIGNED NOT NULL,
    ordem_uso INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_missao_baterias UNIQUE (missao_id, bateria_id),
    CONSTRAINT uq_missao_baterias_ordem UNIQUE (missao_id, ordem_uso),
    CONSTRAINT ck_missao_baterias_ordem_uso CHECK (ordem_uso > 0),
    CONSTRAINT fk_missao_baterias_missao_id FOREIGN KEY (missao_id) REFERENCES missoes(id) ON DELETE CASCADE,
    CONSTRAINT fk_missao_baterias_bateria_id FOREIGN KEY (bateria_id) REFERENCES baterias(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS reservas_insumo (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    missao_id BIGINT UNSIGNED NOT NULL,
    insumo_id BIGINT UNSIGNED NOT NULL,
    quantidade_prevista DECIMAL(14,3) NOT NULL,
    unidade_medida VARCHAR(30) NOT NULL,
    justificativa_excesso TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_reservas_insumo_quantidade_prevista CHECK (quantidade_prevista >= 0),
    CONSTRAINT fk_reservas_insumo_missao_id FOREIGN KEY (missao_id) REFERENCES missoes(id) ON DELETE CASCADE,
    CONSTRAINT fk_reservas_insumo_insumo_id FOREIGN KEY (insumo_id) REFERENCES insumos(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS consumos_insumo_missao (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    missao_id BIGINT UNSIGNED NOT NULL,
    insumo_id BIGINT UNSIGNED NOT NULL,
    quantidade_realizada DECIMAL(14,3) NOT NULL,
    unidade_medida VARCHAR(30) NOT NULL,
    observacoes TEXT,
    justificativa_excesso TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_consumos_insumo_missao_quantidade_realizada CHECK (quantidade_realizada >= 0),
    CONSTRAINT fk_consumos_insumo_missao_missao_id FOREIGN KEY (missao_id) REFERENCES missoes(id) ON DELETE CASCADE,
    CONSTRAINT fk_consumos_insumo_missao_insumo_id FOREIGN KEY (insumo_id) REFERENCES insumos(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS checklists_missao (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    missao_id BIGINT UNSIGNED NOT NULL UNIQUE,
    status_geral VARCHAR(30) NOT NULL,
    preenchido_por BIGINT UNSIGNED NOT NULL,
    revisado_por BIGINT UNSIGNED,
    preenchido_em TIMESTAMP NOT NULL,
    revisado_em TIMESTAMP,
    observacoes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT ck_checklists_missao_status_geral CHECK (status_geral IN ('PENDENTE','EM_PREENCHIMENTO','CONCLUIDO','REPROVADO','APROVADO')),
    CONSTRAINT ck_checklists_missao_revisado_em CHECK (revisado_em IS NULL OR revisado_em >= preenchido_em),
    CONSTRAINT fk_checklists_missao_missao_id FOREIGN KEY (missao_id) REFERENCES missoes(id) ON DELETE CASCADE,
    CONSTRAINT fk_checklists_missao_preenchido_por FOREIGN KEY (preenchido_por) REFERENCES usuarios(id),
    CONSTRAINT fk_checklists_missao_revisado_por FOREIGN KEY (revisado_por) REFERENCES usuarios(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS itens_checklist_missao (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    checklist_id BIGINT UNSIGNED NOT NULL,
    nome_item VARCHAR(200) NOT NULL,
    obrigatorio BOOLEAN NOT NULL DEFAULT TRUE,
    status_item VARCHAR(20) NOT NULL,
    observacao TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT ck_itens_checklist_missao_status_item CHECK (status_item IN ('PENDENTE','APROVADO','REPROVADO','NAO_APLICAVEL')),
    CONSTRAINT ck_itens_checklist_missao_observacao CHECK (status_item <> 'REPROVADO' OR observacao IS NOT NULL),
    CONSTRAINT fk_itens_checklist_missao_checklist_id FOREIGN KEY (checklist_id) REFERENCES checklists_missao(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ocorrencias (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    missao_id BIGINT UNSIGNED NOT NULL,
    tipo_ocorrencia_id BIGINT UNSIGNED NOT NULL,
    descricao TEXT NOT NULL,
    severidade VARCHAR(20) NOT NULL,
    registrada_por BIGINT UNSIGNED NOT NULL,
    registrada_em TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT ck_ocorrencias_severidade CHECK (severidade IN ('BAIXA','MEDIA','ALTA','CRITICA')),
    CONSTRAINT fk_ocorrencias_missao_id FOREIGN KEY (missao_id) REFERENCES missoes(id) ON DELETE CASCADE,
    CONSTRAINT fk_ocorrencias_tipo_ocorrencia_id FOREIGN KEY (tipo_ocorrencia_id) REFERENCES tipos_ocorrencia(id),
    CONSTRAINT fk_ocorrencias_registrada_por FOREIGN KEY (registrada_por) REFERENCES usuarios(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS evidencias (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    missao_id BIGINT UNSIGNED NOT NULL,
    nome_arquivo VARCHAR(255) NOT NULL,
    url_arquivo TEXT,
    tipo_arquivo VARCHAR(80),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    enviado_por BIGINT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_evidencias_latitude CHECK (latitude IS NULL OR latitude BETWEEN -90 AND 90),
    CONSTRAINT ck_evidencias_longitude CHECK (longitude IS NULL OR longitude BETWEEN -180 AND 180),
    CONSTRAINT fk_evidencias_missao_id FOREIGN KEY (missao_id) REFERENCES missoes(id) ON DELETE CASCADE,
    CONSTRAINT fk_evidencias_enviado_por FOREIGN KEY (enviado_por) REFERENCES usuarios(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS manutencoes (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    drone_id BIGINT UNSIGNED NOT NULL,
    tipo VARCHAR(100) NOT NULL,
    descricao TEXT,
    data_manutencao DATE NOT NULL,
    proxima_manutencao DATE,
    horas_na_data DECIMAL(12,2),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT ck_manutencoes_horas_na_data CHECK (horas_na_data IS NULL OR horas_na_data >= 0),
    CONSTRAINT ck_manutencoes_proxima_data CHECK (proxima_manutencao IS NULL OR proxima_manutencao >= data_manutencao),
    CONSTRAINT fk_manutencoes_drone_id FOREIGN KEY (drone_id) REFERENCES drones(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS financeiro_missao (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    missao_id BIGINT UNSIGNED NOT NULL UNIQUE,
    custo_estimado DECIMAL(14,2) NOT NULL DEFAULT 0,
    custo_realizado DECIMAL(14,2) NOT NULL DEFAULT 0,
    valor_faturado DECIMAL(14,2) NOT NULL DEFAULT 0,
    status_financeiro VARCHAR(30) NOT NULL,
    observacoes TEXT,
    fechado_por BIGINT UNSIGNED,
    fechado_em TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT ck_financeiro_missao_custo_estimado CHECK (custo_estimado >= 0),
    CONSTRAINT ck_financeiro_missao_custo_realizado CHECK (custo_realizado >= 0),
    CONSTRAINT ck_financeiro_missao_valor_faturado CHECK (valor_faturado >= 0),
    CONSTRAINT ck_financeiro_missao_status_financeiro CHECK (status_financeiro IN ('PENDENTE','EM_FATURAMENTO','FATURADO','RECEBIDO','CANCELADO')),
    CONSTRAINT fk_financeiro_missao_missao_id FOREIGN KEY (missao_id) REFERENCES missoes(id) ON DELETE CASCADE,
    CONSTRAINT fk_financeiro_missao_fechado_por FOREIGN KEY (fechado_por) REFERENCES usuarios(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS auditoria (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    entidade VARCHAR(120) NOT NULL,
    entidade_id BIGINT UNSIGNED NOT NULL,
    acao VARCHAR(120) NOT NULL,
    valor_anterior JSON,
    valor_novo JSON,
    usuario_id BIGINT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_auditoria_usuario_id FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- DOCUMENTOS OFICIAIS / FÍSICOS
-- Modelagem centralizada para suportar múltiplos documentos por entidade.
-- Evita espalhar content_type/s3_key em várias tabelas e permite evolução.
-- ============================================================================

CREATE TABLE IF NOT EXISTS documentos_oficiais (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    entidade VARCHAR(80) NOT NULL,
    entidade_id BIGINT UNSIGNED NOT NULL,
    tipo_documento VARCHAR(120) NOT NULL,
    descricao VARCHAR(255),
    nome_arquivo VARCHAR(255) NOT NULL,
    content_type VARCHAR(120) NOT NULL,
    s3_key TEXT NOT NULL,
    bucket_s3 VARCHAR(255),
    data_emissao DATE,
    data_validade DATE,
    status VARCHAR(30) NOT NULL DEFAULT 'ATIVO',
    enviado_por BIGINT UNSIGNED,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT ck_documentos_oficiais_entidade CHECK (entidade IN ('DRONE','MANUTENCAO','USUARIO','CLIENTE','PROPRIEDADE','INSUMO','MISSAO')),
    CONSTRAINT ck_documentos_oficiais_status CHECK (status IN ('ATIVO','SUBSTITUIDO','VENCIDO','INATIVO')),
    CONSTRAINT ck_documentos_oficiais_validade CHECK (data_validade IS NULL OR data_emissao IS NULL OR data_validade >= data_emissao),
    CONSTRAINT fk_documentos_oficiais_enviado_por FOREIGN KEY (enviado_por) REFERENCES usuarios(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- ÍNDICES
-- Nota: MySQL 8.0 não suporta CREATE INDEX IF NOT EXISTS nativamente.
-- Como esta é a migração V1 do Flyway, os índices serão criados apenas na
-- primeira execução. O Flyway garante que este script não será re-executado
-- via tabela flyway_schema_history.
-- Se o banco já possuir os índices (baseline), use `flyway baseline` antes
-- de executar `flyway migrate`.
-- ============================================================================

CREATE INDEX idx_usuarios_perfil_id ON usuarios(perfil_id);
CREATE INDEX idx_usuarios_ativo ON usuarios(ativo);

CREATE INDEX idx_clientes_nome ON clientes(nome);
CREATE INDEX idx_clientes_cpf_cnpj ON clientes(cpf_cnpj);

CREATE INDEX idx_propriedades_cliente_id ON propriedades(cliente_id);
CREATE INDEX idx_propriedades_nome ON propriedades(nome);
CREATE INDEX idx_propriedades_municipio_estado ON propriedades(municipio, estado);

CREATE INDEX idx_talhoes_propriedade_id ON talhoes(propriedade_id);
CREATE INDEX idx_talhoes_cultura_id ON talhoes(cultura_id);
CREATE INDEX idx_talhoes_nome ON talhoes(nome);

CREATE INDEX idx_drones_status ON drones(status);
CREATE INDEX idx_baterias_drone_id ON baterias(drone_id);
CREATE INDEX idx_baterias_status ON baterias(status);
CREATE INDEX idx_insumos_nome ON insumos(nome);
CREATE INDEX idx_insumos_lote ON insumos(lote);

CREATE INDEX idx_ordens_servico_cliente_id ON ordens_servico(cliente_id);
CREATE INDEX idx_ordens_servico_propriedade_id ON ordens_servico(propriedade_id);
CREATE INDEX idx_ordens_servico_talhao_id ON ordens_servico(talhao_id);
CREATE INDEX idx_ordens_servico_cultura_id ON ordens_servico(cultura_id);
CREATE INDEX idx_ordens_servico_status ON ordens_servico(status);
CREATE INDEX idx_ordens_servico_data_prevista ON ordens_servico(data_prevista);
CREATE INDEX idx_ordens_servico_criado_por ON ordens_servico(criado_por);

CREATE INDEX idx_historico_status_os_ordem_servico_id ON historico_status_os(ordem_servico_id);
CREATE INDEX idx_historico_status_os_created_at ON historico_status_os(created_at);

CREATE INDEX idx_missoes_ordem_servico_id ON missoes(ordem_servico_id);
CREATE INDEX idx_missoes_piloto_id ON missoes(piloto_id);
CREATE INDEX idx_missoes_tecnico_id ON missoes(tecnico_id);
CREATE INDEX idx_missoes_drone_id ON missoes(drone_id);
CREATE INDEX idx_missoes_status ON missoes(status);
CREATE INDEX idx_missoes_data_agendada ON missoes(data_agendada);
CREATE INDEX idx_missoes_data_hora ON missoes(data_agendada, hora_agendada);

CREATE INDEX idx_historico_status_missao_missao_id ON historico_status_missao(missao_id);
CREATE INDEX idx_historico_status_missao_created_at ON historico_status_missao(created_at);

CREATE INDEX idx_missao_baterias_missao_id ON missao_baterias(missao_id);
CREATE INDEX idx_missao_baterias_bateria_id ON missao_baterias(bateria_id);

CREATE INDEX idx_reservas_insumo_missao_id ON reservas_insumo(missao_id);
CREATE INDEX idx_reservas_insumo_insumo_id ON reservas_insumo(insumo_id);

CREATE INDEX idx_consumos_insumo_missao_missao_id ON consumos_insumo_missao(missao_id);
CREATE INDEX idx_consumos_insumo_missao_insumo_id ON consumos_insumo_missao(insumo_id);

CREATE INDEX idx_checklists_missao_missao_id ON checklists_missao(missao_id);
CREATE INDEX idx_itens_checklist_missao_checklist_id ON itens_checklist_missao(checklist_id);

CREATE INDEX idx_ocorrencias_missao_id ON ocorrencias(missao_id);
CREATE INDEX idx_ocorrencias_tipo_ocorrencia_id ON ocorrencias(tipo_ocorrencia_id);
CREATE INDEX idx_ocorrencias_registrada_em ON ocorrencias(registrada_em);

CREATE INDEX idx_evidencias_missao_id ON evidencias(missao_id);
CREATE INDEX idx_evidencias_enviado_por ON evidencias(enviado_por);

CREATE INDEX idx_manutencoes_drone_id ON manutencoes(drone_id);
CREATE INDEX idx_manutencoes_data_manutencao ON manutencoes(data_manutencao);

CREATE INDEX idx_financeiro_missao_missao_id ON financeiro_missao(missao_id);
CREATE INDEX idx_financeiro_missao_status_financeiro ON financeiro_missao(status_financeiro);

CREATE INDEX idx_auditoria_entidade_entidade_id ON auditoria(entidade, entidade_id);
CREATE INDEX idx_auditoria_usuario_id ON auditoria(usuario_id);
CREATE INDEX idx_auditoria_created_at ON auditoria(created_at);

CREATE INDEX idx_documentos_oficiais_entidade_entidade_id ON documentos_oficiais(entidade, entidade_id);
CREATE INDEX idx_documentos_oficiais_tipo_documento ON documentos_oficiais(tipo_documento);
CREATE INDEX idx_documentos_oficiais_status ON documentos_oficiais(status);
CREATE INDEX idx_documentos_oficiais_data_validade ON documentos_oficiais(data_validade);

-- ============================================================================
-- DADOS INICIAIS (SEED MÍNIMA)
-- Usa INSERT IGNORE para idempotência — não falha se os registros já existirem.
-- ============================================================================

INSERT IGNORE INTO perfis (nome, descricao) VALUES
('ADMINISTRADOR', 'Acesso total ao sistema'),
('COORDENADOR_OPERACIONAL', 'Gestão operacional de OS e missões'),
('PILOTO', 'Execução de missões'),
('TECNICO', 'Validação e encerramento técnico'),
('FINANCEIRO', 'Encerramento financeiro e faturamento');