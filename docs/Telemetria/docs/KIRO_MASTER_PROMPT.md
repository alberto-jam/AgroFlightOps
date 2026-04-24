# Prompt Mestre para Kiro - Agrotech DJI Agras Analytics MVP

Você deve implementar/evoluir uma aplicação MVP para análise de logs de voo de drones agrícolas DJI Agras.

## Objetivo

Construir uma solução web + backend AWS para upload, processamento, visualização e análise de telemetria de missões.

## Stack esperada

Frontend:
- Vite + React + TypeScript
- Leaflet ou MapLibre para mapa
- Componentes simples de dashboard

Backend/AWS:
- S3 Raw para upload de logs
- Lambda Python 3.13 para parsing/normalização
- S3 Processed para JSONL/GeoJSON/summary
- Glue Catalog + Athena para consultas
- CloudFormation YAML como IaC

## Regras

- Manter nomes padronizados: `<Projeto>-<Ambiente>-<Recurso>`.
- Usar parâmetros Cliente, Projeto, Ambiente, Autor.
- Tags nos recursos que suportarem.
- IAM mínimo necessário.
- Não usar credenciais fixas.
- Separar raw/processed/frontend.
- Preparar evolução para Parquet, mas MVP pode usar JSONL.

## Funcionalidades do Frontend

1. Tela principal com cards:
   - total de pontos
   - score médio
   - bateria mínima
   - pontos anômalos
   - distância percorrida
2. Mapa com linha de voo e pontos amostrados.
3. Tabela de anomalias.
4. Campo para informar URL pública/assinada do GeoJSON ou carregar arquivo local de demonstração.

## Entrada canônica

Cada registro de telemetria deve aceitar:

```json
{
  "flight_id": "AGRAST40_DEMO_20260420_140000",
  "timestamp": "2026-04-20T14:00:00Z",
  "drone_model": "DJI Agras T40",
  "drone_serial": "AGT40-DEMO-0001",
  "pilot_id": "OPERADOR_DEMO_01",
  "latitude": -19.9200,
  "longitude": -44.0500,
  "altitude_m": 12.2,
  "height_above_ground_m": 3.2,
  "speed_mps": 5.3,
  "battery_percent": 90,
  "gps_satellites": 18,
  "signal_strength_percent": 92,
  "spray_on": true,
  "flow_l_min": 4.2,
  "tank_level_percent": 80.0,
  "coverage_width_m": 7.0
}
```

## Critérios de aceite

- CloudFormation provisiona S3, Lambda, Glue DB, Athena WorkGroup e EventBridge Rule.
- Upload em `incoming/` aciona Lambda.
- Lambda gera JSONL, GeoJSON e summary.
- Athena consegue consultar a tabela usando projection.
- Frontend renderiza o GeoJSON de demonstração.
- Código deve ser limpo, modular e documentado.
