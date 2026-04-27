"""
dependency_resolver.py - Resuelve dependencias entre flujos del portal FACTO.

Define el grafo de dependencias entre flujos:
- complemento_pago → ppd
- nota_credito     → factura
- ppd              → (ninguna)
- factura          → (ninguna)
- adenda           → (ninguna)

Permite verificar que los datos requeridos por un flujo
estén disponibles en el execution_context antes de ejecutar.

Uso:
    from app.flows.orchestrator.dependency_resolver import DependencyResolver
    resolver = DependencyResolver(execution_context)
    resolver.verificar_dependencias("complemento_pago")
"""
from app.utils.exceptions import FlowDependencyError
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Mapa de dependencias: flujo → lista de datos requeridos en execution_context
DEPENDENCY_MAP: dict[str, list[str]] = {
    "factura":                 [],
    "factura_timbrado":        [],
    "factura_descarga":        ["uuid_cfdi"],
    "nota_credito":            ["uuid_factura_relacionada"],
    "nota_credito_relacion":   ["uuid_factura_relacionada"],
    "ppd":                     [],
    "ppd_validacion":          [],
    "complemento_pago":        ["uuid_cfdi_ppd"],
    "complemento_pago_relacion": ["uuid_cfdi_ppd"],
    "complemento_pago_validacion": [],
    "adenda":                  [],
    "adenda_validacion":       [],
    "login":                   [],
    "navigation":              [],
    "download":                [],
    "validation":              [],
}


class DependencyResolver:
    """
    Verifica que las dependencias de datos de un flujo estén satisfechas.
    """

    def __init__(self, context) -> None:
        """
        Args:
            context: ExecutionContext con los datos del escenario actual.
        """
        self.context = context

    def verificar_dependencias(self, flow_name: str) -> None:
        """
        Verifica que todos los datos requeridos por el flujo existan
        en el execution_context.

        Args:
            flow_name: Nombre del flujo a verificar.

        Raises:
            FlowDependencyError: Si falta algún dato requerido.
        """
        required_keys = DEPENDENCY_MAP.get(flow_name, [])
        faltantes = []

        for key in required_keys:
            valor = self.context.get_dato(key)
            if not valor:
                faltantes.append(key)

        if faltantes:
            raise FlowDependencyError(
                f"El flujo '{flow_name}' requiere los siguientes datos en el contexto "
                f"que no están disponibles: {faltantes}. "
                f"Verifique que los flujos previos se ejecutaron correctamente."
            )

        logger.debug(f"Dependencias de '{flow_name}' satisfechas: {required_keys or 'ninguna'}")

    def get_dependencias(self, flow_name: str) -> list[str]:
        """
        Retorna la lista de claves requeridas por el flujo.

        Args:
            flow_name: Nombre del flujo.

        Returns:
            Lista de claves de datos requeridas.
        """
        return DEPENDENCY_MAP.get(flow_name, [])
