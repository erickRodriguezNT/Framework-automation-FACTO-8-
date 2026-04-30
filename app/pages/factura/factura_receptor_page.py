"""
factura_receptor_page.py - Page Object de la sección "Datos del Receptor" del formulario de Factura.

Componente HTML: <app-receptor-factura>

============================================================
ANÁLISIS DE SELECTORES — app-receptor-factura (HTML analizado)
============================================================

HTML OBSERVADO (extracto relevante):
  <app-receptor-factura>
    <!-- RFC Receptor -->
    <input type="text" placeholder="ABC010101XXX" ng-reflect-form="[object Object]">
    <button type="button"> <!-- Botón de búsqueda RFC -->

    <!-- Razón Social -->
    <input type="text" placeholder="NOMBRE O DENOMINACIÓN SOCIAL" ng-reflect-form="[object Object]">

    <!-- Código Postal -->
    <input type="text" placeholder="00000" ng-reflect-form="[object Object]">

    <!-- Régimen Fiscal Receptor -->
    <select ng-reflect-form="[object Object]">
      <option>601 - General de Ley Personas Morales</option>
      ...
    </select>

    <!-- Uso de CFDI -->
    <select ng-reflect-form="[object Object]">
      <option>G01 - Adquisición de mercancias</option>
      ...
    </select>

    <!-- Email -->
    <input type="email" placeholder="cliente@ejemplo.com" ng-reflect-form="[object Object]">
  </app-receptor-factura>

SELECTORES USADOS:
  - Placeholder para inputs (MEDIUM): depende de que no cambien los textos
  - type="email" para el correo (HIGH): único por tipo en el componente
  - select:nth-of-type para los selects (LOW): positional, frágil si se agregan más selects

SELECTORES RIESGOSOS:
  ⚠️  app-receptor-factura select:nth-of-type(1/2): dependen de la posición DOM
      Si el frontend agrega otro select antes, estos se rompen.

DATA-TESTID RECOMENDADOS AL EQUIPO FRONTEND:
  - data-testid="input-rfc-receptor"             → campo RFC Receptor
  - data-testid="btn-buscar-rfc"                 → botón búsqueda RFC
  - data-testid="input-razon-social"             → campo Razón Social
  - data-testid="input-cp-receptor"              → campo Código Postal
  - data-testid="select-regimen-fiscal-receptor" → dropdown Régimen Fiscal
  - data-testid="select-uso-cfdi"               → dropdown Uso de CFDI
  - data-testid="input-email-receptor"          → campo Email
  - data-testid="toggle-domicilio-fiscal"       → toggle Agregar Domicilio Fiscal
============================================================
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from app.core.base_page import BasePage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FacturaReceptorPage(BasePage):
    """
    Page Object para la sección "Datos del Receptor" del formulario de Factura CFDI 4.0.

    Componente Angular: <app-receptor-factura>

    Campos del formulario:
    - RFC Receptor (con búsqueda automática)
    - Razón Social (autocompleta tras búsqueda)
    - Código Postal
    - Régimen Fiscal Receptor
    - Uso de CFDI
    - Email de envío (opcional)
    - Domicilio Fiscal (opcional)
    """

    # ------------------------------------------------------------------
    # Locators — RFC Receptor
    # ------------------------------------------------------------------

    # Input RFC — selector por placeholder (MEDIUM stability)
    # MEJOR: data-testid="input-rfc-receptor"
    RFC_RECEPTOR = (
        By.CSS_SELECTOR,
        "[data-testid='input-rfc-receptor'], "
        "app-receptor-factura input[placeholder='ABC010101XXX']",
    )

    # Botón de búsqueda de RFC (lupa)
    # MEJOR: data-testid="btn-buscar-rfc"
    BTN_BUSCAR_RFC = (
        By.CSS_SELECTOR,
        "[data-testid='btn-buscar-rfc'], "
        "app-receptor-factura button[type='button']",
    )

    # ------------------------------------------------------------------
    # Locators — Razón Social
    # ------------------------------------------------------------------

    # Input Razón Social — selector por placeholder (MEDIUM stability)
    # MEJOR: data-testid="input-razon-social"
    RAZON_SOCIAL = (
        By.CSS_SELECTOR,
        "[data-testid='input-razon-social'], "
        "app-receptor-factura input[placeholder='NOMBRE O DENOMINACIÓN SOCIAL']",
    )

    # ------------------------------------------------------------------
    # Locators — Código Postal
    # ------------------------------------------------------------------

    # Input Código Postal — selector por placeholder (MEDIUM stability)
    # MEJOR: data-testid="input-cp-receptor"
    CODIGO_POSTAL = (
        By.CSS_SELECTOR,
        "[data-testid='input-cp-receptor'], "
        "app-receptor-factura input[placeholder='00000']",
    )

    # ------------------------------------------------------------------
    # Locators — Régimen Fiscal y Uso CFDI (selects nativos)
    # ⚠️  RIESGO: posicionales dentro del componente
    # ------------------------------------------------------------------

    # Régimen Fiscal Receptor — PRIMER select del componente (LOW stability)
    # ⚠️  Si el frontend agrega selects antes, este selector se romperá.
    # TODO: solicitar al equipo frontend agregar data-testid="select-regimen-fiscal-receptor"
    # DESPUÉS (XPath por label — robusto):
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

    # ------------------------------------------------------------------
    # Locators — Email
    # ------------------------------------------------------------------

    # Input Email — type="email" es único en el componente (HIGH stability)
    # MEJOR: data-testid="input-email-receptor"
    EMAIL = (
        By.CSS_SELECTOR,
        "[data-testid='input-email-receptor'], "
        "app-receptor-factura input[type='email']",
    )

    # ------------------------------------------------------------------
    # Locators — Toggle Domicilio Fiscal (opcional)
    # ------------------------------------------------------------------

    # Toggle para expandir la sección de Domicilio Fiscal
    # TODO: solicitar al equipo frontend agregar data-testid="toggle-domicilio-fiscal"
    TOGGLE_DOMICILIO = (
        By.CSS_SELECTOR,
        "[data-testid='toggle-domicilio-fiscal'], "
        "app-receptor-factura button[role='switch']",
    )

    # ------------------------------------------------------------------
    # Validaciones
    # ------------------------------------------------------------------

    def is_section_loaded(self) -> bool:
        """Verifica que la sección de Datos del Receptor está visible."""
        return self.is_visible(
            (By.CSS_SELECTOR, "app-receptor-factura"),
            timeout=10,
        )

    # ------------------------------------------------------------------
    # Acciones — RFC
    # ------------------------------------------------------------------

    def fill_rfc(self, rfc: str) -> None:
        """
        Ingresa el RFC del Receptor en el campo correspondiente.

        El RFC se ingresa en mayúsculas automáticamente por el portal
        (propiedad CSS: text-transform: uppercase).

        Args:
            rfc: RFC válido SAT (12 caracteres persona moral,
                 13 caracteres persona física, o XAXX010101000 público general).
        """
        self.type_text(self.RFC_RECEPTOR, rfc.upper())
        logger.info(f"[RECEPTOR] RFC ingresado: {rfc.upper()}")

    def click_buscar_rfc(self) -> None:
        """
        Hace click en el botón de búsqueda de RFC (lupa).

        Después de la búsqueda, el portal puede auto-rellenar
        Razón Social y Régimen Fiscal del receptor.
        """
        self.click(self.BTN_BUSCAR_RFC)
        logger.info("[RECEPTOR] Click en botón de búsqueda RFC.")

    def fill_rfc_y_buscar(self, rfc: str) -> None:
        """
        Ingresa el RFC y hace click en el botón de búsqueda.

        Combina fill_rfc() + click_buscar_rfc() como paso atómico.

        Args:
            rfc: RFC del receptor.
        """
        self.fill_rfc(rfc)
        self.click_buscar_rfc()
        logger.info(f"[RECEPTOR] RFC ingresado y búsqueda ejecutada: {rfc}")

    # ------------------------------------------------------------------
    # Acciones — Razón Social
    # ------------------------------------------------------------------

    def fill_razon_social(self, nombre: str) -> None:
        """
        Ingresa la Razón Social del Receptor.

        Espera 0.6s para que el portal auto-rellene tras la búsqueda RFC, luego
        fuerza el valor usando el Native Input Value Setter de Angular si el portal
        lo sobrescribió.

        Args:
            nombre: Nombre o denominación social del receptor (mayúsculas).
        """
        import time as _time

        target = nombre.upper()
        element = self.wait_for_element(self.RAZON_SOCIAL, condition="visible")
        element.clear()
        element.send_keys(target)
        _time.sleep(0.6)  # dar tiempo al portal para que el RFC lookup sobreescriba (si aplica)
        actual = (element.get_attribute("value") or "").strip()
        if actual.upper() != target:
            logger.debug(f"[RECEPTOR] Razón social sobreescrita por portal ('{actual}'), forzando via JS...")
            self.driver.execute_script(
                """const niv = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
                   niv.call(arguments[0], arguments[1]);
                   arguments[0].dispatchEvent(new Event('input', {bubbles:true}));
                   arguments[0].dispatchEvent(new Event('change', {bubbles:true}));""",
                element, target
            )
        logger.info(f"[RECEPTOR] Razón social ingresada: {target}")

    # ------------------------------------------------------------------
    # Acciones — Código Postal
    # ------------------------------------------------------------------

    def fill_codigo_postal(self, cp: str) -> None:
        """
        Ingresa el Código Postal del domicilio fiscal del receptor.

        Args:
            cp: Código postal de 5 dígitos (ej: '06600').
        """
        from selenium.webdriver.common.keys import Keys
        import time as _time
        element = self.wait_for_element(self.CODIGO_POSTAL, condition="visible")
        element.clear()
        element.send_keys(cp)
        # Angular necesita blur/change para poblar el select de régimen fiscal
        element.send_keys(Keys.TAB)
        self.driver.execute_script(
            "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));"
            "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));"
            "arguments[0].dispatchEvent(new Event('blur', {bubbles:true}));",
            element,
        )
        _time.sleep(0.5)
        logger.info(f"[RECEPTOR] Código postal ingresado: {cp}")

    # ------------------------------------------------------------------
    # Acciones — Régimen Fiscal (select nativo)
    # ------------------------------------------------------------------

    def _select_by_codigo(self, locator, codigo: str, campo: str) -> None:
        """Helper: select_by_value con fallback flexible por texto que contenga el código."""
        import time as _time
        from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
        from selenium.webdriver.support.ui import Select as _Select
        for intento in range(3):
            try:
                element = self.wait_for_element(locator, condition="visible", timeout=15)
                sel = _Select(element)
                # Esperar que carguen opciones (más de 1 = la opción vacía inicial)
                if len(sel.options) <= 1:
                    _time.sleep(1)
                    element = self.wait_for_element(locator, condition="visible", timeout=10)
                    sel = _Select(element)
                try:
                    sel.select_by_value(codigo)
                    return
                except NoSuchElementException:
                    pass
                # Fallback: buscar por texto que contenga el código
                for opt in sel.options:
                    texto = opt.text.strip()
                    if texto.startswith(codigo) or f" {codigo} " in texto or texto == codigo:
                        opt.click()
                        return
                # Fallback 2: búsqueda parcial
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
        """Selecciona el Régimen Fiscal del Receptor por código SAT."""
        self._select_by_codigo(self.REGIMEN_FISCAL, codigo, "régimen fiscal")
        logger.info(f"[RECEPTOR] Régimen fiscal seleccionado: {codigo}")

    def select_regimen_fiscal_by_text(self, texto: str) -> None:
        """
        Selecciona el Régimen Fiscal del Receptor por texto visible.

        Args:
            texto: Texto visible del régimen (ej: '616 - Sin obligaciones fiscales').
        """
        self.select_by_visible_text(self.REGIMEN_FISCAL, texto)
        logger.info(f"[RECEPTOR] Régimen fiscal seleccionado por texto: {texto}")

    # ------------------------------------------------------------------
    # Acciones — Uso de CFDI (select nativo)
    # ------------------------------------------------------------------

    def select_uso_cfdi_by_value(self, codigo: str) -> None:
        """
        Selecciona el Uso de CFDI por código SAT.
        Intenta select_by_value, luego busca por texto que empiece con el código.
        """
        self._select_by_codigo(self.USO_CFDI, codigo, "uso CFDI")
        logger.info(f"[RECEPTOR] Uso de CFDI seleccionado: {codigo}")

    def select_uso_cfdi_by_text(self, texto: str) -> None:
        """
        Selecciona el Uso de CFDI por texto visible.

        Args:
            texto: Texto del catálogo SAT (ej: 'S01 - Sin efectos fiscales').
        """
        self.select_by_visible_text(self.USO_CFDI, texto)
        logger.info(f"[RECEPTOR] Uso de CFDI seleccionado por texto: {texto}")

    # ------------------------------------------------------------------
    # Acciones — Email
    # ------------------------------------------------------------------

    def fill_email(self, email: str) -> None:
        """
        Ingresa el correo electrónico para el envío de la factura (opcional).

        Args:
            email: Dirección de correo válida (ej: 'cliente@empresa.com').
        """
        self.type_text(self.EMAIL, email)
        logger.info(f"[RECEPTOR] Email ingresado: {email}")

    # ------------------------------------------------------------------
    # Método de llenado completo
    # ------------------------------------------------------------------

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
        """
        Llena todos los campos de Datos del Receptor en un solo paso.

        Combina todos los métodos de esta sección para usarse desde los Flows.
        Los Flows deben llamar a este método; no deben acceder a campos individuales.

        Args:
            rfc:            RFC del receptor (12 o 13 caracteres).
            razon_social:   Nombre o denominación social.
            codigo_postal:  Código postal (5 dígitos).
            regimen_fiscal: Código del régimen fiscal SAT (ej: '616').
            uso_cfdi:       Código de uso CFDI (ej: 'S01').
            email:          Correo electrónico (opcional).
            buscar_rfc:     Si True, hace click en el botón buscar después del RFC.
        """
        logger.info(f"[RECEPTOR] Iniciando llenado completo — RFC: {rfc}")

        self.fill_rfc(rfc)
        if buscar_rfc:
            self.click_buscar_rfc()

        self.fill_razon_social(razon_social)
        self.fill_codigo_postal(codigo_postal)
        self.select_regimen_fiscal_by_value(regimen_fiscal)
        self.select_uso_cfdi_by_value(uso_cfdi)

        if email:
            self.fill_email(email)

        logger.info(f"[RECEPTOR] Sección Receptor completada para RFC: {rfc}")

    # ------------------------------------------------------------------
    # Alias de métodos — nombres usados por FacturaFlow (dict plano Excel)
    # ------------------------------------------------------------------

    def capturar_rfc_receptor(self, rfc: str) -> None:
        """Alias de fill_rfc para compatibilidad con FacturaFlow."""
        self.fill_rfc(rfc)

    def capturar_razon_social(self, razon_social: str) -> None:
        """Alias de fill_razon_social para compatibilidad con FacturaFlow."""
        self.fill_razon_social(razon_social)

    def leer_razon_social(self) -> str:
        """Lee el valor actual del campo Razón Social desde el DOM."""
        try:
            el = self.driver.find_element(*self.RAZON_SOCIAL)
            return (el.get_attribute("value") or el.text or "").strip()
        except Exception:
            return "(no se pudo leer)"

    def capturar_codigo_postal(self, cp: str) -> None:
        """Alias de fill_codigo_postal para compatibilidad con FacturaFlow."""
        self.fill_codigo_postal(cp)

    def seleccionar_regimen_fiscal_receptor(self, valor: str) -> None:
        """
        Selecciona el Régimen Fiscal por código o texto descriptivo.

        Si el valor es tipo '616 - Sin obligaciones fiscales',
        extrae el código ('616') y usa select_by_value.

        Args:
            valor: Código (ej: '616') o texto completo (ej: '616 - Sin obligaciones fiscales').
        """
        if not valor or not valor.strip():
            return
        codigo = valor.split(" - ")[0].strip() if " - " in valor else valor.strip()
        self.select_regimen_fiscal_by_value(codigo)

    def seleccionar_uso_cfdi(self, valor: str) -> None:
        """
        Selecciona el Uso de CFDI por código o texto descriptivo.

        Args:
            valor: Código (ej: 'S01') o texto completo (ej: 'S01 - Sin efectos fiscales').
        """
        if not valor or not valor.strip():
            return
        codigo = valor.split(" - ")[0].strip() if " - " in valor else valor.strip()
        self.select_uso_cfdi_by_value(codigo)

    def capturar_email(self, email: str) -> None:
        """Alias de fill_email para compatibilidad con FacturaFlow."""
        if email:
            self.fill_email(email)

    # ------------------------------------------------------------------
    # Domicilio Fiscal (opcional)
    # ------------------------------------------------------------------

    def activar_domicilio_fiscal_si_aplica(self, datos: dict) -> bool:
        """
        Activa el switch 'Agregar Domicilio Fiscal' si algún campo de
        domicilio tiene valor.

        Regla: si calle, num_exterior, num_interior, colonia, municipio
        o estado tienen valor → activar switch.

        Args:
            datos: Dict con campos del caso (plano desde Excel).

        Returns:
            True si se activó el domicilio, False si se omitió.
        """
        campos_domicilio = ["calle", "num_exterior", "num_interior", "colonia", "municipio", "estado"]
        tiene_domicilio = any(str(datos.get(campo, "")).strip() for campo in campos_domicilio)

        if not tiene_domicilio:
            logger.info("[RECEPTOR] Sin datos de domicilio fiscal — se omite el switch.")
            return False

        try:
            # El switch es el único button[role='switch'] en la sección receptor
            switch = self.wait_for_element(self.TOGGLE_DOMICILIO, condition="clickable", timeout=10)
            aria_checked = switch.get_attribute("aria-checked")
            if aria_checked != "true":
                switch.click()
                logger.info("[RECEPTOR] Switch 'Agregar Domicilio Fiscal' activado.")
            else:
                logger.info("[RECEPTOR] Switch de domicilio fiscal ya estaba activo.")
            return True
        except Exception as exc:
            logger.warning(f"[RECEPTOR] No se pudo activar domicilio fiscal: {exc}")
            return False

    def capturar_domicilio_fiscal(self, datos: dict) -> None:
        """
        Llena los campos de domicilio fiscal si están presentes.

        Los campos del domicilio solo aparecen cuando el switch está activo.
        Los selectores son TODO hasta tener el HTML del domicilio abierto.

        Args:
            datos: Dict con campos: calle, num_exterior, num_interior,
                   colonia, municipio, estado.

        TODO: Obtener HTML del domicilio abierto e implementar selectores reales.
              Solicitar al equipo frontend:
              - data-testid="input-calle"
              - data-testid="input-num-exterior"
              - data-testid="input-num-interior"
              - data-testid="input-colonia"
              - data-testid="input-municipio"
              - data-testid="input-estado"
        """
        # Locators provisionales — pendientes de confirmación con DOM real
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
                logger.info(f"[RECEPTOR][DOMICILIO] {campo} = '{valor}'")
            except Exception as exc:
                logger.warning(f"[RECEPTOR][DOMICILIO] No se pudo capturar {campo}: {exc}")
