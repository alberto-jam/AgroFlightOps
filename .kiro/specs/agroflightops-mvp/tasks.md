# Plano de Implementação: AgroFlightOps MVP

## Visão Geral

Implementação incremental do sistema AgroFlightOps — gestão de operações de pulverização agrícola com drones. O backend é Python/FastAPI sobre AWS Lambda, banco MySQL 8.0 (RDS), armazenamento S3. O frontend é React/Vite/TypeScript. O DDL já existe em `database/AgroFlightOps_RDS_MySQL_ddl.sql` e deve ser respeitado integralmente.

Cada tarefa referencia requisitos específicos do documento de requisitos e propriedades de corretude do documento de design.

## Tarefas

- [x] 1. Estrutura do projeto backend, configuração e modelos ORM
  - [x] 1.1 Criar estrutura de diretórios do backend e dependências
    - Criar `app/` com subpastas `api/`, `services/`, `repositories/`, `models/`, `schemas/`, `core/`
    - Criar `requirements.txt` com FastAPI, uvicorn, SQLAlchemy, aiomysql, pydantic, passlib[bcrypt], python-jose[cryptography], boto3, mangum, python-multipart, hypothesis
    - Criar `app/main.py` com FastAPI app + Mangum handler para Lambda
    - _Requisitos: 19.1, 19.2, 20.2_

  - [x] 1.2 Implementar módulo de configuração e conexão com banco
    - Criar `app/core/config.py` com Settings (env vars: DATABASE_URL, JWT_SECRET, S3_BUCKET, etc.)
    - Criar `app/core/database.py` com engine SQLAlchemy, SessionLocal, get_db dependency
    - _Requisitos: 20.3_

  - [x] 1.3 Criar modelos SQLAlchemy mapeando todas as tabelas do DDL
    - Mapear 1:1 todas as tabelas de `database/AgroFlightOps_RDS_MySQL_ddl.sql`
    - Incluir: perfis, usuarios, clientes, propriedades, talhoes, culturas, drones, baterias, insumos, tipos_ocorrencia, itens_checklist_padrao, ordens_servico, historico_status_os, missoes, historico_status_missao, missao_baterias, reservas_insumo, consumos_insumo_missao, checklists_missao, itens_checklist_missao, ocorrencias, evidencias, manutencoes, financeiro_missao, auditoria, documentos_oficiais
    - Respeitar tipos, constraints, defaults e relacionamentos do DDL
    - _Requisitos: 20.3_

  - [x] 1.4 Criar exceções customizadas e handler global de erros
    - Criar `app/core/exceptions.py` com EntityNotFoundError, DuplicateEntityError, InvalidStateTransitionError, BusinessRuleViolationError, InsufficientStockError, DependencyActiveError
    - Registrar exception handlers no FastAPI app para mapear exceções → códigos HTTP (404, 409, 422)
    - Garantir formato de resposta JSON padronizado: `{"detail": "...", "errors": [...]}`
    - _Requisitos: 19.2, 19.4, 19.5_

  - [x] 1.5 Implementar repositório base genérico com paginação
    - Criar `app/repositories/base_repository.py` com CRUD genérico (create, get_by_id, list_paginated, update, soft_delete)
    - Implementar paginação com parâmetros `page` e `page_size` (default 20, max 100)
    - Retornar `PaginatedResponse` com items, total, page, page_size, pages
    - _Requisitos: 19.3_

  - [x] 1.6 Criar schemas Pydantic base (request/response) para todas as entidades
    - Criar `app/schemas/` com Base, Create, Update e Response para cada entidade
    - Criar `PaginatedResponse[T]` genérico
    - Validar campos obrigatórios, tipos e constraints (min/max, enums)
    - _Requisitos: 19.4_

