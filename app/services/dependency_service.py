"""
dependency_service.py - Servicio de verificación de dependencias entre escenarios.

Verifica que los datos requeridos por un escenario estén disponibles
en el execution_context antes de ejecutar.

Diferente a DependencyResolver (que verifica datos en contexto),
este servicio verifica dependencias a nivel de suite:
- Que una Factura exista antes de emitir Nota de Crédito
- Que un PPD exista antes de emitir Complemento de Pago

Uso:
    from app.services.dependency_service import DependencyService
    service = DependencyService()
    service.verificar_prerequisito("complemento_pago", contexto)
"""
from app.utils.exceptions import FlowDependencyError
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Mapa de prerequisitos: flujo → (clave_en_contexto, mensaje_de_error)
PREREQUISITOS: dict[str, list[tuple[str, str]]] = {
    "nota_credito": [
        (
            "uuid_factura_relacionada",
            "Nota de Crédito requiere UUID de una Factura previamente timbrada. "
            "Ejecutar primero el flujo 'factura'.",
        ),
    ],
    "complemento_pago": [
        (
            "uuid_cfdi_ppd",
            "Complemento de Pago requiere UUID de un CFDI PPD previamente timbrado. "
            "Ejecutar primero el flujo 'ppd'.",
        ),
    ],
}


class DependencyService:
    """
    Servicio de verificación de prerequisitos de datos entre flujos de negocio.
    """

    def verificar_prerequisito(self, flow_name: str, context) -> None:
        """
        Verifica que los prerequisitos del flujo estén satisfechos.

        Args:
            flow_name: Nombre del flujo a verificar.
            context:   ExecutionContext con los datos disponibles.

        Raises:
            FlowDependencyError: Si algún prerequisito no se cumple.
        """
        requisitos = PREREQUISITOS.get(flow_name, [])

        for clave, mensaje_error in requisitos:
            valor = context.get_dato(clave, "")
            if not valor:
                logger.error(f"Prerequisito faltante para '{flow_name}': clave='{clave}'")
                raise FlowDependencyError(mensaje_error)

        if requisitos:
            logger.debug(f"Prerequisitos de '{flow_name}' verificados correctamente.")

    def tiene_prerequisitos(self, flow_name: str) -> bool:
        """Retorna True si el flujo tiene prerequisitos definidos."""
        return flow_name in PREREQUISITOS
