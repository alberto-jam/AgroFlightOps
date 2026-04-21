# Plano de Implementação: Pipeline de Build e Deploy com AWS SAM

## Visão Geral

Implementação incremental da pipeline de build e deploy do AgroFlightOps usando AWS SAM. As tarefas seguem a ordem: template SAM (backend + frontend + IAM) → configuração multi-ambiente → workflow GitHub Actions (CI/CD, Flyway, deploy, health check). Cada etapa constrói sobre a anterior, garantindo que não haja código órfão.

## Tarefas

- [x] 1. Criar o SAM Template com Lambda, API Gateway e IAM Role
  - [x] 1.1 Criar o arquivo `template.yaml` na raiz do projeto com a estrutura base SAM
    - Definir `AWSTemplateFormatVersion`, `Transform: AWS::Serverless-2016-10-31` e `Description`
    - Definir todos os `Parameters`: Environment, VpcSubnetIds, VpcSecurityGroupIds, DatabaseUrl (NoEcho), JwtSecret (NoEcho), JwtAlgorithm, JwtExpirationMinutes, S3DocumentsBucket, S3Region, CorsOrigins, AppEnv, Debug, Autor (Default: Alberto Moreira)
    - Definir `Globals.Function` com Timeout 30, MemorySize 512, Runtime python3.12 e Tags padrão (Cliente: VistaAgrotech, Projeto: AgroFlightOps, Ambiente: !Ref Environment, Autor: !Ref Autor)
    - _Requisitos: 1.1, 1.3, 1.5, 1.7_

  - [x] 1.2 Definir o recurso `AgroFlightOpsFunction` (AWS::Serverless::Function)
    - Handler: `app.main.handler`, CodeUri: `.`, BuildMethod: `python3.12`
    - VpcConfig referenciando VpcSubnetIds e VpcSecurityGroupIds
    - Environment Variables: DATABASE_URL, JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_MINUTES, S3_BUCKET, S3_REGION, CORS_ORIGINS, APP_ENV, DEBUG (todos via !Ref dos parâmetros)
    - Role: !GetAtt LambdaExecutionRole.Arn
    - Evento HttpApi catch-all `/{proxy+}` com método ANY vinculado ao AgroFlightOpsApi
    - _Requisitos: 1.1, 1.2, 1.3, 1.6_

  - [x] 1.3 Definir o recurso `AgroFlightOpsApi` (AWS::Serverless::HttpApi)
    - StageName: !Ref Environment
    - CorsConfiguration com AllowOrigins, AllowMethods (GET, POST, PUT, PATCH, DELETE, OPTIONS) e AllowHeaders
    - _Requisitos: 1.2_

  - [x] 1.4 Definir o recurso `LambdaExecutionRole` (AWS::IAM::Role)
    - AssumeRolePolicyDocument para lambda.amazonaws.com
    - Política CloudWatch Logs: `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents` com Resource restrito ao ARN do log group da Lambda
    - Política S3 Documentos: `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject`, `s3:ListBucket` com Resource restrito ao ARN do bucket de documentos
    - Política VPC: `ec2:CreateNetworkInterface`, `ec2:DescribeNetworkInterfaces`, `ec2:DeleteNetworkInterface` com Resource `*` (requerido pela AWS para ENI)
    - Tags padrão: Cliente, Projeto, Ambiente, Autor
    - _Requisitos: 1.4, 11.1, 11.2, 11.3, 11.4_

  - [x] 1.5 Definir os `Outputs` do template
    - ApiUrl: URL do API Gateway
    - FrontendBucketName: nome do bucket frontend
    - CloudFrontDomainName: domain do CloudFront
    - CloudFrontDistributionId: ID da distribuição
    - Todos com Export Name no formato `AgroFlightOps-{env}-*`
    - _Requisitos: 2.6_

