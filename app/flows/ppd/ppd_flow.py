"""
ppd_flow.py - Flujo principal de emision de CFDI con metodo de pago PPD.

PPD = Pago en Parcialidades o Diferido.
Un CFDI PPD es una Factura con metodo_pago=PPD. Utiliza exactamente el
mismo formulario de emision que Factura en el portal FACTO 8.

Thin wrapper sobre CfdiManualFlow:
  - Garantiza que metodo_pago siempre sea 'PPD'.
  - Lee datos desde tests/test_data/ppd/ppd_casos.xlsx (hoja PPD).
  - Genera outputs en outputs/ppd/{timestamp}/{caso_id}/.
  - NO copia Page Objects de Factura: los reutiliza directamente.

Uso:
    from app.flows.ppd.ppd_flow import PPDFlow
    flow = PPDFlow(driver, execution_context)
    result = flow.ejecutar_ppd(caso)
"""
from app.core.base_flow import BaseFlow
from app.flows.common.cfdi_manual_flow import CfdiManualFlow
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PPDFlow(BaseFlow):
    """
    Flujo de emision de CFDI con metodo de pago PPD.

    Thin wrapper sobre CfdiManualFlow con tipo_flujo='ppd'.

    La unica responsabilidad propia de PPDFlow es garantizar que
    el campo metodo_pago del caso sea 'PPD' antes de delegar.

    Uso:
        flow = PPDFlow(driver, execution_context)
        result = flow.ejecutar_ppd(caso)       # data-driven desde Excel
        result = flow.run(caso=caso)            # llamada directa
    """

    def run(self, **kwargs) -> dict:
        """
        Punto de entrada estandar del BaseFlow.

        Acepta 'caso' o 'test_data' (retrocompatibilidad con step_ppd.py).

        Args:
            caso:      Dict plano del Excel PPD.
            test_data: Alias de 'caso' para compatibilidad con step_ppd legacy.

        Returns:
            Resultado estandar BaseFlow: { "estado", "datos", "error" }
        """
        caso = kwargs.get("caso", kwargs.get("test_data", {}))
        return self.ejecutar_ppd(caso)

    def ejecutar_ppd(self, caso: dict) -> dict:
        """
        Ejecuta el flujo completo de emision de CFDI PPD.

        Regla de negocio PPD:
          - metodo_pago DEBE ser 'PPD'. Si el Excel lo trae vacio o diferente,
            este metodo lo fuerza a 'PPD' con un warning antes de continuar.

        Delega a CfdiManualFlow con tipo_flujo='ppd', que:
          - Lee run_dir_ppd del contexto (creado por ppd_steps.py).
          - Navega al modulo ppd del portal.
          - Usa los Page Objects de app/pages/factura/ (mismo formulario).
          - Genera outputs en outputs/ppd/{timestamp}/{caso_id}/.

        Args:
            caso: Dict plano del Excel PPD (columnas de ppd_casos.xlsx).

        Returns:
            { "estado": "exitoso"|"fallido", "datos": dict, "error": str|None }
        """
        # â”€â”€ Garantizar metodo_pago = PPD â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        caso_ppd = {**caso}
        metodo_actual = str(caso_ppd.get("metodo_pago", "")).strip().upper()
        if not metodo_actual.startswith("PPD"):
            logger.warning(
                "[PPD FLOW] metodo_pago='%s' no es PPD â€” forzando a 'PPD'.",
                metodo_actual or "(vacio)",
            )
            caso_ppd["metodo_pago"] = "PPD"

        # â”€â”€ Delegar al flujo comun â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        common_flow = CfdiManualFlow(self.driver, self.context)
        return common_flow.ejecutar_cfdi_manual(caso=caso_ppd, tipo_flujo="ppd")


