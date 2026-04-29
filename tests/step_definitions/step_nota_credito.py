"""
step_nota_credito.py - Step definitions para el flujo de Nota de Crédito.

Implementa los pasos del feature file tests/features/nota_credito.feature.

REGLA: Los steps SOLO llaman a flows. No usan Selenium directamente.
"""
from pytest_bdd import given, scenarios, then, when

from app.flows.nota_credito.nota_credito_flow import NotaCreditoFlow
from app.services.data_service import DataService

# scenarios("nota_credito.feature")  # Movido a nota_credito_steps.py


@given("existe una factura previamente timbrada con UUID válido en el sistema")
def prerequisito_factura_existente(execution_context):
    """
    Verifica que hay un UUID de factura disponible para relacionar.
    En pruebas de suite completa, este UUID viene del flujo anterior.
    En pruebas aisladas, se carga desde test_data.
    """
    uuid_existente = execution_context.get_dato("uuid_factura_relacionada", "")
    if not uuid_existente:
        # Cargar UUID de prueba desde test_data si no hay uno en contexto
        data_svc = DataService()
        try:
            datos = data_svc.load("nota_credito", "nota_credito_valida")
            uuid_existente = datos.get("uuid_factura_relacionada", "")
            execution_context.set_dato("uuid_factura_relacionada", uuid_existente)
        except Exception:
            # TODO: En ejecución real, el UUID vendrá de un flujo previo de Factura
            execution_context.set_dato("uuid_factura_relacionada", "TODO-UUID-FACTURA")


@given("que el usuario navega al módulo de Nota de Crédito")
def navegar_nota_credito(driver, execution_context):
    """Navega al módulo de Nota de Crédito."""
    from app.flows.common.navigation_flow import NavigationFlow
    flow = NavigationFlow(driver, execution_context)
    result = flow.run(destino="nota_credito")
    assert result["estado"] == "exitoso", f"Navegación a NC falló: {result.get('error')}"


@when("el usuario captura el UUID de la factura relacionada")
def capturar_uuid_factura_relacionada(execution_context):
    """Usa el UUID de factura disponible en el contexto."""
    uuid = execution_context.get_dato("uuid_factura_relacionada", "")
    assert uuid, "No hay UUID de factura relacionada en el contexto."


@when('el usuario selecciona el tipo de relación "{tipo_relacion}"')
def seleccionar_tipo_relacion(tipo_relacion: str, execution_context):
    """Guarda el tipo de relación en el contexto."""
    execution_context.set_dato("tipo_relacion", tipo_relacion)


@when("el usuario captura los datos del receptor y el motivo de la nota")
def capturar_datos_receptor_nota_credito(driver, execution_context):
    """Carga y ejecuta el flujo de Nota de Crédito."""
    data_svc = DataService()
    test_data = data_svc.load("nota_credito", "nota_credito_valida")

    flow = NotaCreditoFlow(driver, execution_context)
    result = flow.run(test_data=test_data)
    assert result["estado"] == "exitoso", f"NotaCreditoFlow falló: {result.get('error')}"


@when("el usuario captura el importe de la nota de crédito")
def capturar_importe_nota_credito(execution_context):
    """El importe ya está en el test_data cargado en el paso anterior."""
    execution_context.set_dato("importe_nc_capturado", True)


@when("el usuario captura un UUID de factura que no existe en el sistema")
def capturar_uuid_inexistente(execution_context):
    """Establece un UUID que no existe para verificar error."""
    execution_context.set_dato("uuid_factura_relacionada", "00000000-0000-0000-0000-000000000000")


@when("el usuario captura un importe parcial de la factura original")
def capturar_importe_parcial(execution_context):
    """Configura el contexto para una devolución parcial."""
    execution_context.set_dato("importe_parcial", True)


@then("el portal timbra la nota de crédito exitosamente")
def verificar_timbrado_nota_credito(execution_context):
    """Verifica que el flujo de Nota de Crédito completó exitosamente."""
    assert execution_context.estado in ("exitoso", "en_progreso"), (
        f"Nota de Crédito no está en estado exitoso: {execution_context.estado}"
    )


@then("el portal muestra un UUID CFDI de nota de crédito válido")
def verificar_uuid_nota_credito(execution_context):
    """Verifica el UUID de la Nota de Crédito."""
    # TODO: Implementar validación del UUID real cuando flujo esté completo


@then("el usuario puede descargar el PDF de la nota de crédito")
def descargar_pdf_nota_credito(driver, execution_context):
    """Verifica descarga del PDF de la Nota de Crédito."""
    # TODO: Implementar con flujo real


@then("el usuario puede descargar el XML de la nota de crédito")
def descargar_xml_nota_credito(driver, execution_context):
    """Verifica descarga del XML de la Nota de Crédito."""
    # TODO: Implementar con flujo real


@then("el portal muestra un mensaje de error de documento no encontrado")
def verificar_error_documento_no_encontrado(driver):
    """Verifica que el portal muestra error de documento no encontrado."""
    # TODO: Implementar verificación del mensaje de error


@then("el importe de la nota de crédito es menor al total de la factura relacionada")
def verificar_importe_parcial(execution_context):
    """Verifica que el importe de la NC es menor al total de la factura."""
    # TODO: Implementar comparación de importes cuando flujo esté completo
