"""
browser_config.py - Constantes y configuración de navegadores soportados.

Centraliza dimensiones de ventana, argumentos de Chrome y preferencias
de descarga. Importado por chrome_options.py y driver_factory.py.
"""

# --- Navegadores soportados ---
SUPPORTED_BROWSERS = ["chrome"]
# TODO: Agregar "firefox" cuando se requiera

# --- Dimensiones de ventana ---
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080

HEADLESS_WIDTH = 1920
HEADLESS_HEIGHT = 1080

# --- User-Agent para Chrome ---
CHROME_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# --- Argumentos de Chrome para modo headless (CI/Docker) ---
CHROME_ARGUMENTS_HEADLESS = [
    "--headless=new",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-extensions",
    "--disable-infobars",
    "--disable-notifications",
    "--disable-popup-blocking",
    "--ignore-certificate-errors",
    "--allow-running-insecure-content",
    f"--window-size={HEADLESS_WIDTH},{HEADLESS_HEIGHT}",
]

# --- Argumentos de Chrome para ejecución local (modo normal) ---
CHROME_ARGUMENTS_LOCAL = [
    "--disable-infobars",
    "--disable-notifications",
    "--disable-popup-blocking",
    f"--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}",
]

# --- Preferencias de Chrome para descarga automática ---
# download.default_directory se reemplaza en runtime con la ruta real
CHROME_DOWNLOAD_PREFERENCES = {
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    # False  → Chrome puede renderizar PDFs con su visor interno (necesario para
    #          que el visor Angular del portal muestre el preview correctamente).
    # Las descargas reales se controlan vía CDP Page.setDownloadBehavior(allow),
    # que toma precedencia sobre esta preferencia en tiempo de ejecución.
    "plugins.always_open_pdf_externally": False,
    "safebrowsing.enabled": True,
}

# --- Timeouts del driver ---
IMPLICIT_WAIT = 0          # 0 = deshabilitado; usar siempre explicit waits
PAGE_LOAD_TIMEOUT = 30     # segundos
