"""
factura_resultado_page.py - Page Object de la pantalla de resultado post-timbrado.

Componente: Pantalla que aparece después de hacer click en "TIMBRAR CFDI".
Muestra el UUID CFDI timbrado, datos del documento, y botones de descarga.

============================================================
ANÁLISIS DE SELECTORES — Pantalla Resultado (HTML analizado)
============================================================

HTML OBSERVADO:
  La pantalla de resultado NO está disponible en el HTML analizado.
  La vista de resultado se renderiza DESPUÉS de que el PAC/SAT timbra el CFDI.
  Esto significa que los selectores solo pueden obtenerse:
    1. Ejecutando el flujo completo en el portal real
    2. Revisando el HTML renderizado post-timbrado

  SELECTORES CONOCIDOS (del HTML de emisión):
  - Ninguno específico de la pantalla de resultado está disponible.

  PATRONES ESPERADOS (basado en portales CFDI 4.0 típicos):
  - El UUID tiene formato xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx (36 chars)
  - El portal suele mostrar un panel/card con:
    - "Timbrado exitoso" o similar
    - UUID del SAT
    - Fecha de timbrado
    - Botones de descarga PDF/XML
  - Los errores del PAC/SAT suelen aparecer en alerts o modales

DATA-TESTID RECOMENDADOS AL EQUIPO FRONTEND:
  - data-testid="pantalla-resultado"     → contenedor de la pantalla
  - data-testid="uuid-cfdi"              → span/div con UUID timbrado
  - data-testid="mensaje-exito-timbrado" → banner de éxito
  - data-testid="mensaje-error-timbrado" → banner de error con descripción
  - data-testid="btn-descargar-pdf"      → botón descarga PDF
  - data-testid="btn-descargar-xml"      → botón descarga XML
  - data-testid="btn-nueva-factura"      → botón emitir otra factura
  - data-testid="fecha-timbrado"         → fecha y hora de timbrado SAT
============================================================
"""
from selenium.webdriver.common.by import By

