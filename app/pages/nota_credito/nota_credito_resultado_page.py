"""
nota_credito_resultado_page.py - Page Object de la pantalla de resultado post-timbrado de Nota de Crédito.

Réplica exacta de FacturaResultadoPage pero aislada en el módulo de Nota de Crédito.
"""
from selenium.webdriver.common.by import By

from app.core.base_page import BasePage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NotaCreditoResultadoPage(BasePage):
    """
    Page Object para la pantalla de resultado del timbrado de Nota de Crédito.

    Esta pantalla es la más crítica del flujo: expone el UUID CFDI
    generado por el SAT y permite la descarga de PDF y XML.
    """

    PANTALLA_RESULTADO = (
        By.CSS_SELECTOR,
        "[data-testid='pantalla-resultado']",
    )

    UUID_CFDI = (
        By.CSS_SELECTOR,
        "[data-testid='uuid-cfdi'], "
        ".uuid-value, "
        "span.folio-fiscal",
    )

    MENSAJE_EXITO = (
        By.XPATH,
        "//*[@data-testid='mensaje-exito-timbrado' "
        "or contains(@class,'success-message') "
        "or contains(@class,'alert-success') "
        "or contains(normalize-space(.), 'Timbrado exitoso') "
        "or contains(normalize-space(.), 'timbrado exitosamente')]",
    )

    MENSAJE_ERROR = (
        By.XPATH,
        "//*["
        "(@data-testid='mensaje-error-timbrado' "
        "or contains(@class,'error-message') "
        "or contains(@class,'alert-danger') "
        "or contains(@class,'toast-error') "
        "or (contains(normalize-space(.), 'Error al generar la factura') "
        "    and not(.//*[contains(normalize-space(.), 'Error al generar la factura')])) "
        "or (contains(normalize-space(.), 'Error al timbrar') "
        "    and not(.//*[contains(normalize-space(.), 'Error al timbrar')])) "
        "or (contains(normalize-space(.), 'Error del PAC') "
        "    and not(.//*[contains(normalize-space(.), 'Error del PAC')]))"
        ")]",
    )

    FECHA_TIMBRADO = (
        By.CSS_SELECTOR,
        "[data-testid='fecha-timbrado']",
    )

    BTN_DESCARGAR_PDF = (
        By.CSS_SELECTOR,
        "[data-testid='btn-descargar-pdf'], "
        "button[aria-label*='PDF'], "
        "a[href*='.pdf']",
    )

    BTN_DESCARGAR_XML = (
        By.CSS_SELECTOR,
        "[data-testid='btn-descargar-xml'], "
        "button[aria-label*='XML'], "
        "a[href*='.xml']",
    )

    BTN_NUEVA_FACTURA = (
        By.CSS_SELECTOR,
        "[data-testid='btn-nueva-factura']",
    )

    # ------------------------------------------------------------------
    # Verificaciones de estado
    # ------------------------------------------------------------------

    def is_timbrado_exitoso(self) -> bool:
        tiene_uuid = self.is_visible(self.UUID_CFDI, timeout=30)
        tiene_exito = self.is_visible(self.MENSAJE_EXITO, timeout=5)
        resultado = tiene_uuid or tiene_exito
        logger.info(f"[NC RESULTADO] Timbrado exitoso: {resultado}")
        return resultado

    def has_error(self) -> bool:
        return self.is_visible(self.MENSAJE_ERROR, timeout=5)

    def get_uuid_cfdi(self) -> str:
        try:
            uuid = self.get_text(self.UUID_CFDI).strip()
            logger.info(f"[NC RESULTADO] UUID CFDI: {uuid}")
            return uuid
        except Exception:
            logger.warning("[NC RESULTADO] No se pudo obtener el UUID CFDI.")
            return ""

    def get_error_message(self) -> str:
        if not self.has_error():
            return ""
        try:
            el = self.driver.find_element(*self.MENSAJE_ERROR)
            full_text = (el.text or "").strip()
            # Return only the first line starting with "Error" to avoid
            # capturing the entire page text if the locator matched a parent.
            for line in full_text.splitlines():
                line = line.strip()
                if line.lower().startswith("error"):
                    return line
            return full_text.splitlines()[0] if full_text else ""
        except Exception:
            return ""

    def get_fecha_timbrado(self) -> str:
        try:
            return self.get_text(self.FECHA_TIMBRADO).strip()
        except Exception:
            return ""

    # ------------------------------------------------------------------
    # Acciones — Descarga
    # ------------------------------------------------------------------

    def click_descargar_pdf(self) -> None:
        self.click(self.BTN_DESCARGAR_PDF)
        logger.info("[NC RESULTADO] Click en Descargar PDF.")

    def click_descargar_xml(self) -> None:
        self.click(self.BTN_DESCARGAR_XML)
        logger.info("[NC RESULTADO] Click en Descargar XML.")
