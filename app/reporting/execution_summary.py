"""
execution_summary.py - Generador de resumen ejecutivo de una suite de pruebas.

Agrega los resultados de múltiples ejecuciones y genera un resumen
con métricas de la suite completa:
- Total de escenarios
- Escenarios exitosos / fallidos
- Tiempo total
- Tasa de éxito

Uso:
    from app.reporting.execution_summary import ExecutionSummary
    summary = ExecutionSummary()
    summary.add(context)
    summary.save(output_path)
"""
import json
from pathlib import Path

from app.utils.logger import get_logger

logger = get_logger(__name__)


class ExecutionSummary:
    """
    Generador de resumen de una suite de ejecuciones del framework FACTO.
    """

    def __init__(self) -> None:
        self._ejecuciones: list[dict] = []

    def add(self, context) -> None:
        """
        Agrega una ejecución al resumen.

        Args:
            context: ExecutionContext con los datos de la ejecución.
        """
        self._ejecuciones.append(context.to_dict())

    def to_dict(self) -> dict:
        """
        Construye el diccionario de resumen de la suite.

        Returns:
            Diccionario con métricas agregadas.
        """
        total = len(self._ejecuciones)
        exitosos = sum(1 for e in self._ejecuciones if e.get("estado") == "exitoso")
        fallidos = total - exitosos
        duracion_total = sum(e.get("duracion_segundos", 0) for e in self._ejecuciones)
        tasa_exito = round((exitosos / total * 100), 1) if total > 0 else 0.0

        return {
            "total_escenarios":  total,
            "exitosos":          exitosos,
            "fallidos":          fallidos,
            "tasa_exito_pct":    tasa_exito,
            "duracion_total_s":  round(duracion_total, 2),
            "ejecuciones":       self._ejecuciones,
        }

    def save(self, output_path: Path) -> Path:
        """
        Guarda el resumen como JSON.

        Args:
            output_path: Ruta del archivo JSON de salida.

        Returns:
            Path del archivo guardado.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = self.to_dict()

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

        logger.info(
            f"Resumen de suite guardado: {output_path} "
            f"({data['exitosos']}/{data['total_escenarios']} exitosos, "
            f"{data['tasa_exito_pct']}% tasa de éxito)"
        )
        return output_path
