# Plano de Implementação: Drone Telemetry Analytics

## Visão Geral

Implementação incremental do pipeline de telemetria de drones no AgroFlightOps: infraestrutura SAM (S3, Lambda, EventBridge, Glue, Athena), Lambda Processor, endpoints REST (upload, consulta, insights IA), e aba de telemetria no frontend com mapa Leaflet. Cada tarefa constrói sobre a anterior, com checkpoints de validação.

## Tarefas

- [x] 1. Adicionar recursos de infraestrutura de telemetria ao template SAM
  - [x] 1.1 Adicionar parâmetros e buckets S3 (Raw, Processed, Athena Results) ao `template.yaml`
    - Criar parâmetros `TelemetriaRawBucketName` e `TelemetriaProcessedBucketName` (opcionais)
    - Definir `TelemetriaRawBucket` com `EventBridgeConfiguration` habilitado
    - Definir `TelemetriaProcessedBucket` e `TelemetriaAthenaResultsBucket`
    - Todos os nomes de recursos devem incluir `${Environment}` como sufixo
    - _Requisitos: 1.1, 1.2, 1.8_

  - [x] 1.2 Adicionar Lambda Processor, IAM Role e EventBridge Rule ao `template.yaml`
    - Definir `TelemetriaProcessorRole` com permissões S3 read (Raw), S3 write (Processed) e CloudWatch Logs
    - Definir `TelemetriaProcessorFunction` como `AWS::Serverless::Function` com runtime Python 3.12, timeout 120s, memória 512MB
    - Definir `TelemetriaEventRule` (EventBridge) para acionar o Lambda quando objeto criado no Raw Bucket com prefixo `incoming/`
    - Definir `AWS::Lambda::Permission` para EventBridge invocar o Lambda
    - Seguir o mesmo padrão SAM da Lambda `AgroFlightOpsFunction` existente
    - _Requisitos: 1.3, 1.4, 1.7, 1.8_

  - [x] 1.3 Adicionar Glue Database e Athena WorkGroup ao `template.yaml`
    - Definir `TelemetriaGlueDatabase` com nome incluindo ambiente
    - Definir `TelemetriaAthenaWorkGroup` com configuração de bucket de resultados
    - _Requisitos: 1.5, 1.6, 1.8_

  - [x] 1.4 Adicionar permissões S3 (Processed) e Bedrock à `LambdaExecutionRole` existente
    - Adicionar política de leitura no `TelemetriaProcessedBucket` para a Lambda FastAPI
    - Adicionar política de invocação do Bedrock (`bedrock:InvokeModel`) para a Lambda FastAPI
    - Adicionar política de escrita no `TelemetriaRawBucket` para a Lambda FastAPI (upload)
    - _Requisitos: 2.1, 5.1, 6.1_

  - [ ]* 1.5 Validar template SAM com `sam validate`
    - Executar `sam validate` e corrigir erros
    - Verificar que todos os recursos de telemetria existem no template
    - _Requisitos: 1.1–1.8_

- [x] 2. Checkpoint — Validar infraestrutura SAM
  - Ensure all tests pass, ask the user if questions arise.

