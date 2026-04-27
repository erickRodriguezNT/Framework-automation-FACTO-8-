"""
exceptions.py - Jerarquía de excepciones del framework FACTO 8.

Todas las excepciones del framework heredan de FactoFrameworkError,
lo que permite capturar cualquier error propio con un único handler.

Jerarquía:
    FactoFrameworkError
    ├── FlowError
    │   ├── FlowNotFoundError
    │   ├── FlowDependencyError
    │   └── FlowExecutionError
    ├── PageError
    │   ├── ElementNotFoundError
    │   ├── ElementNotInteractableError
    │   └── NavigationError
    ├── DownloadError
    │   ├── DownloadTimeoutError
    │   └── DownloadFileNotFoundError
    ├── ValidationError
    │   ├── UUIDValidationError
    │   └── RFCValidationError
    └── ConfigurationError
        └── EnvironmentConfigError
"""


# ------------------------------------------------------------------
# Base
# ------------------------------------------------------------------

class FactoFrameworkError(Exception):
    """Excepción base del framework FACTO 8."""
    pass


# ------------------------------------------------------------------
# Errores de Flow
# ------------------------------------------------------------------

class FlowError(FactoFrameworkError):
    """Error durante la ejecución de un Flow de negocio."""
    pass


class FlowNotFoundError(FlowError):
    """El flujo solicitado no está registrado en el FlowRegistry."""
    pass


class FlowDependencyError(FlowError):
    """Una dependencia requerida por el flujo no está disponible."""
    pass


class FlowExecutionError(FlowError):
    """Error durante la ejecución de un paso del flujo."""
    pass


# ------------------------------------------------------------------
# Errores de Page
# ------------------------------------------------------------------

class PageError(FactoFrameworkError):
    """Error durante la interacción con un Page Object."""
    pass


class ElementNotFoundError(PageError):
    """Un elemento esperado no fue encontrado en la página."""
    pass


class ElementNotInteractableError(PageError):
    """Un elemento existe pero no se puede interactuar con él."""
    pass


class NavigationError(PageError):
    """Error durante la navegación entre páginas o secciones."""
    pass


# ------------------------------------------------------------------
# Errores de Descarga
# ------------------------------------------------------------------

class DownloadError(FactoFrameworkError):
    """Error relacionado con la descarga de archivos."""
    pass


class DownloadTimeoutError(DownloadError):
    """La descarga no se completó dentro del tiempo esperado."""
    pass


class DownloadFileNotFoundError(DownloadError):
    """El archivo descargado no fue encontrado en el directorio esperado."""
    pass


# ------------------------------------------------------------------
# Errores de Validación
# ------------------------------------------------------------------

class ValidationError(FactoFrameworkError):
    """Error de validación de datos o resultados del flujo."""
    pass


class UUIDValidationError(ValidationError):
    """El UUID CFDI no tiene el formato esperado (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)."""
    pass


class RFCValidationError(ValidationError):
    """El RFC no tiene el formato fiscal mexicano esperado."""
    pass


# ------------------------------------------------------------------
# Errores de Configuración
# ------------------------------------------------------------------

class ConfigurationError(FactoFrameworkError):
    """Error de configuración del framework."""
    pass


class EnvironmentConfigError(ConfigurationError):
    """El entorno configurado no es válido o está incompleto."""
    pass
