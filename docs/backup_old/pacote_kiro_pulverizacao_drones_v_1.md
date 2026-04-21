# Pacote de Implementação Orientado ao Kiro
## Sistema de Gestão de Serviços de Pulverização por Drones — V1

## 1. Decisões de arquitetura já fechadas

### 1.1. Objetivo do produto
Construir uma aplicação web operacional para gestão de serviços de pulverização por drones em plantações diversas, cobrindo o fluxo completo desde a Ordem de Serviço até o encerramento técnico e financeiro da missão.

### 1.2. Estratégia da V1
A V1 deve ser:
- operacionalmente completa
- manual-first
- com rastreabilidade média
- com geolocalização básica
- preparada para integrações futuras
- apta para rápida migração para produção

### 1.3. Engine do banco de dados
**Banco de dados obrigatório: PostgreSQL**

Justificativas:
- domínio transacional e relacional
- forte necessidade de integridade referencial
- boa evolução futura para geolocalização
- suporte confortável a JSON/GeoJSON se a V2 exigir
- melhor base para auditoria e histórico

### 1.4. Chaves e identificação
Padrão recomendado:
- `id`: UUID como chave técnica primária
- `codigo`: identificador funcional legível para entidades de negócio importantes

Exemplos:
- `OS-2026-000001`
- `MIS-2026-000001`

### 1.5. Convenções obrigatórias de modelagem
Todas as entidades principais devem conter, no mínimo:
- `id`
- `created_at`
- `updated_at`

Quando fizer sentido:
- `created_by`
- `updated_by`
- `ativo`

### 1.6. Estratégia de status
- armazenar status como texto controlado
- validar os valores no backend
- evitar dependência forte de enum nativo do banco na V1

---

## 2. Prompt mestre para o Kiro

Use o texto abaixo como prompt-base principal.

Desenvolva uma aplicação web completa para gestão de serviços de pulverização por drones em plantações, seguindo estritamente esta especificação.

Objetivo:
Construir a V1 operacional completa do sistema, com entrada manual de dados, rastreabilidade média, geolocalização básica e arquitetura preparada para integrações futuras.

Diretrizes obrigatórias:
- respeitar integralmente os perfis de usuário e permissões descritos
- implementar todos os módulos da V1
- implementar os estados e transições de status exatamente como definidos
- usar PostgreSQL como banco de dados principal
- usar UUID como chave primária técnica
- não inventar integrações externas na V1
- não simplificar o fluxo operacional
- não remover auditoria dos eventos críticos
- não fundir aprovação da OS com liberação da missão
- implementar geolocalização básica para Propriedade, Talhão e Missão
- permitir armazenamento manual de latitude e longitude
- exibir mapa incorporado por iframe quando houver coordenadas válidas
- não implementar GIS avançado, replay de voo, roteirização, telemetria em tempo real ou motor analítico geoespacial na V1
- preservar separação entre dados previstos e realizados
- preservar separação entre entidades operacionais, financeiras, de checklist e de auditoria

Entregáveis esperados:
- modelagem de dados coerente com o MER orientado
- backend com APIs organizadas por domínio
- frontend responsivo com dashboards e telas operacionais
- validações de regras de negócio
- persistência dos dados
- auditoria básica
- relatórios básicos
- componente reutilizável para exibição de mapa embutido

Importante:
Quando houver ambiguidade, priorize a regra de negócio mais conservadora, preserve a integridade operacional do sistema e mantenha a geolocalização em nível simples e funcional.

---

## 3. Escopo funcional consolidado da V1

A V1 deve cobrir o fluxo completo abaixo:
1. receber Ordem de Serviço
2. analisar e aprovar Ordem de Serviço
3. gerar missão a partir da OS aprovada
4. planejar missão
5. alocar piloto, drone, baterias e insumos
6. agendar missão
7. preencher checklist
8. aprovar tecnicamente a missão
9. liberar operacionalmente a missão
10. executar missão
11. registrar operação realizada
12. encerrar tecnicamente
13. encerrar financeiramente
14. consultar relatórios e dashboards básicos

---

## 4. Perfis de usuário

### 4.1. Administrador
Responsável por configuração geral, usuários, parâmetros, auditoria e ações excepcionais.

