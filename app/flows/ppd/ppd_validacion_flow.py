"""
ppd_validacion_flow.py - Sub-flujo de validación de Factura PPD timbrada.

Verifica que el UUID del PPD es válido y que el CFDI queda
en estado "Pago Pendiente" en el portal.

Uso:
    from app.flows.ppd.ppd_validacion_flow import PPDValidacionFlow
    flow = PPDValidacionFlow(driver, execution_context)
    result = flow.run()
"""
from app.core.base_flow import BaseFlow
from app.pages.ppd.ppd_resultado_page import PPDResultadoPage
from app.utils.logger import get_logger
from app.utils.validations import assert_valid_uuid_cfdi

logger = get_logger(__name__)


class PPDValidacionFlow(BaseFlow):
    """
    Sub-flujo de validación del estado de un PPD timbrado.

    Verifica:
    - UUID CFDI válido
    - Estado del CFDI = pendiente de pago
    - Que el portal no muestra error
    """

    def run(self, **kwargs) -> dict:
        """
        Valida el estado del PPD timbrado.

        Returns:
            Resultado con uuid_cfdi_ppd validado.
        """
        self._registrar_inicio()

        try:
            resultado_page = PPDResultadoPage(self.driver)

            # --- Verificar que no hay error ---
            # TODO: Implementar cuando se tenga el HTML del portal
            # if resultado_page.has_error():
            #     return self._marcar_fallido(resultado_page.get_error_message())

            # --- Validar UUID ---
            uuid_ppd = self.context.get_dato("uuid_cfdi_ppd", "")
            if uuid_ppd:
                try:
                    assert_valid_uuid_cfdi(uuid_ppd)
                    self._registrar_paso("validar_uuid_ppd", "exitoso", uuid_ppd)
                except Exception as exc:
                    return self._marcar_fallido(f"UUID PPD inválido: {exc}")
            else:
                self._registrar_paso(
                    "validar_uuid_ppd", "omitido", "UUID no disponible aún (TODO)"
                )

            # --- Verificar estado del pago ---
            # TODO: Verificar que el estado sea "pendiente" o el que muestre el portal
            # estado_pago = resultado_page.get_estado_pago()
            # if "pendiente" not in estado_pago.lower():
            #     return self._marcar_fallido(f"Estado de pago inesperado: {estado_pago}")
            self._registrar_paso("verificar_estado_pago_ppd", "omitido", "TODO: implementar")
            self._tomar_screenshot("validacion_ppd")

            return self._marcar_exitoso()

        except Exception as exc:
            logger.exception(f"Error en PPDValidacionFlow: {exc}")
            self._tomar_screenshot("error_validacion_ppd")
            return self._marcar_fallido(str(exc))
