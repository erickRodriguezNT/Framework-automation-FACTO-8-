"""
loader_page.py - Page Object para manejo de indicadores de carga del portal FACTO.

Responsabilidades:
- Detectar loaders/spinners activos
- Esperar a que el portal termine de cargar antes de continuar
- Evitar interacciones con elementos mientras el portal procesa

TODO: Reemplazar placeholders con los selectores reales del loader del portal.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from app.core.base_page import BasePage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LoaderPage(BasePage):
    """
    Page Object para detectar y esperar loaders del portal FACTO.

    Debe usarse antes de interactuar con elementos después de
    operaciones que generen procesamiento en el servidor.
    """

    # ------------------------------------------------------------------
    # Locators - Indicadores de carga
    # TODO: Reemplazar con el selector real del loader del portal FACTO
    # ------------------------------------------------------------------

    # Loader / spinner principal
    # TODO: Identificar el elemento de carga del portal (spinner, overlay, progress)
    MAIN_LOADER = (By.CSS_SELECTOR, "[data-testid='loader'], .loading-overlay, .spinner-overlay, #main-loader")

    # Spinner inline (dentro de botones o secciones)
    # TODO: Identificar spinners de botones de acción
    INLINE_SPINNER = (By.CSS_SELECTOR, ".spinner-border, .fa-spinner, [aria-label='cargando'], [data-loading]")

    # Overlay de bloqueo de UI
    # TODO: Identificar el overlay que bloquea la UI durante procesamiento
    BLOCKING_OVERLAY = (By.CSS_SELECTOR, ".blocking-overlay, .ui-block, [data-testid='blocking-overlay']")

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def wait_for_loader_to_disappear(self, timeout: int = 30) -> None:
        """
        Espera a que el loader principal desaparezca.

        Debe llamarse después de cualquier acción que dispare
        una operación asíncrona en el portal.

        Args:
            timeout: Tiempo máximo de espera en segundos.
        """
        from app.utils.waits import wait_for_loader_to_disappear
        wait_for_loader_to_disappear(self.driver, self.MAIN_LOADER, timeout=timeout)

    def wait_for_all_loaders(self, timeout: int = 30) -> None:
        """
        Espera a que todos los loaders conocidos desaparezcan.

        Args:
            timeout: Tiempo máximo de espera por cada loader.
        """
        for loader in [self.MAIN_LOADER, self.BLOCKING_OVERLAY]:
            try:
                self.wait_for_element(loader, condition="invisible", timeout=timeout)
            except Exception:
                # Si el loader no existe, continuar (no es error)
                pass

    def is_loading(self) -> bool:
        """
        Verifica si hay un loader activo en pantalla.

        Returns:
            True si hay algún indicador de carga visible.
        """
        return (
            self.is_visible(self.MAIN_LOADER, timeout=2)
            or self.is_visible(self.BLOCKING_OVERLAY, timeout=2)
        )