Permissões mínimas:
- CRUD de usuários
- CRUD de parâmetros mestres
- acesso total aos módulos
- reabertura excepcional de registros concluídos
- visualização de auditoria

### 4.2. Coordenador Operacional
Responsável pelo fluxo operacional.

Permissões mínimas:
- criar, editar e aprovar OS
- gerar e planejar missão
- alocar recursos
- agendar missão
- acompanhar execução
- liberar missão operacionalmente
- encerrar operacionalmente quando aplicável
- visualizar relatórios operacionais

### 4.3. Piloto
Responsável pela execução da missão.

Permissões mínimas:
- visualizar missões atribuídas
- preencher checklist
- iniciar, pausar, retomar e finalizar missão
- registrar consumo realizado
- registrar ocorrências
- anexar evidências

### 4.4. Técnico
Responsável pela validação técnica.

Permissões mínimas:
- revisar missão planejada
- aprovar tecnicamente a missão
- registrar observações técnicas
- encerrar tecnicamente a missão
- emitir relatório técnico

### 4.5. Financeiro
Responsável pelo fechamento financeiro.

Permissões mínimas:
- visualizar missões encerradas tecnicamente
- registrar custo realizado
- registrar valor faturado
- fechar financeiramente a missão
- emitir relatório financeiro

---

## 5. Estados obrigatórios

### 5.1. Ordem de Serviço
Valores obrigatórios:
- `RASCUNHO`
- `EM_ANALISE`
- `APROVADA`
- `REJEITADA`
- `CANCELADA`

### 5.2. Missão
Valores obrigatórios:
- `RASCUNHO`
- `PLANEJADA`
- `AGENDADA`
- `EM_CHECKLIST`
- `LIBERADA`
- `EM_EXECUCAO`
- `PAUSADA`
- `CONCLUIDA`
- `CANCELADA`
- `ENCERRADA_TECNICAMENTE`
- `ENCERRADA_FINANCEIRAMENTE`

### 5.3. Drone
Valores obrigatórios:
- `DISPONIVEL`
- `EM_USO`
- `EM_MANUTENCAO`
- `BLOQUEADO`
- `INATIVO`

### 5.4. Bateria
Valores obrigatórios:
- `DISPONIVEL`
- `EM_USO`
- `CARREGANDO`
- `REPROVADA`
- `DESCARTADA`

### 5.5. Status financeiro
Valores obrigatórios:
- `PENDENTE`
- `EM_FATURAMENTO`
- `FATURADO`
- `RECEBIDO`
- `CANCELADO`

---

## 6. MER textual orientado

### 6.1. Núcleo de acesso
- `usuarios`
- `perfis`

### 6.2. Núcleo cadastral
- `clientes`
- `propriedades`
- `talhoes`
- `culturas`
- `drones`
- `baterias`
- `insumos`
- `tipos_ocorrencia`
- `itens_checklist_padrao`

### 6.3. Núcleo operacional
- `ordens_servico`
- `historico_status_os`
- `missoes`
- `historico_status_missao`
- `missao_baterias`
- `reservas_insumo`
- `consumos_insumo_missao`
- `checklists_missao`
- `itens_checklist_missao`
- `ocorrencias`
- `evidencias`

### 6.4. Núcleo de ativos
- `manutencoes`

### 6.5. Núcleo financeiro
- `financeiro_missao`

### 6.6. Núcleo transversal
- `auditoria`

---

## 7. Cardinalidades principais

### 7.1. Cliente e Propriedade
- um `cliente` possui muitas `propriedades`
- uma `propriedade` pertence a um único `cliente`

### 7.2. Propriedade e Talhão
- uma `propriedade` possui muitos `talhoes`
- um `talhao` pertence a uma única `propriedade`

### 7.3. Cultura e Talhão
- uma `cultura` pode ser usada em muitos `talhoes`
- um `talhao` possui uma `cultura` principal na V1

### 7.4. Ordem de Serviço
- uma `ordem_servico` pertence a um `cliente`
- uma `ordem_servico` pertence a uma `propriedade`
- uma `ordem_servico` pertence a um `talhao`
- uma `ordem_servico` pertence a uma `cultura`

