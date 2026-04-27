"""
complemento_pago_resultado_page.py - Page Object del resultado de Complemento de Pago.

TODO: Reemplazar placeholders con selectores reales del portal.
"""
from selenium.webdriver.common.by import By

from app.core.base_page import BasePage


class ComplementoPagoResultadoPage(BasePage):
    """
    Page Object para la página de resultado del Complemento de Pago timbrado.
    """

    # ------------------------------------------------------------------
    # Locators
    # TODO: Reemplazar con selectores reales del portal FACTO
    # ------------------------------------------------------------------

    # UUID CFDI del Complemento de Pago
    UUID_CFDI = (By.CSS_SELECTOR, "[data-testid='uuid-cp'], #uuid-cp, .uuid-cp-value, span.folio-fiscal")

    # Mensaje de éxito
    MENSAJE_EXITO = (By.CSS_SELECTOR, "[data-testid='exito-cp'], .success-message, .alert-success")

    # Mensaje de error
    MENSAJE_ERROR = (By.CSS_SELECTOR, "[data-testid='error-cp'], .error-message, .alert-danger")

    # Monto total del complemento
    MONTO_TOTAL = (By.CSS_SELECTOR, "[data-testid='monto-total-cp'], #monto-total-cp, .monto-cp-value")

    # Botón de descarga PDF
    DOWNLOAD_PDF = (By.CSS_SELECTOR, "[data-testid='download-pdf-cp'], .btn-pdf-cp, #btn-pdf-cp")

    # Botón de descarga XML
    DOWNLOAD_XML = (By.CSS_SELECTOR, "[data-testid='download-xml-cp'], .btn-xml-cp, #btn-xml-cp")

    # ------------------------------------------------------------------
    # Acciones y verificaciones
    # ------------------------------------------------------------------

    def get_uuid_cfdi(self) -> str:
        """Obtiene el UUID CFDI del Complemento de Pago timbrado."""
        return self.get_text(self.UUID_CFDI)

    def is_timbrado_exitoso(self) -> bool:
        """Verifica si el timbrado del Complemento de Pago fue exitoso."""
        return (
            self.is_visible(self.UUID_CFDI, timeout=10)
            or self.is_visible(self.MENSAJE_EXITO, timeout=5)
        )

    def has_error(self) -> bool:
        """Verifica si hay un error en el timbrado."""
        return self.is_visible(self.MENSAJE_ERROR, timeout=3)

    def get_error_message(self) -> str:
        """Obtiene el mensaje de error si aplica."""
        if self.has_error():
            return self.get_text(self.MENSAJE_ERROR)
        return ""

    def get_monto_total(self) -> str:
        """Obtiene el monto total del Complemento de Pago."""
        if self.is_visible(self.MONTO_TOTAL, timeout=5):
            return self.get_text(self.MONTO_TOTAL)
        return ""

    def click_download_pdf(self) -> None:
        """Inicia la descarga del PDF del Complemento de Pago."""
        self.click(self.DOWNLOAD_PDF)

    def click_download_xml(self) -> None:
        """Inicia la descarga del XML del Complemento de Pago."""
        self.click(self.DOWNLOAD_XML)
