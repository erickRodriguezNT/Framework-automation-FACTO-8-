"""
pdf_report_builder.py - Constructor de reportes PDF (wrapper de PDFService).

Delega la generación del PDF al PDFService para mantener
la responsabilidad de construcción del documento en el servicio.

Uso:
    from app.reporting.pdf_report_builder import PDFReportBuilder
    builder = PDFReportBuilder()
    path = builder.build(execution_context, output_path)
"""
from pathlib import Path

from app.services.pdf_service import PDFService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PDFReportBuilder:
    """
    Wrapper de PDFService para la capa de reporting del framework.
    """

    def __init__(self) -> None:
        self._service = PDFService()

    def build(self, context, output_path: Path) -> Path:
        """
        Genera el PDF de evidencia de la ejecución.

        Args:
            context:     ExecutionContext con los datos de la ejecución.
            output_path: Ruta destino del PDF.

        Returns:
            Path del PDF generado.
        """
        return self._service.generar_reporte(context, output_path)
