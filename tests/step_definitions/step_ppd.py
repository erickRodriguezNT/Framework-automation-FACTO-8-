"""
step_ppd.py - Step definitions para el flujo de Factura PPD.

Implementa los pasos del feature file tests/features/ppd.feature.

REGLA: Los steps SOLO llaman a flows. No usan Selenium directamente.
"""
from pytest_bdd import given, then, when

from app.flows.ppd.ppd_flow import PPDFlow
from app.services.data_service import DataService

# NOTA: scenarios("ppd.feature") fue removido — los steps de ppd.feature
# ahora están en ppd_steps.py (flujo data-driven desde Excel).


@given("que el usuario navega al módulo de Factura PPD")
def navegar_ppd(driver, execution_context):
    """Navega al módulo de PPD en el portal FACTO."""
    from app.flows.common.navigation_flow import NavigationFlow
    flow = NavigationFlow(driver, execution_context)
    result = flow.run(destino="ppd")
    assert result["estado"] == "exitoso", f"Navegación a PPD falló: {result.get('error')}"


@when("el usuario captura los datos del receptor con RFC válido")
def capturar_datos_receptor_ppd(driver, execution_context):
    """Carga datos de prueba y ejecuta el flujo PPD."""
    data_svc = DataService()
    test_data = data_svc.load("ppd", "ppd_valido")

    flow = PPDFlow(driver, execution_context)
    result = flow.run(test_data=test_data)
    assert result["estado"] == "exitoso", f"PPDFlow falló: {result.get('error')}"


@when("el usuario captura los datos del concepto y el importe")
def capturar_concepto_ppd(execution_context):
    """El concepto ya está en el test_data del flujo anterior."""
    execution_context.set_dato("concepto_ppd_capturado", True)


@when("el usuario emite una factura con método de pago PPD")
def emitir_factura_ppd(driver, execution_context):
    """Ejecuta el flujo PPD completo."""
    data_svc = DataService()
    test_data = data_svc.load("ppd", "ppd_valido")

    flow = PPDFlow(driver, execution_context)
    result = flow.run(test_data=test_data)
    assert result["estado"] == "exitoso", f"PPDFlow falló: {result.get('error')}"


@then("el portal timbra la factura PPD exitosamente")
def verificar_timbrado_ppd(execution_context):
    """Verifica que el PPD fue timbrado exitosamente."""
    assert execution_context.estado in ("exitoso", "en_progreso"), (
        f"PPD no está en estado exitoso: {execution_context.estado}"
    )


@then("el portal muestra un UUID CFDI de PPD válido")
def verificar_uuid_ppd(execution_context):
    """Verifica el UUID del CFDI PPD."""
    # TODO: Implementar validación cuando flujo esté completo


@then("el UUID del PPD queda disponible para el flujo de Complemento de Pago")
def verificar_uuid_ppd_en_contexto(execution_context):
    """Verifica que el UUID del PPD está en el contexto para el flujo dependiente."""
    # TODO: Verificar execution_context.get_dato("uuid_cfdi_ppd") cuando flujo esté completo


@then("el portal muestra el estado del CFDI como pendiente de pago")
def verificar_estado_pendiente(driver, execution_context):
    """Verifica que el estado del PPD es pendiente de pago."""
    # TODO: Implementar verificación de estado cuando flujo esté completo


@then("el usuario puede descargar el PDF de la factura PPD")
def descargar_pdf_ppd(driver, execution_context):
    """Verifica descarga del PDF del PPD."""
    # TODO: Implementar con flujo real


@then("el usuario puede descargar el XML de la factura PPD")
def descargar_xml_ppd(driver, execution_context):
    """Verifica descarga del XML del PPD."""
    # TODO: Implementar con flujo real


@then("el módulo PPD carga correctamente")
def verificar_modulo_ppd(driver):
    """Verifica que el módulo de PPD carga correctamente (smoke)."""
    # TODO: Implementar verificación de carga del módulo
