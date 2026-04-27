"""
pdf_service.py - Servicio de generación de reportes PDF con ReportLab.

Genera el reporte de evidencia en formato PDF con:
- Encabezado del proyecto (FACTO 8 Automatización)
- Resumen del escenario ejecutado
- Tabla de pasos con estado
- Capturas de pantalla embebidas
- UUID CFDI generado

Uso:
    from app.services.pdf_service import PDFService
    service = PDFService()
    ruta = service.generar_reporte(execution_context, output_path)
"""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.utils.logger import get_logger

logger = get_logger(__name__)

# Paleta de colores del reporte
COLOR_HEADER = colors.HexColor("#1a3c6e")    # Azul corporativo
COLOR_EXITOSO = colors.HexColor("#2d7a27")   # Verde
COLOR_FALLIDO = colors.HexColor("#c0392b")   # Rojo
COLOR_OMITIDO = colors.HexColor("#7f8c8d")   # Gris


class PDFService:
    """
    Servicio de generación de reportes PDF de evidencia de ejecución.
    Utiliza ReportLab para construir el PDF.
    """

    def __init__(self, logo_path: Path | None = None) -> None:
        """
        Args:
            logo_path: Ruta opcional al logo para el encabezado del reporte.
        """
        self.logo_path = logo_path
        self.styles = getSampleStyleSheet()

    def generar_reporte(self, context, output_path: Path) -> Path:
        """
        Genera un PDF de evidencia del escenario ejecutado.

        Args:
            context:     ExecutionContext con los datos de la ejecución.
            output_path: Ruta donde se guardará el PDF.

        Returns:
            Path del PDF generado.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        story = []
        story += self._build_header(context)
        story += self._build_resumen(context)
        story += self._build_tabla_pasos(context)
        story += self._build_archivos(context)
        story += self._build_screenshots(context)

        doc.build(story)
        logger.info(f"Reporte PDF generado: {output_path}")
        return output_path

    def _build_header(self, context) -> list:
        """Construye el encabezado del reporte."""
        elements = []
        titulo = Paragraph(
            "<b>FACTO 8 — Reporte de Ejecución Automatizada</b>",
            self.styles["Title"],
        )
        elements.append(titulo)
        elements.append(Spacer(1, 0.5 * cm))

        subtitulo = Paragraph(
            f"Flujo: <b>{context.flujo_actual}</b> | "
            f"Escenario: <b>{context.escenario_actual}</b>",
            self.styles["Heading2"],
        )
        elements.append(subtitulo)
        elements.append(Spacer(1, 0.5 * cm))
        return elements

    def _build_resumen(self, context) -> list:
        """Construye la sección de resumen del escenario."""
        elements = []
        ctx_dict = context.to_dict()
        estado = ctx_dict.get("estado", "")
        estado_color = "#2d7a27" if estado == "exitoso" else "#c0392b"

        data = [
            ["Execution ID",     ctx_dict.get("execution_id", "")],
            ["Estado",           f'<font color="{estado_color}"><b>{estado.upper()}</b></font>'],
            ["Duración",         f'{ctx_dict.get("duracion_segundos", 0):.1f} s'],
            ["UUID CFDI",        context.get_dato("uuid_cfdi", "—")],
        ]

        tabla = Table(data, colWidths=[5 * cm, 12 * cm])
        tabla.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (0, -1), COLOR_HEADER),
            ("TEXTCOLOR",   (0, 0), (0, -1), colors.white),
            ("FONTNAME",    (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE",    (0, 0), (-1, -1), 10),
            ("GRID",        (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
        ]))

        elements.append(Paragraph("<b>Resumen de Ejecución</b>", self.styles["Heading3"]))
        elements.append(tabla)
        elements.append(Spacer(1, 0.5 * cm))
        return elements

    def _build_tabla_pasos(self, context) -> list:
        """Construye la tabla de pasos ejecutados."""
        elements = [Paragraph("<b>Pasos Ejecutados</b>", self.styles["Heading3"])]

        pasos = context.pasos_ejecutados
        if not pasos:
            elements.append(Paragraph("Sin pasos registrados.", self.styles["Normal"]))
            elements.append(Spacer(1, 0.5 * cm))
            return elements

        headers = ["Paso", "Estado", "Detalle"]
        rows = [headers]
        for paso in pasos:
            rows.append([
                paso.get("nombre", ""),
                paso.get("estado", "").upper(),
                str(paso.get("detalle", ""))[:60],
            ])

        tabla = Table(rows, colWidths=[6 * cm, 3 * cm, 8 * cm])
        tabla.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, 0), COLOR_HEADER),
            ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
            ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, -1), 9),
            ("GRID",        (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("VALIGN",      (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (1, 0), (-1, -1), [colors.white, colors.HexColor("#f9f9f9")]),
        ]))

        elements.append(tabla)
        elements.append(Spacer(1, 0.5 * cm))
        return elements

    def _build_archivos(self, context) -> list:
        """Lista los archivos generados registrados en el contexto."""
        elements = [Paragraph("<b>Archivos Generados</b>", self.styles["Heading3"])]
        archivos = context.archivos_generados

        if not archivos:
            elements.append(Paragraph("Sin archivos registrados.", self.styles["Normal"]))
            elements.append(Spacer(1, 0.5 * cm))
            return elements

        for tipo, ruta in archivos.items():
            elements.append(
                Paragraph(f"• <b>{tipo.upper()}</b>: {ruta}", self.styles["Normal"])
            )
        elements.append(Spacer(1, 0.5 * cm))
        return elements

    def _build_screenshots(self, context) -> list:
        """Embebe los screenshots de evidencia (máximo 10)."""
        elements = [Paragraph("<b>Capturas de Pantalla</b>", self.styles["Heading3"])]

        evidence_dir = getattr(context, "evidence_dir", None)
        if evidence_dir is None or not Path(evidence_dir).exists():
            elements.append(Paragraph("Sin capturas de pantalla.", self.styles["Normal"]))
            return elements

        screenshots = sorted(Path(evidence_dir).glob("*.png"))[:10]
        if not screenshots:
            elements.append(Paragraph("Sin capturas de pantalla.", self.styles["Normal"]))
            return elements

        for screenshot in screenshots:
            try:
                img = Image(str(screenshot), width=15 * cm, height=9 * cm)
                elements.append(Paragraph(f"<i>{screenshot.name}</i>", self.styles["Normal"]))
                elements.append(img)
                elements.append(Spacer(1, 0.3 * cm))
            except Exception as exc:
                logger.warning(f"No se pudo embeber screenshot {screenshot}: {exc}")

        return elements