- [x] 2. Autenticação, segurança e RBAC
  - [x] 2.1 Implementar módulo de segurança JWT e bcrypt
    - Criar `app/core/security.py` com funções: hash_password, verify_password (bcrypt), create_access_token, decode_token (python-jose)
    - Token JWT com claims: sub (usuario_id), perfil, email, exp, iat
    - _Requisitos: 1.1, 1.3_

  - [x] 2.2 Implementar dependencies de autenticação e autorização
    - Criar `app/core/dependencies.py` com get_current_user (extrai JWT do header Authorization: Bearer)
    - Criar require_perfil(*perfis) dependency que verifica perfil do usuário
    - Retornar 401 para token ausente/inválido/expirado, 403 para perfil não autorizado
    - _Requisitos: 1.4, 1.5_

  - [x] 2.3 Implementar auth_service e rotas de login/refresh
    - Criar `app/services/auth_service.py` com login (valida email+senha, verifica ativo, retorna JWT)
    - Criar `app/api/auth.py` com POST /auth/login e POST /auth/refresh
    - Mensagem de erro genérica para credenciais inválidas (sem revelar qual campo falhou)
    - Bloquear login de usuários com ativo=FALSE
    - _Requisitos: 1.1, 1.2, 1.6_

  - [ ]* 2.4 Testes de propriedade — Autenticação
    - **Propriedade 1: Round-trip de senha com bcrypt**
    - **Valida: Requisitos 1.3, 2.1**

  - [ ]* 2.5 Testes de propriedade — Credenciais inválidas
    - **Propriedade 3: Credenciais inválidas retornam erro genérico**
    - **Valida: Requisitos 1.2**

  - [ ]* 2.6 Testes de propriedade — Usuário desativado
    - **Propriedade 4: Usuário desativado não consegue autenticar**
    - **Valida: Requisitos 1.6, 2.3**

  - [ ]* 2.7 Testes de propriedade — RBAC
    - **Propriedade 2: RBAC — Matriz de permissões**
    - **Valida: Requisitos 1.5**

- [x] 3. CRUD de entidades base (Usuários, Clientes, Culturas)
  - [x] 3.1 Implementar CRUD de Usuários (service + repository + rotas)
    - Criar `app/repositories/usuario_repository.py`, `app/services/usuario_service.py`, `app/api/usuarios.py`
    - Validar unicidade de email (HTTP 409 se duplicado)
    - Soft-delete (ativo=FALSE) sem excluir registro
    - Listagem paginada com filtros por perfil e status
    - Apenas perfil Administrador pode acessar
    - _Requisitos: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 3.2 Implementar CRUD de Clientes (service + repository + rotas)
    - Criar `app/repositories/cliente_repository.py`, `app/services/cliente_service.py`, `app/api/clientes.py`
    - Validar coordenadas geográficas (lat [-90,90], lon [-180,180])
    - Proteção de desativação: impedir se Cliente tem OS não-CANCELADA
    - Listagem paginada com filtros por nome, CPF/CNPJ, status
    - Perfis: Administrador, Coordenador_Operacional
    - _Requisitos: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 3.3 Implementar CRUD de Culturas (service + repository + rotas)
    - Criar `app/repositories/cultura_repository.py`, `app/services/cultura_service.py`, `app/api/culturas.py`
    - Validar unicidade do nome (HTTP 409)
    - Proteção de desativação: impedir se Cultura tem Talhões ativos
    - Listagem com filtro por status ativo
    - Perfis: Administrador, Coordenador_Operacional
    - _Requisitos: 5.1, 5.2, 5.3, 5.4_

  - [ ]* 3.4 Testes de propriedade — Soft-delete
    - **Propriedade 5: Soft-delete preserva registro**
    - **Valida: Requisitos 2.3, 3.4, 5.3**

  - [ ]* 3.5 Testes de propriedade — Unicidade
    - **Propriedade 6: Unicidade de identificadores**
    - **Valida: Requisitos 2.1, 2.5, 4.2, 5.1, 6.1, 7.1**

  - [ ]* 3.6 Testes de propriedade — Coordenadas geográficas
    - **Propriedade 7: Validação de coordenadas geográficas**
    - **Valida: Requisitos 3.2, 4.1**

  - [ ]* 3.7 Testes de propriedade — Proteção de desativação
    - **Propriedade 8: Proteção de desativação com dependências ativas**
    - **Valida: Requisitos 3.5, 4.6, 5.4, 6.6**

- [x] 4. Checkpoint — Verificar base do projeto
  - Garantir que todos os testes passam, perguntar ao usuário se houver dúvidas.