- [x] 3. Implementar Lambda Processor de telemetria
  - [x] 3.1 Criar o código do Lambda Processor adaptado do draft
    - Copiar e adaptar `docs/Telemetria/lambda/processor/processor.py` para `lambda_processor/processor.py`
    - Ajustar para compatibilidade com o padrão SAM do projeto (CodeUri, Handler)
    - Manter as funções: `parse_ts`, `haversine_m`, `anomaly_reasons`, `mission_score`, `normalize_records`, `build_geojson`, `lambda_handler`
    - Garantir que o `lambda_handler` suporta tanto eventos EventBridge quanto formato S3 Records
    - Criar `lambda_processor/requirements.txt` se necessário (apenas boto3 já disponível no runtime)
    - _Requisitos: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

  - [ ]* 3.2 Escrever teste de propriedade — Distância acumulada monotônica
    - **Propriedade 2: Distância acumulada monotonicamente não-decrescente**
    - Usar Hypothesis com `st.lists` de registros com coordenadas válidas
    - Verificar que `cumulative_distance_m` é não-decrescente na sequência
    - **Valida: Requisito 3.1**

  - [ ]* 3.3 Escrever teste de propriedade — Score no intervalo [0, 100]
    - **Propriedade 3: Score de missão limitado ao intervalo [0, 100]**
    - Usar Hypothesis com valores arbitrários de velocidade, bateria, altura, GPS, sinal, spray
    - Verificar que `mission_score` retorna valor entre 0 e 100 inclusive
    - **Valida: Requisito 3.2**

  - [ ]* 3.4 Escrever teste de propriedade — Detecção de anomalias correta
    - **Propriedade 4: Detecção de anomalias é correta em relação aos thresholds**
    - Usar Hypothesis para gerar registros com valores acima/abaixo de cada threshold
    - Verificar bicondicional: razão presente ↔ threshold violado
    - **Valida: Requisito 3.3**

  - [ ]* 3.5 Escrever teste de propriedade — Consistência do sumário
    - **Propriedade 5: Campos do sumário são consistentes com os registros de entrada**
    - Gerar listas não-vazias de registros normalizados
    - Verificar `points`, `distance_m`, `min_battery`, `anomaly_points`, `avg_score`
    - **Valida: Requisito 3.6**

  - [ ]* 3.6 Escrever teste de propriedade — Normalização de tipos determinística
    - **Propriedade 6: Normalização de tipos é determinística**
    - Gerar registros brutos com campos numéricos como strings, ints ou floats
    - Verificar tipos corretos após normalização (float para coordenadas, int para bateria/GPS/sinal)
    - **Valida: Requisito 4.1**

  - [ ]* 3.7 Escrever teste de propriedade — Round-trip JSONL
    - **Propriedade 7: Round-trip de serialização JSONL**
    - Serializar registros normalizados para JSONL, parsear de volta
    - Verificar equivalência com originais
    - **Valida: Requisitos 4.2, 4.3**

  - [ ]* 3.8 Escrever teste de propriedade — GeoJSON válido e round-trip
    - **Propriedade 8: Validade estrutural e round-trip do GeoJSON**
    - Gerar listas não-vazias de registros normalizados com coordenadas válidas
    - Verificar estrutura FeatureCollection, LineString, Points
    - Verificar round-trip JSON serialize/parse
    - **Valida: Requisitos 3.5, 4.4, 4.5**

- [x] 4. Checkpoint — Validar Lambda Processor e testes de propriedade
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implementar schemas Pydantic e serviços backend
  - [x] 5.1 Criar schemas Pydantic em `app/schemas/telemetria.py`
    - Definir `TelemetriaUploadResponse`, `TelemetriaResumoResponse`, `AnomaliaResponse`, `InsightResponse`
    - Seguir o padrão dos schemas existentes em `app/schemas/`
    - _Requisitos: 2.2, 5.1, 5.3, 6.2_

  - [x] 5.2 Criar `app/services/telemetria_service.py`
    - Implementar `TelemetriaService` com métodos: `upload_telemetria`, `get_resumo`, `get_geojson`, `get_anomalias`, `_find_flight_prefix`
    - Upload: validar JSON, verificar campo `records`, gravar no S3 Raw com metadados
    - Consulta: ler arquivos do S3 Processed (summary.json, track.geojson, JSONL filtrado)
    - Usar boto3 S3 client com `list_objects_v2` para descobrir prefixo por missao_id
    - _Requisitos: 2.1, 2.2, 2.4, 2.5, 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x] 5.3 Criar `app/services/insights_service.py`
    - Implementar `InsightsService` com métodos: `gerar_insight`, `_build_prompt`
    - Recuperar sumário via `TelemetriaService.get_resumo`
    - Invocar Bedrock (`bedrock-runtime`, modelo `amazon.nova-lite-v1:0`) com prompt em português
    - Tratar erros do Bedrock retornando HTTP 502
    - _Requisitos: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [ ]* 5.4 Escrever teste de propriedade — Completude do prompt Bedrock
    - **Propriedade 9: Completude do prompt Bedrock**
    - Gerar sumários válidos com Hypothesis
    - Verificar que o prompt contém todos os campos obrigatórios do sumário
    - **Valida: Requisito 6.3**

