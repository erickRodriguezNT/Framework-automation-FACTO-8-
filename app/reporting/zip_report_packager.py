"""
zip_report_packager.py - Empaquetador de evidencia en ZIP para reporting.

Wrapper de ZipService para la capa de reporting.

Uso:
    from app.reporting.zip_report_packager import ZipReportPackager
    packager = ZipReportPackager()
    zip_path = packager.pack(evidence_dir, output_zip)
"""
from pathlib import Path

from app.services.zip_service import ZipService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ZipReportPackager:
    """
    Empaquetador de evidencia en ZIP para el framework de reporting FACTO.
    """

    def __init__(self) -> None:
        self._service = ZipService()

    def pack(self, evidence_dir: Path, output_zip: Path) -> Path:
        """
        Empaqueta el directorio de evidencia en un ZIP.

        Args:
            evidence_dir: Directorio con artefactos de evidencia.
            output_zip:   Ruta del ZIP de salida.

        Returns:
            Path del ZIP generado.
        """
        return self._service.empaquetar(evidence_dir, output_zip)
