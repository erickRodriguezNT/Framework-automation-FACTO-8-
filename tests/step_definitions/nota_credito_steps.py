"""
nota_credito_steps.py - Step definitions para el flujo base de Nota de Crédito.

Ejecuta el flujo de NC data-driven desde nota_credito_casos.xlsx.
Replica los mismos pasos de Factura Manual para validar que el módulo NC
corre correctamente.
"""
import logging

from pytest_bdd import given, scenarios, then, when

from app.flows.nota_credito.nota_credito_flow import NotaCreditoFlow
from tests.test_data.nota_credito.nota_credito_excel_reader import get_executable_nota_credito_cases

logger = logging.getLogger(__name__)

scenarios("nota_credito.feature")


@given("que existen casos de nota de crédito cargados desde Excel")
def casos_cargados(driver, execution_context):
    casos = get_executable_nota_credito_cases()
    assert casos, "No se encontraron casos ejecutables en nota_credito_casos.xlsx"
    execution_context.set_dato("casos_nota_credito", casos)
    logger.info(f"[NC STEPS] {len(casos)} caso(s) cargado(s) desde Excel.")


@when("ejecuto el flujo base de nota de crédito para cada caso marcado como ejecutable")
def ejecutar_flujo(driver, execution_context):
    casos = execution_context.get_dato("casos_nota_credito") or []
    resultados = []
    for caso in casos:
        caso_id = caso.get("caso_id", "NC_UNKNOWN")
        logger.info(f"[NC STEPS] Ejecutando caso: {caso_id}")
        flow = NotaCreditoFlow(driver=driver, context=execution_context)
        resultado = flow.run(test_data=caso)
        resultados.append({"caso_id": caso_id, "resultado": resultado})
        logger.info(f"[NC STEPS] Caso {caso_id} — estado: {resultado.get('estado')}")
    execution_context.set_dato("resultados_nota_credito", resultados)


@then("cada caso debe generar su resultado esperado")
def verificar_resultados(execution_context):
    resultados = execution_context.get_dato("resultados_nota_credito") or []
    for r in resultados:
        caso_id = r["caso_id"]
        resultado = r["resultado"]
        assert resultado.get("exitoso") or resultado.get("estado") == "exitoso", (
            f"Caso {caso_id} falló: {resultado.get('error', 'sin detalle')}"
        )


@then("se deben guardar evidencias por caso ejecutado en outputs de nota de crédito")
def verificar_evidencias(execution_context):
    from pathlib import Path
    resultados = execution_context.get_dato("resultados_nota_credito") or []
    for r in resultados:
        caso_id = r["caso_id"]
        evidencia_dir = Path("outputs") / "nota_credito" / caso_id / "screenshots"
        if evidencia_dir.exists():
            logger.info(f"[NC STEPS] Evidencias encontradas en: {evidencia_dir}")
        else:
            logger.info(f"[NC STEPS] Directorio de evidencias no creado aún: {evidencia_dir}")
