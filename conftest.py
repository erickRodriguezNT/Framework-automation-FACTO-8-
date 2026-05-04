
"""
conftest.py - Fixtures globales del framework FACTO 8.

Este archivo define los fixtures de pytest compartidos por todos los tests.
Los fixtures declarados aquí son descubiertos automáticamente por pytest.

Fixtures disponibles:
  - settings:          Configuración global cargada desde .env
  - execution_context: Contexto único por escenario (UUID, datos, rutas)
  - driver:            WebDriver creado y destruido por escenario
"""
import pytest
from dotenv import load_dotenv

from app.config.settings import Settings
from app.core.execution_context import ExecutionContext
from app.drivers.driver_factory import DriverFactory

# Carga variables de entorno desde .env al iniciar la sesión
load_dotenv()


@pytest.fixture(scope="session")
def settings() -> Settings:
    """
    Fixture de sesión que expone la configuración global del framework.

    Scope 'session' = se crea una sola vez por ejecución de pytest.
    """
    return Settings()


@pytest.fixture(scope="function")
def execution_context(request, settings) -> ExecutionContext:
    """
    Fixture que crea un ExecutionContext único por escenario/test.

    Captura el nombre del test activo y prepara las rutas de evidencia
    para esta ejecución particular.
    """
    scenario_name = request.node.name
    flow_name = _extract_flow_name(request)

    context = ExecutionContext(
        flujo_actual=flow_name,
        escenario_actual=scenario_name,
        output_dir=settings.output_dir,
    )
    # Inyectar credenciales y URL para que los flows puedan accederlos
    context.set_dato("username", settings.username)
    context.set_dato("password", settings.password)
    context.set_dato("base_url", settings.base_url)
    yield context


@pytest.fixture(scope="function")
def driver(settings, execution_context):
    """
    Fixture que crea y destruye el WebDriver por cada test/escenario.

    - Crea el driver según BROWSER y HEADLESS de la configuración.
    - Hace yield para entregar el driver al test.
    - Al finalizar (éxito o fallo), cierra el navegador limpiamente.
    """
    factory = DriverFactory(settings)
    web_driver = factory.create_driver()

    # Inyecta el driver en el contexto para que los flows puedan accederlo
    execution_context.driver = web_driver

    yield web_driver

    # Teardown: cierre limpio siempre, sin importar el resultado del test
    DriverFactory.quit_driver(web_driver)


# ------------------------------------------------------------------
# Helpers privados
# ------------------------------------------------------------------

def _extract_flow_name(request) -> str:
    """Extrae el nombre del flujo activo desde los markers del test."""
    flow_markers = ["factura", "nota_credito", "ppd", "complemento_pago", "adenda"]
    for marker_name in flow_markers:
        if request.node.get_closest_marker(marker_name):
            return marker_name
    return "general"
