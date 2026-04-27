"""
evidence_naming.py - Convenciones de nombres para archivos de evidencia.

Centraliza la lógica de nomenclatura para:
- Screenshots
- PDFs de evidencia
- XMLs descargados
- ZIPs de empaquetado

Convención: {execution_id}/{flujo}/{escenario}/{paso}_{timestamp}.ext

Uso:
    from app.evidence.evidence_naming import EvidenceNaming
    nombre = EvidenceNaming.screenshot("login_exitoso", context)
    # → "01_login_exitoso_20240601_153045.png"
"""
from datetime import datetime
from pathlib import Path


class EvidenceNaming:
    """
    Utilidades de nomenclatura para archivos de evidencia del framework.
    """

    TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

    @staticmethod
    def timestamp() -> str:
        """Retorna el timestamp actual en formato compacto."""
        return datetime.now().strftime(EvidenceNaming.TIMESTAMP_FORMAT)

    @staticmethod
    def screenshot(paso: str, context=None) -> str:
        """
        Genera el nombre de archivo para un screenshot.

        Args:
            paso:    Nombre del paso (ej. '01_login_exitoso').
            context: ExecutionContext opcional para incluir datos del flujo.

        Returns:
            Nombre de archivo: '{paso}_{timestamp}.png'
        """
        ts = EvidenceNaming.timestamp()
        nombre_limpio = EvidenceNaming._sanitize(paso)
        return f"{nombre_limpio}_{ts}.png"

    @staticmethod
    def reporte_pdf(flujo: str, execution_id: str) -> str:
        """Genera el nombre de archivo para el reporte PDF."""
        return f"reporte_{flujo}_{execution_id[:8]}.pdf"

    @staticmethod
    def resultado_json(flujo: str, execution_id: str) -> str:
        """Genera el nombre de archivo para el JSON de resultados."""
        return f"resultado_{flujo}_{execution_id[:8]}.json"

    @staticmethod
    def evidencia_zip(flujo: str, execution_id: str) -> str:
        """Genera el nombre de archivo para el ZIP de evidencia."""
        return f"evidencia_{flujo}_{execution_id[:8]}.zip"

    @staticmethod
    def xml_descargado(flujo: str, execution_id: str) -> str:
        """Genera el nombre para el XML descargado del portal."""
        return f"{flujo}_{execution_id[:8]}.xml"

    @staticmethod
    def pdf_descargado(flujo: str, execution_id: str) -> str:
        """Genera el nombre para el PDF descargado del portal."""
        return f"{flujo}_{execution_id[:8]}.pdf"

    @staticmethod
    def evidence_dir(base_dir: Path, execution_id: str, flujo: str) -> Path:
        """
        Retorna el directorio de evidencia para una ejecución.

        Estructura: {base_dir}/screenshots/{execution_id}/{flujo}/
        """
        return base_dir / "screenshots" / execution_id / flujo

    @staticmethod
    def _sanitize(nombre: str) -> str:
        """Elimina caracteres no válidos para nombres de archivo."""
        return (
            nombre.replace(" ", "_")
                  .replace("/", "-")
                  .replace("\\", "-")
                  .replace(":", "-")
                  .lower()
        )
