"""
ppd_steps.py — Step definitions para el escenario de Generación de CFDI PPD.

Vincula los steps del feature:
  tests/features/ppd.feature

REGLA ARQUITECTÓNICA:
  Estos steps solo invocan PPDFlow y ppd_excel_reader.
  No contienen Selenium directo ni acceso a Page Objects.
  Toda la lógica de negocio vive en PPDFlow -> CfdiManualFlow.
  Toda la interacción UI vive en los Page Objects.

Fuente de datos:
  tests/test_data/ppd/ppd_casos.xlsx  (hoja: PPD)
  Solo se ejecutan filas con ejecutar = SI.

Uso:
    pytest tests/step_definitions/ppd_steps.py -m ppd -v -s
"""
import pytest
from pytest_bdd import given, scenarios, then, when

from app.flows.ppd.ppd_flow import PPDFlow
from app.utils.output_manager import create_run_output_dir
from app.utils.logger import get_logger
from tests.test_data.ppd.ppd_excel_reader import get_executable_ppd_cases

logger = get_logger(__name__)

# Vincula todos los escenarios del feature file con este módulo de steps
scenarios("ppd.feature")


# ------------------------------------------------------------------
# Given — Precondición: casos cargados desde Excel
# ------------------------------------------------------------------


@given("que existen casos PPD cargados desde Excel")
def casos_ppd_cargados_desde_excel(driver, execution_context):
    """
    Carga los casos ejecutables desde el Excel PPD y los guarda en el contexto.

    Crea el run_dir único para esta corrida (UNA sola vez para todos los casos).
    Solo se procesan filas marcadas con ejecutar = SI.
    Si no hay casos ejecutables, el test se omite (skip).
    """
    assert driver is not None, "El driver no está disponible."
    assert execution_context is not None, "El execution_context no está disponible."

    casos = get_executable_ppd_cases()
    execution_context.set_dato("casos_ppd", casos)
    execution_context.set_dato("resultados_ppd", [])

    # Crear carpeta de corrida única para TODOS los casos de esta ejecución
    run_dir = create_run_output_dir("ppd")
    execution_context.set_dato("run_dir_ppd", str(run_dir))
    logger.info(f"[PPD STEPS] Run dir creado: {run_dir}")

    if not casos:
        pytest.skip("No hay casos ejecutables en el Excel PPD (ninguna fila con ejecutar=SI).")


# ------------------------------------------------------------------
# When — Acción: ejecutar flujo por cada caso
# ------------------------------------------------------------------


@when("ejecuto el flujo PPD para cada caso marcado como ejecutable")
def ejecutar_flujo_ppd_para_cada_caso(driver, execution_context):
    """
    Itera sobre los casos ejecutables y llama a PPDFlow por cada uno.

    Reglas:
    - El flow gestiona login y navegación internamente.
    - Cada caso se ejecuta como un CFDI PPD independiente.
    - Si un caso falla, se registra el error y se continúa con el siguiente.
    - Los resultados se guardan en el contexto para validación en los Then.
    """
    casos: list[dict] = execution_context.get_dato("casos_ppd", [])
    resultados: list[dict] = []

    for caso in casos:
        caso_id = caso.get("caso_id", "DESCONOCIDO")
        try:
            flow = PPDFlow(driver, execution_context)
            resultado = flow.ejecutar_ppd(caso)
            resultado["caso_id"] = caso_id
            resultado["resultado_esperado"] = caso.get("resultado_esperado", "")
            resultados.append(resultado)
        except Exception as exc:
            logger.error(f"[PPD STEPS] Caso {caso_id} falló con excepción: {exc}")
            resultados.append({
                "caso_id": caso_id,
                "estado": "fallido",
                "error": str(exc),
                "resultado_esperado": caso.get("resultado_esperado", ""),
            })

    execution_context.set_dato("resultados_ppd", resultados)


# ------------------------------------------------------------------
# Then — Verificaciones del resultado
# ------------------------------------------------------------------


@then("cada caso PPD debe generar su resultado esperado")
def verificar_resultados_ppd_esperados(execution_context):
    """
    Verifica que cada caso con resultado_esperado=TIMBRADO_EXITOSO
    finalizó con estado exitoso.

    Si algún caso esperado como exitoso falló, el assert falla con
    un resumen de todos los errores encontrados.
    """
    resultados: list[dict] = execution_context.get_dato("resultados_ppd", [])

    if not resultados:
        pytest.skip("No se ejecutaron casos PPD.")

    fallos = []
    for r in resultados:
        if r.get("resultado_esperado", "").upper() == "TIMBRADO_EXITOSO":
            if r.get("estado") != "exitoso":
                fallos.append(
                    f"  • [{r['caso_id']}] Estado: {r.get('estado')!r} — "
                    f"Error: {r.get('error')!r}"
                )

    assert not fallos, (
        f"{len(fallos)} caso(s) PPD fallaron con resultado esperado TIMBRADO_EXITOSO:\n"
        + "\n".join(fallos)
    )


@then("se deben guardar evidencias por caso PPD ejecutado")
def verificar_evidencias_ppd_guardadas(execution_context):
    """
    Verifica que se generaron directorios de evidencias por caso PPD ejecutado.

    Si un directorio no existe, se registra como advertencia (no falla el test).
    Las evidencias son soporte QA, no parte de la lógica de negocio.
    """
    from pathlib import Path
    import warnings

    resultados: list[dict] = execution_context.get_dato("resultados_ppd", [])

    faltantes = []
    for r in resultados:
        caso_id = r.get("caso_id", "")
        screenshots_dir = Path("outputs") / "ppd" / caso_id / "screenshots"
        if not screenshots_dir.exists():
            faltantes.append(
                f"  • [{caso_id}] Directorio no encontrado: {screenshots_dir}"
            )

    if faltantes:
        warnings.warn(
            f"Advertencia: {len(faltantes)} caso(s) PPD sin directorio de evidencias:\n"
            + "\n".join(faltantes)
        )
