SPEC — AgroFlightOps
Sistema de Gestão de Operações de Pulverização com Drones

Versão: 1.0
Projeto: AgroFlightOps
Cliente: Vista Agrotech
Autor: Alberto Moreira

1. Objetivo do Sistema

Desenvolver um sistema web para gestão completa de operações de pulverização agrícola com drones, permitindo:

controle de ordens de serviço
planejamento de missões
gestão de drones
gestão de pilotos
execução e registro das operações
armazenamento de documentos oficiais
relatórios técnicos e financeiros

O sistema será implementado inicialmente como MVP, porém com arquitetura preparada para evolução futura.

2. Arquitetura de Alto Nível

Arquitetura baseada em serviços AWS.

Frontend

S3 Static Website

Tecnologia sugerida:

React
Vite
TypeScript
Backend

API REST

Tecnologia sugerida:

Python
FastAPI
Boto3

Hospedagem:

AWS Lambda
API Gateway
Banco de Dados

Engine:

Amazon RDS for MySQL
Version: 8.0

Database name:

agroflightops
Armazenamento de documentos

Amazon S3

Exemplos:

AgroFlightOps-dev-documents
AgroFlightOps-hml-documents
AgroFlightOps-prd-documents

Documentos armazenados:

registro ANAC de drones
licenças de pilotos
autorizações de voo
contratos
relatórios assinados
3. Perfis de Usuário

Perfis do sistema:

Administrador

Controle total da aplicação.

Piloto

Executa missões e registra resultados.

Técnico

Responsável por planejamento e validação de missão.

Financeiro

Consulta relatórios financeiros.

4. Workflow Operacional

Fluxo principal do sistema:

Ordem de Serviço criada
        ↓
Ordem aprovada
        ↓
Missão criada
        ↓
Piloto alocado
        ↓
Missão agendada
        ↓
Checklist preparado
        ↓
Missão aprovada
        ↓
Execução da missão
        ↓
Registro da operação
        ↓
Encerramento
        ↓
Relatórios técnicos e financeiros
5. Entidades Principais
usuarios

Campos:

id
nome
email
senha_hash
perfil
ativo
created_at
updated_at
drones

Campos:

id
identificacao
modelo
fabricante
capacidade_litros
status
horas_voadas
ultima_manutencao_em
created_at
updated_at
fazendas

Campos:

id
nome
proprietario
latitude
longitude
created_at
ordens_servico

Campos:

id
codigo
fazenda_id
descricao
status
data_abertura
data_aprovacao
missoes

Campos:

id
ordem_servico_id
drone_id
piloto_id
data_agendada
status
area_hectares
documentos_oficiais

Campos:

id
entidade
entidade_id
tipo_documento
content_type
s3_key
bucket_s3
data_validade
created_at
6. Geolocalização

Entidades que podem conter localização:

fazendas
áreas de missão

Formato:

latitude DECIMAL(10,7)
longitude DECIMAL(10,7)

Mapas podem ser exibidos usando:

Google Maps iframe

ou

Leaflet
7. Armazenamento de Documentos

Documentos são armazenados no S3.

No banco são registrados:

content_type
s3_key
bucket_s3

Upload e download serão feitos via API.

8. Regras de Banco de Dados (DATABASE_RULES.md)

Estas regras devem ser seguidas pelo gerador de código.

Engine
MySQL 8.0
Chave Primária

Todas as tabelas devem usar:

BIGINT UNSIGNED AUTO_INCREMENT

Exemplo:

id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
Chaves estrangeiras

Foreign keys devem usar:

BIGINT UNSIGNED
Timestamps padrão

Todas as tabelas devem ter:

created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
Migrations

Ferramenta:

Flyway

Formato:

V1__schema.sql
V2__seed.sql
Índices obrigatórios
INDEX idx_ordem_servico_codigo (codigo)
INDEX idx_missao_data (data_agendada)
INDEX idx_documentos_entidade (entidade, entidade_id)
9. Segurança

Autenticação:

JWT

Senhas:

bcrypt
10. Convenções de Código

API REST.

Exemplos:

GET /usuarios
POST /usuarios
GET /drones
POST /missoes
11. Estrutura de Projeto

Backend:

app/
 ├── api
 ├── services
 ├── repositories
 ├── models
 └── schemas
12. Integrações Futuras

O sistema deve permitir integração futura com:

telemetria de drones
APIs meteorológicas
planejamento automático de voo
sistemas agrícolas externos
plataformas de drones
Conclusão

Esta especificação define o MVP completo do AgroFlightOps, preparado para evolução futura e com diretrizes claras para geração de código assistida pelo Kiro.