# Documento de Requisitos — AgroFlightOps MVP

## Introdução

O AgroFlightOps é um sistema web para gestão completa de operações de pulverização agrícola com drones. O MVP contempla controle de ordens de serviço, planejamento e execução de missões, gestão de drones e pilotos, armazenamento de documentos oficiais e relatórios operacionais/financeiros. A arquitetura é baseada em serviços AWS com frontend React/TypeScript, backend Python/FastAPI e banco MySQL 8.0 (Amazon RDS).

## Glossário

- **Sistema**: A aplicação web AgroFlightOps como um todo (frontend + backend + infraestrutura AWS)
- **API**: O backend REST implementado em Python/FastAPI, hospedado em AWS Lambda via API Gateway
- **Frontend**: A aplicação React/Vite/TypeScript hospedada em S3 como site estático
- **Usuário**: Pessoa cadastrada no sistema com perfil e credenciais de acesso
- **Administrador**: Perfil com controle total da aplicação
- **Piloto**: Perfil que executa missões e registra resultados
- **Técnico**: Perfil responsável por planejamento e validação técnica de missões
- **Financeiro**: Perfil que consulta e gerencia informações financeiras
- **Coordenador_Operacional**: Perfil que gerencia ordens de serviço e missões
- **Cliente**: Pessoa física ou jurídica contratante dos serviços de pulverização
- **Propriedade**: Imóvel rural pertencente a um Cliente
- **Talhão**: Subdivisão de uma Propriedade com cultura específica e área definida
- **Cultura**: Tipo de plantio cultivado em um Talhão (ex: soja, milho, café)
- **Drone**: Aeronave remotamente pilotada utilizada nas operações de pulverização
- **Bateria**: Componente de energia associado a um Drone
- **Insumo**: Produto químico ou biológico utilizado na pulverização
- **Ordem_de_Serviço**: Solicitação formal de serviço de pulverização vinculada a um Cliente, Propriedade e Talhão
- **Missão**: Operação de voo planejada e executada a partir de uma Ordem de Serviço aprovada
- **Checklist**: Lista de verificação obrigatória preenchida antes da execução de uma Missão
- **Ocorrência**: Evento não planejado registrado durante a execução de uma Missão
- **Evidência**: Arquivo (foto, vídeo, documento) anexado como prova de execução de uma Missão
- **Documento_Oficial**: Arquivo regulatório armazenado no S3 (registro ANAC, licença de piloto, etc.)
- **Manutenção**: Registro de serviço de manutenção realizado em um Drone
- **Financeiro_Missão**: Registro de custos e faturamento associado a uma Missão

## Requisitos

### Requisito 1: Autenticação e Controle de Acesso

**User Story:** Como um Usuário, eu quero me autenticar no sistema com email e senha, para que eu possa acessar as funcionalidades de acordo com meu perfil.

#### Critérios de Aceitação

1. WHEN um Usuário submete credenciais válidas (email e senha), THE API SHALL retornar um token JWT com validade definida e os dados do perfil do Usuário
2. WHEN um Usuário submete credenciais inválidas, THE API SHALL retornar código HTTP 401 com mensagem de erro genérica sem revelar qual campo está incorreto
3. THE API SHALL armazenar senhas utilizando hash bcrypt com salt
4. WHEN um token JWT expirado é enviado em uma requisição, THE API SHALL retornar código HTTP 401 e o Frontend SHALL redirecionar o Usuário para a tela de login
5. WHILE um Usuário está autenticado, THE API SHALL validar o perfil do Usuário em cada requisição e restringir acesso apenas às rotas permitidas para o perfil correspondente
6. WHEN um Administrador desativa a conta de um Usuário, THE Sistema SHALL impedir login futuro desse Usuário e invalidar sessões ativas

### Requisito 2: Gestão de Usuários

**User Story:** Como um Administrador, eu quero cadastrar, editar, ativar e desativar usuários do sistema, para que eu possa controlar quem tem acesso e com qual perfil.

#### Critérios de Aceitação

