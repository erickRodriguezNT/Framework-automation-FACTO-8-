"""
adenda_page.py - Page Object del formulario de Adenda del portal FACTO.

Una Adenda es información adicional que se agrega a un CFDI fuera
de los campos estándar del SAT. Es información comercial no fiscal.

TODO: Reemplazar placeholders con selectores reales del portal.
"""
from selenium.webdriver.common.by import By

from app.core.base_page import BasePage


class AdendaPage(BasePage):
    """
    Page Object para el formulario de captura de Adenda.

    La Adenda varía según el cliente/portal receptor.
    Los campos aquí son placeholders genéricos.
    TODO: Actualizar con los campos específicos de adenda del portal FACTO.
    """

    # ------------------------------------------------------------------
    # Locators
    # TODO: Reemplazar con selectores reales del portal FACTO
    # ------------------------------------------------------------------

    # UUID del CFDI al que se agrega la adenda
    # TODO: Identificar el campo UUID de la factura base
    UUID_BASE = (By.CSS_SELECTOR, "[data-testid='uuid-base-adenda'], #uuid-base-adenda, input[name='uuidBase']")

    # Tipo de adenda (si el portal tiene múltiples tipos)
    # TODO: Identificar el selector de tipo de adenda
    TIPO_ADENDA = (By.CSS_SELECTOR, "[data-testid='tipo-adenda'], #tipo-adenda, select[name='tipoAdenda']")

    # Campo de referencia de orden de compra
    # TODO: Identificar el campo de referencia de adenda
    REFERENCIA_OC = (By.CSS_SELECTOR, "[data-testid='referencia-oc'], #referencia-oc, input[name='referenciaOC']")

    # Número de proveedor (para portales que lo requieren)
    # TODO: Identificar el campo de número de proveedor
    NUM_PROVEEDOR = (By.CSS_SELECTOR, "[data-testid='num-proveedor'], #num-proveedor, input[name='numProveedor']")

    # Campo de descripción adicional de la adenda
    # TODO: Identificar el campo de descripción/notas de adenda
    DESCRIPCION_ADENDA = (By.CSS_SELECTOR, "[data-testid='descripcion-adenda'], #descripcion-adenda, textarea[name='descripcionAdenda']")

    # Campo adicional 1 (genérico — actualizar según adenda real)
    # TODO: Identificar campos específicos de la adenda del cliente
    CAMPO_EXTRA_1 = (By.CSS_SELECTOR, "[data-testid='campo-extra-1'], #campo-extra-1, input[name='campoExtra1']")

    # Campo adicional 2 (genérico)
    # TODO: Identificar segundo campo adicional si aplica
    CAMPO_EXTRA_2 = (By.CSS_SELECTOR, "[data-testid='campo-extra-2'], #campo-extra-2, input[name='campoExtra2']")

    # Botón para adjuntar/guardar la adenda
    # TODO: Identificar el botón de guardar adenda
    BTN_GUARDAR = (By.CSS_SELECTOR, "[data-testid='btn-guardar-adenda'], #btn-guardar-adenda, button.btn-guardar-adenda")

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def fill_uuid_base(self, uuid: str) -> None:
        """Ingresa el UUID del CFDI base al que se agrega la adenda."""
        self.type_text(self.UUID_BASE, uuid)

    def select_tipo_adenda(self, tipo: str) -> None:
        """Selecciona el tipo de adenda."""
        self.select_by_visible_text(self.TIPO_ADENDA, tipo)

    def fill_referencia_oc(self, referencia: str) -> None:
        """Ingresa la referencia de orden de compra."""
        self.type_text(self.REFERENCIA_OC, referencia)

    def fill_num_proveedor(self, num: str) -> None:
        """Ingresa el número de proveedor."""
        self.type_text(self.NUM_PROVEEDOR, num)

    def fill_descripcion(self, descripcion: str) -> None:
        """Ingresa la descripción adicional de la adenda."""
        self.type_text(self.DESCRIPCION_ADENDA, descripcion)

    def fill_campo_extra(self, campo_num: int, valor: str) -> None:
        """
        Ingresa un campo extra de la adenda.

        Args:
            campo_num: Número del campo extra (1 o 2).
            valor:     Valor a ingresar.
        """
        locator = self.CAMPO_EXTRA_1 if campo_num == 1 else self.CAMPO_EXTRA_2
        self.type_text(locator, valor)

    def click_guardar(self) -> None:
        """Guarda/envía la adenda."""
        self.click(self.BTN_GUARDAR)
