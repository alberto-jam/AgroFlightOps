# Agrotech DJI Agras Analytics MVP - Next Level

MVP demonstrável para ingestão, processamento, análise e visualização de telemetria de missões de drones DJI Agras.

## Objetivo

Permitir que logs pós-missão sejam carregados em um Data Lake AWS para geração de relatórios operacionais, mapas de trajeto, score de missão e análises de eficiência.

## Componentes

- S3 Raw: recebimento de arquivos JSON/CSV normalizados ou logs convertidos.
- Lambda Processor: normaliza, calcula métricas, gera GeoJSON e dados particionados.
- S3 Processed: armazenamento analítico em JSONL particionado para MVP.
- Glue Data Catalog: banco e tabela externa.
- Athena: consultas SQL e views analíticas.
- S3 Frontend: site estático React/Vite para dashboard e mapa.
- Bedrock Ready: prompts e estrutura para análise textual por IA.

> Nota: esta versão evita dependências pesadas como pandas/pyarrow na Lambda para simplificar o deploy inicial. Para produção, recomenda-se evoluir para Parquet com Glue ETL ou Lambda container image.

## Estrutura

```text
infra/cloudformation.yaml
lambda/processor/processor.py
athena/create_tables.sql
athena/views.sql
data/sample_agras_flight_5000.json
frontend/
docs/KIRO_MASTER_PROMPT.md
docs/ARCHITECTURE.md
scripts/deploy.sh
```

## Fluxo

1. Upload do arquivo em `s3://<raw-bucket>/incoming/`.
2. Evento S3 aciona Lambda.
3. Lambda calcula score, anomalias e métricas.
4. Saída analítica gravada em `processed/telemetry/dt=YYYY-MM-DD/flight_id=.../*.jsonl`.
5. GeoJSON gravado em `processed/geojson/dt=YYYY-MM-DD/flight_id=.../track.geojson`.
6. Athena consulta os dados particionados.
7. Frontend consome o GeoJSON e pode exibir KPIs via API futura ou arquivos estáticos.

## Deploy resumido

```bash
cd scripts
chmod +x deploy.sh
./deploy.sh agrotech dev us-east-1
```

Depois, envie o dataset exemplo:

```bash
aws s3 cp ../data/sample_agras_flight_5000.json s3://agrotech-dev-agras-raw/incoming/sample_agras_flight_5000.json
```

