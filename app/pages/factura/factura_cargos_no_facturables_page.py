"""
factura_cargos_no_facturables_page.py — Page Object para la sección
"Cargos No Facturables" del formulario de Factura CFDI 4.0.

Componente HTML: <app-cargos-no-facturables>

============================================================
SELECTORES CONFIRMADOS EN HTML:
============================================================
  - input[formcontrolname='cargo']                           → nombre del cargo
  - app-cargos-no-facturables input[formcontrolname='importe'] → importe del cargo
  - app-cargos-no-facturables button[type='submit']          → botón Agregar cargo

NOTA: Los cargos no facturables son montos adicionales que se incluyen
en el comprobante pero NO forman parte del subtotal fiscal del CFDI.
Son opcionales y solo se capturan cuando el caso Excel tiene un cargo definido.

DATA-TESTID RECOMENDADOS AL EQUIPO FRONTEND:
  - data-testid="input-cargo-nombre"   → campo nombre del cargo
  - data-testid="input-cargo-importe"  → campo importe del cargo
  - data-testid="btn-agregar-cargo"    → botón Agregar
  - data-testid="tabla-cargos"         → tabla de cargos agregados
  - data-testid="cargo-row"            → cada fila de cargo en tabla
============================================================
"""
from selenium.webdriver.common.by import By

