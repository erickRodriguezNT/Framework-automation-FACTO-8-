"""
factura_page.py - Page Object del formulario principal de Generación de Factura CFDI 4.0.

Componente raíz HTML: <app-factura>

Este Page Object actúa como punto de entrada del formulario. Provee:
- Validación de que la pantalla de Generación de Factura está cargada
- Botón TIMBRAR CFDI (la acción final del formulario)
- Validación de totales en el resumen inferior
- Información de estado de la pantalla

Las secciones individuales del formulario tienen sus propios Page Objects:
  - FacturaEmisorPage     → <app-emisor-factura>
  - FacturaReceptorPage   → <app-receptor-factura>
  - FacturaComprobantePage → <app-comprobante-factura>
  - FacturaConceptosPage  → <app-conceptos-factura>
  - FacturaResultadoPage  → pantalla de resultado post-timbrado

============================================================
ANÁLISIS DE SELECTORES — app-factura (HTML analizado)
============================================================

HTML OBSERVADO — Botón Timbrar CFDI:
  <button class="relative flex items-center justify-center w-full h-12 bg-[#1760d7] ...">
    <span class="material-icons text-[18px]">send</span> TIMBRAR CFDI
  </button>
  ↳ Sin id, sin formcontrolname, sin data-testid.
  ↳ Selector por texto via XPath relativo (no absoluto). Es aceptable en Angular.

HTML OBSERVADO — Totales:
  <span> "Subtotal" / "$0.00" </span>
  <span> "Descuento" / "$0.00" </span>
  <span> "Total" / "$0.00" </span>
  <span class="text-[24px] font-black text-[#1760d7] ..."> "$0.00" </span>  ← Gran Total
  ↳ Sin data-testid. Usar XPath por contenedor semántico.

SELECTORES RIESGOSOS:
  ⚠️  XPath por texto para el botón Timbrar (no es XPath absoluto, es aceptable)
  ⚠️  Totales por posición en su contenedor

DATA-TESTID RECOMENDADOS AL EQUIPO FRONTEND:
  - data-testid="btn-timbrar-cfdi"      → botón TIMBRAR CFDI (único botón crítico)
  - data-testid="total-subtotal"        → span valor subtotal
  - data-testid="total-descuento"       → span valor descuento
  - data-testid="total-importe"         → span valor total (antes de impuestos)
  - data-testid="gran-total"            → span gran total en azul
  - data-testid="factura-titulo"        → título de la pantalla
============================================================
"""
from selenium.webdriver.common.by import By

