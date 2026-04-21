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
