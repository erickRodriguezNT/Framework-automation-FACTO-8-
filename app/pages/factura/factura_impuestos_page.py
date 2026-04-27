"""
factura_impuestos_page.py - Page Object para la configuración de Impuestos de Factura.

Componente: Los impuestos en FACTO 8 se configuran a nivel de concepto dentro del
modal <app-modal-agregar-concepto>, NO en una sección separada del formulario.

============================================================
ANÁLISIS DE SELECTORES — Impuestos (HTML analizado)
============================================================

HTML OBSERVADO:
  Los impuestos NO aparecen como sección independiente en el HTML analizado.
  En el catálogo <app-conceptos-factura> los impuestos se capturan por concepto:
    - "objeto_impuesto": '02' indica que el concepto SÍ tiene impuestos
    - Los traslados (IVA, IEPS) y retenciones se configuran dentro del
      modal <app-modal-agregar-concepto> al agregar cada concepto.

  La sección actual del formulario muestra el resumen de totales:
    - Subtotal
    - Descuento
    - Total
    - GRAN TOTAL

NOTA ARQUITECTÓNICA:
  En CFDI 4.0, los impuestos son a nivel de concepto (no del comprobante).
  El portal FACTO 8 calcula los totales automáticamente al agregar conceptos
  con objeto_impuesto='02' y tasa IVA 16%.

  Si el portal tiene una sección de configuración de impuestos separada,
  solicitar al equipo frontend los selectores y data-testid correspondientes.

DATA-TESTID RECOMENDADOS AL EQUIPO FRONTEND (si aplica sección separada):
  - data-testid="seccion-impuestos"         → contenedor de la sección
  - data-testid="select-tipo-impuesto"      → tipo: IVA/IEPS/ISR
  - data-testid="select-tasa-impuesto"      → tasa: 0.16, 0.08, etc.
  - data-testid="select-tipo-factor"        → Tasa/Cuota/Exento
  - data-testid="total-traslados"           → total IVA calculado
  - data-testid="total-retenciones"         → total retenciones
============================================================
"""
from selenium.webdriver.common.by import By

from app.core.base_page import BasePage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FacturaImpuestosPage(BasePage):
    """
    Page Object placeholder para la sección de Impuestos.

    NOTA: En CFDI 4.0 con FACTO 8, los impuestos se capturan a nivel de
    concepto (dentro del modal). Esta clase existe para:
    1. Consistencia arquitectónica con el flujo
    2. Futuras validaciones de totales de impuestos en el resumen
    3. Extensión cuando se confirme si el portal tiene sección dedicada

    Los totales de impuestos calculados se leen mediante FacturaPage.validar_totales().
    """

    # ------------------------------------------------------------------
    # Locators — Resumen de impuestos (si la sección existe)
    # TODO: Confirmar con el equipo frontend si hay sección de impuestos separada
    # ------------------------------------------------------------------

    # Total de IVA trasladado calculado
    # TODO: Reemplazar con selector real obtenido del portal
    # Selector temporal: XPath por label + valor siguiente
    TOTAL_TRASLADOS = (
        By.XPATH,
        "//*[@data-testid='total-traslados'] | "
        "//span[contains(normalize-space(.), 'IVA')]/following-sibling::span[1]",
    )

    # Total de retenciones
    # TODO: Reemplazar con selector real obtenido del portal
    TOTAL_RETENCIONES = (
        By.XPATH,
        "//*[@data-testid='total-retenciones'] | "
        "//span[contains(normalize-space(.), 'Retenci')]/following-sibling::span[1]",
    )

    # Sección de impuestos (si existe como panel separado)
    # TODO: Reemplazar con selector real obtenido del portal
    SECCION_IMPUESTOS = (
        By.CSS_SELECTOR,
        "[data-testid='seccion-impuestos'], "
        "app-impuestos-factura, "
        ".impuestos-section",
    )

    # ------------------------------------------------------------------
    # Métodos
    # ------------------------------------------------------------------

    def is_seccion_visible(self) -> bool:
        """
        Verifica si existe una sección de Impuestos separada en el formulario.

        Returns:
            True si la sección es visible, False si los impuestos
            se manejan solo a nivel de concepto (caso más común en FACTO 8).
        """
        visible = self.is_visible(self.SECCION_IMPUESTOS, timeout=3)
        logger.debug(f"[IMPUESTOS] Sección de impuestos visible: {visible}")
        return visible

    def wait_for_seccion(self, timeout: int = 10) -> bool:
        """
        Espera a que la sección de impuestos sea visible.

        Retorna False en lugar de lanzar excepción si no existe,
        ya que en CFDI 4.0 puede no haber sección separada.

        Args:
            timeout: Segundos máximos de espera.

        Returns:
            True si la sección apareció, False si no existe.
        """
        visible = self.is_visible(self.SECCION_IMPUESTOS, timeout=timeout)
        if visible:
            logger.info("[IMPUESTOS] Sección de impuestos cargada.")
        else:
            logger.info(
                "[IMPUESTOS] No se detectó sección de impuestos separada. "
                "Los impuestos se configuran a nivel de concepto (CFDI 4.0)."
            )
        return visible

    def get_total_traslados(self) -> str:
        """
        Retorna el total de impuestos trasladados (IVA calculado).

        Intenta leer el valor del portal. Si la sección de impuestos
        no existe como panel separado, retorna cadena vacía.

        TODO: Reemplazar con selector real obtenido del portal

        Returns:
            Texto del total de traslados (ej: '$160.00'), o '' si no aplica.
        """
        try:
            valor = self.get_text(self.TOTAL_TRASLADOS)
            logger.debug(f"[IMPUESTOS] Total traslados: {valor}")
            return valor
        except Exception:
            logger.debug(
                "[IMPUESTOS] Total traslados no visible. "
                "Normal en CFDI 4.0 si impuestos son a nivel concepto."
            )
            return ""

    def get_total_retenciones(self) -> str:
        """
        Retorna el total de retenciones aplicadas.

        TODO: Reemplazar con selector real obtenido del portal

        Returns:
            Texto del total de retenciones, o '' si no aplica.
        """
        try:
            valor = self.get_text(self.TOTAL_RETENCIONES)
            logger.debug(f"[IMPUESTOS] Total retenciones: {valor}")
            return valor
        except Exception:
            logger.debug("[IMPUESTOS] Total retenciones no visible.")
            return ""

    def registrar_totales_impuestos(self) -> dict:
        """
        Lee y registra en log los totales de impuestos disponibles.

        Método utilitario para flujos que quieran dejar evidencia de los
        impuestos calculados antes de timbrar.

        Returns:
            Diccionario con totales disponibles:
            { "traslados": str, "retenciones": str, "seccion_visible": bool }
        """
        seccion = self.is_seccion_visible()
        totales = {
            "seccion_visible": seccion,
            "traslados":       self.get_total_traslados(),
            "retenciones":     self.get_total_retenciones(),
        }
        logger.info(f"[IMPUESTOS] Totales de impuestos: {totales}")
        return totales

