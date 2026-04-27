"""
menu_page.py - Page Object del menú de navegación principal del portal FACTO.

Responsabilidades:
- Acceder a los módulos del portal (Factura, Nota de Crédito, PPD, etc.)
- Navegar entre secciones del menú
- Verificar disponibilidad de opciones del menú

TODO: Reemplazar todos los placeholders con selectores reales del portal.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from app.core.base_page import BasePage


class MenuPage(BasePage):
    """
    Page Object para el menú de navegación principal del portal FACTO.

    Centraliza todos los puntos de entrada a módulos del portal.

    El portal usa un sidebar con un botón "Emitir CFDI" que abre un
    dropdown con las opciones de tipo de CFDI (Factura, Nota de Crédito,
    Pago, Traslado, Cartaporte). La navegación es siempre de dos pasos:
      1. Click en EMITIR_CFDI_BTN
      2. Click en la opción del dropdown
    """

    # ------------------------------------------------------------------
    # Locators - Confirmados por inspección DOM (2026-04-24)
    # ------------------------------------------------------------------

    # Sidebar: contenedor principal del menú
    MENU_CONTAINER = (By.CSS_SELECTOR, "aside[aria-label='Navegación principal']")

    # Botón "Emitir CFDI" (azul, parte inferior del sidebar)
    # Abre el dropdown de tipo de CFDI
    EMITIR_CFDI_BTN = (By.XPATH, "//button[.//span[normalize-space(text())='Emitir CFDI']]")

    # Opciones del dropdown "TIPO DE CFDI" (visibles solo tras abrir el dropdown)
    MENU_FACTURA        = (By.XPATH, "//button[.//span[normalize-space(text())='Factura']]")
    MENU_NOTA_CREDITO   = (By.XPATH, "//button[.//span[normalize-space(text())='Nota de Crédito']]")
    MENU_PPD            = (By.XPATH, "//button[.//span[normalize-space(text())='Pago']]")
    MENU_COMPLEMENTO_PAGO = (By.XPATH, "//button[.//span[normalize-space(text())='Pago']]")
    MENU_ADENDA         = (By.XPATH, "//button[.//span[normalize-space(text())='Adenda']]")

    # ------------------------------------------------------------------
    # Acciones internas
    # ------------------------------------------------------------------

    def _open_emitir_cfdi_dropdown(self) -> None:
        """Abre el dropdown de tipo de CFDI haciendo click en 'Emitir CFDI'."""
        self.click(self.EMITIR_CFDI_BTN)
        # Esperar que el dropdown sea visible (opción Factura aparece)
        self.wait_for_element(self.MENU_FACTURA, condition="visible", timeout=5)

    # ------------------------------------------------------------------
    # Acciones de navegación (dos pasos: abrir dropdown + seleccionar)
    # ------------------------------------------------------------------

    def navigate_to_factura(self) -> None:
        """Navega al módulo de Factura desde el menú."""
        self._open_emitir_cfdi_dropdown()
        self.click(self.MENU_FACTURA)

    def navigate_to_nota_credito(self) -> None:
        """Navega al módulo de Nota de Crédito desde el menú."""
        self._open_emitir_cfdi_dropdown()
        self.click(self.MENU_NOTA_CREDITO)

    def navigate_to_ppd(self) -> None:
        """Navega al módulo de PPD desde el menú."""
        self._open_emitir_cfdi_dropdown()
        self.click(self.MENU_PPD)

    def navigate_to_complemento_pago(self) -> None:
        """Navega al módulo de Complemento de Pago desde el menú."""
        self._open_emitir_cfdi_dropdown()
        self.click(self.MENU_COMPLEMENTO_PAGO)

    def navigate_to_adenda(self) -> None:
        """Navega al módulo de Adenda desde el menú."""
        self._open_emitir_cfdi_dropdown()
        self.click(self.MENU_ADENDA)

    # ------------------------------------------------------------------
    # Verificaciones
    # ------------------------------------------------------------------

    def is_menu_visible(self) -> bool:
        """Verifica si el sidebar de navegación está visible."""
        return self.is_visible(self.MENU_CONTAINER, timeout=30)

    def is_factura_available(self) -> bool:
        """Verifica si la opción de Factura está disponible en el dropdown."""
        return self.is_present(self.MENU_FACTURA, timeout=3)

    def is_complemento_pago_available(self) -> bool:
        """Verifica si la opción de Complemento de Pago está disponible."""
        return self.is_present(self.MENU_COMPLEMENTO_PAGO, timeout=3)
