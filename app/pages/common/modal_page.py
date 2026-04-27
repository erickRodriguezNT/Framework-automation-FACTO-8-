"""
modal_page.py - Page Object para manejo de modales y diálogos del portal FACTO.

Responsabilidades:
- Detectar y esperar modales
- Confirmar o cancelar acciones en modales
- Leer mensajes de modales (éxito, error, advertencia)
- Cerrar modales

TODO: Reemplazar placeholders con selectores reales del portal.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from app.core.base_page import BasePage
from app.utils.waits import wait_for_modal_visible


class ModalPage(BasePage):
    """
    Page Object para modales y diálogos del portal FACTO.

    Provee métodos genéricos para interactuar con cualquier
    modal del portal (confirmación, error, éxito, advertencia).
    """

    # ------------------------------------------------------------------
    # Locators - Modal genérico
    # TODO: Reemplazar con selectores reales del portal
    # ------------------------------------------------------------------

    # Contenedor del modal
    # TODO: Identificar el contenedor real de modales del portal
    MODAL_CONTAINER = (By.CSS_SELECTOR, "[role='dialog'], .modal.show, .popup-active, [data-testid='modal']")

    # Título del modal
    # TODO: Actualizar con el selector del título del modal
    MODAL_TITLE = (By.CSS_SELECTOR, "[data-testid='modal-title'], .modal-title, .dialog-title, h4.modal-header-title")

    # Cuerpo / mensaje del modal
    # TODO: Actualizar con el selector del mensaje del modal
    MODAL_BODY = (By.CSS_SELECTOR, "[data-testid='modal-body'], .modal-body, .dialog-content, .popup-message")

    # Botón de confirmación / aceptar
    # TODO: Identificar el botón de confirmación del portal
    CONFIRM_BUTTON = (By.CSS_SELECTOR, "[data-testid='modal-confirm'], .btn-confirm, .btn-primary, button[data-action='confirm']")

    # Botón de cancelar
    # TODO: Identificar el botón de cancelar del portal
    CANCEL_BUTTON = (By.CSS_SELECTOR, "[data-testid='modal-cancel'], .btn-cancel, .btn-secondary, button[data-action='cancel']")

    # Botón X de cerrar
    # TODO: Identificar el botón de cierre del modal
    CLOSE_BUTTON = (By.CSS_SELECTOR, "[data-testid='modal-close'], .modal-close, .close, button[aria-label='Close']")

    # ------------------------------------------------------------------
    # Acciones sobre el modal
    # ------------------------------------------------------------------

    def wait_for_modal(self, timeout: int = 10) -> None:
        """Espera a que el modal sea visible."""
        wait_for_modal_visible(self.driver, self.MODAL_CONTAINER, timeout=timeout)

    def get_modal_title(self) -> str:
        """Obtiene el título del modal visible."""
        if self.is_visible(self.MODAL_TITLE, timeout=3):
            return self.get_text(self.MODAL_TITLE)
        return ""

    def get_modal_message(self) -> str:
        """Obtiene el mensaje/cuerpo del modal visible."""
        if self.is_visible(self.MODAL_BODY, timeout=3):
            return self.get_text(self.MODAL_BODY)
        return ""

    def confirm(self) -> None:
        """Hace click en el botón de confirmación del modal."""
        self.click(self.CONFIRM_BUTTON)

    def cancel(self) -> None:
        """Hace click en el botón de cancelar del modal."""
        self.click(self.CANCEL_BUTTON)

    def close(self) -> None:
        """Cierra el modal usando el botón X."""
        self.click(self.CLOSE_BUTTON)

    def is_modal_visible(self) -> bool:
        """Verifica si hay un modal visible en pantalla."""
        return self.is_visible(self.MODAL_CONTAINER, timeout=3)

    def is_modal_closed(self) -> bool:
        """Verifica que el modal ya no esté visible."""
        return not self.is_visible(self.MODAL_CONTAINER, timeout=3)