from app.core.base_page import BasePage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FacturaResultadoPage(BasePage):
    """
    Page Object para la pantalla de resultado del timbrado de Factura.

    Esta pantalla es la más crítica del flujo: expone el UUID CFDI
    generado por el SAT y permite la descarga de PDF y XML.

    ⚠️  Los selectores son TODO hasta ejecutar el flujo completo en el portal.
        Prioridad máxima: solicitar data-testid al equipo frontend.
    """

    # ------------------------------------------------------------------
    # Locators — Contenedor de resultado
    # TODO: solicitar al equipo frontend agregar data-testid="pantalla-resultado"
    # ------------------------------------------------------------------

    PANTALLA_RESULTADO = (
        By.CSS_SELECTOR,
        "[data-testid='pantalla-resultado']",
    )

    # ------------------------------------------------------------------
    # Locators — UUID CFDI timbrado
    # TODO: solicitar al equipo frontend agregar data-testid="uuid-cfdi"
    # ------------------------------------------------------------------

    UUID_CFDI = (
        By.CSS_SELECTOR,
        "[data-testid='uuid-cfdi'], "
        ".uuid-value, "
        "span.folio-fiscal",
    )

    # ------------------------------------------------------------------
    # Locators — Mensaje de éxito
    # TODO: solicitar al equipo frontend agregar data-testid="mensaje-exito-timbrado"
    # ------------------------------------------------------------------

    MENSAJE_EXITO = (
        By.XPATH,
        "//*[@data-testid='mensaje-exito-timbrado' "
        "or contains(@class,'success-message') "
        "or contains(@class,'alert-success') "
        "or contains(normalize-space(.), 'Timbrado exitoso') "
        "or contains(normalize-space(.), 'timbrado exitosamente')]",
    )

    # ------------------------------------------------------------------
    # Locators — Mensaje de error de timbrado
    # TODO: solicitar al equipo frontend agregar data-testid="mensaje-error-timbrado"
    # ------------------------------------------------------------------

    MENSAJE_ERROR = (
        By.XPATH,
        "//*[contains(normalize-space(.), 'Error al generar la factura') "
        "or contains(normalize-space(.), 'Error al timbrar') "
        "or contains(normalize-space(.), 'Error del PAC') "
        "or @data-testid='mensaje-error-timbrado' "
        "or contains(@class,'error-message') "
        "or contains(@class,'alert-danger') "
        "or contains(@class,'toast-error')]",
    )

    # ------------------------------------------------------------------
    # Locators — Fecha de timbrado
    # TODO: solicitar al equipo frontend agregar data-testid="fecha-timbrado"
    # ------------------------------------------------------------------

    FECHA_TIMBRADO = (
        By.CSS_SELECTOR,
        "[data-testid='fecha-timbrado']",
    )

    # ------------------------------------------------------------------
    # Locators — Descarga de documentos
    # TODO: solicitar al equipo frontend agregar data-testid="btn-descargar-pdf" y "btn-descargar-xml"
    # ------------------------------------------------------------------

    BTN_DESCARGAR_PDF = (
        By.CSS_SELECTOR,
        "[data-testid='btn-descargar-pdf'], "
        "button[aria-label*='PDF'], "
        "a[href*='.pdf']",
    )

    BTN_DESCARGAR_XML = (
        By.CSS_SELECTOR,
        "[data-testid='btn-descargar-xml'], "
        "button[aria-label*='XML'], "
        "a[href*='.xml']",
    )

    # Botón para emitir otra factura
    # TODO: solicitar al equipo frontend agregar data-testid="btn-nueva-factura"
    BTN_NUEVA_FACTURA = (
        By.CSS_SELECTOR,
        "[data-testid='btn-nueva-factura']",
    )

    # ------------------------------------------------------------------
    # Verificaciones de estado
    # ------------------------------------------------------------------

    def is_timbrado_exitoso(self) -> bool:
        """
        Verifica si el timbrado fue exitoso.

        Comprueba la presencia del UUID o del mensaje de éxito.
        El timeout es mayor para dar tiempo al PAC/SAT de responder.

        Returns:
            True si el timbrado fue exitoso.
        """
        tiene_uuid = self.is_visible(self.UUID_CFDI, timeout=30)
        tiene_exito = self.is_visible(self.MENSAJE_EXITO, timeout=5)
        resultado = tiene_uuid or tiene_exito
        logger.info(f"[RESULTADO] Timbrado exitoso: {resultado}")
        return resultado

    def has_error(self) -> bool:
        """
        Verifica si hay un mensaje de error de timbrado.

        Returns:
            True si se muestra un error del PAC/SAT.
        """
        return self.is_visible(self.MENSAJE_ERROR, timeout=5)

    def get_uuid_cfdi(self) -> str:
        """
        Obtiene el UUID CFDI generado por el SAT.

        Returns:
            UUID como string (ej: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'),
            o vacío si no está visible.
        """
        try:
            uuid = self.get_text(self.UUID_CFDI).strip()
            logger.info(f"[RESULTADO] UUID CFDI: {uuid}")
            return uuid
        except Exception:
            logger.warning("[RESULTADO] No se pudo obtener el UUID CFDI.")
            return ""

    def get_error_message(self) -> str:
        """
        Obtiene el mensaje de error si el timbrado falló.

        Returns:
            Texto del error, o vacío si no hay error.
        """
        if self.has_error():
            return self.get_text(self.MENSAJE_ERROR).strip()
        return ""

    def get_fecha_timbrado(self) -> str:
        """
        Obtiene la fecha de timbrado del documento.

        Returns:
            Texto de la fecha, o vacío si no aplica.
        """
        try:
            return self.get_text(self.FECHA_TIMBRADO).strip()
        except Exception:
            return ""

    # ------------------------------------------------------------------
    # Acciones — Descarga
    # ------------------------------------------------------------------

    def click_descargar_pdf(self) -> None:
        """Inicia la descarga del PDF de la factura timbrada."""
        self.click(self.BTN_DESCARGAR_PDF)
        logger.info("[RESULTADO] Click en Descargar PDF.")

    def click_descargar_xml(self) -> None:
        """Inicia la descarga del XML de la factura timbrada."""
        self.click(self.BTN_DESCARGAR_XML)
        logger.info("[RESULTADO] Click en Descargar XML.")

    def click_nueva_factura(self) -> None:
        """Navega a la pantalla de nueva factura / emitir otra."""
        self.click(self.BTN_NUEVA_FACTURA)
        logger.info("[RESULTADO] Click en Nueva Factura.")