1. WHEN um Administrador cria um novo Usuário, THE API SHALL validar unicidade do email, associar um perfil válido e armazenar a senha com hash bcrypt
2. WHEN um Administrador edita um Usuário existente, THE API SHALL atualizar os campos permitidos e registrar a alteração no campo updated_at
3. WHEN um Administrador desativa um Usuário, THE API SHALL definir o campo ativo como FALSE sem excluir o registro
4. THE API SHALL retornar lista paginada de Usuários com filtros por perfil e status (ativo/inativo)
5. IF um Administrador tenta criar um Usuário com email já existente, THEN THE API SHALL retornar código HTTP 409 com mensagem indicando duplicidade

### Requisito 3: Gestão de Clientes

**User Story:** Como um Coordenador_Operacional, eu quero cadastrar e gerenciar clientes, para que eu possa associar ordens de serviço aos contratantes corretos.

#### Critérios de Aceitação

1. WHEN um Coordenador_Operacional cria um novo Cliente, THE API SHALL validar formato de CPF/CNPJ (quando informado), armazenar dados de endereço e geolocalização, e retornar o registro criado
2. WHEN coordenadas de latitude e longitude são informadas, THE API SHALL validar que latitude está entre -90 e 90 e longitude está entre -180 e 180
3. THE API SHALL retornar lista paginada de Clientes com filtros por nome, CPF/CNPJ e status ativo
4. WHEN um Coordenador_Operacional desativa um Cliente, THE API SHALL definir o campo ativo como FALSE sem excluir o registro
5. IF um Cliente possui Ordens de Serviço com status diferente de CANCELADA, THEN THE API SHALL impedir a desativação e retornar mensagem informativa

### Requisito 4: Gestão de Propriedades e Talhões

**User Story:** Como um Coordenador_Operacional, eu quero cadastrar propriedades rurais e seus talhões, para que eu possa vincular ordens de serviço a áreas específicas de aplicação.

#### Critérios de Aceitação

1. WHEN um Coordenador_Operacional cria uma Propriedade, THE API SHALL associar a Propriedade a um Cliente existente, validar campos obrigatórios (nome, município, estado, area_total) e validar coordenadas geográficas quando informadas
2. WHEN um Coordenador_Operacional cria um Talhão, THE API SHALL associar o Talhão a uma Propriedade existente, validar unicidade do nome dentro da Propriedade, validar area_hectares maior ou igual a zero e associar uma Cultura válida
3. THE API SHALL retornar lista de Propriedades filtrada por Cliente, município e estado
4. THE API SHALL retornar lista de Talhões filtrada por Propriedade e Cultura
5. WHEN coordenadas geográficas são informadas para Talhão, THE API SHALL aceitar e armazenar dados GeoJSON para representação do perímetro
6. IF um Talhão possui Ordens de Serviço vinculadas com status diferente de CANCELADA, THEN THE API SHALL impedir a desativação do Talhão

### Requisito 5: Gestão de Culturas

**User Story:** Como um Coordenador_Operacional, eu quero cadastrar tipos de cultura agrícola, para que eu possa associar culturas aos talhões e ordens de serviço.

#### Critérios de Aceitação

1. WHEN um Coordenador_Operacional cria uma Cultura, THE API SHALL validar unicidade do nome e armazenar o registro
2. THE API SHALL retornar lista de Culturas com filtro por status ativo
3. WHEN um Coordenador_Operacional desativa uma Cultura, THE API SHALL definir o campo ativo como FALSE
4. IF uma Cultura está associada a Talhões ativos, THEN THE API SHALL impedir a desativação e retornar mensagem informativa

### Requisito 6: Gestão de Drones

**User Story:** Como um Administrador, eu quero cadastrar e gerenciar drones da frota, para que eu possa controlar disponibilidade, status e histórico de manutenção.

#### Critérios de Aceitação

