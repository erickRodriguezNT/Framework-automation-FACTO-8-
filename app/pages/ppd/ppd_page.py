"""
ppd_page.py - Page Object del formulario de PPD (Pago en Parcialidades o Diferido).

Un CFDI PPD es una Factura con método de pago PPD.
Requiere posteriormente un Complemento de Pago cuando se recibe el pago.

TODO: Reemplazar placeholders con selectores reales del portal.
"""
from selenium.webdriver.common.by import By

from app.core.base_page import BasePage


class PPDPage(BasePage):
    """
    Page Object para el formulario de emisión de un CFDI con método de pago PPD.

    El flujo PPD es similar al de Factura pero con método de pago='PPD'.
    La diferencia funcional es que queda como 'pendiente de pago'.
    """

    # ------------------------------------------------------------------
    # Locators
    # TODO: Reemplazar con selectores reales del portal FACTO
    # ------------------------------------------------------------------

    # RFC del receptor
    # TODO: Identificar el campo RFC receptor en el formulario PPD
    RFC_RECEPTOR = (By.CSS_SELECTOR, "[data-testid='rfc-receptor-ppd'], #rfc-receptor-ppd, input[name='rfcReceptor']")

    # Nombre del receptor
    # TODO: Identificar el campo nombre del receptor
    NOMBRE_RECEPTOR = (By.CSS_SELECTOR, "[data-testid='nombre-receptor-ppd'], #nombre-receptor-ppd, input[name='nombreReceptor']")

    # Uso del CFDI
    # TODO: Identificar el selector de uso CFDI
    USO_CFDI = (By.CSS_SELECTOR, "[data-testid='uso-cfdi-ppd'], #uso-cfdi-ppd, select[name='usoCFDI']")

    # Método de pago — debe ser PPD
    # TODO: Identificar el selector de método de pago
    METODO_PAGO = (By.CSS_SELECTOR, "[data-testid='metodo-pago-ppd'], #metodo-pago-ppd, select[name='metodoPago']")

    # Forma de pago (99 = Por definir, común en PPD)
    # TODO: Identificar el selector de forma de pago
    FORMA_PAGO = (By.CSS_SELECTOR, "[data-testid='forma-pago-ppd'], #forma-pago-ppd, select[name='formaPago']")

    # Condiciones de pago (plazo)
    # TODO: Identificar el campo de condiciones de pago
    CONDICIONES_PAGO = (By.CSS_SELECTOR, "[data-testid='condiciones-pago'], #condiciones-pago, input[name='condicionesPago']")

    # Descripción del servicio / concepto
    # TODO: Identificar el campo de descripción del concepto PPD
    DESCRIPCION = (By.CSS_SELECTOR, "[data-testid='descripcion-ppd'], #descripcion-ppd, input[name='descripcion'], textarea[name='descripcion']")

    # Importe total
    # TODO: Identificar el campo de importe total
    IMPORTE = (By.CSS_SELECTOR, "[data-testid='importe-ppd'], #importe-ppd, input[name='importe']")

    # Botón de continuar
    # TODO: Identificar el botón de continuar
    BTN_CONTINUAR = (By.CSS_SELECTOR, "[data-testid='btn-continuar-ppd'], #btn-continuar-ppd, button.btn-siguiente")

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def fill_rfc_receptor(self, rfc: str) -> None:
        """Ingresa el RFC del receptor."""
        self.type_text(self.RFC_RECEPTOR, rfc)

    def fill_nombre_receptor(self, nombre: str) -> None:
        """Ingresa el nombre del receptor."""
        self.type_text(self.NOMBRE_RECEPTOR, nombre)

    def select_uso_cfdi(self, uso: str) -> None:
        """Selecciona el uso del CFDI."""
        self.select_by_visible_text(self.USO_CFDI, uso)

    def select_metodo_pago_ppd(self) -> None:
        """Selecciona PPD como método de pago."""
        # TODO: Verificar el valor exacto del <option> PPD en el portal
        self.select_by_visible_text(self.METODO_PAGO, "PPD")

    def select_forma_pago(self, forma: str) -> None:
        """Selecciona la forma de pago (normalmente '99 - Por definir' en PPD)."""
        self.select_by_visible_text(self.FORMA_PAGO, forma)

    def fill_condiciones_pago(self, condiciones: str) -> None:
        """Ingresa las condiciones de pago (ej: 'NET30')."""
        self.type_text(self.CONDICIONES_PAGO, condiciones)

    def fill_descripcion(self, descripcion: str) -> None:
        """Ingresa la descripción del servicio o concepto."""
        self.type_text(self.DESCRIPCION, descripcion)

    def fill_importe(self, importe: str) -> None:
        """Ingresa el importe total."""
        self.type_text(self.IMPORTE, importe)

    def click_continuar(self) -> None:
        """Continúa al siguiente paso."""
        self.click(self.BTN_CONTINUAR)
