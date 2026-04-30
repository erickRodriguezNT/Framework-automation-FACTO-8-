"""
cfdi_descarga_flow.py — Flujo común de descarga PDF/XML post-timbrado CFDI.

Compartido entre Factura, Nota de Crédito y cualquier flujo futuro.

Responsabilidades:
  1. Esperar el visor de timbrado y tomar screenshot (máx timeout_visor s)
  2. Configurar Chrome via CDP para descargar en outputs/{modulo}/{caso_id}/
     sin mostrar el diálogo "conservar/eliminar"
  3. Hacer click en Descargar PDF → esperar que el archivo aparezca en disco
  4. Validar el PDF descargado (magic bytes %PDF-, tamaño)
  5. Si el render visual falla, extraer base64 del DOM como fallback
  6. Hacer click en Descargar XML
  7. Registrar archivos en el execution_context

Uso (desde un sub-flujo específico):
    from app.flows.common.cfdi_descarga_flow import CfdiDescargaFlow
    from app.pages.factura.factura_resultado_page import FacturaResultadoPage

    class FacturaDescargaFlow(CfdiDescargaFlow):
        def _get_resultado_page(self):
            return FacturaResultadoPage(self.driver)
"""
import time
from pathlib import Path

from app.core.base_flow import BaseFlow
from app.pages.common.cfdi_pdf_page import CfdiPdfPage
from app.utils.logger import get_logger
from app.utils.pdf_validator import wait_for_pdf_download, validate_pdf_file

logger = get_logger(__name__)


