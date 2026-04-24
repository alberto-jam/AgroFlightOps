# Documento de Requisitos — Drone Telemetry Analytics

## Introdução

Este documento define os requisitos para integração de processamento de telemetria de drones, mapas de trajeto, analytics e insights de IA ao sistema AgroFlightOps. A funcionalidade permite que logs pós-missão de drones DJI Agras sejam carregados, processados em um Data Lake AWS, e visualizados em dashboards com KPIs, mapas e análises textuais geradas por IA (Amazon Bedrock).

## Glossário

- **Sistema_Backend**: Aplicação FastAPI do AgroFlightOps que serve a API REST via AWS Lambda + API Gateway
- **Lambda_Processor**: Função AWS Lambda dedicada ao processamento de telemetria, acionada por eventos S3 via EventBridge
- **S3_Raw_Bucket**: Bucket S3 para armazenamento de arquivos brutos de telemetria enviados pelo operador
- **S3_Processed_Bucket**: Bucket S3 para armazenamento de dados processados (JSONL particionado, GeoJSON, sumários)
- **Glue_Catalog**: AWS Glue Data Catalog contendo o banco e tabelas externas para consulta via Athena
- **Athena_Workgroup**: Workgroup do Amazon Athena configurado para consultas analíticas sobre os dados processados
- **Frontend_App**: Aplicação React/Ant Design do AgroFlightOps servida via S3 + CloudFront
- **Bedrock_Service**: Serviço Amazon Bedrock (modelo Claude) utilizado para gerar insights textuais a partir de sumários de telemetria
- **Missao**: Entidade existente no AgroFlightOps representando uma missão de pulverização agrícola
- **Telemetria**: Conjunto de dados de voo coletados durante a execução de uma missão (posição, velocidade, bateria, pulverização, etc.)
- **GeoJSON**: Formato padrão para representação de dados geoespaciais, usado para trajetos de voo
- **Score_Missao**: Pontuação operacional calculada por ponto de telemetria (0–100), baseada em penalidades por anomalias e bônus por operação ideal
- **Anomalia**: Condição operacional fora dos parâmetros ideais detectada em um ponto de telemetria (ex.: velocidade excessiva, bateria baixa, GPS fraco)
- **JSONL**: Formato JSON Lines — um registro JSON por linha, usado para armazenamento particionado compatível com Athena

## Requisitos

### Requisito 1: Infraestrutura de Data Lake para Telemetria

**User Story:** Como administrador do sistema, quero que a infraestrutura de ingestão e processamento de telemetria seja provisionada no template SAM existente, para que o pipeline funcione dentro do mesmo ciclo de CI/CD do AgroFlightOps.

#### Critérios de Aceitação

1. THE template SAM SHALL definir um recurso S3_Raw_Bucket com EventBridge habilitado para notificações de objetos criados no prefixo `incoming/`
2. THE template SAM SHALL definir um recurso S3_Processed_Bucket para armazenamento de dados processados particionados
3. THE template SAM SHALL definir um recurso Lambda_Processor com runtime Python 3.12, timeout de 120 segundos e 512 MB de memória
4. THE template SAM SHALL definir uma regra EventBridge que acione o Lambda_Processor quando um objeto for criado no S3_Raw_Bucket com prefixo `incoming/`
5. THE template SAM SHALL definir um recurso Glue_Catalog com banco de dados para telemetria de drones
6. THE template SAM SHALL definir um recurso Athena_Workgroup com configuração de bucket de resultados
7. THE template SAM SHALL definir uma IAM Role para o Lambda_Processor com permissões de leitura no S3_Raw_Bucket, escrita no S3_Processed_Bucket e escrita em CloudWatch Logs
8. WHEN o parâmetro Environment for alterado, THE template SAM SHALL nomear todos os recursos de telemetria com o sufixo do ambiente correspondente

### Requisito 2: Upload de Telemetria via API

**User Story:** Como piloto ou coordenador operacional, quero enviar o arquivo de log de voo de uma missão via API, para que os dados sejam armazenados no Data Lake e processados automaticamente.

#### Critérios de Aceitação

1. WHEN uma requisição POST for recebida em `/missoes/{missao_id}/telemetria` com um arquivo JSON válido, THE Sistema_Backend SHALL armazenar o arquivo no S3_Raw_Bucket no caminho `incoming/{missao_id}_{timestamp}.json`
2. WHEN o upload for concluído com sucesso, THE Sistema_Backend SHALL retornar status HTTP 201 com o identificador S3 do arquivo armazenado
3. IF a missão referenciada pelo missao_id não existir, THEN THE Sistema_Backend SHALL retornar status HTTP 404 com mensagem descritiva
4. IF o arquivo enviado não for um JSON válido ou não contiver o campo obrigatório `records` (lista de pontos de telemetria), THEN THE Sistema_Backend SHALL retornar status HTTP 422 com mensagem de erro de validação
5. WHEN o arquivo for armazenado no S3_Raw_Bucket, THE Sistema_Backend SHALL incluir metadados S3 com `missao_id`, `uploaded_by` e `uploaded_at`