### 7.5. Ordem de Serviço e Missão
- uma `ordem_servico` pode possuir muitas `missoes`
- uma `missao` pertence a uma única `ordem_servico`

Observação de arquitetura:
Na V1, a interface pode trabalhar normalmente com uma missão por OS, mas o modelo deve permitir múltiplas missões futuras.

### 7.6. Missão e usuários
- uma `missao` possui um `piloto`
- uma `missao` pode possuir um `tecnico`

### 7.7. Missão e Drone
- uma `missao` utiliza um `drone`
- um `drone` pode participar de muitas `missoes` ao longo do tempo

### 7.8. Missão e Bateria
- relação N:N por `missao_baterias`

### 7.9. Missão e Insumos
- previstos em `reservas_insumo`
- realizados em `consumos_insumo_missao`
- manter separação obrigatória entre previsto e realizado

### 7.10. Missão e Checklist
- uma `missao` possui um `checklists_missao`
- um `checklists_missao` possui muitos `itens_checklist_missao`

### 7.11. Missão e Ocorrências
- uma `missao` pode possuir muitas `ocorrencias`

### 7.12. Missão e Evidências
- uma `missao` pode possuir muitas `evidencias`

### 7.13. Missão e Financeiro
- uma `missao` possui um `financeiro_missao`

### 7.14. Drone e Manutenção
- um `drone` pode possuir muitas `manutencoes`

---

## 8. Especificação lógica das entidades principais

### 8.1. usuarios
Campos mínimos:
- `id`
- `nome`
- `email`
- `senha_hash`
- `perfil_id`
- `ativo`
- `created_at`
- `updated_at`

### 8.2. perfis
Campos mínimos:
- `id`
- `nome`
- `descricao`
- `ativo`

Perfis iniciais obrigatórios:
- ADMINISTRADOR
- COORDENADOR_OPERACIONAL
- PILOTO
- TECNICO
- FINANCEIRO

### 8.3. clientes
Campos mínimos:
- `id`
- `nome`
- `cpf_cnpj`
- `telefone`
- `email`
- `endereco`
- `numero`
- `complemento`
- `bairro`
- `municipio`
- `estado`
- `cep`
- `latitude` opcional
- `longitude` opcional
- `referencia_local` opcional
- `ativo`
- `created_at`
- `updated_at`

### 8.4. propriedades
Campos mínimos:
- `id`
- `cliente_id`
- `nome`
- `endereco` opcional
- `numero` opcional
- `complemento` opcional
- `bairro` opcional
- `municipio`
- `estado`
- `cep` opcional
- `localizacao_descritiva`
- `referencia_local` opcional
- `latitude` opcional
- `longitude` opcional
- `area_total`
- `ativo`
- `created_at`
- `updated_at`

### 8.5. culturas
Campos mínimos:
- `id`
- `nome`
- `descricao`
- `ativo`
- `created_at`
- `updated_at`

### 8.6. talhoes
Campos mínimos:
- `id`
- `propriedade_id`
- `nome`
- `area_hectares`
- `cultura_id`
- `observacoes`
- `latitude` opcional
- `longitude` opcional
- `ponto_referencia` opcional
- `geojson` opcional
- `ativo`
- `created_at`
- `updated_at`

### 8.7. drones
Campos mínimos:
- `id`
- `identificacao`
- `modelo`
- `fabricante`
- `capacidade_litros`
- `status`
- `horas_voadas`
- `ultima_manutencao_em` opcional
- `ativo`
- `created_at`
- `updated_at`

### 8.8. baterias
Campos mínimos:
- `id`
- `identificacao`
- `drone_id` opcional
- `ciclos`
- `status`
- `observacoes`
- `ativo`
- `created_at`
- `updated_at`

### 8.9. insumos
Campos mínimos:
- `id`
- `nome`
- `fabricante`
- `unidade_medida`
- `saldo_atual`
- `lote` opcional
- `validade` opcional
- `ativo`
- `created_at`
- `updated_at`

### 8.10. ordens_servico
Campos mínimos:
- `id`
- `codigo`
- `cliente_id`
- `propriedade_id`
- `talhao_id`
- `cultura_id`
- `tipo_aplicacao`
- `prioridade`
- `descricao`
- `data_prevista`
- `status`
- `motivo_rejeicao` opcional
- `motivo_cancelamento` opcional
- `criado_por`
- `aprovado_por` opcional
- `created_at`
- `updated_at`