1. WHEN um Administrador cadastra um Drone, THE API SHALL validar unicidade da identificação, validar capacidade_litros maior ou igual a zero e definir status inicial como DISPONIVEL
2. THE API SHALL permitir os seguintes valores de status para Drone: DISPONIVEL, EM_USO, EM_MANUTENCAO, BLOQUEADO, INATIVO
3. WHEN o status de um Drone é alterado para EM_USO, THE API SHALL validar que o Drone estava previamente com status DISPONIVEL
4. THE API SHALL retornar lista de Drones com filtros por status e modelo
5. WHEN um Drone acumula horas de voo após uma Missão concluída, THE API SHALL incrementar o campo horas_voadas do Drone
6. IF um Drone possui Missões com status EM_EXECUCAO ou AGENDADA, THEN THE API SHALL impedir alteração de status para INATIVO ou EM_MANUTENCAO

### Requisito 7: Gestão de Baterias

**User Story:** Como um Administrador, eu quero cadastrar e gerenciar baterias dos drones, para que eu possa controlar ciclos de uso e disponibilidade.

#### Critérios de Aceitação

1. WHEN um Administrador cadastra uma Bateria, THE API SHALL validar unicidade da identificação, associar opcionalmente a um Drone e definir ciclos inicial como zero
2. THE API SHALL permitir os seguintes valores de status para Bateria: DISPONIVEL, EM_USO, CARREGANDO, REPROVADA, DESCARTADA
3. WHEN uma Bateria é utilizada em uma Missão, THE API SHALL incrementar o contador de ciclos da Bateria
4. THE API SHALL retornar lista de Baterias com filtros por status e Drone associado
5. IF uma Bateria possui status REPROVADA ou DESCARTADA, THEN THE API SHALL impedir associação da Bateria a novas Missões

### Requisito 8: Gestão de Insumos

**User Story:** Como um Coordenador_Operacional, eu quero cadastrar e controlar o estoque de insumos, para que eu possa planejar reservas para missões e rastrear consumo.

#### Critérios de Aceitação

1. WHEN um Coordenador_Operacional cadastra um Insumo, THE API SHALL armazenar nome, fabricante, unidade_medida, saldo_atual, lote e validade
2. THE API SHALL validar que saldo_atual é maior ou igual a zero
3. WHEN uma reserva de Insumo é criada para uma Missão, THE API SHALL registrar quantidade_prevista e unidade_medida
4. WHEN o consumo real de Insumo é registrado após uma Missão, THE API SHALL atualizar o saldo_atual do Insumo subtraindo a quantidade_realizada
5. THE API SHALL retornar lista de Insumos com filtros por nome, lote e status ativo
6. IF o saldo_atual de um Insumo ficar abaixo de zero após consumo, THEN THE API SHALL rejeitar o registro de consumo e retornar mensagem de saldo insuficiente

### Requisito 9: Gestão de Ordens de Serviço

**User Story:** Como um Coordenador_Operacional, eu quero criar e gerenciar ordens de serviço, para que eu possa formalizar solicitações de pulverização e controlar o fluxo de aprovação.

#### Critérios de Aceitação

1. WHEN um Coordenador_Operacional cria uma Ordem_de_Serviço, THE API SHALL gerar código único, associar Cliente, Propriedade, Talhão e Cultura, definir status inicial como RASCUNHO e registrar o criador
2. THE API SHALL permitir os seguintes valores de status para Ordem_de_Serviço: RASCUNHO, EM_ANALISE, APROVADA, REJEITADA, CANCELADA
3. THE API SHALL permitir os seguintes valores de prioridade: BAIXA, MEDIA, ALTA, CRITICA
4. WHEN uma Ordem_de_Serviço é submetida para análise, THE API SHALL alterar status de RASCUNHO para EM_ANALISE
5. WHEN um Administrador aprova uma Ordem_de_Serviço, THE API SHALL alterar status para APROVADA e registrar o aprovador
6. WHEN um Administrador rejeita uma Ordem_de_Serviço, THE API SHALL exigir preenchimento do campo motivo_rejeicao e alterar status para REJEITADA
7. WHEN uma Ordem_de_Serviço é cancelada, THE API SHALL exigir preenchimento do campo motivo_cancelamento e alterar status para CANCELADA
8. WHEN o status de uma Ordem_de_Serviço é alterado, THE API SHALL registrar a transição no histórico (historico_status_os) com status anterior, status novo, motivo e usuário responsável
9. THE API SHALL retornar lista paginada de Ordens de Serviço com filtros por status, cliente, propriedade, prioridade e data_prevista

