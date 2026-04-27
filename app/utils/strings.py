"""
strings.py - Utilidades de manipulación de strings para el framework FACTO 8.

Helpers para:
- Generación de UUIDs
- Sanitización de nombres de archivo
- Normalización de texto
- Conversión de formatos
"""
import re
import uuid


def generate_uuid() -> str:
    """
    Genera un UUID v4 como string.

    Útil para identificadores de ejecución y datos de prueba únicos.

    Returns:
        String UUID v4, ej: 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
    """
    return str(uuid.uuid4())


def sanitize_filename(name: str) -> str:
    """
    Sanitiza un string para uso seguro como nombre de archivo.

    Reemplaza caracteres no permitidos por guión bajo y
    elimina guiones bajos repetidos.

    Args:
        name: Nombre a sanitizar.

    Returns:
        Nombre seguro para sistema de archivos (sin espacios ni caracteres especiales).
    """
    sanitized = re.sub(r"[^\w\-]", "_", name, flags=re.UNICODE)
    sanitized = re.sub(r"_+", "_", sanitized)
    return sanitized.strip("_")


def normalize_text(text: str) -> str:
    """
    Normaliza un texto: strip, lowercase, elimina espacios múltiples.

    Args:
        text: Texto a normalizar.

    Returns:
        Texto normalizado en minúsculas y sin espacios extras.
    """
    return " ".join(text.strip().lower().split())


def truncate(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Trunca un string a una longitud máxima.

    Args:
        text:       Texto a truncar.
        max_length: Longitud máxima del resultado.
        suffix:     Sufijo a agregar si se trunca.

    Returns:
        Texto truncado con sufijo si excede max_length.
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def to_snake_case(text: str) -> str:
    """
    Convierte un texto a snake_case.

    Args:
        text: Texto con espacios, guiones o mezcla.

    Returns:
        String en snake_case.

    Examples:
        "Factura Emitida" → "factura_emitida"
        "complemento-pago" → "complemento_pago"
    """
    text = re.sub(r"[\s\-]+", "_", text.strip())
    text = re.sub(r"[^\w]", "", text)
    return text.lower()


def mask_sensitive(value: str, visible_chars: int = 4) -> str:
    """
    Enmascara un string sensible mostrando solo los últimos N caracteres.

    Útil para logging de contraseñas o datos sensibles.

    Args:
        value:         Valor a enmascarar.
        visible_chars: Cantidad de caracteres visibles al final.

    Returns:
        String enmascarado, ej: '****word'
    """
    if len(value) <= visible_chars:
        return "*" * len(value)
    return "*" * (len(value) - visible_chars) + value[-visible_chars:]
