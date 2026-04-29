"""
nota_credito_configuracion_page.py - Page Object del drawer "Personalizar" de Nota de Crédito.

Componente HTML: <app-drawer-config-invoice>
Accesible mediante el botón "PERSONALIZAR" en la barra lateral izquierda del formulario.

Estructura del drawer:
  ┌─────────────────────────────┬──────────────┐
  │  Contenido de la sección    │   Nav tabs   │
  │  (Inf. Adicional activo)    │ > Inf. Adic. │
  │  · CFDI Relacionado [toggle]│   Complement.│
  │  · Información Global [tog.]│   Addendas   │
  └─────────────────────────────┴──────────────┘
  [X] botón cerrar (esquina superior)

Uso típico:
    config_page = NotaCreditoConfiguracionPage(driver)
    config_page.configurar_cfdi_relacionado()
"""
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.core.base_page import BasePage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NotaCreditoConfiguracionPage(BasePage):
    """
    Page Object para el drawer de configuración 'Personalizar' de Nota de Crédito.

    Contiene todos los selectores y acciones del panel lateral app-drawer-config-invoice.
    """

    # ------------------------------------------------------------------
    # Botón lateral para abrir el drawer
    # CSS del portal: body > ... > app-nota-credito > app-drawer-config-invoice > button
    # ------------------------------------------------------------------
    BTN_PERSONALIZAR = (
        By.CSS_SELECTOR,
        "app-nota-credito app-drawer-config-invoice > button, "
        "app-drawer-config-invoice > button",
    )

    # ------------------------------------------------------------------
    # Panel / contenedor del drawer (visible cuando está abierto)
    # ------------------------------------------------------------------
    DRAWER_PANEL = (
        By.CSS_SELECTOR,
        "app-drawer-config-invoice > div",
    )

    # ------------------------------------------------------------------
    # Botón cerrar (✕) — esquina superior del drawer
    # CSS del portal: app-drawer-config-invoice > div > div.shrink-0 > button > span
    # Se hace click en el <button> padre, no en el <span> del ícono
    # ------------------------------------------------------------------
    BTN_CERRAR_DRAWER = (
        By.CSS_SELECTOR,
        "app-drawer-config-invoice > div > div.shrink-0 > button, "
        "app-drawer-config-invoice div.shrink-0.border-b > button",
    )

    # ------------------------------------------------------------------
    # Tabs de navegación del drawer (columna derecha)
    # ------------------------------------------------------------------
    TAB_INF_ADICIONAL = (
        By.XPATH,
        "//app-drawer-config-invoice//button[contains(normalize-space(.), 'Inf. Adicional')]",
    )
    TAB_COMPLEMENTOS = (
        By.XPATH,
        "//app-drawer-config-invoice//button[contains(normalize-space(.), 'Complementos')]",
    )
    TAB_ADDENDAS = (
        By.XPATH,
        "//app-drawer-config-invoice//button[contains(normalize-space(.), 'Addendas')]",
    )

    # ------------------------------------------------------------------
    # Toggles — sección "Información Adicional"
    # Cada toggle es un <button role="switch" aria-checked="true|false">
    # ------------------------------------------------------------------

    # CFDI Relacionado — habilita el bloque de UUID/tipo de relación en el formulario
    TOGGLE_CFDI_RELACIONADO = (
        By.XPATH,
        "//app-drawer-config-invoice"
        "//p[contains(normalize-space(.), 'CFDI Relacionado')]"
        "/ancestor::div[contains(@class,'justify-between')]"
        "//button[@role='switch']",
    )

    # Información Global — habilita la sección de datos globales
    TOGGLE_INFORMACION_GLOBAL = (
        By.XPATH,
        "//app-drawer-config-invoice"
        "//p[contains(normalize-space(.), 'Información Global')]"
        "/ancestor::div[contains(@class,'justify-between')]"
        "//button[@role='switch']",
    )

    # ------------------------------------------------------------------
    # Sección CFDI Relacionado — formulario en la página principal
    # Aparece al habilitar el toggle CFDI Relacionado y cerrar el drawer.
    # ------------------------------------------------------------------

    # Acordeón <details>/<summary> — hay que hacer click para expandirlo
    # Selector exacto del portal:
    # body > app-root > ... > app-nota-credito > div > div.flex... > app-comprobante-factura
    #   > div > app-cfdi-relacionado > details > summary
    CFDI_RELACIONADO_SUMMARY = (
        By.CSS_SELECTOR,
        "app-cfdi-relacionado > details > summary, "
        "app-cfdi-relacionado details > summary",
    )

    # Dropdown <app-select> de Tipo de Relación — scoped a app-cfdi-relacionado
    # El select usa formControlName='tipoRelacion', NO tiene atributo placeholder.
    APP_SELECT_TIPO_RELACION = (
        By.CSS_SELECTOR,
        "app-cfdi-relacionado select[formcontrolname='tipoRelacion'], "
        "app-cfdi-relacionado select[ng-reflect-name='tipoRelacion']",
    )
    # Fallback XPATH también scoped a app-cfdi-relacionado
    APP_SELECT_TIPO_RELACION_XPATH = (
        By.XPATH,
        "//app-cfdi-relacionado//select[@formcontrolname='tipoRelacion'] "
        "| //app-cfdi-relacionado//select",
    )

    # Input para UUID del CFDI relacionado
    # Locator amplio: primer input de texto visible dentro del acordeón de CFDI Relacionado
    INPUT_UUID_RELACIONADO = (
        By.CSS_SELECTOR,
        "app-cfdi-relacionado details input[type='text'], "
        "app-cfdi-relacionado details input:not([type='hidden']):not([type='checkbox']):not([type='radio'])",
    )

    # Botón "Agregar UUID"
    BTN_AGREGAR_UUID = (
        By.XPATH,
        "//app-nota-credito//button[contains(normalize-space(.), 'Agregar UUID') "
        "or contains(normalize-space(.), 'Agregar') and contains(normalize-space(.), 'UUID')]",
    )

    # ------------------------------------------------------------------
    # Helpers de estado
    # ------------------------------------------------------------------

    def is_drawer_abierto(self) -> bool:
        return self.is_visible(self.DRAWER_PANEL, timeout=3)

    def _toggle_is_activo(self, locator: tuple) -> bool:
        try:
            el = self.wait_for_element(locator, condition="visible", timeout=5)
            return el.get_attribute("aria-checked") == "true"
        except Exception:
            return False

    def is_cfdi_relacionado_activo(self) -> bool:
        return self._toggle_is_activo(self.TOGGLE_CFDI_RELACIONADO)

    def is_informacion_global_activo(self) -> bool:
        return self._toggle_is_activo(self.TOGGLE_INFORMACION_GLOBAL)

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def abrir_personalizar(self) -> None:
        """Hace click en el botón lateral 'PERSONALIZAR' y espera que el drawer abra."""
        self.wait_for_element(self.BTN_PERSONALIZAR, condition="clickable", timeout=10)
        self.click(self.BTN_PERSONALIZAR)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.DRAWER_PANEL)
            )
        except TimeoutException:
            raise TimeoutException(
                "[NC CONFIG] El drawer 'Personalizar' no se abrió tras hacer click en el botón."
            )
        logger.info("[NC CONFIG] Drawer 'Personalizar' abierto.")

    def click_tab_inf_adicional(self) -> None:
        """Selecciona la pestaña 'Inf. Adicional' en el nav del drawer."""
        self.wait_for_element(self.TAB_INF_ADICIONAL, condition="clickable", timeout=8)
        self.click(self.TAB_INF_ADICIONAL)
        time.sleep(0.3)
        logger.info("[NC CONFIG] Tab 'Inf. Adicional' seleccionado.")

    def click_tab_complementos(self) -> None:
        """Selecciona la pestaña 'Complementos' en el nav del drawer."""
        self.wait_for_element(self.TAB_COMPLEMENTOS, condition="clickable", timeout=8)
        self.click(self.TAB_COMPLEMENTOS)
        time.sleep(0.3)
        logger.info("[NC CONFIG] Tab 'Complementos' seleccionado.")

    def click_tab_addendas(self) -> None:
        """Selecciona la pestaña 'Addendas' en el nav del drawer."""
        self.wait_for_element(self.TAB_ADDENDAS, condition="clickable", timeout=8)
        self.click(self.TAB_ADDENDAS)
        time.sleep(0.3)
        logger.info("[NC CONFIG] Tab 'Addendas' seleccionado.")

    def activar_cfdi_relacionado(self) -> None:
        """Activa el toggle 'CFDI Relacionado' si no estaba activo ya."""
        el = self.wait_for_element(self.TOGGLE_CFDI_RELACIONADO, condition="clickable", timeout=8)
        if el.get_attribute("aria-checked") != "true":
            el.click()
            time.sleep(0.4)
            logger.info("[NC CONFIG] Toggle 'CFDI Relacionado' activado.")
        else:
            logger.info("[NC CONFIG] Toggle 'CFDI Relacionado' ya estaba activo.")

    def desactivar_cfdi_relacionado(self) -> None:
        """Desactiva el toggle 'CFDI Relacionado' si estaba activo."""
        el = self.wait_for_element(self.TOGGLE_CFDI_RELACIONADO, condition="clickable", timeout=8)
        if el.get_attribute("aria-checked") == "true":
            el.click()
            time.sleep(0.4)
            logger.info("[NC CONFIG] Toggle 'CFDI Relacionado' desactivado.")

    def activar_informacion_global(self) -> None:
        """Activa el toggle 'Información Global' si no estaba activo ya."""
        el = self.wait_for_element(self.TOGGLE_INFORMACION_GLOBAL, condition="clickable", timeout=8)
        if el.get_attribute("aria-checked") != "true":
            el.click()
            time.sleep(0.4)
            logger.info("[NC CONFIG] Toggle 'Información Global' activado.")
        else:
            logger.info("[NC CONFIG] Toggle 'Información Global' ya estaba activo.")

    def cerrar_drawer(self) -> None:
        """Hace click en el botón ✕ y espera que el drawer se cierre."""
        self.wait_for_element(self.BTN_CERRAR_DRAWER, condition="clickable", timeout=8)
        self.click(self.BTN_CERRAR_DRAWER)
        try:
            WebDriverWait(self.driver, 8).until(
                EC.invisibility_of_element_located(self.DRAWER_PANEL)
            )
        except TimeoutException:
            logger.warning("[NC CONFIG] El drawer no desapareció tras click en cerrar.")
        logger.info("[NC CONFIG] Drawer 'Personalizar' cerrado.")

    # ------------------------------------------------------------------
    # Método combinado: abrir → Inf. Adicional → activar toggle → cerrar
    # ------------------------------------------------------------------

    def configurar_cfdi_relacionado(self) -> None:
        """
        Flujo completo para habilitar CFDI Relacionado desde el drawer:
          1. Abre el drawer 'Personalizar'
          2. Selecciona tab 'Inf. Adicional'
          3. Activa el toggle 'CFDI Relacionado'
          4. Cierra el drawer
        """
        self.abrir_personalizar()
        self.click_tab_inf_adicional()
        self.activar_cfdi_relacionado()
        self.cerrar_drawer()
        logger.info("[NC CONFIG] CFDI Relacionado habilitado y drawer cerrado.")

    # ------------------------------------------------------------------
    # Formulario CFDI Relacionado (página principal, fuera del drawer)
    # ------------------------------------------------------------------

    def _select_tipo_relacion(self, tipo_relacion: str) -> None:
        """
        Selecciona el Tipo de Relación.
        Estrategia dual: intenta primero <select> nativo (Selenium Select),
        luego <app-select> Angular (click trigger + buscar opción en overlay).
        """
        from selenium.webdriver.support.ui import Select as SeleniumSelect
        from selenium.webdriver.common.action_chains import ActionChains

        termino = tipo_relacion.split(" - ")[0] if " - " in tipo_relacion else tipo_relacion

        # ── Estrategia 1: <select> nativo ─────────────────────────────
        _NATIVE_LOCATORS = [
            (By.CSS_SELECTOR, "app-cfdi-relacionado select[formcontrolname='tipoRelacion']"),
            (By.CSS_SELECTOR, "app-cfdi-relacionado select[ng-reflect-name='tipoRelacion']"),
            (By.XPATH,        "//app-cfdi-relacionado//select[@formcontrolname='tipoRelacion']"),
            (By.XPATH,        "//app-cfdi-relacionado//select"),
        ]
        for locator in _NATIVE_LOCATORS:
            try:
                el = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located(locator)
                )
                if el.tag_name.lower() == "select":
                    sel = SeleniumSelect(el)
                    try:
                        sel.select_by_visible_text(tipo_relacion)
                    except Exception:
                        # Intentar sólo con el código ("01")
                        try:
                            sel.select_by_value(termino)
                        except Exception:
                            sel.select_by_visible_text(termino)
                    logger.info(
                        f"[NC CONFIG] Tipo de Relación seleccionado (native select): '{tipo_relacion}'"
                    )
                    return
            except TimeoutException:
                continue
            except Exception:
                continue

        # ── Estrategia 2: <app-select> Angular custom ──────────────────
        _APP_SELECT_LOCATORS = [
            (By.CSS_SELECTOR, "app-cfdi-relacionado app-select[formcontrolname='tipoRelacion'] > div"),
            (By.CSS_SELECTOR, "app-cfdi-relacionado app-select[ng-reflect-name='tipoRelacion'] > div"),
            (By.XPATH,        "//app-cfdi-relacionado//app-select[@formcontrolname='tipoRelacion']//div"),
            (By.XPATH,        "//app-cfdi-relacionado//app-select//div"),
        ]
        trigger = None
        for locator in _APP_SELECT_LOCATORS:
            try:
                trigger = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable(locator)
                )
                break
            except TimeoutException:
                continue

        if trigger is not None:
            try:
                trigger.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", trigger)
            time.sleep(0.5)

            _js_find = """
                const target = arguments[0];
                const container = document.querySelector('app-cfdi-relacionado') || document.body;
                const all = container.querySelectorAll('*');
                for (const el of all) {
                    const rect = el.getBoundingClientRect();
                    if (rect.width === 0 || rect.height === 0) continue;
                    const t = (el.textContent || '').trim();
                    if (t === target && el.children.length === 0) return el;
                }
                for (const el of all) {
                    const rect = el.getBoundingClientRect();
                    if (rect.width === 0 || rect.height === 0) continue;
                    const t = (el.textContent || '').trim();
                    if (t.includes(target) && el.children.length <= 2) return el;
                }
                return null;
            """
            option_el = self.driver.execute_script(_js_find, tipo_relacion)
            if option_el is None:
                option_el = self.driver.execute_script(_js_find, termino)

            if option_el:
                try:
                    ActionChains(self.driver).move_to_element(option_el).click().perform()
                except Exception:
                    try:
                        option_el.click()
                    except Exception:
                        self.driver.execute_script("arguments[0].click();", option_el)
                logger.info(
                    f"[NC CONFIG] Tipo de Relación seleccionado (app-select): '{tipo_relacion}'"
                )
                self._esperar_cierre_overlay()
                return

        raise TimeoutException(
            f"[NC CONFIG] No se encontró el control Tipo de Relación dentro de "
            f"app-cfdi-relacionado (probados: select nativo y app-select Angular). "
            f"Verifica que el acordeón esté expandido y el campo sea visible."
        )

    def _esperar_cierre_overlay(self, timeout: int = 5) -> None:
        """
        Espera a que el overlay CDK de app-select desaparezca.
        Usa ActionChains para enviar eventos nativos reales que CDK responde correctamente.
        """
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.common.keys import Keys
        overlay_locator = (By.CSS_SELECTOR, "div.cdk-overlay-backdrop.select-overlay-backdrop")
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(overlay_locator)
            )
            return
        except TimeoutException:
            pass

        # Cerrar con ActionChains click en el backdrop — eventos nativos que CDK sí responde
        try:
            backdrop = self.driver.find_element(*overlay_locator)
            ActionChains(self.driver).move_to_element(backdrop).click().perform()
            time.sleep(0.4)
        except Exception:
            pass

        # Verificar si ya se cerró
        try:
            WebDriverWait(self.driver, 2).until(
                EC.invisibility_of_element_located(overlay_locator)
            )
            logger.warning("[NC CONFIG] Overlay app-select cerrado via ActionChains click en backdrop.")
            return
        except TimeoutException:
            pass

        # Último recurso: ActionChains Escape
        try:
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        except Exception:
            pass
        time.sleep(0.4)
        logger.warning("[NC CONFIG] Overlay app-select cerrado con ActionChains+Escape (último recurso).")

    def abrir_seccion_cfdi_relacionado(self) -> None:
        """
        Expande el acordeón <details>/<summary> de CFDI Relacionado en la página principal.
        Solo hace click si <details> no está ya abierto (sin atributo 'open').
        """
        try:
            summary = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.CFDI_RELACIONADO_SUMMARY)
            )
        except TimeoutException:
            raise TimeoutException(
                "[NC CONFIG] No se encontró el acordeón CFDI Relacionado en la página. "
                "Verifica que el toggle fue activado y el drawer fue cerrado."
            )

        # Verificar si el <details> padre ya está abierto
        details_el = self.driver.execute_script(
            "return arguments[0].closest('details');", summary
        )
        is_open = self.driver.execute_script(
            "return arguments[0].hasAttribute('open');", details_el
        ) if details_el else False

        if not is_open:
            try:
                summary.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", summary)
            time.sleep(0.4)
            logger.info("[NC CONFIG] Acordeón CFDI Relacionado expandido.")
        else:
            logger.info("[NC CONFIG] Acordeón CFDI Relacionado ya estaba abierto.")

    def fill_cfdi_relacionado(self, tipo_relacion: str, uuid: str) -> None:
        """
        Llena el formulario CFDI Relacionado en la página principal:
          1. Expande el acordeón <details>/<summary>
          2. Selecciona Tipo de Relación
          3. Ingresa el UUID del CFDI relacionado
          4. Hace click en 'Agregar UUID'

        Args:
            tipo_relacion: Texto de la opción a seleccionar (ej. "01 - Nota de crédito...").
            uuid:          UUID del CFDI relacionado a agregar.
        """
        logger.info(f"[NC CONFIG] Llenando CFDI Relacionado: tipo='{tipo_relacion}', uuid='{uuid}'")

        # Paso 1: Abrir el acordeón
        self.abrir_seccion_cfdi_relacionado()

        if tipo_relacion:
            self._select_tipo_relacion(tipo_relacion)
            time.sleep(0.3)
            logger.info(f"[NC CONFIG] Tipo de Relación capturado: '{tipo_relacion}'")

        if uuid:
            # Asegurar que no haya ningún overlay CDK abierto antes de escribir el UUID
            self._esperar_cierre_overlay(timeout=3)
            input_el = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(self.INPUT_UUID_RELACIONADO)
            )
            input_el.clear()
            input_el.send_keys(uuid)
            time.sleep(0.2)
            logger.info(f"[NC CONFIG] UUID relacionado ingresado: '{uuid}'")

            btn_agregar = WebDriverWait(self.driver, 8).until(
                EC.element_to_be_clickable(self.BTN_AGREGAR_UUID)
            )
            btn_agregar.click()
            time.sleep(0.5)
            logger.info("[NC CONFIG] Click en 'Agregar UUID' realizado.")

        logger.info("[NC CONFIG] Formulario CFDI Relacionado completado.")