### Requisito 3: Processamento de Telemetria pelo Lambda Processor

**User Story:** Como sistema, quero que os dados brutos de telemetria sejam processados automaticamente após o upload, para que métricas, anomalias e trajetos estejam disponíveis para consulta.

#### Critérios de Aceitação

1. WHEN um arquivo for criado no S3_Raw_Bucket com prefixo `incoming/`, THE Lambda_Processor SHALL ler o arquivo, normalizar os registros e calcular a distância acumulada entre pontos consecutivos usando a fórmula de Haversine
2. WHEN os registros forem normalizados, THE Lambda_Processor SHALL calcular o Score_Missao para cada ponto com base em penalidades por anomalias e bônus por operação dentro dos parâmetros ideais (altura 3–4m, velocidade 4–6.5 m/s durante pulverização)
3. WHEN os registros forem normalizados, THE Lambda_Processor SHALL detectar anomalias em cada ponto verificando: velocidade acima de 8 m/s, bateria abaixo de 20%, altura abaixo de 2m, altura acima de 5m, satélites GPS abaixo de 10, sinal abaixo de 55%, e pulverização ativa sem fluxo (flow abaixo de 0.1 L/min)
4. WHEN o processamento for concluído, THE Lambda_Processor SHALL gravar os dados normalizados em formato JSONL particionado no S3_Processed_Bucket no caminho `telemetry/dt={data}/flight_id={id}/part-00000.jsonl`
5. WHEN o processamento for concluído, THE Lambda_Processor SHALL gerar um arquivo GeoJSON com LineString do trajeto e pontos amostrados, e gravá-lo no S3_Processed_Bucket no caminho `geojson/dt={data}/flight_id={id}/track.geojson`
6. WHEN o processamento for concluído, THE Lambda_Processor SHALL gerar um arquivo de sumário JSON contendo flight_id, data, total de pontos, distância total, score médio, bateria mínima e total de pontos com anomalia, e gravá-lo no caminho `summary/dt={data}/flight_id={id}/summary.json`
7. IF o arquivo de entrada não puder ser parseado como JSON ou não contiver registros válidos, THEN THE Lambda_Processor SHALL registrar o erro no CloudWatch Logs e encerrar sem gravar dados processados

### Requisito 4: Normalização e Serialização de Telemetria

**User Story:** Como desenvolvedor, quero que a normalização de telemetria seja determinística e reversível, para garantir integridade dos dados no pipeline.

#### Critérios de Aceitação

1. THE Lambda_Processor SHALL normalizar cada registro de telemetria convertendo todos os campos numéricos para os tipos definidos no schema (float para coordenadas/velocidades, int para bateria/satélites/sinal)
2. THE Lambda_Processor SHALL serializar os registros normalizados em formato JSONL onde cada linha é um objeto JSON válido
3. FOR ALL registros normalizados válidos, parsear o JSONL gerado e comparar com os registros originais normalizados SHALL produzir objetos equivalentes (propriedade round-trip)
4. THE Lambda_Processor SHALL gerar GeoJSON válido conforme a especificação RFC 7946, com FeatureCollection contendo um Feature LineString e Features Point amostrados
5. FOR ALL GeoJSON gerados, parsear o JSON e validar a estrutura SHALL produzir um objeto GeoJSON válido com coordenadas numéricas e tipos de geometria corretos (propriedade round-trip)

### Requisito 5: Endpoints de Consulta de Telemetria

**User Story:** Como piloto ou coordenador operacional, quero consultar o resumo, trajeto e anomalias de uma missão via API, para acompanhar a qualidade operacional dos voos.

#### Critérios de Aceitação

1. WHEN uma requisição GET for recebida em `/missoes/{missao_id}/telemetria/resumo`, THE Sistema_Backend SHALL retornar o sumário da missão contendo: flight_id, data, total de pontos, distância em metros, score médio, bateria mínima e total de pontos com anomalia
2. WHEN uma requisição GET for recebida em `/missoes/{missao_id}/telemetria/geojson`, THE Sistema_Backend SHALL retornar o arquivo GeoJSON do trajeto da missão com Content-Type `application/geo+json`
3. WHEN uma requisição GET for recebida em `/missoes/{missao_id}/telemetria/anomalias`, THE Sistema_Backend SHALL retornar a lista de pontos com anomalia contendo: timestamp, latitude, longitude, velocidade, bateria, altura, satélites GPS, sinal, razões da anomalia e score
4. IF a missão referenciada não existir, THEN THE Sistema_Backend SHALL retornar status HTTP 404
5. IF a missão não possuir dados de telemetria processados, THEN THE Sistema_Backend SHALL retornar status HTTP 404 com mensagem indicando que telemetria não foi encontrada para a missão

