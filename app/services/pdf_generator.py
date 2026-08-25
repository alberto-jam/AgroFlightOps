"""PDF generator for Relatório de Medição ROP."""

from datetime import date
from decimal import Decimal
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class MedicaoRopPdfGenerator:
    """Generates a PDF report for Medição ROP following the Documento_Exemplo layout."""

    def gerar(
        self,
        cliente_nome: str,
        data_inicial: date,
        data_final: date,
        missoes: list[dict],
        total_area: Decimal,
    ) -> bytes:
        """Generate the measurement report PDF.

        Args:
            cliente_nome: Client name displayed in the header.
            data_inicial: Start date of the measurement period.
            data_final: End date of the measurement period.
            missoes: List of dicts with keys: codigo, propriedade_nome,
                     talhao_nome, area_realizada, encerrado_tecnicamente_em.
            total_area: Sum of area_realizada across all missions.

        Returns:
            PDF content as bytes.
        """
        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=1.5 * cm,
            rightMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
        )

        elements = self._build_elements(
            cliente_nome, data_inicial, data_final, missoes, total_area
        )

        doc.build(elements)

        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    def _build_elements(
        self,
        cliente_nome: str,
        data_inicial: date,
        data_final: date,
        missoes: list[dict],
        total_area: Decimal,
    ) -> list:
        """Build the list of Platypus flowables for the PDF."""
        styles = getSampleStyleSheet()
        elements: list = []

        # --- Custom styles ---
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Heading1"],
            fontSize=16,
            alignment=1,  # center
            spaceAfter=6 * mm,
            textColor=colors.HexColor("#1a5276"),
        )

        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Heading2"],
            fontSize=12,
            alignment=1,  # center
            spaceAfter=4 * mm,
            textColor=colors.HexColor("#2c3e50"),
        )

        info_style = ParagraphStyle(
            "InfoStyle",
            parent=styles["Normal"],
            fontSize=10,
            alignment=1,  # center
            spaceAfter=2 * mm,
        )

        # --- Header ---
        elements.append(Paragraph("Vista Agrotech", title_style))
        elements.append(
            Paragraph("Relatório de Medição", subtitle_style)
        )
        elements.append(Spacer(1, 4 * mm))

        # Client name
        elements.append(
            Paragraph(f"<b>Cliente:</b> {cliente_nome}", info_style)
        )

        # Period
        periodo_texto = (
            f"<b>Período:</b> {data_inicial.strftime('%d/%m/%Y')} a "
            f"{data_final.strftime('%d/%m/%Y')}"
        )
        elements.append(Paragraph(periodo_texto, info_style))
        elements.append(Spacer(1, 8 * mm))

        # --- Missions table ---
        elements.append(self._build_table(missoes, total_area))

        return elements

    def _build_table(self, missoes: list[dict], total_area: Decimal) -> Table:
        """Build the missions table with header and totalization row."""
        # Table header
        header = ["Código", "Propriedade", "Talhão", "Área (ha)", "Data Encerramento"]

        # Table data rows
        data_rows: list[list[str]] = [header]
        for missao in missoes:
            area = missao.get("area_realizada")
            area_str = f"{area:.4f}" if area is not None else "—"

            data_enc = missao.get("encerrado_tecnicamente_em")
            if data_enc is not None:
                if hasattr(data_enc, "strftime"):
                    data_enc_str = data_enc.strftime("%d/%m/%Y")
                else:
                    data_enc_str = str(data_enc)
            else:
                data_enc_str = "—"

            data_rows.append([
                missao.get("codigo", ""),
                missao.get("propriedade_nome", ""),
                missao.get("talhao_nome", ""),
                area_str,
                data_enc_str,
            ])

        # Totalization row
        data_rows.append([
            "",
            "",
            "TOTAL",
            f"{total_area:.4f}",
            "",
        ])

        # Column widths (A4 usable width ~ 18cm with 1.5cm margins each side)
        col_widths = [3 * cm, 4.5 * cm, 4 * cm, 2.5 * cm, 4 * cm]

        table = Table(data_rows, colWidths=col_widths)

        # Table styling
        style_commands = [
            # Header row
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a5276")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("TOPPADDING", (0, 0), (-1, 0), 8),
            # Data rows
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
            ("TOPPADDING", (0, 1), (-1, -1), 5),
            # Alignment for area column (right-aligned)
            ("ALIGN", (3, 1), (3, -1), "RIGHT"),
            # Alignment for date column (center)
            ("ALIGN", (4, 1), (4, -1), "CENTER"),
            # Grid
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bdc3c7")),
            # Alternating row colors
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f2f4f4")]),
            # Total row styling
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#eaf2f8")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, -1), (-1, -1), 9),
            ("LINEABOVE", (0, -1), (-1, -1), 1.5, colors.HexColor("#1a5276")),
        ]

        table.setStyle(TableStyle(style_commands))
        return table