### 8.11. historico_status_os
Campos mínimos:
- `id`
- `ordem_servico_id`
- `status_anterior` opcional
- `status_novo`
- `motivo` opcional
- `alterado_por`
- `created_at`

### 8.12. missoes
Campos mínimos:
- `id`
- `codigo`
- `ordem_servico_id`
- `piloto_id`
- `tecnico_id` opcional
- `drone_id`
- `data_agendada`
- `hora_agendada`
- `area_prevista`
- `area_realizada` opcional
- `volume_previsto`
- `volume_realizado` opcional
- `janela_operacional`
- `restricoes`
- `observacoes_planejamento`
- `observacoes_execucao`
- `status`
- `latitude_operacao` opcional
- `longitude_operacao` opcional
- `endereco_operacao` opcional
- `referencia_operacao` opcional
- `iniciado_em` opcional
- `finalizado_em` opcional
- `encerrado_tecnicamente_em` opcional
- `encerrado_financeiramente_em` opcional
- `created_at`
- `updated_at`

### 8.13. historico_status_missao
Campos mínimos:
- `id`
- `missao_id`
- `status_anterior` opcional
- `status_novo`
- `motivo` opcional
- `alterado_por`
- `created_at`

### 8.14. missao_baterias
Campos mínimos:
- `id`
- `missao_id`
- `bateria_id`
- `ordem_uso`
- `created_at`

### 8.15. reservas_insumo
Campos mínimos:
- `id`
- `missao_id`
- `insumo_id`
- `quantidade_prevista`
- `unidade_medida`
- `justificativa_excesso` opcional
- `created_at`

### 8.16. consumos_insumo_missao
Campos mínimos:
- `id`
- `missao_id`
- `insumo_id`
- `quantidade_realizada`
- `unidade_medida`
- `observacoes`
- `justificativa_excesso` opcional
- `created_at`

### 8.17. checklists_missao
Campos mínimos:
- `id`
- `missao_id`
- `status_geral`
- `preenchido_por`
- `revisado_por` opcional
- `preenchido_em`
- `revisado_em` opcional
- `observacoes`
- `created_at`
- `updated_at`

### 8.18. itens_checklist_padrao
Campos mínimos:
- `id`
- `nome_item`
- `descricao` opcional
- `obrigatorio`
- `ativo`
- `ordem_exibicao`
- `created_at`
- `updated_at`

### 8.19. itens_checklist_missao
Campos mínimos:
- `id`
- `checklist_id`
- `nome_item`
- `obrigatorio`
- `status_item`
- `observacao`
- `created_at`
- `updated_at`

Valores obrigatórios para `status_item`:
- `PENDENTE`
- `APROVADO`
- `REPROVADO`
- `NAO_APLICAVEL`

### 8.20. tipos_ocorrencia
Campos mínimos:
- `id`
- `nome`
- `descricao`
- `ativo`
- `created_at`
- `updated_at`

### 8.21. ocorrencias
Campos mínimos:
- `id`
- `missao_id`
- `tipo_ocorrencia_id`
- `descricao`
- `severidade`
- `registrada_por`
- `registrada_em`
- `created_at`
- `updated_at`

### 8.22. evidencias
Campos mínimos:
- `id`
- `missao_id`
- `nome_arquivo`
- `url_arquivo`
- `tipo_arquivo`
- `latitude` opcional
- `longitude` opcional
- `enviado_por`
- `created_at`

### 8.23. manutencoes
Campos mínimos:
- `id`
- `drone_id`
- `tipo`
- `descricao`
- `data_manutencao`
- `proxima_manutencao` opcional
- `horas_na_data` opcional
- `created_at`
- `updated_at`

### 8.24. financeiro_missao
Campos mínimos:
- `id`
- `missao_id`
- `custo_estimado`
- `custo_realizado`
- `valor_faturado`
- `status_financeiro`
- `observacoes`
- `fechado_por` opcional
- `fechado_em` opcional
- `created_at`
- `updated_at`

