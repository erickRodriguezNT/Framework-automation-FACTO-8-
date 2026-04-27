"""
nota_credito_resultado_page.py - Page Object del resultado de Nota de Crédito timbrada.

TODO: Reemplazar placeholders con selectores reales del portal.
"""
from selenium.webdriver.common.by import By

from app.core.base_page import BasePage


class NotaCreditoResultadoPage(BasePage):
    """
    Page Object para la página de resultado de una Nota de Crédito timbrada.
    """

    # ------------------------------------------------------------------
    # Locators
    # TODO: Reemplazar con selectores reales del portal FACTO
    # ------------------------------------------------------------------

    # UUID CFDI de la nota de crédito
    UUID_CFDI = (By.CSS_SELECTOR, "[data-testid='uuid-nc'], #uuid-nc, .uuid-nota-credito, span.folio-fiscal")

    # Mensaje de éxito
    MENSAJE_EXITO = (By.CSS_SELECTOR, "[data-testid='exito-nc'], .success-message, .alert-success")

    # Mensaje de error
    MENSAJE_ERROR = (By.CSS_SELECTOR, "[data-testid='error-nc'], .error-message, .alert-danger")

    # Total de la nota de crédito
    TOTAL = (By.CSS_SELECTOR, "[data-testid='total-nc'], #total-nc, .total-nc-value")

    # Botón de descarga PDF
    DOWNLOAD_PDF = (By.CSS_SELECTOR, "[data-testid='download-pdf-nc'], .btn-pdf-nc, #btn-pdf-nc")

    # Botón de descarga XML
    DOWNLOAD_XML = (By.CSS_SELECTOR, "[data-testid='download-xml-nc'], .btn-xml-nc, #btn-xml-nc")

    # ------------------------------------------------------------------
    # Acciones y verificaciones
    # ------------------------------------------------------------------

    def get_uuid_cfdi(self) -> str:
        """Obtiene el UUID CFDI de la nota de crédito timbrada."""
        return self.get_text(self.UUID_CFDI)

    def is_timbrado_exitoso(self) -> bool:
        """Verifica si el timbrado de la nota de crédito fue exitoso."""
        return (
            self.is_visible(self.UUID_CFDI, timeout=10)
            or self.is_visible(self.MENSAJE_EXITO, timeout=5)
        )

    def has_error(self) -> bool:
        """Verifica si hay un error en el timbrado."""
        return self.is_visible(self.MENSAJE_ERROR, timeout=3)

    def get_error_message(self) -> str:
        """Obtiene el mensaje de error si falló el timbrado."""
        if self.has_error():
            return self.get_text(self.MENSAJE_ERROR)
        return ""

    def click_download_pdf(self) -> None:
        """Inicia la descarga del PDF de la nota de crédito."""
        self.click(self.DOWNLOAD_PDF)

    def click_download_xml(self) -> None:
        """Inicia la descarga del XML de la nota de crédito."""
        self.click(self.DOWNLOAD_XML)
