"""
nota_credito_timbrado_flow.py - Sub-flujo de timbrado de Nota de Crédito.

Réplica de FacturaTimbradoFlow pero para el módulo de Nota de Crédito.
"""
import time

from app.core.base_flow import BaseFlow
from app.pages.common.loader_page import LoaderPage
from app.pages.nota_credito.nota_credito_resultado_page import NotaCreditoResultadoPage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NotaCreditoTimbradoFlow(BaseFlow):
    """Sub-flujo de verificación del timbrado de Nota de Crédito."""

    def run(self, **kwargs) -> dict:
        self._registrar_inicio()
        try:
            loader_page = LoaderPage(self.driver)
            resultado_page = NotaCreditoResultadoPage(self.driver)

            loader_page.wait_for_all_loaders()
            self._registrar_paso("esperar_respuesta_sat", "en_progreso")

            if resultado_page.has_error():
                error_msg = resultado_page.get_error_message()
                self._volcar_consola_browser("ERROR FRONT—timbrado NC")
                self._tomar_screenshot("nc_timbrado_error_sat")
                self._registrar_paso("verificar_timbrado", "fallido", error_msg)
                time.sleep(10)
                return self._marcar_fallido(f"Error del SAT/PAC al timbrar NC: {error_msg}")

            if not resultado_page.is_timbrado_exitoso():
                self._volcar_consola_browser("SIN EXITO—timbrado NC")
                self._tomar_screenshot("nc_timbrado_no_confirmado")
                self._registrar_paso(
                    "verificar_timbrado",
                    "fallido",
                    "El portal no confirmó el timbrado exitoso de NC.",
                )
                time.sleep(10)
                return self._marcar_fallido(
                    "El portal no confirmó el timbrado exitoso de NC."
                )

            self._registrar_paso("verificar_timbrado", "exitoso")
            self._tomar_screenshot("nc_timbrado_exitoso")

            uuid_nc = resultado_page.get_uuid_cfdi()
            self._registrar_paso(
                "capturar_uuid",
                "exitoso" if uuid_nc else "advertencia",
                uuid_nc or "UUID no visible",
            )

            if uuid_nc:
                self.context.set_dato("uuid_nota_credito", uuid_nc)
                self._guardar_resultado("uuid_nota_credito", uuid_nc)
                logger.info(f"[NC TIMBRADO FLOW] UUID registrado: {uuid_nc}")

            fecha_timbrado = resultado_page.get_fecha_timbrado()
            if fecha_timbrado:
                self._guardar_resultado("fecha_timbrado_nc", fecha_timbrado)

            return self._marcar_exitoso()

        except Exception as exc:
            logger.exception(f"[NC TIMBRADO FLOW] Error: {exc}")
            self._volcar_consola_browser("EXCEPCION—timbrado NC")
            self._tomar_screenshot("error_nc_timbrado_flow")
            time.sleep(10)
            return self._marcar_fallido(str(exc))

    def _volcar_consola_browser(self, contexto: str = "") -> None:
        try:
            logs = self.driver.get_log("browser")
            if not logs:
                logger.info(f"[CONSOLA BROWSER] ({contexto}) Sin mensajes en consola.")
                return
            for entry in logs:
                nivel  = entry.get("level", "")
                msg    = entry.get("message", "")
                source = entry.get("source", "")
                if nivel in ("WARNING", "SEVERE"):
                    logger.warning(f"[CONSOLA BROWSER] [{nivel}] ({contexto}) {source}: {msg}")
                else:
                    logger.info(f"[CONSOLA BROWSER] [{nivel}] ({contexto}) {source}: {msg}")
        except Exception as exc:
            logger.warning(f"[CONSOLA BROWSER] No se pudieron obtener logs del browser: {exc}")
