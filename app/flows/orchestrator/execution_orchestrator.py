"""
execution_orchestrator.py - Orquestador principal de flujos del framework FACTO.

Coordina la ejecución de flujos en secuencia, respetando dependencias
y manejando el estado del execution_context entre flujos.

Uso típico (desde un step definition):
    from app.flows.orchestrator.execution_orchestrator import ExecutionOrchestrator
    orch = ExecutionOrchestrator(driver, execution_context)
    result = orch.ejecutar("factura", test_data={...})

Uso para flujo completo end-to-end:
    results = orch.ejecutar_secuencia([
        ("login",     {"username": "...", "password": "..."}),
        ("factura",   {"test_data": {...}}),
        ("ppd",       {"test_data": {...}}),
        ("complemento_pago", {"test_data": {...}}),
    ])
"""
from app.flows.orchestrator.dependency_resolver import DependencyResolver
from app.flows.orchestrator.flow_registry import FlowRegistry
from app.utils.exceptions import FlowDependencyError, FlowNotFoundError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ExecutionOrchestrator:
    """
    Orquestador de flujos del framework de automatización FACTO.

    Responsabilidades:
    - Resolver flujos por nombre vía FlowRegistry
    - Verificar dependencias via DependencyResolver
    - Ejecutar flujos con el contexto compartido
    - Propagar resultados entre flujos
    - Registrar cada flujo ejecutado en el execution_context
    """

    def __init__(self, driver, context) -> None:
        """
        Args:
            driver:  Instancia del WebDriver de Selenium.
            context: ExecutionContext del escenario actual.
        """
        self.driver = driver
        self.context = context
        self.resolver = DependencyResolver(context)

    def ejecutar(self, flow_name: str, **kwargs) -> dict:
        """
        Ejecuta un flujo por nombre.

        Args:
            flow_name: Nombre del flujo (ver FlowRegistry).
            **kwargs:  Argumentos pasados al método run() del flujo.

        Returns:
            dict con estado, flujo, execution_id, datos, error.

        Raises:
            FlowNotFoundError: Si el flujo no está registrado.
            FlowDependencyError: Si las dependencias no están satisfechas.
        """
        logger.info(f"Ejecutando flujo: {flow_name}")

        # Verificar existencia del flujo
        try:
            flow_class = FlowRegistry.get(flow_name)
        except KeyError as exc:
            raise FlowNotFoundError(str(exc)) from exc

        # Verificar dependencias
        try:
            self.resolver.verificar_dependencias(flow_name)
        except FlowDependencyError:
            raise

        # Instanciar y ejecutar
        flow = flow_class(self.driver, self.context)
        result = flow.run(**kwargs)

        # Propagar resultados al contexto para flujos dependientes
        if result.get("estado") == "exitoso":
            datos = result.get("datos", {})
            for key, value in datos.items():
                self.context.set_dato(key, value)

        logger.info(f"Flujo '{flow_name}' finalizado con estado: {result.get('estado')}")
        return result

    def ejecutar_secuencia(self, secuencia: list[tuple]) -> list[dict]:
        """
        Ejecuta una secuencia de flujos en orden.

        Si un flujo falla (estado=fallido), la secuencia se detiene.

        Args:
            secuencia: Lista de tuplas (flow_name, kwargs_dict).
                       Ej: [("login", {"username": "..."}), ("factura", {...})]

        Returns:
            Lista de resultados de cada flujo.
        """
        resultados = []

        for flow_name, kwargs in secuencia:
            result = self.ejecutar(flow_name, **kwargs)
            resultados.append(result)

            if result.get("estado") == "fallido":
                logger.error(
                    f"Secuencia interrumpida en flujo '{flow_name}': {result.get('error')}"
                )
                break

        return resultados
