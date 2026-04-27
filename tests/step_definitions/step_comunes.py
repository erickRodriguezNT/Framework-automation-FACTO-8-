"""
step_comunes.py - Step definitions compartidos entre todos los flujos.

Incluye los pasos de:
- Autenticación (login)
- Precondiciones de sesión
- Verificaciones genéricas de módulos

Los steps aquí definidos son reutilizados por TODOS los feature files,
por lo que pytest-bdd los registra globalmente.

REGLA: Los steps SOLO llaman a flows. No usan Selenium directamente.
"""
import pytest
from pytest_bdd import given, scenarios, then, when

from app.flows.common.login_flow import LoginFlow
from app.flows.common.navigation_flow import NavigationFlow

# Vincula este archivo a los feature files que contienen pasos de login.
# Los pasos compartidos son descubiertos automáticamente.
# No es necesario scenarios() aquí si se declara en cada step file propio.


@given("que el usuario está autenticado en el portal FACTO 8")
def usuario_autenticado(driver, execution_context, settings):
    """Ejecuta el flujo de login con las credenciales del entorno."""
    flow = LoginFlow(driver, execution_context)
    result = flow.run(
        username=settings.username,
        password=settings.password,
        base_url=settings.base_url,
    )
    assert result["estado"] == "exitoso", (
        f"Login falló: {result.get('error')}"
    )


@given("que el portal FACTO 8 está disponible")
def portal_disponible(driver, settings):
    """Verifica que el portal está disponible navegando a la URL base."""
    driver.get(settings.base_url)
    assert driver.title is not None, "El portal no respondió con una página válida."


@when("el usuario se autentica con credenciales válidas")
def autenticar_usuario(driver, execution_context, settings):
    """Reutiliza la autenticación con credenciales del entorno."""
    flow = LoginFlow(driver, execution_context)
    result = flow.run(
        username=settings.username,
        password=settings.password,
        base_url=settings.base_url,
    )
    assert result["estado"] == "exitoso", f"Login falló: {result.get('error')}"


@then("el usuario ve el dashboard principal del portal")
def verificar_dashboard(driver, execution_context):
    """Verifica que el dashboard principal está visible."""
    from app.pages.common.home_page import HomePage
    home = HomePage(driver)
    assert home.is_logged_in(), "El dashboard principal no está visible tras el login."
