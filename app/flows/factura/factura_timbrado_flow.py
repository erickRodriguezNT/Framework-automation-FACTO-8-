"""
factura_timbrado_flow.py - Sub-flujo de timbrado de una Factura.

Este sub-flujo se encarga únicamente de la verificación del timbrado:
- Esperar la respuesta del PAC/SAT
- Verificar que el timbrado fue exitoso
- Capturar el UUID CFDI generado
- Registrar el UUID en el execution_context

Se separa de FacturaFlow para permitir:
- Pruebas aisladas del proceso de timbrado
- Manejo específico de errores del SAT durante el timbrado
- Reutilización desde FacturaFlow y flujos de retry

Uso:
    from app.flows.factura.factura_timbrado_flow import FacturaTimbradoFlow
    flow = FacturaTimbradoFlow(driver, execution_context)
    result = flow.run()
"""
from app.core.base_flow import BaseFlow
from app.pages.common.loader_page import LoaderPage
from app.pages.factura.factura_resultado_page import FacturaResultadoPage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FacturaTimbradoFlow(BaseFlow):
    """
    Sub-flujo de verificación del timbrado de una Factura CFDI.

    Asume que el formulario ya fue completado y se hizo click en "TIMBRAR CFDI".
    Se encarga de esperar la respuesta del SAT, capturar el UUID y
    registrarlo en el execution_context para uso posterior.
    """

    def run(self, **kwargs) -> dict:
        """
        Espera y verifica el resultado del timbrado.

        Args:
            (ninguno requerido — el estado viene de FacturaResultadoPage)

        Returns:
            Resultado con uuid_cfdi en datos o mensaje de error del SAT.
        """
        self._registrar_inicio()

        try:
            loader_page = LoaderPage(self.driver)
            resultado_page = FacturaResultadoPage(self.driver)

            # --- Esperar a que el portal procese la respuesta del PAC/SAT ---
            loader_page.wait_for_all_loaders()
            self._registrar_paso("esperar_respuesta_sat", "en_progreso")

            if resultado_page.has_error():
                error_msg = resultado_page.get_error_message()
                self._volcar_consola_browser("ERROR FRONT—timbrado")
                self._tomar_screenshot("timbrado_error_sat")
                self._registrar_paso("verificar_timbrado", "fallido", error_msg)
                return self._marcar_fallido(f"Error del SAT/PAC al timbrar: {error_msg}")

            if not self.validar_timbrado_exitoso(resultado_page):
                self._volcar_consola_browser("SIN EXITO—timbrado")
                self._tomar_screenshot("timbrado_no_confirmado")
                self._registrar_paso(
                    "verificar_timbrado",
                    "fallido",
                    "El portal no confirmó el timbrado exitoso. "
                    "Verificar data-testid='mensaje-exito-timbrado' en portal.",
                )
                return self._marcar_fallido(
                    "El portal no confirmó el timbrado exitoso. "
                    "Posible timeout o error no identificado."
                )

            self._registrar_paso("verificar_timbrado", "exitoso")
            self._tomar_screenshot("timbrado_exitoso")

            # --- Capturar UUID ---
            uuid_cfdi = self.obtener_uuid(resultado_page)
            self._registrar_paso(
                "capturar_uuid",
                "exitoso" if uuid_cfdi else "advertencia",
                uuid_cfdi or "UUID no visible (TODO: data-testid='uuid-cfdi')",
            )

            # --- Registrar en contexto ---
            if uuid_cfdi:
                self.registrar_uuid_en_contexto(uuid_cfdi)

            # --- Capturar fecha de timbrado ---
            fecha_timbrado = resultado_page.get_fecha_timbrado()
            if fecha_timbrado:
                self._guardar_resultado("fecha_timbrado", fecha_timbrado)

            return self._marcar_exitoso()

        except Exception as exc:
            logger.exception(f"Error en FacturaTimbradoFlow: {exc}")
            self._volcar_consola_browser("EXCEPCION—timbrado")
            self._tomar_screenshot("error_timbrado_flow")
            return self._marcar_fallido(str(exc))

    # ------------------------------------------------------------------
    # Métodos helper
    # ------------------------------------------------------------------

    def _volcar_consola_browser(self, contexto: str = "") -> None:
        """
        Lee los logs de la consola del browser (nivel WARNING/SEVERE) y los
        imprime en el log de pytest para distinguir errores del front vs. del aplicativo.
        """
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

    def validar_timbrado_exitoso(self, resultado_page: FacturaResultadoPage) -> bool:
        """
        Verifica que la pantalla de resultado confirma el timbrado exitoso.

        Delega a FacturaResultadoPage.is_timbrado_exitoso() que busca
        el UUID o el mensaje de éxito del portal.

        Args:
            resultado_page: Instancia de FacturaResultadoPage.

        Returns:
            True si el timbrado fue exitoso.
        """
        exitoso = resultado_page.is_timbrado_exitoso()
        logger.info(f"[TIMBRADO FLOW] Validación timbrado exitoso: {exitoso}")
        return exitoso

    def obtener_uuid(self, resultado_page: FacturaResultadoPage) -> str:
        """
        Obtiene el UUID CFDI de la pantalla de resultado.

        Args:
            resultado_page: Instancia de FacturaResultadoPage.

        Returns:
            UUID como string (ej: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'),
            o vacío si no está disponible.
        """
        uuid = resultado_page.get_uuid_cfdi()
        logger.info(f"[TIMBRADO FLOW] UUID obtenido: {uuid!r}")
        return uuid

    def registrar_uuid_en_contexto(self, uuid: str) -> None:
        """
        Registra el UUID CFDI en el execution_context.

        El UUID queda disponible para cualquier flujo o step subsiguiente
        mediante context.get_dato("uuid_cfdi").

        Args:
            uuid: UUID CFDI timbrado.
        """
        self.context.set_dato("uuid_cfdi", uuid)
        self._guardar_resultado("uuid_cfdi", uuid)
        logger.info(f"[TIMBRADO FLOW] UUID registrado en contexto: {uuid}")


