"""
validations.py - Validadores de datos para el framework FACTO 8.

Valida formatos fiscales mexicanos y datos del portal:
- UUID CFDI (formato estándar SAT)
- RFC (persona física y moral)
- Strings no vacíos
- Contenido esperado en textos
"""
import re

from app.utils.exceptions import (
    RFCValidationError,
    UUIDValidationError,
    ValidationError,
)

# --- Patrones de validación ---

# UUID estándar (aplica para CFDI timbrado)
UUID_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)

# RFC México:
# Persona moral:  3 letras + 6 dígitos (fecha) + 3 alfanuméricos (homoclave)
# Persona física: 4 letras + 6 dígitos (fecha) + 3 alfanuméricos (homoclave)
RFC_PATTERN = re.compile(
    r"^[A-ZÑ&]{3,4}[0-9]{6}[A-Z0-9]{3}$",
    re.IGNORECASE,
)


# ------------------------------------------------------------------
# UUID CFDI
# ------------------------------------------------------------------

def is_valid_uuid_cfdi(uuid_str: str) -> bool:
    """
    Verifica si un string es un UUID CFDI válido.

    Args:
        uuid_str: String a validar.

    Returns:
        True si tiene formato UUID válido.
    """
    return bool(UUID_PATTERN.match(uuid_str.strip()))


def assert_valid_uuid_cfdi(uuid_str: str) -> None:
    """
    Aserta que un string sea un UUID CFDI válido.

    Args:
        uuid_str: UUID a validar.

    Raises:
        UUIDValidationError: Si el UUID no tiene el formato correcto.
    """
    if not is_valid_uuid_cfdi(uuid_str):
        raise UUIDValidationError(
            f"UUID CFDI inválido: '{uuid_str}'. "
            f"Formato esperado: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
        )


# ------------------------------------------------------------------
# RFC
# ------------------------------------------------------------------

def is_valid_rfc(rfc: str) -> bool:
    """
    Verifica si un string tiene formato de RFC mexicano válido.

    Args:
        rfc: RFC a validar.

    Returns:
        True si el formato es válido.
    """
    return bool(RFC_PATTERN.match(rfc.strip()))


def assert_valid_rfc(rfc: str) -> None:
    """
    Aserta que un string sea un RFC mexicano válido.

    Raises:
        RFCValidationError: Si el RFC no tiene el formato correcto.
    """
    if not is_valid_rfc(rfc):
        raise RFCValidationError(
            f"RFC inválido: '{rfc}'. "
            f"Formato esperado: AAAA-NNNNNN-XXX (persona física) o AAA-NNNNNN-XXX (moral)"
        )


# ------------------------------------------------------------------
# Validaciones genéricas
# ------------------------------------------------------------------

def assert_not_empty(value: str, field_name: str = "valor") -> None:
    """
    Aserta que un string no esté vacío ni sea solo espacios.

    Args:
        value:      Valor a verificar.
        field_name: Nombre del campo (para el mensaje de error).

    Raises:
        ValidationError: Si el valor está vacío.
    """
    if not value or not value.strip():
        raise ValidationError(f"El campo '{field_name}' no debe estar vacío.")


def assert_contains(text: str, substring: str, context: str = "") -> None:
    """
    Aserta que un texto contenga un substring esperado.

    Args:
        text:      Texto completo donde buscar.
        substring: Fragmento que debe estar presente.
        context:   Contexto adicional para el mensaje de error.

    Raises:
        ValidationError: Si el texto no contiene el substring.
    """
    if substring not in text:
        msg = f"Se esperaba encontrar '{substring}' en: '{text}'"
        if context:
            msg += f" (contexto: {context})"
        raise ValidationError(msg)


def assert_equals(actual: str, expected: str, field_name: str = "valor") -> None:
    """
    Aserta que dos valores sean iguales.

    Args:
        actual:     Valor real obtenido del portal.
        expected:   Valor esperado.
        field_name: Nombre del campo (para el mensaje de error).

    Raises:
        ValidationError: Si los valores no son iguales.
    """
    if actual != expected:
        raise ValidationError(
            f"'{field_name}' no coincide. "
            f"Esperado: '{expected}', Obtenido: '{actual}'"
        )
