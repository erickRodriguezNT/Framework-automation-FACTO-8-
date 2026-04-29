"""
nota_credito_page.py - Page Object del formulario principal de Nota de Crédito CFDI 4.0.

Componente raíz HTML: <app-nota-credito> (con fallback a <app-factura>)

Replica exactamente el comportamiento de FacturaPage pero aislado en el
módulo de Nota de Crédito. Evidence guardada en outputs/nota_credito/{caso_id}/
"""
from pathlib import Path

from selenium.webdriver.common.by import By

from app.core.base_page import BasePage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NotaCreditoPage(BasePage):
    """
    Page Object raíz para el formulario de Nota de Crédito CFDI 4.0.

    Responsabilidades:
    - Verificar que la pantalla de Nota de Crédito está cargada y activa
    - Ejecutar el Timbrado del CFDI (acción final del flujo)
    - Leer los totales del resumen (Subtotal, Descuento, Total, Gran Total)
    """

    # ------------------------------------------------------------------
    # Locators — Validación de pantalla
    # ------------------------------------------------------------------

    CONTENEDOR_NOTA_CREDITO = (By.CSS_SELECTOR, "app-nota-credito, app-factura")
    SECCION_CONCEPTOS = (By.CSS_SELECTOR, "app-conceptos-factura")

    # ------------------------------------------------------------------
    # Locators — Botón TIMBRAR CFDI
    # ------------------------------------------------------------------

    BTN_TIMBRAR = (
        By.XPATH,
        "//button[contains(normalize-space(.), 'TIMBRAR CFDI')]",
    )

    # ------------------------------------------------------------------
    # Locators — Resumen de Totales
    # ------------------------------------------------------------------

    GRAN_TOTAL = (
        By.CSS_SELECTOR,
        "[data-testid='gran-total'], "
        "app-factura span.font-black.text-\\[\\#1760d7\\]",
    )

    SUBTOTAL_VALOR = (
        By.XPATH,
        "//span[normalize-space(.)='Subtotal']/following-sibling::span[1]",
    )

    TOTAL_VALOR = (
        By.XPATH,
        "//span[normalize-space(.)='Total']/following-sibling::span[1]",
    )

    # ------------------------------------------------------------------
    # Validaciones de pantalla
    # ------------------------------------------------------------------

    def is_pantalla_nota_credito_cargada(self) -> bool:
        return (
            self.is_visible(self.CONTENEDOR_NOTA_CREDITO, timeout=15)
            and self.is_visible(self.SECCION_CONCEPTOS, timeout=10)
        )

    def wait_for_pantalla_nota_credito(self) -> None:
        self.wait_for_element(self.CONTENEDOR_NOTA_CREDITO, condition="visible", timeout=20)
        self.wait_for_element(self.SECCION_CONCEPTOS, condition="visible", timeout=15)
        logger.info("[NC] Pantalla de Nota de Crédito cargada.")

    # ------------------------------------------------------------------
    # Acción principal — Timbrar CFDI
    # ------------------------------------------------------------------

    def wait_for_boton_timbrar(self, timeout: int = 20) -> None:
        self.wait_for_element(self.BTN_TIMBRAR, condition="clickable", timeout=timeout)
        logger.info("[NC] Botón TIMBRAR CFDI está clickeable.")

    def click_timbrar(self) -> None:
        logger.info("[NC] Esperando que botón TIMBRAR CFDI esté disponible...")
        self.wait_for_boton_timbrar(timeout=20)
        el = self.wait_for_element(self.BTN_TIMBRAR, condition="clickable", timeout=5)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center', behavior:'instant'});", el
        )
        el.click()
        logger.info("[NC] Click en botón TIMBRAR CFDI ejecutado.")

    def is_boton_timbrar_visible(self) -> bool:
        return self.is_visible(self.BTN_TIMBRAR, timeout=5)

    def is_boton_timbrar_habilitado(self) -> bool:
        try:
            element = self.wait_for_element(self.BTN_TIMBRAR, condition="present", timeout=5)
            disabled = element.get_attribute("disabled")
            habilitado = disabled is None
            logger.debug(f"[NC] Botón TIMBRAR habilitado: {habilitado}")
            return habilitado
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Lectura de totales
    # ------------------------------------------------------------------

    def get_gran_total(self) -> str:
        try:
            return self.get_text(self.GRAN_TOTAL, timeout=2)
        except Exception:
            logger.warning("[NC] No se pudo leer el Gran Total.")
            return ""

    def get_subtotal(self) -> str:
        try:
            valor = self.get_text(self.SUBTOTAL_VALOR, timeout=2)
            logger.debug(f"[NC] Subtotal: {valor}")
            return valor
        except Exception as exc:
            logger.debug(f"[NC] No se pudo leer Subtotal: {exc}")
            return ""

    def get_descuento(self) -> str:
        _DESCUENTO_VALOR = (
            By.XPATH,
            "//span[normalize-space(.)='Descuento']/following-sibling::span[1]",
        )
        try:
            valor = self.get_text(_DESCUENTO_VALOR, timeout=2)
            logger.debug(f"[NC] Descuento: {valor}")
            return valor
        except Exception:
            return ""

    def get_total(self) -> str:
        try:
            valor = self.get_text(self.TOTAL_VALOR, timeout=2)
            logger.debug(f"[NC] Total: {valor}")
            return valor
        except Exception as exc:
            logger.debug(f"[NC] No se pudo leer Total: {exc}")
            return ""

    def validar_totales(self) -> dict:
        self.wait_for_page_load(timeout=5)
        totales = {
            "subtotal":   self.get_subtotal(),
            "descuento":  self.get_descuento(),
            "total":      self.get_total(),
            "gran_total": self.get_gran_total(),
        }
        logger.info(f"[NC] Totales leídos: {totales}")
        return totales

    # ------------------------------------------------------------------
    # Utilidades de scroll y evidencia
    # ------------------------------------------------------------------

    def scroll_to_bottom(self) -> None:
        self.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        logger.debug("[NC] Scroll hasta el final de la página.")

    def scroll_to_top(self) -> None:
        self.execute_script("window.scrollTo(0, 0);")
        logger.debug("[NC] Scroll hasta el inicio de la página.")

    def tomar_evidencia_pantalla(
        self,
        caso_id: str,
        nombre_paso: str,
        blocking: bool = True,
    ) -> str | None:
        """
        Captura un screenshot y lo guarda en outputs/nota_credito/{caso_id}/screenshots/.

        NOTA: blocking=False está desactivado — Selenium WebDriver no es thread-safe.
        El parámetro se mantiene por compatibilidad de firma pero siempre es síncrono.

        parents[3] sube: nota_credito/ -> pages/ -> app/ -> automation_framework/
        """
        automation_root = Path(__file__).resolve().parents[3]
        directorio = automation_root / "outputs" / "nota_credito" / caso_id / "screenshots"
        try:
            return str(self.take_screenshot(nombre_paso, directory=directorio))
        except Exception as exc:
            logger.warning(f"[NC] No se pudo capturar screenshot '{nombre_paso}': {exc}")
            return None
