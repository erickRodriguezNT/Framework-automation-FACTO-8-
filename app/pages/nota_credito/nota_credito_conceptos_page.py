"""
nota_credito_conceptos_page.py - Page Object para la sección Conceptos del formulario de Nota de Crédito.

Subclase delgada de CfdiEmisionPage. Toda la lógica común vive en el base.
Solo contiene overrides específicos de Nota de Crédito.

Componente HTML: <app-conceptos-factura> + <app-modal-agregar-concepto>
"""
from selenium.webdriver.common.by import By

from app.pages.common.cfdi_emision_page import CfdiEmisionPage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NotaCreditoConceptosPage(CfdiEmisionPage):
    """
    Page Object para la sección de Conceptos en el formulario de Nota de Crédito.

    Extiende CfdiEmisionPage con:
    - Timeouts reducidos (modal cerrado y confirmación en tabla: 2s)
    - Override click_guardar_concepto con screenshot pre-guardado
    - Override _post_agregar_impuesto_hook con pause(5)
    - Acción exclusiva click_facturar_cfdi
    """

    # NC usa timeouts cortos ya que el portal responde más rápido
    _MODAL_CERRADO_TIMEOUT: int = 2
    _CONCEPTO_GUARDADO_TIMEOUT: int = 2

    # ------------------------------------------------------------------
    # Override — screenshot antes de guardar concepto
    # ------------------------------------------------------------------

    def click_guardar_concepto(self) -> None:
        logger.info("[NC CONCEPTOS] Click en botón guardar concepto...")
        try:
            self.take_screenshot("nc_pre_guardar_concepto", directory=None)
        except Exception:
            pass
        self.wait_for_element(self.MODAL_BTN_GUARDAR, condition="clickable", timeout=10)
        self.click(self.MODAL_BTN_GUARDAR)
        logger.info("[NC CONCEPTOS] Click en botón guardar ejecutado.")

    # ------------------------------------------------------------------
    # Override — pausa tras agregar impuesto
    # ------------------------------------------------------------------

    def _post_agregar_impuesto_hook(self) -> None:
        """Espera 5s para que el portal procese el impuesto antes de guardar."""
        self.pause(5)

    # ------------------------------------------------------------------
    # Acción exclusiva de NC — botón Facturar CFDI
    # ------------------------------------------------------------------

    def click_facturar_cfdi(self) -> None:
        _BTN = (By.CSS_SELECTOR, "button[data-testid='btn-facturar-cfdi']")
        logger.info("[NC CONCEPTOS] Haciendo scroll hacia el botón 'Facturar CFDI'...")
        facturar_btn = self.wait_for_element(_BTN, condition="visible", timeout=10)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", facturar_btn)
        self.wait_for_element(_BTN, condition="clickable", timeout=10)
        self.click(_BTN)
        logger.info("[NC CONCEPTOS] Click en botón 'Facturar CFDI' ejecutado.")
