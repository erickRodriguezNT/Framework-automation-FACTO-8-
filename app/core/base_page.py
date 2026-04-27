"""
base_page.py - Clase base para todos los Page Objects del framework FACTO 8.

Provee métodos reutilizables de interacción con el navegador:
- Esperas explícitas con condiciones configurables
- Clicks seguros (con fallback a JavaScript)
- Ingreso de texto con limpieza opcional
- Lectura de texto y atributos
- Verificación de visibilidad sin lanzar excepción
- Capturas de pantalla
- Helpers de JavaScript

REGLA ARQUITECTÓNICA:
Las subclases (Page Objects) solo deben:
  1. Declarar locators como atributos de clase
  2. Implementar métodos de acción atómicos (fill_campo, click_boton)

La lógica de negocio completa vive en los Flows, no aquí.
"""
from pathlib import Path
from typing import Any, Optional, Union

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.utils.exceptions import PageError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BasePage:
    """
    Clase base de todos los Page Objects.

    Cada Page Object hereda de esta clase y obtiene acceso
    a todos los métodos de interacción con el navegador.

    Args:
        driver:  Instancia activa de WebDriver.
        timeout: Tiempo máximo de espera explícita en segundos.
    """

    def __init__(self, driver: WebDriver, timeout: int = 30):
        self.driver = driver
        self.timeout = timeout
        self._wait = WebDriverWait(driver, timeout)

    # ------------------------------------------------------------------
    # Esperas explícitas
    # ------------------------------------------------------------------

    def wait_for_element(
        self,
        locator: tuple,
        condition: str = "visible",
        timeout: Optional[int] = None,
    ) -> WebElement:
        """
        Espera a que un elemento cumpla una condición y lo retorna.

        Args:
            locator:   Tupla (By.XX, "valor") del selector.
            condition: 'visible' | 'clickable' | 'present' | 'invisible'
            timeout:   Override del timeout por defecto.

        Returns:
            WebElement encontrado.

        Raises:
            PageError: Si el elemento no aparece dentro del timeout.
        """
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        condition_map = {
            "visible":   EC.visibility_of_element_located(locator),
            "clickable": EC.element_to_be_clickable(locator),
            "present":   EC.presence_of_element_located(locator),
            "invisible": EC.invisibility_of_element_located(locator),
        }

        if condition not in condition_map:
            raise ValueError(
                f"Condición '{condition}' no válida. "
                f"Opciones: {list(condition_map.keys())}"
            )

        try:
            return wait.until(condition_map[condition])
        except TimeoutException:
            raise PageError(
                f"Elemento {locator} no encontrado en "
                f"{timeout or self.timeout}s (condición: {condition})"
            )

    def wait_for_elements(
        self,
        locator: tuple,
        timeout: Optional[int] = None,
    ) -> list[WebElement]:
        """Espera a que haya al menos un elemento presente y los retorna todos."""
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        try:
            return wait.until(EC.presence_of_all_elements_located(locator))
        except TimeoutException:
            raise PageError(
                f"Elementos {locator} no encontrados en {timeout or self.timeout}s"
            )

    # ------------------------------------------------------------------
    # Interacciones
    # ------------------------------------------------------------------

    def click(self, locator: tuple, timeout: Optional[int] = None) -> None:
        """
        Hace click en un elemento esperando que sea clickeable.

        Usa fallback a JavaScript si el click directo falla.

        Args:
            locator: Tupla (By.XX, "valor") del selector.
            timeout: Override del timeout por defecto.
        """
        logger.debug(f"Click en {locator}")
        element = self.wait_for_element(locator, condition="clickable", timeout=timeout)
        try:
            element.click()
        except ElementNotInteractableException:
            logger.warning(f"Click directo falló en {locator}, usando JS click")
            self.driver.execute_script("arguments[0].click();", element)
        except ElementClickInterceptedException:
            # Portal tiene overlay de carga (z-[9999]) — esperar que desaparezca y reintentar
            _OVERLAY = (By.CSS_SELECTOR, "div.fixed.inset-0[class*='z-']")
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.invisibility_of_element_located(_OVERLAY)
                )
            except TimeoutException:
                pass
            # Re-buscar el elemento y hacer click via JS
            element = self.wait_for_element(locator, condition="clickable", timeout=timeout)
            self.driver.execute_script("arguments[0].click();", element)

    def type_text(
        self,
        locator: tuple,
        text: str,
        clear_first: bool = True,
        timeout: Optional[int] = None,
    ) -> None:
        """
        Escribe texto en un campo de entrada.

        Args:
            locator:     Tupla (By.XX, "valor") del selector.
            text:        Texto a escribir.
            clear_first: Si True, limpia el campo antes de escribir.
            timeout:     Override del timeout por defecto.
        """
        display = f"'{text[:20]}...'" if len(text) > 20 else f"'{text}'"
        logger.debug(f"Escribir {display} en {locator}")
        element = self.wait_for_element(locator, condition="visible", timeout=timeout)
        if clear_first:
            element.clear()
        element.send_keys(text)

    def get_text(self, locator: tuple, timeout: Optional[int] = None) -> str:
        """
        Obtiene el texto visible de un elemento.

        Returns:
            Texto del elemento (stripped).
        """
        element = self.wait_for_element(locator, condition="visible", timeout=timeout)
        return element.text.strip()

    def get_attribute(
        self,
        locator: tuple,
        attribute: str,
        timeout: Optional[int] = None,
    ) -> Optional[str]:
        """Obtiene el valor de un atributo de un elemento."""
        element = self.wait_for_element(locator, condition="present", timeout=timeout)
        return element.get_attribute(attribute)

    def select_by_visible_text(
        self,
        locator: tuple,
        text: str,
        timeout: Optional[int] = None,
    ) -> None:
        """Selecciona una opción de un <select> por su texto visible."""
        from selenium.webdriver.support.ui import Select
        element = self.wait_for_element(locator, condition="present", timeout=timeout)
        Select(element).select_by_visible_text(text)

    def select_by_value(
        self,
        locator: tuple,
        value: str,
        timeout: Optional[int] = None,
    ) -> None:
        """Selecciona una opción de un <select> por su valor de atributo."""
        from selenium.webdriver.support.ui import Select
        element = self.wait_for_element(locator, condition="present", timeout=timeout)
        Select(element).select_by_value(value)

    # ------------------------------------------------------------------
    # Verificaciones de estado (sin lanzar excepción)
    # ------------------------------------------------------------------

    def is_visible(self, locator: tuple, timeout: int = 5) -> bool:
        """
        Verifica si un elemento es visible sin lanzar excepción.

        Args:
            locator: Tupla (By.XX, "valor") del selector.
            timeout: Timeout corto para verificación rápida.

        Returns:
            True si el elemento es visible, False en caso contrario.
        """
        try:
            self.wait_for_element(locator, condition="visible", timeout=timeout)
            return True
        except (PageError, TimeoutException, WebDriverException):
            return False

    def is_present(self, locator: tuple, timeout: int = 5) -> bool:
        """Verifica si un elemento está presente en el DOM."""
        try:
            self.wait_for_element(locator, condition="present", timeout=timeout)
            return True
        except (PageError, TimeoutException, WebDriverException):
            return False

    # ------------------------------------------------------------------
    # Navegación
    # ------------------------------------------------------------------

    def navigate_to(self, url: str) -> None:
        """Navega a una URL específica."""
        logger.info(f"Navegando a: {url}")
        self.driver.get(url)

    def get_current_url(self) -> str:
        """Retorna la URL actual del navegador."""
        return self.driver.current_url

    def get_title(self) -> str:
        """Retorna el título de la página actual."""
        return self.driver.title

    def refresh(self) -> None:
        """Recarga la página actual."""
        self.driver.refresh()

    def scroll_into_view(self, locator: tuple) -> None:
        """Hace scroll hasta que el elemento sea visible."""
        element = self.wait_for_element(locator, condition="present")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

    # ------------------------------------------------------------------
    # Capturas de pantalla
    # ------------------------------------------------------------------

    def take_screenshot(
        self,
        filename: str,
        directory: Optional[Union[str, Path]] = None,
    ) -> Path:
        """
        Captura una pantalla y la guarda en el directorio especificado.

        Args:
            filename:  Nombre del archivo (sin extensión).
            directory: Directorio destino. Usa 'outputs/screenshots' por defecto.

        Returns:
            Path donde se guardó el screenshot.
        """
        save_dir = Path(directory) if directory else Path("outputs") / "screenshots"
        save_dir.mkdir(parents=True, exist_ok=True)

        # Sanitiza el nombre del archivo
        safe_name = "".join(c for c in filename if c.isalnum() or c in "-_")
        filepath = save_dir / f"{safe_name}.png"

        self.driver.save_screenshot(str(filepath))
        logger.info(f"Screenshot guardado: {filepath}")
        return filepath

    # ------------------------------------------------------------------
    # JavaScript helpers
    # ------------------------------------------------------------------

    def execute_script(self, script: str, *args: Any) -> Any:
        """Ejecuta JavaScript en la página."""
        return self.driver.execute_script(script, *args)

    def wait_for_page_load(self, timeout: Optional[int] = None) -> None:
        """Espera a que document.readyState sea 'complete'."""
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        wait.until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
