"""
complemento_pago_validacion_flow.py - Sub-flujo de validación de Complemento de Pago.

Verifica que el Complemento de Pago fue timbrado correctamente
y que el UUID es válido.

Uso:
    from app.flows.complemento_pago.complemento_pago_validacion_flow import ComplementoPagoValidacionFlow
    flow = ComplementoPagoValidacionFlow(driver, execution_context)
    result = flow.run()
"""
from app.core.base_flow import BaseFlow
from app.pages.complemento_pago.complemento_pago_resultado_page import (
    ComplementoPagoResultadoPage,
)
from app.utils.logger import get_logger
from app.utils.validations import assert_valid_uuid_cfdi

logger = get_logger(__name__)


class ComplementoPagoValidacionFlow(BaseFlow):
    """
    Sub-flujo de validación del Complemento de Pago timbrado.
    """

    def run(self, **kwargs) -> dict:
        """
        Valida el resultado del Complemento de Pago.

        Returns:
            Resultado con UUID del complemento validado.
        """
        self._registrar_inicio()

        try:
            resultado_page = ComplementoPagoResultadoPage(self.driver)

            # --- Verificar error ---
            # TODO: Implementar con HTML real
            # if resultado_page.has_error():
            #     return self._marcar_fallido(resultado_page.get_error_message())

            # --- Validar UUID ---
            uuid_cp = self.context.get_dato("uuid_complemento_pago", "")
            if uuid_cp:
                try:
                    assert_valid_uuid_cfdi(uuid_cp)
                    self._registrar_paso("validar_uuid_complemento", "exitoso", uuid_cp)
                except Exception as exc:
                    return self._marcar_fallido(f"UUID Complemento de Pago inválido: {exc}")
            else:
                self._registrar_paso(
                    "validar_uuid_complemento", "omitido", "UUID no disponible aún (TODO)"
                )

            self._tomar_screenshot("validacion_complemento_pago")
            return self._marcar_exitoso()

        except Exception as exc:
            logger.exception(f"Error en ComplementoPagoValidacionFlow: {exc}")
            self._tomar_screenshot("error_validacion_complemento")
            return self._marcar_fallido(str(exc))