- [x] 5. CRUD de Propriedades, Talhões, Drones, Baterias e Insumos
  - [x] 5.1 Implementar CRUD de Propriedades (service + repository + rotas)
    - Criar `app/repositories/propriedade_repository.py`, `app/services/propriedade_service.py`, `app/api/propriedades.py`
    - Associar a Cliente existente, validar campos obrigatórios (nome, município, estado, area_total)
    - Validar coordenadas geográficas quando informadas
    - Listagem filtrada por Cliente, município, estado
    - Perfis: Administrador, Coordenador_Operacional
    - _Requisitos: 4.1, 4.3_

  - [x] 5.2 Implementar CRUD de Talhões (service + repository + rotas)
    - Criar `app/repositories/talhao_repository.py`, `app/services/talhao_service.py`, `app/api/talhoes.py`
    - Validar unicidade (propriedade_id, nome), area_hectares >= 0, associar Cultura válida
    - Aceitar e armazenar GeoJSON para perímetro
    - Proteção de desativação: impedir se Talhão tem OS não-CANCELADA
    - Listagem filtrada por Propriedade e Cultura
    - Perfis: Administrador, Coordenador_Operacional
    - _Requisitos: 4.2, 4.4, 4.5, 4.6_

  - [x] 5.3 Implementar CRUD de Drones (service + repository + rotas)
    - Criar `app/repositories/drone_repository.py`, `app/services/drone_service.py`, `app/api/drones.py`
    - Validar unicidade de identificação, capacidade_litros >= 0, status inicial DISPONIVEL
    - Proteção: impedir INATIVO/EM_MANUTENCAO se Drone tem Missões EM_EXECUCAO ou AGENDADA
    - Listagem filtrada por status e modelo
    - Perfil: Administrador
    - _Requisitos: 6.1, 6.2, 6.3, 6.4, 6.6_

  - [x] 5.4 Implementar CRUD de Baterias (service + repository + rotas)
    - Criar `app/repositories/bateria_repository.py`, `app/services/bateria_service.py`, `app/api/baterias.py`
    - Validar unicidade de identificação, ciclos inicial 0, associação opcional a Drone
    - Impedir associação a Missão se status REPROVADA ou DESCARTADA
    - Listagem filtrada por status e Drone
    - Perfil: Administrador
    - _Requisitos: 7.1, 7.2, 7.4, 7.5_

  - [x] 5.5 Implementar CRUD de Insumos (service + repository + rotas)
    - Criar `app/repositories/insumo_repository.py`, `app/services/insumo_service.py`, `app/api/insumos.py`
    - Validar saldo_atual >= 0
    - Listagem filtrada por nome, lote, status ativo
    - Perfis: Administrador, Coordenador_Operacional
    - _Requisitos: 8.1, 8.2, 8.5_

  - [ ]* 5.6 Testes de propriedade — Validação de enums
    - **Propriedade 9: Validação de enums de status**
    - **Valida: Requisitos 6.2, 7.2, 9.2, 9.3, 10.2, 13.2, 15.3, 16.4**

  - [ ]* 5.7 Testes de propriedade — GeoJSON round-trip
    - **Propriedade 32: GeoJSON round-trip**
    - **Valida: Requisitos 4.5**

  - [ ]* 5.8 Testes de propriedade — Bateria impedida
    - **Propriedade 24: Bateria REPROVADA/DESCARTADA não pode ser associada a missão**
    - **Valida: Requisitos 7.5**

- [x] 6. Checkpoint — Verificar CRUDs base
  - Garantir que todos os testes passam, perguntar ao usuário se houver dúvidas.

- [x] 7. Ordens de Serviço — CRUD e máquina de estados
  - [x] 7.1 Implementar CRUD de Ordens de Serviço (service + repository + rotas)
    - Criar `app/repositories/ordem_servico_repository.py`, `app/services/ordem_servico_service.py`, `app/api/ordens_servico.py`
    - Gerar código único, associar Cliente/Propriedade/Talhão/Cultura, status inicial RASCUNHO, registrar criado_por
    - Listagem paginada com filtros por status, cliente, propriedade, prioridade, data_prevista
    - Perfis: Administrador, Coordenador_Operacional
    - _Requisitos: 9.1, 9.2, 9.3, 9.9_

  - [x] 7.2 Implementar máquina de estados de OS com transições e histórico
    - Implementar endpoint PATCH `/ordens-servico/{id}/transicao`
    - Transições válidas: RASCUNHO→EM_ANALISE, EM_ANALISE→APROVADA, EM_ANALISE→REJEITADA, {RASCUNHO,EM_ANALISE,APROVADA}→CANCELADA
    - Exigir motivo_rejeicao para REJEITADA, motivo_cancelamento para CANCELADA
    - Registrar aprovado_por ao aprovar
    - Criar registro em historico_status_os a cada transição (status_anterior, status_novo, motivo, alterado_por)
    - _Requisitos: 9.4, 9.5, 9.6, 9.7, 9.8_

  - [ ]* 7.3 Testes de propriedade — Máquina de estados OS
    - **Propriedade 10: Máquina de estados de Ordem de Serviço**
    - **Valida: Requisitos 9.4, 9.5, 9.6, 9.7**

  - [ ]* 7.4 Testes de propriedade — Histórico de transições
    - **Propriedade 11: Histórico de transições de status**
    - **Valida: Requisitos 9.8, 10.6**

