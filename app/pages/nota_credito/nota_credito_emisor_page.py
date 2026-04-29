"""
nota_credito_emisor_page.py - Page Object de la sección Emisor del formulario de Nota de Crédito.

Réplica exacta de FacturaEmisorPage pero aislada en el módulo de Nota de Crédito.
Componente HTML: <app-emisor-factura>
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from app.core.base_page import BasePage
from app.utils.exceptions import PageError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NotaCreditoEmisorPage(BasePage):
    """
    Page Object para la sección del Emisor en el formulario de Nota de Crédito.

    Componente Angular: <app-emisor-factura>
    """

    CONTENEDOR_EMISOR = (By.CSS_SELECTOR, "app-emisor-factura")

    NOMBRE_EMISOR = (
        By.CSS_SELECTOR,
        "[data-testid='emisor-nombre'], "
        "app-emisor-factura .flex-col:nth-of-type(1) span.font-semibold",
    )

    RFC_EMISOR = (
        By.CSS_SELECTOR,
        "[data-testid='emisor-rfc'], "
        "app-emisor-factura .flex-col:nth-of-type(2) span.font-semibold",
    )

    REGIMEN_FISCAL_EMISOR = (
        By.CSS_SELECTOR,
        "[data-testid='emisor-regimen-fiscal'], "
        "app-emisor-factura .flex-col:nth-of-type(3) span.font-semibold",
    )

    SELECT_CENTRO_CONSUMO_TRIGGER = (
        By.CSS_SELECTOR,
        "[data-testid='select-centro-consumo'] > div, "
        "app-emisor-factura app-select[formcontrolname='centroConsumo'] > div, "
        "app-emisor-factura app-select[ng-reflect-name='centroConsumo'] > div, "
        "app-emisor-factura app-select[placeholder='Seleccione Centro de Consumo'] > div, "
        "app-emisor-factura app-select[ng-reflect-placeholder='Seleccione Centro de Consumo'] > div",
    )

    SELECT_SERIE_TRIGGER = (
        By.CSS_SELECTOR,
        "[data-testid='select-serie'] > div, "
        "app-emisor-factura app-select[placeholder='Seleccione Serie'] > div",
    )

    # ------------------------------------------------------------------
    # Validaciones
    # ------------------------------------------------------------------

    def is_loaded(self) -> bool:
        return self.is_visible(self.CONTENEDOR_EMISOR, timeout=10)

    def wait_for_emisor_loaded(self) -> None:
        self.wait_for_element(self.CONTENEDOR_EMISOR, condition="visible", timeout=15)
        logger.info("[NC EMISOR] Sección de emisor cargada.")

    # ------------------------------------------------------------------
    # Lectura de datos readonly
    # ------------------------------------------------------------------

    def get_nombre_emisor(self) -> str:
        try:
            return self.get_text(self.NOMBRE_EMISOR)
        except Exception:
            logger.warning("[NC EMISOR] No se pudo leer el nombre del emisor.")
            return ""

    def get_rfc_emisor(self) -> str:
        try:
            return self.get_text(self.RFC_EMISOR)
        except Exception:
            logger.warning("[NC EMISOR] No se pudo leer el RFC del emisor.")
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
            logger.debug("[NC EMISOR] CDK select overlay backdrop descartado antes de abrir select.")
        except Exception:
            pass

    def _click_app_select_option(self, trigger_locator: tuple, texto_opcion: str) -> None:
        """Interactúa con un componente <app-select> personalizado de Angular."""
        import time as _time
        from selenium.webdriver.common.action_chains import ActionChains

        # Descartar cualquier CDK select overlay residual (p.ej. del drawer de Paso 2b)
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
        logger.debug(f"[NC app-select emisor] Dropdown abierto, buscando RFC: '{termino}'")

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
            # Buscar con texto completo para filtrar la opción exacta (evita match parcial con opciones similares)
            search_box.send_keys(texto_opcion)
            logger.debug(f"[NC app-select emisor] Búsqueda por texto completo: '{texto_opcion}'")
        except TimeoutException:
            pass

        _time.sleep(0.8)

        _js_find = """
            const target = arguments[0];
            const normalizeText = t => (t || '').trim().replace(/\\s+/g, ' ');
            const targetNorm = normalizeText(target);
            const containers = [document.querySelector('app-emisor-factura'), document.body];
            for (const container of containers) {
                if (!container) continue;
                const all = container.querySelectorAll('*');
                // Primer paso: texto exacto normalizado, elemento hoja
                for (const el of all) {
                    const rect = el.getBoundingClientRect();
                    if (rect.width === 0 || rect.height === 0) continue;
                    if (rect.top < 0 || rect.left < 0) continue;
                    const t = normalizeText(el.textContent);
                    if (t === targetNorm && el.children.length === 0) return el;
                }
                // Segundo paso: texto exacto normalizado (con hijos permitidos)
                for (const el of all) {
                    const rect = el.getBoundingClientRect();
                    if (rect.width === 0 || rect.height === 0) continue;
                    const t = normalizeText(el.textContent);
                    if (t === targetNorm) return el;
                    if (t.includes(targetNorm) && el.children.length <= 2) return el;
                }
                if (container !== document.body) continue;
                break;
            }
            return null;
        """
        # Buscar por texto completo primero, luego por RFC (primer token del Excel)
        option_el = self.driver.execute_script(_js_find, texto_opcion)
        if option_el is None and termino != texto_opcion:
            logger.debug(f"[NC app-select emisor] No hallado por texto completo, buscando por RFC: '{termino}'")
            option_el = self.driver.execute_script(_js_find, termino)

        if option_el:
            try:
                ActionChains(self.driver).move_to_element(option_el).click().perform()
            except Exception:
                try:
                    option_el.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", option_el)
            logger.info(f"[NC app-select emisor] Opción seleccionada (RFC='{termino}'): '{texto_opcion}'")
            return

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
            logger.info(f"[NC app-select emisor] Opción seleccionada (XPath texto completo): '{texto_opcion}'")
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
            logger.warning(f"[NC app-select emisor] Textos visibles en DOM: {visibles}")
            raise PageError(
                f"[NC EMISOR] No se encontró la opción '{texto_opcion}' (RFC='{termino}') en el app-select. "
                f"Textos visibles: {visibles[:10]}."
            )

    # ------------------------------------------------------------------
    # Selección de parámetros del CFDI
    # ------------------------------------------------------------------

    def select_centro_consumo(self, valor: str) -> None:
        logger.info(f"[NC EMISOR] Seleccionando Centro de Consumo: '{valor}'")
        self._click_app_select_option(self.SELECT_CENTRO_CONSUMO_TRIGGER, valor)

    def select_serie(self, serie: str) -> None:
        if not serie or not str(serie).strip():
            logger.info("[NC EMISOR] Serie vacía — se omite la selección de serie.")
            return
        logger.info(f"[NC EMISOR] Seleccionando Serie: '{serie}'")
        self._click_app_select_option(self.SELECT_SERIE_TRIGGER, str(serie).strip())

    def leer_centro_consumo_seleccionado(self) -> str:
        """Lee el texto del dropdown Centro de Consumo tras la selección."""
        import re as _re
        try:
            el = self.driver.find_element(*self.SELECT_CENTRO_CONSUMO_TRIGGER)
            texto = (el.text or el.get_attribute("textContent") or "").strip()
            texto = _re.sub(r'\b(close|expand_more|expand_less|arrow_drop_down)\b', '', texto).strip()
            return texto
        except Exception:
            return "(no se pudo leer)"
