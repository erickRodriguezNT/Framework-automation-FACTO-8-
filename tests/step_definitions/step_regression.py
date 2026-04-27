"""
step_regression.py - Step definitions para los feature files de regresión.

Implementa los pasos de:
- tests/features/regression/smoke.feature
- tests/features/regression/end_to_end.feature
- tests/features/regression/dependencias.feature

REGLA: Los steps SOLO llaman a flows. No usan Selenium directamente.
"""
import pytest
from pytest_bdd import given, scenarios, then, when

from app.flows.common.navigation_flow import NavigationFlow
from app.services.dependency_service import DependencyService
from app.utils.exceptions import FlowDependencyError

# Vincular todos los feature files de regresión
scenarios("regression/smoke.feature")
scenarios("regression/end_to_end.feature")
scenarios("regression/dependencias.feature")


# ---------------------------------------------------------------------------
# Smoke test steps
# ---------------------------------------------------------------------------

@when('el usuario navega al módulo de Factura')
def navegar_modulo_factura(driver, execution_context):
    """Navega al módulo de Factura."""
    flow = NavigationFlow(driver, execution_context)
    result = flow.run(destino="factura")
    assert result["estado"] == "exitoso"


@then("el módulo de Factura carga correctamente")
def verificar_modulo_factura(driver):
    """Verifica que el módulo de Factura cargó."""
    # TODO: Implementar verificación real


@when("el usuario navega al módulo de Nota de Crédito")
def navegar_modulo_nc(driver, execution_context):
    """Navega al módulo de Nota de Crédito."""
    flow = NavigationFlow(driver, execution_context)
    result = flow.run(destino="nota_credito")
    assert result["estado"] == "exitoso"


@then("el módulo de Nota de Crédito carga correctamente")
def verificar_modulo_nc(driver):
    """Verifica que el módulo de NC cargó."""
    # TODO: Implementar


@then("el módulo de Complemento de Pago carga correctamente")
def verificar_modulo_cp(driver):
    """Verifica que el módulo de CP cargó."""
    # TODO: Implementar


# ---------------------------------------------------------------------------
# End-to-End steps
# ---------------------------------------------------------------------------

@when("el usuario emite una factura con método de pago PPD")
def emitir_factura_ppd_e2e(driver, execution_context):
    """Emite una factura PPD en el contexto del test end-to-end."""
    from app.flows.ppd.ppd_flow import PPDFlow
    from app.services.data_service import DataService

    data_svc = DataService()
    test_data = data_svc.load("ppd", "ppd_valido")

    flow = PPDFlow(driver, execution_context)
    result = flow.run(test_data=test_data)
    assert result["estado"] == "exitoso", f"PPDFlow E2E falló: {result.get('error')}"


@when("el usuario emite una factura de ingreso con datos válidos")
def emitir_factura_ingreso_e2e(driver, execution_context):
    """Emite una factura de ingreso para el test E2E de NC."""
    from app.flows.factura.factura_flow import FacturaFlow
    from app.services.data_service import DataService

    data_svc = DataService()
    test_data = data_svc.load("factura", "factura_valida")

    flow = FacturaFlow(driver, execution_context)
    result = flow.run(test_data=test_data)
    assert result["estado"] == "exitoso", f"FacturaFlow E2E falló: {result.get('error')}"


@when("el usuario relaciona la factura PPD recién emitida")
def relacionar_factura_ppd_e2e(execution_context):
    """El UUID del PPD ya está en el contexto del flujo anterior."""
    uuid_ppd = execution_context.get_dato("uuid_cfdi_ppd", "")
    assert uuid_ppd, "UUID PPD no disponible en el contexto para E2E."


@when("el usuario captura los datos del pago recibido")
def capturar_datos_pago_e2e(driver, execution_context):
    """Ejecuta el flujo de CP con datos del pago."""
    from app.flows.complemento_pago.complemento_pago_flow import ComplementoPagoFlow
    from app.services.data_service import DataService

    data_svc = DataService()
    test_data = data_svc.load("complemento_pago", "complemento_pago_valido")

    flow = ComplementoPagoFlow(driver, execution_context)
    result = flow.run(test_data=test_data)
    assert result["estado"] == "exitoso", f"ComplementoPagoFlow E2E falló: {result.get('error')}"


@then("el complemento de pago queda relacionado con la factura PPD")
def verificar_relacion_cp_ppd(execution_context):
    """Verifica la relación entre CP y PPD."""
    # TODO: Implementar cuando flujos reales estén completos