- [x] 8. Missões — CRUD, máquina de estados e ciclo Drone
  - [x] 8.1 Implementar CRUD de Missões (service + repository + rotas)
    - Criar `app/repositories/missao_repository.py`, `app/services/missao_service.py`, `app/api/missoes.py`
    - Gerar código único, associar a OS APROVADA (rejeitar se outro status), alocar Piloto/Drone/Técnico
    - Validar area_prevista >= 0, volume_previsto >= 0
    - Status inicial RASCUNHO
    - Listagem paginada com filtros por status, piloto, drone, data_agendada, ordem_servico
    - Perfis: Administrador, Coordenador_Operacional, Piloto, Técnico
    - _Requisitos: 10.1, 10.2, 10.7, 10.8_

  - [x] 8.2 Implementar máquina de estados de Missão com ciclo Drone
    - Implementar endpoint PATCH `/missoes/{id}/transicao`
    - Transições conforme diagrama de estados do design
    - Ao transitar para EM_EXECUCAO: registrar iniciado_em, alterar Drone para EM_USO
    - Ao transitar para CONCLUIDA: registrar finalizado_em (>= iniciado_em), alterar Drone para DISPONIVEL
    - Registrar historico_status_missao a cada transição
    - _Requisitos: 10.3, 10.4, 10.5, 10.6_

  - [x] 8.3 Implementar associação de Baterias a Missões
    - Criar endpoint para associar baterias (missao_baterias) com ordem_uso
    - Validar que bateria não está REPROVADA/DESCARTADA
    - _Requisitos: 7.3, 7.5_

  - [x] 8.4 Implementar reservas de insumo para Missões
    - Criar endpoint para registrar reservas_insumo (quantidade_prevista, unidade_medida)
    - _Requisitos: 8.3_

  - [ ]* 8.5 Testes de propriedade — Missão requer OS APROVADA
    - **Propriedade 12: Missão só pode ser criada para OS APROVADA**
    - **Valida: Requisitos 10.1**

  - [ ]* 8.6 Testes de propriedade — Ciclo Drone-Missão
    - **Propriedade 13: Ciclo de vida Drone-Missão**
    - **Valida: Requisitos 6.3, 10.3, 10.4, 10.5**

- [x] 9. Checkpoint — Verificar OS e Missões
  - Garantir que todos os testes passam, perguntar ao usuário se houver dúvidas.

- [x] 10. Checklist de Missão
  - [x] 10.1 Implementar checklist_service e rotas de checklist
    - Criar `app/services/checklist_service.py`, `app/api/checklists.py`
    - Ao transitar Missão para EM_CHECKLIST: criar checklist com status PENDENTE, copiar itens de itens_checklist_padrao ativos
    - Endpoint para preencher itens (APROVADO, REPROVADO, NAO_APLICAVEL)
    - Exigir observação para item obrigatório REPROVADO
    - Permitir CONCLUIDO somente se todos obrigatórios são APROVADO ou NAO_APLICAVEL
    - Endpoint para Técnico aprovar checklist → status APROVADO, registrar revisado_por/revisado_em, liberar Missão para LIBERADA
    - Impedir aprovação se item obrigatório REPROVADO
    - Perfis: Piloto (preenchimento), Técnico (aprovação)
    - _Requisitos: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6_

  - [ ]* 10.2 Testes de propriedade — Checklist bloqueia/libera
    - **Propriedade 14: Checklist bloqueia/libera missão**
    - **Valida: Requisitos 11.4, 11.5, 11.6**

  - [ ]* 10.3 Testes de propriedade — Item reprovado exige observação
    - **Propriedade 15: Item obrigatório reprovado exige observação**
    - **Valida: Requisitos 11.3**

