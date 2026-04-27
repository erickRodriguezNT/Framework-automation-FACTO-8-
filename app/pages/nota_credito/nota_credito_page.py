"""
nota_credito_page.py - Page Object del formulario de Nota de Crédito.

Responsabilidades:
- Captura de datos de la nota de crédito
- Relación con la factura original (CFDI relacionado)
- Motivo de la nota de crédito

TODO: Reemplazar placeholders con selectores reales del portal.
"""
from selenium.webdriver.common.by import By

from app.core.base_page import BasePage


class NotaCreditoPage(BasePage):
    """
    Page Object para el formulario de emisión de Nota de Crédito.

    Una nota de crédito es un CFDI de tipo E (Egreso) relacionado
    con una factura (CFDI de tipo I).
    """

    # ------------------------------------------------------------------
    # Locators
    # TODO: Reemplazar con selectores reales del portal FACTO
    # ------------------------------------------------------------------

    # UUID del CFDI relacionado (factura original)
    # TODO: Identificar el campo para el UUID de la factura relacionada
    UUID_RELACIONADO = (By.CSS_SELECTOR, "[data-testid='uuid-relacionado'], #uuid-relacionado, input[name='uuidRelacionado']")

    # Tipo de relación (01 = Nota de crédito de los documentos relacionados)
    # TODO: Identificar el selector de tipo de relación
    TIPO_RELACION = (By.CSS_SELECTOR, "[data-testid='tipo-relacion'], #tipo-relacion, select[name='tipoRelacion']")

    # RFC del receptor
    # TODO: Identificar el campo RFC receptor en el formulario de NC
    RFC_RECEPTOR = (By.CSS_SELECTOR, "[data-testid='rfc-receptor-nc'], #rfc-receptor-nc, input[name='rfcReceptor']")

    # Nombre del receptor
    # TODO: Identificar el campo nombre del receptor
    NOMBRE_RECEPTOR = (By.CSS_SELECTOR, "[data-testid='nombre-receptor-nc'], #nombre-receptor-nc, input[name='nombreReceptor']")

    # Uso del CFDI de egreso
    # TODO: Identificar el selector de uso CFDI para nota de crédito
    USO_CFDI = (By.CSS_SELECTOR, "[data-testid='uso-cfdi-nc'], #uso-cfdi-nc, select[name='usoCFDI']")

    # Motivo de la nota de crédito
    # TODO: Identificar el campo de motivo o descripción
    MOTIVO = (By.CSS_SELECTOR, "[data-testid='motivo-nc'], #motivo-nc, textarea[name='motivo'], input[name='motivo']")

    # Importe de la nota de crédito
    # TODO: Identificar el campo de importe
    IMPORTE = (By.CSS_SELECTOR, "[data-testid='importe-nc'], #importe-nc, input[name='importe']")

    # Botón de continuar
    # TODO: Identificar el botón de continuar
    BTN_CONTINUAR = (By.CSS_SELECTOR, "[data-testid='btn-continuar-nc'], #btn-continuar-nc, button.btn-siguiente")

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def fill_uuid_relacionado(self, uuid: str) -> None:
        """Ingresa el UUID del CFDI relacionado (factura original)."""
        self.type_text(self.UUID_RELACIONADO, uuid)

    def select_tipo_relacion(self, tipo: str) -> None:
        """Selecciona el tipo de relación entre documentos."""
        # TODO: Verificar los valores disponibles en el catálogo del portal
        self.select_by_visible_text(self.TIPO_RELACION, tipo)

    def fill_rfc_receptor(self, rfc: str) -> None:
        """Ingresa el RFC del receptor."""
        self.type_text(self.RFC_RECEPTOR, rfc)

    def fill_nombre_receptor(self, nombre: str) -> None:
        """Ingresa el nombre del receptor."""
        self.type_text(self.NOMBRE_RECEPTOR, nombre)

    def select_uso_cfdi(self, uso: str) -> None:
        """Selecciona el uso del CFDI."""
        self.select_by_visible_text(self.USO_CFDI, uso)

    def fill_motivo(self, motivo: str) -> None:
        """Ingresa el motivo de la nota de crédito."""
        self.type_text(self.MOTIVO, motivo)

    def fill_importe(self, importe: str) -> None:
        """Ingresa el importe de la nota de crédito."""
        self.type_text(self.IMPORTE, importe)

    def click_continuar(self) -> None:
        """Continúa al siguiente paso."""
        self.click(self.BTN_CONTINUAR)
