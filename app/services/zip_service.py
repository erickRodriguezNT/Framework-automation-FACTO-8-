"""
zip_service.py - Servicio de empaquetado de evidencia en archivo ZIP.

Empaqueta todos los archivos de evidencia de una ejecución
(PDFs, XMLs, screenshots, JSONs) en un único archivo ZIP.

Uso:
    from app.services.zip_service import ZipService
    service = ZipService()
    zip_path = service.empaquetar(evidence_dir, output_zip)
"""
import zipfile
from pathlib import Path

from app.utils.logger import get_logger

logger = get_logger(__name__)


class ZipService:
    """
    Servicio de empaquetado de evidencia de ejecución en ZIP.
    """

    def empaquetar(
        self,
        directorio: Path,
        output_zip: Path,
        patron: str = "**/*",
    ) -> Path:
        """
        Empaqueta todos los archivos del directorio en un ZIP.

        Args:
            directorio:  Directorio raíz de evidencia a empaquetar.
            output_zip:  Ruta destino del archivo ZIP.
            patron:      Glob pattern para filtrar archivos. Default: '**/*'.

        Returns:
            Path del ZIP generado.
        """
        if not directorio.exists():
            logger.warning(f"Directorio de evidencia no encontrado: {directorio}")
            directorio.mkdir(parents=True, exist_ok=True)

        output_zip.parent.mkdir(parents=True, exist_ok=True)

        archivos = [f for f in directorio.glob(patron) if f.is_file()]
        logger.info(f"Empaquetando {len(archivos)} archivos en {output_zip.name}")

        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for archivo in archivos:
                arcname = archivo.relative_to(directorio)
                zf.write(archivo, arcname)
                logger.debug(f"  + {arcname}")

        logger.info(f"ZIP generado: {output_zip}")
        return output_zip

    def empaquetar_archivos(
        self,
        archivos: list[Path],
        output_zip: Path,
        base_dir: Path | None = None,
    ) -> Path:
        """
        Empaqueta una lista específica de archivos en un ZIP.

        Args:
            archivos:   Lista de Paths a empaquetar.
            output_zip: Ruta destino del ZIP.
            base_dir:   Directorio base para calcular nombres relativos.

        Returns:
            Path del ZIP generado.
        """
        output_zip.parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            for archivo in archivos:
                if not archivo.exists():
                    logger.warning(f"Archivo no encontrado al empaquetar: {archivo}")
                    continue
                arcname = archivo.relative_to(base_dir) if base_dir else archivo.name
                zf.write(archivo, arcname)

        logger.info(f"ZIP con {len(archivos)} archivos generado: {output_zip}")
        return output_zip
