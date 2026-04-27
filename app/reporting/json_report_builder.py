"""
json_report_builder.py - Constructor de reportes JSON de ejecución.

Genera el archivo JSON con el resumen completo de la ejecución,
incluyendo pasos, tiempos, archivos generados y estado final.

Uso:
    from app.reporting.json_report_builder import JSONReportBuilder
    builder = JSONReportBuilder()
    path = builder.build(execution_context, output_path)
"""
import json
from pathlib import Path

from app.utils.logger import get_logger

logger = get_logger(__name__)


class JSONReportBuilder:
    """
    Constructor de reportes JSON para ejecuciones del framework FACTO.
    """

    def build(self, context, output_path: Path) -> Path:
        """
        Genera el archivo JSON de resultados de la ejecución.

        Args:
            context:     ExecutionContext con los datos de la ejecución.
            output_path: Ruta donde se guardará el JSON.

        Returns:
            Path del JSON generado.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = context.to_dict()

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

        logger.info(f"JSON de ejecución generado: {output_path}")
        return output_path
