"""
excel_service.py — Servicio de lectura de datos de prueba desde Excel.

Responsabilidades:
- Cargar el archivo factura_casos.xlsx (hoja "Factura")
- Filtrar solo las filas marcadas con ejecutar = SI
- Normalizar los valores (NaN → "", SI/NO → bool, AUTO → fecha actual)
- Devolver una lista de dicts planos, uno por caso ejecutable

Uso:
    from app.services.excel_service import get_executable_factura_cases
    casos = get_executable_factura_cases()
    for caso in casos:
        print(caso["caso_id"], caso["rfc_receptor"])
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from app.utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).parents[2]  # automation_framework/
_DEFAULT_EXCEL_PATH = (
    _PROJECT_ROOT / "tests" / "test_data" / "factura" / "factura_casos.xlsx"
)
_SHEET_NAME = "Factura"

# ---------------------------------------------------------------------------
# Columnas booleanas: "SI" → True, "NO" / vacío → False
# ---------------------------------------------------------------------------
_BOOL_COLUMNS = {
    "ejecutar",
    "descargar_pdf",
    "descargar_xml",
}

# ---------------------------------------------------------------------------
# Columnas que deben mantenerse como string (incluso si pandas infiere número)
# ---------------------------------------------------------------------------
_STRING_COLUMNS = {
    "caso_id",
    "codigo_postal",
    "no_identificacion",
    "clave_prod_serv",
    "clave_unidad",
    "tasa_o_cuota",
    "tipo_cambio",
    "cantidad",
    "valor_unitario",
    "descuento",
    "cargo_no_facturable_importe",
    "forma_pago",
    "metodo_pago",
    "exportacion",
    "moneda",
    "objeto_impuesto",
    "impuesto",
}


# ---------------------------------------------------------------------------
# Función principal
# ---------------------------------------------------------------------------


def load_factura_cases_from_excel(
    path: str | Path | None = None,
    sheet_name: str = _SHEET_NAME,
) -> list[dict[str, Any]]:
    """
    Carga todos los casos del Excel (ejecutables o no).

    Args:
        path:       Ruta al archivo .xlsx. Si None, usa la ruta por defecto.
        sheet_name: Nombre de la hoja. Default: "Factura".

    Returns:
        Lista de dicts, uno por fila del Excel. Valores normalizados.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError:        Si la hoja no existe o faltan columnas requeridas.
    """
    try:
        import pandas as pd  # lazy import para no requerir pandas en el global scope
    except ImportError as exc:
        raise ImportError(
            "pandas no está instalado. Ejecutar: pip install pandas openpyxl"
        ) from exc

    excel_path = Path(path) if path else _DEFAULT_EXCEL_PATH

    if not excel_path.exists():
        raise FileNotFoundError(
            f"Archivo de casos Excel no encontrado: {excel_path}\n"
            f"Crear el archivo en: tests/test_data/factura/factura_casos.xlsx"
        )

    logger.info(f"[EXCEL] Cargando casos desde: {excel_path}")

    try:
        df = pd.read_excel(
            excel_path,
            sheet_name=sheet_name,
            dtype=str,  # leer TODO como string; normalizaremos manualmente
            keep_default_na=False,  # NaN → "" en lugar de float NaN
        )
    except Exception as exc:
        raise ValueError(f"Error al leer el Excel '{excel_path}': {exc}") from exc

    if df.empty:
        logger.warning("[EXCEL] El Excel no tiene filas de datos.")
        return []

    # Normalizar nombres de columnas: strip espacios
    df.columns = [str(c).strip() for c in df.columns]

    logger.info(f"[EXCEL] {len(df)} filas cargadas. Columnas: {list(df.columns)}")

    casos: list[dict[str, Any]] = []
    for idx, row in df.iterrows():
        caso = _normalize_row(row.to_dict(), idx)
        casos.append(caso)

    return casos


def get_executable_factura_cases(
    path: str | Path | None = None,
    sheet_name: str = _SHEET_NAME,
) -> list[dict[str, Any]]:
    """
    Carga los casos del Excel y retorna solo los marcados como ejecutables.

    Regla: solo se ejecutan filas donde la columna 'ejecutar' = "SI" (case-insensitive).

    Args:
        path:       Ruta al archivo .xlsx. Si None, usa la ruta por defecto.
        sheet_name: Nombre de la hoja. Default: "Factura".

    Returns:
        Lista de dicts de casos ejecutables. Puede ser vacía.
    """
    todos = load_factura_cases_from_excel(path=path, sheet_name=sheet_name)
    ejecutables = [c for c in todos if c.get("ejecutar") is True]
    logger.info(
        f"[EXCEL] {len(ejecutables)} / {len(todos)} casos marcados como ejecutables."
    )
    return ejecutables


# ---------------------------------------------------------------------------
# Helpers de normalización
# ---------------------------------------------------------------------------


def _normalize_row(raw: dict[str, Any], idx: int) -> dict[str, Any]:
    """
    Normaliza una fila del Excel a un dict listo para el flujo de Factura.

    Transformaciones aplicadas:
    - Todas las claves: strip de espacios
    - Todos los valores: strip de espacios y convertir NaN/None a ""
    - Columnas bool (_BOOL_COLUMNS): "SI" → True, todo lo demás → False
    - fecha_emision = "AUTO" → fecha/hora actual en formato datetime-local
    - Columnas _STRING_COLUMNS: asegurar que son string (no float)
    - caso_id vacío → generar ID por índice: "CASO_{idx+1}"

    Args:
        raw: Diccionario crudo de la fila (valores como string o NaN).
        idx: Índice de la fila (0-based) para mensajes de log.

    Returns:
        Diccionario normalizado listo para usar en FacturaFlow.
    """
    normalized: dict[str, Any] = {}

    for key, value in raw.items():
        key = str(key).strip()

        # Normalizar valor: NaN, None, "nan", "NaN" → ""
        if value is None or (isinstance(value, float) and __import__("math").isnan(value)):
            value = ""
        else:
            value = str(value).strip()
            if value.lower() == "nan":
                value = ""

        # Columnas booleanas
        if key in _BOOL_COLUMNS:
            normalized[key] = value.upper() in ("SI", "SÍ", "YES", "TRUE", "1")
            continue

        # fecha_emision AUTO → fecha actual compatible con datetime-local
        if key == "fecha_emision":
            if value.upper() == "AUTO" or value == "":
                normalized[key] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                logger.debug(f"[EXCEL] fecha_emision AUTO → {normalized[key]}")
            else:
                normalized[key] = value
            continue

        # referencia AUTO → generar referencia con timestamp
        if key == "referencia" and value.upper() == "AUTO":
            normalized[key] = f"AUTO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            continue

        normalized[key] = value

    # caso_id vacío → ID por índice
    if not normalized.get("caso_id"):
        normalized["caso_id"] = f"CASO_{idx + 1}"
        logger.warning(
            f"[EXCEL] Fila {idx + 1} sin caso_id. Asignado automáticamente: {normalized['caso_id']}"
        )

    return normalized


def _extract_code(valor: str) -> str:
    """
    Extrae el código de un valor tipo "616 - Sin obligaciones fiscales" → "616".
    Si no tiene " - ", devuelve el valor tal cual.

    Útil para selects donde el Excel tiene texto descriptivo pero el
    select nativo espera solo el código.

    Args:
        valor: Texto del Excel (ej: "616 - Sin obligaciones fiscales", "S01 - Sin efectos fiscales").

    Returns:
        Código extraído (ej: "616", "S01", "MXN").
    """
    if " - " in valor:
        return valor.split(" - ")[0].strip()
    return valor.strip()
