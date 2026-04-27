"""
dates.py - Utilidades de fecha y hora para el framework FACTO 8.

Helpers para:
- Timestamps formateados para nombres de archivos y evidencias
- Fechas para campos del portal de facturación
- Identificadores basados en tiempo
"""
from datetime import date, datetime
from typing import Optional


def now_str(fmt: str = "%Y%m%d_%H%M%S") -> str:
    """
    Retorna la fecha/hora actual formateada como string.

    Args:
        fmt: Formato strftime. Por defecto: '20240424_153000'

    Returns:
        String con la fecha/hora formateada.
    """
    return datetime.now().strftime(fmt)


def date_for_filename() -> str:
    """
    Retorna la fecha actual en formato seguro para nombres de archivo.

    Returns:
        String tipo '2024-04-24'
    """
    return date.today().isoformat()


def timestamp_id() -> str:
    """
    Retorna un timestamp compacto para uso en identificadores únicos.

    Returns:
        String tipo '20240424153045678' (con milisegundos)
    """
    return datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]


def today_iso() -> str:
    """Retorna la fecha actual en formato ISO 8601 (YYYY-MM-DD)."""
    return date.today().isoformat()


def now_iso() -> str:
    """Retorna la fecha/hora actual en formato ISO 8601 completo."""
    return datetime.now().isoformat()


def format_date_for_portal(dt: Optional[date] = None) -> str:
    """
    Formatea una fecha para los campos de fecha del portal FACTO.

    TODO: Verificar el formato exacto requerido por el portal (DD/MM/YYYY vs YYYY-MM-DD).

    Args:
        dt: Fecha a formatear. Si None, usa la fecha de hoy.

    Returns:
        Fecha formateada según el portal.
    """
    target_date = dt or date.today()
    # TODO: Ajustar al formato real del portal FACTO (actualmente DD/MM/YYYY)
    return target_date.strftime("%d/%m/%Y")


def date_range_str(start: date, end: date) -> str:
    """
    Retorna un rango de fechas como string legible.

    Args:
        start: Fecha de inicio.
        end:   Fecha de fin.

    Returns:
        String tipo '2024-04-01 al 2024-04-24'
    """
    return f"{start.isoformat()} al {end.isoformat()}"