from app.core.base_page import BasePage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FacturaPage(BasePage):
    """
    Page Object raíz para el formulario de Generación de Factura CFDI 4.0.

    Componente Angular: <app-factura>

    Responsabilidades:
    - Verificar que la pantalla de Generación de Factura está cargada y activa
    - Ejecutar el Timbrado del CFDI (acción final del flujo)
    - Leer los totales del resumen (Subtotal, Descuento, Total, Gran Total)
    """

    # ------------------------------------------------------------------
    # Locators — Validación de pantalla
    # ------------------------------------------------------------------

    # Componente raíz del formulario de factura
    CONTENEDOR_FACTURA = (By.CSS_SELECTOR, "app-factura")

    # Sección de conceptos (confirma que el formulario completo cargó)
    SECCION_CONCEPTOS = (By.CSS_SELECTOR, "app-conceptos-factura")

    # ------------------------------------------------------------------
    # Locators — Botón TIMBRAR CFDI
    # ⚠️  Sin data-testid en el HTML. Usando XPath relativo por texto.
    # TODO: solicitar al equipo frontend agregar data-testid="btn-timbrar-cfdi"
    # ------------------------------------------------------------------

    BTN_TIMBRAR = (
        By.XPATH,
        "//button[contains(normalize-space(.), 'TIMBRAR CFDI')]",
    )

    # ------------------------------------------------------------------
    # Locators — Resumen de Totales
    # Posición en el card inferior derecho del formulario
    # ------------------------------------------------------------------

    # Gran Total — el valor más prominente (texto azul grande)
    # TODO: solicitar al equipo frontend agregar data-testid="gran-total"
    GRAN_TOTAL = (
        By.CSS_SELECTOR,
        "[data-testid='gran-total'], "
        "app-factura span.font-black.text-\\[\\#1760d7\\]",
    )

    # Subtotal — primer par label/valor en el card de totales
    # TODO: solicitar al equipo frontend agregar data-testid="total-subtotal"
    SUBTOTAL_VALOR = (
        By.XPATH,
        "//span[normalize-space(.)='Subtotal']/following-sibling::span[1]",
    )

    # Total (antes de gran total)
    # TODO: solicitar al equipo frontend agregar data-testid="total-importe"
    TOTAL_VALOR = (
        By.XPATH,
        "//span[normalize-space(.)='Total']/following-sibling::span[1]",
    )

    # ------------------------------------------------------------------
    # Validaciones de pantalla
    # ------------------------------------------------------------------

    def is_pantalla_factura_cargada(self) -> bool:
        """
        Verifica que la pantalla de Generación de Factura está completamente cargada.

        Comprueba la presencia de los componentes principales del formulario.

        Returns:
            True si app-factura y app-conceptos-factura son visibles.
        """
        return (
            self.is_visible(self.CONTENEDOR_FACTURA, timeout=15)
            and self.is_visible(self.SECCION_CONCEPTOS, timeout=10)
        )

    def wait_for_pantalla_factura(self) -> None:
        """Espera activamente a que la pantalla de Generación de Factura cargue."""
        self.wait_for_element(self.CONTENEDOR_FACTURA, condition="visible", timeout=20)
        self.wait_for_element(self.SECCION_CONCEPTOS, condition="visible", timeout=15)
        logger.info("[FACTURA] Pantalla de Generación de Factura cargada.")

    # ------------------------------------------------------------------
    # Acción principal — Timbrar CFDI
    # ------------------------------------------------------------------

    def wait_for_boton_timbrar(self, timeout: int = 20) -> None:
        """
        Espera explícitamente a que el botón TIMBRAR CFDI esté clickeable.

        Útil para asegurarse de que el formulario no tiene errores de validación
        pendientes antes de intentar timbrar.

        Args:
            timeout: Segundos máximos de espera. Default 20s.

        Raises:
            PageError: Si el botón no está disponible en el tiempo indicado.
        """
        self.wait_for_element(self.BTN_TIMBRAR, condition="clickable", timeout=timeout)
        logger.info("[FACTURA] Botón TIMBRAR CFDI está clickeable.")

    def click_timbrar(self) -> None:
        """
        Hace click en el botón "TIMBRAR CFDI" para enviar el CFDI al SAT.
        Scroll instantáneo vía JS + click sin esperas adicionales.
        """
        logger.info("[FACTURA] Esperando que botón TIMBRAR CFDI esté disponible...")
        self.wait_for_boton_timbrar(timeout=20)
        # Scroll instantáneo sin animación para evitar tiempos muertos
        el = self.wait_for_element(self.BTN_TIMBRAR, condition="clickable", timeout=5)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center', behavior:'instant'});", el
        )
        el.click()
        logger.info("[FACTURA] Click en botón TIMBRAR CFDI ejecutado.")

    def is_boton_timbrar_visible(self) -> bool:
        """Verifica que el botón TIMBRAR CFDI está visible en la pantalla."""
        return self.is_visible(self.BTN_TIMBRAR, timeout=5)

    def is_boton_timbrar_habilitado(self) -> bool:
        """
        Verifica que el botón TIMBRAR CFDI está habilitado (no disabled).

        Un botón disabled indica que el formulario tiene campos obligatorios
        sin completar o errores de validación pendientes.

        Returns:
            True si el botón está presente y no tiene atributo disabled.
        """
        try:
            element = self.wait_for_element(
                self.BTN_TIMBRAR, condition="present", timeout=5
            )
            disabled = element.get_attribute("disabled")
            habilitado = disabled is None
            logger.debug(f"[FACTURA] Botón TIMBRAR habilitado: {habilitado}")
            return habilitado
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Lectura de totales
    # ------------------------------------------------------------------

    def get_gran_total(self) -> str:
        """
        Retorna el texto del Gran Total mostrado en el card de resumen.

        Returns:
            Texto del Gran Total (ej: '$11,600.00'), o vacío si no visible.
        """
        try:
            return self.get_text(self.GRAN_TOTAL, timeout=2)
        except Exception:
            logger.warning("[FACTURA] No se pudo leer el Gran Total.")
            return ""

    def get_subtotal(self) -> str:
        """Retorna el texto del Subtotal (sin impuestos)."""
        try:
            valor = self.get_text(self.SUBTOTAL_VALOR, timeout=2)
            logger.debug(f"[FACTURA] Subtotal: {valor}")
            return valor
        except Exception as exc:
            logger.debug(f"[FACTURA] No se pudo leer Subtotal: {exc}")
            return ""

    def get_descuento(self) -> str:
        """
        Retorna el texto del Descuento del resumen de totales.

        TODO: solicitar al equipo frontend agregar data-testid="total-descuento"
        Selector temporal: XPath relativo por label 'Descuento'.

        Returns:
            Texto del descuento (ej: '$0.00'), o vacío si no aplica.
        """
        # TODO: Reemplazar con selector real obtenido del portal
        # Patrón: label 'Descuento' seguido de su valor numérico
        _DESCUENTO_VALOR = (
            By.XPATH,
            "//span[normalize-space(.)='Descuento']/following-sibling::span[1]",
        )
        try:
            valor = self.get_text(_DESCUENTO_VALOR, timeout=2)
            logger.debug(f"[FACTURA] Descuento: {valor}")
            return valor
        except Exception:
            return ""

    def get_total(self) -> str:
        """Retorna el texto del Total (antes de la fila Gran Total)."""
        try:
            valor = self.get_text(self.TOTAL_VALOR, timeout=2)
            logger.debug(f"[FACTURA] Total: {valor}")
            return valor
        except Exception as exc:
            logger.debug(f"[FACTURA] No se pudo leer Total: {exc}")
            return ""

    def validar_totales(self) -> dict:
        """
        Lee los valores del resumen de totales y los retorna como diccionario.

        Espera brevemente a que los totales sean calculados por Angular
        antes de leerlos. Si un valor no está disponible, retorna cadena vacía.

        Returns:
            Diccionario con claves: subtotal, descuento, total, gran_total.
            Cada valor es el texto tal como aparece en pantalla.
        """
        # Dar tiempo a Angular para recalcular totales tras agregar conceptos
        self.wait_for_page_load(timeout=5)

        totales = {
            "subtotal":   self.get_subtotal(),
            "descuento":  self.get_descuento(),
            "total":      self.get_total(),
            "gran_total": self.get_gran_total(),
        }
        logger.info(f"[FACTURA] Totales leídos: {totales}")
        return totales

    # ------------------------------------------------------------------
    # Utilidades de scroll y evidencia
    # ------------------------------------------------------------------

    def scroll_to_bottom(self) -> None:
        """Hace scroll hasta el final de la página."""
        self.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        logger.debug("[FACTURA] Scroll hasta el final de la página.")

    def scroll_to_top(self) -> None:
        """Hace scroll hasta el inicio de la página."""
        self.execute_script("window.scrollTo(0, 0);")
        logger.debug("[FACTURA] Scroll hasta el inicio de la página.")

    def tomar_evidencia_pantalla(self, caso_id: str, nombre_paso: str) -> str | None:
        """
        Captura un screenshot y lo guarda en el directorio de evidencias del caso.

        Prioridad de ruta:
        1. ``self._screenshot_dir`` — seteado por el flow cuando usa output_manager
           (ej: ``outputs/factura/20260429_214530/FACTURA_001/screenshots/``).
        2. Ruta legacy: ``outputs/factura/{caso_id}/screenshots/`` (retrocompatibilidad).

        Args:
            caso_id:     Identificador del caso (ej: 'FACTURA_001').
            nombre_paso: Nombre descriptivo del paso (ej: 'emisor_completado').

        Returns:
            Ruta del screenshot como string, o None si falló.
        """
        from pathlib import Path
        # Si el flow ya configuró la ruta con run_dir/case_dir, usarla.
        screenshot_dir = getattr(self, "_screenshot_dir", None)
        if screenshot_dir is None:
            # Retrocompatibilidad: ruta sin timestamp
            automation_root = Path(__file__).resolve().parents[3]
            screenshot_dir = automation_root / "outputs" / "factura" / caso_id / "screenshots"
        directorio = Path(screenshot_dir)
        try:
            return str(self.take_screenshot(nombre_paso, directory=directorio))
        except Exception as exc:
            logger.warning(f"[FACTURA] No se pudo capturar screenshot '{nombre_paso}': {exc}")
            return None
