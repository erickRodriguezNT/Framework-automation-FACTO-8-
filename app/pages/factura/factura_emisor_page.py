"""
factura_emisor_page.py - Page Object de la sección Emisor del formulario de Factura.

Componente HTML: <app-emisor-factura>

============================================================
ANÁLISIS DE SELECTORES — app-emisor-factura (HTML analizado)
============================================================

HTML OBSERVADO:
  La sección app-emisor-factura muestra campos de solo lectura:
    - Nombre del Emisor → <span class="text-[13px] font-semibold text-[#374151]">
    - Sucursal          → idem
    - Régimen Fiscal    → idem
    - C.P.              → idem
  Todos con valor "—" (datos del perfil del portal, no editables en este form).

NO SE IDENTIFICARON en el HTML:
  - Input para Centro de Consumo
  - Input/Select para Serie
  Estos campos requieren confirmación del equipo frontend.

SELECTORES USADOS:
  - app-emisor-factura           : contenedor del componente Angular
  - Campos readonly → CSS por clase semántica (riesgoso con Tailwind)

SELECTORES RIESGOSOS:
  - Ninguno activo; todos los campos son readonly en este análisis.

DATA-TESTID RECOMENDADOS AL EQUIPO FRONTEND:
  - data-testid="emisor-container"       → sección principal del emisor
  - data-testid="emisor-nombre"          → span con el nombre del emisor
  - data-testid="emisor-rfc"             → span con el RFC del emisor
  - data-testid="emisor-regimen-fiscal"  → span con el régimen fiscal
  - data-testid="emisor-cp"             → span con el código postal
  - data-testid="select-centro-consumo" → dropdown Centro de Consumo
  - data-testid="select-serie"          → dropdown Serie del CFDI
============================================================
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from app.core.base_page import BasePage
from app.utils.exceptions import PageError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FacturaEmisorPage(BasePage):
    """
    Page Object para la sección del Emisor en el formulario de Factura.

    Componente Angular: <app-emisor-factura>

    Responsabilidades:
    - Validar que la sección de emisor está cargada y visible
    - Leer datos del emisor (nombre, RFC, régimen fiscal) de los campos readonly
    - Seleccionar Centro de Consumo (cuando sea implementado por el frontend)
    - Seleccionar Serie del CFDI (cuando sea implementado por el frontend)
    """

    # ------------------------------------------------------------------
    # Locators — Contenedor del Emisor
    # ------------------------------------------------------------------

    # Contenedor del componente Angular — ESTABLE por tag name
    CONTENEDOR_EMISOR = (By.CSS_SELECTOR, "app-emisor-factura")

    # ------------------------------------------------------------------
    # Locators — Datos readonly del Emisor
    # Selectores provisionales por posición CSS dentro del componente.
    # Solicitar data-testid específicos al equipo frontend.
    # ------------------------------------------------------------------

    # Nombre del Emisor (primer campo de la fila superior)
    # TODO: solicitar al equipo frontend agregar data-testid="emisor-nombre"
    NOMBRE_EMISOR = (
        By.CSS_SELECTOR,
        "[data-testid='emisor-nombre'], "
        "app-emisor-factura .flex-col:nth-of-type(1) span.font-semibold",
    )

    # RFC del Emisor
    # TODO: solicitar al equipo frontend agregar data-testid="emisor-rfc"
    RFC_EMISOR = (
        By.CSS_SELECTOR,
        "[data-testid='emisor-rfc'], "
        "app-emisor-factura .flex-col:nth-of-type(2) span.font-semibold",
    )

    # Régimen Fiscal del Emisor
    # TODO: solicitar al equipo frontend agregar data-testid="emisor-regimen-fiscal"
    REGIMEN_FISCAL_EMISOR = (
        By.CSS_SELECTOR,
        "[data-testid='emisor-regimen-fiscal'], "
        "app-emisor-factura .flex-col:nth-of-type(3) span.font-semibold",
    )

    # ------------------------------------------------------------------
    # Locators — Selección de Centro de Consumo y Serie
    # NO ENCONTRADOS en el HTML analizado.
    # ------------------------------------------------------------------

    # Centro de Consumo — <app-select> custom. Trigger = el div interior del componente.
    # TODO: solicitar al equipo frontend agregar data-testid="select-centro-consumo"
    # Identificado en HTML: placeholder="Seleccione Centro de Consumo"
    SELECT_CENTRO_CONSUMO_TRIGGER = (
        By.CSS_SELECTOR,
        "[data-testid='select-centro-consumo'] > div, "
        "app-emisor-factura app-select[formcontrolname='centroConsumo'] > div, "
        "app-emisor-factura app-select[ng-reflect-name='centroConsumo'] > div, "
        "app-emisor-factura app-select[placeholder='Seleccione Centro de Consumo'] > div, "
        "app-emisor-factura app-select[ng-reflect-placeholder='Seleccione Centro de Consumo'] > div",
    )

    # Serie del CFDI — <app-select> custom.
    # TODO: solicitar al equipo frontend agregar data-testid="select-serie"
    # Identificado en HTML: placeholder="Seleccione Serie"
    SELECT_SERIE_TRIGGER = (
        By.CSS_SELECTOR,
        "[data-testid='select-serie'] > div, "
        "app-emisor-factura app-select[placeholder='Seleccione Serie'] > div",
    )

    # ------------------------------------------------------------------
    # Validaciones de carga
    # ------------------------------------------------------------------

    def is_loaded(self) -> bool:
        """
        Verifica que la sección de datos del Emisor está visible en pantalla.

        Returns:
            True si el componente app-emisor-factura es visible.
        """
        return self.is_visible(self.CONTENEDOR_EMISOR, timeout=10)

    def wait_for_emisor_loaded(self) -> None:
        """Espera activamente hasta que la sección del Emisor esté visible."""
        self.wait_for_element(self.CONTENEDOR_EMISOR, condition="visible", timeout=15)
        logger.info("[EMISOR] Sección de emisor cargada.")

    # ------------------------------------------------------------------
    # Lectura de datos readonly
    # ------------------------------------------------------------------

    def get_nombre_emisor(self) -> str:
        """
        Retorna el nombre del emisor cargado desde el perfil del portal.

        Returns:
            Nombre del emisor como texto, o cadena vacía si no es visible.
        """
        try:
            return self.get_text(self.NOMBRE_EMISOR)
        except Exception:
            logger.warning("[EMISOR] No se pudo leer el nombre del emisor.")
            return ""

    def get_rfc_emisor(self) -> str:
        """
        Retorna el RFC del emisor.

        Returns:
            RFC del emisor como texto, o cadena vacía si no es visible.
        """
        try:
            return self.get_text(self.RFC_EMISOR)
        except Exception:
            logger.warning("[EMISOR] No se pudo leer el RFC del emisor.")
            return ""

    # ------------------------------------------------------------------
    # Helper interno: interacción con componente <app-select> Angular
    # ------------------------------------------------------------------

    def _click_app_select_option(self, trigger_locator: tuple, texto_opcion: str) -> None:
        """
        Interactúa con un componente <app-select> personalizado de Angular.

        Flujo:
        1. Hace click en el div trigger del app-select para abrir el dropdown.
        2. Espera a que aparezcan opciones en el DOM.
        3. Hace click en la opción que coincide con texto_opcion.

        Args:
            trigger_locator: Locator del div trigger del app-select.
            texto_opcion:    Texto visible de la opción a seleccionar.

        Raises:
            PageError: Si la opción no se encuentra en el tiempo de espera.

        TODO: Una vez que el portal agregue data-testid en las opciones,
              reemplazar el XPath por texto con selector estable.
        """
        # Esperar que desaparezca el overlay de carga del portal antes de interactuar
        _OVERLAY = (By.CSS_SELECTOR, "div.fixed.inset-0[class*='z-']")
        try:
            WebDriverWait(self.driver, 15).until(
                EC.invisibility_of_element_located(_OVERLAY)
            )
        except TimeoutException:
            pass  # Si no hay overlay o ya desapareció, continuar

        self.scroll_into_view(trigger_locator)
        # Intentar click normal; si está interceptado usar JS click
        try:
            self.click(trigger_locator)
        except Exception:
            element = self.driver.find_element(*trigger_locator)
            self.driver.execute_script("arguments[0].click();", element)
        logger.debug(f"[app-select emisor] Dropdown abierto, buscando: '{texto_opcion}'")

        # El dropdown tiene campo de búsqueda — esperar que aparezca y escribir para filtrar
        _SEARCH_INPUT = (
            By.CSS_SELECTOR,
            "input[placeholder*='uscar'], input[placeholder*='earch'], "
            "input[placeholder*='ilter'], input[placeholder*='Buscar']",
        )
        try:
            search_box = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(_SEARCH_INPUT)
            )
            # Escribir la primera parte (RFC) para filtrar resultados
            termino = texto_opcion.split(" - ")[0] if " - " in texto_opcion else texto_opcion
            search_box.clear()
            search_box.send_keys(termino)
            logger.debug(f"[app-select emisor] Búsqueda escrita: '{termino}'")
        except TimeoutException:
            pass  # Sin campo de búsqueda, las opciones ya están visibles

        import time as _time
        _time.sleep(0.5)  # Esperar que el filtro aplique

        # Buscar la opción SOLO dentro de app-emisor-factura (o su overlay adyacente)
        # para evitar seleccionar elementos del Receptor u otras secciones.
        _js_find = """
            const target = arguments[0];
            // Primero intentar dentro del emisor o en overlays con z-index alto
            const emisor = document.querySelector('app-emisor-factura');
            const containers = [emisor, document.body];
            for (const container of containers) {
                if (!container) continue;
                const all = container.querySelectorAll('*');
                for (const el of all) {
                    const rect = el.getBoundingClientRect();
                    if (rect.width === 0 || rect.height === 0) continue;
                    if (rect.top < 0 || rect.left < 0) continue;
                    const t = (el.textContent || '').trim();
                    if (t === target && el.children.length === 0) return el;
                }
                // Segunda pasada: contains
                for (const el of all) {
                    const rect = el.getBoundingClientRect();
                    if (rect.width === 0 || rect.height === 0) continue;
                    const t = (el.textContent || '').trim();
                    if (t === target) return el;
                    if (t.includes(target) && el.children.length <= 2) return el;
                }
                // Solo iterar el body si no se encontró en el emisor
                if (container === emisor) continue;
                break;
            }
            return null;
        """
        option_el = self.driver.execute_script(_js_find, texto_opcion)
        if option_el:
            try:
                option_el.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", option_el)
            logger.info(f"[app-select emisor] Opción seleccionada (JS): '{texto_opcion}'")
            return

        # Fallback XPath: busca por texto parcial ACOTADO a app-emisor-factura
        termino_busqueda = texto_opcion.split(" - ")[0] if " - " in texto_opcion else texto_opcion
        fallback_xpath = (
            By.XPATH,
            f"//app-emisor-factura//*[contains(normalize-space(.), '{termino_busqueda}') and "
            f"not(self::input) and not(self::textarea) and not(self::button) and "
            f"not(self::nav) and not(self::header)]"
            f" | //*[contains(@class,'option') and contains(normalize-space(.), '{termino_busqueda}')]",
        )
        try:
            option = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(fallback_xpath)
            )
            option.click()
            logger.info(f"[app-select emisor] Opción seleccionada (XPath): '{texto_opcion}'")
        except TimeoutException:
            # Diagnóstico final: dump de todos los textos visibles
            _js_dump = """
                const result = [];
                for (const el of document.querySelectorAll('*')) {
                    const rect = el.getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0 && el.children.length === 0) {
                        const t = (el.textContent || '').trim();
                        if (t.length > 3 && t.length < 120) result.push(t);
                    }
                    if (result.length >= 30) break;
                }
                return result;
            """
            visibles = self.driver.execute_script(_js_dump) or []
            logger.warning(f"[app-select emisor] Textos visibles en DOM: {visibles}")
            raise PageError(
                f"[EMISOR] No se encontró la opción '{texto_opcion}' en el app-select. "
                f"Textos visibles: {visibles[:10]}. "
                f"Verificar que el texto en el Excel coincide con el portal."
            )

    # ------------------------------------------------------------------
    # Selección de parámetros del CFDI
    # ------------------------------------------------------------------

    def select_centro_consumo(self, valor: str) -> None:
        """
        Selecciona el Centro de Consumo para el CFDI.

        El Centro de Consumo usa un componente <app-select> Angular custom.
        Interacción: click en trigger → esperar opciones → click por texto.

        Args:
            valor: Texto visible del Centro de Consumo
                   (ej: 'NID200929V26 - PRUEBAS - Pruebas').
        """
        logger.info(f"[EMISOR] Seleccionando Centro de Consumo: '{valor}'")
        self._click_app_select_option(self.SELECT_CENTRO_CONSUMO_TRIGGER, valor)

    def select_serie(self, serie: str) -> None:
        """
        Selecciona la Serie del CFDI si se proporciona un valor.

        Si serie es vacía, el método retorna sin acción (conforme a la regla:
        'Si serie está vacía, no seleccionar serie y continuar').

        Args:
            serie: Valor de la serie (ej: 'A', 'B', 'H'), o cadena vacía para omitir.
        """
        if not serie or not str(serie).strip():
            logger.info("[EMISOR] Serie vacía — se omite la selección de serie.")
            return
        logger.info(f"[EMISOR] Seleccionando Serie: '{serie}'")
        self._click_app_select_option(self.SELECT_SERIE_TRIGGER, str(serie).strip())
