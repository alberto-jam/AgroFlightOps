-- ============================================================================
-- V2: Add relatorios_medicao and relatorio_medicao_missoes tables
-- Feature: Gestão de Relatórios de Medição
-- ============================================================================

CREATE TABLE IF NOT EXISTS relatorios_medicao (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cliente_id BIGINT NOT NULL,
    s3_key VARCHAR(500) NOT NULL,
    data_inicial DATE NOT NULL,
    data_final DATE NOT NULL,
    total_area NUMERIC(14, 2) NOT NULL,
    qtd_missoes INT NOT NULL,
    gerado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    gerado_por BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ATIVO',
    enviado_em DATETIME NULL,
    enviado_para TEXT NULL,
    CONSTRAINT fk_relatorios_medicao_cliente FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    CONSTRAINT fk_relatorios_medicao_gerador FOREIGN KEY (gerado_por) REFERENCES usuarios(id),
    CONSTRAINT ck_relatorios_medicao_status CHECK (status IN ('ATIVO', 'EXCLUIDO')),
    CONSTRAINT ck_relatorios_medicao_total_area CHECK (total_area >= 0),
    CONSTRAINT ck_relatorios_medicao_qtd_missoes CHECK (qtd_missoes > 0)
);

CREATE TABLE IF NOT EXISTS relatorio_medicao_missoes (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    relatorio_id BIGINT NOT NULL,
    missao_id BIGINT NOT NULL,
    CONSTRAINT fk_relatorio_missoes_relatorio FOREIGN KEY (relatorio_id)
        REFERENCES relatorios_medicao(id) ON DELETE CASCADE,
    CONSTRAINT fk_relatorio_missoes_missao FOREIGN KEY (missao_id)
        REFERENCES missoes(id),
    CONSTRAINT uq_relatorio_medicao_missoes UNIQUE (relatorio_id, missao_id)
);

-- Add column medicao_enviada_em to missoes if not exists
-- (This column may already exist from a previous migration)
SET @col_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'missoes'
      AND COLUMN_NAME = 'medicao_enviada_em'
);

SET @sql = IF(@col_exists = 0,
    'ALTER TABLE missoes ADD COLUMN medicao_enviada_em DATETIME NULL',
    'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
