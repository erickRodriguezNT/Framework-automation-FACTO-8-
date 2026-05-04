"""
factura_conceptos_page.py - Page Object para la sección "Conceptos y Servicios" del formulario de Factura.

Subclase delgada de CfdiEmisionPage. Toda la lógica común vive en el base.
Solo contiene locators y overrides específicos de Factura.

Componente HTML: <app-conceptos-factura> + <app-modal-agregar-concepto>
"""
from selenium.webdriver.common.by import By

from app.pages.common.cfdi_emision_page import CfdiEmisionPage
from app.utils.exceptions import PageError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FacturaConceptosPage(CfdiEmisionPage):
    """
    Page Object para la sección Conceptos y Servicios del formulario de Factura.

    Extiende CfdiEmisionPage con:
    - Locators únicos de Factura (estado vacío, tabla, cancelar)
    - Override _wait_for_modal_abierto con diagnóstico JS
    - Override _post_guardar_hook con screenshot de validación
    """

    # Factura espera hasta 15s en cierre y confirmación (el base usa este valor como default)
    _MODAL_CERRADO_TIMEOUT: int = 15
    _CONCEPTO_GUARDADO_TIMEOUT: int = 15

    # ------------------------------------------------------------------
    # Locators únicos de Factura
    # ------------------------------------------------------------------

    MENSAJE_SIN_CONCEPTOS = (
        By.XPATH,
        "//p[contains(normalize-space(.), 'No hay conceptos agregados')]",
    )

    TABLA_CONCEPTOS = (
        By.CSS_SELECTOR,
        "[data-testid='tabla-conceptos'], "
        "app-conceptos-factura table, "
        "app-conceptos-factura .dt-card table",
    )

    FILAS_CONCEPTOS = (
        By.CSS_SELECTOR,
        "[data-testid='concepto-row'], "
        "app-conceptos-factura table tbody tr",
    )

    MODAL_BTN_CANCELAR = (
        By.CSS_SELECTOR,
        "[data-testid='btn-cancelar-concepto']",
    )

    # Locator de respaldo: cualquier input/select visible dentro del modal
    _MODAL_CUALQUIER_CAMPO = (
        By.XPATH,
        "("
        "//app-modal-agregar-concepto//input | "
        "//app-modal-agregar-concepto//select | "
        "//*[@data-testid='modal-agregar-concepto']//input"
        ")[1]",
    )

    # ------------------------------------------------------------------
    # Validaciones de estado de la sección
    # ------------------------------------------------------------------

    def is_seccion_visible(self) -> bool:
        """Verifica que la sección Conceptos y Servicios está visible."""
        return self.is_visible(
            (By.CSS_SELECTOR, "app-conceptos-factura"),
            timeout=10,
        )

    def is_tabla_vacia(self) -> bool:
        """Verifica que la tabla de conceptos está vacía."""
        return self.is_visible(self.MENSAJE_SIN_CONCEPTOS, timeout=3)

    def is_modal_abierto(self) -> bool:
        """Verifica que el modal de Agregar Concepto está abierto."""
        return (
            self.is_visible(self.MODAL_CONTENEDOR, timeout=2)
            or self.is_visible(self._MODAL_CUALQUIER_CAMPO, timeout=2)
        )

    # ------------------------------------------------------------------
    # Override — espera apertura del modal con diagnóstico JS
    # ------------------------------------------------------------------

    def _wait_for_modal_abierto(self, timeout: int = 10) -> None:
        """
        Espera apertura del modal con dos niveles de fallback y diagnóstico JS.

        Raises:
            PageError: Si el modal no abre en el tiempo indicado.
        """
        logger.debug("[CONCEPTOS] Esperando apertura del modal...")

        if self.is_visible(self.MODAL_CONTENEDOR, timeout=timeout):
            logger.info("[CONCEPTOS] Modal abierto (via app-modal-agregar-concepto).")
            return

        if self.is_visible(self._MODAL_CUALQUIER_CAMPO, timeout=3):
            logger.info("[CONCEPTOS] Modal abierto (via campo genérico).")
            try:
                info = self.driver.execute_script("""
                    const m = document.querySelector('app-modal-agregar-concepto');
                    if (!m) return 'NO_MODAL';
                    return Array.from(m.querySelectorAll('input,select,textarea,app-select')).map((el,i) => {
                        const fc = el.getAttribute('formcontrolname') || el.getAttribute('ng-reflect-name') || '-';
                        const ph = el.getAttribute('placeholder') || el.getAttribute('ng-reflect-placeholder') || '-';
                        return `[${i}]${el.tagName}:${fc}:${ph}`;
                    }).join(' | ');
                """)
                logger.info(f"[CONCEPTOS DIAG modal-fields] {info}")
            except Exception as _e:
                logger.warning(f"[CONCEPTOS DIAG] Error dump: {_e}")
            return

        raise PageError(
            "El modal 'Agregar Concepto' no se abrió después de hacer click. "
            "TODO: agregar data-testid='modal-agregar-concepto' al componente "
            "<app-modal-agregar-concepto> para detectar apertura."
        )

    # ------------------------------------------------------------------
    # Override — screenshot de validación post-guardado
    # ------------------------------------------------------------------

    def _post_guardar_hook(self, descripcion: str) -> None:
        """Toma screenshot de validación tras confirmar concepto en tabla."""
        try:
            self.take_screenshot(
                f"concepto_guardado_{descripcion[:30].replace(' ', '_')}",
                directory=None,
            )
            logger.info("[CONCEPTOS] Screenshot de validación post-guardado tomado.")
        except Exception as _exc:
            logger.warning(f"[CONCEPTOS] No se pudo tomar screenshot post-guardado: {_exc}")
