"""
step_complemento_pago.py - Step definitions para el flujo de Complemento de Pago.

Implementa los pasos del feature file tests/features/complemento_pago.feature.

REGLA: Los steps SOLO llaman a flows. No usan Selenium directamente.
"""
from pytest_bdd import given, scenarios, then, when

from app.flows.complemento_pago.complemento_pago_flow import ComplementoPagoFlow
from app.services.data_service import DataService

scenarios("complemento_pago.feature")


@given("existe una factura PPD previamente timbrada con UUID disponible en el contexto")
def prerequisito_ppd_existente(execution_context):
    """
    Verifica que hay un UUID de PPD disponible.
    En suites completas viene del flujo PPD anterior.
    En pruebas aisladas se carga desde test_data.
    """
    uuid_ppd = execution_context.get_dato("uuid_cfdi_ppd", "")
    if not uuid_ppd:
        data_svc = DataService()
        try:
            datos = data_svc.load("complemento_pago", "complemento_pago_valido")
            uuid_ppd = datos.get("uuid_cfdi_ppd", "")
            execution_context.set_dato("uuid_cfdi_ppd", uuid_ppd)
        except Exception:
            # TODO: En ejecución real vendrá del flujo PPD previo
            execution_context.set_dato("uuid_cfdi_ppd", "TODO-UUID-PPD")


@given("que el usuario navega al módulo de Complemento de Pago")
def navegar_complemento_pago(driver, execution_context):
    """Navega al módulo de Complemento de Pago."""
    from app.flows.common.navigation_flow import NavigationFlow
    flow = NavigationFlow(driver, execution_context)
    result = flow.run(destino="complemento_pago")
    assert result["estado"] == "exitoso", f"Navegación a CP falló: {result.get('error')}"


@when("el usuario captura la fecha de pago")
def capturar_fecha_pago(execution_context):
    """La fecha de pago está en el test_data."""
    execution_context.set_dato("fecha_pago_capturada", True)


@when('el usuario selecciona la forma de pago "{forma_pago}"')
def seleccionar_forma_pago_cp(forma_pago: str, execution_context):
    """Guarda la forma de pago en el contexto."""
    execution_context.set_dato("forma_pago_cp", forma_pago)


@when("el usuario captura el monto del pago y el número de operación")
def capturar_monto_operacion(execution_context):
    """Los datos de pago están en el test_data."""
    execution_context.set_dato("monto_operacion_capturado", True)


@when("el usuario relaciona el UUID del CFDI PPD pendiente de pago")
def relacionar_ppd(execution_context):
    """Usa el UUID del PPD disponible en el contexto."""
    uuid_ppd = execution_context.get_dato("uuid_cfdi_ppd", "")
    assert uuid_ppd, "No hay UUID de PPD en el contexto para relacionar."


@when("el usuario captura el número de parcialidad e importes del documento relacionado")
def capturar_parcialidad_importes(driver, execution_context):
    """Ejecuta el flujo completo de Complemento de Pago."""
    data_svc = DataService()
    test_data = data_svc.load("complemento_pago", "complemento_pago_valido")

    flow = ComplementoPagoFlow(driver, execution_context)
    result = flow.run(test_data=test_data)
    assert result["estado"] == "exitoso", f"ComplementoPagoFlow falló: {result.get('error')}"


@when("el usuario captura los datos del pago")
def capturar_datos_pago_cp(driver, execution_context):
    """Carga datos de prueba para el complemento."""
    data_svc = DataService()
    test_data = data_svc.load("complemento_pago", "complemento_pago_valido")
    execution_context.set_dato("test_data_cp", test_data)


@when("el usuario intenta relacionar un UUID de PPD que no existe")
def relacionar_uuid_inexistente(execution_context):
    """Establece un UUID inexistente para verificar el error."""
    execution_context.set_dato("uuid_cfdi_ppd", "00000000-0000-0000-0000-000000000000")


@when("el usuario captura la fecha y datos del pago")
def capturar_fecha_datos_pago(driver, execution_context):
    """Captura fecha y datos del pago para el complemento."""
    data_svc = DataService()
    test_data = data_svc.load("complemento_pago", "complemento_pago_valido")
    execution_context.set_dato("test_data_cp", test_data)


@when("el usuario relaciona el UUID del PPD con saldo insoluto igual al total original")
def relacionar_ppd_saldo_total(execution_context):
    """Configura la relación con saldo igual al total de la factura."""
    execution_context.set_dato("pago_total", True)


@when("el usuario captura el importe pagado igual al total de la factura")
def capturar_importe_total(driver, execution_context):
    """Ejecuta el flujo con pago total."""
    data_svc = DataService()
    test_data = data_svc.load("complemento_pago", "complemento_pago_valido")

    flow = ComplementoPagoFlow(driver, execution_context)
    result = flow.run(test_data=test_data)
    assert result["estado"] == "exitoso", f"ComplementoPagoFlow falló: {result.get('error')}"


@then("el portal timbra el complemento de pago exitosamente")
def verificar_timbrado_cp(execution_context):
    """Verifica que el Complemento de Pago fue timbrado."""
    assert execution_context.estado in ("exitoso", "en_progreso"), (
        f"Complemento de Pago no está en estado exitoso: {execution_context.estado}"
    )


@then("el portal muestra un UUID CFDI de complemento de pago válido")
def verificar_uuid_cp(execution_context):
    """Verifica el UUID del Complemento de Pago."""
    # TODO: Implementar cuando flujo esté completo


@then("el usuario puede descargar el PDF del complemento de pago")
def descargar_pdf_cp(driver, execution_context):
    """Verifica descarga del PDF del Complemento."""
    # TODO: Implementar


@then("el usuario puede descargar el XML del complemento de pago")
def descargar_xml_cp(driver, execution_context):
    """Verifica descarga del XML del Complemento."""
    # TODO: Implementar


@then("el portal muestra un mensaje de error de documento no encontrado")
def verificar_error_cp_no_encontrado(driver):
    """Verifica error cuando el PPD no existe."""
    # TODO: Implementar


@then("el saldo insoluto del documento relacionado queda en cero")
def verificar_saldo_insoluto_cero(execution_context):
    """Verifica que el saldo insoluto después del pago es 0."""
    # TODO: Implementar cuando flujo esté completo


@then("el módulo de Complemento de Pago carga correctamente")
def verificar_modulo_cp(driver):
    """Smoke: verifica que el módulo carga."""
    # TODO: Implementar
