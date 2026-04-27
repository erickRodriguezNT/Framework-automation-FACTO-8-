"""
download_page.py - Page Object para manejo de descargas de archivos del portal FACTO.

Responsabilidades:
- Hacer click en botones de descarga (PDF, XML)
- Verificar disponibilidad de botones de descarga
- Iniciar descarga de comprobantes

TODO: Reemplazar placeholders con selectores reales del portal.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from app.core.base_page import BasePage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DownloadPage(BasePage):
    """
    Page Object para la sección de descargas del portal FACTO.

    Gestiona los botones de descarga disponibles en las páginas
    de resultado de cada flujo (Factura, PPD, Complemento, etc.).
    """

    # ------------------------------------------------------------------
    # Locators - Botones de descarga
    # TODO: Reemplazar con selectores reales del portal
    # ------------------------------------------------------------------

    # Botón de descarga de PDF
    # TODO: Identificar el botón de descarga PDF en páginas de resultado
    DOWNLOAD_PDF_BUTTON = (By.CSS_SELECTOR, "[data-testid='download-pdf'], .btn-download-pdf, a[href*='.pdf'], #btn-pdf")

    # Botón de descarga de XML
    # TODO: Identificar el botón de descarga XML en páginas de resultado
    DOWNLOAD_XML_BUTTON = (By.CSS_SELECTOR, "[data-testid='download-xml'], .btn-download-xml, a[href*='.xml'], #btn-xml")

    # Botón de descarga de ZIP (paquete completo)
    # TODO: Identificar el botón de descarga ZIP del portal
    DOWNLOAD_ZIP_BUTTON = (By.CSS_SELECTOR, "[data-testid='download-zip'], .btn-download-zip, a[href*='.zip'], #btn-zip")

    # Estado de la descarga (indicador de progreso si aplica)
    # TODO: Identificar el indicador de progreso de descarga
    DOWNLOAD_STATUS = (By.CSS_SELECTOR, "[data-testid='download-status'], .download-progress, #download-status")

    # ------------------------------------------------------------------
    # Acciones de descarga
    # ------------------------------------------------------------------

    def click_download_pdf(self) -> None:
        """Hace click en el botón de descarga de PDF."""
        logger.info("Iniciando descarga de PDF")
        self.click(self.DOWNLOAD_PDF_BUTTON)

    def click_download_xml(self) -> None:
        """Hace click en el botón de descarga de XML."""
        logger.info("Iniciando descarga de XML")
        self.click(self.DOWNLOAD_XML_BUTTON)

    def click_download_zip(self) -> None:
        """Hace click en el botón de descarga del paquete ZIP."""
        logger.info("Iniciando descarga de ZIP")
        self.click(self.DOWNLOAD_ZIP_BUTTON)

    # ------------------------------------------------------------------
    # Verificaciones
    # ------------------------------------------------------------------

    def is_pdf_available(self) -> bool:
        """Verifica si el botón de descarga PDF está disponible."""
        return self.is_present(self.DOWNLOAD_PDF_BUTTON, timeout=5)

    def is_xml_available(self) -> bool:
        """Verifica si el botón de descarga XML está disponible."""
        return self.is_present(self.DOWNLOAD_XML_BUTTON, timeout=5)

    def are_downloads_available(self) -> bool:
        """Verifica si ambos archivos (PDF y XML) están disponibles para descarga."""
        return self.is_pdf_available() and self.is_xml_available()
