"""
nota_credito_impuestos_page.py - Page Object de impuestos de Nota de Crédito.

En CFDI 4.0 los impuestos se configuran a nivel de concepto.
Esta clase existe para consistencia arquitectónica.
"""
from selenium.webdriver.common.by import By

from app.core.base_page import BasePage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NotaCreditoImpuestosPage(BasePage):
    """
    Page Object placeholder para la sección de Impuestos de Nota de Crédito.

    NOTA: En CFDI 4.0 con FACTO 8, los impuestos se capturan a nivel de
    concepto (dentro del modal). Esta clase existe para consistencia
    arquitectónica con el flujo de NC.
    """

    TOTAL_TRASLADOS = (
        By.XPATH,
        "//*[@data-testid='total-traslados'] | "
        "//span[contains(normalize-space(.), 'IVA')]/following-sibling::span[1]",
    )

    TOTAL_RETENCIONES = (
        By.XPATH,
        "//*[@data-testid='total-retenciones'] | "
        "//span[contains(normalize-space(.), 'Retenci')]/following-sibling::span[1]",
    )

    SECCION_IMPUESTOS = (
        By.CSS_SELECTOR,
        "[data-testid='seccion-impuestos'], "
        "app-impuestos-factura, "
        ".impuestos-section",
    )

    def is_seccion_visible(self) -> bool:
        visible = self.is_visible(self.SECCION_IMPUESTOS, timeout=3)
        logger.debug(f"[NC IMPUESTOS] Sección de impuestos visible: {visible}")
        return visible

    def wait_for_seccion(self, timeout: int = 10) -> bool:
        visible = self.is_visible(self.SECCION_IMPUESTOS, timeout=timeout)
        if visible:
            logger.info("[NC IMPUESTOS] Sección de impuestos cargada.")
        else:
            logger.info("[NC IMPUESTOS] No se detectó sección de impuestos separada.")
        return visible

    def get_total_traslados(self) -> str:
        try:
            valor = self.get_text(self.TOTAL_TRASLADOS, timeout=2)
            logger.debug(f"[NC IMPUESTOS] Total traslados: {valor}")
            return valor
        except Exception:
            return ""

    def get_total_retenciones(self) -> str:
        try:
            valor = self.get_text(self.TOTAL_RETENCIONES, timeout=2)
            logger.debug(f"[NC IMPUESTOS] Total retenciones: {valor}")
            return valor
        except Exception:
            return ""

    def registrar_totales_impuestos(self) -> dict:
        totales = {
            "total_traslados": self.get_total_traslados(),
            "total_retenciones": self.get_total_retenciones(),
        }
        logger.info(f"[NC IMPUESTOS] Totales de impuestos: {totales}")
        return totales
