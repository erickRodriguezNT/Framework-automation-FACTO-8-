"""
environment_config.py - Mapeo de entornos y configuración por ambiente.

Permite resolver la URL base correcta según el entorno (dev/staging/prod),
centraliza URLs de servicios por ambiente y facilita agregar nuevos entornos.

Uso:
    from app.config.environment_config import EnvironmentManager
    manager = EnvironmentManager()
    config = manager.get_config("staging")
    print(config.base_url)
"""
import os
from dataclasses import dataclass


@dataclass
class EnvironmentConfig:
    """Configuración completa de un entorno."""
    name: str
    base_url: str
    api_url: str = ""
    description: str = ""


class EnvironmentManager:
    """
    Gestiona la configuración de múltiples entornos del portal FACTO.

    Permite resolver parámetros de conexión por entorno y registrar
    nuevos entornos dinámicamente (útil para PR environments en CI/CD).
    """

    # Registro de entornos disponibles
    # TODO: Actualizar las URLs reales cuando estén disponibles
    ENVIRONMENTS: dict[str, EnvironmentConfig] = {
        "dev": EnvironmentConfig(
            name="dev",
            base_url=os.getenv("BASE_URL_DEV", "https://dev.factoportal.ejemplo.com"),
            api_url=os.getenv("API_URL_DEV", ""),
            description="Entorno de desarrollo / integración continua",
        ),
        "staging": EnvironmentConfig(
            name="staging",
            base_url=os.getenv("BASE_URL_STAGING", "https://staging.factoportal.ejemplo.com"),
            api_url=os.getenv("API_URL_STAGING", ""),
            description="Entorno de pruebas de aceptación (UAT)",
        ),
        "prod": EnvironmentConfig(
            name="prod",
            base_url=os.getenv("BASE_URL_PROD", "https://www.factoportal.ejemplo.com"),
            api_url=os.getenv("API_URL_PROD", ""),
            description="Producción — usar con extrema precaución",
        ),
    }

    def get_config(self, environment: str) -> EnvironmentConfig:
        """
        Retorna la configuración del entorno solicitado.

        Args:
            environment: Nombre del entorno ('dev', 'staging', 'prod').

        Returns:
            EnvironmentConfig correspondiente.

        Raises:
            ValueError: Si el entorno no está registrado.
        """
        env = environment.lower()
        if env not in self.ENVIRONMENTS:
            available = list(self.ENVIRONMENTS.keys())
            raise ValueError(
                f"Entorno '{environment}' no reconocido. "
                f"Entornos disponibles: {available}"
            )
        return self.ENVIRONMENTS[env]

    def get_base_url(self, environment: str) -> str:
        """Atajo para obtener la URL base de un entorno."""
        return self.get_config(environment).base_url

    def list_environments(self) -> list[str]:
        """Retorna la lista de nombres de entornos disponibles."""
        return list(self.ENVIRONMENTS.keys())

    def register_environment(self, config: EnvironmentConfig) -> None:
        """
        Registra un nuevo entorno dinámicamente.

        Útil para entornos de PR / ambientes efímeros en CI/CD.

        Args:
            config: Configuración del nuevo entorno.
        """
        self.ENVIRONMENTS[config.name] = config