- [x] 2. Adicionar recursos de Frontend (S3 + CloudFront) ao SAM Template
  - [x] 2.1 Definir o recurso `FrontendBucket` (AWS::S3::Bucket)
    - WebsiteConfiguration: IndexDocument `index.html`, ErrorDocument `index.html`
    - PublicAccessBlockConfiguration: bloquear todo acesso público (BlockPublicAcls, BlockPublicPolicy, IgnorePublicAcls, RestrictPublicBuckets = true)
    - Tags padrão: Cliente, Projeto, Ambiente, Autor
    - _Requisitos: 2.1, 2.2_

  - [x] 2.2 Definir os recursos `CloudFrontOAC` e `CloudFrontDistribution`
    - CloudFrontOAC (AWS::CloudFront::OriginAccessControl): SigningProtocol sigv4, SigningBehavior always, OriginAccessControlOriginType s3
    - CloudFrontDistribution (AWS::CloudFront::Distribution): Origin apontando para FrontendBucket via OAC, DefaultCacheBehavior para arquivos estáticos, CustomErrorResponses para 403/404 redirecionando para `/index.html` (suporte SPA), DefaultRootObject `index.html`
    - Tags padrão na distribuição
    - _Requisitos: 2.3, 2.4_

  - [x] 2.3 Definir o recurso `FrontendBucketPolicy` (AWS::S3::BucketPolicy)
    - Permitir `s3:GetObject` somente para o principal `cloudfront.amazonaws.com` com condição `aws:SourceArn` apontando para a CloudFrontDistribution
    - _Requisitos: 2.5, 11.5_