- [x] 11. Execução de Missão, Consumo de Insumos e Ocorrências
  - [x] 11.1 Implementar registro de execução de Missão
    - Permitir atualização de area_realizada, volume_realizado, observacoes_execucao apenas quando status EM_EXECUCAO
    - Validar que area_realizada e volume_realizado estão preenchidos ao concluir
    - _Requisitos: 12.1, 12.4_

  - [x] 11.2 Implementar consumo de insumos durante Missão
    - Criar endpoint para registrar consumos_insumo_missao
    - Debitar saldo_atual do insumo (rejeitar se saldo ficaria negativo)
    - Exigir justificativa_excesso se quantidade_realizada > quantidade_prevista da reserva
    - Permitir apenas quando Missão em EM_EXECUCAO
    - _Requisitos: 8.4, 8.6, 12.3, 12.5_

  - [x] 11.3 Implementar registro de Ocorrências
    - Criar `app/services/ocorrencia_service.py`, `app/api/ocorrencias.py`
    - Permitir registro apenas quando Missão em EM_EXECUCAO ou PAUSADA
    - Validar severidade (BAIXA, MEDIA, ALTA, CRITICA)
    - Registrar timestamp e piloto responsável
    - Listagem filtrada por Missão, tipo, severidade
    - _Requisitos: 13.1, 13.2, 13.3, 13.4_

  - [x] 11.4 Implementar upload de Evidências
    - Criar `app/services/evidencia_service.py`, `app/api/evidencias.py`
    - Upload de arquivos com metadados de geolocalização
    - Armazenar no S3, registrar metadados no banco
    - Permitir apenas quando Missão em EM_EXECUCAO
    - _Requisitos: 12.2_

  - [ ]* 11.5 Testes de propriedade — Invariante de saldo de insumo
    - **Propriedade 16: Invariante de saldo de insumo**
    - **Valida: Requisitos 8.4, 8.6**

  - [ ]* 11.6 Testes de propriedade — Excesso exige justificativa
    - **Propriedade 17: Excesso de consumo exige justificativa**
    - **Valida: Requisitos 12.5**

  - [ ]* 11.7 Testes de propriedade — Execução restrita a status
    - **Propriedade 18: Registro de execução restrito a EM_EXECUCAO**
    - **Valida: Requisitos 12.1, 12.3, 13.1**

  - [ ]* 11.8 Testes de propriedade — Conclusão exige dados
    - **Propriedade 19: Conclusão de missão exige dados de execução**
    - **Valida: Requisitos 12.4, 10.8**

- [x] 12. Checkpoint — Verificar fluxo operacional completo
  - Garantir que todos os testes passam, perguntar ao usuário se houver dúvidas.

- [x] 13. Manutenção de Drones
  - [x] 13.1 Implementar CRUD de Manutenções (service + repository + rotas)
    - Criar `app/repositories/manutencao_repository.py`, `app/services/manutencao_service.py`, `app/api/manutencoes.py`
    - Associar ao Drone, registrar tipo, descrição, data_manutencao, horas_na_data
    - Atualizar ultima_manutencao_em do Drone com data_manutencao
    - Validar proxima_manutencao >= data_manutencao quando informada
    - Alterar status do Drone para EM_MANUTENCAO quando aplicável
    - Listagem filtrada por Drone e período
    - Perfis: Administrador, Técnico
    - _Requisitos: 14.1, 14.2, 14.3, 14.4, 14.5_

  - [ ]* 13.2 Testes de propriedade — Manutenção atualiza drone
    - **Propriedade 30: Manutenção atualiza drone**
    - **Valida: Requisitos 14.2, 14.3, 14.5**

  - [ ]* 13.3 Testes de propriedade — Horas voadas e ciclos
    - **Propriedade 31: Incremento de horas voadas e ciclos de bateria**
    - **Valida: Requisitos 6.5, 7.3**

- [x] 14. Documentos Oficiais
  - [x] 14.1 Implementar gestão de Documentos Oficiais (service + repository + rotas)
    - Criar `app/services/documento_service.py`, `app/api/documentos_oficiais.py`
    - Upload para S3 com metadados (content_type, s3_key, bucket_s3, tipo_documento, entidade, entidade_id)
    - Entidades permitidas: DRONE, MANUTENCAO, USUARIO, CLIENTE, PROPRIEDADE, INSUMO, MISSAO
    - Substituição automática: ao enviar novo documento do mesmo tipo/entidade, marcar anterior como SUBSTITUIDO
    - Verificação de vencimento: marcar como VENCIDO se data_validade < data atual
    - Download via URL pré-assinada do S3 com validade limitada
    - Listagem filtrada por entidade, entidade_id, tipo_documento, status
    - Perfil upload: Administrador; Download: Autenticado
    - _Requisitos: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7_

  - [ ]* 14.2 Testes de propriedade — Substituição de documento
    - **Propriedade 22: Substituição de documento marca anterior como SUBSTITUIDO**
    - **Valida: Requisitos 15.5**

  - [ ]* 14.3 Testes de propriedade — Documento vencido
    - **Propriedade 23: Documento vencido é marcado automaticamente**
    - **Valida: Requisitos 15.4**

