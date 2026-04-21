# Documento de Requisitos — Pipeline de Build e Deploy com AWS SAM

## Introdução

Este documento define os requisitos para a criação de uma pipeline completa de build e deploy do sistema AgroFlightOps utilizando AWS SAM (Serverless Application Model). A pipeline abrange o empacotamento do backend Python/FastAPI como função Lambda, a configuração do API Gateway HTTP como proxy, o hosting estático do frontend React/Vite/TypeScript via S3 + CloudFront, a execução de migrações de banco de dados com Flyway, e a automação CI/CD com GitHub Actions para promoção entre os ambientes dev, hml e prd.

## Glossário

- **SAM_Template**: Arquivo `template.yaml` no formato AWS SAM que define todos os recursos serverless da aplicação (Lambda, API Gateway, IAM, S3, CloudFront)
- **SAM_Config**: Arquivo `samconfig.toml` que armazena configurações de deploy por ambiente (parâmetros, região, stack name, S3 bucket de artefatos)
- **Pipeline_CI_CD**: Workflow do GitHub Actions que automatiza build, testes, e deploy da aplicação nos ambientes configurados
- **Lambda_Function**: Função AWS Lambda que executa o backend FastAPI via handler Mangum (`app.main.handler`)
- **API_Gateway**: API Gateway HTTP (v2) configurado como proxy para a Lambda_Function
- **Frontend_Bucket**: Bucket S3 configurado para hosting estático do frontend React compilado
- **CloudFront_Distribution**: Distribuição CloudFront que serve o Frontend_Bucket com HTTPS e cache
- **Lambda_Execution_Role**: Role IAM atribuída à Lambda_Function com permissões para acessar RDS, S3 de documentos e CloudWatch Logs
- **Flyway_Migration**: Processo de execução de scripts SQL versionados no diretório `database/` contra o banco MySQL RDS
- **Ambiente**: Uma das três instâncias de deploy do sistema: dev, hml ou prd, cada uma com parâmetros e recursos independentes
- **Artefato_Backend**: Pacote gerado pelo `sam build` contendo o código Python e dependências da Lambda_Function
- **Artefato_Frontend**: Diretório `frontend/dist/` gerado pelo `npm run build` contendo os arquivos estáticos do frontend

## Requisitos

### Requisito 1: Template SAM para Backend Serverless

**User Story:** Como engenheiro DevOps, eu quero um SAM_Template que defina a infraestrutura serverless do backend, para que o deploy do backend seja reprodutível e versionado como código.

#### Critérios de Aceitação

1. THE SAM_Template SHALL definir uma Lambda_Function com runtime Python 3.12, handler `app.main.handler`, timeout de 30 segundos e memória de 512 MB
2. THE SAM_Template SHALL definir um API_Gateway do tipo `HttpApi` como evento da Lambda_Function, com rota catch-all `/{proxy+}` nos métodos GET, POST, PUT, PATCH e DELETE
3. THE SAM_Template SHALL aceitar parâmetros para as variáveis de ambiente da Lambda_Function: DATABASE_URL, JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_MINUTES, S3_BUCKET, S3_REGION, CORS_ORIGINS, APP_ENV e DEBUG
4. THE SAM_Template SHALL definir uma Lambda_Execution_Role com políticas para acesso ao Amazon RDS (via VPC), leitura e escrita no bucket S3 de documentos, e escrita em CloudWatch Logs
5. WHEN o parâmetro `Environment` for fornecido, THE SAM_Template SHALL aplicar tags `Cliente: VistaAgrotech`, `Projeto: AgroFlightOps`, `Ambiente: {Environment}` e `Autor: Alberto Moreira` em todos os recursos que suportam tags
6. THE SAM_Template SHALL configurar a Lambda_Function dentro da VPC, referenciando SubnetIds e SecurityGroupIds como parâmetros
7. THE SAM_Template SHALL definir parâmetros para VpcSubnetIds, VpcSecurityGroupIds, DatabaseUrl, JwtSecret, S3DocumentsBucket, S3Region e Autor, todos do tipo String. O parâmetro Autor SHALL ter valor default `Alberto Moreira`

