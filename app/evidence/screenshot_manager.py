"""
screenshot_manager.py - Gestor de capturas de pantalla de evidencia.

Centraliza la toma y guardado de screenshots:
- Nombrado consistente con EvidenceNaming
- Guardado en directorio de evidencia del contexto
- Registro en el execution_context

Uso:
    from app.evidence.screenshot_manager import ScreenshotManager
    mgr = ScreenshotManager(driver, context)
    path = mgr.take("login_exitoso")
"""
from pathlib import Path

from app.evidence.evidence_naming import EvidenceNaming
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ScreenshotManager:
    """
    Gestor de capturas de pantalla para el framework FACTO.
    """

    def __init__(self, driver, context) -> None:
        """
        Args:
            driver:  WebDriver de Selenium activo.
            context: ExecutionContext de la ejecución actual.
        """
        self.driver = driver
        self.context = context

    def take(self, paso: str) -> Path | None:
        """
        Toma un screenshot y lo guarda en el directorio de evidencia.

        Args:
            paso: Nombre del paso para el nombre del archivo.

        Returns:
            Path del screenshot guardado, o None si falló.
        """
        try:
            evidence_dir = Path(self.context.evidence_dir)
            evidence_dir.mkdir(parents=True, exist_ok=True)

            filename = EvidenceNaming.screenshot(paso, self.context)
            filepath = evidence_dir / filename

            self.driver.save_screenshot(str(filepath))
            logger.debug(f"Screenshot guardado: {filepath}")
            return filepath

        except Exception as exc:
            logger.warning(f"No se pudo tomar screenshot '{paso}': {exc}")
            return None

    def take_on_failure(self, test_name: str) -> Path | None:
        """
        Toma un screenshot de fallo al final de un test.

        Args:
            test_name: Nombre del test para identificar el screenshot.

        Returns:
            Path del screenshot de fallo.
        """
        return self.take(f"FALLO_{test_name}")
