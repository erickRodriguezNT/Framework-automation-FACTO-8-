"""
factura_steps.py — Step definitions para el escenario de Generación de Factura CFDI 4.0.

Vincula los steps del feature:
  tests/features/factura.feature

REGLA ARQUITECTÓNICA:
  Estos steps solo invocan FacturaFlow y ExcelService.
  No contienen Selenium directo ni acceso a Page Objects.
  Toda la lógica de negocio vive en FacturaFlow.
  Toda la interacción UI vive en los Page Objects.

Fuente de datos:
  tests/test_data/factura/factura_casos.xlsx  (hoja: Factura)
  Solo se ejecutan filas con ejecutar = SI.

Uso:
    pytest tests/step_definitions/factura_steps.py -m factura -v -s
"""
import pytest
from pytest_bdd import given, scenarios, then, when

from app.flows.factura.factura_flow import FacturaFlow
from app.services.excel_service import get_executable_factura_cases

# Vincula todos los escenarios del feature file con este módulo de steps
scenarios("factura.feature")


# ------------------------------------------------------------------
# Given — Precondición: casos cargados desde Excel
# ------------------------------------------------------------------


@given("que existen casos de factura cargados desde Excel")
def casos_cargados_desde_excel(driver, execution_context):
    """
    Carga los casos ejecutables desde el Excel y los guarda en el contexto.

    Solo se procesan filas marcadas con ejecutar = SI.
    Si no hay casos ejecutables, el test se omite (skip).
    """
    assert driver is not None, "El driver no está disponible."
    assert execution_context is not None, "El execution_context no está disponible."

    casos = get_executable_factura_cases()
    execution_context.set_dato("casos_factura", casos)
    execution_context.set_dato("resultados_factura", [])

    if not casos:
        pytest.skip("No hay casos ejecutables en el Excel (ninguna fila con ejecutar=SI).")


# ------------------------------------------------------------------
# When — Acción: ejecutar flujo por cada caso
# ------------------------------------------------------------------


@when("ejecuto el flujo manual de factura para cada caso marcado como ejecutable")
def ejecutar_flujo_para_cada_caso(driver, execution_context):
    """
    Itera sobre los casos ejecutables y llama a FacturaFlow por cada uno.

    Reglas:
    - El flow gestiona login y navegación internamente.
    - Cada caso se ejecuta como una factura independiente.
    - Si un caso falla, se registra el error y se continúa con el siguiente.
    - Los resultados se guardan en el contexto para validación en los Then.
    """
    casos: list[dict] = execution_context.get_dato("casos_factura", [])
    resultados: list[dict] = []

    for caso in casos:
        caso_id = caso.get("caso_id", "DESCONOCIDO")
        try:
            flow = FacturaFlow(driver, execution_context)
            resultado = flow.ejecutar_factura_manual(caso)
            resultado["caso_id"] = caso_id
            resultado["resultado_esperado"] = caso.get("resultado_esperado", "")
            resultados.append(resultado)
        except Exception as exc:
            resultados.append({
                "caso_id": caso_id,
                "estado": "fallido",
                "error": str(exc),
                "resultado_esperado": caso.get("resultado_esperado", ""),
            })

    execution_context.set_dato("resultados_factura", resultados)


# ------------------------------------------------------------------
# Then — Verificaciones del resultado
# ------------------------------------------------------------------


@then("cada caso debe generar su resultado esperado")
def verificar_resultados_esperados(execution_context):
    """
    Verifica que cada caso con resultado_esperado=TIMBRADO_EXITOSO
    finalizó con estado exitoso.

    Si algún caso esperado como exitoso falló, el assert falla con
    un resumen de todos los errores encontrados.
    """
    resultados: list[dict] = execution_context.get_dato("resultados_factura", [])

    if not resultados:
        pytest.skip("No se ejecutaron casos de factura.")

    fallos = []
    for r in resultados:
        if r.get("resultado_esperado", "").upper() == "TIMBRADO_EXITOSO":
            if r.get("estado") != "exitoso":
                fallos.append(
                    f"  • [{r['caso_id']}] Estado: {r.get('estado')!r} — "
                    f"Error: {r.get('error')!r}"
                )

    assert not fallos, (
        f"{len(fallos)} caso(s) fallaron con resultado esperado TIMBRADO_EXITOSO:\n"
        + "\n".join(fallos)
    )


@then("se deben guardar evidencias por caso ejecutado")
def verificar_evidencias_guardadas(execution_context):
    """
    Verifica que se generaron directorios de evidencias por caso ejecutado.

    Si un directorio no existe, se registra como advertencia (no falla el test).
    Las evidencias son soporte QA, no parte de la lógica de negocio.
    """
    from pathlib import Path
    import warnings

    resultados: list[dict] = execution_context.get_dato("resultados_factura", [])

    faltantes = []
    for r in resultados:
        caso_id = r.get("caso_id", "")
        screenshots_dir = Path("outputs") / "factura" / caso_id / "screenshots"
        if not screenshots_dir.exists():
            faltantes.append(
                f"  • [{caso_id}] Directorio no encontrado: {screenshots_dir}"
            )

    if faltantes:
        warnings.warn(
            f"Advertencia: {len(faltantes)} caso(s) sin directorio de evidencias:\n"
            + "\n".join(faltantes)
        )
