"""
settings.py - Configuración central del framework FACTO 8.

Carga todas las variables de entorno y las expone como propiedades tipadas.
Las credenciales y URLs sensibles NUNCA deben hardcodearse aquí.

Uso:
    from app.config.settings import Settings
    settings = Settings()
    print(settings.base_url)
"""
import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

# override=True para que .env sobreescriba variables del sistema (ej. USERNAME en Windows)
load_dotenv(override=True)


@dataclass
class Settings:
    """
    Configuración central del framework.

    Todas las propiedades se leen desde variables de entorno.
    Valores por defecto seguros para entorno de desarrollo local.
    """

    # --- Entorno ---
    environment: str = field(
        default_factory=lambda: os.getenv("ENVIRONMENT", "dev")
    )

    # --- URL base ---
    base_url: str = field(
        default_factory=lambda: os.getenv("BASE_URL", "http://localhost")
    )

    # --- Credenciales ---
    username: str = field(
        default_factory=lambda: os.getenv("USERNAME", "")
    )
    password: str = field(
        default_factory=lambda: os.getenv("PASSWORD", "")
    )

    # --- Navegador ---
    browser: str = field(
        default_factory=lambda: os.getenv("BROWSER", "chrome").lower()
    )
    headless: bool = field(
        default_factory=lambda: os.getenv("HEADLESS", "false").lower() == "true"
    )

    # --- Timeouts (segundos) ---
    timeout: int = field(
        default_factory=lambda: int(os.getenv("TIMEOUT", "30"))
    )
    download_timeout: int = field(
        default_factory=lambda: int(os.getenv("DOWNLOAD_TIMEOUT", "60"))
    )

    # --- Directorios de salida ---
    output_dir: str = field(
        default_factory=lambda: os.getenv("OUTPUT_DIR", "outputs")
    )

    # --- Allure ---
    allure_results_dir: str = field(
        default_factory=lambda: os.getenv("ALLURE_RESULTS_DIR", "allure-results")
    )

    # --- Logging ---
    log_level: str = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO").upper()
    )

    def validate(self) -> None:
        """
        Valida que las variables críticas estén configuradas.
        Debe llamarse antes de iniciar una ejecución completa.

        Raises:
            ValueError: Si una variable crítica está vacía o ausente.
        """
        if not self.base_url:
            raise ValueError("BASE_URL no está configurada.")
        if not self.username:
            raise ValueError("USERNAME no está configurado.")
        if not self.password:
            raise ValueError("PASSWORD no está configurado.")

    def __repr__(self) -> str:
        return (
            f"Settings("
            f"environment={self.environment!r}, "
            f"base_url={self.base_url!r}, "
            f"browser={self.browser!r}, "
            f"headless={self.headless}, "
            f"timeout={self.timeout})"
        )
