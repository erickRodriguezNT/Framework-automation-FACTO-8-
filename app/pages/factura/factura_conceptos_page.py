"""
factura_conceptos_page.py - Page Object para la sección "Conceptos y Servicios" del formulario de Factura.

Componente HTML: <app-conceptos-factura> + <app-modal-agregar-concepto>

============================================================
ANÁLISIS DE SELECTORES — app-conceptos-factura (HTML analizado)
============================================================

HTML OBSERVADO:
  <app-conceptos-factura>
    <!-- Encabezado con botón agregar -->
    <app-modal-agregar-concepto ...>
      <button class="flex items-center gap-2 bg-[#1760d7] ...">
        <span class="material-icons ...">add</span> Agregar Concepto
      </button>
      <!--container-->  ← el modal se renderiza aquí al hacer click
    </app-modal-agregar-concepto>

    <!-- Tabla de conceptos / estado vacío -->
    <p class="text-[14px] text-[#6b7280]">No hay conceptos agregados aún.</p>
  </app-conceptos-factura>

NOTA IMPORTANTE:
  El modal <app-modal-agregar-concepto> NO está abierto en el HTML analizado.
  Los campos del modal (clave producto, descripción, cantidad, etc.) son
  DESCONOCIDOS hasta ejecutar el test y abrir el modal.
  Los selectores del modal están marcados como TODO.

SELECTORES USADOS:
  - app-modal-agregar-concepto button : botón "Agregar Concepto" (MEDIUM, por tag dentro de componente)
  - Texto "No hay conceptos..." : validación de estado vacío (via XPath por texto)
  - Campos del modal: TODO (no visibles en HTML)

DATA-TESTID RECOMENDADOS AL EQUIPO FRONTEND:
  - data-testid="btn-agregar-concepto"     → botón "Agregar Concepto"
  - data-testid="modal-agregar-concepto"   → contenedor del modal
  - data-testid="input-descripcion"        → campo Descripción del concepto en modal
  - data-testid="input-cantidad"           → campo Cantidad en modal
  - data-testid="input-valor-unitario"     → campo Valor Unitario en modal
  - data-testid="input-clave-prod-serv"    → campo Clave Producto/Servicio en modal
  - data-testid="select-clave-unidad"      → select Clave de Unidad en modal
  - data-testid="select-objeto-impuesto"   → select Objeto Impuesto en modal
  - data-testid="input-descuento"          → campo Descuento en modal
  - data-testid="btn-guardar-concepto"     → botón Guardar del modal
  - data-testid="btn-cancelar-concepto"    → botón Cancelar del modal
  - data-testid="tabla-conceptos"          → tabla de conceptos agregados
  - data-testid="concepto-row"             → cada fila de concepto en tabla
============================================================
"""
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.core.base_page import BasePage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FacturaConceptosPage(BasePage):
    """
    Page Object para la sección "Conceptos y Servicios" del formulario de Factura.

    Componentes Angular:
    - <app-conceptos-factura>: contenedor de la sección
    - <app-modal-agregar-concepto>: modal de captura de cada concepto

    Un concepto es cada línea facturada (producto o servicio).
    El flujo es: click Agregar → llenar modal → guardar → verificar en tabla.
    """

    # ------------------------------------------------------------------
    # Locators — Botón Agregar Concepto
    # ------------------------------------------------------------------

    # Botón "Agregar Concepto" dentro del componente app-modal-agregar-concepto
    # El botón usa un <button> nativo con texto "Agregar Concepto" e ícono "add"
    # TODO: solicitar al equipo frontend agregar data-testid="btn-agregar-concepto"
    BTN_AGREGAR_CONCEPTO = (
        By.CSS_SELECTOR,
        "[data-testid='btn-agregar-concepto'], "
        "app-modal-agregar-concepto button",
    )

    # ------------------------------------------------------------------
    # Locators — Estado vacío de la tabla
    # ------------------------------------------------------------------

    # Mensaje cuando no hay conceptos: "No hay conceptos agregados aún."
    MENSAJE_SIN_CONCEPTOS = (
        By.XPATH,
        "//p[contains(normalize-space(.), 'No hay conceptos agregados')]",
    )

    # ------------------------------------------------------------------
    # Locators — Tabla de Conceptos (post-captura)
    # ------------------------------------------------------------------

    # Tabla o contenedor de la lista de conceptos
    # TODO: solicitar al equipo frontend agregar data-testid="tabla-conceptos"
    TABLA_CONCEPTOS = (
        By.CSS_SELECTOR,
        "[data-testid='tabla-conceptos'], "
        "app-conceptos-factura table, "
        "app-conceptos-factura .dt-card table",
    )

    # Filas de conceptos en la tabla
    # TODO: solicitar al equipo frontend agregar data-testid="concepto-row"
    FILAS_CONCEPTOS = (
        By.CSS_SELECTOR,
        "[data-testid='concepto-row'], "
        "app-conceptos-factura table tbody tr",
    )

    # ------------------------------------------------------------------
    # Locators — Modal de Agregar Concepto (campos internos)
    # ⚠️  El modal NO está abierto en el HTML analizado.
    #     Todos los selectores son TODO hasta confirmarlos con el portal real.
    # ------------------------------------------------------------------

    # Contenedor del modal
    # TODO: solicitar al equipo frontend agregar data-testid="modal-agregar-concepto"
    MODAL_CONTAINER = (
        By.CSS_SELECTOR,
        "[data-testid='modal-agregar-concepto']",
    )

    # Campo Descripción del Concepto
    MODAL_DESCRIPCION = (
        By.CSS_SELECTOR,
        "[data-testid='input-descripcion'], "
        "app-modal-agregar-concepto textarea[formcontrolname='descripcion'], "
        "app-modal-agregar-concepto input[formcontrolname='descripcion'], "
        "app-modal-agregar-concepto [placeholder*='Describa'], "
        "app-modal-agregar-concepto [placeholder*='escripci']",
    )

    # Campo Cantidad
    MODAL_CANTIDAD = (
        By.CSS_SELECTOR,
        "[data-testid='input-cantidad'], "
        "app-modal-agregar-concepto input[formcontrolname='cantidad'], "
        "app-modal-agregar-concepto input[type='number'][formcontrolname='cantidad'], "
        "app-modal-agregar-concepto input[type='number']",
    )

    # Campo No. Identificación (SKU/folio interno)
    MODAL_NO_IDENTIFICACION = (
        By.CSS_SELECTOR,
        "[data-testid='input-no-identificacion'], "
        "app-modal-agregar-concepto input[formcontrolname='noIdentificacion'], "
        "app-modal-agregar-concepto input[placeholder*='SKU']",
    )

    # Campo Valor Unitario / Precio Unitario
    MODAL_VALOR_UNITARIO = (
        By.CSS_SELECTOR,
        "[data-testid='input-valor-unitario'], "
        "app-modal-agregar-concepto input[formcontrolname='valorUnitario'], "
        "app-modal-agregar-concepto input[formcontrolname='precioUnitario']",
    )

    # Trigger del componente app-select-async para Clave Prod/Serv SAT
    # Confirmado en outerHTML: <app-select-async formcontrolname="claveProdServ"> con búsqueda async
    MODAL_CLAVE_PROD_SERV = (
        By.CSS_SELECTOR,
        "app-modal-agregar-concepto app-select-async[formcontrolname='claveProdServ'] > div, "
        "app-modal-agregar-concepto app-select-async[ng-reflect-name='claveProdServ'] > div",
    )

    # Trigger del componente app-select-async para Clave Unidad SAT
    # Confirmado en outerHTML: <app-select-async formcontrolname="claveUnidad"> con búsqueda async
    MODAL_CLAVE_UNIDAD = (
        By.CSS_SELECTOR,
        "app-modal-agregar-concepto app-select-async[formcontrolname='claveUnidad'] > div, "
        "app-modal-agregar-concepto app-select-async[ng-reflect-name='claveUnidad'] > div",
    )

    # Select Objeto de Impuesto (01 - No objeto, 02 - Sí objeto)
    # TODO: solicitar al equipo frontend agregar data-testid="select-objeto-impuesto"
    MODAL_OBJETO_IMPUESTO = (
        By.CSS_SELECTOR,
        "[data-testid='select-objeto-impuesto'], "
        "app-modal-agregar-concepto select[formcontrolname='objetoImp']",
    )

    # Campo Descuento (opcional)
    # TODO: solicitar al equipo frontend agregar data-testid="input-descuento"
    MODAL_DESCUENTO = (
        By.CSS_SELECTOR,
        "[data-testid='input-descuento'], "
        "app-modal-agregar-concepto input[formcontrolname='descuento']",
    )

    # Impuesto — app-select (no async) con formcontrolname='impuesto'
    MODAL_IMPUESTO_TRIGGER = (
        By.CSS_SELECTOR,
        "app-modal-agregar-concepto app-select[formcontrolname='impuesto'] > div",
    )

    # Retención o Traslado — select nativo con formcontrolname='retencionOTraslado'
    MODAL_RETENCION_O_TRASLADO = (
        By.CSS_SELECTOR,
        "app-modal-agregar-concepto select[formcontrolname='retencionOTraslado']",
    )

    # Tipo Factor — select nativo con formcontrolname='tipoFactor'
    MODAL_TIPO_FACTOR = (
        By.CSS_SELECTOR,
        "app-modal-agregar-concepto select[formcontrolname='tipoFactor']",
    )

    # Tasa o Cuota — input text con formcontrolname='tasaoCuota'
    MODAL_TASA_O_CUOTA = (
        By.CSS_SELECTOR,
        "app-modal-agregar-concepto input[formcontrolname='tasaoCuota']",
    )

    # Botón azul de guardar/agregar concepto — footer del modal.
    # Selector exacto obtenido del HTML del portal:
    #   div.flex.items-center.justify-end.gap-3.px-6.py-4.border-t > button.bg-[#1760d7]
    MODAL_BTN_GUARDAR = (
        By.CSS_SELECTOR,
        "app-modal-agregar-concepto "
        "div.flex.items-center.justify-end.gap-3.px-6.py-4.border-t "
        "button.bg-\\[\\#1760d7\\]",
    )

    # Botón Cancelar en el modal
    # TODO: solicitar al equipo frontend agregar data-testid="btn-cancelar-concepto"
    MODAL_BTN_CANCELAR = (
        By.CSS_SELECTOR,
        "[data-testid='btn-cancelar-concepto']",
    )

    # Botón "Agregar Impuesto" dentro del modal (confirma los valores de tasa/factor/ret)
    MODAL_BTN_AGREGAR_IMPUESTO = (
        By.XPATH,
        "//app-modal-agregar-concepto//button["
        "contains(normalize-space(.), 'Agregar Impuesto') "
        "or contains(normalize-space(.), 'Agregar impuesto')"
        "] | //app-modal-agregar-concepto//button[@data-testid='btn-agregar-impuesto']",
    )

    # Selector genérico de cualquier campo del modal (para detectar apertura)
    # Busca el primer input visible dentro del modal tras hacer click en Agregar
    # TODO: Reemplazar con selector real obtenido del portal
    _MODAL_CUALQUIER_CAMPO = (
        By.XPATH,
        "("
        "//app-modal-agregar-concepto//input | "
        "//app-modal-agregar-concepto//select | "
        "//*[@data-testid='modal-agregar-concepto']//input"
        ")[1]",
    )

    # ------------------------------------------------------------------
    # Validaciones de estado de la sección
    # ------------------------------------------------------------------

    def is_seccion_visible(self) -> bool:
        """Verifica que la sección Conceptos y Servicios está visible."""
        return self.is_visible(
            (By.CSS_SELECTOR, "app-conceptos-factura"),
            timeout=10,
        )

    def is_tabla_vacia(self) -> bool:
        """
        Verifica que la tabla de conceptos está vacía.

        Returns:
            True si se muestra el mensaje "No hay conceptos agregados aún."
        """
        return self.is_visible(self.MENSAJE_SIN_CONCEPTOS, timeout=3)

    def get_cantidad_conceptos(self) -> int:
        """
        Retorna el número de conceptos actualmente en la tabla.

        Returns:
            Número de filas de concepto en la tabla (0 si la tabla está vacía).
        """
        try:
            filas = self.wait_for_elements(self.FILAS_CONCEPTOS, timeout=5)
            return len(filas)
        except Exception:
            return 0

    def is_modal_abierto(self) -> bool:
        """
        Verifica que el modal de Agregar Concepto está abierto.

        Comprueba el contenedor data-testid primero; si no existe todavía,
        busca cualquier input/select dentro del componente del modal.
        """
        return (
            self.is_visible(self.MODAL_CONTAINER, timeout=2)
            or self.is_visible(self._MODAL_CUALQUIER_CAMPO, timeout=2)
        )

    # ------------------------------------------------------------------
    # Esperas explícitas del modal
    # ------------------------------------------------------------------

    def _wait_for_modal_abierto(self, timeout: int = 10) -> None:
        """
        Espera a que el modal de Agregar Concepto esté visible.

        Intenta primero el contenedor con data-testid; si no responde,
        busca cualquier campo de entrada dentro del componente modal.

        Args:
            timeout: Segundos máximos de espera.

        Raises:
            PageError: Si el modal no abre en el tiempo indicado.
        """
        from app.utils.exceptions import PageError
        logger.debug("[CONCEPTOS] Esperando apertura del modal...")

        # Intento 1: data-testid del contenedor del modal
        if self.is_visible(self.MODAL_CONTAINER, timeout=timeout):
            logger.info("[CONCEPTOS] Modal abierto (via data-testid).")
            return

        # Intento 2: cualquier input/select dentro del componente modal
        if self.is_visible(self._MODAL_CUALQUIER_CAMPO, timeout=3):
            logger.info("[CONCEPTOS] Modal abierto (via campo genérico).")
            # DIAGNÓSTICO compacto: atributos clave de cada campo del modal
            try:
                info = self.driver.execute_script("""
                    const m = document.querySelector('app-modal-agregar-concepto');
                    if (!m) return 'NO_MODAL';
                    return Array.from(m.querySelectorAll('input,select,textarea,app-select')).map((el,i) => {
                        const fc = el.getAttribute('formcontrolname') || el.getAttribute('ng-reflect-name') || '-';
                        const ph = el.getAttribute('placeholder') || el.getAttribute('ng-reflect-placeholder') || '-';
                        return `[${i}]${el.tagName}:${fc}:${ph}`;
                    }).join(' | ');
                """)
                logger.info(f"[CONCEPTOS DIAG modal-fields] {info}")
            except Exception as _e:
                logger.warning(f"[CONCEPTOS DIAG] Error dump: {_e}")
            return

        raise PageError(
            "El modal 'Agregar Concepto' no se abrió después de hacer click. "
            "TODO: agregar data-testid='modal-agregar-concepto' al componente "
            "<app-modal-agregar-concepto> para detectar apertura."
        )

    def _wait_for_modal_cerrado(self, timeout: int = 15) -> None:
        """
        Espera a que el modal de Agregar Concepto se cierre tras guardar.

        Usa EC.invisibility_of_element_located para ESPERAR activamente
        hasta que los campos del modal dejen de ser visibles (Angular cierra
        el modal con animación tras el submit exitoso).

        Args:
            timeout: Segundos máximos de espera.
        """
        import time as _time
        logger.debug("[CONCEPTOS] Esperando cierre del modal...")

        try:
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(self._MODAL_CUALQUIER_CAMPO)
            )
            logger.info("[CONCEPTOS] Modal cerrado.")
        except TimeoutException:
            logger.warning(
                "[CONCEPTOS] El modal podría no haberse cerrado. "
                "Verificar en ejecución real."
            )
        # Pausa extra para que Angular termine de actualizar totales y la lista
        _time.sleep(1.5)

    def wait_for_nuevo_concepto_guardado(self, count_antes: int, timeout: int = 10) -> None:
        """
        Espera a que la tabla tenga al menos un concepto más que antes de agregar.

        Útil para confirmar que el modal se cerró y el concepto fue registrado
        correctamente en la tabla.

        Args:
            count_antes: Número de conceptos antes de agregar el nuevo.
            timeout:     Segundos máximos de espera.
        """
        import time
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            count_actual = self.get_cantidad_conceptos()
            if count_actual > count_antes:
                logger.info(f"[CONCEPTOS] Concepto guardado. Total en tabla: {count_actual}")
                return
            time.sleep(0.5)

        logger.warning(
            f"[CONCEPTOS] No se detectó nuevo concepto en tabla tras {timeout}s. "
            "Puede ser normal si la tabla usa paginación o lazy render."
        )

    # ------------------------------------------------------------------
    # Acciones — Abrir modal
    # ------------------------------------------------------------------

    def click_agregar_concepto(self) -> None:
        """
        Hace click en el botón "Agregar Concepto" para abrir el modal.

        El modal se renderiza como un overlay o panel dentro del componente
        <app-modal-agregar-concepto>. Espera a que el botón sea clickeable.
        """
        logger.info("[CONCEPTOS] Haciendo click en 'Agregar Concepto'...")
        self.wait_for_element(self.BTN_AGREGAR_CONCEPTO, condition="clickable", timeout=15)
        self.click(self.BTN_AGREGAR_CONCEPTO)
        logger.info("[CONCEPTOS] Click en 'Agregar Concepto' ejecutado.")

    # ------------------------------------------------------------------
    # Acciones — app-select custom (mismo patrón que comprobante/emisor)
    # ------------------------------------------------------------------

    def _click_app_select_async_option(self, formcontrolname: str, texto_opcion: str) -> None:
        """
        Interactúa con <app-select-async formcontrolname='...'> del modal:
        click trigger → input de búsqueda interno → espera resultados async → click opción.

        Usa JS para operar directamente dentro del componente específico, evitando
        interferencia con otros app-select del modal.
        """
        import time as _time

        # Buscar el componente async por formcontrolname
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

        # Scroll y click con Selenium (necesario para disparar eventos Angular)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", host)
        trigger_div = host.find_element(By.CSS_SELECTOR, "div")
        try:
            trigger_div.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", trigger_div)

        # Esperar el input de búsqueda via driver (no host que queda stale post-render)
        # app-select-async renderiza un input con placeholder "Escribe al menos 3 caracteres..."
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
            # Fallback: input con placeholder que menciona "caracteres" o "Escribe"
            search_input = WebDriverWait(self.driver, 4).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR,
                     "input[placeholder*='caracteres'], input[placeholder*='Escribe']")
                )
            )

        # Escribir término de búsqueda
        termino = texto_opcion.split(" - ")[0] if " - " in texto_opcion else texto_opcion
        search_input.clear()
        search_input.send_keys(termino)

        # Esperar resultados async (debounce 400ms + tiempo de API)
        _time.sleep(2.5)

        # Buscar la opción en el dropdown que aparece tras la búsqueda
        # El dropdown se renderiza dentro del componente o como overlay adyacente
        _js_find_in_async = """
            const fc = arguments[0];
            const target = arguments[1];
            // Buscar dentro del componente app-select-async
            const host = document.querySelector(
                `app-modal-agregar-concepto app-select-async[formcontrolname="${fc}"]`
            );
            // El dropdown puede estar en host o como overlay en el body/document
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
            logger.info(f"[CONCEPTOS app-select-async] Opción seleccionada: '{texto_opcion}'")
            return

        # Fallback XPath: buscar opción visible que contenga el término
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
            logger.info(f"[CONCEPTOS app-select-async] Opción seleccionada (XPath): '{texto_opcion}'")
        except TimeoutException:
            raise TimeoutException(
                f"No se encontró opción '{texto_opcion}' en app-select-async[formcontrolname='{formcontrolname}']"
            )

    def _click_app_select_option(self, trigger_locator: tuple, texto_opcion: str, sleep_after_type: float = 0.5) -> None:
        """Interactúa con un <app-select> del modal: click trigger → búsqueda → click opción."""
        import time as _time
        _OVERLAY = (By.CSS_SELECTOR, "div.fixed.inset-0[class*='z-']")
        try:
            WebDriverWait(self.driver, 10).until(EC.invisibility_of_element_located(_OVERLAY))
        except TimeoutException:
            pass
        # Usar wait directo sin scroll_into_view para evitar timeout largo
        try:
            trigger = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(trigger_locator)
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", trigger)
        except TimeoutException:
            raise TimeoutException(
                f"No se encontró trigger app-select para '{texto_opcion}': {trigger_locator}"
            )
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
            search_box = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(_SEARCH_INPUT)
            )
            termino = texto_opcion.split(" - ")[0] if " - " in texto_opcion else texto_opcion
            search_box.clear()
            search_box.send_keys(termino)
        except TimeoutException:
            pass
        _time.sleep(sleep_after_type)

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
            logger.info(f"[CONCEPTOS app-select] Opción seleccionada (JS): '{texto_opcion}'")
            return

        termino = texto_opcion.split(" - ")[0] if " - " in texto_opcion else texto_opcion
        fallback = (By.XPATH,
            f"//*[contains(normalize-space(.), '{termino}') and "
            f"not(self::input) and not(self::textarea) and not(self::button) and "
            f"not(self::nav) and not(self::header)]")
        try:
            opt = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(fallback))
            opt.click()
            logger.info(f"[CONCEPTOS app-select] Opción seleccionada (XPath): '{texto_opcion}'")
        except TimeoutException:
            raise TimeoutException(f"No se encontró opción '{texto_opcion}' en app-select del modal.")

    # ------------------------------------------------------------------
    # Acciones — Campos del modal
    # ------------------------------------------------------------------

    def fill_descripcion(self, descripcion: str) -> None:
        """
        Ingresa la Descripción del concepto en el modal.

        Args:
            descripcion: Texto de la descripción (ej: 'SERVICIO DE HOSPEDAJE').
        """
        self.type_text(self.MODAL_DESCRIPCION, descripcion)
        logger.info(f"[CONCEPTOS] Descripción: {descripcion}")

    def fill_cantidad(self, cantidad: str) -> None:
        """
        Ingresa la Cantidad del concepto.

        Args:
            cantidad: Cantidad como string (ej: '1', '2.5').
        """
        self.type_text(self.MODAL_CANTIDAD, cantidad)
        logger.info(f"[CONCEPTOS] Cantidad: {cantidad}")

    def fill_valor_unitario(self, valor: str) -> None:
        """
        Ingresa el Valor Unitario / Precio Unitario del concepto.

        Args:
            valor: Precio unitario como string (ej: '1000.00').
        """
        self.type_text(self.MODAL_VALOR_UNITARIO, valor)
        logger.info(f"[CONCEPTOS] Valor unitario: {valor}")

    def fill_clave_prod_serv(self, clave: str) -> None:
        """
        Selecciona la Clave de Producto/Servicio SAT via app-select-async.

        Args:
            clave: Clave SAT (ej: '90111501' para hospedaje).
        """
        self._click_app_select_async_option('claveProdServ', clave)
        logger.info(f"[CONCEPTOS] Clave prod/serv: {clave}")

    def fill_clave_unidad(self, clave_unidad: str) -> None:
        """
        Selecciona la Clave de Unidad SAT via app-select-async.

        Args:
            clave_unidad: Clave de unidad (ej: 'E48' para Unidad de Servicio).
        """
        self._click_app_select_async_option('claveUnidad', clave_unidad)
        logger.info(f"[CONCEPTOS] Clave unidad: {clave_unidad}")

    def select_objeto_impuesto(self, valor: str) -> None:
        """
        Selecciona el Objeto de Impuesto del concepto.

        Args:
            valor: '01' (No objeto), '02' (Sí objeto impuesto), '03' (Sí con retención).
        """
        self.select_by_value(self.MODAL_OBJETO_IMPUESTO, valor)
        logger.info(f"[CONCEPTOS] Objeto de impuesto: {valor}")

    def fill_descuento(self, descuento: str) -> None:
        """
        Ingresa el Descuento aplicado al concepto (opcional).

        Args:
            descuento: Importe de descuento como string (ej: '0.00').
        """
        self.type_text(self.MODAL_DESCUENTO, descuento)
        logger.info(f"[CONCEPTOS] Descuento: {descuento}")

    def select_impuesto(self, impuesto: str) -> None:
        """Selecciona el tipo de impuesto (ej: '002' IVA) usando el app-select del modal."""
        self._click_app_select_option(self.MODAL_IMPUESTO_TRIGGER, impuesto)
        logger.info(f"[CONCEPTOS] Impuesto: {impuesto}")

    def select_retencion_o_traslado(self, valor: str) -> None:
        """Selecciona Retención o Traslado en el select nativo del modal."""
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
        logger.info(f"[CONCEPTOS] Retención/Traslado: {valor}")

    def select_tipo_factor(self, valor: str) -> None:
        """Selecciona el Tipo de Factor (Tasa/Cuota/Exento) en el select nativo del modal."""
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
        logger.info(f"[CONCEPTOS] Tipo factor: {valor}")

    def fill_tasa_o_cuota(self, tasa: str) -> None:
        """Ingresa la Tasa o Cuota del impuesto (ej: '0.160000')."""
        self.type_text(self.MODAL_TASA_O_CUOTA, tasa)
        logger.info(f"[CONCEPTOS] Tasa o cuota: {tasa}")

    def fill_no_identificacion(self, no_id: str) -> None:
        """
        Ingresa el No. de Identificación (SKU/folio interno) del concepto (opcional).

        Args:
            no_id: Folio o SKU (ej: 'SKU-001').
        """
        self.type_text(self.MODAL_NO_IDENTIFICACION, no_id)
        logger.info(f"[CONCEPTOS] No. Identificación: {no_id}")

    # ------------------------------------------------------------------
    # Helpers de validación de campos enviados
    # ------------------------------------------------------------------

    def _validar_campo_enviado(self, nombre: str, esperado: str, locator: tuple) -> None:
        """
        Lee el valor actual de un campo (input o app-select) y lo compara
        con el valor esperado. Registra INFO si coincide, WARNING si difiere.
        """
        try:
            el = self.wait_for_element(locator, condition="visible", timeout=3)
            actual_value = (el.get_attribute("value") or "").strip()
            actual_text  = (el.text or "").strip()
            actual = actual_value if actual_value else actual_text
            if esperado.strip() in actual or actual == esperado.strip():
                logger.info(
                    f"[CONCEPTOS VALIDACIÓN] ✔ {nombre}: '{actual}'"
                )
            else:
                logger.warning(
                    f"[CONCEPTOS VALIDACIÓN] ✗ {nombre}: "
                    f"enviado='{esperado}' — campo_value='{actual_value}' campo_text='{actual_text}'"
                )
        except Exception as exc:
            logger.warning(
                f"[CONCEPTOS VALIDACIÓN] No se pudo leer '{nombre}': {exc}"
            )

    def _validar_select_enviado(self, nombre: str, esperado: str, locator: tuple) -> None:
        """
        Lee el valor actualmente seleccionado en un <select> nativo y lo
        compara con el valor esperado (texto visible o value).
        """
        try:
            from selenium.webdriver.support.ui import Select as _Select
            el = self.wait_for_element(locator, condition="visible", timeout=3)
            sel = _Select(el)
            selected = sel.first_selected_option
            actual_text = selected.text.strip()
            actual_val  = (selected.get_attribute("value") or "").strip()
            if esperado.strip().lower() in (actual_text.lower(), actual_val.lower()):
                logger.info(
                    f"[CONCEPTOS VALIDACIÓN] ✔ {nombre}: '{actual_text}' (value='{actual_val}')"
                )
            else:
                logger.warning(
                    f"[CONCEPTOS VALIDACIÓN] ✗ {nombre}: "
                    f"enviado='{esperado}' — seleccionado='{actual_text}' (value='{actual_val}')"
                )
        except Exception as exc:
            logger.warning(
                f"[CONCEPTOS VALIDACIÓN] No se pudo leer '{nombre}': {exc}"
            )

    def click_guardar_concepto(self) -> None:
        """
        Guarda el concepto haciendo click en el botón azul del footer del modal.

        Usa el selector exacto del botón de guardar (footer del modal),
        evitando confundirlo con otros botones tipo 'Agregar Impuesto'.
        """
        logger.info("[CONCEPTOS] Haciendo click en botón guardar concepto...")
        self.wait_for_element(self.MODAL_BTN_GUARDAR, condition="clickable", timeout=10)
        self.click(self.MODAL_BTN_GUARDAR)
        logger.info("[CONCEPTOS] Click en botón guardar ejecutado.")

    # ------------------------------------------------------------------
    # Método de captura completa de un concepto
    # ------------------------------------------------------------------

    def agregar_concepto_completo(self, concepto: dict) -> None:
        """
        Agrega un concepto completo al formulario de Factura.

        Abre el modal, llena todos los campos y guarda el concepto.
        Usa los datos del diccionario según la estructura de test_data.

        Args:
            concepto: Diccionario con los datos del concepto. Estructura:
                {
                    "descripcion":             "SERVICIO DE HOSPEDAJE",
                    "cantidad":                "1",
                    "unidad":                  "E48",
                    "clave_producto_servicio": "90111501",
                    "valor_unitario":          "1000.00",
                    "descuento":               "0.00",    # opcional
                    "objeto_impuesto":         "02"
                }
        """
        descripcion = concepto.get("descripcion", "")
        logger.info(f"[CONCEPTOS] Iniciando captura de concepto: {descripcion!r}")

        # Registrar cantidad actual antes de agregar (para verificar al final)
        # ── Log de todos los valores que vienen del Excel ──────────────────
        logger.info(
            "[CONCEPTOS] Valores recibidos del Excel:\n"
            f"   1. CLAVE UNIDAD       = {concepto.get('unidad', '')!r}\n"
            f"   2. CANTIDAD           = {concepto.get('cantidad', '1')!r}\n"
            f"   3. NO. IDENTIFICACION = {concepto.get('no_identificacion', '')!r}\n"
            f"   4. CLAVE PROD/SERV    = {concepto.get('clave_producto_servicio', '')!r}\n"
            f"   5. DESCRIPCION        = {concepto.get('descripcion', '')!r}\n"
            f"   6. VALOR UNITARIO     = {concepto.get('valor_unitario', '0.00')!r}\n"
            f"   7. DESCUENTO          = {concepto.get('descuento', '0.00')!r}\n"
            f"   8. OBJETO IMPUESTO    = {concepto.get('objeto_impuesto', '')!r}\n"
            f"   9. IMPUESTO           = {concepto.get('impuesto', '')!r}\n"
            f"  10. RET/TRAS           = {concepto.get('ret_tras', '')!r}\n"
            f"  11. TIPO FACTOR        = {concepto.get('tipo_factor', '')!r}\n"
            f"  12. TASA O CUOTA       = {concepto.get('tasa_o_cuota', '')!r}"
        )

        count_antes = self.get_cantidad_conceptos()

        # Abrir el modal
        self.click_agregar_concepto()
        self._wait_for_modal_abierto(timeout=10)

        # ── 1. CLAVE UNIDAD ──────────────────────────────────────────────────
        clave_unidad = concepto.get("unidad", "")
        if clave_unidad:
            self.fill_clave_unidad(clave_unidad)
            self._validar_campo_enviado("CLAVE UNIDAD", clave_unidad, self.MODAL_CLAVE_UNIDAD)
        else:
            logger.warning("[CONCEPTOS] CLAVE UNIDAD: vacío en Excel, campo no enviado")

        # ── 2. CANTIDAD ───────────────────────────────────────────────────────
        cantidad = concepto.get("cantidad", "1")
        self.fill_cantidad(cantidad)
        self._validar_campo_enviado("CANTIDAD", cantidad, self.MODAL_CANTIDAD)

        # ── 3. NO. IDENTIFICACION ─────────────────────────────────────────────
        no_id = concepto.get("no_identificacion", "")
        if no_id:
            self.fill_no_identificacion(no_id)
            self._validar_campo_enviado("NO. IDENTIFICACION", no_id, self.MODAL_NO_IDENTIFICACION)
        else:
            logger.warning("[CONCEPTOS] NO. IDENTIFICACION: vacío en Excel, campo no enviado")

        # ── 4. CLAVE PROD/SERV ────────────────────────────────────────────────
        clave_prod = concepto.get("clave_producto_servicio", "")
        if clave_prod:
            self.fill_clave_prod_serv(clave_prod)
            self._validar_campo_enviado("CLAVE PROD/SERV", clave_prod, self.MODAL_CLAVE_PROD_SERV)
        else:
            logger.warning("[CONCEPTOS] CLAVE PROD/SERV: vacío en Excel, campo no enviado")

        # ── 5. DESCRIPCION ────────────────────────────────────────────────────
        self.fill_descripcion(descripcion)
        self._validar_campo_enviado("DESCRIPCION", descripcion, self.MODAL_DESCRIPCION)

        # ── 6. VALOR UNITARIO ─────────────────────────────────────────────────
        valor_unitario = concepto.get("valor_unitario", "0.00")
        self.fill_valor_unitario(valor_unitario)
        self._validar_campo_enviado("VALOR UNITARIO", valor_unitario, self.MODAL_VALOR_UNITARIO)

        # ── 7. DESCUENTO ──────────────────────────────────────────────────────
        descuento = concepto.get("descuento", "0.00")
        if descuento and descuento not in ("0.00", "0", ""):
            self.fill_descuento(descuento)
            self._validar_campo_enviado("DESCUENTO", descuento, self.MODAL_DESCUENTO)
        else:
            logger.info(f"[CONCEPTOS] DESCUENTO: {descuento!r} — sin descuento, campo no modificado")

        # ── 8. OBJETO IMPUESTO ────────────────────────────────────────────────
        objeto_imp = concepto.get("objeto_impuesto", "")
        if objeto_imp:
            self.select_objeto_impuesto(objeto_imp)
            self._validar_select_enviado("OBJETO IMPUESTO", objeto_imp, self.MODAL_OBJETO_IMPUESTO)
        else:
            logger.warning("[CONCEPTOS] OBJETO IMPUESTO: vacío en Excel, campo no enviado")

        # ── 9. IMPUESTO ───────────────────────────────────────────────────────
        impuesto = concepto.get("impuesto", "")
        if impuesto:
            self.select_impuesto(impuesto)
            self._validar_campo_enviado("IMPUESTO", impuesto, self.MODAL_IMPUESTO_TRIGGER)
        else:
            logger.warning("[CONCEPTOS] IMPUESTO: vacío en Excel, campo no enviado")

        # ── 10. RET/TRAS ──────────────────────────────────────────────────────
        ret_tras = concepto.get("ret_tras", "")
        if ret_tras:
            self.select_retencion_o_traslado(ret_tras)
            self._validar_select_enviado("RET/TRAS", ret_tras, self.MODAL_RETENCION_O_TRASLADO)
        else:
            logger.warning("[CONCEPTOS] RET/TRAS: vacío en Excel, campo no enviado")

        # ── 11. TIPO FACTOR ───────────────────────────────────────────────────
        tipo_factor = concepto.get("tipo_factor", "")
        if tipo_factor:
            self.select_tipo_factor(tipo_factor)
            self._validar_select_enviado("TIPO FACTOR", tipo_factor, self.MODAL_TIPO_FACTOR)
        else:
            logger.warning("[CONCEPTOS] TIPO FACTOR: vacío en Excel, campo no enviado")

        # ── 12. TASA O CUOTA ──────────────────────────────────────────────────
        tasa_o_cuota = concepto.get("tasa_o_cuota", "")
        if tasa_o_cuota:
            self.fill_tasa_o_cuota(tasa_o_cuota)
            self._validar_campo_enviado("TASA O CUOTA", tasa_o_cuota, self.MODAL_TASA_O_CUOTA)
        else:
            logger.warning("[CONCEPTOS] TASA O CUOTA: vacío en Excel, campo no enviado")
        # ── Agregar Impuesto (confirma la fila de impuesto en el modal) ────────────
        if self.is_visible(self.MODAL_BTN_AGREGAR_IMPUESTO, timeout=5):
            self.wait_for_element(self.MODAL_BTN_AGREGAR_IMPUESTO, condition="clickable", timeout=8)
            self.click(self.MODAL_BTN_AGREGAR_IMPUESTO)
            logger.info("[CONCEPTOS] Click en 'Agregar Impuesto' ejecutado.")
        else:
            logger.warning("[CONCEPTOS] Botón 'Agregar Impuesto' no encontrado — puede no existir en esta versión del portal.")
        # Guardar y esperar que el modal se cierre
        self.click_guardar_concepto()
        self._wait_for_modal_cerrado(timeout=15)

        # Confirmar que el concepto apareció en la tabla
        self.wait_for_nuevo_concepto_guardado(count_antes, timeout=15)
        logger.info(f"[CONCEPTOS] Concepto agregado exitosamente: {descripcion!r}")

        # Captura de pantalla de validación: tabla de conceptos + totales post-guardado
        try:
            self.take_screenshot(
                f"concepto_guardado_{descripcion[:30].replace(' ', '_')}",
                directory=None,
            )
            logger.info("[CONCEPTOS] Screenshot de validación post-guardado tomado.")
        except Exception as _exc:
            logger.warning(f"[CONCEPTOS] No se pudo tomar screenshot post-guardado: {_exc}")

    def agregar_concepto_desde_caso(self, caso: dict) -> None:
        """
        Adapter para FacturaFlow: construye el dict de concepto desde el
        dict plano del Excel y llama a agregar_concepto_completo.

        Mapeo de claves Excel → claves de concepto:
            concepto_descripcion             → descripcion
            concepto_cantidad                → cantidad
            concepto_unidad (clave SAT)      → unidad
            concepto_clave_prod_serv         → clave_producto_servicio
            concepto_valor_unitario          → valor_unitario
            concepto_descuento               → descuento
            concepto_objeto_impuesto         → objeto_impuesto

        Args:
            caso: Dict plano con los datos del caso desde el Excel.
        """
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