@when("el usuario relaciona la factura recién emitida")
def relacionar_factura_nc_e2e(execution_context):
    """El UUID de la factura ya está en el contexto."""
    uuid = execution_context.get_dato("uuid_cfdi", "")
    execution_context.set_dato("uuid_factura_relacionada", uuid)


@when("el usuario captura los datos de la nota de crédito")
def capturar_datos_nc_e2e(driver, execution_context):
    """Ejecuta el flujo de Nota de Crédito."""
    from app.flows.nota_credito.nota_credito_flow import NotaCreditoFlow
    from app.services.data_service import DataService

    data_svc = DataService()
    test_data = data_svc.load("nota_credito", "nota_credito_valida")

    flow = NotaCreditoFlow(driver, execution_context)
    result = flow.run(test_data=test_data)
    assert result["estado"] == "exitoso", f"NotaCreditoFlow E2E falló: {result.get('error')}"


@then("la nota de crédito queda relacionada con la factura de ingreso")
def verificar_relacion_nc_factura(execution_context):
    """Verifica la relación entre NC y Factura."""
    # TODO: Implementar cuando flujos reales estén completos


# ---------------------------------------------------------------------------
# Dependencias steps
# ---------------------------------------------------------------------------

@when("el sistema intenta ejecutar el flujo de Complemento de Pago sin un PPD previo")
def ejecutar_cp_sin_ppd(execution_context):
    """Intenta ejecutar CP sin UUID de PPD en el contexto."""
    execution_context.set_dato("uuid_cfdi_ppd", "")
    execution_context.set_dato("dependencia_violada", "complemento_pago")


@when("el sistema intenta ejecutar el flujo de Nota de Crédito sin una factura previa")
def ejecutar_nc_sin_factura(execution_context):
    """Intenta ejecutar NC sin UUID de factura en el contexto."""
    execution_context.set_dato("uuid_factura_relacionada", "")
    execution_context.set_dato("dependencia_violada", "nota_credito")


@then("el sistema lanza un error de dependencia indicando que se requiere un CFDI PPD")
def verificar_error_dependencia_ppd(execution_context):
    """Verifica que el sistema detecta la dependencia faltante de PPD."""
    dep_service = DependencyService()
    # Simular contexto vacío
    class MockCtx:
        def get_dato(self, key, default=""):
            return default
    try:
        dep_service.verificar_prerequisito("complemento_pago", MockCtx())
        pytest.fail("Se esperaba FlowDependencyError pero no se lanzó.")
    except FlowDependencyError:
        pass  # Correcto: la dependencia fue detectada


@then("el sistema lanza un error de dependencia indicando que se requiere un CFDI de ingreso")
def verificar_error_dependencia_factura(execution_context):
    """Verifica que el sistema detecta la dependencia faltante de Factura."""
    dep_service = DependencyService()
    class MockCtx:
        def get_dato(self, key, default=""):
            return default
    try:
        dep_service.verificar_prerequisito("nota_credito", MockCtx())
        pytest.fail("Se esperaba FlowDependencyError pero no se lanzó.")
    except FlowDependencyError:
        pass  # Correcto


@when("el usuario emite una factura PPD exitosamente")
def emitir_ppd_dependencias(driver, execution_context):
    """Emite un PPD para verificar la propagación del UUID."""
    from app.flows.ppd.ppd_flow import PPDFlow
    from app.services.data_service import DataService

    data_svc = DataService()
    test_data = data_svc.load("ppd", "ppd_valido")

    flow = PPDFlow(driver, execution_context)
    result = flow.run(test_data=test_data)
    assert result["estado"] == "exitoso"


@then("el UUID del PPD está disponible en el contexto de ejecución")
def verificar_uuid_ppd_contexto(execution_context):
    """Verifica que el UUID del PPD está en el contexto."""
    # TODO: Verificar execution_context.get_dato("uuid_cfdi_ppd") cuando flujo esté completo


@then("el flujo de Complemento de Pago puede acceder al UUID del PPD automáticamente")
def verificar_acceso_uuid_ppd(execution_context):
    """Verifica que CP puede acceder al UUID del PPD del contexto."""
    dep_service = DependencyService()
    # El UUID debería estar disponible tras el flujo PPD
    # TODO: Verificar dependency_resolver con contexto real
