"""
complemento_pago_flow.py - Flujo principal de emisión de Complemento de Pago.

Un Complemento de Pago (CfDI tipo P) se emite cuando se recibe
el pago de una factura con método PPD.

DEPENDENCIA CRÍTICA: Requiere UUID de un CFDI PPD previamente timbrado.

Flujo completo:
1. Navegar al módulo de Complemento de Pago
2. Llenar datos del pago (fecha, forma, monto, moneda)
3. Relacionar con el CFDI PPD (RelacionPPDPage)
4. Timbrar y capturar UUID del Complemento

Uso:
    from app.flows.complemento_pago.complemento_pago_flow import ComplementoPagoFlow
    flow = ComplementoPagoFlow(driver, execution_context)
    result = flow.run(test_data={...}, uuid_ppd="xxx-yyy-zzz")
"""
from app.core.base_flow import BaseFlow
from app.flows.common.navigation_flow import NavigationFlow
from app.pages.common.loader_page import LoaderPage
from app.pages.complemento_pago.complemento_pago_page import ComplementoPagoPage
from app.pages.complemento_pago.complemento_pago_resultado_page import (
    ComplementoPagoResultadoPage,
)
from app.pages.complemento_pago.relacion_ppd_page import RelacionPPDPage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ComplementoPagoFlow(BaseFlow):
    """
    Flujo de emisión de Complemento de Pago (CFDI tipo P).

    Requiere UUID de una Factura PPD como documento a liquidar.
    """

    def run(self, **kwargs) -> dict:
        """
        Ejecuta el flujo de Complemento de Pago.

        Args:
            test_data: (dict) Datos del complemento de pago.
            uuid_ppd:  (str)  UUID del CFDI PPD a liquidar.

        Returns:
            Resultado con uuid_cfdi del Complemento de Pago.
        """
        self._registrar_inicio()
        test_data: dict = kwargs.get("test_data", {})
        uuid_ppd = (
            kwargs.get("uuid_ppd")
            or self.context.get_dato("uuid_cfdi_ppd", "")
        )

        if not uuid_ppd:
            return self._marcar_fallido(
                "Se requiere uuid_ppd para emitir un Complemento de Pago."
            )

        try:
            # --- Paso 1: Navegar al módulo ---
            nav_flow = NavigationFlow(self.driver, self.context)
            nav_result = nav_flow.run(destino="complemento_pago")
            if nav_result["estado"] == "fallido":
                return self._marcar_fallido(f"Navegación falló: {nav_result['error']}")
            self._registrar_paso("navegar_complemento_pago", "exitoso")

            # --- Paso 2: Llenar datos del pago ---
            cp_page = ComplementoPagoPage(self.driver)
            loader_page = LoaderPage(self.driver)

            # TODO: Implementar con selectores reales del portal
            # cp_page.fill_rfc_receptor(test_data.get("rfc_receptor", ""))
            # cp_page.fill_fecha_pago(test_data.get("fecha_pago", ""))
            # cp_page.select_forma_pago(test_data.get("forma_pago", ""))
            # cp_page.select_moneda(test_data.get("moneda", "MXN"))
            # cp_page.fill_monto_pago(str(test_data.get("monto_pago", "")))
            # cp_page.fill_num_operacion(test_data.get("num_operacion", ""))
            # cp_page.click_continuar()
            # loader_page.wait_for_loader_to_disappear()

            self._registrar_paso("llenar_datos_pago", "omitido", "TODO: implementar")
            self._tomar_screenshot("02_datos_complemento_pago")

            # --- Paso 3: Relacionar con PPD ---
            relacion_page = RelacionPPDPage(self.driver)

            # TODO: Implementar relación con PPD
            # relacion_page.click_agregar_documento()
            # relacion_page.fill_uuid_documento_ppd(uuid_ppd)
            # relacion_page.fill_num_parcialidad(str(test_data.get("num_parcialidad", 1)))
            # relacion_page.fill_importe_saldo_anterior(str(test_data.get("importe_saldo_anterior", "")))
            # relacion_page.fill_importe_pagado(str(test_data.get("importe_pagado", "")))
            # relacion_page.fill_importe_saldo_insoluto(str(test_data.get("importe_saldo_insoluto", "0.00")))
            # relacion_page.click_guardar_documento()
            # relacion_page.click_continuar()
            # loader_page.wait_for_loader_to_disappear()

            self._registrar_paso("relacionar_ppd", "omitido", f"TODO: uuid_ppd={uuid_ppd}")
            self._tomar_screenshot("03_relacion_ppd")

            # --- Paso 4: Obtener resultado ---
            resultado_page = ComplementoPagoResultadoPage(self.driver)

            # TODO: Verificar timbrado
            # if not resultado_page.is_timbrado_exitoso():
            #     return self._marcar_fallido(resultado_page.get_error_message())
            # uuid_cp = resultado_page.get_uuid_cfdi()
            # self._guardar_resultado("uuid_cfdi_cp", uuid_cp)
            # self.context.set_dato("uuid_complemento_pago", uuid_cp)

            self._registrar_paso("obtener_uuid_complemento", "omitido", "TODO: implementar")
            self._tomar_screenshot("04_resultado_complemento_pago")

            return self._marcar_exitoso()

        except Exception as exc:
            logger.exception(f"Error en ComplementoPagoFlow: {exc}")
            self._tomar_screenshot("error_complemento_pago")
            return self._marcar_fallido(str(exc))
