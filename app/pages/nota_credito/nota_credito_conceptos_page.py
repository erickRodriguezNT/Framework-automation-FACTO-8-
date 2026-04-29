"""
nota_credito_conceptos_page.py - Page Object de la sección Conceptos del formulario de Nota de Crédito.

Réplica exacta de FacturaConceptosPage pero aislada en el módulo de Nota de Crédito.
Componente HTML: <app-conceptos-factura>
"""
import time
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.core.base_page import BasePage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NotaCreditoConceptosPage(BasePage):
    """
    Page Object para la sección de Conceptos en el formulario de Nota de Crédito.

    Componente Angular: <app-conceptos-factura>
    """

    # ------------------------------------------------------------------
    # Locators — Tabla de conceptos y botón Agregar
    # ------------------------------------------------------------------

    BTN_AGREGAR_CONCEPTO = (
        By.CSS_SELECTOR,
        "[data-testid='btn-agregar-concepto'], "
        "app-modal-agregar-concepto button",
    )

    CONCEPTOS_TABLE_ROWS = (
        By.CSS_SELECTOR,
        "app-conceptos-factura table tbody tr, "
        "app-conceptos-factura .concepto-row",
    )

    # ------------------------------------------------------------------
    # Locators — Modal de agregar concepto
    # ------------------------------------------------------------------

    MODAL_AGREGAR = (By.CSS_SELECTOR, "app-modal-agregar-concepto")
    MODAL_BTN_GUARDAR = (
        By.CSS_SELECTOR,
        "app-modal-agregar-concepto "
        "div.flex.items-center.justify-end.gap-3.px-6.py-4.border-t "
        "button.bg-\\[\\#1760d7\\]",
    )
    MODAL_BTN_AGREGAR_IMPUESTO = (
        By.XPATH,
        "//app-modal-agregar-concepto//button[contains(normalize-space(.), 'Agregar Impuesto')]",
    )

    # ------------------------------------------------------------------
    # Locators — Campos del modal
    # ------------------------------------------------------------------

    MODAL_DESCRIPCION = (By.CSS_SELECTOR, "app-modal-agregar-concepto input[formcontrolname='descripcion']")
    MODAL_CANTIDAD = (By.CSS_SELECTOR, "app-modal-agregar-concepto input[formcontrolname='cantidad']")
    MODAL_NO_IDENTIFICACION = (By.CSS_SELECTOR, "app-modal-agregar-concepto input[formcontrolname='noIdentificacion']")
    MODAL_VALOR_UNITARIO = (By.CSS_SELECTOR, "app-modal-agregar-concepto input[formcontrolname='valorUnitario']")
    MODAL_CLAVE_PROD_SERV = (
        By.CSS_SELECTOR,
        "app-modal-agregar-concepto app-select-async[formcontrolname='claveProdServ'] > div, "
        "app-modal-agregar-concepto app-select-async[ng-reflect-name='claveProdServ'] > div",
    )
    MODAL_CLAVE_UNIDAD = (
        By.CSS_SELECTOR,
        "app-modal-agregar-concepto app-select-async[formcontrolname='claveUnidad'] > div, "
        "app-modal-agregar-concepto app-select-async[ng-reflect-name='claveUnidad'] > div",
    )
    MODAL_OBJETO_IMPUESTO = (By.CSS_SELECTOR, "app-modal-agregar-concepto select[formcontrolname='objetoImp']")
    MODAL_DESCUENTO = (By.CSS_SELECTOR, "app-modal-agregar-concepto input[formcontrolname='descuento']")
    MODAL_IMPUESTO_TRIGGER = (
        By.CSS_SELECTOR,
        "app-modal-agregar-concepto app-select[formcontrolname='impuesto'] > div, "
        "app-modal-agregar-concepto app-select[placeholder*='mpuesto'] > div",
    )
    MODAL_RETENCION_O_TRASLADO = (By.CSS_SELECTOR, "app-modal-agregar-concepto select[formcontrolname='retencionOTraslado']")
    MODAL_TIPO_FACTOR = (By.CSS_SELECTOR, "app-modal-agregar-concepto select[formcontrolname='tipoFactor']")
    MODAL_TASA_O_CUOTA = (By.CSS_SELECTOR, "app-modal-agregar-concepto input[formcontrolname='tasaoCuota']")

    # ------------------------------------------------------------------
    # Helpers de espera
    # ------------------------------------------------------------------

    def _wait_for_modal_abierto(self, timeout: int = 10) -> None:
        self.wait_for_element(self.MODAL_AGREGAR, condition="visible", timeout=timeout)
        logger.debug("[NC CONCEPTOS] Modal de agregar concepto abierto.")

    def _wait_for_modal_cerrado(self, timeout: int = 5) -> None:
        import time as _time
        logger.debug("[NC CONCEPTOS] Esperando cierre del modal...")
        # Angular no oculta el componente app-modal-agregar-concepto en sí,
        # sino su contenido interno. Igual que factura: esperamos que el campo
        # 'descripcion' dentro del modal deje de ser visible.
        _campo_interno = (By.CSS_SELECTOR, "app-modal-agregar-concepto input[formcontrolname='descripcion']")
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(_campo_interno)
            )
            logger.debug("[NC CONCEPTOS] Modal de agregar concepto cerrado.")
        except TimeoutException:
            logger.warning(
                f"[NC CONCEPTOS] Modal podría no haberse cerrado tras {timeout}s — continuando."
            )
        # Pausa extra para que Angular actualice la tabla de conceptos
        _time.sleep(0.5)

    def get_cantidad_conceptos(self) -> int:
        try:
            filas = self.driver.find_elements(*self.CONCEPTOS_TABLE_ROWS)
            return len(filas)
        except Exception:
            return 0

    def wait_for_nuevo_concepto_guardado(self, count_antes: int, timeout: int = 15) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.get_cantidad_conceptos() > count_antes:
                logger.info(f"[NC CONCEPTOS] Concepto confirmado en tabla (antes={count_antes}).")
                return
            time.sleep(0.5)
        logger.warning("[NC CONCEPTOS] No se confirmó el nuevo concepto en la tabla.")

    def click_agregar_concepto(self) -> None:
        self.wait_for_element(self.BTN_AGREGAR_CONCEPTO, condition="clickable", timeout=15)
        self.click(self.BTN_AGREGAR_CONCEPTO)
        logger.info("[NC CONCEPTOS] Click en botón Agregar Concepto.")

    def pause(self, seconds=2, reason=None):
        if reason:
            logger.info(f"[PAUSE] esperando {seconds}s - {reason}")
        time.sleep(seconds)

    # ------------------------------------------------------------------
    # Helpers de interacción con app-select y app-select-async
    # ------------------------------------------------------------------

    def _click_app_select_async_option(self, formcontrolname: str, texto_opcion: str) -> None:
        import time as _time

        _HOST_LOC = (
            By.CSS_SELECTOR,
            f"app-modal-agregar-concepto app-select-async[formcontrolname='{formcontrolname}']",
        )
        try:
            host = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(_HOST_LOC)
            )
        except TimeoutException:
            raise TimeoutException(
                f"No se encontró app-select-async[formcontrolname='{formcontrolname}']"
            )

        # 1. Scroll + click en el trigger div para abrir el dropdown
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", host)
        trigger_div = host.find_element(By.CSS_SELECTOR, "div")
        try:
            trigger_div.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", trigger_div)

        # 2. Esperar el input de búsqueda que aparece tras abrir el dropdown
        _INPUT_CSS = (
            f"app-modal-agregar-concepto "
            f"app-select-async[formcontrolname='{formcontrolname}'] input"
        )
        _time.sleep(0.4)
        try:
            search_input = WebDriverWait(self.driver, 6).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, _INPUT_CSS))
            )
        except TimeoutException:
            search_input = WebDriverWait(self.driver, 4).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR,
                    "input[placeholder*='caracteres'], input[placeholder*='Escribe']")
                )
            )

        # 3. Escribir el término de búsqueda
        termino = texto_opcion.split(" - ")[0] if " - " in texto_opcion else texto_opcion
        search_input.clear()
        search_input.send_keys(termino)
        _time.sleep(2.5)  # debounce + tiempo de API async

        # 4. Buscar y clickear la opción resultante
        _js_find_in_async = """
            const fc = arguments[0];
            const target = arguments[1];
            const host = document.querySelector(
                `app-modal-agregar-concepto app-select-async[formcontrolname="${fc}"]`
            );
            const containers = [host, document.body];
            for (const container of containers) {
                if (!container) continue;
                const els = container.querySelectorAll('div, span, li, p');
                for (const el of els) {
                    const rect = el.getBoundingClientRect();
                    if (rect.width === 0 || rect.height === 0) continue;
                    const t = (el.textContent || '').trim();
                    if (t.startsWith(target) && el.children.length === 0) return el;
                    if (t.startsWith(target) && el.children.length <= 2) return el;
                    if (t === target) return el;
                    if (t.includes(target) && el.children.length === 0) return el;
                }
            }
            return null;
        """
        option_el = self.driver.execute_script(_js_find_in_async, formcontrolname, termino)
        if option_el:
            try:
                option_el.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", option_el)
            logger.info(f"[NC CONCEPTOS app-select-async] Opción seleccionada: '{texto_opcion}'")
            return

        fallback = (
            By.XPATH,
            f"//app-modal-agregar-concepto//app-select-async[@formcontrolname='{formcontrolname}']"
            f"//*[contains(normalize-space(.), '{termino}') and not(self::input)]"
            f" | //*[contains(@class,'option') and contains(normalize-space(.), '{termino}')]"
            f" | //*[contains(@class,'item') and contains(normalize-space(.), '{termino}') and not(self::input)]",
        )
        try:
            opt = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(fallback))
            opt.click()
            logger.info(f"[NC CONCEPTOS app-select-async] Opción seleccionada (XPath): '{texto_opcion}'")
        except TimeoutException:
            raise TimeoutException(
                f"No se encontró opción '{texto_opcion}' en app-select-async[formcontrolname='{formcontrolname}']"
            )

    def _click_app_select_option(self, trigger_locator: tuple, texto_opcion: str, sleep_after_type: float = 0.5) -> None:
        _OVERLAY = (By.CSS_SELECTOR, "div.fixed.inset-0[class*='z-']")
        try:
            WebDriverWait(self.driver, 10).until(EC.invisibility_of_element_located(_OVERLAY))
        except TimeoutException:
            pass
        try:
            trigger = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(trigger_locator))
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", trigger)
        except TimeoutException:
            raise TimeoutException(f"No se encontró trigger app-select para '{texto_opcion}': {trigger_locator}")
        try:
            trigger.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", trigger)

        _SEARCH_INPUT = (
            By.CSS_SELECTOR,
            "input[placeholder*='uscar'], input[placeholder*='earch'], "
            "input[placeholder*='ilter'], input[placeholder*='Buscar']",
        )
        try:
            search_box = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(_SEARCH_INPUT))
            termino = texto_opcion.split(" - ")[0] if " - " in texto_opcion else texto_opcion
            search_box.clear()
            search_box.send_keys(termino)
        except TimeoutException:
            pass
        time.sleep(sleep_after_type)

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
            logger.info(f"[NC CONCEPTOS app-select] Opción seleccionada (JS): '{texto_opcion}'")
            return

        termino = texto_opcion.split(" - ")[0] if " - " in texto_opcion else texto_opcion
        fallback = (By.XPATH,
            f"//*[contains(normalize-space(.), '{termino}') and "
            f"not(self::input) and not(self::textarea) and not(self::button) and "
            f"not(self::nav) and not(self::header)]")
        try:
            opt = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(fallback))
            opt.click()
            logger.info(f"[NC CONCEPTOS app-select] Opción seleccionada (XPath): '{texto_opcion}'")
        except TimeoutException:
            raise TimeoutException(f"No se encontró opción '{texto_opcion}' en app-select del modal.")
        

    def click_facturar_cfdi(self) -> None:
        FACTURAR_CFDI_BTN = (By.CSS_SELECTOR, "button[data-testid='btn-facturar-cfdi']")
        logger.info("[NC CONCEPTOS] Haciendo scroll hacia el botón 'Facturar CFDI'...")
        
        # Esperar que el botón esté presente
        facturar_btn = self.wait_for_element(FACTURAR_CFDI_BTN, condition="visible", timeout=10)
        
        # Hacer scroll hacia el botón
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", facturar_btn)
        
        # Esperar que sea clickeable y hacer clic
        self.wait_for_element(FACTURAR_CFDI_BTN, condition="clickable", timeout=10)
        self.click(FACTURAR_CFDI_BTN)
        logger.info("[NC CONCEPTOS] Click en botón 'Facturar CFDI' ejecutado.")

    # ------------------------------------------------------------------
    # Acciones — Campos del modal
    # ------------------------------------------------------------------

    def fill_descripcion(self, descripcion: str) -> None:
        self.type_text(self.MODAL_DESCRIPCION, descripcion)
        logger.info(f"[NC CONCEPTOS] Descripción: {descripcion}")

    def fill_cantidad(self, cantidad: str) -> None:
        self.type_text(self.MODAL_CANTIDAD, cantidad)
        logger.info(f"[NC CONCEPTOS] Cantidad: {cantidad}")

    def fill_valor_unitario(self, valor: str) -> None:
        self.type_text(self.MODAL_VALOR_UNITARIO, valor)
        logger.info(f"[NC CONCEPTOS] Valor unitario: {valor}")

    def fill_clave_prod_serv(self, clave: str) -> None:
        self._click_app_select_async_option('claveProdServ', clave)
        logger.info(f"[NC CONCEPTOS] Clave prod/serv: {clave}")

    def fill_clave_unidad(self, clave_unidad: str) -> None:
        self._click_app_select_async_option('claveUnidad', clave_unidad)
        logger.info(f"[NC CONCEPTOS] Clave unidad: {clave_unidad}")

    def select_objeto_impuesto(self, valor: str) -> None:
        self.select_by_value(self.MODAL_OBJETO_IMPUESTO, valor)
        logger.info(f"[NC CONCEPTOS] Objeto de impuesto: {valor}")

    def fill_descuento(self, descuento: str) -> None:
        self.type_text(self.MODAL_DESCUENTO, descuento)
        logger.info(f"[NC CONCEPTOS] Descuento: {descuento}")

    def select_impuesto(self, impuesto: str) -> None:
        self._click_app_select_option(self.MODAL_IMPUESTO_TRIGGER, impuesto)
        logger.info(f"[NC CONCEPTOS] Impuesto: {impuesto}")

    def select_retencion_o_traslado(self, valor: str) -> None:
        from selenium.webdriver.support.ui import Select as _Select
        el = self.wait_for_element(self.MODAL_RETENCION_O_TRASLADO, condition="visible")
        sel = _Select(el)
        try:
            sel.select_by_value(valor)
        except Exception:
            for opt in sel.options:
                if opt.text.strip().lower() == valor.strip().lower():
                    opt.click()
                    break
        logger.info(f"[NC CONCEPTOS] Retención/Traslado: {valor}")

    def select_tipo_factor(self, valor: str) -> None:
        from selenium.webdriver.support.ui import Select as _Select
        el = self.wait_for_element(self.MODAL_TIPO_FACTOR, condition="visible")
        sel = _Select(el)
        try:
            sel.select_by_value(valor)
        except Exception:
            for opt in sel.options:
                if opt.text.strip().lower() == valor.strip().lower():
                    opt.click()
                    break
        logger.info(f"[NC CONCEPTOS] Tipo factor: {valor}")

    def fill_tasa_o_cuota(self, tasa: str) -> None:
        self.type_text(self.MODAL_TASA_O_CUOTA, tasa)
        logger.info(f"[NC CONCEPTOS] Tasa o cuota: {tasa}")

    def fill_no_identificacion(self, no_id: str) -> None:
        self.type_text(self.MODAL_NO_IDENTIFICACION, no_id)
        logger.info(f"[NC CONCEPTOS] No. Identificación: {no_id}")

    # ------------------------------------------------------------------
    # Helpers de validación
    # ------------------------------------------------------------------

    def _validar_campo_enviado(self, nombre: str, esperado: str, locator: tuple) -> None:
        try:
            el = self.wait_for_element(locator, condition="visible", timeout=3)
            actual_value = (el.get_attribute("value") or "").strip()
            actual_text  = (el.text or "").strip()
            actual = actual_value if actual_value else actual_text
            if esperado.strip() in actual or actual == esperado.strip():
                logger.info(f"[NC CONCEPTOS VALIDACIÓN] ✔ {nombre}: '{actual}'")
            else:
                logger.warning(f"[NC CONCEPTOS VALIDACIÓN] ✗ {nombre}: enviado='{esperado}' — campo='{actual}'")
        except Exception as exc:
            logger.warning(f"[NC CONCEPTOS VALIDACIÓN] No se pudo leer '{nombre}': {exc}")

    def _validar_select_enviado(self, nombre: str, esperado: str, locator: tuple) -> None:
        try:
            from selenium.webdriver.support.ui import Select as _Select
            el = self.wait_for_element(locator, condition="visible", timeout=3)
            sel = _Select(el)
            selected = sel.first_selected_option
            actual_text = selected.text.strip()
            actual_val  = (selected.get_attribute("value") or "").strip()
            if esperado.strip().lower() in (actual_text.lower(), actual_val.lower()):
                logger.info(f"[NC CONCEPTOS VALIDACIÓN] ✔ {nombre}: '{actual_text}'")
            else:
                logger.warning(f"[NC CONCEPTOS VALIDACIÓN] ✗ {nombre}: enviado='{esperado}' — seleccionado='{actual_text}'")
        except Exception as exc:
            logger.warning(f"[NC CONCEPTOS VALIDACIÓN] No se pudo leer '{nombre}': {exc}")

    def click_guardar_concepto(self) -> None:
        logger.info("[NC CONCEPTOS] Haciendo click en botón guardar concepto...")
        try:
            self.take_screenshot("nc_pre_guardar_concepto", directory=None)
        except Exception:
            pass
        self.wait_for_element(self.MODAL_BTN_GUARDAR, condition="clickable", timeout=10)
        self.click(self.MODAL_BTN_GUARDAR)
        logger.info("[NC CONCEPTOS] Click en botón guardar ejecutado.")

    # ------------------------------------------------------------------
    # Método de captura completa de un concepto
    # ------------------------------------------------------------------

    def agregar_concepto_completo(self, concepto: dict) -> None:
        descripcion = concepto.get("descripcion", "")
        logger.info(f"[NC CONCEPTOS] Iniciando captura de concepto: {descripcion!r}")

        count_antes = self.get_cantidad_conceptos()

        self.click_agregar_concepto()
        self._wait_for_modal_abierto(timeout=10)

        clave_unidad = concepto.get("unidad", "")
        if clave_unidad:
            self.fill_clave_unidad(clave_unidad)
            self._validar_campo_enviado("CLAVE UNIDAD", clave_unidad, self.MODAL_CLAVE_UNIDAD)
        else:
            logger.warning("[NC CONCEPTOS] CLAVE UNIDAD: vacío en Excel")

        cantidad = concepto.get("cantidad", "1")
        self.fill_cantidad(cantidad)
        self._validar_campo_enviado("CANTIDAD", cantidad, self.MODAL_CANTIDAD)

        no_id = concepto.get("no_identificacion", "")
        if no_id:
            self.fill_no_identificacion(no_id)
            self._validar_campo_enviado("NO. IDENTIFICACION", no_id, self.MODAL_NO_IDENTIFICACION)
        else:
            logger.warning("[NC CONCEPTOS] NO. IDENTIFICACION: vacío en Excel")

        clave_prod = concepto.get("clave_producto_servicio", "")
        if clave_prod:
            self.fill_clave_prod_serv(clave_prod)
            self._validar_campo_enviado("CLAVE PROD/SERV", clave_prod, self.MODAL_CLAVE_PROD_SERV)
        else:
            logger.warning("[NC CONCEPTOS] CLAVE PROD/SERV: vacío en Excel")

        self.fill_descripcion(descripcion)
        self._validar_campo_enviado("DESCRIPCION", descripcion, self.MODAL_DESCRIPCION)

        valor_unitario = concepto.get("valor_unitario", "0.00")
        self.fill_valor_unitario(valor_unitario)
        self._validar_campo_enviado("VALOR UNITARIO", valor_unitario, self.MODAL_VALOR_UNITARIO)

        descuento = concepto.get("descuento", "0.00")
        if descuento and descuento not in ("0.00", "0", ""):
            self.fill_descuento(descuento)
            self._validar_campo_enviado("DESCUENTO", descuento, self.MODAL_DESCUENTO)
        else:
            logger.info(f"[NC CONCEPTOS] DESCUENTO: {descuento!r} — sin descuento, campo no modificado")

        objeto_imp = concepto.get("objeto_impuesto", "")
        if objeto_imp:
            self.select_objeto_impuesto(objeto_imp)
            self._validar_select_enviado("OBJETO IMPUESTO", objeto_imp, self.MODAL_OBJETO_IMPUESTO)
        else:
            logger.warning("[NC CONCEPTOS] OBJETO IMPUESTO: vacío en Excel")

        impuesto = concepto.get("impuesto", "")
        if impuesto:
            self.select_impuesto(impuesto)
            self._validar_campo_enviado("IMPUESTO", impuesto, self.MODAL_IMPUESTO_TRIGGER)
        else:
            logger.warning("[NC CONCEPTOS] IMPUESTO: vacío en Excel")

        ret_tras = concepto.get("ret_tras", "")
        if ret_tras:
            self.select_retencion_o_traslado(ret_tras)
            self._validar_select_enviado("RET/TRAS", ret_tras, self.MODAL_RETENCION_O_TRASLADO)
        else:
            logger.warning("[NC CONCEPTOS] RET/TRAS: vacío en Excel")

        tipo_factor = concepto.get("tipo_factor", "")
        if tipo_factor:
            self.select_tipo_factor(tipo_factor)
            self._validar_select_enviado("TIPO FACTOR", tipo_factor, self.MODAL_TIPO_FACTOR)
        else:
            logger.warning("[NC CONCEPTOS] TIPO FACTOR: vacío en Excel")

        tasa_o_cuota = concepto.get("tasa_o_cuota", "")
        if tasa_o_cuota:
            self.fill_tasa_o_cuota(tasa_o_cuota)
            self._validar_campo_enviado("TASA O CUOTA", tasa_o_cuota, self.MODAL_TASA_O_CUOTA)
        else:
            logger.warning("[NC CONCEPTOS] TASA O CUOTA: vacío en Excel")

        if self.is_visible(self.MODAL_BTN_AGREGAR_IMPUESTO, timeout=5):
            self.wait_for_element(self.MODAL_BTN_AGREGAR_IMPUESTO, condition="clickable", timeout=8)
            self.click(self.MODAL_BTN_AGREGAR_IMPUESTO)
            logger.info("[NC CONCEPTOS] Click en 'Agregar Impuesto' ejecutado.")
            self.pause(5)  # Esperar que se procese el agregado del impuesto antes de guardar el concepto
        else:
            logger.warning("[NC CONCEPTOS] Botón 'Agregar Impuesto' no encontrado.")

        self.click_guardar_concepto()
        self._wait_for_modal_cerrado(timeout=2)
        self.wait_for_nuevo_concepto_guardado(count_antes, timeout=2)
        logger.info(f"[NC CONCEPTOS] Concepto agregado exitosamente: {descripcion!r}")


    def agregar_concepto_desde_caso(self, caso: dict) -> None:
        concepto = {
            "descripcion":             str(caso.get("descripcion_concepto",  "")).strip(),
            "cantidad":                str(caso.get("cantidad",              "1")).strip(),
            "no_identificacion":       str(caso.get("no_identificacion",     "")).strip(),
            "unidad":                  str(caso.get("clave_unidad",          "")).strip(),
            "clave_producto_servicio": str(caso.get("clave_prod_serv",       "")).strip(),
            "valor_unitario":          str(caso.get("valor_unitario",        "0.00")).strip(),
            "descuento":               str(caso.get("descuento",             "0.00")).strip(),
            "objeto_impuesto":         str(caso.get("objeto_impuesto",       "02")).strip(),
            "impuesto":                str(caso.get("impuesto",              "")).strip(),
            "ret_tras":                str(caso.get("ret_tras",              "")).strip(),
            "tipo_factor":             str(caso.get("tipo_factor",           "")).strip(),
            "tasa_o_cuota":            str(caso.get("tasa_o_cuota",          "")).strip(),
        }
        self.agregar_concepto_completo(concepto)