- [x] 15. Encerramento Técnico e Financeiro
  - [x] 15.1 Implementar encerramento técnico de Missão
    - Transição CONCLUIDA → ENCERRADA_TECNICAMENTE
    - Registrar encerrado_tecnicamente_em
    - Criar registro em financeiro_missao com status_financeiro PENDENTE
    - _Requisitos: 16.1, 16.2_

  - [x] 15.2 Implementar gestão financeira de Missão (service + rotas)
    - Criar `app/services/financeiro_service.py`, `app/api/financeiro.py`
    - Registrar custo_estimado, custo_realizado, valor_faturado (todos >= 0)
    - Status financeiro: PENDENTE, EM_FATURAMENTO, FATURADO, RECEBIDO, CANCELADO
    - Encerramento financeiro: alterar Missão para ENCERRADA_FINANCEIRAMENTE, registrar timestamps e fechado_por
    - Perfis: Financeiro, Administrador
    - _Requisitos: 16.3, 16.4, 16.5_

  - [ ]* 15.3 Testes de propriedade — Encerramento técnico cria financeiro
    - **Propriedade 20: Encerramento técnico cria registro financeiro**
    - **Valida: Requisitos 16.1, 16.2**

  - [ ]* 15.4 Testes de propriedade — Valores financeiros não-negativos
    - **Propriedade 21: Valores financeiros não-negativos**
    - **Valida: Requisitos 16.3**

- [x] 16. Auditoria
  - [x] 16.1 Implementar serviço de auditoria centralizado
    - Criar `app/services/auditoria_service.py`, `app/api/auditoria.py`
    - Registrar automaticamente operações CUD em entidades principais
    - Armazenar entidade, entidade_id, ação, valor_anterior (JSON), valor_novo (JSON), usuario_id
    - Para criações: valor_anterior = NULL
    - Para atualizações: valor_anterior e valor_novo refletem valores reais
    - Integrar chamadas de auditoria nos services existentes (usuario, cliente, cultura, propriedade, talhao, drone, bateria, insumo, ordem_servico, missao, documento)
    - Endpoint de consulta filtrado por entidade, entidade_id, usuário, período
    - Perfil: Administrador
    - _Requisitos: 17.1, 17.2, 17.3_

  - [ ]* 16.2 Testes de propriedade — Auditoria CUD
    - **Propriedade 25: Auditoria registra operações CUD com JSON**
    - **Valida: Requisitos 17.1, 17.3**

- [x] 17. Checkpoint — Verificar módulos complementares
  - Garantir que todos os testes passam, perguntar ao usuário se houver dúvidas.

- [x] 18. Relatórios Operacionais e Financeiros
  - [x] 18.1 Implementar endpoints de relatórios
    - Criar `app/services/relatorio_service.py`, `app/api/relatorios.py`
    - Relatório de Missões por status em período especificado
    - Relatório de área total pulverizada por período e por Cliente
    - Relatório financeiro (custo_estimado, custo_realizado, valor_faturado) por período — apenas Missões ENCERRADA_FINANCEIRAMENTE
    - Relatório de utilização de Drones (horas voadas) por período
    - Perfis: Administrador, Financeiro
    - _Requisitos: 18.1, 18.2, 18.3, 18.4, 18.5_

  - [ ]* 18.2 Testes de propriedade — Relatórios agregação
    - **Propriedade 26: Relatórios filtram e agregam corretamente**
    - **Valida: Requisitos 18.1, 18.2, 18.3, 18.5**