### 8.25. auditoria
Campos mínimos:
- `id`
- `entidade`
- `entidade_id`
- `acao`
- `valor_anterior` opcional
- `valor_novo` opcional
- `usuario_id`
- `created_at`

---

## 9. Regras de negócio obrigatórias

### 9.1. Ordem de Serviço
- não aprovar OS incompleta
- rejeição exige motivo
- cancelamento exige motivo
- não gerar missão a partir de OS não aprovada

### 9.2. Missão
- missão só nasce de OS aprovada
- missão sem piloto não pode ser agendada
- missão sem drone não pode ser agendada
- missão sem checklist completo não pode ser liberada
- missão sem aprovação técnica não pode ser liberada
- missão concluída não pode voltar para rascunho
- missão encerrada financeiramente só pode ser alterada por administrador

### 9.3. Drone
- drone em manutenção não pode ser alocado
- drone bloqueado não pode ser alocado
- ao iniciar missão, drone passa para `EM_USO`
- ao encerrar missão, drone volta para `DISPONIVEL`, salvo bloqueio posterior

### 9.4. Bateria
- bateria reprovada ou descartada não pode ser vinculada à missão
- bateria em uso não pode ser associada simultaneamente a missão conflitante

### 9.5. Insumos
- consumo realizado deve ser armazenado separadamente da reserva
- consumo maior que o previsto exige justificativa
- insumo inativo não pode ser reservado

### 9.6. Checklist
- checklist incompleto bloqueia liberação
- item reprovado exige observação

### 9.7. Fechamentos
- encerramento técnico depende de missão concluída
- encerramento financeiro depende de encerramento técnico
- toda reabertura deve gerar auditoria

### 9.8. Geolocalização
- latitude válida entre -90 e 90
- longitude válida entre -180 e 180
- sistema deve funcionar sem coordenadas cadastradas
- mapa só deve ser exibido quando coordenadas forem válidas

---

## 10. Módulos e responsabilidades técnicas

### 10.1. Autenticação e autorização
- login
- logout
- controle de sessão
- RBAC simples por perfil
- proteção de rotas e ações

### 10.2. Cadastros mestres
- clientes
- propriedades
- talhões
- culturas
- drones
- baterias
- usuários
- insumos
- tipos de ocorrência
- itens de checklist padrão

### 10.3. Ordem de Serviço
- CRUD
- aprovação
- rejeição
- cancelamento
- histórico
- geração de missão

### 10.4. Planejamento de missão
- criação a partir de OS aprovada
- parâmetros técnicos
- previsão de área e volume
- insumos previstos
- restrições
- localização operacional

### 10.5. Agenda e alocação
- alocar piloto
- alocar drone
- alocar baterias
- reservar insumos
- agendar missão
- detectar conflitos

### 10.6. Checklist e liberação
- gerar checklist da missão
- preencher checklist
- revisar tecnicamente
- liberar operacionalmente

### 10.7. Execução operacional
- iniciar
- pausar
- retomar
- registrar realizado
- registrar ocorrências
- anexar evidências
- finalizar

### 10.8. Frota e ativos
- status do drone
- manutenção
- histórico básico de uso
- controle de baterias

### 10.9. Financeiro
- custo estimado
- custo realizado
- valor faturado
- status financeiro
- fechamento financeiro

### 10.10. Relatórios
- operacional
- técnico
- financeiro
- produtividade por piloto
- produtividade por drone
- consumo por missão
- horas voadas por drone

### 10.11. Auditoria
- rastrear alteração crítica
- exibir histórico básico por registro

---

## 11. Diretrizes de frontend

### 11.1. Tecnologia
O Kiro pode escolher a organização do frontend, mas deve produzir:
- aplicação web responsiva
- foco desktop para administrativo
- foco tablet/mobile para execução de campo

### 11.2. Telas obrigatórias
- login
- dashboard por perfil
- CRUD de clientes
- CRUD de propriedades
- CRUD de talhões
- CRUD de culturas
- CRUD de drones
- CRUD de baterias
- CRUD de insumos
- lista e detalhe de OS
- formulário de OS
- lista e detalhe de missão
- planejamento de missão
- checklist de missão
- execução de missão
- tela de frota/manutenção
- tela financeira
- relatórios