- [x] 3. Checkpoint — Validar o SAM Template
  - Executar `sam validate` para verificar sintaxe do template
  - Executar `cfn-lint template.yaml` para verificar boas práticas CloudFormation
  - Verificar que todos os parâmetros obrigatórios estão definidos
  - Verificar que as 4 TAGs padrão estão em todos os recursos que suportam tags
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Criar a configuração multi-ambiente (`samconfig.toml`)
  - [x] 4.1 Criar o arquivo `samconfig.toml` na raiz do projeto
    - Definir `version = 0.1`
    - Seção `[default.build.parameters]` com `use_container = true`
    - Seção `[dev.deploy.parameters]`: stack_name `agroflightops-dev`, region `us-east-1`, confirm_changeset false, capabilities `CAPABILITY_IAM CAPABILITY_NAMED_IAM`, s3_prefix `agroflightops-dev-artifacts`, parameter_overrides com Environment=dev, AppEnv=dev, Debug=true e placeholders para demais parâmetros
    - Seção `[hml.deploy.parameters]`: stack_name `agroflightops-hml`, mesma estrutura com Debug=false e parâmetros de hml
    - Seção `[prd.deploy.parameters]`: stack_name `agroflightops-prd`, mesma estrutura com Debug=false e parâmetros de produção
    - _Requisitos: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [x] 5. Criar o workflow GitHub Actions de CI/CD
  - [x] 5.1 Criar o arquivo `.github/workflows/deploy.yml` com triggers e permissões
    - Trigger `push` nas branches `main` e `release/*`
    - Trigger `push` em tags `v*.*.*`
    - Permissions: `id-token: write` (OIDC), `contents: read`
    - Definir lógica de determinação do ambiente: main→dev, release/*→hml, tag v*.*.*→prd
    - Configurar `environment` condicional: `production` para prd (aprovação manual via GitHub Environments)
    - _Requisitos: 9.1, 9.2, 9.3, 9.6, 10.3_

  - [x] 5.2 Implementar os steps de setup e testes
    - Checkout do código
    - Setup Python 3.12
    - Setup Node.js 20
    - Instalar dependências Python: `pip install -r requirements.txt`
    - Instalar dependências frontend: `npm ci` no diretório `frontend/`
    - Executar testes backend: `pytest` — falha interrompe o workflow
    - Executar lint frontend: `npm run lint` no diretório `frontend/` — falha interrompe o workflow
    - _Requisitos: 9.4, 9.5, 9.8_

  - [x] 5.3 Implementar os steps de build (backend e frontend)
    - Configurar credenciais AWS via OIDC: `aws-actions/configure-aws-credentials@v4` com `role-to-assume: ${{ secrets.AWS_ROLE_ARN }}`
    - Build backend: `sam build --use-container`
    - Build frontend: `VITE_API_URL={api_url_do_ambiente} npm run build` no diretório `frontend/`
    - _Requisitos: 4.1, 4.2, 4.4, 5.1, 5.2, 5.3, 5.4, 9.6_

  - [x] 5.4 Implementar o step de migração Flyway
    - Executar Flyway via Docker: `docker run --rm -v database:/flyway/sql flyway/flyway:latest migrate` com credenciais parseadas do secret `DATABASE_URL_{ENV}`
    - Falha na migração interrompe o deploy completo (backend e frontend)
    - _Requisitos: 8.1, 8.2, 8.3, 8.4, 8.5_

  - [x] 5.5 Implementar os steps de deploy backend e frontend
    - Deploy backend: `sam deploy --config-env {ambiente}` com parameter overrides para DATABASE_URL, JWT_SECRET e demais variáveis sensíveis via GitHub Secrets
    - Verificar status da stack e capturar eventos de erro em caso de falha
    - Exibir URL do API Gateway como output do workflow
    - Deploy frontend: `aws s3 sync frontend/dist/ s3://{FrontendBucket} --delete`
    - Criar invalidação CloudFront: `aws cloudfront create-invalidation --distribution-id {id} --paths "/*"`
    - Aguardar conclusão da invalidação antes de reportar sucesso
    - Falha no s3 sync interrompe sem criar invalidação
    - _Requisitos: 6.1, 6.2, 6.3, 6.4, 6.5, 7.1, 7.2, 7.3, 7.4_

  - [x] 5.6 Implementar o step de health check pós-deploy
    - Executar `curl` no endpoint `/health` do API Gateway com retry (até 3 tentativas com backoff para cold start)
    - Verificar resposta HTTP 200 com `{"status": "ok"}`
    - Marcar workflow como falho se health check falhar
    - _Requisitos: 10.4, 10.5_

- [x] 6. Checkpoint — Validar workflow e configurações
  - Verificar que o workflow YAML é válido (sintaxe)
  - Verificar que todos os secrets referenciados estão documentados: AWS_ROLE_ARN, DATABASE_URL_DEV, DATABASE_URL_HML, DATABASE_URL_PRD, JWT_SECRET_DEV, JWT_SECRET_HML, JWT_SECRET_PRD
  - Verificar que a ordem dos steps segue: checkout → setup → testes → build → Flyway → deploy backend → deploy frontend → health check
  - Verificar que o samconfig.toml tem as 3 seções de ambiente com todos os campos obrigatórios
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Preparar scripts Flyway e documentação de secrets
  - [x] 7.1 Renomear/organizar o DDL existente para convenção Flyway
    - Criar arquivo `database/V1__initial_schema.sql` baseado no DDL existente (`database/AgroFlightOps_RDS_MySQL_ddl.sql`)
    - Garantir que o script é idempotente ou adequado para primeira execução do Flyway
    - _Requisitos: 8.2_

  - [x] 7.2 Adicionar comentários no workflow documentando os GitHub Secrets necessários
    - Documentar no topo do `deploy.yml` os secrets obrigatórios e seus formatos esperados
    - Documentar o pré-requisito de IAM Identity Provider para OIDC e a IAM Role com trust policy para o repositório
    - _Requisitos: 9.7_

- [x] 8. Checkpoint final — Validação completa
  - Executar `sam validate` no template.yaml
  - Verificar que todos os 11 requisitos estão cobertos pelas tarefas implementadas
  - Verificar que o workflow referencia corretamente o samconfig.toml para cada ambiente
  - Verificar que as TAGs padrão (Cliente, Projeto, Ambiente, Autor) estão em todos os recursos do template
  - Ensure all tests pass, ask the user if questions arise.

## Notas

- Esta feature é 100% IaC/DevOps — não há testes baseados em propriedades (PBT)
- A stack RDS/S3 existente (`infra/AgroFlightOps-RDS-S3.yaml`) NÃO é recriada — o template SAM referencia recursos existentes via parâmetros
- Os checkpoints servem para validar incrementalmente antes de avançar
- Cada tarefa referencia os requisitos específicos para rastreabilidade
