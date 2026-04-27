"""
xml_report_builder.py - Constructor de reportes XML de ejecución.

Genera un archivo XML estructurado con los resultados de la ejecución,
compatible con herramientas de CI/CD que consumen JUnit XML.

Uso:
    from app.reporting.xml_report_builder import XMLReportBuilder
    builder = XMLReportBuilder()
    path = builder.build(execution_context, output_path)
"""
from pathlib import Path

from lxml import etree

from app.utils.logger import get_logger

logger = get_logger(__name__)


class XMLReportBuilder:
    """
    Constructor de reportes XML (formato JUnit-compatible) para el framework FACTO.
    """

    def build(self, context, output_path: Path) -> Path:
        """
        Genera el archivo XML de resultados en formato JUnit.

        Args:
            context:     ExecutionContext con los datos de la ejecución.
            output_path: Ruta donde se guardará el XML.

        Returns:
            Path del XML generado.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        ctx_dict = context.to_dict()

        # Elemento raíz <testsuite>
        testsuite = etree.Element("testsuite")
        testsuite.set("name", f"FACTO8.{ctx_dict.get('flujo_actual', '')}")
        testsuite.set("tests", str(len(context.pasos_ejecutados)))
        testsuite.set("time", str(round(ctx_dict.get("duracion_segundos", 0), 2)))
        testsuite.set("execution_id", ctx_dict.get("execution_id", ""))

        # Un <testcase> por paso
        for paso in context.pasos_ejecutados:
            testcase = etree.SubElement(testsuite, "testcase")
            testcase.set("name", paso.get("nombre", ""))
            testcase.set("classname", ctx_dict.get("flujo_actual", ""))

            if paso.get("estado") == "fallido":
                failure = etree.SubElement(testcase, "failure")
                failure.set("message", str(paso.get("detalle", "")))

        tree = etree.ElementTree(testsuite)
        tree.write(
            str(output_path),
            pretty_print=True,
            xml_declaration=True,
            encoding="UTF-8",
        )

        logger.info(f"XML JUnit generado: {output_path}")
        return output_path
