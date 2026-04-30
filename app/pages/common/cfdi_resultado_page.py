"""
cfdi_resultado_page.py - Base Page Object para la pantalla de resultado post-timbrado.

Compartido entre FacturaResultadoPage y NotaCreditoResultadoPage.
Contiene todos los locators y métodos comunes.
"""
from selenium.webdriver.common.by import By

from app.core.base_page import BasePage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CfdiResultadoPage(BasePage):
    """
    Base Page Object para la pantalla de resultado del timbrado CFDI.

    Compartido entre módulos Factura y Nota de Crédito.
    Contiene UUID, detección de éxito/error y botones de descarga.
    """

    PANTALLA_RESULTADO = (
        By.CSS_SELECTOR,
        "[data-testid='pantalla-resultado']",
    )

    UUID_CFDI = (
        By.CSS_SELECTOR,
        "[data-testid='uuid-cfdi'], "
        ".uuid-value, "
        "span.folio-fiscal",
    )

    MENSAJE_EXITO = (
        By.XPATH,
        "//*[@data-testid='mensaje-exito-timbrado' "
        "or contains(@class,'success-message') "
        "or contains(@class,'alert-success') "
        "or contains(normalize-space(.), 'Timbrado exitoso') "
        "or contains(normalize-space(.), 'timbrado exitosamente')]",
    )

    # Versión mejorada: usa "and not(.//*[...])" para capturar solo el elemento más
    # interno que contiene el texto de error, evitando devolver todo el HTML de la página.
    MENSAJE_ERROR = (
        By.XPATH,
        "//*["
        "(@data-testid='mensaje-error-timbrado' "
        "or contains(@class,'error-message') "
        "or contains(@class,'alert-danger') "
        "or contains(@class,'toast-error') "
        "or (contains(normalize-space(.), 'Error al generar la factura') "
        "    and not(.//*[contains(normalize-space(.), 'Error al generar la factura')])) "
        "or (contains(normalize-space(.), 'Error al timbrar') "
        "    and not(.//*[contains(normalize-space(.), 'Error al timbrar')])) "
        "or (contains(normalize-space(.), 'Error del PAC') "
        "    and not(.//*[contains(normalize-space(.), 'Error del PAC')]))"
        ")]",
    )

    FECHA_TIMBRADO = (
        By.CSS_SELECTOR,
        "[data-testid='fecha-timbrado']",
    )

    # Visor post-timbrado compartido entre Factura y NC
    PANTALLA_VISOR = (
        By.CSS_SELECTOR,
        "app-factura-timbrada",
    )

    # Botones de descarga reales del portal (dentro de app-factura-timbrada)
    BTN_DESCARGAR_PDF = (
        By.CSS_SELECTOR,
        "app-factura-timbrada div.flex.flex-col.gap-4.w-full button:nth-child(1)",
    )

    BTN_DESCARGAR_XML = (
        By.CSS_SELECTOR,
        "app-factura-timbrada div.flex.flex-col.gap-4.w-full button:nth-child(2)",
    )

    BTN_NUEVA_FACTURA = (
        By.CSS_SELECTOR,
        "[data-testid='btn-nueva-factura']",
    )

    # ------------------------------------------------------------------
    # Verificaciones de estado
    # ------------------------------------------------------------------

    def wait_for_visor_timbrado(self, timeout: int = 3) -> bool:
        """
        Espera a que aparezca el visor de timbrado (app-factura-timbrada).

        No lanza excepción si no aparece; retorna False para que el flow
        pueda continuar igual.

        Args:
            timeout: Segundos máximos de espera (default 3).

        Returns:
            True si el visor se hizo visible, False si se agotó el tiempo.
        """
        visible = self.is_visible(self.PANTALLA_VISOR, timeout=timeout)
        logger.info("[RESULTADO] Visor timbrado visible: %s (timeout=%ss)", visible, timeout)
        return visible

    def is_timbrado_exitoso(self) -> bool:
        # Primero intenta detectar el visor real del portal (hasta 30 s)
        if self.is_visible(self.PANTALLA_VISOR, timeout=30):
            logger.info("[RESULTADO] Timbrado exitoso: visor app-factura-timbrada visible.")
            return True
        # Fallback: UUID o mensaje de éxito genérico
        tiene_uuid = self.is_visible(self.UUID_CFDI, timeout=5)
        tiene_exito = self.is_visible(self.MENSAJE_EXITO, timeout=5)
        resultado = tiene_uuid or tiene_exito
        logger.info("[RESULTADO] Timbrado exitoso (fallback): %s", resultado)
        return resultado

    def has_error(self) -> bool:
        return self.is_visible(self.MENSAJE_ERROR, timeout=5)

    def get_uuid_cfdi(self, timeout: int = 2) -> str:
        try:
            uuid = self.get_text(self.UUID_CFDI, timeout=timeout).strip()
            logger.info(f"[RESULTADO] UUID CFDI: {uuid}")
            return uuid
        except Exception:
            logger.warning("[RESULTADO] No se pudo obtener el UUID CFDI.")
            return ""

    def get_error_message(self) -> str:
        if not self.has_error():
            return ""
        try:
            el = self.driver.find_element(*self.MENSAJE_ERROR)
            full_text = (el.text or "").strip()
            # Retorna sólo la primera línea que empieza con "Error" para evitar
            # capturar todo el texto de la página si el locator coincidió con un padre.
            for line in full_text.splitlines():
                line = line.strip()
                if line.lower().startswith("error"):
                    return line
            return full_text.splitlines()[0] if full_text else ""
        except Exception:
            return ""

    def get_fecha_timbrado(self, timeout: int = 2) -> str:
        try:
            return self.get_text(self.FECHA_TIMBRADO, timeout=timeout).strip()
        except Exception:
            return ""

    # ------------------------------------------------------------------
    # Acciones — Descarga
    # ------------------------------------------------------------------

    def click_descargar_pdf(self) -> None:
        self.click(self.BTN_DESCARGAR_PDF)
        logger.info("[RESULTADO] Click en Descargar PDF.")

    def click_descargar_xml(self) -> None:
        self.click(self.BTN_DESCARGAR_XML)
        logger.info("[RESULTADO] Click en Descargar XML.")

    def click_nueva_factura(self) -> None:
        self.click(self.BTN_NUEVA_FACTURA)
        logger.info("[RESULTADO] Click en Nueva Factura.")