### Requisito 10: Gestão de Missões

**User Story:** Como um Coordenador_Operacional, eu quero criar e gerenciar missões de voo, para que eu possa planejar, agendar e acompanhar a execução das operações de pulverização.

#### Critérios de Aceitação

1. WHEN um Coordenador_Operacional cria uma Missão, THE API SHALL gerar código único, associar a uma Ordem_de_Serviço com status APROVADA, alocar Piloto, Drone e opcionalmente Técnico, e definir status inicial como RASCUNHO
2. THE API SHALL permitir os seguintes valores de status para Missão: RASCUNHO, PLANEJADA, AGENDADA, EM_CHECKLIST, LIBERADA, EM_EXECUCAO, PAUSADA, CONCLUIDA, CANCELADA, ENCERRADA_TECNICAMENTE, ENCERRADA_FINANCEIRAMENTE
3. WHEN uma Missão é agendada, THE API SHALL validar que data_agendada e hora_agendada estão preenchidas e que o Drone alocado possui status DISPONIVEL
4. WHEN uma Missão transita para EM_EXECUCAO, THE API SHALL registrar o timestamp em iniciado_em e alterar o status do Drone para EM_USO
5. WHEN uma Missão transita para CONCLUIDA, THE API SHALL registrar o timestamp em finalizado_em, validar que finalizado_em é posterior a iniciado_em e alterar o status do Drone para DISPONIVEL
6. WHEN o status de uma Missão é alterado, THE API SHALL registrar a transição no histórico (historico_status_missao) com status anterior, status novo, motivo e usuário responsável
7. THE API SHALL retornar lista paginada de Missões com filtros por status, piloto, drone, data_agendada e ordem_servico
8. WHEN uma Missão é criada, THE API SHALL validar que area_prevista e volume_previsto são maiores ou iguais a zero

### Requisito 11: Checklist de Missão

**User Story:** Como um Piloto, eu quero preencher o checklist pré-voo da missão, para que eu possa garantir que todas as condições de segurança estão atendidas antes da execução.

#### Critérios de Aceitação

1. WHEN uma Missão transita para status EM_CHECKLIST, THE API SHALL criar um registro de Checklist com status_geral PENDENTE e copiar os itens do checklist padrão (itens_checklist_padrao) ativos
2. WHEN um Piloto preenche um item do Checklist, THE API SHALL registrar o status_item como APROVADO, REPROVADO ou NAO_APLICAVEL
3. IF um item obrigatório é marcado como REPROVADO, THEN THE API SHALL exigir preenchimento do campo observacao
4. WHEN todos os itens obrigatórios do Checklist estão com status APROVADO ou NAO_APLICAVEL, THE API SHALL permitir transição do status_geral para CONCLUIDO
5. WHEN um Técnico revisa e aprova o Checklist, THE API SHALL alterar status_geral para APROVADO, registrar revisado_por e revisado_em, e permitir transição da Missão para LIBERADA
6. IF algum item obrigatório do Checklist possui status REPROVADO, THEN THE API SHALL impedir aprovação do Checklist e manter a Missão no status EM_CHECKLIST

### Requisito 12: Registro de Execução de Missão

**User Story:** Como um Piloto, eu quero registrar os dados de execução da missão (área realizada, volume aplicado, evidências), para que eu possa documentar a operação realizada.

#### Critérios de Aceitação

1. WHILE uma Missão está com status EM_EXECUCAO, THE API SHALL permitir que o Piloto registre area_realizada, volume_realizado e observacoes_execucao
2. WHILE uma Missão está com status EM_EXECUCAO, THE API SHALL permitir upload de Evidências (fotos, vídeos) com metadados de geolocalização
3. WHEN um Piloto registra consumo de Insumo durante a Missão, THE API SHALL criar registro em consumos_insumo_missao com quantidade_realizada e unidade_medida
4. WHEN uma Missão é concluída, THE API SHALL validar que area_realizada e volume_realizado estão preenchidos
5. IF a quantidade_realizada de Insumo excede a quantidade_prevista na reserva, THEN THE API SHALL exigir preenchimento do campo justificativa_excesso

