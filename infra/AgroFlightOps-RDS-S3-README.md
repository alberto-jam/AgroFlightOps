# AgroFlightOps — README de Implantação

Este documento descreve como implantar a stack CloudFormation do banco PostgreSQL e do bucket de documentos do produto **AgroFlightOps**.

## Arquivos

- `AgroFlightOps-RDS-S3.yaml`
- `AgroFlightOps-RDS-S3-dev-params.json`
- `AgroFlightOps-RDS-S3-hml-params.json`
- `AgroFlightOps-RDS-S3-prd-params.json`

## O que a stack provisiona

- Amazon RDS PostgreSQL
- AWS Secrets Manager para credenciais do banco
- Bucket S3 para documentos
- Security Group do banco
- DB Subnet Group
- DB Parameter Group
- Outputs exportáveis para integração com outras stacks

## Convenções adotadas

### Parâmetros
- `Client = Vista Agrotech`
- `Project = AgroFlightOps`
- `Environment = dev | hml | prd`
- `Author = Alberto Moreira`

### Tags
- `Cliente = Client`
- `Projeto = Project`
- `Ambiente = Environment`
- `Autor = Author`

### Nome dos recursos
Padrão:

`<Project>-<Environment>-<Nome Recurso>`

Exemplos:
- `AgroFlightOps-dev-db`
- `AgroFlightOps-hml-db`
- `AgroFlightOps-prd-db`
- `AgroFlightOps-dev-documents`

## Pré-requisitos

Antes do deploy, confirme:

- AWS CLI instalado e autenticado
- permissão para CloudFormation, RDS, EC2, S3 e Secrets Manager
- VPC existente
- ao menos 2 subnets privadas em AZs distintas
- um Security Group da aplicação que precisará acessar o banco

## Parâmetros que você precisa revisar

Nos arquivos `.json`, ajuste os valores abaixo:

- `VpcId`
- `PrivateSubnetIds`
- `AppSecurityGroupId`

Opcionalmente:

- `DocumentsBucketName`

Se você quiser um nome fixo para o bucket, informe explicitamente. Se preferir reduzir risco de colisão global, use um nome único por conta/ambiente.

## Perfis sugeridos por ambiente

### dev
- instância: `db.t4g.micro`
- storage: `20 GB`
- Multi-AZ: `false`
- deletion protection: `false`

### hml
- instância: `db.t4g.small`
- storage: `50 GB`
- Multi-AZ: `false`
- deletion protection: `false`

### prd
- instância: `db.t4g.medium`
- storage: `100 GB`
- Multi-AZ: `true`
- deletion protection: `true`

## Validar a stack antes do deploy

```bash
aws cloudformation validate-template \
  --template-body file://AgroFlightOps-RDS-S3.yaml
```

## Criar a stack

### DEV

```bash
aws cloudformation create-stack \
  --stack-name AgroFlightOps-dev-rds-s3 \
  --template-body file://AgroFlightOps-RDS-S3.yaml \
  --parameters file://AgroFlightOps-RDS-S3-dev-params.json
```

### HML

```bash
aws cloudformation create-stack \
  --stack-name AgroFlightOps-hml-rds-s3 \
  --template-body file://AgroFlightOps-RDS-S3.yaml \
  --parameters file://AgroFlightOps-RDS-S3-hml-params.json
```

### PRD

```bash
aws cloudformation create-stack \
  --stack-name AgroFlightOps-prd-rds-s3 \
  --template-body file://AgroFlightOps-RDS-S3.yaml \
  --parameters file://AgroFlightOps-RDS-S3-prd-params.json
```

## Acompanhar a criação

```bash
aws cloudformation describe-stacks \
  --stack-name AgroFlightOps-dev-rds-s3
```

ou

```bash
aws cloudformation wait stack-create-complete \
  --stack-name AgroFlightOps-dev-rds-s3
```

## Atualizar a stack

### DEV

```bash
aws cloudformation update-stack \
  --stack-name AgroFlightOps-dev-rds-s3 \
  --template-body file://AgroFlightOps-RDS-S3.yaml \
  --parameters file://AgroFlightOps-RDS-S3-dev-params.json
```

### HML

