GitHub:
  user: alberto-jam
  token: <SEU_TOKEN_AQUI>  # NUNCA commitar tokens reais — use variáveis de ambiente


aws cloudformation deploy \
--template-file AgroFlightOps-RDS-MySQL-S3.yaml \
--stack-name agrotech-dev-RDS-s3 \
--parameter-overrides file://AgroFlightOps-RDS-S3-dev-params.json \
--capabilities CAPABILITY_NAMED_IAM

Checklist de Deploy — AgroFlightOps na AWS
1. Pré-requisitos na conta AWS
 Verificar que a stack de infra existente (
AgroFlightOps-RDS-S3.yaml
) está deployada — RDS MySQL e S3 de documentos já rodando
 Anotar os valores: VPC Subnet IDs, Security Group IDs, nome do bucket S3 de documentos, endpoint do RDS
2. Configurar OIDC para GitHub Actions
 Criar o IAM Identity Provider no console AWS:
IAM → Identity providers → Add provider → OpenID Connect
Provider URL: https://token.actions.githubusercontent.com
Audience: sts.amazonaws.com
 Criar a IAM Role GitHubActions-AgroFlightOps-Deploy com:
Trust policy apontando para o OIDC provider e restrita ao seu repositório (repo:<org>/<repo>:*)
Permissões: CloudFormation, S3, Lambda, API Gateway, CloudFront, IAM (PassRole), CloudWatch Logs, EC2 (VPC/ENI)
3. Configurar GitHub Secrets e Variables
 Em Settings → Secrets and variables → Actions, criar os Secrets:
AWS_ROLE_ARN — ARN da role criada no passo 2
DATABASE_URL_DEV — mysql+aiomysql://user:pass@host:3306/dbname
JWT_SECRET_DEV — gerar com openssl rand -hex 32
(Repetir para HML e PRD quando necessário)
 Criar as Variables:
VPC_SUBNET_IDS_DEV — ex: subnet-xxx,subnet-yyy
VPC_SG_IDS_DEV — ex: sg-xxx
S3_DOCS_BUCKET_DEV — nome do bucket de documentos
CORS_ORIGINS_DEV — ex: http://localhost:5173
API_URL_DEV — preencher após o primeiro deploy (ou usar placeholder)
4. Configurar GitHub Environment para produção
 Settings → Environments → New environment → production
 Adicionar pelo menos 1 "Required reviewer" para aprovação manual de deploys em prd
5. Primeiro deploy (ambiente dev)
 Fazer push na branch main
 Acompanhar o workflow em Actions — ele vai:
Rodar testes (pytest + lint)
Build backend (sam build --use-container)
Build frontend (npm run build)
Flyway migrate (schema inicial)
sam deploy --config-env dev
S3 sync + CloudFront invalidation
Health check no /health
 Após sucesso, copiar a API URL do step summary e atualizar API_URL_DEV nas variables
6. Validação pós-deploy
 Acessar a URL do CloudFront — frontend deve carregar
 Testar curl {API_URL}/health — deve retornar {"status": "ok"}
 Verificar logs no CloudWatch (/aws/lambda/AgroFlightOps-dev-*)
 Verificar que flyway_schema_history foi criada no banco
7. Promoção para HML e PRD
 Criar secrets/variables para HML e PRD (mesma estrutura do dev)
 Para HML: criar branch 
x.y
 e fazer push
 Para PRD: criar tag v1.0.0 — workflow aguardará aprovação manual
Comece pelo passo 1 e vá marcando. O passo mais crítico é o 2 (OIDC) — sem ele o workflow não consegue autenticar com a AWS. Se travar em algum ponto, me chama.

======================================
Inserir primeiro administrador:

INSERT INTO perfis (nome, descricao) VALUES ('ADMINISTRADOR', 'Administrador do sistema')
ON DUPLICATE KEY UPDATE nome = nome;

-- Crie o usuário admin (senha: Admin@123 hasheada com bcrypt)
INSERT INTO usuarios (nome, email, senha_hash, perfil_id, ativo, created_at, updated_at)
VALUES (
  'Alberto Moreira',
  'admin@agroflightops.com',
  '$2b$12$LJ3m4ys3Lk0TSwHjfT8/.OB8JxKxGZGKl1L7VDBsGOIAU3p.8mOi6',
  (SELECT id FROM perfis WHERE nome = 'ADMINISTRADOR'),
  1,
  NOW(),
  NOW()
);
Email: admin@agroflightops.com
Senha: Admin@123