### Requisito 13: Registro de Ocorrências

**User Story:** Como um Piloto, eu quero registrar ocorrências durante a missão, para que eu possa documentar eventos não planejados e garantir rastreabilidade.

#### Critérios de Aceitação

1. WHILE uma Missão está com status EM_EXECUCAO ou PAUSADA, THE API SHALL permitir registro de Ocorrências com tipo, descrição e severidade
2. THE API SHALL permitir os seguintes valores de severidade para Ocorrência: BAIXA, MEDIA, ALTA, CRITICA
3. WHEN uma Ocorrência com severidade CRITICA é registrada, THE API SHALL registrar o timestamp e o Piloto responsável
4. THE API SHALL retornar lista de Ocorrências filtrada por Missão, tipo e severidade

### Requisito 14: Manutenção de Drones

**User Story:** Como um Técnico, eu quero registrar manutenções realizadas nos drones, para que eu possa manter o histórico de serviços e controlar a próxima manutenção programada.

#### Critérios de Aceitação

1. WHEN um Técnico registra uma Manutenção, THE API SHALL associar ao Drone, registrar tipo, descrição, data_manutencao e horas_na_data
2. WHEN uma Manutenção é registrada, THE API SHALL atualizar o campo ultima_manutencao_em do Drone com a data_manutencao
3. WHEN a data de proxima_manutencao é informada, THE API SHALL validar que proxima_manutencao é posterior ou igual a data_manutencao
4. THE API SHALL retornar lista de Manutenções filtrada por Drone e período
5. WHEN um Drone entra em manutenção, THE API SHALL alterar o status do Drone para EM_MANUTENCAO

### Requisito 15: Gestão de Documentos Oficiais

**User Story:** Como um Administrador, eu quero fazer upload e gerenciar documentos oficiais (registro ANAC, licenças, autorizações), para que eu possa manter a conformidade regulatória da operação.

#### Critérios de Aceitação

1. WHEN um Usuário faz upload de um Documento_Oficial, THE API SHALL armazenar o arquivo no bucket S3 correspondente ao ambiente e registrar metadados (content_type, s3_key, bucket_s3, tipo_documento, entidade, entidade_id) no banco de dados
2. THE API SHALL permitir associar Documentos Oficiais às seguintes entidades: DRONE, MANUTENCAO, USUARIO, CLIENTE, PROPRIEDADE, INSUMO, MISSAO
3. THE API SHALL permitir os seguintes valores de status para Documento_Oficial: ATIVO, SUBSTITUIDO, VENCIDO, INATIVO
4. WHEN a data_validade de um Documento_Oficial é anterior à data atual, THE Sistema SHALL marcar o status como VENCIDO
5. WHEN um novo Documento_Oficial é enviado para substituir um existente do mesmo tipo e entidade, THE API SHALL alterar o status do documento anterior para SUBSTITUIDO
6. THE API SHALL retornar lista de Documentos Oficiais filtrada por entidade, entidade_id, tipo_documento e status
7. WHEN um Usuário solicita download de um Documento_Oficial, THE API SHALL gerar URL pré-assinada do S3 com validade limitada

### Requisito 16: Encerramento Técnico e Financeiro de Missão

**User Story:** Como um Técnico, eu quero encerrar tecnicamente uma missão concluída, e como um Financeiro, eu quero registrar custos e faturamento, para que o ciclo operacional e financeiro da missão seja completado.

#### Critérios de Aceitação

