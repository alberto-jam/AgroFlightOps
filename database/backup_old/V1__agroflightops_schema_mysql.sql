
-- AgroFlightOps MySQL Schema
-- Engine: MySQL 8.0 (compatible with Amazon RDS MySQL)

-- Flyway migration

CREATE TABLE usuarios (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    perfil VARCHAR(50) NOT NULL,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE drones (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    identificacao VARCHAR(100) NOT NULL,
    modelo VARCHAR(100),
    fabricante VARCHAR(100),
    capacidade_litros DECIMAL(10,2),
    status VARCHAR(30),
    horas_voadas DECIMAL(10,2) DEFAULT 0,
    ultima_manutencao_em DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE fazendas (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    proprietario VARCHAR(150),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ordens_servico (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(30) UNIQUE,
    fazenda_id BIGINT UNSIGNED,
    descricao TEXT,
    status VARCHAR(50),
    data_abertura DATETIME,
    data_aprovacao DATETIME,
    FOREIGN KEY (fazenda_id) REFERENCES fazendas(id)
);

CREATE TABLE missoes (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    ordem_servico_id BIGINT UNSIGNED,
    drone_id BIGINT UNSIGNED,
    piloto_id BIGINT UNSIGNED,
    data_agendada DATETIME,
    status VARCHAR(50),
    area_hectares DECIMAL(10,2),
    FOREIGN KEY (ordem_servico_id) REFERENCES ordens_servico(id),
    FOREIGN KEY (drone_id) REFERENCES drones(id),
    FOREIGN KEY (piloto_id) REFERENCES usuarios(id)
);

CREATE TABLE documentos_oficiais (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    entidade VARCHAR(100),
    entidade_id BIGINT UNSIGNED,
    tipo_documento VARCHAR(100),
    content_type VARCHAR(100),
    s3_key VARCHAR(500),
    bucket_s3 VARCHAR(200),
    data_validade DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
