"""
adenda_flow.py - Flujo principal para agregar una Adenda a un CFDI.

Una Adenda es información adicional de negocio que se incorpora
al CFDI fuera de los nodos fiscales del SAT (datos comerciales
requeridos por el receptor).

Uso:
    from app.flows.adenda.adenda_flow import AdendaFlow
    flow = AdendaFlow(driver, execution_context)
    result = flow.run(test_data={...}, uuid_cfdi="xxx-yyy-zzz")
"""
from app.core.base_flow import BaseFlow
from app.flows.common.navigation_flow import NavigationFlow
from app.pages.adenda.adenda_page import AdendaPage
from app.pages.adenda.adenda_resultado_page import AdendaResultadoPage
from app.pages.common.loader_page import LoaderPage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AdendaFlow(BaseFlow):
    """
    Flujo para agregar una Adenda a un CFDI ya emitido en el portal FACTO.
    """

    def run(self, **kwargs) -> dict:
        """
        Ejecuta el flujo de captura y procesamiento de Adenda.

        Args:
            test_data: (dict) Datos de la adenda.
                       Ver tests/test_data/adenda/adenda_valida.json
            uuid_cfdi: (str)  UUID del CFDI al que se agrega la adenda.

        Returns:
            Resultado del flujo con ID de adenda procesada o error.
        """
        self._registrar_inicio()
        test_data: dict = kwargs.get("test_data", {})
        uuid_cfdi = (
            kwargs.get("uuid_cfdi")
            or self.context.get_dato("uuid_cfdi", "")
        )

        try:
            # --- Paso 1: Navegar al módulo de Adenda ---
            nav_flow = NavigationFlow(self.driver, self.context)
            nav_result = nav_flow.run(destino="adenda")
            if nav_result["estado"] == "fallido":
                return self._marcar_fallido(f"Navegación a adenda falló: {nav_result['error']}")
            self._registrar_paso("navegar_adenda", "exitoso")

            # --- Paso 2: Llenar formulario de Adenda ---
            adenda_page = AdendaPage(self.driver)
            loader_page = LoaderPage(self.driver)

            # TODO: Implementar con selectores reales del portal
            # if uuid_cfdi:
            #     adenda_page.fill_uuid_base(uuid_cfdi)
            # adenda_page.select_tipo_adenda(test_data.get("tipo_adenda", ""))
            # adenda_page.fill_referencia_oc(test_data.get("referencia_oc", ""))
            # adenda_page.fill_num_proveedor(test_data.get("num_proveedor", ""))
            # adenda_page.fill_descripcion(test_data.get("descripcion_adenda", ""))
            # adenda_page.click_guardar()
            # loader_page.wait_for_loader_to_disappear()

            self._registrar_paso("llenar_adenda", "omitido", "TODO: implementar")
            self._tomar_screenshot("02_formulario_adenda")

            # --- Paso 3: Verificar resultado ---
            resultado_page = AdendaResultadoPage(self.driver)

            # TODO: Verificar que la adenda fue procesada
            # if resultado_page.has_error():
            #     return self._marcar_fallido(resultado_page.get_error_message())
            # id_adenda = resultado_page.get_id_adenda()
            # self._guardar_resultado("id_adenda", id_adenda)

            self._registrar_paso("verificar_adenda", "omitido", "TODO: implementar")
            self._tomar_screenshot("03_resultado_adenda")

            return self._marcar_exitoso()

        except Exception as exc:
            logger.exception(f"Error en AdendaFlow: {exc}")
            self._tomar_screenshot("error_adenda")
            return self._marcar_fallido(str(exc))
