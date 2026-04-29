"""
nota_credito_comprobante_page.py - Page Object de la sección "Comprobante" del formulario de Nota de Crédito.

Réplica exacta de FacturaComprobantePage pero aislada en el módulo de Nota de Crédito.
Componente HTML: <app-comprobante-factura>
"""
from typing import Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.core.base_page import BasePage
from app.utils.exceptions import PageError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NotaCreditoComprobantePage(BasePage):
    """
    Page Object para la sección "Comprobante" del formulario de Nota de Crédito CFDI 4.0.

    Componente Angular: <app-comprobante-factura>
    """

    # ------------------------------------------------------------------
    # Locators — Campos nativos con formcontrolname (ALTA ESTABILIDAD ✓)
    # ------------------------------------------------------------------

    FECHA_EMISION = (By.CSS_SELECTOR, "input[formcontrolname='fecha']")
    EXPORTACION = (By.CSS_SELECTOR, "select[formcontrolname='exportacion']")
    MONEDA = (By.CSS_SELECTOR, "select[formcontrolname='moneda']")
    TIPO_CAMBIO = (By.CSS_SELECTOR, "input[formcontrolname='tipoCambio']")
    CONDICIONES_PAGO = (By.CSS_SELECTOR, "input[formcontrolname='condicionesDePago']")
    NOTAS = (By.CSS_SELECTOR, "input[formcontrolname='notas']")
    REFERENCIA = (By.CSS_SELECTOR, "input[formcontrolname='referencia']")

    APP_SELECT_METODO_PAGO = (
        By.CSS_SELECTOR,
        "[data-testid='select-metodo-pago'] > div, "
        "app-select[placeholder*='todo de pago'] > div, "
        "app-select[placeholder*='étodo'] > div",
    )

    APP_SELECT_FORMA_PAGO = (
        By.CSS_SELECTOR,
        "[data-testid='select-forma-pago'] > div, "
        "app-select[placeholder*='orma de pago'] > div, "
        "app-select[placeholder*='orma'] > div",
    )

    IDIOMA = (
        By.CSS_SELECTOR,
        "[data-testid='select-idioma'], "
        "app-comprobante-factura select:not([formcontrolname])",
    )

    # ------------------------------------------------------------------
    # Validaciones
    # ------------------------------------------------------------------

    def is_section_loaded(self) -> bool:
        return self.is_visible((By.CSS_SELECTOR, "app-comprobante-factura"), timeout=10)

    # ------------------------------------------------------------------
    # Acciones — Campos nativos
    # ------------------------------------------------------------------

    def fill_fecha_emision(self, fecha_iso: str) -> None:
        if fecha_iso.upper() == "AUTO":
            logger.info("[NC COMPROBANTE] Fecha de emisión: usando valor por defecto del portal.")
            return
        element = self.wait_for_element(self.FECHA_EMISION, condition="visible")
        self.execute_script(
            """
            arguments[0].value = arguments[1];
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """,
            element,
            fecha_iso,
        )
        logger.info(f"[NC COMPROBANTE] Fecha de emisión ingresada: {fecha_iso}")

    def select_exportacion_by_value(self, valor: str) -> None:
        self.select_by_value(self.EXPORTACION, valor)
        logger.info(f"[NC COMPROBANTE] Exportación seleccionada: {valor}")

    def select_moneda_by_value(self, moneda: str) -> None:
        self.select_by_value(self.MONEDA, moneda)
        logger.info(f"[NC COMPROBANTE] Moneda seleccionada: {moneda}")

    def fill_tipo_cambio(self, tipo_cambio: str) -> None:
        self.type_text(self.TIPO_CAMBIO, tipo_cambio)
        logger.info(f"[NC COMPROBANTE] Tipo de cambio ingresado: {tipo_cambio}")

    def fill_condiciones_pago(self, condiciones: str) -> None:
        self.type_text(self.CONDICIONES_PAGO, condiciones)
        logger.info(f"[NC COMPROBANTE] Condiciones de pago ingresadas: {condiciones}")

    def fill_notas(self, notas: str) -> None:
        self.type_text(self.NOTAS, notas)
        logger.info(f"[NC COMPROBANTE] Notas ingresadas: {notas[:50]}...")

    def fill_referencia(self, referencia: str) -> None:
        self.type_text(self.REFERENCIA, referencia)
        logger.info(f"[NC COMPROBANTE] Referencia ingresada: {referencia}")

    def select_idioma_by_value(self, idioma: str) -> None:
        if not idioma:
            return
        _MAPA = {
            "espanol": "ES", "español": "ES", "es": "ES",
            "ingles": "EN", "inglés": "EN", "en": "EN",
        }
        valor = _MAPA.get(idioma.strip().lower(), idioma.strip())
        from selenium.common.exceptions import NoSuchElementException
        from selenium.webdriver.support.ui import Select as _Select
        element = self.wait_for_element(self.IDIOMA, condition="visible")
        sel = _Select(element)
        try:
            sel.select_by_value(valor)
        except NoSuchElementException:
            for opt in sel.options:
                if (opt.text.strip().lower().startswith(valor.lower()) or
                        opt.get_attribute("value").strip().lower() == valor.lower()):
                    opt.click()
                    break
            else:
                raise
        logger.info(f"[NC COMPROBANTE] Idioma seleccionado: {valor}")

    # ------------------------------------------------------------------
    # Helper: interacción con componente <app-select> Angular
    # ------------------------------------------------------------------

    def _click_app_select_option(self, trigger_locator: tuple, texto_opcion: str) -> None:
        import time as _time

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
        logger.debug(f"[NC app-select comprobante] Dropdown abierto, buscando: '{texto_opcion}'")

        _SEARCH_INPUT = (
            By.CSS_SELECTOR,
            "input[placeholder*='uscar'], input[placeholder*='earch'], "
            "input[placeholder*='ilter'], input[placeholder*='Buscar']",
        )
        try:
            search_box = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(_SEARCH_INPUT)
            )
            termino = texto_opcion.split(" - ")[0] if " - " in texto_opcion else texto_opcion
            search_box.clear()
            search_box.send_keys(termino)
        except TimeoutException:
            pass

        _time.sleep(0.5)

        _js_find = """
            const target = arguments[0];
            const all = document.querySelectorAll('*');
            for (const el of all) {
                const rect = el.getBoundingClientRect();
                if (rect.width === 0 || rect.height === 0) continue;
                if (rect.top < 0 || rect.left < 0) continue;
                const t = (el.textContent || '').trim();
                if (t === target && el.children.length === 0) return el;
            }
            for (const el of all) {
                const rect = el.getBoundingClientRect();
                if (rect.width === 0 || rect.height === 0) continue;
                const t = (el.textContent || '').trim();
                if (t === target) return el;
                if (t.includes(target) && el.children.length <= 2) return el;
            }
            return null;
        """
        option_el = self.driver.execute_script(_js_find, texto_opcion)
        if option_el:
            try:
                option_el.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", option_el)
            logger.info(f"[NC app-select comprobante] Opción seleccionada (JS): '{texto_opcion}'")
            return

        termino_busqueda = texto_opcion.split(" - ")[0] if " - " in texto_opcion else texto_opcion
        fallback_xpath = (
            By.XPATH,
            f"//*[contains(normalize-space(.), '{termino_busqueda}') and "
            f"not(self::input) and not(self::textarea) and not(self::button) and "
            f"not(self::nav) and not(self::header)]",
        )
        try:
            option = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(fallback_xpath)
            )
            option.click()
            logger.info(f"[NC app-select comprobante] Opción seleccionada (XPath): '{texto_opcion}'")
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
            logger.warning(f"[NC app-select comprobante] Textos visibles: {visibles}")
            raise PageError(
                f"[NC COMPROBANTE] No se encontró la opción '{texto_opcion}' en el app-select. "
                f"Textos visibles: {visibles[:10]}."
            )

    def select_metodo_pago(self, texto_opcion: str) -> None:
        if not texto_opcion:
            logger.info("[NC COMPROBANTE] Método de pago vacío — se omite.")
            return
        logger.info(f"[NC COMPROBANTE] Seleccionando Método de Pago: '{texto_opcion}'")
        self._click_app_select_option(self.APP_SELECT_METODO_PAGO, texto_opcion)

    def select_forma_pago(self, texto_opcion: str) -> None:
        if not texto_opcion:
            logger.info("[NC COMPROBANTE] Forma de pago vacía — se omite.")
            return
        logger.info(f"[NC COMPROBANTE] Seleccionando Forma de Pago: '{texto_opcion}'")
        self._click_app_select_option(self.APP_SELECT_FORMA_PAGO, texto_opcion)

    # ------------------------------------------------------------------
    # Método de llenado completo
    # ------------------------------------------------------------------

    def fill_comprobante_completo(
        self,
        fecha_emision: str = "AUTO",
        exportacion: str = "01",
        moneda: str = "MXN",
        tipo_cambio: str = "1",
        metodo_pago: str = "",
        forma_pago: str = "",
        condiciones_pago: str = "",
        notas: str = "",
        idioma: str = "",
        referencia: str = "",
    ) -> None:
        logger.info("[NC COMPROBANTE] Iniciando llenado completo de sección Comprobante.")

        self.fill_fecha_emision(fecha_emision)
        self.select_exportacion_by_value(exportacion)
        self.select_moneda_by_value(moneda)
        self.fill_tipo_cambio(tipo_cambio)
        self.select_metodo_pago(metodo_pago)
        self.select_forma_pago(forma_pago)

        if condiciones_pago:
            self.fill_condiciones_pago(condiciones_pago)
        if notas:
            self.fill_notas(notas)
        if idioma:
            self.select_idioma_by_value(idioma)
        if referencia:
            self.fill_referencia(referencia)

        logger.info("[NC COMPROBANTE] Sección Comprobante completada.")

    def fill_comprobante_desde_caso(self, caso: dict) -> None:
        def _codigo(valor: str, default: str = "") -> str:
            v = str(valor).strip()
            return v.split(" - ")[0].strip() if " - " in v else (v or default)

        self.fill_comprobante_completo(
            fecha_emision    = str(caso.get("fecha_emision",    "AUTO")).strip(),
            exportacion      = _codigo(caso.get("exportacion",      ""), "01"),
            moneda           = _codigo(caso.get("moneda",           ""), "MXN"),
            tipo_cambio      = str(caso.get("tipo_cambio",      "1")).strip(),
            metodo_pago      = str(caso.get("metodo_pago",      "")).strip(),
            forma_pago       = str(caso.get("forma_pago",       "")).strip(),
            condiciones_pago = str(caso.get("condiciones_pago", "")).strip(),
            notas            = str(caso.get("observaciones_pdf", caso.get("notas", ""))).strip(),
            idioma           = _codigo(caso.get("idioma",           ""), "ES"),
            referencia       = str(caso.get("referencia",       "")).strip(),
        )
        integraciones = str(caso.get("integraciones", "")).strip()
        if integraciones:
            self.seleccionar_integraciones(integraciones)

    def seleccionar_integraciones(self, valor: str) -> None:
        _MULTISELECT_TRIGGER = (
            By.CSS_SELECTOR,
            "[data-testid='select-integraciones'] > div, "
            "app-comprobante-factura app-multiselect[placeholder*='ntegra'] > div",
        )
        opciones = [v.strip() for v in valor.split("|") if v.strip()]
        for opcion in opciones:
            try:
                self.scroll_into_view(_MULTISELECT_TRIGGER)
                self.click(_MULTISELECT_TRIGGER)
                logger.debug(f"[NC COMPROBANTE][INTEGRACIONES] Dropdown abierto, buscando: '{opcion}'")
                option_xpath = (
                    By.XPATH,
                    f"//div[@data-select-host]//li[normalize-space(.)='{opcion}'] | "
                    f"//div[@data-select-host]//div[@role='option'][normalize-space(.)='{opcion}'] | "
                    f"//div[contains(@class,'option')][normalize-space(.)='{opcion}']",
                )
                wait = WebDriverWait(self.driver, 10)
                option_el = wait.until(EC.element_to_be_clickable(option_xpath))
                option_el.click()
                logger.info(f"[NC COMPROBANTE][INTEGRACIONES] Opción seleccionada: '{opcion}'")
            except TimeoutException:
                logger.warning(
                    f"[NC COMPROBANTE][INTEGRACIONES] No se encontró la opción '{opcion}'. "
                    "Verificar placeholder del app-multiselect en el portal."
                )