- [x] 19. Validações transversais e paginação
  - [x] 19.1 Revisar e garantir validações transversais em todos os endpoints
    - Verificar que todos os endpoints retornam 422 com detalhamento para dados inválidos
    - Verificar que todos os endpoints retornam 404 para IDs inexistentes
    - Verificar consistência de paginação em todos os endpoints de listagem
    - _Requisitos: 19.4, 19.5_

  - [ ]* 19.2 Testes de propriedade — Paginação consistente
    - **Propriedade 27: Paginação consistente**
    - **Valida: Requisitos 19.3**

  - [ ]* 19.3 Testes de propriedade — Validação 422
    - **Propriedade 28: Validação retorna 422 com detalhamento**
    - **Valida: Requisitos 19.4**

  - [ ]* 19.4 Testes de propriedade — 404 inexistente
    - **Propriedade 29: Recurso inexistente retorna 404**
    - **Valida: Requisitos 19.5**

- [x] 20. Checkpoint — Verificar backend completo
  - Garantir que todos os testes passam, perguntar ao usuário se houver dúvidas.

- [x] 21. Frontend — Estrutura base, autenticação e navegação
  - [x] 21.1 Criar projeto React/Vite/TypeScript e estrutura de diretórios
    - Inicializar projeto com Vite + React + TypeScript
    - Criar estrutura: `src/api/`, `src/auth/`, `src/pages/`, `src/components/`, `src/hooks/`, `src/types/`, `src/utils/`
    - Instalar dependências: axios, react-router-dom, ant-design ou MUI
    - _Requisitos: 20.1_

  - [x] 21.2 Implementar cliente API com interceptors JWT
    - Criar `src/api/client.ts` com Axios, base URL configurável, interceptor para adicionar Bearer token, interceptor para refresh automático
    - _Requisitos: 1.1, 1.4_

  - [x] 21.3 Implementar contexto de autenticação e rotas protegidas
    - Criar `src/auth/AuthContext.tsx` com estado de autenticação, login, logout
    - Criar `src/auth/ProtectedRoute.tsx` com guard por perfil
    - Criar `src/auth/useAuth.ts` hook
    - Criar `src/pages/Login.tsx`
    - _Requisitos: 1.1, 1.5_

  - [x] 21.4 Implementar layout principal e navegação
    - Criar layout com sidebar/menu baseado no perfil do usuário
    - Configurar react-router-dom com rotas para todas as páginas
    - _Requisitos: 1.5_

- [x] 22. Frontend — Componentes reutilizáveis
  - [x] 22.1 Criar componentes reutilizáveis base
    - `src/components/DataTable.tsx` — tabela paginada genérica com filtros
    - `src/components/StatusBadge.tsx` — badge colorido por status
    - `src/components/FormModal.tsx` — modal de formulário genérico (criar/editar)
    - `src/components/FileUpload.tsx` — upload de arquivos
    - `src/components/GeoLocationPicker.tsx` — seletor de coordenadas
    - _Requisitos: 19.3_

  - [x] 22.2 Criar tipos TypeScript para todas as entidades
    - Criar `src/types/` com interfaces para cada entidade (matching schemas Pydantic)
    - Incluir PaginatedResponse<T> genérico
    - _Requisitos: 19.2_

- [x] 23. Frontend — Páginas CRUD de entidades base
  - [x] 23.1 Implementar páginas de Usuários, Clientes e Culturas
    - `src/pages/Usuarios.tsx` — listagem paginada, criar, editar, ativar/desativar
    - `src/pages/Clientes.tsx` — listagem paginada com filtros, criar, editar, desativar
    - `src/pages/Culturas.tsx` — listagem, criar, editar, desativar
    - _Requisitos: 2.1–2.5, 3.1–3.5, 5.1–5.4_

  - [x] 23.2 Implementar páginas de Propriedades, Talhões, Drones, Baterias e Insumos
    - `src/pages/Propriedades.tsx` — listagem filtrada por Cliente, criar, editar
    - `src/pages/Talhoes.tsx` — listagem filtrada por Propriedade, criar com GeoJSON, editar
    - `src/pages/Drones.tsx` — listagem filtrada por status, criar, editar
    - `src/pages/Baterias.tsx` — listagem filtrada por status/Drone, criar, editar
    - `src/pages/Insumos.tsx` — listagem filtrada, criar, editar
    - _Requisitos: 4.1–4.6, 6.1–6.6, 7.1–7.5, 8.1–8.6_