### 11.3. Mapas
Criar componente reutilizável `LocationMapEmbed` com:
- `latitude`
- `longitude`
- `title`
- `height` opcional
- `fallbackText` opcional

Comportamento:
- renderizar iframe apenas com coordenadas válidas
- exibir texto de fallback quando não houver coordenadas
- reutilizar em Propriedade, Talhão e Missão

---

## 12. Diretrizes de backend

### 12.1. Organização por domínio
Separar os módulos por contexto de negócio, preferencialmente:
- auth
- users
- cadastros
- ordens_servico
- missoes
- checklist
- execucao
- frota
- financeiro
- relatorios
- auditoria

### 12.2. API
A API deve expor endpoints claros por recurso e ação de negócio.

Exemplos mínimos esperados:
- CRUD padrão para cadastros
- endpoints de transição de status para OS e Missão
- endpoints específicos para checklist, alocação, execução e fechamento
- endpoints de dashboard e relatórios básicos

### 12.3. Validação
Toda regra crítica deve ser validada no backend, independentemente do frontend.

---

## 13. O que o Kiro pode decidir

O Kiro pode decidir:
- ORM e estratégia de mapeamento
- estrutura de migrations
- nome de alguns índices e FKs
- organização interna de services/controllers/repositories
- DTOs, schemas e serializers
- convenções de componentes frontend
- paginação e filtros detalhados
- estrutura de upload de arquivos

---

## 14. O que o Kiro não pode decidir livremente

O Kiro não deve alterar sem instrução:
- engine PostgreSQL
- uso de UUID como chave técnica principal
- entidades definidas no MER base
- cardinalidades principais
- separação entre OS e Missão
- separação entre reserva e consumo real de insumo
- separação entre checklist, financeiro e auditoria
- estados obrigatórios
- necessidade de histórico de status
- necessidade de auditoria
- geolocalização básica nas entidades definidas

---

## 15. Backlog orientado por épicos e histórias

### Épico 1 — Fundação técnica
**Objetivo:** preparar a base da aplicação.

Histórias:
1. Como administrador, quero autenticar no sistema para acessar funcionalidades autorizadas.
2. Como sistema, quero controlar permissões por perfil para restringir ações conforme o papel do usuário.
3. Como equipe técnica, queremos uma estrutura com PostgreSQL, migrations e seed inicial para suportar evolução segura.
4. Como sistema, quero registrar auditoria básica para alterações críticas.

### Épico 2 — Cadastros mestres
**Objetivo:** disponibilizar os dados-base do domínio.

Histórias:
1. Como administrador, quero cadastrar usuários e perfis.
2. Como coordenador, quero cadastrar clientes.
3. Como coordenador, quero cadastrar propriedades com geolocalização opcional.
4. Como coordenador, quero cadastrar talhões com geolocalização opcional.
5. Como coordenador, quero cadastrar culturas.
6. Como coordenador, quero cadastrar drones e seu status.
7. Como coordenador, quero cadastrar baterias.
8. Como coordenador, quero cadastrar insumos.
9. Como administrador, quero cadastrar tipos de ocorrência e itens padrão de checklist.

### Épico 3 — Ordem de Serviço
**Objetivo:** iniciar o fluxo operacional.

Histórias:
1. Como coordenador, quero criar uma OS com cliente, propriedade, talhão e cultura.
2. Como coordenador, quero enviar a OS para análise.
3. Como usuário autorizado, quero aprovar ou rejeitar a OS.
4. Como usuário autorizado, quero cancelar a OS com motivo.
5. Como coordenador, quero visualizar histórico de status da OS.

### Épico 4 — Planejamento da missão
**Objetivo:** converter uma OS aprovada em uma missão executável.

Histórias:
1. Como coordenador, quero gerar missão a partir de OS aprovada.
2. Como coordenador, quero informar área prevista, volume previsto, janela operacional e restrições.
3. Como coordenador, quero informar localização operacional da missão.
4. Como coordenador, quero registrar insumos previstos.

### Épico 5 — Alocação e agenda
**Objetivo:** preparar recursos e agenda.