### Requisito 2: Hosting Estático do Frontend com S3 e CloudFront

**User Story:** Como engenheiro DevOps, eu quero que o SAM_Template provisione um Frontend_Bucket e uma CloudFront_Distribution, para que o frontend React seja servido com HTTPS, cache e baixa latência.

#### Critérios de Aceitação

1. THE SAM_Template SHALL definir um Frontend_Bucket com configuração de website estático (IndexDocument: `index.html`, ErrorDocument: `index.html`)
2. THE SAM_Template SHALL bloquear acesso público direto ao Frontend_Bucket via PublicAccessBlockConfiguration
3. THE SAM_Template SHALL definir uma CloudFront_Distribution com origin apontando para o Frontend_Bucket via Origin Access Control (OAC)
4. THE SAM_Template SHALL configurar a CloudFront_Distribution com comportamento de cache padrão para arquivos estáticos e redirecionamento de erros 403/404 para `/index.html` (suporte a SPA)
5. THE SAM_Template SHALL definir uma BucketPolicy no Frontend_Bucket que permita acesso somente à CloudFront_Distribution via condição `aws:SourceArn`
6. THE SAM_Template SHALL exportar o nome do Frontend_Bucket e o domain name da CloudFront_Distribution como Outputs

### Requisito 3: Configuração Multi-Ambiente com samconfig.toml

**User Story:** Como engenheiro DevOps, eu quero um SAM_Config com perfis para dev, hml e prd, para que cada ambiente tenha parâmetros de deploy independentes e o processo seja padronizado.

#### Critérios de Aceitação

1. THE SAM_Config SHALL definir seções `[dev.deploy.parameters]`, `[hml.deploy.parameters]` e `[prd.deploy.parameters]`
2. WHEN o deploy for executado com `--config-env dev`, THE SAM_Config SHALL fornecer stack_name `agroflightops-dev`, região `us-east-1` e parâmetros específicos do ambiente dev
3. WHEN o deploy for executado com `--config-env hml`, THE SAM_Config SHALL fornecer stack_name `agroflightops-hml`, região `us-east-1` e parâmetros específicos do ambiente hml
4. WHEN o deploy for executado com `--config-env prd`, THE SAM_Config SHALL fornecer stack_name `agroflightops-prd`, região `us-east-1` e parâmetros específicos do ambiente prd
5. THE SAM_Config SHALL incluir `confirm_changeset = false` e `capabilities = "CAPABILITY_IAM CAPABILITY_NAMED_IAM"` em todos os ambientes
6. THE SAM_Config SHALL definir um S3 bucket prefix para artefatos de deploy no formato `agroflightops-{ambiente}-artifacts`

### Requisito 4: Processo de Build do Backend

**User Story:** Como engenheiro DevOps, eu quero que o processo de build empacote o backend Python com todas as dependências, para que a Lambda_Function execute corretamente com o código e bibliotecas necessárias.

#### Critérios de Aceitação

1. WHEN `sam build` for executado, THE Artefato_Backend SHALL conter o código do diretório `app/` e todas as dependências listadas em `requirements.txt`
2. THE SAM_Template SHALL especificar `BuildMethod: python3.12` e `CodeUri: .` para que o SAM resolva as dependências automaticamente
3. WHEN o build for concluído, THE Artefato_Backend SHALL ser verificável via execução de `sam local invoke` com evento de teste
4. IF `requirements.txt` contiver dependências com binários nativos (aiomysql, cryptography), THEN THE processo de build SHALL utilizar container Docker via flag `--use-container` para garantir compatibilidade com o runtime Lambda

### Requisito 5: Processo de Build do Frontend

**User Story:** Como engenheiro DevOps, eu quero que o processo de build compile o frontend React/TypeScript, para que os arquivos estáticos otimizados sejam gerados para deploy no S3.

#### Critérios de Aceitação