### Requisito 6: Insights de IA via Amazon Bedrock

**User Story:** Como coordenador operacional, quero receber análises textuais geradas por IA sobre a telemetria de uma missão, para obter recomendações de melhoria operacional sem precisar interpretar dados brutos.

#### Critérios de Aceitação

1. WHEN uma requisição GET for recebida em `/missoes/{missao_id}/insights`, THE Sistema_Backend SHALL recuperar o sumário de telemetria da missão e enviá-lo ao Bedrock_Service para geração de insights textuais
2. WHEN o Bedrock_Service retornar a resposta, THE Sistema_Backend SHALL retornar um objeto JSON contendo: missao_id, texto do insight gerado, modelo utilizado e timestamp da geração
3. THE Sistema_Backend SHALL enviar ao Bedrock_Service um prompt estruturado em português contendo o sumário da missão e instruções para análise de qualidade operacional, recomendações e alertas
4. IF a missão não possuir dados de telemetria processados, THEN THE Sistema_Backend SHALL retornar status HTTP 404 com mensagem indicando que telemetria não foi encontrada
5. IF o Bedrock_Service retornar erro ou estiver indisponível, THEN THE Sistema_Backend SHALL retornar status HTTP 502 com mensagem indicando falha na geração de insights

### Requisito 7: Tabelas e Views Athena para Analytics

**User Story:** Como analista de dados, quero consultar dados de telemetria via SQL no Athena, para gerar relatórios de eficiência operacional e análise de anomalias.

#### Critérios de Aceitação

1. THE Glue_Catalog SHALL conter uma tabela externa `agras_telemetry_jsonl` com schema correspondente aos campos normalizados pelo Lambda_Processor, particionada por `dt` e `flight_id_part`
2. THE Glue_Catalog SHALL utilizar projeção de partições para descoberta automática de novas partições sem necessidade de `MSCK REPAIR TABLE`
3. THE Athena_Workgroup SHALL conter uma view `vw_agras_flight_summary` que agregue por flight_id: horários de início e fim, total de pontos, distância, velocidade média, fluxo médio durante pulverização, bateria mínima e inicial, score médio e total de pontos com anomalia
4. THE Athena_Workgroup SHALL conter uma view `vw_agras_anomaly_points` que filtre pontos com anomalia_count maior que zero, retornando localização, métricas operacionais e razões da anomalia
5. THE Athena_Workgroup SHALL conter uma view `vw_agras_spray_efficiency` que calcule por flight_id: total de pontos, pontos com pulverização, percentual de tempo pulverizando, velocidade média durante pulverização, altura média durante pulverização e score médio durante pulverização

### Requisito 8: Interface de Telemetria no Frontend

**User Story:** Como piloto ou coordenador operacional, quero visualizar a telemetria de uma missão em uma aba dedicada no modal de execução, para acompanhar trajeto, KPIs e anomalias de forma visual.

#### Critérios de Aceitação

1. WHEN o usuário abrir o modal de detalhes de uma missão que possua telemetria processada, THE Frontend_App SHALL exibir uma aba "Telemetria" com mapa de trajeto, KPIs e lista de anomalias
2. THE Frontend_App SHALL renderizar o trajeto da missão em um mapa interativo utilizando a biblioteca Leaflet, exibindo a LineString do GeoJSON e pontos amostrados com cores indicando o score
3. THE Frontend_App SHALL exibir KPIs em cards: Score Médio da Missão, Distância Total (metros), Total de Anomalias e Bateria Mínima
4. THE Frontend_App SHALL exibir uma tabela de anomalias com colunas: Horário, Tipo de Anomalia, Velocidade, Bateria, Altura e Score
5. WHILE os dados de telemetria estiverem sendo carregados, THE Frontend_App SHALL exibir um indicador de carregamento (spinner)
6. IF a missão não possuir dados de telemetria, THE Frontend_App SHALL exibir uma mensagem informativa indicando que nenhuma telemetria foi encontrada para a missão
7. WHEN o usuário clicar em um ponto de anomalia na tabela, THE Frontend_App SHALL centralizar o mapa na localização correspondente e destacar o ponto

