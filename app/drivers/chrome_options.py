"""
chrome_options.py - Construcción de ChromeOptions para el framework FACTO 8.

Centraliza la configuración de opciones de Chrome para:
- Modo headless (CI/Docker)
- Modo normal (desarrollo local)
- Descargas automáticas de PDF y XML
"""
from selenium.webdriver.chrome.options import Options as ChromeOptions

from app.config.browser_config import (
    CHROME_ARGUMENTS_HEADLESS,
    CHROME_ARGUMENTS_LOCAL,
    CHROME_DOWNLOAD_PREFERENCES,
)


def build_chrome_options(
    headless: bool = False,
    download_dir: str = "outputs",
) -> ChromeOptions:
    """
    Construye y retorna ChromeOptions configuradas para el framework.

    Args:
        headless: Si True, agrega flags para modo headless sin ventana.
        download_dir: Ruta absoluta donde se guardarán las descargas.

    Returns:
        Instancia de ChromeOptions lista para usar en el driver.
    """
    options = ChromeOptions()

    # Argumentos según el modo de ejecución
    arguments = CHROME_ARGUMENTS_HEADLESS if headless else CHROME_ARGUMENTS_LOCAL
    for arg in arguments:
        options.add_argument(arg)

    # Preferencias de descarga automática
    prefs = dict(CHROME_DOWNLOAD_PREFERENCES)
    prefs["download.default_directory"] = download_dir
    options.add_experimental_option("prefs", prefs)

    # Elimina banners de automatización de Chrome
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    return options