1. WHEN o build do frontend for executado, THE Pipeline_CI_CD SHALL executar `npm ci` seguido de `npm run build` no diretório `frontend/`
2. WHEN o build for concluído, THE Artefato_Frontend SHALL estar disponível no diretório `frontend/dist/` contendo os arquivos HTML, JS e CSS otimizados
3. WHEN o build do frontend for executado para um Ambiente específico, THE Pipeline_CI_CD SHALL configurar a variável de ambiente `VITE_API_URL` com a URL do API_Gateway correspondente ao Ambiente
4. IF o build do frontend falhar (código de saída diferente de zero), THEN THE Pipeline_CI_CD SHALL interromper o deploy e reportar o erro

### Requisito 6: Deploy do Backend via SAM

**User Story:** Como engenheiro DevOps, eu quero executar o deploy do backend com `sam deploy` parametrizado por ambiente, para que cada ambiente receba a configuração correta de forma automatizada.

#### Critérios de Aceitação

1. WHEN `sam deploy --config-env {ambiente}` for executado, THE SAM_Template SHALL criar ou atualizar a stack CloudFormation com os recursos definidos para o Ambiente especificado
2. THE processo de deploy SHALL utilizar parameter overrides para injetar DATABASE_URL, JWT_SECRET e demais variáveis sensíveis a partir de AWS Secrets Manager ou variáveis de ambiente do CI
3. WHEN o deploy for concluído, THE Pipeline_CI_CD SHALL verificar o status da stack CloudFormation e reportar sucesso ou falha
4. IF o deploy falhar (rollback da stack), THEN THE Pipeline_CI_CD SHALL capturar os eventos de erro do CloudFormation e exibi-los no log do workflow
5. WHEN o deploy for concluído com sucesso, THE Pipeline_CI_CD SHALL exibir a URL do API_Gateway como output

### Requisito 7: Deploy do Frontend para S3 e Invalidação de Cache

**User Story:** Como engenheiro DevOps, eu quero que o frontend compilado seja sincronizado com o Frontend_Bucket e o cache do CloudFront seja invalidado, para que os usuários acessem a versão mais recente da aplicação.

#### Critérios de Aceitação

1. WHEN o deploy do frontend for executado, THE Pipeline_CI_CD SHALL executar `aws s3 sync frontend/dist/ s3://{Frontend_Bucket} --delete` para sincronizar os arquivos estáticos
2. WHEN a sincronização S3 for concluída, THE Pipeline_CI_CD SHALL criar uma invalidação no CloudFront para o path `/*`
3. WHEN a invalidação for criada, THE Pipeline_CI_CD SHALL aguardar a conclusão da invalidação antes de reportar sucesso
4. IF a sincronização S3 falhar, THEN THE Pipeline_CI_CD SHALL interromper o processo e reportar o erro sem criar invalidação no CloudFront

### Requisito 8: Migrações de Banco de Dados com Flyway

**User Story:** Como engenheiro DevOps, eu quero que as migrações SQL sejam executadas automaticamente antes do deploy da aplicação, para que o schema do banco esteja sempre atualizado e compatível com o código sendo implantado.

#### Critérios de Aceitação

1. WHEN o deploy for iniciado para um Ambiente, THE Pipeline_CI_CD SHALL executar as migrações Flyway antes do deploy do backend
2. THE Flyway_Migration SHALL utilizar os scripts SQL versionados no diretório `database/` seguindo a convenção `V{versao}__{descricao}.sql`
3. WHEN a migração for executada, THE Flyway_Migration SHALL conectar ao banco MySQL RDS do Ambiente correspondente utilizando credenciais do AWS Secrets Manager
4. IF uma migração falhar, THEN THE Pipeline_CI_CD SHALL interromper o deploy completo (backend e frontend) e reportar o erro de migração
5. WHEN a migração for concluída com sucesso, THE Flyway_Migration SHALL registrar a versão aplicada na tabela de controle do Flyway (`flyway_schema_history`)

