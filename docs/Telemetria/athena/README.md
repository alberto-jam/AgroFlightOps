# Athena — Tabelas e Views de Telemetria

## Pré-requisitos

Os recursos Glue Database e Athena WorkGroup são criados automaticamente pelo template SAM durante o deploy. Após o deploy, execute os comandos SQL abaixo no console Athena ou via AWS CLI.

- **Glue Database**: `agroflightops_{ambiente}_telemetria`
- **Athena WorkGroup**: `AgroFlightOps-{ambiente}-telemetria`
- **S3 Processed Bucket**: `agroflightops-{ambiente}-telemetria-processed`

## Execução via Console Athena

1. Acesse o console Athena: https://console.aws.amazon.com/athena
2. Selecione o WorkGroup `AgroFlightOps-dev-telemetria`
3. Selecione o Database `agroflightops_dev_telemetria`
4. Execute os comandos SQL abaixo na ordem

## Execução via AWS CLI

```bash
# Criar tabela
aws athena start-query-execution \
  --query-string "$(cat docs/Telemetria/athena/create_tables.sql)" \
  --work-group AgroFlightOps-dev-telemetria \
  --query-execution-context Database=agroflightops_dev_telemetria

# Criar views
aws athena start-query-execution \
  --query-string "$(cat docs/Telemetria/athena/views.sql)" \
  --work-group AgroFlightOps-dev-telemetria \
  --query-execution-context Database=agroflightops_dev_telemetria
```

## Arquivos SQL

- `create_tables.sql` — Tabela externa `agras_telemetry_jsonl` com projeção de partições
- `views.sql` — Views analíticas: `vw_agras_flight_summary`, `vw_agras_anomaly_points`, `vw_agras_spray_efficiency`

## Nota

Ajuste o nome do bucket S3 na LOCATION da tabela se estiver usando um ambiente diferente de `dev`.
