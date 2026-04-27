"""
base_flow.py - Clase base abstracta para todos los Flows del framework FACTO 8.

Los Flows encapsulan la lógica funcional completa de un proceso de negocio.
Coordinan múltiples Page Objects para completar un flujo de principio a fin.

REGLA ARQUITECTÓNICA:
  - Los Flows coordinan Page Objects. No usan Selenium directamente.
  - Los Steps de pytest-bdd solo llaman Flows, nunca Pages directamente.
  - La lógica de negocio completa vive aquí, no en Page Objects.

Cada Flow concreto hereda de BaseFlow e implementa el método `run()`.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional

from selenium.webdriver.remote.webdriver import WebDriver

from app.core.execution_context import ExecutionContext
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BaseFlow(ABC):
    """
    Clase base abstracta para todos los Flows del framework.

    Proporciona:
    - Acceso al driver y al execution_context
    - Registro de pasos y datos en el contexto
    - Métodos de marcación de estado (exitoso/fallido)
    - Helper para captura de screenshots

    Args:
        driver:  Instancia activa de WebDriver.
        context: ExecutionContext del escenario actual.
    """

    def __init__(self, driver: WebDriver, context: ExecutionContext):
        self.driver = driver
        self.context = context
        self.flow_name: str = self.__class__.__name__
        logger.info(f"[FLOW] Inicializado: {self.flow_name}")

    @abstractmethod
    def run(self, **kwargs) -> dict:
        """
        Ejecuta el flujo completo de negocio.

        Cada subclase implementa la secuencia de pasos que componen
        el proceso de negocio (login, navegación, captura de datos, etc.).

        Args:
            **kwargs: Datos de entrada para el flujo (test data).

        Returns:
            Diccionario con los resultados del flujo:
            {
                "estado":       "exitoso" | "fallido",
                "flujo":        str,
                "execution_id": str,
                "datos":        dict,       # datos generados (UUID, folio, etc.)
                "error":        str | None  # mensaje de error si falló
            }
        """
        ...

    # ------------------------------------------------------------------
    # Registro de pasos y datos
    # ------------------------------------------------------------------

    def _registrar_inicio(self) -> None:
        """Registra el inicio del flujo en el contexto."""
        logger.info(f"[FLOW] Iniciando: {self.flow_name}")
        self.context.set_flujo(self.flow_name)
        self.context.registrar_paso(f"{self.flow_name}_inicio", "en_progreso")

    def _registrar_paso(
        self,
        nombre: str,
        estado: str = "exitoso",
        detalle: str = "",
    ) -> None:
        """
        Registra la ejecución de un paso del flujo.

        Args:
            nombre:  Nombre descriptivo del paso.
            estado:  'exitoso' | 'fallido' | 'omitido'
            detalle: Información adicional.
        """
        logger.info(f"[PASO] {nombre}: {estado}" + (f" — {detalle}" if detalle else ""))
        self.context.registrar_paso(nombre, estado, detalle)

    def _guardar_resultado(self, clave: str, valor: Any) -> None:
        """
        Guarda un dato resultado en el contexto de ejecución.

        Útil para persistir UUID CFDI, folios, series, archivos descargados, etc.
        Estos datos pueden ser leídos por flows dependientes en el orchestrator.

        Args:
            clave: Nombre del dato (ej: 'uuid_cfdi', 'folio', 'archivo_pdf').
            valor: Valor del dato.
        """
        self.context.set_dato(clave, valor)
        logger.debug(f"[DATO] {clave}: {valor}")

    def _obtener_dato(self, clave: str, default: Any = None) -> Any:
        """Obtiene un dato del contexto de ejecución."""
        return self.context.get_dato(clave, default)

    # ------------------------------------------------------------------
    # Finalización del flujo
    # ------------------------------------------------------------------

    def _marcar_exitoso(self) -> dict:
        """Marca el flujo como exitoso y retorna el resultado estándar."""
        self.context.marcar_exitoso()
        logger.info(f"[FLOW] Completado exitosamente: {self.flow_name}")
        return {
            "estado":       "exitoso",
            "flujo":        self.flow_name,
            "execution_id": self.context.execution_id,
            "datos":        self.context.datos_dinamicos.copy(),
            "error":        None,
        }

    def _marcar_fallido(self, error: str) -> dict:
        """Marca el flujo como fallido y retorna el resultado de error."""
        self.context.marcar_fallido(error)
        logger.error(f"[FLOW] Fallido: {self.flow_name} — {error}")
        return {
            "estado":       "fallido",
            "flujo":        self.flow_name,
            "execution_id": self.context.execution_id,
            "datos":        self.context.datos_dinamicos.copy(),
            "error":        error,
        }

    # ------------------------------------------------------------------
    # Utilidades comunes
    # ------------------------------------------------------------------

    def _tomar_screenshot(self, nombre_paso: str) -> Optional[str]:
        """
        Captura screenshot del estado actual y lo registra en el contexto.

        Args:
            nombre_paso: Nombre del paso para naming del archivo.

        Returns:
            Ruta al screenshot guardado, o None si falló.
        """
        try:
            from app.evidence.screenshot_manager import ScreenshotManager
            manager = ScreenshotManager(self.driver, self.context)
            path = manager.take(nombre_paso)
            return str(path)
        except Exception as exc:
            logger.warning(f"No se pudo tomar screenshot en '{nombre_paso}': {exc}")
            return None

    def __repr__(self) -> str:
        return f"{self.flow_name}(execution_id={self.context.execution_id[:8]}...)"
