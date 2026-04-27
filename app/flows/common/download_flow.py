"""
download_flow.py - Flujo de descarga de archivos del portal FACTO.

Encapsula la lógica completa de descarga de archivos:
1. Hacer click en el botón de descarga
2. Esperar a que la descarga se complete
3. Verificar que el archivo descargado es correcto
4. Registrar el archivo en el execution_context

Uso:
    from app.flows.common.download_flow import DownloadFlow
    flow = DownloadFlow(driver, execution_context)
    result = flow.run(tipo="pdf", download_dir="outputs")
"""
from pathlib import Path

from app.core.base_flow import BaseFlow
from app.pages.common.download_page import DownloadPage
from app.utils.logger import get_logger
from app.utils.waits import wait_for_download_complete

logger = get_logger(__name__)


class DownloadFlow(BaseFlow):
    """
    Flow de descarga de archivos (PDF, XML) del portal FACTO.

    Gestiona la descarga de comprobantes y verifica que los
    archivos llegaron correctamente al directorio de output.
    """

    def run(self, **kwargs) -> dict:
        """
        Ejecuta el flujo de descarga de un archivo.

        Args:
            tipo:         (str) Tipo de archivo: 'pdf', 'xml', 'zip'.
            download_dir: (str) Directorio donde se guarda la descarga.
                          Por defecto: la ruta de output del contexto.
            pattern:      (str) Patrón del nombre del archivo esperado (opcional).
            timeout:      (int) Timeout de descarga en segundos. Default: 60.

        Returns:
            Resultado del flow con la ruta del archivo descargado.
        """
        self._registrar_inicio()

        tipo = kwargs.get("tipo", "pdf")
        download_dir = kwargs.get("download_dir", str(self.context.output_dir))
        pattern = kwargs.get("pattern", "")
        timeout = kwargs.get("timeout", 60)

        try:
            download_page = DownloadPage(self.driver)

            # --- Paso 1: Click en el botón de descarga ---
            if tipo == "pdf":
                if not download_page.is_pdf_available():
                    return self._marcar_fallido("Botón de descarga PDF no disponible en la página actual.")
                download_page.click_download_pdf()

            elif tipo == "xml":
                if not download_page.is_xml_available():
                    return self._marcar_fallido("Botón de descarga XML no disponible en la página actual.")
                download_page.click_download_xml()

            elif tipo == "zip":
                download_page.click_download_zip()

            else:
                return self._marcar_fallido(f"Tipo de descarga '{tipo}' no reconocido. Opciones: pdf, xml, zip")

            self._registrar_paso(f"click_download_{tipo}", "exitoso")
            logger.info(f"Iniciada descarga de {tipo.upper()}")

            # --- Paso 2: Esperar descarga completa ---
            # TODO: Ajustar el patrón según los nombres reales de archivos del portal
            archivo = wait_for_download_complete(
                download_dir=download_dir,
                filename_pattern=pattern or f".{tipo}",
                timeout=timeout,
            )

            self._registrar_paso(f"verificar_descarga_{tipo}", "exitoso", str(archivo))

            # --- Paso 3: Registrar el archivo en el contexto ---
            self.context.registrar_archivo(tipo, archivo)
            self._guardar_resultado(f"archivo_{tipo}", str(archivo))

            logger.info(f"Descarga completada: {archivo}")
            return self._marcar_exitoso()

        except Exception as exc:
            logger.exception(f"Error en DownloadFlow ({tipo}): {exc}")
            self._tomar_screenshot(f"error_download_{tipo}")
            return self._marcar_fallido(str(exc))