class CfdiDescargaFlow(BaseFlow):
    """
    Base flow de descarga de comprobantes CFDI post-timbrado.

    Subclases concretas solo necesitan implementar `_get_resultado_page()`
    para devolver el Page Object correcto (Factura o NC).
    """

    # Tiempo máximo para que aparezca el visor (no bloquea si se agota)
    _TIMEOUT_VISOR: int = 3
    # Segundos máximos esperando que el PDF aparezca en disco tras el click
    _TIMEOUT_PDF_DOWNLOAD: int = 30

    def run(self, **kwargs) -> dict:
        """
        Descarga PDF y XML de la factura/NC ya timbrada y valida el PDF.

        Args:
            tipos: (list) Tipos a descargar. Default: ['pdf', 'xml'].

        Returns:
            Resultado estándar BaseFlow con archivos_descargados en datos.
        """
        self._registrar_inicio()
        tipos: list = kwargs.get("tipos", ["pdf", "xml"])
        archivos_descargados: dict = {}

        try:
            resultado_page = self._get_resultado_page()
            pdf_page = CfdiPdfPage(self.driver)

            # ── 1. Screenshot del visor + intento de render ───────────────
            tiene_visor = resultado_page.wait_for_visor_timbrado(
                timeout=self._TIMEOUT_VISOR
            )
            self._tomar_screenshot("visor_timbrado")
            if tiene_visor:
                logger.info("[CFDI DESCARGA] Visor timbrado capturado.")
            else:
                logger.warning(
                    "[CFDI DESCARGA] Visor no visible en %ss, se continúa la descarga.",
                    self._TIMEOUT_VISOR,
                )

            # ── 2. Obtener case_dir — PDF y XML van sueltos en él ────────
            case_dir = self._obtener_case_dir()

            # ── 3. CDP → case_dir, luego Descargar PDF ───────────────────
            self._configurar_cdp_descarga(str(case_dir))

            # ── 3. Descargar PDF ──────────────────────────────────────────
            if "pdf" in tipos:
                logger.info("[CFDI DESCARGA] Descargando PDF → %s", case_dir)
                resultado_page.click_descargar_pdf()

                # Esperar que el archivo aparezca en disco (reemplaza sleep(2))
                pdf_path = wait_for_pdf_download(
                    download_dir=str(case_dir),
                    timeout=self._TIMEOUT_PDF_DOWNLOAD,
                )
                self._tomar_screenshot("descarga_pdf_iniciada")

                if pdf_path:
                    # ── 4. Validar PDF (magic bytes + tamaño) ─────────────
                    validacion = validate_pdf_file(pdf_path)
                    archivos_descargados["pdf"] = validacion["is_valid_pdf"]
                    archivos_descargados["pdf_path"] = str(pdf_path)
                    archivos_descargados["pdf_size_bytes"] = validacion["size_bytes"]

                    if validacion["is_valid_pdf"]:
                        self._registrar_paso("descargar_pdf", "exitoso", str(pdf_path.name))
                        logger.info(
                            "[CFDI DESCARGA] PDF validado: %s (%d bytes)",
                            pdf_path.name,
                            validacion["size_bytes"],
                        )
                    else:
                        self._registrar_paso(
                            "descargar_pdf", "advertencia",
                            validacion.get("error", "PDF inválido"),
                        )
                        logger.warning(
                            "[CFDI DESCARGA] PDF descargado pero inválido: %s",
                            validacion.get("error"),
                        )
                else:
                    # ── 5. Fallback: extraer base64 del DOM ───────────────
                    logger.warning(
                        "[CFDI DESCARGA] PDF no encontrado en disco tras %ds. "
                        "Intentando extracción base64 del DOM...",
                        self._TIMEOUT_PDF_DOWNLOAD,
                    )
                    fallback_path = case_dir / "preview_cfdi.pdf"
                    saved = pdf_page.save_pdf_from_base64(fallback_path)

                    if saved:
                        archivos_descargados["pdf"] = True
                        archivos_descargados["pdf_path"] = str(saved)
                        archivos_descargados["pdf_fuente"] = "base64_dom"
                        self._registrar_paso("descargar_pdf", "exitoso_base64", str(saved.name))
                        self._tomar_screenshot("pdf_guardado_base64")
                    else:
                        archivos_descargados["pdf"] = False
                        self._registrar_paso(
                            "descargar_pdf", "fallido",
                            "PDF no descargado y base64 no disponible en el DOM",
                        )

            # ── 6. Descargar XML → case_dir (suelto) ─────────────────────
            if "xml" in tipos:
                logger.info("[CFDI DESCARGA] Descargando XML → %s", case_dir)
                self._configurar_cdp_descarga(str(case_dir))   # mismo dir que PDF
                resultado_page.click_descargar_xml()
                # XML es pequeño — espera fija breve es suficiente
                time.sleep(2)
                self._tomar_screenshot("descarga_xml_iniciada")
                self._registrar_paso("descargar_xml", "exitoso")
                archivos_descargados["xml"] = True

            # ── 7. Registrar en contexto ──────────────────────────────────
            self.context.set_dato("archivos_descargados", archivos_descargados)
            self._guardar_resultado("archivos_descargados", archivos_descargados)
            logger.info("[CFDI DESCARGA] Case dir: %s", case_dir)

            return self._marcar_exitoso()

        except Exception as exc:
            logger.exception("[CFDI DESCARGA] Error: %s", exc)
            self._tomar_screenshot("error_cfdi_descarga")
            return self._marcar_fallido(str(exc))

    # ------------------------------------------------------------------
    # Hooks para subclases
    # ------------------------------------------------------------------

    def _get_resultado_page(self):
        """
        Retorna el Page Object de la pantalla de resultado.

        Debe ser implementado por cada subclase concreta.

        Raises:
            NotImplementedError: Si la subclase no sobreescribe este método.
        """
        raise NotImplementedError(
            "CfdiDescargaFlow._get_resultado_page() debe ser implementado "
            "por la subclase concreta (FacturaDescargaFlow / NotaCreditoDescargaFlow)."
        )

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _obtener_case_dir(self) -> Path:
        """
        Retorna el directorio del caso actual como Path.

        Lee ``evidence_dir`` del contexto (seteado por el flow padre como
        ``case_dir/screenshots``). El case_dir es el padre de screenshots/.

        Si no se encontró la clave, usa la ruta legacy sin timestamp.

        Returns:
            ``Path`` absoluto al directorio del caso (padre de screenshots/).
        """
        evidence_dir = self.context.get_dato(
            "evidence_dir",
            "outputs/cfdi/RUN/screenshots",
        )
        case_dir = Path(evidence_dir).parent.resolve()
        case_dir.mkdir(parents=True, exist_ok=True)
        return case_dir

    def _configurar_cdp_descarga(self, download_dir: str) -> None:
        """
        Configura Chrome via CDP para:
          - Guardar descargas en download_dir sin preguntar
          - Aceptar archivos sin mostrar el aviso "conservar/eliminar"

        Args:
            download_dir: Ruta absoluta del directorio de destino.
        """
        try:
            self.driver.execute_cdp_cmd(
                "Page.setDownloadBehavior",
                {
                    "behavior": "allow",
                    "downloadPath": download_dir,
                },
            )
            logger.info("[CFDI DESCARGA] CDP configurado: %s", download_dir)
        except Exception as exc:
            logger.warning(
                "[CFDI DESCARGA] CDP no disponible, descarga puede pedir confirmación: %s",
                exc,
            )
