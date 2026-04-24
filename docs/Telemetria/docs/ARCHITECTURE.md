# Arquitetura - Agrotech DJI Agras Analytics MVP

## Visão Geral

A solução transforma logs de voo pós-missão em uma camada analítica para relatórios, mapas de trajeto e análise de eficácia operacional.

```text
Operador / Cliente
   |
   | upload log pós-missão
   v
S3 Raw /incoming
   |
   | EventBridge Object Created
   v
Lambda Processor
   |-- normalização de telemetria
   |-- cálculo de score
   |-- detecção de anomalias
   |-- geração GeoJSON
   v
S3 Processed
   |-- telemetry/dt=.../flight_id=.../*.jsonl
   |-- geojson/dt=.../flight_id=.../track.geojson
   |-- summary/dt=.../flight_id=.../summary.json
   v
Glue Catalog + Athena
   v
QuickSight / Frontend / Bedrock
```

## Decisão técnica do MVP

Para acelerar a demonstração, o Lambda grava JSONL particionado, sem dependências externas. Isso reduz risco de empacotamento. A evolução natural para produção é Parquet via AWS Glue ETL, Lambda container image ou AWS Data Wrangler Layer.

## Métricas calculadas

- distância acumulada
- velocidade média
- bateria mínima
- percentual de tempo pulverizando
- pontos com anomalia
- score operacional por ponto
- score médio da missão

## Anomalias iniciais

- velocidade excessiva
- bateria baixa
- altura baixa/alta
- GPS fraco
- sinal fraco
- pulverização ligada sem fluxo

## Evoluções recomendadas

1. Parser real para log DJI Agras exportado.
2. Conversão para Parquet.
3. API Gateway + Lambda para listar missões e servir KPIs.
4. Bedrock Agent com Action Group sobre Athena.
5. QuickSight para dashboards executivos.
6. Detecção ML de padrões anômalos por operador, talhão e equipamento.
