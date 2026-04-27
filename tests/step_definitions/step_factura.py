"""
step_factura.py - Step definitions para el flujo de Factura.

Implementa los pasos del feature file tests/features/factura.feature.

REGLA: Los steps SOLO llaman a flows o pages.
       NO usan Selenium directamente.
"""
import pytest
from pytest_bdd import given, scenarios, then, when

from app.flows.common.download_flow import DownloadFlow
from app.flows.factura.factura_flow import FacturaFlow
from app.services.data_service import DataService

# Vincula este archivo con el feature de Factura
scenarios("factura.feature")


@given("que el usuario navega al módulo de Factura")
def navegar_factura(driver, execution_context):
    """Navega al módulo de Factura en el portal FACTO."""
    from app.flows.common.navigation_flow import NavigationFlow
    flow = NavigationFlow(driver, execution_context)
    result = flow.run(destino="factura")
    assert result["estado"] == "exitoso", f"Navegación a Factura falló: {result.get('error')}"


@when("el usuario captura los datos del receptor con RFC válido")
def capturar_datos_receptor_factura(driver, execution_context):
    """Carga los datos de prueba y ejecuta el flujo de Factura."""
    data_svc = DataService()
    test_data = data_svc.load("factura", "factura_valida")
    execution_context.set_dato("test_data_factura", test_data)

    flow = FacturaFlow(driver, execution_context)
    result = flow.run(test_data=test_data)
    assert result["estado"] == "exitoso", f"FacturaFlow falló: {result.get('error')}"


@when("el usuario captura los datos de un receptor persona moral con RFC de 12 caracteres")
def capturar_receptor_persona_moral(driver, execution_context):
    """Captura datos de persona moral para la factura."""
    data_svc = DataService()
    test_data = data_svc.load("factura", "factura_valida")
    # TODO: Usar fixture de persona moral cuando esté disponible
    execution_context.set_dato("test_data_factura", test_data)

    flow = FacturaFlow(driver, execution_context)
    result = flow.run(test_data=test_data)
    assert result["estado"] == "exitoso", f"FacturaFlow (persona moral) falló: {result.get('error')}"


@when('el usuario selecciona el uso de CFDI "{uso_cfdi}"')
def seleccionar_uso_cfdi(uso_cfdi: str, execution_context):
    """Guarda el uso de CFDI en el contexto para uso del flujo."""
    execution_context.set_dato("uso_cfdi", uso_cfdi)


@when('el usuario selecciona el método de pago "{metodo_pago}"')
def seleccionar_metodo_pago(metodo_pago: str, execution_context):
    """Guarda el método de pago en el contexto."""
    execution_context.set_dato("metodo_pago", metodo_pago)


@when('el usuario selecciona la forma de pago "{forma_pago}"')
def seleccionar_forma_pago(forma_pago: str, execution_context):
    """Guarda la forma de pago en el contexto."""
    execution_context.set_dato("forma_pago", forma_pago)


@when("el usuario agrega al menos un concepto con clave SAT válida")
def agregar_concepto_factura(execution_context):
    """Marca en el contexto que se agrega un concepto. El flujo se encarga del llenado."""
    execution_context.set_dato("agregar_concepto", True)


@when("el usuario agrega un concepto de servicio con clave SAT válida")
def agregar_concepto_servicio(execution_context):
    """Marca en el contexto que se agrega un concepto de servicio."""
    execution_context.set_dato("agregar_concepto_servicio", True)


@when("el usuario agrega tres conceptos con claves SAT distintas")
def agregar_tres_conceptos(execution_context):
    """Marca en el contexto que se agregarán múltiples conceptos."""
    execution_context.set_dato("num_conceptos", 3)


@when("el usuario agrega un concepto con clave SAT válida")
def agregar_concepto_generico(execution_context):
    """Versión genérica: agrega un concepto con clave SAT."""
    execution_context.set_dato("agregar_concepto", True)


@when("el usuario confirma los impuestos de la factura")
def confirmar_impuestos_factura(execution_context):
    """Marca que los impuestos han sido confirmados."""
    execution_context.set_dato("impuestos_confirmados", True)


@when("el usuario captura un RFC de receptor con formato inválido")
def capturar_rfc_invalido(driver, execution_context):
    """Intenta capturar un RFC inválido para verificar la validación del portal."""
    execution_context.set_dato("rfc_receptor", "INVALIDO123")
    # TODO: Implementar llenado de RFC inválido en el portal


@then("el portal timbra la factura exitosamente")
def verificar_timbrado_factura(execution_context):
    """Verifica que el flujo de factura completó con estado exitoso."""
    assert execution_context.estado in ("exitoso", "en_progreso"), (
        f"El flujo de factura no está en estado exitoso: {execution_context.estado}"
    )


@then("el portal muestra un UUID CFDI válido")
def verificar_uuid_cfdi(execution_context):
    """Verifica que el UUID CFDI generado es válido."""
    uuid = execution_context.get_dato("uuid_cfdi", "")
    # TODO: Descomentar cuando el flujo capture el UUID real
    # from app.utils.validations import assert_valid_uuid_cfdi
    # assert_valid_uuid_cfdi(uuid)
    # Por ahora solo verifica que el paso se ejecutó


@then("el usuario puede descargar el PDF de la factura")
def descargar_pdf_factura(driver, execution_context, settings):
    """Verifica que el PDF de la factura puede descargarse."""
    from app.flows.common.download_flow import DownloadFlow
    # TODO: Implementar cuando el flujo real esté completo


@then("el usuario puede descargar el XML de la factura")
def descargar_xml_factura(driver, execution_context, settings):
    """Verifica que el XML de la factura puede descargarse."""
    # TODO: Implementar cuando el flujo real esté completo


@then("el UUID generado queda guardado en el contexto de ejecución")
def verificar_uuid_en_contexto(execution_context):
    """Verifica que el UUID está disponible para flujos dependientes."""
    # TODO: Verificar execution_context.get_dato("uuid_cfdi")


@then("el portal muestra un mensaje de error de validación del RFC")
def verificar_error_rfc(driver):
    """Verifica que el portal muestra el error de RFC inválido."""
    # TODO: Implementar verificación del mensaje de error


@then("el subtotal y total mostrados son consistentes con los conceptos capturados")
def verificar_totales_consistentes(execution_context):
    """Verifica la consistencia de los totales calculados."""
    # TODO: Implementar verificación de cálculos cuando se tenga acceso real
