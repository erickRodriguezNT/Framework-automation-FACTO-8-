"""
ppd_resultado_page.py - Page Object del resultado de un CFDI PPD timbrado.

TODO: Reemplazar placeholders con selectores reales del portal.
"""
from selenium.webdriver.common.by import By

from app.core.base_page import BasePage


class PPDResultadoPage(BasePage):
    """
    Page Object para la página de resultado de un CFDI PPD timbrado.

    La pantalla más importante del flujo PPD: expone el UUID que será
    requerido posteriormente para relacionarlo con un Complemento de Pago.
    """

    # ------------------------------------------------------------------
    # Locators
    # TODO: Reemplazar con selectores reales del portal FACTO
    # ------------------------------------------------------------------

    # UUID CFDI del PPD timbrado — CRÍTICO: será usado por complemento de pago
    UUID_CFDI = (By.CSS_SELECTOR, "[data-testid='uuid-ppd'], #uuid-ppd, .uuid-ppd-value, span.folio-fiscal")

    # Estado del CFDI PPD (pendiente de pago)
    ESTADO_PAGO = (By.CSS_SELECTOR, "[data-testid='estado-pago'], #estado-pago, .estado-pago-value, span.estado-cfdi")

    # Mensaje de éxito del timbrado
    MENSAJE_EXITO = (By.CSS_SELECTOR, "[data-testid='exito-ppd'], .success-message, .alert-success")

    # Mensaje de error
    MENSAJE_ERROR = (By.CSS_SELECTOR, "[data-testid='error-ppd'], .error-message, .alert-danger")

    # Total del CFDI PPD
    TOTAL = (By.CSS_SELECTOR, "[data-testid='total-ppd'], #total-ppd, .total-ppd-value")

    # Botón de descarga PDF
    DOWNLOAD_PDF = (By.CSS_SELECTOR, "[data-testid='download-pdf-ppd'], .btn-pdf-ppd, #btn-pdf-ppd")

    # Botón de descarga XML
    DOWNLOAD_XML = (By.CSS_SELECTOR, "[data-testid='download-xml-ppd'], .btn-xml-ppd, #btn-xml-ppd")

    # ------------------------------------------------------------------
    # Acciones y verificaciones
    # ------------------------------------------------------------------

    def get_uuid_cfdi(self) -> str:
        """
        Obtiene el UUID CFDI del PPD timbrado.

        Este UUID es requerido para relacionarlo con un Complemento de Pago.
        """
        return self.get_text(self.UUID_CFDI)

    def get_estado_pago(self) -> str:
        """Obtiene el estado de pago del CFDI (ej: 'Pendiente')."""
        if self.is_visible(self.ESTADO_PAGO, timeout=5):
            return self.get_text(self.ESTADO_PAGO)
        return ""

    def is_timbrado_exitoso(self) -> bool:
        """Verifica si el timbrado del PPD fue exitoso."""
        return (
            self.is_visible(self.UUID_CFDI, timeout=10)
            or self.is_visible(self.MENSAJE_EXITO, timeout=5)
        )

    def has_error(self) -> bool:
        """Verifica si hay error en el timbrado."""
        return self.is_visible(self.MENSAJE_ERROR, timeout=3)

    def get_error_message(self) -> str:
        """Obtiene el mensaje de error si aplica."""
        if self.has_error():
            return self.get_text(self.MENSAJE_ERROR)
        return ""

    def click_download_pdf(self) -> None:
        """Inicia la descarga del PDF del PPD."""
        self.click(self.DOWNLOAD_PDF)

    def click_download_xml(self) -> None:
        """Inicia la descarga del XML del PPD."""
        self.click(self.DOWNLOAD_XML)
