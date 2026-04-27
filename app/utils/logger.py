"""
logger.py - Configuración centralizada de logging con loguru.

Provee un logger estructurado con:
- Output a consola con colores (nivel configurable)
- Output a archivo con rotación diaria y retención 30 días
- Formato consistente con timestamp, módulo y función

Uso:
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Mensaje de ejemplo")
"""
import sys
from pathlib import Path

from loguru import logger as _loguru_logger

# Flag para evitar configurar múltiples veces
_configured = False


def configure_logger(log_dir: str = "outputs/logs", level: str = "INFO") -> None:
    """
    Configura el logger global de loguru.

    Idempotente: llamadas repetidas son ignoradas.

    Args:
        log_dir: Directorio donde se guardarán los archivos de log.
        level:   Nivel mínimo de log ('DEBUG', 'INFO', 'WARNING', 'ERROR').
    """
    global _configured
    if _configured:
        return

    # Eliminar handlers por defecto de loguru
    _loguru_logger.remove()

    # --- Handler de consola con colores ---
    _loguru_logger.add(
        sys.stdout,
        level=level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        colorize=True,
    )

    # --- Handler de archivo con rotación diaria ---
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    _loguru_logger.add(
        str(log_path / "facto8_{time:YYYY-MM-DD}.log"),
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation="00:00",      # Nuevo archivo cada día a medianoche
        retention="30 days",   # Conservar 30 días de logs
        encoding="utf-8",
    )

    _configured = True


def get_logger(name: str):
    """
    Retorna el logger de loguru configurado para un módulo específico.

    Asegura que el logger esté configurado antes de retornarlo.

    Args:
        name: Nombre del módulo (pasar __name__ desde el módulo que lo usa).

    Returns:
        Logger de loguru listo para usar.
    """
    configure_logger()
    return _loguru_logger.bind(module=name)
