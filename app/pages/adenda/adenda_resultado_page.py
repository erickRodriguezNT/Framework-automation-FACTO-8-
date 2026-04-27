"""
adenda_resultado_page.py - Page Object del resultado de Adenda procesada.

TODO: Reemplazar placeholders con selectores reales del portal.
"""
from selenium.webdriver.common.by import By

from app.core.base_page import BasePage


class AdendaResultadoPage(BasePage):
    """
    Page Object para la pantalla de confirmación de Adenda procesada.
    """

    # ------------------------------------------------------------------
    # Locators
    # TODO: Reemplazar con selectores reales del portal FACTO
    # ------------------------------------------------------------------

    # Mensaje de confirmación de adenda procesada
    MENSAJE_EXITO = (By.CSS_SELECTOR, "[data-testid='exito-adenda'], .success-message, .alert-success, #adenda-success")

    # Mensaje de error
    MENSAJE_ERROR = (By.CSS_SELECTOR, "[data-testid='error-adenda'], .error-message, .alert-danger, #adenda-error")

    # ID o referencia de la adenda procesada
    ID_ADENDA = (By.CSS_SELECTOR, "[data-testid='id-adenda'], #id-adenda, .adenda-id-value")

    # UUID del CFDI con adenda
    UUID_CFDI = (By.CSS_SELECTOR, "[data-testid='uuid-cfdi-adenda'], #uuid-cfdi-adenda, .uuid-adenda-value")

    # Botón de descarga del PDF con adenda
    DOWNLOAD_PDF = (By.CSS_SELECTOR, "[data-testid='download-pdf-adenda'], .btn-pdf-adenda, #btn-pdf-adenda")

    # Botón de descarga del XML con adenda
    DOWNLOAD_XML = (By.CSS_SELECTOR, "[data-testid='download-xml-adenda'], .btn-xml-adenda, #btn-xml-adenda")

    # ------------------------------------------------------------------
    # Acciones y verificaciones
    # ------------------------------------------------------------------

    def is_adenda_procesada(self) -> bool:
        """Verifica si la adenda fue procesada correctamente."""
        return (
            self.is_visible(self.MENSAJE_EXITO, timeout=10)
            or self.is_visible(self.ID_ADENDA, timeout=5)
        )

    def has_error(self) -> bool:
        """Verifica si hubo un error al procesar la adenda."""
        return self.is_visible(self.MENSAJE_ERROR, timeout=3)

    def get_error_message(self) -> str:
        """Obtiene el mensaje de error si aplica."""
        if self.has_error():
            return self.get_text(self.MENSAJE_ERROR)
        return ""

    def get_id_adenda(self) -> str:
        """Obtiene el identificador de la adenda procesada."""
        if self.is_visible(self.ID_ADENDA, timeout=5):
            return self.get_text(self.ID_ADENDA)
        return ""

    def get_uuid_cfdi(self) -> str:
        """Obtiene el UUID del CFDI al que se agregó la adenda."""
        if self.is_visible(self.UUID_CFDI, timeout=5):
            return self.get_text(self.UUID_CFDI)
        return ""

    def click_download_pdf(self) -> None:
        """Descarga el PDF del CFDI con adenda."""
        self.click(self.DOWNLOAD_PDF)

    def click_download_xml(self) -> None:
        """Descarga el XML del CFDI con adenda."""
        self.click(self.DOWNLOAD_XML)
