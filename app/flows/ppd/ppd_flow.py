"""
ppd_flow.py - Flujo principal de emisión de Factura PPD.

PPD = Pago en Parcialidades o Diferido.
Un CFDI con método de pago PPD indica que el pago se realizará
en una fecha futura o en parcialidades, por lo que requerirá
un Complemento de Pago cuando se reciba el pago.

Uso:
    from app.flows.ppd.ppd_flow import PPDFlow
    flow = PPDFlow(driver, execution_context)
    result = flow.run(test_data={...})
"""
from app.core.base_flow import BaseFlow
from app.flows.common.navigation_flow import NavigationFlow
from app.pages.common.loader_page import LoaderPage
from app.pages.ppd.ppd_page import PPDPage
from app.pages.ppd.ppd_resultado_page import PPDResultadoPage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PPDFlow(BaseFlow):
    """
    Flujo de emisión de Factura con método de pago PPD
    (Pago en Parcialidades o Diferido).

    El UUID generado por este flujo se utiliza en ComplementoPagoFlow.
    """

    def run(self, **kwargs) -> dict:
        """
        Ejecuta el flujo completo de emisión de Factura PPD.

        Args:
            test_data: (dict) Datos del PPD.
                       Ver tests/test_data/ppd/ppd_valido.json

        Returns:
            Resultado con uuid_cfdi_ppd para uso en Complemento de Pago.
        """
        self._registrar_inicio()
        test_data: dict = kwargs.get("test_data", {})

        try:
            # --- Paso 1: Navegar al módulo PPD ---
            nav_flow = NavigationFlow(self.driver, self.context)
            nav_result = nav_flow.run(destino="ppd")
            if nav_result["estado"] == "fallido":
                return self._marcar_fallido(f"Navegación a PPD falló: {nav_result['error']}")
            self._registrar_paso("navegar_ppd", "exitoso")

            # --- Paso 2: Llenar formulario PPD ---
            ppd_page = PPDPage(self.driver)
            loader_page = LoaderPage(self.driver)

            # TODO: Implementar con selectores reales del portal
            # ppd_page.fill_rfc_receptor(test_data.get("rfc_receptor", ""))
            # ppd_page.fill_nombre_receptor(test_data.get("nombre_receptor", ""))
            # ppd_page.select_uso_cfdi(test_data.get("uso_cfdi", ""))
            # ppd_page.select_metodo_pago_ppd()   # Siempre PPD
            # ppd_page.select_forma_pago(test_data.get("forma_pago", "99"))  # Por definir
            # ppd_page.fill_descripcion(test_data.get("descripcion", ""))
            # ppd_page.fill_importe(str(test_data.get("importe", "")))
            # ppd_page.click_continuar()
            # loader_page.wait_for_loader_to_disappear()

            self._registrar_paso("llenar_formulario_ppd", "omitido", "TODO: implementar")
            self._tomar_screenshot("02_formulario_ppd")

            # --- Paso 3: Capturar resultado ---
            resultado_page = PPDResultadoPage(self.driver)

            # TODO: Verificar timbrado y capturar UUID
            # if not resultado_page.is_timbrado_exitoso():
            #     return self._marcar_fallido(resultado_page.get_error_message())
            # uuid_ppd = resultado_page.get_uuid_cfdi()
            # self._guardar_resultado("uuid_cfdi_ppd", uuid_ppd)
            # self.context.set_dato("uuid_cfdi_ppd", uuid_ppd)  # Usado por complemento_pago

            self._registrar_paso("obtener_uuid_ppd", "omitido", "TODO: implementar")
            self._tomar_screenshot("03_resultado_ppd")

            return self._marcar_exitoso()

        except Exception as exc:
            logger.exception(f"Error en PPDFlow: {exc}")
            self._tomar_screenshot("error_ppd")
            return self._marcar_fallido(str(exc))
