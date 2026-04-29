"""
nota_credito_descarga_flow.py - Sub-flujo de descarga de archivos de Nota de Crédito timbrada.

Réplica de FacturaDescargaFlow pero para el módulo de Nota de Crédito.
"""
from app.core.base_flow import BaseFlow
from app.pages.nota_credito.nota_credito_resultado_page import NotaCreditoResultadoPage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NotaCreditoDescargaFlow(BaseFlow):
    """Sub-flujo de descarga de comprobantes de Nota de Crédito timbrada."""

    def run(self, **kwargs) -> dict:
        self._registrar_inicio()
        tipos = kwargs.get("tipos", ["pdf", "xml"])
        archivos_descargados: dict = {}

        try:
            resultado_page = NotaCreditoResultadoPage(self.driver)

            if "pdf" in tipos:
                resultado_page.click_descargar_pdf()
                self._registrar_paso("descargar_pdf_nc", "exitoso")
                archivos_descargados["pdf"] = True
                self._tomar_screenshot("nc_descarga_pdf_completada")

            if "xml" in tipos:
                resultado_page.click_descargar_xml()
                self._registrar_paso("descargar_xml_nc", "exitoso")
                archivos_descargados["xml"] = True
                self._tomar_screenshot("nc_descarga_xml_completada")

            self.context.set_dato("archivos_descargados_nc", archivos_descargados)
            self._guardar_resultado("archivos_descargados_nc", archivos_descargados)
            logger.info(f"[NC DESCARGA FLOW] Archivos descargados: {archivos_descargados}")

            return self._marcar_exitoso()

        except Exception as exc:
            logger.exception(f"[NC DESCARGA FLOW] Error: {exc}")
            self._tomar_screenshot("error_nc_descarga_flow")
            return self._marcar_fallido(str(exc))
