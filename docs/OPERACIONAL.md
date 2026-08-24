# AgroFlightOps — Documentação Operacional

> Versão: 1.0 · Última atualização: julho/2026 · Autor: Alberto Moreira

---

## Sumário

1. [Visão Geral do Sistema](#1-visão-geral-do-sistema)
2. [Arquitetura de Infraestrutura](#2-arquitetura-de-infraestrutura)
3. [Ambientes](#3-ambientes)
4. [Autenticação e Perfis de Acesso](#4-autenticação-e-perfis-de-acesso)
5. [Módulos e Endpoints da API](#5-módulos-e-endpoints-da-api)
6. [Fluxo Operacional Principal](#6-fluxo-operacional-principal)
7. [Pipeline de Telemetria](#7-pipeline-de-telemetria)
8. [Banco de Dados](#8-banco-de-dados)
9. [Deploy e CI/CD](#9-deploy-e-cicd)
10. [Variáveis de Ambiente e Segredos](#10-variáveis-de-ambiente-e-segredos)
11. [Monitoramento e Health Check](#11-monitoramento-e-health-check)
12. [Erros e Códigos de Resposta](#12-erros-e-códigos-de-resposta)
13. [Desenvolvimento Local](#13-desenvolvimento-local)

---

## 1. Visão Geral do Sistema

O **AgroFlightOps** é uma plataforma de gestão de operações de pulverização agrícola com drones. O sistema cobre todo o ciclo operacional: cadastro de clientes e propriedades, planejamento de ordens de serviço, agendamento e execução de missões de voo, controle de frota (drones e baterias), gestão de insumos, checklist pré-voo, registro de telemetria e encerramento financeiro.

### Stack tecnológico

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12 · FastAPI · SQLAlchemy (async) · Mangum |
| Banco de dados | MySQL 8 (Amazon RDS) via `aiomysql` |
| Frontend | React 18 · TypeScript · Vite · Ant Design · Leaflet |
| Infraestrutura | AWS Lambda · API Gateway HTTP · S3 · CloudFront · EventBridge · Glue · Athena |
| IaC / Deploy | AWS SAM · GitHub Actions (OIDC) · Flyway (migrações) |
| IA | Amazon Bedrock (insights de telemetria) |

---

## 2. Arquitetura de Infraestrutura

```
Internet
   │
   ▼
CloudFront (CDN / HTTPS)
   │
   ├──► S3 FrontendBucket (SPA React — acesso apenas via OAC)
   │
   └──► API Gateway HTTP  ──► Lambda AgroFlightOpsFunction
                                   │
                         ┌─────────┴──────────┐
                         ▼                    ▼
                    RDS MySQL           S3 DocumentsBucket
                 (VPC privada)         (documentos oficiais)

Telemetria (pipeline assíncrono):
  Upload API ──► S3 TelemetriaRawBucket (incoming/)
                        │
                 EventBridge Rule (Object Created)
                        │
                        ▼
            Lambda TelemetriaProcessorFunction
                        │
              ┌─────────┴──────────┐
              ▼                    ▼
   S3 TelemetriaProcessedBucket   GeoJSON / Summary
              │
       Glue Database ──► Athena WorkGroup
```

### Recursos AWS provisionados (por ambiente)

| Recurso | Nome / Padrão |
|---|---|
| Lambda principal | `agroflightops-{env}-AgroFlightOpsFunction` |
| Lambda telemetria | `agroflightops-{env}-TelemetriaProcessorFunction` |
| API Gateway | `AgroFlightOpsApi` (stage = env) |
| CloudFormation Stack | `agroflightops-{env}` |
| S3 Frontend | gerado pelo SAM |
| S3 Documentos | fornecido via parâmetro `S3DocumentsBucket` |
| S3 Telemetria Raw | `agroflightops-{env}-telemetria-raw` |
| S3 Telemetria Processed | `agroflightops-{env}-telemetria-processed` |
| S3 Athena Results | `agroflightops-{env}-telemetria-athena-results` |
| Glue Database | `agroflightops_{env}_telemetria` |
| Athena WorkGroup | `AgroFlightOps-{env}-telemetria` |

---

## 3. Ambientes

| Ambiente | Trigger | Stack | Debug | URL base (padrão) |
|---|---|---|---|---|
| `dev` | Push em `main` | `agroflightops-dev` | `true` | `https://<api-id>.execute-api.us-east-1.amazonaws.com/dev` |
| `hml` | Push em `release/*` | `agroflightops-hml` | `false` | `https://<api-id>.execute-api.us-east-1.amazonaws.com/hml` |
| `prd` | Tag `v*.*.*` + aprovação manual | `agroflightops-prd` | `false` | `https://<api-id>.execute-api.us-east-1.amazonaws.com/prd` |

A URL real da API de cada ambiente é exposta como output do CloudFormation (`ApiUrl`) e registrada no GitHub Step Summary após cada deploy.

---

## 4. Autenticação e Perfis de Acesso

### Autenticação

O sistema usa JWT Bearer Token (HS256). O token é obtido via `POST /auth/login` e deve ser enviado no cabeçalho de todas as requisições protegidas:

```
Authorization: Bearer <token>
```

Expiração padrão: **60 minutos**. O token pode ser renovado via `POST /auth/refresh` enquanto ainda for válido.

### Perfis disponíveis

| Perfil | Acesso |
|---|---|
| `ADMINISTRADOR` | Acesso total a todos os módulos |
| `COORDENADOR_OPERACIONAL` | Ordens de Serviço, Missões, leitura geral |
| `PILOTO` | Missões (execução), Checklist (preenchimento), Telemetria |
| `TECNICO` | Manutenções, Checklist (aprovação), Missões |
| `FINANCEIRO` | Financeiro de missões, Relatórios |

### Matriz de acesso por módulo

| Módulo | ADMIN | COORD | PILOTO | TECNICO | FINANCEIRO |
|---|:---:|:---:|:---:|:---:|:---:|
| Usuários | ✅ | — | — | — | — |
| Clientes / Propriedades / Talhões | ✅ | ✅ | — | — | — |
| Drones / Baterias / Insumos | ✅ | ✅ | — | — | — |
| Culturas / Tipos Ocorrência | ✅ | ✅ | — | — | — |
| Ordens de Serviço | ✅ | ✅ | — | — | — |
| Missões | ✅ | ✅ | ✅ | ✅ | — |
| Checklist (preencher) | ✅ | — | ✅ | — | — |
| Checklist (aprovar) | ✅ | — | — | ✅ | — |
| Manutenções | ✅ | — | — | ✅ | — |
| Documentos Oficiais (upload) | ✅ | — | — | — | — |
| Documentos Oficiais (leitura) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Telemetria / Insights IA | ✅ | ✅ | ✅ | ✅ | ✅ |
| Financeiro de Missão | ✅ | — | — | — | ✅ |
| Relatórios | ✅ | — | — | — | ✅ |
| Auditoria | ✅ | — | — | — | — |

---

## 5. Módulos e Endpoints da API

A documentação interativa completa (Swagger UI) está disponível em `{API_URL}/docs`.

### Autenticação
| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/auth/login` | Login com email e senha, retorna JWT |
| POST | `/auth/refresh` | Renova o token JWT |

### Usuários
| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/usuarios` | Lista usuários (paginado) |
| POST | `/usuarios` | Cria usuário |
| GET | `/usuarios/{id}` | Busca usuário por ID |
| PUT/PATCH | `/usuarios/{id}` | Atualiza usuário |
| DELETE | `/usuarios/{id}` | Desativa usuário (soft-delete) |

### Clientes, Propriedades, Talhões, Culturas
Seguem o padrão CRUD paginado:
- `GET/POST /clientes`, `GET/PUT/PATCH /clientes/{id}`
- `GET/POST /propriedades`, `GET/PUT/PATCH /propriedades/{id}`
- `GET/POST /talhoes`, `GET/PUT/PATCH /talhoes/{id}`
- `GET/POST /culturas`, `GET/PUT/PATCH /culturas/{id}`

### Drones e Baterias
- `GET/POST /drones`, `GET/PUT/PATCH /drones/{id}`
- `GET/POST /baterias`, `GET/PUT/PATCH /baterias/{id}`

Status de drone: `DISPONIVEL · EM_USO · EM_MANUTENCAO · BLOQUEADO · INATIVO`
Status de bateria: `DISPONIVEL · EM_USO · CARREGANDO · REPROVADA · DESCARTADA`

### Insumos
- `GET/POST /insumos`, `GET/PUT/PATCH /insumos/{id}`

### Ordens de Serviço
| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/ordens-servico` | Cria OS |
| GET | `/ordens-servico` | Lista com filtros (status, cliente, propriedade, prioridade, data) |
| GET | `/ordens-servico/{id}` | Detalhe da OS |
| PUT/PATCH | `/ordens-servico/{id}` | Atualiza OS |
| PATCH | `/ordens-servico/{id}/transicao` | Transiciona status |
| GET | `/ordens-servico/{id}/historico` | Histórico de status |

Status: `RASCUNHO → EM_ANALISE → APROVADA` (ou `REJEITADA / CANCELADA`)
Prioridades: `BAIXA · MEDIA · ALTA · CRITICA`

### Missões
| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/missoes` | Cria missão |
| GET | `/missoes` | Lista com filtros (status, piloto, drone, data, OS) |
| GET | `/missoes/{id}` | Detalhe da missão |
| PUT/PATCH | `/missoes/{id}` | Atualiza missão |
| PATCH | `/missoes/{id}/transicao` | Transiciona status |
| PATCH | `/missoes/{id}/execucao` | Registra dados de execução |
| GET | `/missoes/{id}/historico` | Histórico de status |
| POST/GET | `/missoes/{id}/baterias` | Associa/lista baterias |
| POST/GET | `/missoes/{id}/reservas-insumo` | Reserva/lista insumos |
| POST/GET | `/missoes/{id}/consumos-insumo` | Registra/lista consumo real |

### Checklist
| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/missoes/{id}/checklist` | Obtém checklist da missão |
| PATCH | `/missoes/{id}/checklist/itens/{item_id}` | Atualiza item (Piloto) |
| POST | `/missoes/{id}/checklist/concluir` | Conclui checklist (Piloto) |
| POST | `/missoes/{id}/checklist/aprovar` | Aprova checklist → libera missão (Técnico) |

### Manutenções
- `GET/POST /manutencoes`, `GET/PUT/PATCH /manutencoes/{id}`
- Filtros: `drone_id`, `data_inicio`, `data_fim`

### Financeiro
| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/missoes/{id}/financeiro` | Obtém registro financeiro |
| PATCH | `/missoes/{id}/financeiro` | Atualiza dados financeiros |
| POST | `/missoes/{id}/financeiro/encerrar` | Encerra financeiramente |

Status financeiro: `PENDENTE → EM_FATURAMENTO → FATURADO → RECEBIDO` (ou `CANCELADO`)

### Telemetria e Insights IA
| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/missoes/{id}/telemetria` | Upload de arquivo JSON de telemetria |
| GET | `/missoes/{id}/telemetria/resumo` | Resumo da telemetria processada |
| GET | `/missoes/{id}/telemetria/geojson` | Trajeto GeoJSON da missão |
| GET | `/missoes/{id}/telemetria/anomalias` | Pontos de anomalia detectados |
| GET | `/missoes/{id}/insights` | Insights gerados por IA (Amazon Bedrock) |

### Documentos Oficiais
- `POST /documentos-oficiais` (upload para S3)
- `GET /documentos-oficiais` (listagem com filtros)
- `GET /documentos-oficiais/{id}/download` (URL pré-assinada S3, válida por 3600s)

### Relatórios
| Método | Endpoint | Parâmetros |
|---|---|---|
| GET | `/relatorios/missoes-por-status` | `data_inicio`, `data_fim` |
| GET | `/relatorios/area-por-cliente` | `data_inicio`, `data_fim` |
| GET | `/relatorios/financeiro` | `data_inicio`, `data_fim` |
| GET | `/relatorios/utilizacao-drones` | `data_inicio`, `data_fim` |

### Auditoria
- `GET /auditoria` — filtros: `entidade`, `entidade_id`, `usuario_id`, `data_inicio`, `data_fim`

### Health Check
- `GET /health` — retorna `{"status": "ok"}` (sem autenticação, usado pelo CI/CD)

---

## 6. Fluxo Operacional Principal

O ciclo completo de uma operação segue este fluxo:

```
[1] CADASTRO BASE
    Clientes → Propriedades → Talhões → Culturas
    Drones → Baterias → Insumos → Usuários

[2] ORDEM DE SERVIÇO
    Criar OS (RASCUNHO)
         ↓
    Submeter para análise (EM_ANALISE)
         ↓
    APROVADA  ←──  REJEITADA
         ↓
    (ou CANCELADA a qualquer momento)

[3] MISSÃO (vinculada à OS aprovada)
    Criar (RASCUNHO → PLANEJADA)
         ↓
    Agendar → AGENDADA
         ↓
    Iniciar checklist → EM_CHECKLIST
         │
         ├─ Piloto preenche itens do checklist
         ├─ Piloto conclui checklist (CONCLUIDO)
         └─ Técnico aprova checklist → LIBERADA
         ↓
    Iniciar execução → EM_EXECUCAO
         ↓
    (PAUSADA ↔ EM_EXECUCAO)
         ↓
    CONCLUIDA
         ↓
    Encerramento técnico → ENCERRADA_TECNICAMENTE
         ↓
    Encerramento financeiro → ENCERRADA_FINANCEIRAMENTE
         ↓
    (ou CANCELADA a qualquer momento)

[4] PÓS-MISSÃO
    - Upload de telemetria (JSON) → processamento assíncrono
    - Registro de consumo real de insumos
    - Upload de evidências (fotos/vídeos)
    - Registro de ocorrências
    - Fechamento financeiro (faturamento, recebimento)
```

### Pré-requisitos para iniciar uma missão

Antes que o checklist possa ser concluído e a missão liberada para execução, os seguintes itens devem estar associados:
- Pelo menos 1 bateria vinculada
- Insumos reservados (quantidade prevista)
- Todos os itens obrigatórios do checklist preenchidos como `APROVADO`

---

## 7. Pipeline de Telemetria

### Upload de dados brutos

O piloto ou sistema externo faz upload de um arquivo JSON via `POST /missoes/{id}/telemetria`. O arquivo é salvo no **TelemetriaRawBucket** no caminho `incoming/{missao_id}_{timestamp}.json`.

### Processamento assíncrono

Um EventBridge Rule detecta a criação do objeto e aciona automaticamente a **Lambda TelemetriaProcessorFunction**. O processamento:

1. Lê o arquivo bruto do S3 Raw
2. Normaliza e enriquece cada ponto de telemetria (distância acumulada Haversine, atributos padronizados)
3. Detecta anomalias por ponto:

| Anomalia | Condição |
|---|---|
| `VELOCIDADE_EXCESSIVA` | speed > 8 m/s |
| `BATERIA_BAIXA` | battery < 20% |
| `ALTURA_BAIXA` | height < 2m |
| `ALTURA_ALTA` | height > 5m |
| `GPS_FRACO` | satellites < 10 |
| `SINAL_FRACO` | signal < 55% |
| `PULVERIZACAO_SEM_FLUXO` | spray_on = true e flow ≤ 0.1 L/min |

4. Calcula `mission_score` (0–100) por ponto com penalidades por anomalia e bônus para operação ideal (height 3–4m, speed 4–6.5 m/s durante pulverização)
5. Grava no **TelemetriaProcessedBucket**:
   - `telemetry/dt={data}/flight_id={id}/part-00000.jsonl` — registros normalizados (JSONL)
   - `geojson/dt={data}/flight_id={id}/track.geojson` — trajeto + pontos amostrados
   - `summary/dt={data}/flight_id={id}/summary.json` — métricas agregadas

### Consulta via API

Após o processamento, os dados ficam disponíveis via:
- `GET /missoes/{id}/telemetria/resumo` — distância total, score médio, pontos de anomalia
- `GET /missoes/{id}/telemetria/geojson` — para visualização no mapa
- `GET /missoes/{id}/telemetria/anomalias` — lista de pontos anômalos
- `GET /missoes/{id}/insights` — análise interpretativa gerada pelo Amazon Bedrock

### Consultas analíticas

Os dados processados estão catalogados no **Glue Database** e podem ser consultados via **Athena WorkGroup** para análises históricas e relatórios personalizados.

---

## 8. Banco de Dados

### Tecnologia
MySQL 8 em Amazon RDS, dentro de VPC privada. A conexão usa `mysql+aiomysql` (async) com pool de 5 conexões + 10 overflow.

### Migrações

As migrações são gerenciadas pelo **Flyway**, executado automaticamente no CI/CD quando `FLYWAY_ENABLED=true` (GitHub Variable). Os scripts SQL ficam em `database/` e seguem a convenção `V{n}__{descricao}.sql`.

Para rodar migrações manualmente:
```bash
docker run --rm \
  -v ./database:/flyway/sql \
  flyway/flyway:latest \
  -url="jdbc:mysql://{HOST}:{PORT}/{DB}" \
  -user="{USER}" \
  -password="{PASS}" \
  migrate
```

### Principais tabelas

| Tabela | Descrição |
|---|---|
| `perfis` / `usuarios` | Usuários e controle de acesso |
| `clientes` | Clientes produtores rurais |
| `propriedades` / `talhoes` | Fazendas e parcelas de cada cliente |
| `culturas` | Culturas agrícolas cadastradas |
| `drones` / `baterias` | Frota de drones e baterias |
| `insumos` | Estoque de defensivos e fertilizantes |
| `ordens_servico` / `historico_status_os` | OS e histórico de status |
| `missoes` / `historico_status_missao` | Missões de voo e histórico |
| `missao_baterias` | Baterias utilizadas por missão |
| `reservas_insumo` / `consumos_insumo_missao` | Planejamento e consumo real |
| `checklists_missao` / `itens_checklist_missao` | Checklist pré-voo |
| `itens_checklist_padrao` | Template de itens do checklist |
| `manutencoes` | Registros de manutenção de drones |
| `ocorrencias` / `tipos_ocorrencia` | Ocorrências durante missões |
| `evidencias` | Fotos/vídeos vinculados a missões |
| `financeiro_missao` | Dados financeiros por missão |
| `documentos_oficiais` | Metadados de documentos no S3 |
| `auditoria` | Log de alterações no sistema |

---

## 9. Deploy e CI/CD

### Fluxo automático

| Ação Git | Ambiente alvo | Aprovação |
|---|---|---|
| Push em `main` | `dev` | Automático |
| Push em `release/*` | `hml` | Automático |
| Tag `v*.*.*` | `prd` | Manual — GitHub Environment "production" |

### Etapas do pipeline

```
1. Checkout + Setup (Python 3.12, Node.js 20)
2. Testes: pytest (backend) + eslint (frontend)
3. Credenciais AWS via OIDC (sem access keys estáticas)
4. Build frontend (Vite) com VITE_API_BASE_URL do ambiente
5. Build backend: sam build --use-container
6. Flyway migrations (se FLYWAY_ENABLED=true)
7. sam deploy --config-env {dev|hml|prd}
8. Sync frontend → S3 + invalidação CloudFront
9. Health check com retry (3 tentativas, backoff exponencial)
```

### Deploy manual (local)

Pré-requisitos: AWS CLI configurado, SAM CLI, Docker (para `--use-container`).

```bash
# Build
sam build --use-container

# Deploy num ambiente específico
sam deploy --config-env dev \
  --parameter-overrides \
    "DatabaseUrl=mysql+aiomysql://user:pass@host:3306/db" \
    "JwtSecret=sua-chave-secreta-aqui" \
    "VpcSubnetIds=subnet-xxx,subnet-yyy" \
    "VpcSecurityGroupIds=sg-xxx" \
    "S3DocumentsBucket=nome-do-bucket" \
    "CorsOrigins=https://seu-frontend.com"
```

### Criar nova versão para produção

```bash
git tag v1.2.3
git push origin v1.2.3
# O deploy em prd aguarda aprovação manual no GitHub Environment "production"
```

### Pré-requisitos AWS (configuração única)

1. **IAM Identity Provider OIDC**
   - URL: `https://token.actions.githubusercontent.com`
   - Audience: `sts.amazonaws.com`

2. **IAM Role** com trust policy para o repositório GitHub, com permissões para CloudFormation, S3, Lambda, API Gateway, CloudFront, IAM (PassRole), CloudWatch Logs, EC2 (VPC/ENI)

3. **GitHub Environment "production"** com pelo menos 1 reviewer obrigatório

---

## 10. Variáveis de Ambiente e Segredos

### GitHub Secrets (valores sensíveis)

| Secret | Descrição |
|---|---|
| `AWS_ROLE_ARN` | ARN da IAM Role assumida via OIDC |
| `DATABASE_URL_DEV` / `_HML` / `_PRD` | Connection string MySQL por ambiente |
| `JWT_SECRET_DEV` / `_HML` / `_PRD` | Chave de assinatura JWT por ambiente |

### GitHub Variables (valores não-sensíveis)

| Variable | Descrição |
|---|---|
| `VPC_SUBNET_IDS_DEV` / `_HML` / `_PRD` | IDs das subnets privadas (vírgula) |
| `VPC_SG_IDS_DEV` / `_HML` / `_PRD` | IDs dos Security Groups (vírgula) |
| `S3_DOCS_BUCKET_DEV` / `_HML` / `_PRD` | Nome do bucket S3 de documentos |
| `CORS_ORIGINS_DEV` / `_HML` / `_PRD` | Origens CORS permitidas (vírgula) |
| `API_URL_DEV` / `_HML` / `_PRD` | URL da API para build do frontend |
| `FLYWAY_ENABLED` | `true` para habilitar migrações automáticas |

### Variáveis de ambiente da Lambda (injetadas via SAM)

| Variável | Valor padrão (dev) | Descrição |
|---|---|---|
| `DATABASE_URL` | `mysql+aiomysql://root:root@localhost:3306/agroflightops` | Connection string |
| `JWT_SECRET` | `dev-secret-change-in-production` | Chave JWT |
| `JWT_ALGORITHM` | `HS256` | Algoritmo JWT |
| `JWT_EXPIRATION_MINUTES` | `60` | Expiração do token |
| `S3_BUCKET` | `agroflightops-docs-dev` | Bucket de documentos |
| `S3_REGION` | `us-east-1` | Região do S3 |
| `S3_PRESIGNED_URL_EXPIRATION` | `3600` | Validade de URLs pré-assinadas (segundos) |
| `CORS_ORIGINS` | `*` | Origens CORS |
| `APP_ENV` | `dev` | Nome do ambiente |
| `DEBUG` | `false` | Ativa logs SQL e modo debug |
| `TELEMETRIA_RAW_BUCKET` | — | Bucket raw de telemetria |
| `TELEMETRIA_PROCESSED_BUCKET` | — | Bucket processed de telemetria |

---

## 11. Monitoramento e Health Check

### Health check

```
GET /health
→ 200 {"status": "ok"}
```

Executado pelo CI/CD após cada deploy com até 3 tentativas (backoff exponencial: 10s → 20s → 40s). Falha interrompe o pipeline.

### CloudWatch Logs

Todos os logs da Lambda são enviados para o grupo `/aws/lambda/agroflightops-{env}-AgroFlightOpsFunction`. O nível de detalhe dos logs SQL é controlado pela variável `DEBUG`.

### Outputs do CloudFormation

Após o deploy, os principais endpoints ficam disponíveis como outputs da stack:

```bash
aws cloudformation describe-stacks \
  --stack-name agroflightops-dev \
  --query "Stacks[0].Outputs"
```

| Output | Descrição |
|---|---|
| `ApiUrl` | URL do API Gateway |
| `FrontendBucketName` | Nome do bucket S3 do frontend |
| `CloudFrontDomainName` | Domínio da distribuição CloudFront |
| `CloudFrontDistributionId` | ID da distribuição (para invalidação) |
| `TelemetriaRawBucketName` | Bucket raw de telemetria |
| `TelemetriaProcessedBucketName` | Bucket processed de telemetria |
| `GlueDatabaseName` | Nome do banco Glue |
| `AthenaWorkGroupName` | WorkGroup Athena |

---

## 12. Erros e Códigos de Resposta

Todos os erros seguem o formato:
```json
{
  "detail": "Mensagem descritiva do erro",
  "errors": []
}
```

Para erros de validação (`422`), `errors` contém a lista de campos com problemas:
```json
{
  "detail": "Erro de validação nos dados enviados",
  "errors": [
    {"field": "email", "message": "value is not a valid email address"}
  ]
}
```

### Tabela de códigos

| Código | Situação |
|---|---|
| `200` | Sucesso |
| `201` | Recurso criado |
| `401` | Token não fornecido, inválido ou expirado |
| `403` | Perfil sem permissão para o recurso |
| `404` | Recurso não encontrado |
| `409` | Registro duplicado / transição de status inválida / dependência ativa |
| `422` | Erro de validação ou violação de regra de negócio |
| `502` | Erro ao invocar Amazon Bedrock (insights IA) |

---

## 13. Desenvolvimento Local

### Pré-requisitos

- Python 3.12
- Node.js 20
- MySQL 8 local (ou Docker)
- Docker (para `sam build --use-container`)
- AWS SAM CLI
- AWS CLI (para deploys manuais)

### Configuração do backend

```bash
# Clonar e instalar dependências
pip install -r requirements.txt

# Criar arquivo .env na raiz do projeto
cat > .env << EOF
DATABASE_URL=mysql+aiomysql://root:root@localhost:3306/agroflightops
JWT_SECRET=dev-secret-local
S3_BUCKET=agroflightops-local
CORS_ORIGINS=*
APP_ENV=dev
DEBUG=true
EOF

# Rodar localmente (sem Lambda)
uvicorn app.main:app --reload --port 8000
```

A API estará disponível em `http://localhost:8000` e o Swagger em `http://localhost:8000/docs`.

> **Atenção:** ao rodar localmente o `root_path` e o `api_gateway_base_path` ficam vazios (`APP_ENV=""`), então os endpoints ficam direto na raiz sem o prefixo de ambiente.

### Configuração do frontend

```bash
cd frontend
npm install

# Criar .env.local
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local

npm run dev
# Frontend em http://localhost:5173
```

### Testes

```bash
# Backend — todos os testes
pytest

# Backend — apenas testes de um módulo
pytest tests/test_missoes.py -v

# Frontend — lint
cd frontend && npm run lint
```

### Banco de dados local

```bash
# Subir MySQL via Docker
docker run -d \
  --name agroflightops-db \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=agroflightops \
  -p 3306:3306 \
  mysql:8

# Aplicar schema inicial
mysql -h 127.0.0.1 -u root -proot agroflightops < database/V1__initial_schema.sql
```

### Estrutura de diretórios

```
AgroFlightOps/
├── app/
│   ├── api/          # Routers FastAPI (um arquivo por módulo)
│   ├── core/         # Config, database, security, dependencies, exceptions
│   ├── models/       # ORM SQLAlchemy (models.py, enums.py)
│   ├── repositories/ # Acesso a dados (Repository pattern)
│   ├── schemas/      # Pydantic schemas (request/response)
│   ├── services/     # Lógica de negócio
│   └── main.py       # Entry point FastAPI + Mangum handler
├── frontend/         # SPA React + TypeScript + Vite
├── lambda_processor/ # Lambda de processamento de telemetria
├── database/         # Scripts SQL e migrations Flyway
├── tests/            # Testes pytest
├── docs/             # Documentação
├── template.yaml     # SAM template (IaC)
├── samconfig.toml    # Configurações de deploy por ambiente
└── .github/
    └── workflows/
        └── deploy.yml  # Pipeline CI/CD
```

---

*Documentação gerada com base no código-fonte do projeto. Para dúvidas operacionais, consulte os logs no CloudWatch ou abra uma issue no repositório.*
