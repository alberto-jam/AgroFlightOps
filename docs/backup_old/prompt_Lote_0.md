AGROTECH - PROMPT LOTE 0
------------------------
Implemente o **LOTE 0 — Fundação e Esqueleto do Projeto** para o sistema de gestão de serviços de pulverização por drones, seguindo rigorosamente a especificação fornecida.

IMPORTANTE
Este é apenas o LOTE 0.
Não implemente funcionalidades de negócio completas ainda.
O objetivo é preparar a infraestrutura do sistema para os próximos lotes.

Respeite integralmente as decisões arquiteturais descritas na especificação.

---

# Objetivo do Lote 0

Criar a base técnica do sistema, incluindo:

* estrutura do projeto
* banco de dados PostgreSQL
* autenticação
* controle de acesso por perfil (RBAC)
* migrations
* auditoria básica
* layout inicial da aplicação
* navegação protegida
* componentes reutilizáveis
* componente de mapa embutido para geolocalização

Ao final deste lote, o sistema deve iniciar corretamente e permitir login com perfis de usuário.

---

# Decisões obrigatórias de arquitetura

Banco de dados:
PostgreSQL

Chave primária padrão:
UUID

Campos obrigatórios nas entidades principais:

* id
* created_at
* updated_at

Controle de acesso:
RBAC baseado em perfil de usuário

Perfis obrigatórios iniciais:

* ADMINISTRADOR
* COORDENADOR_OPERACIONAL
* PILOTO
* TECNICO
* FINANCEIRO

Não alterar essas decisões.

---

# Estrutura esperada do projeto

O projeto deve ser organizado de forma clara e modular.

Backend deve ser estruturado por domínio.

Sugestão de módulos backend:

* auth
* users
* cadastros
* ordens_servico
* missoes
* checklist
* execucao
* frota
* financeiro
* relatorios
* auditoria

Neste lote, apenas **auth, users e auditoria precisam de implementação real**.

Os demais módulos podem existir apenas como estrutura inicial.

---

# Banco de dados

Configurar:

* conexão PostgreSQL
* migrations automáticas
* suporte a UUID

Criar migrations iniciais para:

### perfis

Campos:

* id (UUID)
* nome
* descricao
* ativo
* created_at
* updated_at

### usuarios

Campos:

* id (UUID)
* nome
* email
* senha_hash
* perfil_id
* ativo
* created_at
* updated_at

Relacionamento:
usuarios.perfil_id -> perfis.id

### auditoria

Campos:

* id
* entidade
* entidade_id
* acao
* valor_anterior (json opcional)
* valor_novo (json opcional)
* usuario_id
* created_at

---

# Seeds obrigatórios

Criar seed inicial para perfis:

ADMINISTRADOR
COORDENADOR_OPERACIONAL
PILOTO
TECNICO
FINANCEIRO

Criar também um usuário inicial:

nome: Administrador
email: [admin@admin.com](mailto:admin@admin.com)
senha: admin123
perfil: ADMINISTRADOR

---

# Autenticação

Implementar:

* login por email e senha
* geração de token de sessão
* middleware de autenticação
* proteção de rotas privadas

Requisitos:

* usuário inativo não pode autenticar
* senha deve ser armazenada com hash seguro
* erro claro para login inválido

---

# Controle de acesso (RBAC)

Implementar middleware que valide o perfil do usuário.

Regras básicas:

* ADMINISTRADOR tem acesso total
* demais perfis acessam apenas rotas autorizadas

Neste lote, apenas estruturar o mecanismo.

---

# Frontend

Criar aplicação web responsiva.

Implementar:

### Tela de Login

Campos:

* email
* senha

Ações:

* autenticar
* redirecionar para dashboard

---

### Layout base da aplicação

Criar:

* barra lateral de navegação
* header superior
* área principal de conteúdo

Menu inicial (placeholder):

* Dashboard
* Cadastros
* Ordens de Serviço
* Missões
* Frota
* Financeiro
* Relatórios
* Administração

Alguns itens podem aparecer apenas para perfis específicos.

---

### Dashboard inicial

Implementar dashboard simples com:

* mensagem de boas-vindas
* identificação do usuário logado
* perfil do usuário

Widgets podem ser placeholders neste lote.

---

# Componentes reutilizáveis

Criar base para:

### Tabela padrão

* paginação
* ordenação simples
* cabeçalhos configuráveis

### Formulário padrão

* validação básica
* mensagens de erro

### Modal padrão

---

# Componente de geolocalização

Criar componente reutilizável:

LocationMapEmbed

Parâmetros:

* latitude
* longitude
* title
* height (opcional)
* fallbackText (opcional)

Comportamento:

Se latitude e longitude forem válidas:

* renderizar mapa embutido usando iframe

Se não forem válidas:

* mostrar mensagem amigável de fallback

Este componente será usado posteriormente em:

* propriedades
* talhões
* missões

Não implementar mapas interativos nesta fase.

---

# Auditoria

Criar infraestrutura de auditoria básica.

Requisitos:

* registrar ações importantes
* registrar usuário responsável
* registrar timestamp

Não é necessário aplicar auditoria completa neste lote, apenas preparar a estrutura.

---

# Requisitos de qualidade

O código gerado deve:

* seguir organização modular
* separar camadas de domínio
* usar boas práticas de segurança
* ter validações básicas no backend
* evitar lógica de negócio complexa neste lote
* preparar terreno para os próximos módulos

---

# O que NÃO deve ser implementado neste lote

Não implementar ainda:

* cadastros mestres
* ordens de serviço
* missões
* checklist
* execução operacional
* financeiro
* relatórios
* manutenção de drones
* lógica de planejamento de missão

Apenas criar a infraestrutura necessária.

---

# Entregáveis esperados

Ao final da implementação, informe:

1. estrutura de diretórios criada
2. migrations criadas
3. tabelas criadas no banco
4. endpoints de autenticação
5. componentes frontend criados
6. estrutura RBAC implementada
7. como iniciar o sistema localmente
8. variáveis de ambiente necessárias

---

# Critério de sucesso do Lote 0

O lote será considerado concluído quando for possível:

* iniciar o backend
* iniciar o frontend
* conectar ao PostgreSQL
* executar migrations
* executar seeds
* autenticar com usuário admin
* acessar dashboard autenticado
* ver layout base da aplicação
* ver componente de mapa disponível no código

Sem erros críticos no startup do sistema.