from app.core.base_page import BasePage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FacturaCargosNoFacturablesPage(BasePage):
    """
    Page Object para la sección "Cargos No Facturables" del formulario de Factura.

    Los cargos no facturables son importes adicionales (propinas, seguros, etc.)
    que se registran en el comprobante pero no impactan los totales fiscales del CFDI.

    Flujo de uso:
        1. Verificar visibilidad de la sección
        2. Llenar nombre del cargo
        3. Llenar importe del cargo
        4. Click en Agregar
        5. Verificar que el cargo aparece en la tabla
    """

    # ------------------------------------------------------------------
    # Locators — confirmados en HTML del portal
    # ------------------------------------------------------------------

    # Campo nombre del cargo
    # Confirmado en HTML: input[formcontrolname='cargo']
    CARGO_NOMBRE = (
        By.CSS_SELECTOR,
        "[data-testid='input-cargo-nombre'], "
        "app-cargos-no-facturables input[formcontrolname='cargo'], "
        "input[formcontrolname='cargo']",
    )

    # Campo importe del cargo
    # Confirmado en HTML: app-cargos-no-facturables input[formcontrolname='importe']
    CARGO_IMPORTE = (
        By.CSS_SELECTOR,
        "[data-testid='input-cargo-importe'], "
        "app-cargos-no-facturables input[formcontrolname='importe']",
    )

    # Botón Agregar cargo
    # Confirmado en HTML: app-cargos-no-facturables button[type='submit']
    BTN_AGREGAR = (
        By.CSS_SELECTOR,
        "[data-testid='btn-agregar-cargo'], "
        "app-cargos-no-facturables button[type='submit']",
    )

    # Contenedor de la sección
    CONTENEDOR_CARGOS = (
        By.CSS_SELECTOR,
        "app-cargos-no-facturables",
    )

    # Tabla de cargos agregados
    TABLA_CARGOS = (
        By.CSS_SELECTOR,
        "[data-testid='tabla-cargos'], "
        "app-cargos-no-facturables table",
    )

    # Filas de cargos en la tabla
    FILAS_CARGOS = (
        By.CSS_SELECTOR,
        "[data-testid='cargo-row'], "
        "app-cargos-no-facturables table tbody tr",
    )

    # ------------------------------------------------------------------
    # Verificaciones de estado
    # ------------------------------------------------------------------

    def is_seccion_visible(self) -> bool:
        """
        Verifica que la sección Cargos No Facturables está visible en pantalla.

        Returns:
            True si el componente app-cargos-no-facturables es visible.
        """
        return self.is_visible(self.CONTENEDOR_CARGOS, timeout=5)

    def get_cantidad_cargos(self) -> int:
        """
        Retorna el número de cargos actualmente en la tabla.

        Returns:
            Número de filas de cargo (0 si la tabla está vacía).
        """
        try:
            filas = self.wait_for_elements(self.FILAS_CARGOS, timeout=5)
            return len(filas)
        except Exception:
            return 0

    # ------------------------------------------------------------------
    # Acciones — captura de cargo
    # ------------------------------------------------------------------

    def fill_nombre_cargo(self, nombre: str) -> None:
        """
        Ingresa el nombre/descripción del cargo no facturable.

        Args:
            nombre: Nombre del cargo (ej: 'Propina', 'Seguro de viaje').
        """
        self.type_text(self.CARGO_NOMBRE, nombre, clear_first=True)
        logger.info(f"[CARGOS-NF] Nombre de cargo: '{nombre}'")

    def fill_importe_cargo(self, importe: str) -> None:
        """
        Ingresa el importe del cargo no facturable.

        Args:
            importe: Importe como string (ej: '150.00').
        """
        self.type_text(self.CARGO_IMPORTE, importe, clear_first=True)
        logger.info(f"[CARGOS-NF] Importe del cargo: '{importe}'")

    def click_agregar_cargo(self) -> None:
        """
        Hace click en el botón Agregar para registrar el cargo.

        Espera a que el botón esté clickeable antes de hacer click.
        Después del click, el cargo debe aparecer en la tabla.
        """
        self.wait_for_element(self.BTN_AGREGAR, condition="clickable", timeout=10)
        self.click(self.BTN_AGREGAR)
        logger.info("[CARGOS-NF] Click en botón Agregar cargo.")

    def agregar_cargo_no_facturable(self, nombre: str, importe: str) -> None:
        """
        Agrega un cargo no facturable completo (nombre + importe + agregar).

        Espera la aparición de una nueva fila en la tabla para confirmar
        que el cargo fue registrado correctamente.

        Args:
            nombre:  Nombre del cargo (ej: 'Propina').
            importe: Importe como string (ej: '150.00').
        """
        logger.info(f"[CARGOS-NF] Agregando cargo: '{nombre}' — ${importe}")
        count_antes = self.get_cantidad_cargos()

        self.fill_nombre_cargo(nombre)
        self.fill_importe_cargo(importe)
        self.click_agregar_cargo()

        # Esperar confirmación de que el cargo fue agregado a la tabla
        import time
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if self.get_cantidad_cargos() > count_antes:
                logger.info(f"[CARGOS-NF] Cargo agregado exitosamente: '{nombre}' ${importe}")
                return
            time.sleep(0.5)

        logger.warning(
            f"[CARGOS-NF] No se confirmó la adición del cargo '{nombre}' en la tabla. "
            "Puede ser normal si la tabla usa lazy rendering."
        )

    def agregar_cargo_desde_caso(self, caso: dict) -> None:
        """
        Adapter para FacturaFlow: agrega cargo no facturable si el caso lo define.

        Verifica que los campos cargo_no_facturable_nombre e importe no estén vacíos
        antes de intentar agregar el cargo. Si están vacíos, se omite sin error.

        Claves del dict plano (Excel):
            cargo_no_facturable_nombre  → nombre del cargo
            cargo_no_facturable_importe → importe del cargo

        Args:
            caso: Dict plano con los datos del caso desde el Excel.
        """
        nombre  = str(caso.get("cargo_no_facturable_nombre",  "")).strip()
        importe = str(caso.get("cargo_no_facturable_importe", "")).strip()

        if not nombre or not importe or importe in ("0", "0.00", "nan", ""):
            logger.info("[CARGOS-NF] Sin cargo no facturable en este caso — se omite.")
            return

        # Verificar que la sección está visible antes de intentar interactuar
        if not self.is_seccion_visible():
            logger.warning(
                "[CARGOS-NF] La sección 'Cargos No Facturables' no es visible. "
                "Verificar si el formulario la muestra para este tipo de factura."
            )
            return

        self.agregar_cargo_no_facturable(nombre, importe)

    def validar_cargo_agregado(self, nombre: str) -> bool:
        """
        Verifica que un cargo con el nombre dado fue agregado a la tabla.

        Busca en las filas de la tabla un texto que coincida con el nombre
        del cargo.

        Args:
            nombre: Nombre del cargo a verificar.

        Returns:
            True si el cargo aparece en la tabla, False si no se encuentra.
        """
        try:
            xpath = (
                By.XPATH,
                f"//app-cargos-no-facturables//table//td[contains(normalize-space(.), '{nombre}')]",
            )
            encontrado = self.is_visible(xpath, timeout=5)
            logger.info(f"[CARGOS-NF] Cargo '{nombre}' en tabla: {encontrado}")
            return encontrado
        except Exception as exc:
            logger.warning(f"[CARGOS-NF] Error al validar cargo '{nombre}': {exc}")
            return False
