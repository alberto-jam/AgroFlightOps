
# DATABASE_RULES.md

## Engine

MySQL 8.0 (Amazon RDS MySQL)

## Primary Key Pattern

id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY

## Foreign Key Pattern

<entity>_id BIGINT UNSIGNED

## Timestamp Pattern

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

## Migration Tool

Flyway

## Migration Naming

V1__schema.sql
V2__seed.sql

## Index Guidelines

idx_ordem_servico_codigo
idx_missao_data
idx_documentos_entidade

## Geolocation Fields

latitude DECIMAL(10,7)
longitude DECIMAL(10,7)

## Document Storage Metadata

content_type
s3_key
bucket_s3
