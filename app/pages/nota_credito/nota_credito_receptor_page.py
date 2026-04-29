"""
nota_credito_receptor_page.py - Page Object de la sección Receptor del formulario de Nota de Crédito.

Réplica exacta de FacturaReceptorPage pero aislada en el módulo de Nota de Crédito.
Componente HTML: <app-receptor-factura>
"""
from selenium.webdriver.common.by import By

from app.core.base_page import BasePage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NotaCreditoReceptorPage(BasePage):
    """
    Page Object para la sección del Receptor en el formulario de Nota de Crédito.

    Componente Angular: <app-receptor-factura>
    """

    RFC_RECEPTOR = (
        By.CSS_SELECTOR,
        "[data-testid='input-rfc-receptor'], "
        "app-receptor-factura input[placeholder='ABC010101XXX']",
    )

    BTN_BUSCAR_RFC = (
        By.CSS_SELECTOR,
        "[data-testid='btn-buscar-rfc'], "
        "app-receptor-factura button[type='button']",
    )

    RAZON_SOCIAL = (
        By.CSS_SELECTOR,
        "[data-testid='input-razon-social'], "
        "app-receptor-factura input[placeholder='NOMBRE O DENOMINACIÓN SOCIAL']",
    )

    CODIGO_POSTAL = (
        By.CSS_SELECTOR,
        "[data-testid='input-cp-receptor'], "
        "app-receptor-factura input[placeholder='00000']",
    )

    REGIMEN_FISCAL = (
        By.XPATH,
        "//app-receptor-factura//label[contains(., 'Régimen Fiscal')]"
        "/following::select[1]",
    )

    USO_CFDI = (
        By.XPATH,
        "//app-receptor-factura//label[contains(., 'Uso de CFDI')]"
        "/following::select[1]",
    )

    EMAIL = (
        By.CSS_SELECTOR,
        "[data-testid='input-email-receptor'], "
        "app-receptor-factura input[type='email']",
    )

    TOGGLE_DOMICILIO = (
        By.CSS_SELECTOR,
        "[data-testid='toggle-domicilio-fiscal'], "
        "app-receptor-factura button[role='switch']",
    )

    # ------------------------------------------------------------------
    # Validaciones
    # ------------------------------------------------------------------

    def is_section_loaded(self) -> bool:
        return self.is_visible((By.CSS_SELECTOR, "app-receptor-factura"), timeout=10)

    # ------------------------------------------------------------------
    # Acciones — RFC
    # ------------------------------------------------------------------

    def fill_rfc(self, rfc: str) -> None:
        self.type_text(self.RFC_RECEPTOR, rfc.upper())
        logger.info(f"[NC RECEPTOR] RFC ingresado: {rfc.upper()}")

    def click_buscar_rfc(self) -> None:
        self.click(self.BTN_BUSCAR_RFC)
        logger.info("[NC RECEPTOR] Click en botón de búsqueda RFC.")

    def fill_rfc_y_buscar(self, rfc: str) -> None:
        self.fill_rfc(rfc)
        self.click_buscar_rfc()
        logger.info(f"[NC RECEPTOR] RFC ingresado y búsqueda ejecutada: {rfc}")

    def fill_razon_social(self, nombre: str) -> None:
        import time as _time
        target = nombre.upper()
        element = self.wait_for_element(self.RAZON_SOCIAL, condition="visible", timeout=10)
        element.clear()
        element.send_keys(target)
        _time.sleep(0.6)  # dar tiempo al portal para que el RFC lookup sobreescriba (si aplica)
        actual = (element.get_attribute("value") or "").strip()
        if actual.upper() != target:
            logger.debug(f"[NC RECEPTOR] Razón social sobreescrita por portal ('{actual}'), forzando via JS...")
            self.driver.execute_script(
                """const niv = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
                   niv.call(arguments[0], arguments[1]);
                   arguments[0].dispatchEvent(new Event('input', {bubbles:true}));
                   arguments[0].dispatchEvent(new Event('change', {bubbles:true}));""",
                element, target
            )
        logger.info(f"[NC RECEPTOR] Razón social ingresada: {target}")

    def fill_codigo_postal(self, cp: str) -> None:
        from selenium.webdriver.common.keys import Keys
        import time as _time
        element = self.wait_for_element(self.CODIGO_POSTAL, condition="visible", timeout=10)
        element.clear()
        element.send_keys(cp)
        # Angular necesita blur/change para poblar el select de régimen fiscal
        element.send_keys(Keys.TAB)
        # Disparar eventos Angular via JS por si el TAB no alcanza
        self.driver.execute_script(
            "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));"
            "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));"
            "arguments[0].dispatchEvent(new Event('blur', {bubbles:true}));",
            element,
        )
        _time.sleep(0.5)
        logger.info(f"[NC RECEPTOR] Código postal ingresado: {cp}")

    # ------------------------------------------------------------------
    # Acciones — Selects con retry y StaleElement handling
    # ------------------------------------------------------------------

    def _select_by_codigo(self, locator, codigo: str, campo: str) -> None:
        """Helper: select_by_value con fallback flexible + espera activa a que carguen opciones."""
        import time as _time
        from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
        from selenium.webdriver.support.ui import Select as _Select
        for intento in range(3):
            try:
                element = self.wait_for_element(locator, condition="visible", timeout=15)
                sel = _Select(element)
                # Espera activa: hasta 20s a que el <select> tenga más de 1 opción
                _deadline = _time.monotonic() + 20
                while len(sel.options) <= 1 and _time.monotonic() < _deadline:
                    _time.sleep(0.5)
                    element = self.wait_for_element(locator, condition="visible", timeout=10)
                    sel = _Select(element)
                try:
                    sel.select_by_value(codigo)
                    return
                except NoSuchElementException:
                    pass
                for opt in sel.options:
                    texto = opt.text.strip()
                    if texto.startswith(codigo) or f" {codigo} " in texto or texto == codigo:
                        opt.click()
                        return
                for opt in sel.options:
                    if codigo in opt.text:
                        opt.click()
                        return
                raise NoSuchElementException(
                    f"No se encontró opción con código '{codigo}' en {campo}. "
                    f"Opciones disponibles: {[o.text for o in sel.options[:10]]}"
                )
            except StaleElementReferenceException:
                if intento == 2:
                    raise
                _time.sleep(0.5)

    def select_regimen_fiscal_by_value(self, codigo: str) -> None:
        self._select_by_codigo(self.REGIMEN_FISCAL, codigo, "régimen fiscal")
        logger.info(f"[NC RECEPTOR] Régimen fiscal seleccionado: {codigo}")

    def select_uso_cfdi_by_value(self, codigo: str) -> None:
        self._select_by_codigo(self.USO_CFDI, codigo, "uso CFDI")
        logger.info(f"[NC RECEPTOR] Uso de CFDI seleccionado: {codigo}")

    def fill_email(self, email: str) -> None:
        self.type_text(self.EMAIL, email)
        logger.info(f"[NC RECEPTOR] Email ingresado: {email}")

    def fill_receptor_completo(
        self,
        rfc: str,
        razon_social: str,
        codigo_postal: str,
        regimen_fiscal: str,
        uso_cfdi: str,
        email: str = "",
        buscar_rfc: bool = True,
    ) -> None:
        logger.info(f"[NC RECEPTOR] Iniciando llenado completo — RFC: {rfc}")
        self.fill_rfc(rfc)
        if buscar_rfc:
            self.click_buscar_rfc()
        self.fill_razon_social(razon_social)
        self.fill_codigo_postal(codigo_postal)
        self.select_regimen_fiscal_by_value(regimen_fiscal)
        self.select_uso_cfdi_by_value(uso_cfdi)
        if email:
            self.fill_email(email)
        logger.info(f"[NC RECEPTOR] Sección Receptor completada para RFC: {rfc}")

    # ------------------------------------------------------------------
    # Alias de métodos (compatibilidad con Flow)
    # ------------------------------------------------------------------

    def capturar_rfc_receptor(self, rfc: str) -> None:
        self.fill_rfc(rfc)

    def capturar_razon_social(self, razon_social: str) -> None:
        self.fill_razon_social(razon_social)

    def capturar_codigo_postal(self, cp: str) -> None:
        self.fill_codigo_postal(cp)

    def seleccionar_regimen_fiscal_receptor(self, valor: str) -> None:
        if not valor or not valor.strip():
            return
        codigo = valor.split(" - ")[0].strip() if " - " in valor else valor.strip()
        self.select_regimen_fiscal_by_value(codigo)

    def seleccionar_uso_cfdi(self, valor: str) -> None:
        if not valor or not valor.strip():
            return
        codigo = valor.split(" - ")[0].strip() if " - " in valor else valor.strip()
        self.select_uso_cfdi_by_value(codigo)

    def capturar_email(self, email: str) -> None:
        if email:
            self.fill_email(email)

    # ------------------------------------------------------------------
    # Domicilio Fiscal (opcional)
    # ------------------------------------------------------------------

    def activar_domicilio_fiscal_si_aplica(self, datos: dict) -> bool:
        campos_domicilio = ["calle", "num_exterior", "num_interior", "colonia", "municipio", "estado"]
        tiene_domicilio = any(str(datos.get(campo, "")).strip() for campo in campos_domicilio)
        if not tiene_domicilio:
            # El switch puede haberse activado solo (ej: auto-fill del portal tras buscar RFC).
            # Si está activo sin datos de domicilio, hay que DESACTIVARLO o el portal bloqueará el timbrado.
            try:
                switch = self.wait_for_element(self.TOGGLE_DOMICILIO, condition="visible", timeout=5)
                aria_checked = switch.get_attribute("aria-checked")
                if aria_checked == "true":
                    switch.click()
                    logger.info("[NC RECEPTOR] Switch 'Agregar Domicilio Fiscal' DESACTIVADO (se activó sin datos).")
                else:
                    logger.info("[NC RECEPTOR] Sin datos de domicilio fiscal — switch ya inactivo.")
            except Exception as exc:
                logger.debug(f"[NC RECEPTOR] No se pudo verificar switch domicilio: {exc}")
            return False
        try:
            switch = self.wait_for_element(self.TOGGLE_DOMICILIO, condition="clickable", timeout=10)
            aria_checked = switch.get_attribute("aria-checked")
            if aria_checked != "true":
                switch.click()
                logger.info("[NC RECEPTOR] Switch 'Agregar Domicilio Fiscal' activado.")
            else:
                logger.info("[NC RECEPTOR] Switch de domicilio fiscal ya estaba activo.")
            return True
        except Exception as exc:
            logger.warning(f"[NC RECEPTOR] No se pudo activar domicilio fiscal: {exc}")
            return False

    def capturar_domicilio_fiscal(self, datos: dict) -> None:
        _CAMPO_MAP = {
            "calle":        (By.CSS_SELECTOR, "[data-testid='input-calle'], input[formcontrolname='calle'], input[placeholder*='alle']"),
            "num_exterior": (By.CSS_SELECTOR, "[data-testid='input-num-exterior'], input[formcontrolname='numExt'], input[formcontrolname='numExterior']"),
            "num_interior": (By.CSS_SELECTOR, "[data-testid='input-num-interior'], input[formcontrolname='numInt'], input[formcontrolname='numInterior']"),
            "colonia":      (By.CSS_SELECTOR, "[data-testid='input-colonia'], input[formcontrolname='colonia']"),
            "municipio":    (By.CSS_SELECTOR, "[data-testid='input-municipio'], input[formcontrolname='municipio']"),
            "estado":       (By.CSS_SELECTOR, "[data-testid='input-estado'], input[formcontrolname='estado']"),
        }
        for campo, locator in _CAMPO_MAP.items():
            valor = str(datos.get(campo, "")).strip()
            if not valor:
                continue
            try:
                self.type_text(locator, valor, clear_first=True)
                logger.info(f"[NC RECEPTOR][DOMICILIO] {campo} = '{valor}'")
            except Exception as exc:
                logger.warning(f"[NC RECEPTOR][DOMICILIO] No se pudo capturar {campo}: {exc}")