- [x] 24. Frontend — Ordens de Serviço e Missões
  - [x] 24.1 Implementar página de Ordens de Serviço
    - `src/pages/OrdensServico.tsx` — listagem paginada com filtros, criar, editar, transições de status com confirmação
    - Exibir histórico de transições
    - Formulário de rejeição/cancelamento com campo de motivo obrigatório
    - _Requisitos: 9.1–9.9_

  - [x] 24.2 Implementar página de Missões
    - `src/pages/Missoes.tsx` — listagem paginada com filtros, criar (selecionar OS APROVADA), transições de status
    - Exibir histórico de transições
    - Associação de baterias e reservas de insumo
    - _Requisitos: 10.1–10.8_

  - [x] 24.3 Implementar página de Checklists
    - `src/pages/Checklists.tsx` — preenchimento de itens, aprovação/reprovação, campo de observação para reprovados
    - Indicação visual de itens obrigatórios
    - Botão de aprovação do checklist (Técnico)
    - _Requisitos: 11.1–11.6_

- [x] 25. Frontend — Execução, Ocorrências, Manutenções e Documentos
  - [x] 25.1 Implementar tela de execução de Missão
    - Formulário para registrar area_realizada, volume_realizado, observações
    - Upload de evidências com metadados de geolocalização
    - Registro de consumo de insumos com justificativa de excesso
    - Registro de ocorrências com tipo e severidade
    - _Requisitos: 12.1–12.5, 13.1–13.4_

  - [x] 25.2 Implementar páginas de Manutenções e Documentos Oficiais
    - Página de Manutenções com listagem filtrada por Drone/período, criar, editar
    - Página de Documentos Oficiais com upload, listagem filtrada, download
    - _Requisitos: 14.1–14.5, 15.1–15.7_

- [x] 26. Frontend — Financeiro, Relatórios, Auditoria e Dashboard
  - [x] 26.1 Implementar tela de encerramento financeiro
    - Formulário para custo_estimado, custo_realizado, valor_faturado
    - Transições de status financeiro
    - _Requisitos: 16.1–16.5_

  - [x] 26.2 Implementar página de Relatórios
    - `src/pages/Relatorios.tsx` — seleção de tipo de relatório, filtros por período/cliente
    - Gráficos com componentes Charts (missões por status, área pulverizada, financeiro, utilização drones)
    - _Requisitos: 18.1–18.5_

  - [x] 26.3 Implementar página de Auditoria
    - `src/pages/Auditoria.tsx` — listagem filtrada por entidade, usuário, período
    - Exibição de valor_anterior/valor_novo em JSON formatado
    - _Requisitos: 17.1–17.3_

  - [x] 26.4 Implementar Dashboard principal
    - `src/pages/Dashboard.tsx` — indicadores resumidos (OS por status, Missões ativas, Drones disponíveis, alertas de documentos vencidos)
    - _Requisitos: 18.1–18.4_

- [x] 27. Checkpoint — Verificar frontend completo
  - Garantir que todos os testes passam, perguntar ao usuário se houver dúvidas.

- [x] 28. Integração final e testes de configuração
  - [x] 28.1 Configurar Mangum handler e empacotamento Lambda
    - Garantir que `app/main.py` exporta handler Mangum corretamente
    - Configurar CORS para permitir requisições do frontend S3
    - _Requisitos: 20.2_

  - [x] 28.2 Criar conftest.py e factories para testes
    - Criar `tests/conftest.py` com fixtures compartilhadas (TestClient, banco em memória/mock, sessão de teste)
    - Criar `tests/factories.py` com Hypothesis strategies para todas as entidades
    - Configurar profiles Hypothesis (ci: 100 exemplos, dev: 30 exemplos)
    - _Requisitos: 19.1_

  - [x] 28.3 Testes de integração S3
    - Testar upload/download de documentos com mock S3 (moto)
    - Testar geração de URLs pré-assinadas
    - _Requisitos: 15.1, 15.7_

- [x] 29. Checkpoint final — Verificar sistema completo
  - Garantir que todos os testes passam, perguntar ao usuário se houver dúvidas.

## Notas

- Tarefas marcadas com `*` são opcionais e podem ser puladas para um MVP mais rápido
- Cada tarefa referencia requisitos específicos para rastreabilidade
- Checkpoints garantem validação incremental
- Testes de propriedade validam propriedades universais de corretude (Hypothesis)
- Testes unitários validam exemplos específicos e edge cases
- O DDL existente em `database/AgroFlightOps_RDS_MySQL_ddl.sql` é a fonte de verdade para o schema
- As regras de banco em `docs/DATABASE_RULES.md` devem ser seguidas
