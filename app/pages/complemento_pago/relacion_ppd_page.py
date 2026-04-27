"""
relacion_ppd_page.py - Page Object para relacionar documentos PPD en el Complemento de Pago.

Esta pantalla permite vincular uno o más CFDIs PPD con el Complemento de Pago
que se está generando, indicando el importe pagado por cada uno.

TODO: Reemplazar placeholders con selectores reales del portal.
"""
from selenium.webdriver.common.by import By

from app.core.base_page import BasePage


class RelacionPPDPage(BasePage):
    """
    Page Object para la sección de relación de documentos PPD
    dentro del formulario de Complemento de Pago.
    """

    # ------------------------------------------------------------------
    # Locators - Relación de CFDIs PPD
    # TODO: Reemplazar con selectores reales del portal FACTO
    # ------------------------------------------------------------------

    # Botón para agregar un documento PPD relacionado
    # TODO: Identificar el botón de agregar documento relacionado
    BTN_AGREGAR_DOCUMENTO = (By.CSS_SELECTOR, "[data-testid='btn-agregar-doc-ppd'], #btn-agregar-doc-ppd, .btn-add-ppd")

    # Campo de UUID del documento PPD relacionado
    # TODO: Identificar el campo UUID del documento PPD a relacionar
    UUID_DOCUMENTO_PPD = (By.CSS_SELECTOR, "[data-testid='uuid-doc-ppd'], #uuid-doc-ppd, input[name='uuidDocumento']")

    # Número de parcialidad (1, 2, 3... para pagos parciales)
    # TODO: Identificar el campo de número de parcialidad
    NUM_PARCIALIDAD = (By.CSS_SELECTOR, "[data-testid='num-parcialidad'], #num-parcialidad, input[name='numParcialidad']")

    # Importe saldo anterior (saldo antes de este pago)
    # TODO: Identificar el campo de saldo anterior
    IMPORTE_SALDO_ANT = (By.CSS_SELECTOR, "[data-testid='importe-saldo-ant'], #importe-saldo-ant, input[name='importeSaldoAnt']")

    # Importe pagado en este Complemento
    # TODO: Identificar el campo de importe pagado
    IMPORTE_PAGADO = (By.CSS_SELECTOR, "[data-testid='importe-pagado'], #importe-pagado, input[name='importePagado']")

    # Importe saldo insoluto (saldo restante después del pago)
    # TODO: Identificar el campo de saldo insoluto (puede ser calculado automáticamente)
    IMPORTE_SALDO_INSOLUTO = (By.CSS_SELECTOR, "[data-testid='importe-saldo-ins'], #importe-saldo-ins, input[name='importeSaldoInsoluto']")

    # Moneda del documento relacionado
    # TODO: Identificar el selector de moneda del documento relacionado
    MONEDA_DR = (By.CSS_SELECTOR, "[data-testid='moneda-dr'], #moneda-dr, select[name='monedaDR']")

    # Tabla de documentos relacionados agregados
    # TODO: Identificar la tabla de documentos relacionados
    TABLA_DOCUMENTOS = (By.CSS_SELECTOR, "[data-testid='tabla-docs-ppd'], #tabla-docs-ppd, .tabla-relacionados, table.ppd-docs-table")

    # Botón guardar documento relacionado
    # TODO: Identificar el botón de guardar el documento relacionado
    BTN_GUARDAR_DOCUMENTO = (By.CSS_SELECTOR, "[data-testid='btn-guardar-doc'], #btn-guardar-doc, .btn-save-doc")

    # Botón de continuar a la siguiente sección
    # TODO: Identificar el botón de continuar
    BTN_CONTINUAR = (By.CSS_SELECTOR, "[data-testid='btn-continuar-relacion'], #btn-continuar-relacion, button.btn-siguiente")

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def click_agregar_documento(self) -> None:
        """Abre el formulario para agregar un documento PPD relacionado."""
        self.click(self.BTN_AGREGAR_DOCUMENTO)

    def fill_uuid_documento_ppd(self, uuid: str) -> None:
        """Ingresa el UUID del CFDI PPD a relacionar."""
        self.type_text(self.UUID_DOCUMENTO_PPD, uuid)

    def fill_num_parcialidad(self, numero: str) -> None:
        """Ingresa el número de parcialidad."""
        self.type_text(self.NUM_PARCIALIDAD, numero)

    def fill_importe_saldo_anterior(self, importe: str) -> None:
        """Ingresa el importe del saldo anterior del documento."""
        self.type_text(self.IMPORTE_SALDO_ANT, importe)

    def fill_importe_pagado(self, importe: str) -> None:
        """Ingresa el importe pagado en este Complemento."""
        self.type_text(self.IMPORTE_PAGADO, importe)

    def select_moneda_dr(self, moneda: str) -> None:
        """Selecciona la moneda del documento relacionado."""
        self.select_by_visible_text(self.MONEDA_DR, moneda)

    def click_guardar_documento(self) -> None:
        """Guarda el documento relacionado en la tabla."""
        self.click(self.BTN_GUARDAR_DOCUMENTO)

    def click_continuar(self) -> None:
        """Continúa a la siguiente sección del formulario."""
        self.click(self.BTN_CONTINUAR)

    def has_at_least_one_documento(self) -> bool:
        """Verifica que haya al menos un documento PPD relacionado."""
        return self.is_present(self.TABLA_DOCUMENTOS, timeout=3)
