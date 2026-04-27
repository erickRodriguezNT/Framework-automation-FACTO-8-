"""
file_service.py - Servicio de gestión de archivos de evidencia y output.

Provee operaciones comunes de sistema de archivos:
- Crear directorios de output por ejecución
- Mover / copiar archivos descargados al directorio correcto
- Listar archivos de un directorio

Uso:
    from app.services.file_service import FileService
    service = FileService(output_dir=Path("outputs"))
    service.ensure_dir("screenshots/exec-001")
"""
import shutil
from pathlib import Path

from app.utils.logger import get_logger

logger = get_logger(__name__)


class FileService:
    """
    Servicio de operaciones de sistema de archivos para el framework.
    """

    def __init__(self, output_dir: Path | None = None) -> None:
        self.output_dir = output_dir or Path("outputs")

    def ensure_dir(self, sub_path: str | Path) -> Path:
        """
        Crea un directorio (y subdirectorios) si no existe.

        Args:
            sub_path: Ruta relativa dentro de output_dir, o absoluta.

        Returns:
            Path absoluto del directorio creado.
        """
        path = (
            Path(sub_path)
            if Path(sub_path).is_absolute()
            else self.output_dir / sub_path
        )
        path.mkdir(parents=True, exist_ok=True)
        return path

    def move_file(self, origen: Path, destino: Path) -> Path:
        """
        Mueve un archivo al directorio de destino.

        Args:
            origen:  Ruta actual del archivo.
            destino: Ruta destino (incluyendo nombre de archivo).

        Returns:
            Path final del archivo.
        """
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(origen), str(destino))
        logger.debug(f"Archivo movido: {origen} → {destino}")
        return destino

    def copy_file(self, origen: Path, destino: Path) -> Path:
        """
        Copia un archivo al directorio de destino.

        Returns:
            Path del archivo copiado.
        """
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(origen), str(destino))
        logger.debug(f"Archivo copiado: {origen} → {destino}")
        return destino

    def list_files(self, directorio: Path, pattern: str = "*") -> list[Path]:
        """
        Lista archivos en un directorio que coincidan con el patrón.

        Args:
            directorio: Directorio a listar.
            pattern:    Glob pattern. Default: '*' (todos los archivos).

        Returns:
            Lista de Paths de los archivos encontrados.
        """
        if not directorio.exists():
            return []
        return sorted(directorio.glob(pattern))

    def delete_file(self, path: Path) -> bool:
        """
        Elimina un archivo si existe.

        Returns:
            True si fue eliminado, False si no existía.
        """
        if path.exists() and path.is_file():
            path.unlink()
            logger.debug(f"Archivo eliminado: {path}")
            return True
        return False
