"""
nota_credito_relacion_flow.py - Sub-flujo de vinculación de Nota de Crédito con Factura.

Gestiona específicamente el paso de relacionar la Nota de Crédito
con el CFDI de Ingreso (Factura) que la origina.

Se separa como sub-flujo para:
- Pruebas aisladas de la relación de documentos
- Reutilización en escenarios de múltiples notas sobre la misma factura

Uso:
    from app.flows.nota_credito.nota_credito_relacion_flow import NotaCreditoRelacionFlow
    flow = NotaCreditoRelacionFlow(driver, execution_context)
    result = flow.run(uuid_relacionado="xxx-yyy-zzz", tipo_relacion="01")
"""
from app.core.base_flow import BaseFlow
from app.pages.nota_credito.nota_credito_page import NotaCreditoPage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NotaCreditoRelacionFlow(BaseFlow):
    """
    Sub-flujo para establecer la relación entre la Nota de Crédito y su CFDI origen.
    """

    def run(self, **kwargs) -> dict:
        """
        Establece la relación del CFDI en el formulario de Nota de Crédito.

        Args:
            uuid_relacionado: (str) UUID del CFDI de Ingreso a relacionar.
            tipo_relacion:    (str) Código de tipo de relación SAT. Default: '01'.

        Returns:
            Resultado del sub-flujo.
        """
        self._registrar_inicio()

        uuid_relacionado = (
            kwargs.get("uuid_relacionado")
            or self.context.get_dato("uuid_factura_relacionada", "")
        )
        tipo_relacion = kwargs.get("tipo_relacion", "01")

        if not uuid_relacionado:
            return self._marcar_fallido("Se requiere uuid_relacionado para la Nota de Crédito.")

        try:
            nc_page = NotaCreditoPage(self.driver)

            # TODO: Implementar cuando se tenga el HTML del portal
            # nc_page.fill_uuid_relacionado(uuid_relacionado)
            # nc_page.select_tipo_relacion(tipo_relacion)
            # nc_page.wait_for_relacion_validada()

            self._registrar_paso(
                "establecer_relacion_cfdi",
                "omitido",
                f"TODO: vincular uuid={uuid_relacionado} tipo={tipo_relacion}",
            )
            self._tomar_screenshot("relacion_nota_credito")
            self._guardar_resultado("uuid_relacionado", uuid_relacionado)
            self._guardar_resultado("tipo_relacion", tipo_relacion)

            return self._marcar_exitoso()

        except Exception as exc:
            logger.exception(f"Error en NotaCreditoRelacionFlow: {exc}")
            self._tomar_screenshot("error_relacion_nota_credito")
            return self._marcar_fallido(str(exc))