1. WHEN um Técnico encerra tecnicamente uma Missão com status CONCLUIDA, THE API SHALL alterar status para ENCERRADA_TECNICAMENTE e registrar timestamp em encerrado_tecnicamente_em
2. WHEN uma Missão é encerrada tecnicamente, THE API SHALL criar registro em financeiro_missao com status_financeiro PENDENTE
3. WHEN um Financeiro registra dados financeiros, THE API SHALL armazenar custo_estimado, custo_realizado e valor_faturado com valores maiores ou iguais a zero
4. THE API SHALL permitir os seguintes valores de status_financeiro: PENDENTE, EM_FATURAMENTO, FATURADO, RECEBIDO, CANCELADO
5. WHEN um Financeiro encerra financeiramente uma Missão, THE API SHALL alterar status da Missão para ENCERRADA_FINANCEIRAMENTE, registrar timestamp em encerrado_financeiramente_em e registrar fechado_por e fechado_em no financeiro_missao

### Requisito 17: Auditoria de Operações

**User Story:** Como um Administrador, eu quero que todas as alterações críticas sejam registradas em log de auditoria, para que eu possa rastrear quem fez o quê e quando.

#### Critérios de Aceitação

1. WHEN uma entidade principal é criada, atualizada ou excluída logicamente, THE API SHALL registrar na tabela auditoria a entidade, entidade_id, ação, valor_anterior (JSON), valor_novo (JSON) e usuario_id
2. THE API SHALL retornar registros de auditoria filtrados por entidade, entidade_id, usuário e período
3. THE Sistema SHALL armazenar valor_anterior e valor_novo em formato JSON para permitir comparação de alterações

### Requisito 18: Relatórios Operacionais e Financeiros

**User Story:** Como um Administrador ou Financeiro, eu quero consultar relatórios consolidados de operações e finanças, para que eu possa acompanhar indicadores de desempenho e faturamento.

#### Critérios de Aceitação

1. THE API SHALL fornecer endpoint de relatório com total de Missões por status em um período especificado
2. THE API SHALL fornecer endpoint de relatório com área total pulverizada (soma de area_realizada) por período e por Cliente
3. THE API SHALL fornecer endpoint de relatório financeiro com totais de custo_estimado, custo_realizado e valor_faturado por período
4. THE API SHALL fornecer endpoint de relatório de utilização de Drones com horas voadas por período
5. WHEN um Financeiro solicita relatório financeiro, THE API SHALL filtrar dados apenas de Missões com status ENCERRADA_FINANCEIRAMENTE

### Requisito 19: API REST e Convenções

**User Story:** Como um desenvolvedor, eu quero que a API siga convenções REST consistentes, para que a integração entre frontend e backend seja previsível e padronizada.

#### Critérios de Aceitação

1. THE API SHALL utilizar verbos HTTP padrão: GET para consulta, POST para criação, PUT para atualização completa, PATCH para atualização parcial, DELETE para exclusão lógica
2. THE API SHALL retornar respostas em formato JSON com códigos HTTP apropriados (200, 201, 400, 401, 403, 404, 409, 422, 500)
3. THE API SHALL implementar paginação em todos os endpoints de listagem com parâmetros page e page_size
4. THE API SHALL validar dados de entrada e retornar erros de validação com código HTTP 422 e detalhamento dos campos inválidos
5. IF uma requisição referencia um recurso inexistente, THEN THE API SHALL retornar código HTTP 404 com mensagem descritiva

### Requisito 20: Infraestrutura e Armazenamento

**User Story:** Como um Administrador de sistema, eu quero que a aplicação utilize serviços AWS gerenciados, para que eu tenha escalabilidade, segurança e baixo custo operacional.

#### Critérios de Aceitação

1. THE Sistema SHALL hospedar o Frontend como site estático no Amazon S3
2. THE Sistema SHALL hospedar o Backend em AWS Lambda com API Gateway como proxy HTTP
3. THE Sistema SHALL utilizar Amazon RDS for MySQL 8.0 como banco de dados relacional
4. THE Sistema SHALL utilizar buckets S3 separados por ambiente (dev, hml, prd) para armazenamento de documentos
5. THE Sistema SHALL utilizar migrações Flyway com nomenclatura V{n}__{descricao}.sql para versionamento do schema do banco de dados