```bash
aws cloudformation update-stack \
  --stack-name AgroFlightOps-hml-rds-s3 \
  --template-body file://AgroFlightOps-RDS-S3.yaml \
  --parameters file://AgroFlightOps-RDS-S3-hml-params.json
```

### PRD

```bash
aws cloudformation update-stack \
  --stack-name AgroFlightOps-prd-rds-s3 \
  --template-body file://AgroFlightOps-RDS-S3.yaml \
  --parameters file://AgroFlightOps-RDS-S3-prd-params.json
```

## Ver outputs da stack

```bash
aws cloudformation describe-stacks \
  --stack-name AgroFlightOps-dev-rds-s3 \
  --query "Stacks[0].Outputs"
```

Você deve obter outputs como:

- endpoint do RDS
- porta do banco
- nome do secret
- nome do bucket de documentos
- security group do banco

## Ler as credenciais do banco no Secrets Manager

```bash
aws secretsmanager get-secret-value \
  --secret-id AgroFlightOps-dev-db-secret
```

A resposta deve conter algo equivalente a:

```json
{
  "username": "postgres",
  "password": "...",
  "engine": "postgres",
  "host": "...",
  "port": 5432,
  "dbname": "agroflightops"
}
```

## Testar conexão no PostgreSQL

Exemplo usando `psql`:

```bash
psql \
  -h <DB_ENDPOINT> \
  -p 5432 \
  -U postgres \
  -d agroflightops
```

## Aplicar o DDL do banco

Após a criação do RDS, aplique o script SQL do schema:

- `pulverizacao_drones_postgres_ddl.sql`

Exemplo:

```bash
psql \
  -h <DB_ENDPOINT> \
  -p 5432 \
  -U postgres \
  -d agroflightops \
  -f pulverizacao_drones_postgres_ddl.sql
```

## Validações pós-deploy

Verifique:

- stack em status `CREATE_COMPLETE` ou `UPDATE_COMPLETE`
- RDS criado e disponível
- secret criado
- bucket S3 criado
- Security Group criado
- aplicação consegue acessar a porta 5432 no RDS
- DDL aplicado com sucesso

## Erros comuns

### 1. Bucket name já existe
Causa:
- nome S3 globalmente já utilizado

Ação:
- definir `DocumentsBucketName` com um nome único

### 2. Subnets inválidas para RDS
Causa:
- subnets não pertencem à mesma VPC
- falta de ao menos duas subnets adequadas

Ação:
- usar subnets privadas válidas em AZs distintas

### 3. Aplicação não conecta ao banco
Causa:
- `AppSecurityGroupId` não autorizado
- rota/NACL/VPC incorreta

Ação:
- revisar regra de entrada no SG do banco para porta `5432`
- revisar conectividade da aplicação dentro da VPC

### 4. Falha ao ler o secret
Causa:
- role/usuário sem permissão no Secrets Manager

Ação:
- conceder `secretsmanager:GetSecretValue`

### 5. Atualização falha por mudança não suportada
Causa:
- algumas alterações do RDS geram substituição ou reinicialização

Ação:
- revisar change set antes de atualizar em produção

## Recomendações para evolução

### Curto prazo
- aplicar o DDL completo no banco
- criar stack separada para API/Lambda/backend
- controlar migrações com Flyway ou Liquibase

### Médio prazo
- separar stacks por domínio:
  - dados
  - backend
  - frontend
  - observabilidade
- considerar parameter group dedicado por ambiente
- adicionar alarms do CloudWatch para RDS

### Produção
- habilitar monitoramento aprimorado quando necessário
- revisar backup retention
- revisar janela de manutenção
- avaliar Aurora PostgreSQL se houver crescimento relevante

## Ordem recomendada de implantação

1. criar stack de banco e documentos
2. validar outputs
3. recuperar credenciais do secret
4. testar conexão no banco
5. aplicar DDL do schema
6. implantar backend
7. implantar frontend
8. validar upload/download de documentos no S3

## Artefatos relacionados

- stack CloudFormation: `AgroFlightOps-RDS-S3.yaml`
- parâmetros dev: `AgroFlightOps-RDS-S3-dev-params.json`
- parâmetros hml: `AgroFlightOps-RDS-S3-hml-params.json`
- parâmetros prd: `AgroFlightOps-RDS-S3-prd-params.json`
- DDL PostgreSQL: `pulverizacao_drones_postgres_ddl.sql`