Histórias:
1. Como coordenador, quero alocar piloto à missão.
2. Como coordenador, quero alocar drone à missão.
3. Como coordenador, quero associar baterias à missão.
4. Como coordenador, quero reservar insumos para a missão.
5. Como coordenador, quero agendar data e hora da missão.
6. Como sistema, quero alertar conflitos de agenda de piloto ou drone.

### Épico 6 — Checklist e liberação
**Objetivo:** controlar prontidão da missão.

Histórias:
1. Como piloto, quero preencher checklist da missão.
2. Como sistema, quero impedir liberação com checklist incompleto.
3. Como técnico, quero aprovar tecnicamente a missão.
4. Como coordenador, quero liberar operacionalmente a missão.

### Épico 7 — Execução operacional
**Objetivo:** registrar o realizado em campo.

Histórias:
1. Como piloto, quero iniciar a missão.
2. Como piloto, quero pausar e retomar a missão com motivo.
3. Como piloto, quero registrar área e volume realizados.
4. Como piloto, quero registrar consumo real de insumos.
5. Como piloto, quero registrar ocorrências.
6. Como piloto, quero anexar evidências.
7. Como piloto, quero finalizar a missão.

### Épico 8 — Frota e ativos
**Objetivo:** manter controle básico sobre recursos operacionais.

Histórias:
1. Como coordenador, quero acompanhar horas voadas por drone.
2. Como coordenador, quero registrar manutenção de drone.
3. Como sistema, quero bloquear alocação de drone indisponível.
4. Como sistema, quero bloquear uso de bateria reprovada ou descartada.

### Épico 9 — Encerramento técnico e financeiro
**Objetivo:** concluir a missão formalmente.

Histórias:
1. Como técnico, quero encerrar tecnicamente missão concluída.
2. Como financeiro, quero registrar custo realizado.
3. Como financeiro, quero registrar valor faturado.
4. Como financeiro, quero fechar financeiramente a missão.
5. Como sistema, quero impedir fechamento financeiro antes do encerramento técnico.

### Épico 10 — Relatórios e dashboards
**Objetivo:** disponibilizar visão gerencial mínima.

Histórias:
1. Como coordenador, quero ver OS por status.
2. Como coordenador, quero ver missões por status.
3. Como gestor, quero ver área aplicada no período.
4. Como gestor, quero ver produtividade por piloto e por drone.
5. Como gestor, quero ver horas voadas por drone.
6. Como financeiro, quero ver receita, custo e margem por missão.
7. Como gestor, quero consultar ocorrências por tipo.

---

## 16. Sequência recomendada de implementação

### Fase 1
- fundação técnica
- autenticação e autorização
- cadastros mestres

### Fase 2
- ordem de serviço
- planejamento de missão
- agenda e alocação

### Fase 3
- checklist e liberação
- execução operacional
- upload básico de evidências

### Fase 4
- frota/manutenção
- encerramento técnico
- encerramento financeiro

### Fase 5
- dashboards
- relatórios
- refinamentos de UX

---

## 17. Critérios de aceite consolidados

A V1 será considerada pronta quando permitir:
1. autenticação com perfis distintos
2. cadastro de usuários, clientes, propriedades, talhões, culturas, drones, baterias, insumos, tipos de ocorrência e itens padrão de checklist
3. criação, aprovação, rejeição e cancelamento de OS
4. geração de missão a partir de OS aprovada
5. planejamento da missão com área, volume, restrições, geolocalização e insumos previstos
6. alocação de piloto, drone e baterias
7. agendamento da missão
8. preenchimento e conclusão do checklist
9. aprovação técnica e liberação operacional
10. execução manual completa da missão
11. registro de consumo real, ocorrências e evidências
12. encerramento técnico
13. encerramento financeiro
14. visualização de dashboards e relatórios básicos
15. exibição de mapas embutidos quando houver coordenadas válidas
16. bloqueio de transições inválidas
17. respeito às permissões por perfil
18. auditoria básica de eventos críticos

---

## 18. Instrução final para uso com Kiro

Usar este pacote como base mandatória. A geração deve respeitar o domínio, o fluxo operacional, o MER orientado e as regras de negócio definidas. O foco é obter uma V1 sólida, clara e pronta para crescer sem retrabalho estrutural.

