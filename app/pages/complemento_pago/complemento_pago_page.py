"""
complemento_pago_page.py - Page Object del formulario de Complemento de Pago.

Un Complemento de Pago (CP) es un CFDI de tipo P que documenta
el pago recibido por uno o más CFDIs PPD previamente emitidos.

TODO: Reemplazar placeholders con selectores reales del portal.
"""
from selenium.webdriver.common.by import By

from app.core.base_page import BasePage


class ComplementoPagoPage(BasePage):
    """
    Page Object para el formulario de emisión del Complemento de Pago.

    DEPENDENCIA: Requiere al menos un CFDI PPD previamente timbrado
    cuyo UUID se relacionará en esta sección.
    """

    # ------------------------------------------------------------------
    # Locators - Encabezado del Complemento de Pago
    # TODO: Reemplazar con selectores reales del portal FACTO
    # ------------------------------------------------------------------

    # RFC del receptor (quien realizó el pago)
    # TODO: Identificar el campo RFC en el formulario de CP
    RFC_RECEPTOR = (By.CSS_SELECTOR, "[data-testid='rfc-receptor-cp'], #rfc-receptor-cp, input[name='rfcReceptor']")

    # Nombre del receptor
    # TODO: Identificar el campo nombre
    NOMBRE_RECEPTOR = (By.CSS_SELECTOR, "[data-testid='nombre-receptor-cp'], #nombre-receptor-cp, input[name='nombreReceptor']")

    # Fecha de pago
    # TODO: Identificar el campo de fecha de pago
    FECHA_PAGO = (By.CSS_SELECTOR, "[data-testid='fecha-pago'], #fecha-pago, input[name='fechaPago'], input[type='date']")

    # Forma de pago del complemento (ej: 03 = Transferencia electrónica)
    # TODO: Identificar el selector de forma de pago
    FORMA_PAGO = (By.CSS_SELECTOR, "[data-testid='forma-pago-cp'], #forma-pago-cp, select[name='formaPago']")

    # Moneda del pago
    # TODO: Identificar el selector de moneda
    MONEDA = (By.CSS_SELECTOR, "[data-testid='moneda-cp'], #moneda-cp, select[name='moneda']")

    # Tipo de cambio (si moneda ≠ MXN)
    # TODO: Identificar el campo de tipo de cambio
    TIPO_CAMBIO = (By.CSS_SELECTOR, "[data-testid='tipo-cambio-cp'], #tipo-cambio-cp, input[name='tipoCambio']")

    # Monto total pagado
    # TODO: Identificar el campo de monto del pago
    MONTO_PAGO = (By.CSS_SELECTOR, "[data-testid='monto-pago'], #monto-pago, input[name='montoPago']")

    # Número de operación bancaria (referencia)
    # TODO: Identificar el campo de número de operación
    NUM_OPERACION = (By.CSS_SELECTOR, "[data-testid='num-operacion'], #num-operacion, input[name='numOperacion']")

    # Botón de continuar a la sección de documentos relacionados
    # TODO: Identificar el botón de continuar
    BTN_CONTINUAR = (By.CSS_SELECTOR, "[data-testid='btn-continuar-cp'], #btn-continuar-cp, button.btn-siguiente")

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def fill_rfc_receptor(self, rfc: str) -> None:
        """Ingresa el RFC del receptor."""
        self.type_text(self.RFC_RECEPTOR, rfc)

    def fill_nombre_receptor(self, nombre: str) -> None:
        """Ingresa el nombre del receptor."""
        self.type_text(self.NOMBRE_RECEPTOR, nombre)

    def fill_fecha_pago(self, fecha: str) -> None:
        """Ingresa la fecha en que se recibió el pago."""
        self.type_text(self.FECHA_PAGO, fecha)

    def select_forma_pago(self, forma: str) -> None:
        """Selecciona la forma de pago (ej: 03 = Transferencia)."""
        self.select_by_visible_text(self.FORMA_PAGO, forma)

    def select_moneda(self, moneda: str) -> None:
        """Selecciona la moneda del pago (ej: MXN)."""
        self.select_by_visible_text(self.MONEDA, moneda)

    def fill_tipo_cambio(self, tipo_cambio: str) -> None:
        """Ingresa el tipo de cambio (si aplica)."""
        self.type_text(self.TIPO_CAMBIO, tipo_cambio)

    def fill_monto_pago(self, monto: str) -> None:
        """Ingresa el monto total del pago recibido."""
        self.type_text(self.MONTO_PAGO, monto)

    def fill_num_operacion(self, num: str) -> None:
        """Ingresa el número de operación bancaria."""
        self.type_text(self.NUM_OPERACION, num)

    def click_continuar(self) -> None:
        """Continúa a la sección de documentos relacionados (PPDs)."""
        self.click(self.BTN_CONTINUAR)
