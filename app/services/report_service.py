"""
report_service.py - Servicio coordinador de generación de reportes.

Orquesta la generación de todos los reportes de una ejecución:
- Reporte PDF de evidencia
- Reporte JSON de resultados
- Empaquetado ZIP

Es el punto de entrada unificado para generar toda la evidencia
al final de un escenario.

Uso:
    from app.services.report_service import ReportService
    service = ReportService(output_dir=Path("outputs"))
    service.generar_evidencia_completa(execution_context)
"""
from pathlib import Path

from app.utils.logger import get_logger

logger = get_logger(__name__)


class ReportService:
    """
    Servicio coordinador de generación de reportes de evidencia.
    """

    def __init__(self, output_dir: Path | None = None) -> None:
        self.output_dir = output_dir or Path("outputs")

    def generar_evidencia_completa(self, context) -> dict[str, Path]:
        """
        Genera todos los artefactos de evidencia para una ejecución.

        Genera:
        - PDF de reporte de ejecución
        - JSON de resultados
        - ZIP con toda la evidencia

        Args:
            context: ExecutionContext de la ejecución.

        Returns:
            Diccionario con rutas de los artefactos generados:
            {'pdf': Path, 'json': Path, 'zip': Path}
        """
        execution_id = context.execution_id
        flujo = context.flujo_actual
        base_dir = self.output_dir / execution_id / flujo

        artefactos: dict[str, Path] = {}

        # --- Reporte PDF ---
        try:
            from app.services.pdf_service import PDFService
            pdf_service = PDFService()
            pdf_path = base_dir / f"reporte_{flujo}_{execution_id[:8]}.pdf"
            pdf_service.generar_reporte(context, pdf_path)
            artefactos["pdf"] = pdf_path
            context.registrar_archivo("reporte_pdf", pdf_path)
        except Exception as exc:
            logger.warning(f"No se pudo generar PDF de evidencia: {exc}")

        # --- Reporte JSON ---
        try:
            import json
            json_path = base_dir / f"resultado_{flujo}_{execution_id[:8]}.json"
            json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(context.to_dict(), f, ensure_ascii=False, indent=2, default=str)
            artefactos["json"] = json_path
            context.registrar_archivo("reporte_json", json_path)
            logger.info(f"JSON de resultados generado: {json_path}")
        except Exception as exc:
            logger.warning(f"No se pudo generar JSON de resultados: {exc}")

        # --- ZIP de evidencia ---
        try:
            from app.services.zip_service import ZipService
            zip_service = ZipService()
            zip_path = self.output_dir / "zip" / f"evidencia_{flujo}_{execution_id[:8]}.zip"
            zip_service.empaquetar(base_dir, zip_path)
            artefactos["zip"] = zip_path
            context.registrar_archivo("evidencia_zip", zip_path)
        except Exception as exc:
            logger.warning(f"No se pudo generar ZIP de evidencia: {exc}")

        return artefactos
