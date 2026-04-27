"""
conftest.py (tests/) - Fixtures de soporte para pytest-bdd.

Importa los hooks de setup/teardown y agrega el fixture
de screenshot automático en caso de fallo.

NO duplicar fixtures definidos en conftest.py raíz.
Los fixtures de settings, execution_context y driver
están en el conftest.py de la raíz del proyecto.
"""
import pytest

from tests.hooks.hooks import (
    attach_screenshot_to_allure,
    pytest_runtest_makereport,  # noqa: F401 — auto-usado por pytest
)


@pytest.fixture(autouse=True)
def screenshot_on_failure(driver, execution_context, request):
    """
    Fixture autouse que toma un screenshot automático al fallar un test.

    Se ejecuta después de cada test y verifica si hubo fallo.
    Adjunta el screenshot a Allure si está disponible.
    """
    yield

    # El hook pytest_runtest_makereport (en hooks.py) captura el estado del test.
    # Aquí accedemos al resultado almacenado en el request node.
    report = getattr(request.node, "_last_report", None)
    if report and report.failed:
        attach_screenshot_to_allure(driver, request.node.name)
