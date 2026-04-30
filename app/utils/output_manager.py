"""
output_manager.py — Gestión centralizada de directorios de salida del framework.

Garantiza que cada ejecución genere una carpeta única con timestamp, evitando
que corridas anteriores sean sobrescritas.

Estructura generada:
    outputs/
      factura/
        20260429_214530/          ← run_dir  (una por ejecución completa)
          FACTURA_001/            ← case_dir (una por caso del Excel)
            screenshots/          ← Única subcarpeta
            FACTURA_001.pdf       ← PDF suelto en case_dir
            FACTURA_001.xml       ← XML suelto en case_dir
            reporte_FACTURA_001.json  ← log/reporte suelto en case_dir
          FACTURA_002/
            ...
      nota_credito/
        20260429_215010/
          NC_001/
            screenshots/
            NC_001.pdf
            NC_001.xml

Uso típico (en steps / before_all hooks):

    from app.utils.output_manager import create_run_output_dir, create_case_output_dir

    # 1. Una sola vez por ejecución completa del feature
    run_dir = create_run_output_dir("factura")

    # 2. Una vez por cada caso / fila del Excel
    case_dir = create_case_output_dir(run_dir, caso["caso_id"])

    # 3. Acceder al sub-directorio de screenshots
    screenshot_dir = get_screenshot_dir(case_dir)
    # PDF y XML se guardan directamente en case_dir (sin subcarpeta)
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

# Raíz del proyecto: sube desde app/utils/ → app/ → automation_framework/
_PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Nombre de la carpeta raíz de outputs (relativa a la raíz del proyecto)
_OUTPUTS_ROOT = "outputs"

# Formato del timestamp de corrida
_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

# Única subcarpeta por caso — PDF, XML y logs van sueltos en case_dir
_CASE_SUBDIRS = ("screenshots",)


# ──────────────────────────────────────────────────────────────────────
# Funciones públicas
# ──────────────────────────────────────────────────────────────────────


def create_run_output_dir(flow_name: str, timestamp: str | None = None) -> Path:
    """
    Crea el directorio raíz de una corrida (run) para el flujo indicado.

    Se genera UNA sola vez al inicio de la ejecución completa del feature.
    Todos los casos del Excel dentro de la misma corrida comparten este directorio.

    Args:
        flow_name:  Nombre del flujo / módulo (ej: ``"factura"``, ``"nota_credito"``).
        timestamp:  Timestamp fijo en formato ``YYYYMMDD_HHMMSS``.
                    Si se omite, se usa ``datetime.now()``. Útil en tests unitarios.

    Returns:
        ``Path`` al directorio creado, ej:
        ``<project_root>/outputs/factura/20260429_214530/``

    Example::

        run_dir = create_run_output_dir("factura")
        # → outputs/factura/20260429_214530/
    """
    if timestamp is None:
        timestamp = datetime.now().strftime(_TIMESTAMP_FORMAT)

    run_dir = _PROJECT_ROOT / _OUTPUTS_ROOT / flow_name / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def create_case_output_dir(run_dir: Path, case_id: str, row_index: int = 0) -> Path:
    """
    Crea el directorio de un caso dentro del run_dir e inicializa sus sub-carpetas.

    Args:
        run_dir:    Directorio raíz de la corrida (devuelto por
                    :func:`create_run_output_dir`).
        case_id:    Identificador del caso, tomado del campo ``caso_id`` del Excel.
                    Si viene vacío o solo espacios, se genera un nombre automático
                    ``fila_NNN`` usando ``row_index``.
        row_index:  Número de fila (base 1) para el nombre automático cuando
                    ``case_id`` es vacío.

    Returns:
        ``Path`` al directorio del caso, ej:
        ``<run_dir>/FACTURA_001/``

    Sub-carpetas creadas automáticamente:
        - ``screenshots/``  (PDF, XML y logs quedan sueltos en case_dir)

    Example::

        case_dir = create_case_output_dir(run_dir, "FACTURA_001")
        # → outputs/factura/20260429_214530/FACTURA_001/
    """
    safe_id = _sanitize_case_id(case_id, row_index)
    case_dir = run_dir / safe_id
    case_dir.mkdir(parents=True, exist_ok=True)

    for subdir in _CASE_SUBDIRS:
        (case_dir / subdir).mkdir(exist_ok=True)

    return case_dir


# ──────────────────────────────────────────────────────────────────────
# Accessors de sub-directorios
# ──────────────────────────────────────────────────────────────────────


def get_screenshot_dir(case_dir: Path) -> Path:
    """Retorna el directorio de screenshots del caso (ya creado)."""
    return case_dir / "screenshots"


def get_log_dir(case_dir: Path) -> Path:
    """Logs van sueltos en case_dir (sin subcarpeta)."""
    return case_dir


def get_pdf_dir(case_dir: Path) -> Path:
    """PDFs van sueltos en case_dir (sin subcarpeta)."""
    return case_dir


def get_xml_dir(case_dir: Path) -> Path:
    """XMLs van sueltos en case_dir (sin subcarpeta)."""
    return case_dir


# ──────────────────────────────────────────────────────────────────────
# Helpers internos
# ──────────────────────────────────────────────────────────────────────


def _sanitize_case_id(case_id: str, row_index: int = 0) -> str:
    """
    Devuelve un nombre de carpeta seguro a partir del caso_id.

    - Si el caso_id está vacío, genera ``fila_001``, ``fila_002``, etc.
    - Reemplaza caracteres no permitidos en rutas de Windows / Linux.
    - Trunca a 80 caracteres para evitar rutas demasiado largas.

    Args:
        case_id:    Valor crudo del campo caso_id del Excel.
        row_index:  Índice de fila para el nombre automático.

    Returns:
        Nombre de carpeta seguro.
    """
    raw = str(case_id).strip()

    if not raw or raw.lower() in ("nan", "none", ""):
        return f"fila_{row_index:03d}"

    # Reemplaza caracteres problemáticos en rutas
    for char in r'\/:*?"<>|':
        raw = raw.replace(char, "_")

    # Elimina espacios y trunca
    return raw.replace(" ", "_")[:80]