- [x] 6. Implementar endpoints da API REST
  - [x] 6.1 Criar `app/api/telemetria.py` com endpoints de upload e consulta
    - POST `/missoes/{missao_id}/telemetria` — upload de arquivo JSON
    - GET `/missoes/{missao_id}/telemetria/resumo` — sumário da missão
    - GET `/missoes/{missao_id}/telemetria/geojson` — GeoJSON do trajeto (Content-Type: application/geo+json)
    - GET `/missoes/{missao_id}/telemetria/anomalias` — lista de anomalias
    - Validar existência da missão (404), validar JSON (422)
    - _Requisitos: 2.1, 2.2, 2.3, 2.4, 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x] 6.2 Criar `app/api/insights.py` com endpoint de insights IA
    - GET `/missoes/{missao_id}/insights` — insight gerado via Bedrock
    - Tratar 404 (sem telemetria) e 502 (falha Bedrock)
    - _Requisitos: 6.1, 6.2, 6.4, 6.5_

  - [x] 6.3 Registrar novos routers em `app/main.py`
    - Importar e incluir `telemetria_router` e `insights_router`
    - Seguir o padrão dos routers existentes
    - _Requisitos: 2.1, 5.1, 6.1_

  - [ ]* 6.4 Escrever teste de propriedade — Rejeição de entrada inválida
    - **Propriedade 1: Rejeição de entrada inválida de telemetria**
    - Usar Hypothesis com `st.binary()` e `st.dictionaries()` sem campo "records"
    - Verificar que a validação rejeita e retorna erro sem modificar estado
    - **Valida: Requisito 2.4**

  - [ ]* 6.5 Escrever testes unitários para endpoints de telemetria e insights
    - Upload válido retorna 201; missão inexistente retorna 404; JSON inválido retorna 422
    - Resumo, GeoJSON e anomalias retornam dados corretos (mock S3)
    - Insights: sucesso, Bedrock indisponível (502), sem telemetria (404)
    - _Requisitos: 2.1–2.5, 5.1–5.5, 6.1–6.5_

- [x] 7. Checkpoint — Validar API backend completa
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Documentar SQL do Athena (tabelas e views)
  - [x] 8.1 Criar arquivo de documentação SQL em `docs/Telemetria/athena/README.md`
    - Documentar os comandos SQL de `create_tables.sql` e `views.sql` para execução manual no Athena
    - Incluir instruções de como executar via console Athena ou CLI
    - Referenciar o Glue Database e WorkGroup criados pelo template SAM
    - _Requisitos: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 9. Implementar aba de Telemetria no frontend
  - [x] 9.1 Criar componente `TelemetriaTab` com mapa Leaflet, KPIs e tabela de anomalias
    - Criar componente container que busca dados dos endpoints `/resumo`, `/geojson`, `/anomalias`
    - Renderizar mapa Leaflet com trajeto (LineString) e pontos coloridos por score
    - Exibir cards KPIs: Score Médio, Distância Total, Total Anomalias, Bateria Mínima
    - Exibir tabela de anomalias com colunas: Horário, Tipo, Velocidade, Bateria, Altura, Score
    - Implementar clique em anomalia para centralizar mapa no ponto
    - Exibir spinner durante carregamento e mensagem quando sem telemetria
    - Instalar dependência `leaflet` e `react-leaflet` se necessário
    - _Requisitos: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

  - [x] 9.2 Integrar `TelemetriaTab` no modal de detalhes da missão
    - Adicionar aba "Telemetria" ao modal/drawer existente de detalhes de missão
    - Condicionar exibição à existência de telemetria processada
    - _Requisitos: 8.1_

- [x] 10. Checkpoint final — Validar integração completa
  - Ensure all tests pass, ask the user if questions arise.

## Notas

- Tarefas marcadas com `*` são opcionais e podem ser puladas para um MVP mais rápido
- Cada tarefa referencia requisitos específicos para rastreabilidade
- Checkpoints garantem validação incremental
- Testes de propriedade validam propriedades universais de corretude definidas no design
- Testes unitários validam exemplos específicos e edge cases
- Os comandos SQL do Athena (tabelas e views) devem ser executados manualmente — não são automatizáveis via código
- O código do Lambda Processor em `docs/Telemetria/lambda/processor/processor.py` deve ser adaptado, não copiado literalmente
