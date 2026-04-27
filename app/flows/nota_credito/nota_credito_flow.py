"""
nota_credito_flow.py - Flujo principal de emisión de Nota de Crédito.

Una Nota de Crédito (CFDI tipo E - Egreso) se emite para:
- Descuentos sobre una factura ya timbrada
- Devoluciones de mercancía
- Bonificaciones

DEPENDENCIA: Requiere UUID de una Factura (tipo I - Ingreso) previamente
             timbrada para establecer la relación CFDI.

Uso:
    from app.flows.nota_credito.nota_credito_flow import NotaCreditoFlow
    flow = NotaCreditoFlow(driver, execution_context)
    result = flow.run(test_data={...}, uuid_factura_relacionada="xxx-yyy-zzz")
"""
from app.core.base_flow import BaseFlow
from app.flows.common.navigation_flow import NavigationFlow
from app.pages.common.loader_page import LoaderPage
from app.pages.nota_credito.nota_credito_page import NotaCreditoPage
from app.pages.nota_credito.nota_credito_resultado_page import NotaCreditoResultadoPage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NotaCreditoFlow(BaseFlow):
    """
    Flujo de emisión de Nota de Crédito (CFDI tipo E - Egreso).

    Requiere el UUID de la factura relacionada como dato previo.
    """

    def run(self, **kwargs) -> dict:
        """
        Ejecuta el flujo completo de emisión de Nota de Crédito.

        Args:
            test_data:               (dict) Datos de la nota de crédito.
            uuid_factura_relacionada:(str)  UUID del CFDI de ingreso relacionado.

        Returns:
            Resultado con UUID de la Nota de Crédito o error.
        """
        self._registrar_inicio()
        test_data: dict = kwargs.get("test_data", {})
        uuid_factura = (
            kwargs.get("uuid_factura_relacionada")
            or self.context.get_dato("uuid_factura_relacionada")
            or self.context.get_dato("uuid_cfdi", "")
        )

        if not uuid_factura:
            return self._marcar_fallido(
                "Se requiere uuid_factura_relacionada para emitir una Nota de Crédito."
            )

        try:
            # --- Paso 1: Navegar al módulo de Nota de Crédito ---
            nav_flow = NavigationFlow(self.driver, self.context)
            nav_result = nav_flow.run(destino="nota_credito")
            if nav_result["estado"] == "fallido":
                return self._marcar_fallido(f"Navegación falló: {nav_result['error']}")
            self._registrar_paso("navegar_nota_credito", "exitoso")

            # --- Paso 2: Llenar formulario ---
            nc_page = NotaCreditoPage(self.driver)
            loader_page = LoaderPage(self.driver)

            # TODO: Implementar con selectores reales del portal
            # nc_page.fill_uuid_relacionado(uuid_factura)
            # nc_page.select_tipo_relacion(test_data.get("tipo_relacion", "01"))
            # nc_page.fill_rfc_receptor(test_data.get("rfc_receptor", ""))
            # nc_page.fill_nombre_receptor(test_data.get("nombre_receptor", ""))
            # nc_page.select_uso_cfdi(test_data.get("uso_cfdi", ""))
            # nc_page.fill_motivo(test_data.get("motivo", ""))
            # nc_page.fill_importe(str(test_data.get("importe", "")))
            # nc_page.click_continuar()
            # loader_page.wait_for_loader_to_disappear()

            self._registrar_paso("llenar_formulario_nota_credito", "omitido", "TODO: implementar")
            self._tomar_screenshot("02_formulario_nota_credito")

            # --- Paso 3: Capturar resultado ---
            resultado_page = NotaCreditoResultadoPage(self.driver)

            # TODO: Verificar timbrado y capturar UUID
            # if not resultado_page.is_timbrado_exitoso():
            #     return self._marcar_fallido(resultado_page.get_error_message())
            # uuid_nc = resultado_page.get_uuid_cfdi()
            # self._guardar_resultado("uuid_cfdi_nc", uuid_nc)
            # self.context.set_dato("uuid_nota_credito", uuid_nc)

            self._registrar_paso("obtener_uuid_nota_credito", "omitido", "TODO: implementar")
            self._tomar_screenshot("03_resultado_nota_credito")

            return self._marcar_exitoso()

        except Exception as exc:
            logger.exception(f"Error en NotaCreditoFlow: {exc}")
            self._tomar_screenshot("error_nota_credito")
            return self._marcar_fallido(str(exc))
