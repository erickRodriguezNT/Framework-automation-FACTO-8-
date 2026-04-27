"""
factura_descarga_flow.py - Sub-flujo de descarga de archivos de Factura timbrada.

Gestiona la descarga del PDF y XML de una Factura ya timbrada
y registra los archivos en el execution_context.

Se separa de FacturaFlow para:
- Pruebas aisladas de descarga
- Reutilización desde otros flujos que requieran descargar facturas
- Manejo de timeouts específicos de descarga

Uso:
    from app.flows.factura.factura_descarga_flow import FacturaDescargaFlow
    flow = FacturaDescargaFlow(driver, execution_context)
    result = flow.run(tipos=["pdf", "xml"])
"""
from app.core.base_flow import BaseFlow
from app.pages.factura.factura_resultado_page import FacturaResultadoPage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FacturaDescargaFlow(BaseFlow):
    """
    Sub-flujo de descarga de comprobantes de Factura timbrada.

    Hace click en los botones de descarga de PDF y XML en la
    pantalla de resultado del timbrado y registra los archivos
    en el execution_context.

    ⚠️  Los selectores de los botones de descarga son TODO hasta
        confirmarlos con el portal real. Ver FacturaResultadoPage.
    """

    def run(self, **kwargs) -> dict:
        """
        Descarga los archivos de la factura timbrada.

        Args:
            tipos: (list) Tipos de archivo a descargar. Default: ['pdf', 'xml'].
                   Valores válidos: 'pdf', 'xml'.

        Returns:
            Resultado estándar del BaseFlow con archivos_descargados en datos.
        """
        self._registrar_inicio()

        tipos = kwargs.get("tipos", ["pdf", "xml"])
        archivos_descargados: dict = {}

        try:
            resultado_page = FacturaResultadoPage(self.driver)

            if "pdf" in tipos:
                self.descargar_pdf(resultado_page)
                archivos_descargados["pdf"] = True
                self._tomar_screenshot("descarga_pdf_completada")

            if "xml" in tipos:
                self.descargar_xml(resultado_page)
                archivos_descargados["xml"] = True
                self._tomar_screenshot("descarga_xml_completada")

            self.registrar_archivos_en_contexto(archivos_descargados)
            self._guardar_resultado("archivos_descargados", archivos_descargados)

            return self._marcar_exitoso()

        except Exception as exc:
            logger.exception(f"[DESCARGA FLOW] Error en FacturaDescargaFlow: {exc}")
            self._tomar_screenshot("error_descarga_factura")
            return self._marcar_fallido(str(exc))

    # ------------------------------------------------------------------
    # Métodos helper de descarga
    # ------------------------------------------------------------------

    def descargar_pdf(self, resultado_page: FacturaResultadoPage) -> None:
        """
        Inicia la descarga del PDF de la factura.

        Args:
            resultado_page: Instancia de FacturaResultadoPage.

        Raises:
            Exception: Si el botón de descarga no está disponible.

        TODO: Confirmar selector data-testid="btn-descargar-pdf" con equipo frontend.
        """
        logger.info("[DESCARGA FLOW] Iniciando descarga de PDF.")
        resultado_page.click_descargar_pdf()
        self._registrar_paso("descargar_pdf", "exitoso")

    def descargar_xml(self, resultado_page: FacturaResultadoPage) -> None:
        """
        Inicia la descarga del XML de la factura.

        Args:
            resultado_page: Instancia de FacturaResultadoPage.

        Raises:
            Exception: Si el botón de descarga no está disponible.

        TODO: Confirmar selector data-testid="btn-descargar-xml" con equipo frontend.
        """
        logger.info("[DESCARGA FLOW] Iniciando descarga de XML.")
        resultado_page.click_descargar_xml()
        self._registrar_paso("descargar_xml", "exitoso")

    def validar_archivos_descargados(self, tipos: list) -> dict:
        """
        Verifica que los archivos se descargaron correctamente.

        TODO: Implementar validación real cuando se defina el directorio
              de descarga y el patrón de nombre de archivo esperado.

        Args:
            tipos: Lista de tipos verificados ['pdf', 'xml'].

        Returns:
            Diccionario con tipo → bool indicando si fue descargado.
        """
        validacion = {tipo: True for tipo in tipos}
        logger.info(f"[DESCARGA FLOW] Validación archivos: {validacion}")
        return validacion

    def registrar_archivos_en_contexto(self, archivos: dict) -> None:
        """
        Registra los archivos descargados en el execution_context.

        Los archivos quedan disponibles para cualquier step posterior
        mediante context.get_dato("archivos_descargados").

        Args:
            archivos: { "pdf": bool|str, "xml": bool|str }
        """
        self.context.set_dato("archivos_descargados", archivos)
        logger.info(f"[DESCARGA FLOW] Archivos registrados en contexto: {archivos}")
