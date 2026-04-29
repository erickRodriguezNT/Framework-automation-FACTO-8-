"""
nota_credito_cargos_no_facturables_page.py - Page Object para Cargos No Facturables de Nota de Crédito.

Réplica exacta de FacturaCargosNoFacturablesPage pero aislada en el módulo de NC.
Componente HTML: <app-cargos-no-facturables>
"""
import time

from selenium.webdriver.common.by import By

from app.core.base_page import BasePage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NotaCreditoCargosNoFacturablesPage(BasePage):
    """
    Page Object para la sección "Cargos No Facturables" del formulario de Nota de Crédito.
    """

    CARGO_NOMBRE = (
        By.CSS_SELECTOR,
        "[data-testid='input-cargo-nombre'], "
        "app-cargos-no-facturables input[formcontrolname='cargo'], "
        "input[formcontrolname='cargo']",
    )

    CARGO_IMPORTE = (
        By.CSS_SELECTOR,
        "[data-testid='input-cargo-importe'], "
        "app-cargos-no-facturables input[formcontrolname='importe']",
    )

    BTN_AGREGAR = (
        By.CSS_SELECTOR,
        "[data-testid='btn-agregar-cargo'], "
        "app-cargos-no-facturables button[type='submit']",
    )

    CONTENEDOR_CARGOS = (By.CSS_SELECTOR, "app-cargos-no-facturables")
    TABLA_CARGOS = (By.CSS_SELECTOR, "[data-testid='tabla-cargos'], app-cargos-no-facturables table")
    FILAS_CARGOS = (By.CSS_SELECTOR, "[data-testid='cargo-row'], app-cargos-no-facturables table tbody tr")

    def is_seccion_visible(self) -> bool:
        return self.is_visible(self.CONTENEDOR_CARGOS, timeout=5)

    def get_cantidad_cargos(self) -> int:
        try:
            filas = self.wait_for_elements(self.FILAS_CARGOS, timeout=5)
            return len(filas)
        except Exception:
            return 0

    def fill_nombre_cargo(self, nombre: str) -> None:
        self.type_text(self.CARGO_NOMBRE, nombre, clear_first=True)
        logger.info(f"[NC CARGOS-NF] Nombre de cargo: '{nombre}'")

    def fill_importe_cargo(self, importe: str) -> None:
        self.type_text(self.CARGO_IMPORTE, importe, clear_first=True)
        logger.info(f"[NC CARGOS-NF] Importe del cargo: '{importe}'")

    def click_agregar_cargo(self) -> None:
        self.wait_for_element(self.BTN_AGREGAR, condition="clickable", timeout=10)
        self.click(self.BTN_AGREGAR)
        logger.info("[NC CARGOS-NF] Click en botón Agregar cargo.")

    def agregar_cargo_no_facturable(self, nombre: str, importe: str) -> None:
        logger.info(f"[NC CARGOS-NF] Agregando cargo: '{nombre}' — ${importe}")
        count_antes = self.get_cantidad_cargos()
        self.fill_nombre_cargo(nombre)
        self.fill_importe_cargo(importe)
        self.click_agregar_cargo()
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if self.get_cantidad_cargos() > count_antes:
                logger.info(f"[NC CARGOS-NF] Cargo agregado exitosamente: '{nombre}' ${importe}")
                return
            time.sleep(0.5)
        logger.warning(f"[NC CARGOS-NF] No se confirmó la adición del cargo '{nombre}' en la tabla.")

    def agregar_cargo_desde_caso(self, caso: dict) -> None:
        nombre = str(caso.get("cargo_no_facturable_nombre", "")).strip()
        importe = str(caso.get("cargo_no_facturable_importe", "")).strip()
        if not nombre or not importe:
            logger.info("[NC CARGOS-NF] Sin cargo no facturable definido en el caso — se omite.")
            return
        if not self.is_seccion_visible():
            logger.warning("[NC CARGOS-NF] Sección de cargos no facturables no visible — se omite.")
            return
        self.agregar_cargo_no_facturable(nombre, importe)