### Requisito 9: Workflow CI/CD com GitHub Actions

**User Story:** Como engenheiro DevOps, eu quero um workflow GitHub Actions que automatize o ciclo completo de build, teste e deploy, para que o processo de entrega seja confiável e repetível.

#### Critérios de Aceitação

1. WHEN um push for feito na branch `main`, THE Pipeline_CI_CD SHALL executar o deploy automático no Ambiente dev
2. WHEN um push for feito na branch `release/*`, THE Pipeline_CI_CD SHALL executar o deploy automático no Ambiente hml
3. WHEN uma tag no formato `v*.*.*` for criada, THE Pipeline_CI_CD SHALL executar o deploy no Ambiente prd com aprovação manual obrigatória via GitHub Environments
4. THE Pipeline_CI_CD SHALL executar testes automatizados do backend (`pytest`) antes de qualquer deploy, e interromper o processo se algum teste falhar
5. THE Pipeline_CI_CD SHALL executar lint do frontend (`npm run lint`) antes do build, e interromper o processo se houver erros
6. THE Pipeline_CI_CD SHALL configurar credenciais AWS via OIDC (OpenID Connect) com role assumida, sem utilizar access keys estáticas
7. THE Pipeline_CI_CD SHALL definir os secrets necessários como GitHub Secrets: `AWS_ROLE_ARN`, `DATABASE_URL_{ENV}`, `JWT_SECRET_{ENV}`
8. THE Pipeline_CI_CD SHALL executar as etapas na seguinte ordem: checkout, setup Python, setup Node.js, instalar dependências, executar testes, build backend (sam build), build frontend, migração Flyway, deploy backend (sam deploy), deploy frontend (s3 sync + CloudFront invalidation)

### Requisito 10: Promoção Multi-Ambiente

**User Story:** Como engenheiro DevOps, eu quero que a promoção entre ambientes siga o fluxo dev → hml → prd com controles de qualidade, para que apenas código validado chegue à produção.

#### Critérios de Aceitação

1. THE Pipeline_CI_CD SHALL garantir que o deploy em hml utilize o mesmo artefato (commit SHA) que foi validado em dev
2. THE Pipeline_CI_CD SHALL garantir que o deploy em prd utilize o mesmo artefato (commit SHA) que foi validado em hml
3. WHEN o deploy em prd for solicitado, THE Pipeline_CI_CD SHALL exigir aprovação manual de pelo menos um revisor configurado no GitHub Environment `production`
4. WHEN o deploy em qualquer Ambiente for concluído, THE Pipeline_CI_CD SHALL executar um health check no endpoint `/health` do API_Gateway e reportar o resultado
5. IF o health check falhar após o deploy, THEN THE Pipeline_CI_CD SHALL marcar o workflow como falho e notificar via output do GitHub Actions

### Requisito 11: Segurança e Permissões IAM

**User Story:** Como engenheiro de segurança, eu quero que as permissões IAM sigam o princípio de menor privilégio, para que a Lambda_Function tenha acesso apenas aos recursos necessários.

#### Critérios de Aceitação

1. THE Lambda_Execution_Role SHALL conceder permissão `logs:CreateLogGroup`, `logs:CreateLogStream` e `logs:PutLogEvents` para CloudWatch Logs
2. THE Lambda_Execution_Role SHALL conceder permissões `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject` e `s3:ListBucket` restritas ao bucket S3 de documentos do Ambiente correspondente
3. THE Lambda_Execution_Role SHALL conceder permissões de rede VPC (`ec2:CreateNetworkInterface`, `ec2:DescribeNetworkInterfaces`, `ec2:DeleteNetworkInterface`) para acesso ao RDS
4. THE Lambda_Execution_Role SHALL restringir o Resource de cada política ao ARN específico do recurso, sem utilizar wildcards (`*`) no nível de recurso
5. THE SAM_Template SHALL definir a política do Frontend_Bucket permitindo acesso somente via CloudFront_Distribution, sem acesso público direto
