"""
data_service.py - Servicio de carga y gestión de datos de prueba.

Carga los archivos JSON de test_data y los entrega listos
para ser usados por los flujos y step definitions.

Uso:
    from app.services.data_service import DataService
    service = DataService()
    datos = service.load("factura", "factura_valida")
"""
import json
from pathlib import Path

from app.utils.exceptions import ConfigurationError
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Directorio raíz de test_data relativo al proyecto
# tests/test_data/<modulo>/<archivo>.json
_TEST_DATA_ROOT = Path(__file__).parents[2] / "tests" / "test_data"


class DataService:
    """
    Servicio de carga de datos de prueba desde archivos JSON.
    """

    def __init__(self, test_data_root: Path | None = None) -> None:
        self._root = test_data_root or _TEST_DATA_ROOT

    def load(self, modulo: str, archivo: str) -> dict:
        """
        Carga un archivo JSON de test_data.

        Args:
            modulo:  Sub-directorio dentro de test_data (ej. 'factura').
            archivo: Nombre del archivo sin extensión (ej. 'factura_valida').

        Returns:
            Diccionario con los datos del JSON.

        Raises:
            ConfigurationError: Si el archivo no existe o no es JSON válido.
        """
        path = self._root / modulo / f"{archivo}.json"
        if not path.exists():
            raise ConfigurationError(
                f"Archivo de datos no encontrado: {path}. "
                f"Verificar que tests/test_data/{modulo}/{archivo}.json existe."
            )

        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            logger.debug(f"Datos cargados desde: {path}")
            return data
        except json.JSONDecodeError as exc:
            raise ConfigurationError(f"JSON inválido en {path}: {exc}") from exc

    def load_all(self, modulo: str) -> dict[str, dict]:
        """
        Carga todos los archivos JSON de un módulo.

        Args:
            modulo: Sub-directorio dentro de test_data.

        Returns:
            Diccionario con {nombre_archivo: datos}.
        """
        modulo_dir = self._root / modulo
        if not modulo_dir.exists():
            return {}

        result = {}
        for json_file in modulo_dir.glob("*.json"):
            try:
                result[json_file.stem] = self.load(modulo, json_file.stem)
            except ConfigurationError as exc:
                logger.warning(f"No se pudo cargar {json_file}: {exc}")

        return result
