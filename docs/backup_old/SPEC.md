
# AgroFlightOps — SPEC.md

Projeto: AgroFlightOps
Cliente: Vista Agrotech
Autor: Alberto Moreira

## Objetivo

Sistema web para gestão de operações de pulverização agrícola com drones.

Funcionalidades principais:

- gestão de ordens de serviço
- planejamento de missões
- alocação de pilotos
- controle de drones
- execução e registro de operações
- armazenamento de documentos oficiais
- relatórios técnicos e financeiros

## Arquitetura

Frontend:
- React
- Vite
- TypeScript
- hospedagem em S3

Backend:
- Python
- FastAPI
- AWS Lambda
- API Gateway

Banco de dados:
- Amazon RDS MySQL 8.0
- database name: agroflightops

Documentos:
- Amazon S3

## Perfis de Usuário

Administrador
Piloto
Técnico
Financeiro

## Workflow Operacional

Ordem de Serviço criada
→ Aprovação
→ Missão criada
→ Piloto alocado
→ Missão agendada
→ Checklist preparado
→ Missão aprovada
→ Execução
→ Registro da operação
→ Encerramento
→ Relatórios

## Entidades

usuarios
drones
fazendas
ordens_servico
missoes
documentos_oficiais

## Geolocalização

latitude DECIMAL(10,7)
longitude DECIMAL(10,7)

Mapas podem utilizar Google Maps ou Leaflet.

## Documentos

Documentos oficiais armazenados em S3.

Campos registrados no banco:

content_type
s3_key
bucket_s3
data_validade
