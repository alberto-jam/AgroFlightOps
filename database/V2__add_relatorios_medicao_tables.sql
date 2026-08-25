-- ============================================================================
-- V2: Add relatorios_medicao and relatorio_medicao_missoes tables
-- Feature: Gestão de Relatórios de Medição
-- ============================================================================

CREATE TABLE IF NOT EXISTS relatorios_medicao (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    cliente_id BIGINT UNSIGNED NOT NULL,
    s3_key VARCHAR(500) NOT NULL,
    data_inicial DATE NOT NULL,
    data_final DATE NOT NULL,
    total_area NUMERIC(14, 2) NOT NULL,
    qtd_missoes INT NOT NULL,
    gerado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    gerado_por BIGINT UNSIGNED NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ATIVO',
    enviado_em DATETIME NULL,
    enviado_para TEXT NULL,
    CONSTRAINT fk_relatorios_medicao_cliente FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    CONSTRAINT fk_relatorios_medicao_gerador FOREIGN KEY (gerado_por) REFERENCES usuarios(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS relatorio_medicao_missoes (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    relatorio_id BIGINT UNSIGNED NOT NULL,
    missao_id BIGINT UNSIGNED NOT NULL,
    CONSTRAINT fk_relatorio_missoes_relatorio FOREIGN KEY (relatorio_id)
        REFERENCES relatorios_medicao(id) ON DELETE CASCADE,
    CONSTRAINT fk_relatorio_missoes_missao FOREIGN KEY (missao_id)
        REFERENCES missoes(id),
    CONSTRAINT uq_relatorio_medicao_missoes UNIQUE (relatorio_id, missao_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
