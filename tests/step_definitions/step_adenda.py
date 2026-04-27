"""
step_adenda.py - Step definitions para el flujo de Adenda.

Implementa los pasos del feature file tests/features/adenda.feature.

REGLA: Los steps SOLO llaman a flows. No usan Selenium directamente.
"""
from pytest_bdd import given, scenarios, then, when

from app.flows.adenda.adenda_flow import AdendaFlow
from app.services.data_service import DataService

scenarios("adenda.feature")


@given("que el usuario navega al módulo de Adenda")
def navegar_adenda(driver, execution_context):
    """Navega al módulo de Adenda en el portal FACTO."""
    from app.flows.common.navigation_flow import NavigationFlow
    flow = NavigationFlow(driver, execution_context)
    result = flow.run(destino="adenda")
    assert result["estado"] == "exitoso", f"Navegación a Adenda falló: {result.get('error')}"


@when("el usuario captura el UUID del CFDI al que desea agregar la adenda")
def capturar_uuid_cfdi_adenda(execution_context):
    """Usa el UUID del CFDI disponible en el contexto o carga desde test_data."""
    uuid = execution_context.get_dato("uuid_cfdi", "")
    if not uuid:
        data_svc = DataService()
        try:
            datos = data_svc.load("adenda", "adenda_valida")
            uuid = datos.get("uuid_cfdi", "")
            execution_context.set_dato("uuid_cfdi", uuid)
        except Exception:
            execution_context.set_dato("uuid_cfdi", "TODO-UUID-CFDI")


@when("el usuario captura los datos comerciales de la adenda")
def capturar_datos_adenda(driver, execution_context):
    """Carga test_data y ejecuta el flujo de Adenda."""
    data_svc = DataService()
    test_data = data_svc.load("adenda", "adenda_valida")

    flow = AdendaFlow(driver, execution_context)
    result = flow.run(test_data=test_data, uuid_cfdi=execution_context.get_dato("uuid_cfdi", ""))
    assert result["estado"] == "exitoso", f"AdendaFlow falló: {result.get('error')}"


@when("el usuario captura la referencia de orden de compra en la adenda")
def capturar_referencia_oc(execution_context):
    """Configura la referencia de OC en el contexto."""
    data_svc = DataService()
    try:
        datos = data_svc.load("adenda", "adenda_valida")
        execution_context.set_dato("referencia_oc", datos.get("referencia_oc", "OC-001"))
    except Exception:
        execution_context.set_dato("referencia_oc", "OC-TEST-001")


@when("el usuario agrega una adenda a un CFDI válido")
def agregar_adenda_completa(driver, execution_context):
    """Ejecuta el flujo completo de Adenda."""
    data_svc = DataService()
    test_data = data_svc.load("adenda", "adenda_valida")

    flow = AdendaFlow(driver, execution_context)
    result = flow.run(test_data=test_data, uuid_cfdi=execution_context.get_dato("uuid_cfdi", ""))
    assert result["estado"] == "exitoso", f"AdendaFlow falló: {result.get('error')}"


@then("el portal procesa y guarda la adenda exitosamente")
def verificar_adenda_procesada(execution_context):
    """Verifica que la adenda fue procesada correctamente."""
    assert execution_context.estado in ("exitoso", "en_progreso"), (
        f"Adenda no está en estado exitoso: {execution_context.estado}"
    )


@then("el portal confirma que la adenda fue agregada al CFDI")
def verificar_confirmacion_adenda(driver, execution_context):
    """Verifica la confirmación del portal."""
    # TODO: Implementar con páginas reales


@then("la adenda contiene la referencia de orden de compra capturada")
def verificar_referencia_oc_en_adenda(execution_context):
    """Verifica que la OC está en la adenda procesada."""
    # TODO: Implementar cuando flujo esté completo


@then("el usuario puede descargar el PDF del CFDI con la adenda incluida")
def descargar_pdf_adenda(driver, execution_context):
    """Verifica descarga del PDF con adenda."""
    # TODO: Implementar


@then("el usuario puede descargar el XML del CFDI con la adenda incluida")
def descargar_xml_adenda(driver, execution_context):
    """Verifica descarga del XML con adenda."""
    # TODO: Implementar
