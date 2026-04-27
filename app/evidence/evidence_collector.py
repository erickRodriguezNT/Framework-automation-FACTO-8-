"""
evidence_collector.py - Colector de evidencia al cierre de un escenario.

Recopila todos los artefactos de evidencia de una ejecución:
- Screenshots tomados durante el flujo
- Archivos descargados (PDF, XML)
- Datos del execution_context

Se ejecuta en el teardown del fixture 'driver' en conftest.py.

Uso:
    from app.evidence.evidence_collector import EvidenceCollector
    collector = EvidenceCollector(context, output_dir)
    collector.collect()
"""
from pathlib import Path

from app.utils.logger import get_logger

logger = get_logger(__name__)


class EvidenceCollector:
    """
    Colector de evidencia al cierre de un escenario de prueba.

    Centraliza la recopilación y organización de artefactos
    generados durante una ejecución de flujo.
    """

    def __init__(self, context, output_dir: Path | None = None) -> None:
        """
        Args:
            context:    ExecutionContext de la ejecución.
            output_dir: Directorio raíz de outputs. Default: Path('outputs').
        """
        self.context = context
        self.output_dir = output_dir or Path("outputs")

    def collect(self) -> dict:
        """
        Recopila todos los artefactos de evidencia.

        Returns:
            Resumen de artefactos recopilados: {tipo: lista_de_paths}.
        """
        logger.info(
            f"Recopilando evidencia para ejecución: {self.context.execution_id} "
            f"flujo: {self.context.flujo_actual}"
        )

        resumen = {
            "screenshots":         self._collect_screenshots(),
            "archivos_generados":  list(self.context.archivos_generados.keys()),
            "pasos_total":         len(self.context.pasos_ejecutados),
            "estado":              self.context.estado,
        }

        logger.debug(f"Evidencia recopilada: {resumen}")
        return resumen

    def _collect_screenshots(self) -> list[str]:
        """Lista los screenshots en el directorio de evidencia del contexto."""
        evidence_dir = Path(getattr(self.context, "evidence_dir", ""))
        if not evidence_dir.exists():
            return []
        return [str(p) for p in sorted(evidence_dir.glob("*.png"))]

    def generate_reports(self) -> None:
        """
        Genera todos los reportes de evidencia llamando al ReportService.

        Se ejecuta automáticamente en el teardown si el contexto
        está en estado 'exitoso' o 'fallido'.
        """
        try:
            from app.services.report_service import ReportService
            service = ReportService(self.output_dir)
            artefactos = service.generar_evidencia_completa(self.context)
            logger.info(f"Reportes de evidencia generados: {list(artefactos.keys())}")
        except Exception as exc:
            logger.warning(f"Error al generar reportes de evidencia: {exc}")
