"""
ppd_excel_reader.py — Lector de casos de prueba PPD desde Excel.

Responsabilidades:
- Cargar ppd_casos.xlsx (hoja "PPD")
- Filtrar solo filas marcadas ejecutar = SI
- Normalizar valores (NaN → "", SI/NO → bool, AUTO → fecha actual)
- Devolver lista de dicts planos, uno por caso ejecutable

Uso:
    from tests.test_data.ppd.ppd_excel_reader import get_executable_ppd_cases
    casos = get_executable_ppd_cases()
    for caso in casos:
        print(caso["caso_id"], caso["rfc_receptor"], caso["metodo_pago"])
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

_PROJECT_ROOT = Path(__file__).parents[3]  # automation_framework/
_DEFAULT_EXCEL_PATH = Path(__file__).parent / "ppd_casos.xlsx"
_SHEET_NAME = "PPD"

# ---------------------------------------------------------------------------
# Columnas booleanas: "SI" -> True, "NO" / vacio -> False
# ---------------------------------------------------------------------------
_BOOL_COLUMNS = {
    "ejecutar",
    "descargar_pdf",
    "descargar_xml",
}

# ---------------------------------------------------------------------------
# Columnas que deben mantenerse como string
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
# Funcion principal
# ---------------------------------------------------------------------------


def load_ppd_cases_from_excel(
    path: str | Path | None = None,
    sheet_name: str = _SHEET_NAME,
) -> list[dict[str, Any]]:
    """
    Carga todos los casos PPD del Excel (ejecutables o no).

    Args:
        path:       Ruta al archivo .xlsx. Si None, usa ppd_casos.xlsx.
        sheet_name: Nombre de la hoja. Default: "PPD".

    Returns:
        Lista de dicts normalizados.

    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError:        Si la hoja no existe o hay error de lectura.
    """
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError(
            "pandas no esta instalado. Ejecutar: pip install pandas openpyxl"
        ) from exc

    excel_path = Path(path) if path else _DEFAULT_EXCEL_PATH

    if not excel_path.exists():
        raise FileNotFoundError(
            f"Archivo de casos PPD no encontrado: {excel_path}\n"
            f"Crear el archivo en: tests/test_data/ppd/ppd_casos.xlsx"
        )

    logger.info("[PPD EXCEL] Cargando casos desde: %s", excel_path)

    try:
        df = pd.read_excel(
            excel_path,
            sheet_name=sheet_name,
            dtype=str,
            keep_default_na=False,
        )
    except Exception as exc:
        raise ValueError(f"Error al leer el Excel PPD '{excel_path}': {exc}") from exc

    if df.empty:
        logger.warning("[PPD EXCEL] El Excel no tiene filas de datos.")
        return []

    df.columns = [str(c).strip() for c in df.columns]
    logger.info("[PPD EXCEL] %d filas cargadas. Columnas: %s", len(df), list(df.columns))

    casos: list[dict[str, Any]] = []
    for idx, row in df.iterrows():
        caso = _normalize_row(row.to_dict(), idx)
        casos.append(caso)

    logger.info("[PPD EXCEL] %d casos totales cargados.", len(casos))
    return casos


def get_executable_ppd_cases(
    path: str | Path | None = None,
) -> list[dict[str, Any]]:
    """
    Carga y filtra solo los casos con ejecutar=SI del Excel PPD.

    Args:
        path: Ruta opcional al archivo .xlsx.

    Returns:
        Lista de casos ejecutables (dicts normalizados).
    """
    todos = load_ppd_cases_from_excel(path)
    ejecutables = [c for c in todos if c.get("ejecutar") is True]
    logger.info(
        "[PPD EXCEL] %d/%d casos ejecutables (ejecutar=SI).",
        len(ejecutables), len(todos),
    )
    return ejecutables


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------


def _normalize_row(row: dict, row_index: int) -> dict[str, Any]:
    """
    Normaliza una fila del Excel a tipos Python limpios.

    Transformaciones:
    - Columnas booleanas: "SI" -> True, cualquier otro valor -> False
    - "AUTO" en fecha_emision -> fecha actual en formato dd/mm/YYYY
    - Espacios extra: strip() en todos los strings
    - NaN / cadenas vacías: se dejan como "" (pandas ya lo hace con keep_default_na=False)
    - Columnas numericas: se dejan como string (el flow convierte segun necesidad)
    """
    normalized: dict[str, Any] = {"_row_index": row_index}

    for key, value in row.items():
        key = str(key).strip()
        value = str(value).strip() if value is not None else ""

        if key in _BOOL_COLUMNS:
            normalized[key] = value.upper() == "SI"
        elif key == "fecha_emision":
            if value.upper() in ("AUTO", ""):
                normalized[key] = datetime.now().strftime("%d/%m/%Y")
            else:
                normalized[key] = value
        elif key in _STRING_COLUMNS:
            # Eliminar decimales espurios de pandas (ej: "03104.0" -> "03104")
            if value.endswith(".0"):
                try:
                    normalized[key] = str(int(float(value)))
                except ValueError:
                    normalized[key] = value
            else:
                normalized[key] = value
        else:
            normalized[key] = value

    return normalized
