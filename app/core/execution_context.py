"""
execution_context.py - Contexto de ejecución por escenario.

Mantiene estado, trazabilidad y metadatos durante la ejecución
de un flujo o escenario. Cada test/escenario tiene su propio
ExecutionContext con un UUID de ejecución único.

Almacena:
- Identificador único (UUID4)
- Metadatos del flujo/escenario activos
- Datos dinámicos generados (UUID CFDI, folios, archivos)
- Rutas de evidencia
- Resultados parciales por paso
"""
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class ExecutionContext:
    """
    Contexto de ejecución para un escenario/flujo.

    Se crea uno por test/escenario y se inyecta en cada flow
    a través del fixture de pytest.
    """

    def __init__(
        self,
        flujo_actual: str = "general",
        escenario_actual: str = "",
        output_dir: str = "outputs",
    ):
        # --- Identificadores ---
        self.execution_id: str = str(uuid.uuid4())
        self.inicio_ejecucion: datetime = datetime.now()
        self.fin_ejecucion: Optional[datetime] = None

        # --- Flujo y escenario activos ---
        self.flujo_actual: str = flujo_actual
        self.escenario_actual: str = escenario_actual

        # --- Datos dinámicos generados durante la ejecución ---
        # Ejemplos: {"uuid_cfdi": "...", "folio": "001", "serie": "A"}
        self.datos_dinamicos: dict[str, Any] = {}

        # --- Archivos generados/descargados ---
        # Ejemplos: {"pdf": Path("..."), "xml": Path("...")}
        self.archivos_generados: dict[str, Path] = {}

        # --- Resultados parciales por paso ---
        self.resultados_parciales: dict[str, Any] = {}

        # --- Log de pasos ejecutados ---
        self.pasos_ejecutados: list[dict] = []

        # --- Estado general del escenario ---
        self.estado: str = "en_progreso"  # "en_progreso" | "exitoso" | "fallido"

        # --- Referencia al driver (asignada en conftest.py) ---
        self.driver = None

        # --- Rutas de evidencia ---
        self.output_dir = Path(output_dir)
        self.evidence_dir = self.output_dir / "screenshots" / self.execution_id / flujo_actual

        # --- Mensaje de error (si aplica) ---
        self.error_message: Optional[str] = None

        # --- Test data de entrada ---
        self.test_data: dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Setters de estado
    # ------------------------------------------------------------------

    def set_flujo(self, flujo: str) -> None:
        """Actualiza el flujo activo y recalcula la ruta de evidencia."""
        self.flujo_actual = flujo
        self.evidence_dir = self.output_dir / "screenshots" / self.execution_id / flujo

    def set_escenario(self, escenario: str) -> None:
        """Actualiza el escenario activo."""
        self.escenario_actual = escenario

    # ------------------------------------------------------------------
    # Gestión de datos dinámicos
    # ------------------------------------------------------------------

    def set_dato(self, clave: str, valor: Any) -> None:
        """
        Almacena un dato dinámico generado durante la ejecución.

        Args:
            clave: Nombre del dato (ej: 'uuid_cfdi', 'folio', 'serie').
            valor: Valor del dato.
        """
        self.datos_dinamicos[clave] = valor

    def get_dato(self, clave: str, default: Any = None) -> Any:
        """Recupera un dato dinámico por clave."""
        return self.datos_dinamicos.get(clave, default)

    def registrar_archivo(self, tipo: str, ruta: Path) -> None:
        """
        Registra un archivo generado o descargado.

        Args:
            tipo: Tipo de archivo ('pdf', 'xml', 'screenshot', 'zip').
            ruta: Path al archivo.
        """
        self.archivos_generados[tipo] = ruta

    # ------------------------------------------------------------------
    # Log de pasos
    # ------------------------------------------------------------------

    def registrar_paso(self, nombre: str, estado: str, detalle: str = "") -> None:
        """
        Registra la ejecución de un paso del flujo.

        Args:
            nombre: Nombre descriptivo del paso.
            estado: 'exitoso' | 'fallido' | 'omitido' | 'en_progreso'
            detalle: Información adicional del paso.
        """
        paso = {
            "nombre": nombre,
            "estado": estado,
            "detalle": detalle,
            "timestamp": datetime.now().isoformat(),
        }
        self.pasos_ejecutados.append(paso)
        self.resultados_parciales[nombre] = estado

    # ------------------------------------------------------------------
    # Finalización
    # ------------------------------------------------------------------

    def marcar_exitoso(self) -> None:
        """Marca el contexto como exitoso y registra el tiempo de fin."""
        self.estado = "exitoso"
        self.fin_ejecucion = datetime.now()

    def marcar_fallido(self, error: str) -> None:
        """Marca el contexto como fallido con el mensaje de error."""
        self.estado = "fallido"
        self.fin_ejecucion = datetime.now()
        self.error_message = error

    # ------------------------------------------------------------------
    # Propiedades calculadas
    # ------------------------------------------------------------------

    @property
    def duracion_segundos(self) -> Optional[float]:
        """Calcula la duración de la ejecución en segundos."""
        if self.fin_ejecucion:
            delta = self.fin_ejecucion - self.inicio_ejecucion
            return round(delta.total_seconds(), 2)
        return None

    # ------------------------------------------------------------------
    # Serialización
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serializa el contexto a un diccionario para reportes JSON."""
        return {
            "execution_id": self.execution_id,
            "flujo": self.flujo_actual,
            "escenario": self.escenario_actual,
            "inicio": self.inicio_ejecucion.isoformat(),
            "fin": self.fin_ejecucion.isoformat() if self.fin_ejecucion else None,
            "duracion_segundos": self.duracion_segundos,
            "estado": self.estado,
            "datos_dinamicos": self.datos_dinamicos,
            "archivos_generados": {k: str(v) for k, v in self.archivos_generados.items()},
            "pasos_ejecutados": self.pasos_ejecutados,
            "error_message": self.error_message,
        }

    def __repr__(self) -> str:
        return (
            f"ExecutionContext("
            f"id={self.execution_id[:8]}..., "
            f"flujo={self.flujo_actual!r}, "
            f"estado={self.estado!r})"
        )
