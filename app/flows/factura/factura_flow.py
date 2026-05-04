"""
factura_flow.py - Flujo principal de emisiÃ³n de Factura manual en el portal FACTO 8.

Thin wrapper sobre CfdiManualFlow que preserva el contrato pÃºblico original:

    flow = FacturaFlow(driver, execution_context)
    result = flow.ejecutar_factura_manual(test_data)
    result = flow.run(test_data=test_data)

Toda la orquestaciÃ³n real vive en:
    app/flows/common/cfdi_manual_flow.py

La separaciÃ³n permite que PPD y futuros mÃ³dulos reutilicen la misma
lÃ³gica sin duplicar cÃ³digo.
"""
from app.core.base_flow import BaseFlow
from app.flows.common.cfdi_manual_flow import CfdiManualFlow
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FacturaFlow(BaseFlow):
    """
    Flujo de emisiÃ³n de Factura manual (CFDI tipo I - Ingreso).

    Thin wrapper que preserva el contrato pÃºblico original.
    Toda la orquestaciÃ³n vive en CfdiManualFlow.

    Uso:
        flow = FacturaFlow(driver, execution_context)
        result = flow.ejecutar_factura_manual(test_data)
        result = flow.run(test_data=test_data)
    """

    def run(self, **kwargs) -> dict:
        """
        Punto de entrada estÃ¡ndar del BaseFlow.

        Args:
            test_data: (dict) Datos del formulario (plano Excel o anidado JSON).

        Returns:
            Resultado estÃ¡ndar BaseFlow: { "estado", "datos", "error" }
        """
        return self.ejecutar_factura_manual(kwargs.get("test_data", {}))

    def ejecutar_factura_manual(self, test_data: dict) -> dict:
        """
        Ejecuta el flujo completo de generaciÃ³n de Factura manual.

        Acepta el formato plano del Excel (clave rfc_receptor / caso_id)
        o el formato anidado legacy (claves emisor/receptor/comprobante).

        Delega a CfdiManualFlow con tipo_flujo='factura'.

        Args:
            test_data: Dict plano del Excel o dict anidado del JSON legacy.

        Returns:
            { "estado": "exitoso"|"fallido", "datos": dict, "error": str|None }
        """
        common_flow = CfdiManualFlow(self.driver, self.context)
        return common_flow.ejecutar_cfdi_manual(caso=test_data, tipo_flujo="factura")
