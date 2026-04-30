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

    def _dismiss_cdk_select_overlay(self) -> None:
        """Descarta cualquier overlay CDK de app-select que haya quedado abierto."""
        from selenium.webdriver.common.action_chains import ActionChains
        import time as _time
        _CDK = (By.CSS_SELECTOR, "div.cdk-overlay-backdrop.select-overlay-backdrop.cdk-overlay-backdrop-showing")
        try:
            backdrop = self.driver.find_element(*_CDK)
            ActionChains(self.driver).move_to_element(backdrop).click().perform()
            _time.sleep(0.3)
            logger.debug("[EMISOR] CDK select overlay backdrop descartado antes de abrir select.")
        except Exception:
            pass

    def _click_app_select_option(self, trigger_locator: tuple, texto_opcion: str) -> None:
        """Interactúa con un componente <app-select> personalizado de Angular."""
        import time as _time
        from selenium.webdriver.common.action_chains import ActionChains

        # Descartar cualquier CDK select overlay residual
        self._dismiss_cdk_select_overlay()

        # RFC = primer token del campo centro_consumo del Excel (p.ej. 'NID200929V26')
        termino = texto_opcion.split(" - ")[0] if " - " in texto_opcion else texto_opcion

        _OVERLAY = (By.CSS_SELECTOR, "div.fixed.inset-0[class*='z-']")
        try:
            WebDriverWait(self.driver, 15).until(
                EC.invisibility_of_element_located(_OVERLAY)
            )
        except TimeoutException:
            pass

        self.scroll_into_view(trigger_locator)
        try:
            self.click(trigger_locator)
        except Exception:
            element = self.driver.find_element(*trigger_locator)
            self.driver.execute_script("arguments[0].click();", element)
        logger.debug(f"[app-select emisor] Dropdown abierto, buscando: '{texto_opcion}'")

        _SEARCH_INPUT = (
            By.CSS_SELECTOR,
            "input[placeholder*='uscar'], input[placeholder*='earch'], "
            "input[placeholder*='ilter'], input[placeholder*='Buscar']",
        )
        try:
            search_box = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(_SEARCH_INPUT)
            )
            search_box.clear()
            # Buscar con texto completo para filtrar la opción exacta
            search_box.send_keys(texto_opcion)
            logger.debug(f"[app-select emisor] Búsqueda por texto completo: '{texto_opcion}'")
        except TimeoutException:
            pass  # Sin campo de búsqueda, las opciones ya están visibles

        _time.sleep(0.8)

        _js_find = """
            const target = arguments[0];
            const normalizeText = t => (t || '').trim().replace(/\\s+/g, ' ');
            const targetNorm = normalizeText(target);
            const containers = [document.querySelector('app-emisor-factura'), document.body];
            for (const container of containers) {
                if (!container) continue;
                const all = container.querySelectorAll('*');
                // Primera pasada: texto exacto normalizado, elemento hoja
                const exactLeaf = [];
                for (const el of all) {
                    const rect = el.getBoundingClientRect();
                    if (rect.width === 0 || rect.height === 0) continue;
                    if (rect.top < 0 || rect.left < 0) continue;
                    const t = normalizeText(el.textContent);
                    if (t === targetNorm && el.children.length === 0) exactLeaf.push(el);
                }
                if (exactLeaf.length > 0) return exactLeaf[exactLeaf.length - 1];
                // Segunda pasada: exacto normalizado (hijos permitidos) o contains sin prefijos falsos
                const exactAny = [];
                const containsAny = [];
                for (const el of all) {
                    const rect = el.getBoundingClientRect();
                    if (rect.width === 0 || rect.height === 0) continue;
                    const t = normalizeText(el.textContent);
                    if (t === targetNorm) {
                        exactAny.push(el);
                    } else if (el.children.length <= 2) {
                        const idx = t.indexOf(targetNorm);
                        if (idx >= 0) {
                            const after = t.slice(idx + targetNorm.length).trimStart();
                            if (after === '' || after.startsWith('-') || after.startsWith('(') || after.startsWith('/')) {
                                containsAny.push(el);
                            }
                        }
                    }
                }
                if (exactAny.length > 0) return exactAny[exactAny.length - 1];
                if (containsAny.length > 0) return containsAny[containsAny.length - 1];
                if (container !== document.body) continue;
                break;
            }
            return null;
        """
        # Buscar por texto completo primero, luego por RFC (primer token)
        option_el = self.driver.execute_script(_js_find, texto_opcion)
        if option_el is None and termino != texto_opcion:
            logger.debug(f"[app-select emisor] No hallado por texto completo, buscando por RFC: '{termino}'")
            option_el = self.driver.execute_script(_js_find, termino)

        if option_el:
            try:
                ActionChains(self.driver).move_to_element(option_el).click().perform()
            except Exception:
                try:
                    option_el.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", option_el)
            logger.info(f"[app-select emisor] Opción seleccionada (RFC='{termino}'): '{texto_opcion}'")
            return

        # Fallback XPath: busca por texto completo acotado a app-emisor-factura
        fallback_xpath = (
            By.XPATH,
            f"//app-emisor-factura//*[contains(normalize-space(.), '{texto_opcion}') and "
            f"not(self::input) and not(self::textarea) and not(self::button) and "
            f"not(self::nav) and not(self::header)]"
            f" | //*[contains(@class,'option') and contains(normalize-space(.), '{texto_opcion}')]",
        )
        try:
            option = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(fallback_xpath)
            )
            option.click()
            logger.info(f"[app-select emisor] Opción seleccionada (XPath): '{texto_opcion}'")
        except TimeoutException:
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
                f"[EMISOR] No se encontró la opción '{texto_opcion}' (RFC='{termino}') en el app-select. "
                f"Textos visibles: {visibles[:10]}."
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
