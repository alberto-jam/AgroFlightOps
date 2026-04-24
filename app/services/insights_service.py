"""Business logic for AI-powered telemetry insights via Amazon Bedrock."""

import json
import logging
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

from app.schemas.telemetria import InsightResponse, TelemetriaResumoResponse
from app.services.telemetria_service import TelemetriaService

logger = logging.getLogger(__name__)

MODEL_ID = "amazon.nova-lite-v1:0"


class InsightsService:
    """Service that generates textual insights from telemetry summaries using Bedrock."""

    def __init__(self, telemetria_service: TelemetriaService) -> None:
        self.telemetria_service = telemetria_service
        self.bedrock = boto3.client("bedrock-runtime")

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def gerar_insight(self, missao_id: int) -> InsightResponse:
        """Retrieve the mission summary and invoke Bedrock to generate an insight."""
        resumo = self.telemetria_service.get_resumo(missao_id)
        prompt = self._build_prompt(resumo)

        try:
            response = self.bedrock.invoke_model(
                modelId=MODEL_ID,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(
                    {
                        "messages": [
                            {"role": "user", "content": [{"text": prompt}]},
                        ],
                        "inferenceConfig": {
                            "maxTokens": 1024,
                            "temperature": 0.7,
                        },
                    }
                ),
            )
            result = json.loads(response["body"].read())
            insight_text = result["output"]["message"]["content"][0]["text"]
        except (ClientError, KeyError, Exception) as exc:
            logger.error("Bedrock invocation failed: %s", exc)
            raise BedrockError(
                "Falha na geração de insights via IA"
            ) from exc

        return InsightResponse(
            missao_id=missao_id,
            insight=insight_text,
            model_id=MODEL_ID,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    # ------------------------------------------------------------------
    # Prompt builder
    # ------------------------------------------------------------------

    def _build_prompt(self, resumo: TelemetriaResumoResponse) -> str:
        """Build a structured prompt in Portuguese for Bedrock."""
        return (
            "Você é um analista especializado em operações de pulverização agrícola com drones DJI Agras.\n"
            "\n"
            "Analise o seguinte resumo de telemetria de uma missão e forneça:\n"
            "1. Avaliação geral da qualidade operacional (score médio e significado)\n"
            "2. Análise de anomalias detectadas e possíveis causas\n"
            "3. Recomendações práticas para melhorar a operação\n"
            "4. Alertas de segurança se aplicável\n"
            "\n"
            "Resumo da Missão:\n"
            f"- ID do Voo: {resumo.flight_id}\n"
            f"- Data: {resumo.dt}\n"
            f"- Total de Pontos de Telemetria: {resumo.points}\n"
            f"- Distância Total: {resumo.distance_m:.0f} metros\n"
            f"- Score Médio: {resumo.avg_score:.1f}/100\n"
            f"- Bateria Mínima: {resumo.min_battery}%\n"
            f"- Pontos com Anomalia: {resumo.anomaly_points} de {resumo.points}\n"
            "\n"
            "Responda em português brasileiro, de forma objetiva e técnica."
        )


class BedrockError(Exception):
    """Raised when Bedrock invocation fails — maps to HTTP 502."""

    def __init__(self, message: str = "Falha na geração de insights via IA"):
        self.message = message
        super().__init__(self.message)
