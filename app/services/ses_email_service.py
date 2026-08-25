"""Service for sending emails via Amazon SES."""

import boto3

from app.core.config import settings


class SesEmailService:
    """Sends report download emails via Amazon SES."""

    def __init__(self):
        self.client = boto3.client("ses", region_name=settings.SES_REGION)
        self.sender = settings.SES_SENDER_EMAIL

    def send_relatorio_email(
        self,
        to_addresses: list[str],
        subject: str,
        download_url: str,
        mensagem_personalizada: str | None = None,
    ) -> None:
        """Send an email with the report download link.

        Args:
            to_addresses: List of recipient email addresses.
            subject: Email subject line.
            download_url: Presigned URL for downloading the report.
            mensagem_personalizada: Optional custom message to include before the link.
        """
        body_parts = []
        if mensagem_personalizada:
            body_parts.append(f"<p>{mensagem_personalizada}</p>")
        body_parts.append(
            f'<p>Clique no link abaixo para baixar o relatório:</p>'
            f'<p><a href="{download_url}">Download do Relatório</a></p>'
        )
        body_parts.append(
            "<p><small>Este link expira em 72 horas.</small></p>"
        )

        html_body = "\n".join(body_parts)

        self.client.send_email(
            Source=self.sender,
            Destination={"ToAddresses": to_addresses},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Html": {"Data": html_body, "Charset": "UTF-8"},
                },
            },
        )
