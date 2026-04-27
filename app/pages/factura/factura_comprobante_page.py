"""
factura_comprobante_page.py - Page Object de la sección "Comprobante" del formulario de Factura.

Componente HTML: <app-comprobante-factura>

============================================================
ANÁLISIS DE SELECTORES — app-comprobante-factura (HTML analizado)
============================================================

HTML OBSERVADO — campos con formcontrolname (ALTA ESTABILIDAD ✓):
  - input[formcontrolname="fecha"]              → Fecha de Emisión (datetime-local)
  - select[formcontrolname="exportacion"]       → Exportación (01/02/03)
  - select[formcontrolname="moneda"]            → Moneda (MXN, USD, etc.)
  - input[formcontrolname="tipoCambio"]         → Tipo de Cambio (number)
  - input[formcontrolname="condicionesDePago"]  → Condiciones de Pago (text)
  - input[formcontrolname="notas"]              → Observaciones / Notas PDF (text)
  - input[formcontrolname="referencia"]         → Referencia (text)

HTML OBSERVADO — componentes custom Angular (BAJA ESTABILIDAD ⚠️):
  - <app-select data-select-host="true" placeholder="Seleccione método de pago...">
    → Método de Pago: componente <app-select> personalizado
    → Interacción: click trigger → esperar opciones → click opción por texto
  - <app-select data-select-host="true" placeholder="Seleccione forma de pago...">
    → Forma de Pago: idem

HTML OBSERVADO — selects sin formcontrolname (MEDIUM ESTABILIDAD):
  - select sin formcontrolname dentro de app-comprobante-factura
    → Idioma (opciones: ES, EN) — único select sin formcontrolname en la sección

SELECTORES RIESGOSOS:
  ⚠️  app-comprobante-factura app-select:nth-of-type(1/2): positional para custom selects
  ⚠️  app-comprobante-factura select:not([formcontrolname]): selector negativo para Idioma

DATA-TESTID RECOMENDADOS AL EQUIPO FRONTEND:
  - data-testid="select-metodo-pago"      → <app-select> Método de Pago
  - data-testid="select-forma-pago"       → <app-select> Forma de Pago
  - data-testid="select-idioma"           → <select> Idioma
  - data-testid="select-integraciones"    → <app-multiselect> Integraciones
  - data-testid="comprobante-container"   → contenedor de la sección
============================================================
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


class FacturaComprobantePage(BasePage):
    """
    Page Object para la sección "Comprobante" del formulario de Factura CFDI 4.0.

    Componente Angular: <app-comprobante-factura>

    Sección nro. 3 del formulario. Cubre:
    - Fecha de Emisión
    - Exportación
    - Moneda y Tipo de Cambio
    - Método de Pago (componente app-select custom)
    - Forma de Pago (componente app-select custom)
    - Condiciones de Pago
    - Observaciones / Notas en PDF
    - Idioma
    - Referencia
    """

    # ------------------------------------------------------------------
    # Locators — Campos nativos con formcontrolname (ALTA ESTABILIDAD ✓)
    # ------------------------------------------------------------------

    # Fecha de Emisión — input datetime-local con formcontrolname="fecha"
    FECHA_EMISION = (By.CSS_SELECTOR, "input[formcontrolname='fecha']")

    # Exportación — select nativo con formcontrolname="exportacion"
    EXPORTACION = (By.CSS_SELECTOR, "select[formcontrolname='exportacion']")

    # Moneda — select nativo con formcontrolname="moneda"
    MONEDA = (By.CSS_SELECTOR, "select[formcontrolname='moneda']")

    # Tipo de Cambio — input number con formcontrolname="tipoCambio"
    TIPO_CAMBIO = (By.CSS_SELECTOR, "input[formcontrolname='tipoCambio']")

    # Condiciones de Pago — input text con formcontrolname="condicionesDePago"
    CONDICIONES_PAGO = (By.CSS_SELECTOR, "input[formcontrolname='condicionesDePago']")

    # Observaciones / Notas — input text con formcontrolname="notas"
    NOTAS = (By.CSS_SELECTOR, "input[formcontrolname='notas']")

    # Referencia — input text con formcontrolname="referencia"
    REFERENCIA = (By.CSS_SELECTOR, "input[formcontrolname='referencia']")

    # ------------------------------------------------------------------
    # Locators — Componentes custom app-select (BAJA ESTABILIDAD ⚠️)
    # Interacción especial: click trigger → esperar opciones → click opción
    # ------------------------------------------------------------------

    # Método de Pago — primer <app-select> en el componente
    # ⚠️  Posicional. Si se agrega otro app-select antes, se rompe.
    # TODO: solicitar al equipo frontend agregar data-testid="select-metodo-pago"
    APP_SELECT_METODO_PAGO = (
        By.CSS_SELECTOR,
        "[data-testid='select-metodo-pago'] > div, "
        "app-select[placeholder*='todo de pago'] > div, "
        "app-select[placeholder*='étodo'] > div",
    )

    # Forma de Pago — app-select por placeholder (MEDIUM stability)
    APP_SELECT_FORMA_PAGO = (
        By.CSS_SELECTOR,
        "[data-testid='select-forma-pago'] > div, "
        "app-select[placeholder*='orma de pago'] > div, "
        "app-select[placeholder*='orma'] > div",
    )

    # Opciones del dropdown de app-select (genérico, aplica a ambos)
    # Renderizadas en el DOM después de hacer click en el trigger.
    # TODO: Confirmar con equipo frontend el selector real del panel de opciones.
    _APP_SELECT_OPTION_TEMPLATE = (
        By.XPATH,
        "//*[contains(@class,'option') or local-name()='li'][normalize-space(.)='{text}']",
    )

    # ------------------------------------------------------------------
    # Locators — Idioma (select nativo sin formcontrolname)
    # ------------------------------------------------------------------

    # Idioma — selector negativo porque es el único select sin formcontrolname
    # en app-comprobante-factura (los otros tienen: exportacion, moneda).
    # TODO: solicitar al equipo frontend agregar data-testid="select-idioma"
    IDIOMA = (
        By.CSS_SELECTOR,
        "[data-testid='select-idioma'], "
        "app-comprobante-factura select:not([formcontrolname])",
    )

    # ------------------------------------------------------------------
    # Validaciones
    # ------------------------------------------------------------------

    def is_section_loaded(self) -> bool:
        """Verifica que la sección Comprobante está visible."""
        return self.is_visible(
            (By.CSS_SELECTOR, "app-comprobante-factura"),
            timeout=10,
        )

    # ------------------------------------------------------------------
    # Acciones — Campos nativos
    # ------------------------------------------------------------------

    def fill_fecha_emision(self, fecha_iso: str) -> None:
        """
        Ingresa la Fecha de Emisión del CFDI.

        El campo acepta formato datetime-local (HTML5): 'YYYY-MM-DDTHH:MM:SS'
        Si se pasa 'AUTO', el flujo no toca este campo (el portal lo pre-rellena).

        Args:
            fecha_iso: Fecha en formato 'YYYY-MM-DDTHH:MM:SS'
                       o 'AUTO' para no modificar el valor por defecto.
        """
        if fecha_iso.upper() == "AUTO":
            logger.info("[COMPROBANTE] Fecha de emisión: usando valor por defecto del portal.")
            return
        # Selenium no puede escribir directamente en datetime-local en todos los browsers.
        # Se usa JavaScript para establecer el valor y disparar el evento change.
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
        logger.info(f"[COMPROBANTE] Fecha de emisión ingresada: {fecha_iso}")

    def select_exportacion_by_value(self, valor: str) -> None:
        """
        Selecciona el tipo de Exportación.

        Args:
            valor: '01' (No aplica), '02' (Definitiva), '03' (Temporal).
        """
        self.select_by_value(self.EXPORTACION, valor)
        logger.info(f"[COMPROBANTE] Exportación seleccionada: {valor}")

    def select_moneda_by_value(self, moneda: str) -> None:
        """
        Selecciona la Moneda del CFDI.

        Args:
            moneda: Código ISO 4217 (ej: 'MXN', 'USD', 'EUR').
        """
        self.select_by_value(self.MONEDA, moneda)
        logger.info(f"[COMPROBANTE] Moneda seleccionada: {moneda}")

    def fill_tipo_cambio(self, tipo_cambio: str) -> None:
        """
        Ingresa el Tipo de Cambio respecto al peso mexicano.

        Args:
            tipo_cambio: Valor numérico como string (ej: '17.50', '1').
                         Para MXN siempre es '1'.
        """
        self.type_text(self.TIPO_CAMBIO, tipo_cambio)
        logger.info(f"[COMPROBANTE] Tipo de cambio ingresado: {tipo_cambio}")

    def fill_condiciones_pago(self, condiciones: str) -> None:
        """
        Ingresa las Condiciones de Pago.

        Args:
            condiciones: Texto libre (ej: 'NET30', 'CONTADO', '15 días').
        """
        self.type_text(self.CONDICIONES_PAGO, condiciones)
        logger.info(f"[COMPROBANTE] Condiciones de pago ingresadas: {condiciones}")

    def fill_notas(self, notas: str) -> None:
        """
        Ingresa las Observaciones / Notas que aparecerán en el PDF.

        Args:
            notas: Texto libre de hasta N caracteres.
        """
        self.type_text(self.NOTAS, notas)
        logger.info(f"[COMPROBANTE] Notas ingresadas: {notas[:50]}...")

    def fill_referencia(self, referencia: str) -> None:
        """
        Ingresa la Referencia interna o folio de reserva.

        Args:
            referencia: Referencia interna (ej: 'AUTO-FACTURA-001', 'RESERVA-12345').
        """
        self.type_text(self.REFERENCIA, referencia)
        logger.info(f"[COMPROBANTE] Referencia ingresada: {referencia}")

    def select_idioma_by_value(self, idioma: str) -> None:
        """
        Selecciona el Idioma del comprobante.

        Args:
            idioma: 'ES' / 'Espanol' / 'Español' (Español) o 'EN' / 'Ingles' / 'Inglés' (Inglés).
        """
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
                if opt.text.strip().lower().startswith(valor.lower()) or opt.get_attribute("value").strip().lower() == valor.lower():
                    opt.click()
                    break
            else:
                raise
        logger.info(f"[COMPROBANTE] Idioma seleccionado: {valor}")

    # ------------------------------------------------------------------
    # Acciones — Componentes custom app-select
    # Estrategia: click trigger → esperar panel → click opción por texto
    # ------------------------------------------------------------------

    def _click_app_select_option(self, trigger_locator: tuple, texto_opcion: str) -> None:
        """
        Interactúa con un componente <app-select> personalizado de Angular.

        Mismo flujo JS que factura_emisor_page: overlay-wait → click trigger →
        search box → JS getBoundingClientRect() para encontrar opción → XPath fallback.
        """
        import time as _time

        # 1. Esperar que desaparezca el overlay de carga del portal
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
        logger.debug(f"[app-select comprobante] Dropdown abierto, buscando: '{texto_opcion}'")

        # 2. Si hay campo de búsqueda, filtrar con el primer token
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
            logger.debug(f"[app-select comprobante] Búsqueda escrita: '{termino}'")
        except TimeoutException:
            pass

        _time.sleep(0.5)

        # 3. JS: buscar opción visible por texto exacto / parcial
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
            logger.info(f"[app-select comprobante] Opción seleccionada (JS): '{texto_opcion}'")
            return

        # 4. XPath fallback por primer token
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
            logger.info(f"[app-select comprobante] Opción seleccionada (XPath): '{texto_opcion}'")
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
            logger.warning(f"[app-select comprobante] Textos visibles: {visibles}")
            raise PageError(
                f"[COMPROBANTE] No se encontró la opción '{texto_opcion}' en el app-select. "
                f"Textos visibles: {visibles[:10]}."
            )

    def select_metodo_pago(self, texto_opcion: str) -> None:
        """
        Selecciona el Método de Pago en el componente app-select personalizado.

        Args:
            texto_opcion: Texto visible del método (ej: 'PUE - Pago en una sola exhibición',
                          'PPD - Pago en parcialidades o diferido').

        ⚠️  Usa componente <app-select> custom. Si falla, solicitar:
            data-testid="select-metodo-pago" al equipo frontend.
        """
        if not texto_opcion:
            return
        logger.info(f"[COMPROBANTE] Seleccionando Método de Pago: {texto_opcion}")
        self._click_app_select_option(self.APP_SELECT_METODO_PAGO, texto_opcion)

    def select_forma_pago(self, texto_opcion: str) -> None:
        """
        Selecciona la Forma de Pago en el componente app-select personalizado.

        Args:
            texto_opcion: Texto visible de la forma (ej: '01 - Efectivo',
                          '03 - Transferencia electrónica de fondos',
                          '99 - Por definir').

        ⚠️  Usa componente <app-select> custom. Si falla, solicitar:
            data-testid="select-forma-pago" al equipo frontend.
        """
        if not texto_opcion:
            return
        logger.info(f"[COMPROBANTE] Seleccionando Forma de Pago: {texto_opcion}")
        self._click_app_select_option(self.APP_SELECT_FORMA_PAGO, texto_opcion)

    # ------------------------------------------------------------------
    # Método de llenado completo
    # ------------------------------------------------------------------

    def fill_comprobante_completo(
        self,
        fecha_emision: str,
        exportacion: str,
        moneda: str,
        tipo_cambio: str,
        metodo_pago: str,
        forma_pago: str,
        condiciones_pago: str = "",
        notas: str = "",
        idioma: str = "ES",
        referencia: str = "",
    ) -> None:
        """
        Llena todos los campos de la sección Comprobante en un solo paso.

        Args:
            fecha_emision:    ISO datetime o 'AUTO' para usar valor del portal.
            exportacion:      Código exportación ('01', '02', '03').
            moneda:           Código ISO moneda ('MXN', 'USD').
            tipo_cambio:      Tipo de cambio como string.
            metodo_pago:      Texto visible del método ('PUE - ...', 'PPD - ...').
            forma_pago:       Texto visible de la forma ('01 - Efectivo', ...).
            condiciones_pago: Texto libre (opcional).
            notas:            Notas para el PDF (opcional).
            idioma:           'ES' o 'EN'.
            referencia:       Referencia interna (opcional).
        """
        logger.info("[COMPROBANTE] Iniciando llenado completo de sección Comprobante.")

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

        logger.info("[COMPROBANTE] Sección Comprobante completada.")

    def fill_comprobante_desde_caso(self, caso: dict) -> None:
        """
        Llena la sección Comprobante con un dict plano proveniente del Excel.

        Mapea directamente las claves del Excel a los métodos de esta página.
        Este método es el punto de entrada desde FacturaFlow cuando los datos
        provienen del archivo `factura_casos.xlsx`.

        Args:
            caso: Dict plano con claves como fecha_emision, exportacion,
                  moneda, tipo_cambio, metodo_pago, forma_pago, etc.
        """
        def _codigo(valor: str, default: str = "") -> str:
            """Para <select> nativo: extrae código antes del ' - '."""
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
        # Integraciones es opcional y usa app-multiselect
        integraciones = str(caso.get("integraciones", "")).strip()
        if integraciones:
            self.seleccionar_integraciones(integraciones)

    def seleccionar_integraciones(self, valor: str) -> None:
        """
        Selecciona una integración en el componente <app-multiselect>.

        Flujo idéntico a _click_app_select_option pero para multiselect:
        click trigger → esperar opciones → click por texto.

        Args:
            valor: Texto visible de la integración (ej: 'Opera PMS').
                   Para múltiples valores separarlos con ' | '.

        TODO: Verificar selector real del trigger de <app-multiselect>
              cuando se cuente con el DOM de la sección Comprobante con
              integraciones visibles.
        """
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException

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
                logger.debug(f"[COMPROBANTE][INTEGRACIONES] Dropdown abierto, buscando: '{opcion}'")

                option_xpath = (
                    By.XPATH,
                    f"//div[@data-select-host]//li[normalize-space(.)='{opcion}'] | "
                    f"//div[@data-select-host]//div[@role='option'][normalize-space(.)='{opcion}'] | "
                    f"//div[contains(@class,'option')][normalize-space(.)='{opcion}']",
                )
                wait = WebDriverWait(self.driver, 10)
                option_el = wait.until(EC.element_to_be_clickable(option_xpath))
                option_el.click()
                logger.info(f"[COMPROBANTE][INTEGRACIONES] Opción seleccionada: '{opcion}'")
            except TimeoutException:
                logger.warning(
                    f"[COMPROBANTE][INTEGRACIONES] No se encontró la opción '{opcion}'. "
                    "Verificar placeholder del app-multiselect en el portal."
                )
