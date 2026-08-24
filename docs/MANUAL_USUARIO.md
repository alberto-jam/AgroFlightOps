# AgroFlightOps — Manual do Usuário

> Versão 1.0 · Julho/2026

---

## Sumário

1. [Acesso ao Sistema](#1-acesso-ao-sistema)
2. [Navegação e Layout](#2-navegação-e-layout)
3. [Dashboard](#3-dashboard)
4. [Cadastros](#4-cadastros)
   - 4.1 [Usuários](#41-usuários--somente-administrador)
   - 4.2 [Clientes](#42-clientes)
   - 4.3 [Propriedades](#43-propriedades)
   - 4.4 [Talhões](#44-talhões)
   - 4.5 [Culturas](#45-culturas)
   - 4.6 [Tipos de Ocorrência](#46-tipos-de-ocorrência)
   - 4.7 [Checklist Padrão](#47-checklist-padrão)
5. [Frota](#5-frota)
   - 5.1 [Drones](#51-drones--somente-administrador)
   - 5.2 [Baterias](#52-baterias--somente-administrador)
   - 5.3 [Insumos](#53-insumos)
6. [Operações](#6-operações)
   - 6.1 [Ordens de Serviço](#61-ordens-de-serviço)
   - 6.2 [Missões](#62-missões)
   - 6.3 [Checklists](#63-checklists)
   - 6.4 [Ocorrências](#64-ocorrências)
   - 6.5 [Evidências](#65-evidências)
   - 6.6 [Manutenções](#66-manutenções)
7. [Documentos Oficiais](#7-documentos-oficiais)
8. [Financeiro](#8-financeiro)
   - 8.1 [Financeiro de Missões](#81-financeiro-de-missões)
   - 8.2 [Relatórios](#82-relatórios)
9. [Sistema](#9-sistema)
   - 9.1 [Auditoria](#91-auditoria--somente-administrador)
10. [Telemetria e Insights IA](#10-telemetria-e-insights-ia)
11. [Perfis de Acesso — Resumo](#11-perfis-de-acesso--resumo)
12. [Observação: Envio de E-mail a Novos Usuários](#12-observação-envio-de-e-mail-a-novos-usuários)

---

## 1. Acesso ao Sistema

### Tela de Login

A tela de login é a porta de entrada do sistema. É exibida automaticamente para qualquer usuário não autenticado.

**Campos:**
| Campo | Obrigatório | Descrição |
|---|:---:|---|
| Email | ✅ | Endereço de e-mail cadastrado pelo administrador |
| Senha | ✅ | Senha definida no cadastro |

**Como acessar:**
1. Abra o navegador e acesse a URL do sistema (fornecida pelo administrador)
2. Informe o **email** e a **senha**
3. Clique em **Entrar**
4. Em caso de sucesso, você será redirecionado ao **Dashboard**

**Mensagens de erro:**
- *"Credenciais inválidas. Verifique email e senha."* — o e-mail não existe, a senha está errada ou o usuário está desativado. A mensagem é propositalmente genérica por segurança.

**Requisitos:**
- O usuário deve estar previamente cadastrado por um **Administrador**
- A conta deve estar com status **Ativo**
- Credenciais são fornecidas pelo administrador (o sistema não possui cadastro próprio nem recuperação de senha)

**Sessão:**
- O token de acesso expira em **60 minutos**
- Ao expirar, o sistema redireciona automaticamente para o login
- Não existe "Lembrar de mim" — cada acesso requer nova autenticação

---

## 2. Navegação e Layout

Após o login, o sistema exibe um layout padrão com três áreas:

### Menu lateral (Sider)
- Localizado à esquerda da tela
- Pode ser **recolhido** clicando no ícone de hambúrguer no cabeçalho
- Exibe apenas as seções que o perfil do usuário tem permissão de acessar
- O item ativo é destacado com cor diferente

**Grupos do menu** (visíveis conforme o perfil):
- **Geral** → Dashboard
- **Cadastros** → Usuários, Clientes, Propriedades, Talhões, Culturas, Tipos de Ocorrência, Checklist Padrão
- **Frota** → Drones, Baterias, Insumos
- **Operações** → Ordens de Serviço, Missões, Checklists, Ocorrências, Evidências, Manutenções
- **Documentos** → Documentos Oficiais
- **Financeiro** → Financeiro, Relatórios
- **Sistema** → Auditoria

### Cabeçalho (Header)
- Fixo no topo da tela
- Exibe o botão de recolher/expandir o menu
- Botão com o **nome do usuário** no canto direito — ao clicar, exibe a opção **Sair** para encerrar a sessão

### Área de conteúdo
- Ocupa o restante da tela
- Cada página carrega nessa área sem recarregar o navegador (SPA)

### Rodapé
- Exibe o nome do sistema e o ano atual

---

## 3. Dashboard

**Acesso:** Todos os perfis  
**Caminho no menu:** Geral → Dashboard

O Dashboard é a tela inicial do sistema e oferece uma visão geral do estado operacional.

### Cards de indicadores (KPIs)

| Card | O que mostra |
|---|---|
| **Ordens de Serviço** | Total de OS cadastradas, com contagem por status |
| **Missões Ativas** | Quantidade de missões em status ativo (Em Execução, Pausada, Agendada, Liberada, Em Checklist) |
| **Drones Disponíveis** | Quantidade de drones com status DISPONIVEL sobre o total cadastrado. Exibe também quantos estão Em Uso |
| **Documentos Vencidos** | Quantidade de documentos oficiais com status VENCIDO. Exibe "Tudo em dia" quando zerado |

### Alerta de documentos vencidos

Quando existem documentos com status VENCIDO, um alerta amarelo é exibido abaixo dos KPIs com a lista dos documentos afetados (até 5), indicando a entidade e a data de vencimento.

### Tabela de Missões Recentes

Exibe as **5 missões** mais recentemente atualizadas com:
- Código da missão
- Status (com badge colorida)
- Data agendada
- Data/hora da última atualização

**Requisito para visualizar os cards de OS e Missões:** o perfil do usuário precisa ter acesso às respectivas rotas (ADMINISTRADOR e COORDENADOR_OPERACIONAL visualizam tudo; outros perfis verão apenas as informações às quais têm acesso).

---

## 4. Cadastros

---

### 4.1 Usuários — Somente Administrador

**Acesso:** ADMINISTRADOR  
**Caminho no menu:** Cadastros → Usuários

Tela de gestão de todos os usuários do sistema.

#### Listagem

Exibe uma tabela paginada com:
- **ID**, **Nome**, **Email**, **Perfil**, **Status** (Ativo/Inativo)

**Filtros disponíveis:**
| Filtro | Tipo | Descrição |
|---|---|---|
| Perfil | Seleção | Filtra por perfil (Administrador, Coordenador Operacional, Piloto, Técnico, Financeiro) |
| Status | Seleção | Filtra por Ativo ou Inativo |

#### Criar usuário

Clique em **+ Novo Usuário**. Preencha:

| Campo | Obrigatório | Regra |
|---|:---:|---|
| Nome | ✅ | Máximo 200 caracteres |
| Email | ✅ | Deve ser um e-mail válido e único no sistema |
| Perfil | ✅ | Selecionar entre os 5 perfis disponíveis |
| Senha | ✅ | Mínimo 6 caracteres (apenas no cadastro — não exibida na edição) |

> ⚠️ **Atenção:** O sistema **não envia e-mail** com as credenciais de acesso. O administrador deve comunicar o e-mail e a senha ao novo usuário por outro meio (veja a [seção 12](#12-observação-envio-de-e-mail-a-novos-usuários)).

#### Editar usuário

Clique em **Editar** na linha desejada. É possível alterar nome, e-mail e perfil. A senha pode ser alterada informando uma nova no campo correspondente (campo não aparece em branco por segurança).

#### Ativar / Desativar usuário

Clique em **Desativar** ou **Ativar** na linha desejada. O sistema pede confirmação. Um usuário desativado não consegue fazer login.

**Premissas:**
- Não é possível excluir um usuário permanentemente (somente desativar)
- O e-mail deve ser único em todo o sistema

---

### 4.2 Clientes

**Acesso:** ADMINISTRADOR, COORDENADOR_OPERACIONAL  
**Caminho no menu:** Cadastros → Clientes

Cadastro dos produtores rurais atendidos pela empresa.

#### Campos do formulário

| Campo | Obrigatório | Descrição |
|---|:---:|---|
| Nome | ✅ | Nome do cliente / razão social |
| CPF/CNPJ | — | Documento do cliente |
| Telefone | — | Contato telefônico |
| Email | — | E-mail de contato |
| Endereço, Número, Complemento, Bairro | — | Endereço completo |
| Município | — | Cidade |
| Estado | — | UF (2 letras) |
| CEP | — | CEP no formato xxxxxxxx |
| Latitude / Longitude | — | Coordenadas geográficas (aceita de -90 a 90 e -180 a 180) |
| Referência Local | — | Descrição livre de referência de localização |

#### Ações disponíveis
- **Novo Cliente** — abre formulário de criação
- **Editar** — altera dados (exceto registros vinculados já finalizados)
- **Desativar** — desativa o cliente. **Não é possível desativar um cliente com Ordens de Serviço não canceladas**

---

### 4.3 Propriedades

**Acesso:** ADMINISTRADOR, COORDENADOR_OPERACIONAL  
**Caminho no menu:** Cadastros → Propriedades

Cadastro das fazendas e propriedades rurais vinculadas a um cliente.

#### Campos do formulário

| Campo | Obrigatório | Descrição |
|---|:---:|---|
| Cliente | ✅ | Cliente proprietário da fazenda |
| Nome | ✅ | Nome da propriedade |
| Município | ✅ | Cidade onde está localizada |
| Estado | ✅ | UF |
| Área Total (ha) | ✅ | Área total em hectares (≥ 0) |
| Endereço / Bairro / CEP | — | Localização detalhada |
| Latitude / Longitude | — | Coordenadas geográficas |
| Localização Descritiva | — | Texto livre descrevendo o acesso |
| Referência Local | — | Ponto de referência para chegada ao local |

**Premissas:**
- Uma propriedade deve estar vinculada a um cliente cadastrado e ativo
- Não é possível desativar uma propriedade com Ordens de Serviço ativas

---

### 4.4 Talhões

**Acesso:** ADMINISTRADOR, COORDENADOR_OPERACIONAL  
**Caminho no menu:** Cadastros → Talhões

Divisões internas de uma propriedade (glebas, parcelas).

#### Campos do formulário

| Campo | Obrigatório | Descrição |
|---|:---:|---|
| Propriedade | ✅ | Propriedade à qual o talhão pertence |
| Nome | ✅ | Identificador do talhão (único dentro da propriedade) |
| Área (ha) | ✅ | Área do talhão em hectares (≥ 0) |
| Cultura | ✅ | Cultura plantada no talhão |
| Latitude / Longitude | — | Ponto de referência do talhão |
| Ponto de Referência | — | Descrição do acesso ao talhão |
| GeoJSON | — | Polígono do talhão em formato GeoJSON (para visualização no mapa) |
| Observações | — | Informações adicionais |

**Premissas:**
- O nome do talhão deve ser único dentro da mesma propriedade
- A cultura informada deve estar previamente cadastrada

---

### 4.5 Culturas

**Acesso:** ADMINISTRADOR, COORDENADOR_OPERACIONAL  
**Caminho no menu:** Cadastros → Culturas

Tabela de culturas agrícolas disponíveis para seleção em talhões e ordens de serviço.

| Campo | Obrigatório | Descrição |
|---|:---:|---|
| Nome | ✅ | Nome da cultura (único no sistema) |
| Descrição | — | Informações adicionais |

**Premissas:**
- O nome da cultura deve ser único
- Não é possível desativar uma cultura que possui talhões ativos vinculados

---

### 4.6 Tipos de Ocorrência

**Acesso:** ADMINISTRADOR, COORDENADOR_OPERACIONAL  
**Caminho no menu:** Cadastros → Tipos de Ocorrência

Tabela de categorias para classificação de ocorrências durante as missões (ex.: "Falha mecânica", "Clima adverso", "Obstáculo no campo").

| Campo | Obrigatório | Descrição |
|---|:---:|---|
| Nome | ✅ | Descrição do tipo (único no sistema) |
| Descrição | — | Detalhamento do tipo de ocorrência |

---

### 4.7 Checklist Padrão

**Acesso:** ADMINISTRADOR, COORDENADOR_OPERACIONAL  
**Caminho no menu:** Cadastros → Checklist Padrão

Define os itens que compõem o checklist pré-voo. Ao criar uma missão e avançá-la para o status **EM_CHECKLIST**, esses itens são automaticamente gerados para preenchimento pelo piloto.

| Campo | Obrigatório | Descrição |
|---|:---:|---|
| Nome do Item | ✅ | Descrição do item (único no sistema) |
| Descrição | — | Orientação sobre como verificar o item |
| Obrigatório | ✅ | Se `Sim`, o item deve ser aprovado para liberar a missão |
| Ordem de Exibição | ✅ | Posição na lista (número ≥ 0) |

**Premissas:**
- A ordem de exibição determina a sequência no checklist
- Itens obrigatórios reprovados ou pendentes impedem a aprovação do checklist

---

## 5. Frota

---

### 5.1 Drones — Somente Administrador

**Acesso:** ADMINISTRADOR  
**Caminho no menu:** Frota → Drones

Cadastro e gestão da frota de drones.

#### Campos do formulário

| Campo | Obrigatório | Descrição |
|---|:---:|---|
| Identificação | ✅ | Código/série único do drone |
| Modelo | ✅ | Modelo do equipamento |
| Fabricante | — | Nome do fabricante |
| Capacidade (L) | ✅ | Capacidade do tanque em litros (≥ 0) |
| Status | ✅ | Status atual do drone |
| Horas Voadas | ✅ | Total de horas de voo acumuladas (≥ 0) |
| Última Manutenção | — | Data da última manutenção realizada |

#### Status possíveis do drone

| Status | Descrição |
|---|---|
| **DISPONIVEL** | Pronto para uso em uma missão |
| **EM_USO** | Atualmente em uma missão ativa |
| **EM_MANUTENCAO** | Fora de operação por manutenção |
| **BLOQUEADO** | Impedido de operar por decisão administrativa |
| **INATIVO** | Desativado permanentemente do sistema |

**Premissas:**
- A identificação deve ser única no sistema
- Somente drones com status **DISPONIVEL** podem ser associados a novas missões

---

### 5.2 Baterias — Somente Administrador

**Acesso:** ADMINISTRADOR  
**Caminho no menu:** Frota → Baterias

Cadastro das baterias da frota, que podem ser associadas a um drone e utilizadas nas missões.

#### Campos do formulário

| Campo | Obrigatório | Descrição |
|---|:---:|---|
| Identificação | ✅ | Código/série único da bateria |
| Drone (vínculo) | — | Drone ao qual a bateria está associada |
| Ciclos | ✅ | Número de ciclos de carga/descarga (≥ 0) |
| Status | ✅ | Status atual da bateria |
| Observações | — | Informações sobre a condição da bateria |

#### Status possíveis da bateria

| Status | Descrição |
|---|---|
| **DISPONIVEL** | Pronta para uso |
| **EM_USO** | Em uso em uma missão |
| **CARREGANDO** | Em processo de carregamento |
| **REPROVADA** | Reprovada em inspeção, aguarda descarte |
| **DESCARTADA** | Descartada permanentemente |

**Premissas:**
- A identificação deve ser única no sistema
- Uma bateria pode ser associada a um drone ou ficar sem vínculo
- Baterias **DESCARTADA** ou **REPROVADA** não devem ser usadas em missões

---

### 5.3 Insumos

**Acesso:** ADMINISTRADOR, COORDENADOR_OPERACIONAL  
**Caminho no menu:** Frota → Insumos

Controle de estoque de defensivos, fertilizantes e demais produtos utilizados nas pulverizações.

#### Campos do formulário

| Campo | Obrigatório | Descrição |
|---|:---:|---|
| Nome | ✅ | Nome do produto |
| Fabricante | — | Fabricante do produto |
| Unidade de Medida | ✅ | Ex.: L, kg, mL |
| Saldo Atual | ✅ | Quantidade disponível em estoque (≥ 0) |
| Lote | — | Número do lote do produto |
| Validade | — | Data de validade do produto |

**Premissas:**
- O saldo é atualizado automaticamente quando consumos reais são registrados em missões
- O sistema bloqueia o uso de insumos com saldo insuficiente ao registrar consumo
- Insumos podem ser criados diretamente a partir da tela de Missões, durante o registro de consumo

---

## 6. Operações

---

### 6.1 Ordens de Serviço

**Acesso:** ADMINISTRADOR, COORDENADOR_OPERACIONAL  
**Caminho no menu:** Operações → Ordens de Serviço

A **Ordem de Serviço (OS)** é o ponto de partida de uma operação. Ela define o que será feito, onde, quando e com qual prioridade. Uma OS precisa ser aprovada antes que missões possam ser criadas a partir dela.

#### Listagem

Exibe tabela paginada com: Código, Cliente, Propriedade, Prioridade, Data Prevista, Status.

**Filtros disponíveis:**
| Filtro | Descrição |
|---|---|
| Status | Filtra por RASCUNHO, EM_ANALISE, APROVADA, REJEITADA ou CANCELADA |
| Cliente | Filtra por cliente |
| Propriedade | Filtra por propriedade |
| Prioridade | Filtra por BAIXA, MEDIA, ALTA ou CRITICA |
| Data Prevista | Filtra pela data de execução planejada |

#### Criar OS

Clique em **+ Nova OS**. O formulário é em cascata:

| Campo | Obrigatório | Regra |
|---|:---:|---|
| Cliente | ✅ | Selecionar entre os clientes ativos |
| Propriedade | ✅ | Filtrada automaticamente pelo cliente selecionado |
| Talhão | ✅ | Filtrado automaticamente pela propriedade selecionada |
| Cultura | ✅ | Cultura a ser tratada |
| Tipo de Aplicação | ✅ | Ex.: "Herbicida", "Fungicida", "Fertilização foliar" |
| Prioridade | ✅ | BAIXA / MEDIA / ALTA / CRITICA |
| Data Prevista | ✅ | Data planejada para execução da operação |
| Observações | — | Informações adicionais ou instruções especiais |

> Após criar, a OS fica em **RASCUNHO**. O código é gerado automaticamente pelo sistema.

#### Editar OS

Disponível apenas para OS em status **RASCUNHO**. OS que já foram submetidas não podem ter seus campos base alterados.

#### Ciclo de vida da OS

```
RASCUNHO ──► EM_ANALISE ──► APROVADA
                │               │
                ▼               ▼
            REJEITADA       CANCELADA
```

| Ação | Status resultante | Motivo obrigatório | Quem pode executar |
|---|---|:---:|---|
| **Submeter** | EM_ANALISE | Não | ADMIN / COORDENADOR |
| **Aprovar** | APROVADA | Não | ADMIN / COORDENADOR |
| **Rejeitar** | REJEITADA | **Sim** | ADMIN / COORDENADOR |
| **Cancelar** | CANCELADA | **Sim** | ADMIN / COORDENADOR |

**Premissas:**
- Apenas OS com status **APROVADA** podem ter missões criadas a partir delas
- OS **REJEITADA** ou **CANCELADA** são estados finais — não há retorno
- O histórico de todas as transições fica disponível no botão **Histórico**

---

### 6.2 Missões

**Acesso:** ADMINISTRADOR, COORDENADOR_OPERACIONAL, PILOTO, TECNICO  
**Caminho no menu:** Operações → Missões

A **Missão** representa a execução física de uma OS em campo. Cada missão é vinculada a uma OS aprovada e passa por um ciclo de vida detalhado.

#### Listagem

Exibe tabela paginada com: Código, OS, Piloto, Drone, Data Agendada, Status.

**Filtros disponíveis:**
| Filtro | Descrição |
|---|---|
| Status | Todos os status disponíveis |
| Piloto | Filtra por piloto responsável |
| Drone | Filtra por drone designado |
| Data Agendada | Filtra pela data de voo |
| Ordem de Serviço | Filtra por OS vinculada |

#### Criar Missão

Clique em **+ Nova Missão**. Apenas OS com status **APROVADA** aparecem para seleção.

| Campo | Obrigatório | Descrição |
|---|:---:|---|
| Ordem de Serviço (Aprovada) | ✅ | OS que origina a missão |
| Piloto | ✅ | Usuário responsável pelo voo |
| Técnico | — | Usuário de suporte técnico (opcional) |
| Drone | ✅ | Drone designado para a missão |
| Área Prevista (ha) | ✅ | Área a ser pulverizada, em hectares |
| Volume Previsto (L) | ✅ | Volume de calda a ser aplicado, em litros |
| Data Agendada | ✅ | Data do voo |
| Hora Agendada | ✅ | Hora de início do voo |

> A localização da operação (coordenadas e endereço) é preenchida automaticamente com base na propriedade da OS.

#### Ciclo de vida da Missão

```
RASCUNHO ──► PLANEJADA ──► AGENDADA ──► EM_CHECKLIST ──► LIBERADA ──► EM_EXECUCAO
                                                                            │
                                                                       PAUSADA ◄──►
                                                                            │
                                                                        CONCLUIDA
                                                                            │
                                                              ENCERRADA_TECNICAMENTE
                                                                            │
                                                            ENCERRADA_FINANCEIRAMENTE
```

| Ação | Status resultante | Campos extras | Observação |
|---|---|---|---|
| **Planejar** | PLANEJADA | Restrições, Obs. Planejamento | — |
| **Agendar** | AGENDADA | Data/Hora agendada | Permite reagendar |
| **Iniciar Checklist** | EM_CHECKLIST | — | Gera os itens do checklist |
| **Liberar** | LIBERADA | — | Somente após checklist aprovado |
| **Iniciar Execução** | EM_EXECUCAO | Obs. Execução | — |
| **Pausar** | PAUSADA | — | Pode retomar |
| **Retomar Execução** | EM_EXECUCAO | — | — |
| **Concluir** | CONCLUIDA | — | — |
| **Encerrar Tecnicamente** | ENCERRADA_TECNICAMENTE | — | — |
| **Encerrar Financeiramente** | ENCERRADA_FINANCEIRAMENTE | — | Requer encerramento financeiro |
| **Cancelar** | CANCELADA | Motivo obrigatório | Disponível em vários status |

#### Ações adicionais na missão

**Baterias** — associa baterias à missão antes do voo:
- Clique em **Baterias** na linha da missão
- Clique em **Adicionar Bateria**
- Selecione a bateria e a **ordem de uso** (qual bateria será usada primeiro)
- **Premissa:** a bateria deve estar cadastrada no sistema

**Insumos (Reserva)** — planeja os insumos necessários:
- Clique em **Insumos** na linha da missão
- Clique em **Reservar Insumo**
- Selecione o insumo, a quantidade prevista e a unidade de medida
- **Premissa:** o insumo deve ter saldo suficiente em estoque

**Execução** — registra dados reais durante o voo (apenas quando status = EM_EXECUCAO):
- Clique em **Execução** na linha da missão
- Informe **Área Realizada** e **Volume Realizado**
- Registre os **consumos reais** de cada insumo utilizado
- Faça **upload de evidências** (fotos/vídeos do campo)

**Histórico** — exibe o log de todas as transições de status com data, motivo e usuário que realizou a ação.

**Telemetria** — acessa os dados de voo (veja a [seção 10](#10-telemetria-e-insights-ia)).

---

### 6.3 Checklists

**Acesso:** ADMINISTRADOR, PILOTO (preenchimento) · TECNICO (aprovação)  
**Caminho no menu:** Operações → Checklists

O checklist pré-voo é gerado automaticamente quando a missão avança para o status **EM_CHECKLIST**. Os itens são baseados no **Checklist Padrão** cadastrado (seção 4.7).

#### O que o Piloto faz:

1. Acesse **Operações → Checklists** e localize a missão
2. Para cada item do checklist, marque o status:
   - **APROVADO** — item verificado e em conformidade
   - **REPROVADO** — item com problema identificado
   - **NAO_APLICAVEL** — item não se aplica a esta missão
3. Registre observações em cada item se necessário
4. Quando todos os itens obrigatórios estiverem preenchidos, clique em **Concluir Checklist**

> O status do checklist muda para **CONCLUIDO** após a conclusão pelo piloto.

#### O que o Técnico faz:

1. Revise os itens preenchidos pelo piloto
2. Clique em **Aprovar Checklist** para liberar a missão
   - O checklist muda para **APROVADO**
   - A missão avança automaticamente para status **LIBERADA**

> Se houver algum item reprovado, o técnico não deve aprovar. A missão permanece em **EM_CHECKLIST** até que os problemas sejam resolvidos.

#### Status do Checklist

| Status | Descrição |
|---|---|
| PENDENTE | Checklist criado, aguardando preenchimento |
| EM_PREENCHIMENTO | Piloto está preenchendo os itens |
| CONCLUIDO | Piloto concluiu, aguardando aprovação do técnico |
| APROVADO | Técnico aprovou — missão liberada para execução |
| REPROVADO | Técnico reprovou — missão não pode prosseguir |

**Premissas:**
- O checklist só existe se a missão estiver em **EM_CHECKLIST** ou status posterior
- Todos os itens marcados como obrigatórios devem estar **APROVADO** para que o técnico possa aprovar
- A aprovação do checklist é o único caminho para avançar a missão para **LIBERADA**

---

### 6.4 Ocorrências

**Acesso:** ADMINISTRADOR, PILOTO  
**Caminho no menu:** Operações → Ocorrências

Registro de eventos não planejados ou adversos que ocorreram durante uma missão.

#### Campos do formulário

| Campo | Obrigatório | Descrição |
|---|:---:|---|
| Missão | ✅ | Missão em que a ocorrência aconteceu |
| Tipo de Ocorrência | ✅ | Categoria (cadastrada em Tipos de Ocorrência) |
| Severidade | ✅ | BAIXA / MEDIA / ALTA / CRITICA |
| Descrição | ✅ | Relato detalhado do ocorrido |
| Data/Hora | ✅ | Quando a ocorrência aconteceu |
| Latitude / Longitude | — | Localização exata da ocorrência |

**Premissas:**
- O tipo de ocorrência deve estar previamente cadastrado
- A missão referenciada deve existir no sistema

---

### 6.5 Evidências

**Acesso:** ADMINISTRADOR, PILOTO  
**Caminho no menu:** Operações → Evidências  
*(Também acessível diretamente pelo painel de Execução da Missão)*

Upload de arquivos de mídia (fotos, vídeos) que comprovam a execução da missão em campo.

#### Campos do formulário

| Campo | Obrigatório | Descrição |
|---|:---:|---|
| Missão | ✅ | Missão à qual a evidência pertence |
| Arquivo | ✅ | Foto ou vídeo (upload via botão) |
| Latitude / Longitude | — | Coordenadas onde a foto/vídeo foi capturado |

**Premissas:**
- Os arquivos são armazenados no Amazon S3 e acessados via URL pré-assinada temporária
- A missão deve existir no sistema
- O link de download expira em **60 minutos** (configurável pelo administrador)

---

### 6.6 Manutenções

**Acesso:** ADMINISTRADOR, TECNICO  
**Caminho no menu:** Operações → Manutenções

Registro de serviços de manutenção realizados nos drones da frota.

#### Listagem

Exibe tabela paginada com dados da manutenção.

**Filtros disponíveis:**
| Filtro | Descrição |
|---|---|
| Drone | Filtra por drone específico |
| Data Início | Data de início do período de busca |
| Data Fim | Data de fim do período de busca |

#### Campos do formulário

| Campo | Obrigatório | Descrição |
|---|:---:|---|
| Drone | ✅ | Drone que recebeu a manutenção |
| Tipo de Manutenção | ✅ | Ex.: Preventiva, Corretiva, Revisão |
| Data de Início | ✅ | Quando a manutenção começou |
| Data de Conclusão | — | Quando a manutenção foi concluída |
| Descrição | — | Detalhamento do serviço realizado |
| Técnico Responsável | — | Quem executou a manutenção |
| Custo | — | Valor do serviço |

**Premissas:**
- O drone deve estar previamente cadastrado
- A data de conclusão não pode ser anterior à data de início

---

## 7. Documentos Oficiais

**Acesso (upload):** ADMINISTRADOR  
**Acesso (visualização e download):** Todos os perfis  
**Caminho no menu:** Documentos → Documentos Oficiais

Repositório central de documentos vinculados às entidades do sistema (drones, manutenções, usuários, clientes, propriedades, insumos, missões).

#### Listagem

Exibe tabela paginada com: Tipo, Entidade, ID da Entidade, Status, Data de Emissão, Data de Validade.

**Filtros disponíveis:**
| Filtro | Descrição |
|---|---|
| Entidade | DRONE / MANUTENCAO / USUARIO / CLIENTE / PROPRIEDADE / INSUMO / MISSAO |
| ID da Entidade | ID numérico da entidade específica |
| Tipo de Documento | Filtra pelo tipo (ex.: "CRAE", "ART", "Receituário") |
| Status | ATIVO / SUBSTITUIDO / VENCIDO / INATIVO |

#### Fazer upload de documento

Somente o **Administrador** pode fazer upload. Clique em **+ Novo Documento** e preencha:

| Campo | Obrigatório | Descrição |
|---|:---:|---|
| Arquivo | ✅ | Arquivo a ser enviado (PDF, imagem, etc.) |
| Entidade | ✅ | Tipo de entidade a que o documento pertence |
| ID da Entidade | ✅ | ID numérico da entidade no sistema |
| Tipo de Documento | ✅ | Categoria do documento (texto livre) |
| Descrição | — | Informações adicionais sobre o documento |
| Data de Emissão | — | Data em que o documento foi emitido |
| Data de Validade | — | Data em que o documento vence |

**Download de documento:**

Qualquer usuário autenticado pode clicar em **Download** para obter uma URL temporária de acesso ao arquivo armazenado no S3. O link expira em **60 minutos**.

**Premissas:**
- Os arquivos são armazenados no Amazon S3 (não no banco de dados)
- Documentos com data de validade vencida aparecem com status **VENCIDO** e geram alerta no Dashboard
- Não é possível excluir documentos — apenas mudar seu status para INATIVO

---

## 8. Financeiro

---

### 8.1 Financeiro de Missões

**Acesso:** ADMINISTRADOR, FINANCEIRO  
**Caminho no menu:** Financeiro → Financeiro

Gestão financeira das missões concluídas. O registro financeiro é criado automaticamente quando a missão atinge o status **ENCERRADA_TECNICAMENTE**.

#### Listagem

Exibe as missões com registro financeiro associado, com filtro por status financeiro.

#### Campos editáveis

| Campo | Descrição |
|---|---|
| Valor por Hectare (R$) | Preço acordado por hectare pulverizado |
| Valor Total (R$) | Calculado automaticamente (Área Realizada × Valor/ha) ou informado manualmente |
| Observações | Notas sobre o faturamento |
| Número NF / Documento | Número da nota fiscal ou documento de cobrança |

#### Ciclo financeiro

| Status | Descrição | Ação disponível |
|---|---|---|
| **PENDENTE** | Aguardando início do faturamento | Atualizar dados, iniciar faturamento |
| **EM_FATURAMENTO** | Em processo de emissão de NF | Atualizar, faturar |
| **FATURADO** | Nota fiscal emitida | Registrar recebimento |
| **RECEBIDO** | Pagamento confirmado | — |
| **CANCELADO** | Operação financeira cancelada | — |

#### Encerramento financeiro

Clique em **Encerrar Financeiramente** para avançar a missão ao status final **ENCERRADA_FINANCEIRAMENTE**.

**Premissas:**
- O registro financeiro só existe se a missão tiver passado por **ENCERRADA_TECNICAMENTE**
- O encerramento financeiro é o status final da missão — não há retorno

---

### 8.2 Relatórios

**Acesso:** ADMINISTRADOR, FINANCEIRO  
**Caminho no menu:** Financeiro → Relatórios

Geração de relatórios analíticos por período. Todos os relatórios exigem informar **Data Início** e **Data Fim**.

| Relatório | O que exibe |
|---|---|
| **Missões por Status** | Total de missões agrupadas por status no período informado |
| **Área por Cliente** | Total de hectares pulverizados por cliente no período |
| **Financeiro** | Resumo financeiro (valores) apenas de missões com status ENCERRADA_FINANCEIRAMENTE |
| **Utilização de Drones** | Horas de voo e número de missões por drone no período |

**Como gerar um relatório:**
1. Selecione o tipo de relatório no menu
2. Informe a **Data de Início** e a **Data de Fim** do período
3. Clique em **Consultar**
4. Os resultados são exibidos na mesma tela

---

## 9. Sistema

---

### 9.1 Auditoria — Somente Administrador

**Acesso:** ADMINISTRADOR  
**Caminho no menu:** Sistema → Auditoria

Registro imutável de todas as ações realizadas no sistema — criações, edições e exclusões de qualquer entidade.

#### Listagem

Exibe tabela paginada com: Entidade, ID, Ação, Usuário, Data/Hora, Valor Anterior, Valor Novo.

**Filtros disponíveis:**
| Filtro | Descrição |
|---|---|
| Entidade | Nome da entidade (ex.: USUARIO, MISSAO, DRONE) |
| ID da Entidade | ID numérico do registro afetado |
| Usuário | ID do usuário que realizou a ação |
| Data Início | Início do período de busca |
| Data Fim | Fim do período de busca |

**O que é registrado:**
- **CRIACAO** — novo registro criado
- **ATUALIZACAO** — dados de um registro alterados (guarda o valor anterior e o novo)
- **EXCLUSAO** — registro desativado

**Premissas:**
- Os registros de auditoria são **somente leitura** — não podem ser editados ou excluídos
- A auditoria registra o estado completo do objeto (JSON) antes e depois de cada alteração

---

## 10. Telemetria e Insights IA

**Acesso:** Todos os perfis autenticados  
**Onde acessar:** Tela de Missões → botão **Telemetria** na linha da missão

A telemetria permite analisar os dados de voo coletados pelo drone durante a missão.

### Upload de Telemetria

1. Na tela de **Missões**, localize a missão desejada
2. Clique no botão **Telemetria**
3. Na aba **Importar**, selecione o arquivo JSON de telemetria exportado pelo drone
4. Clique em **Enviar**

O arquivo é enviado ao S3 e processado automaticamente em segundo plano (pipeline assíncrono via Lambda).

**Formato esperado do arquivo JSON:**
```json
[
  {
    "flight_id": "4",
    "timestamp": "2026-04-25T12:00:00Z",
    "latitude": -15.7801,
    "longitude": -47.9292,
    "altitude_m": 5.0,
    "height_above_ground_m": 3.5,
    "speed_mps": 5.2,
    "battery_percent": 85,
    "spray_on": true,
    "flow_l_min": 1.8,
    "tank_level_percent": 70,
    "gps_satellites": 14,
    "signal_strength_percent": 90
  }
]
```

### Resumo de Telemetria

Após o processamento (geralmente em segundos), a aba **Resumo** exibe:
- Distância total percorrida (metros)
- Score médio da operação (0–100)
- Número de pontos com anomalia detectada
- Número total de pontos registrados

### GeoJSON (Mapa)

A aba **Mapa** (ou acesso via `/missoes/{id}/telemetria/geojson`) exibe o trajeto do drone em formato de mapa interativo usando Leaflet.

### Anomalias

A aba **Anomalias** lista os pontos do voo onde foram detectadas irregularidades:

| Anomalia | Condição detectada |
|---|---|
| VELOCIDADE_EXCESSIVA | Velocidade acima de 8 m/s |
| BATERIA_BAIXA | Bateria abaixo de 20% |
| ALTURA_BAIXA | Altura acima do solo abaixo de 2m |
| ALTURA_ALTA | Altura acima do solo acima de 5m |
| GPS_FRACO | Menos de 10 satélites GPS |
| SINAL_FRACO | Sinal de rádio abaixo de 55% |
| PULVERIZACAO_SEM_FLUXO | Pulverização ativa mas sem fluxo detectado |

### Insights de IA

O botão **Insights** (ou aba correspondente) consulta o **Amazon Bedrock** para gerar uma análise interpretativa da telemetria da missão em linguagem natural, descrevendo o desempenho operacional, anomalias identificadas e sugestões de melhoria.

**Premissas:**
- A telemetria precisa ter sido processada com sucesso antes de consultar o resumo ou o mapa
- Os Insights de IA consomem o Amazon Bedrock — pode haver pequena latência na resposta
- O sistema exibe erro 502 caso o Bedrock esteja indisponível

---

## 11. Perfis de Acesso — Resumo

| Tela | ADMIN | COORD | PILOTO | TECNICO | FINANCEIRO |
|---|:---:|:---:|:---:|:---:|:---:|
| Dashboard | ✅ | ✅ | ✅ | ✅ | ✅ |
| Usuários | ✅ | — | — | — | — |
| Clientes / Propriedades / Talhões | ✅ | ✅ | — | — | — |
| Culturas / Tipos Ocorrência | ✅ | ✅ | — | — | — |
| Checklist Padrão | ✅ | ✅ | — | — | — |
| Drones / Baterias | ✅ | — | — | — | — |
| Insumos | ✅ | ✅ | — | — | — |
| Ordens de Serviço | ✅ | ✅ | — | — | — |
| Missões | ✅ | ✅ | ✅ | ✅ | — |
| Checklists (preencher) | ✅ | — | ✅ | — | — |
| Checklists (aprovar) | ✅ | — | — | ✅ | — |
| Ocorrências / Evidências | ✅ | — | ✅ | — | — |
| Manutenções | ✅ | — | — | ✅ | — |
| Documentos (upload) | ✅ | — | — | — | — |
| Documentos (visualizar) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Telemetria / Insights IA | ✅ | ✅ | ✅ | ✅ | ✅ |
| Financeiro de Missões | ✅ | — | — | — | ✅ |
| Relatórios | ✅ | — | — | — | ✅ |
| Auditoria | ✅ | — | — | — | — |

---

## 12. Observação: Envio de E-mail a Novos Usuários

> **O sistema não envia e-mail automaticamente ao cadastrar um novo usuário.**

Após criar um usuário na tela de Usuários (seção 4.1), o administrador deve comunicar as credenciais de acesso ao usuário por outro meio (e-mail corporativo, mensagem ou outro canal interno).

As informações necessárias para o primeiro acesso são:
- **URL do sistema** (fornecida pelo administrador de infraestrutura)
- **E-mail** informado no cadastro
- **Senha** definida no momento do cadastro

Esta funcionalidade de envio automático de boas-vindas **não está implementada** no sistema atual. Se for necessária, deve ser desenvolvida como uma melhoria futura, integrando, por exemplo, o **Amazon SES (Simple Email Service)** ao fluxo de criação de usuários.

---

*Manual gerado com base no código-fonte do sistema — julho/2026.*
