"""
waits.py - Esperas personalizadas para el framework FACTO 8.

Complementa las esperas de Selenium con helpers específicos
para patrones comunes del portal de facturación:
- Loader/spinner que debe desaparecer antes de continuar
- Descarga de archivos completada
- Modal activo en pantalla
- Cambio de URL
"""
import time
from pathlib import Path
from typing import Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.utils.exceptions import DownloadTimeoutError
from app.utils.logger import get_logger

logger = get_logger(__name__)


def wait_for_element_visible(
    driver: WebDriver,
    locator: tuple,
    timeout: int = 30,
):
    """
    Espera a que un elemento sea visible en la página.

    Args:
        driver:  Instancia de WebDriver.
        locator: Tupla (By.XX, "valor").
        timeout: Tiempo máximo de espera en segundos.

    Returns:
        WebElement visible.
    """
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located(locator)
    )


def wait_for_loader_to_disappear(
    driver: WebDriver,
    loader_locator: Optional[tuple] = None,
    timeout: int = 30,
) -> None:
    """
    Espera a que un indicador de carga (spinner/loader) desaparezca.

    Args:
        driver:         Instancia de WebDriver.
        loader_locator: Locator del elemento loader.
                        Si None, usa el selector placeholder definido aquí.
        timeout:        Tiempo máximo de espera.

    TODO: Reemplazar LOADER_LOCATOR con el selector real del portal FACTO.
    """
    # TODO: Actualizar con el selector real del loader del portal FACTO
    LOADER_LOCATOR = loader_locator or (By.CSS_SELECTOR, ".loading, .spinner, [data-loading='true']")

    try:
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located(LOADER_LOCATOR)
        )
        logger.debug("Loader desapareció correctamente.")
    except TimeoutException:
        logger.warning(f"Loader no desapareció después de {timeout}s (puede continuar)")


def wait_for_download_complete(
    download_dir: str,
    filename_pattern: str = "",
    timeout: int = 60,
    poll_interval: float = 1.0,
) -> Path:
    """
    Espera a que se complete una descarga de archivo.

    Monitorea el directorio de descargas hasta que:
    1. No haya archivos .crdownload (descarga en progreso de Chrome)
    2. Aparezca un archivo que coincida con el patrón esperado

    Args:
        download_dir:     Directorio donde se guardan las descargas.
        filename_pattern: Patrón del nombre del archivo esperado (opcional).
                          Si está vacío, detecta cualquier archivo nuevo.
        timeout:          Tiempo máximo de espera en segundos.
        poll_interval:    Intervalo de verificación en segundos.

    Returns:
        Path al archivo descargado.

    Raises:
        DownloadTimeoutError: Si la descarga no se completa a tiempo.
    """
    download_path = Path(download_dir)
    elapsed = 0.0

    while elapsed < timeout:
        # Verificar que no haya descargas en progreso (.crdownload de Chrome)
        in_progress = list(download_path.glob("*.crdownload"))
        if in_progress:
            logger.debug(f"Descarga en progreso: {in_progress[0].name}")
            time.sleep(poll_interval)
            elapsed += poll_interval
            continue

        # Buscar el archivo con el patrón especificado
        if filename_pattern:
            matches = list(download_path.glob(f"*{filename_pattern}*"))
            if matches:
                latest = max(matches, key=lambda p: p.stat().st_mtime)
                logger.info(f"Descarga completada: {latest.name}")
                return latest
        else:
            # Sin patrón: devuelve el archivo más reciente del directorio
            files = [
                f for f in download_path.iterdir()
                if f.is_file() and not f.name.startswith(".")
            ]
            if files:
                latest = max(files, key=lambda p: p.stat().st_mtime)
                logger.info(f"Descarga detectada: {latest.name}")
                return latest

        time.sleep(poll_interval)
        elapsed += poll_interval

    raise DownloadTimeoutError(
        f"La descarga no se completó en {timeout}s. "
        f"Directorio: {download_dir}, patrón: '{filename_pattern}'"
    )


def wait_for_modal_visible(
    driver: WebDriver,
    modal_locator: Optional[tuple] = None,
    timeout: int = 10,
) -> None:
    """
    Espera a que un modal esté visible en pantalla.

    TODO: Actualizar MODAL_LOCATOR con el selector real del portal FACTO.

    Args:
        driver:        Instancia de WebDriver.
        modal_locator: Locator del modal. Si None, usa el placeholder.
        timeout:       Tiempo máximo de espera.
    """
    # TODO: Reemplazar con el selector real del modal del portal FACTO
    MODAL_LOCATOR = modal_locator or (By.CSS_SELECTOR, "[role='dialog'], .modal, .popup")
    try:
        WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located(MODAL_LOCATOR)
        )
        logger.debug("Modal visible.")
    except TimeoutException:
        logger.warning(f"Modal no apareció después de {timeout}s")


def wait_for_url_contains(
    driver: WebDriver,
    url_fragment: str,
    timeout: int = 15,
) -> bool:
    """
    Espera a que la URL actual contenga un fragmento específico.

    Args:
        driver:       Instancia de WebDriver.
        url_fragment: Texto que debe aparecer en la URL.
        timeout:      Tiempo máximo de espera.

    Returns:
        True si la URL contiene el fragmento, False si agotó timeout.
    """
    try:
        WebDriverWait(driver, timeout).until(EC.url_contains(url_fragment))
        return True
    except TimeoutException:
        return False
