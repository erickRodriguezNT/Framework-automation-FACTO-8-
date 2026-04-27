"""
driver_factory.py - Factory para creación de instancias WebDriver.

Centraliza la lógica de creación del driver y soporta:
- Chrome local (modo normal y headless)
- Configuración de descargas automáticas
- Cierre limpio del navegador

TODO: Agregar soporte para Firefox
TODO: Agregar soporte para Remote WebDriver (Selenium Grid / Cloud Run)
"""
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

from app.config.paths import FrameworkPaths
from app.config.settings import Settings
from app.drivers.chrome_options import build_chrome_options
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DriverFactory:
    """
    Factory que crea instancias WebDriver según la configuración.

    Separa la creación del driver de los tests, permitiendo
    cambiar el browser o la estrategia de conexión sin tocar los tests.
    """

    def __init__(self, settings: Settings):
        """
        Args:
            settings: Configuración del framework.
        """
        self.settings = settings
        self.paths = FrameworkPaths(settings.output_dir)

    def create_driver(self) -> WebDriver:
        """
        Crea y retorna un WebDriver según el browser configurado.

        Returns:
            Instancia de WebDriver lista para usar.

        Raises:
            ValueError: Si el browser configurado no está soportado.
        """
        browser = self.settings.browser.lower()
        logger.info(
            f"Creando driver: browser={browser!r}, headless={self.settings.headless}"
        )

        if browser == "chrome":
            return self._create_chrome_driver()

        raise ValueError(
            f"Browser '{browser}' no soportado. Opciones disponibles: ['chrome']"
        )

    def _create_chrome_driver(self) -> webdriver.Chrome:
        """Crea un driver de Chrome con opciones optimizadas."""
        # Asegura que el directorio de descargas exista
        self.paths.create_all_output_dirs()
        download_dir = str(self.paths.output_root.resolve())

        options = build_chrome_options(
            headless=self.settings.headless,
            download_dir=download_dir,
        )

        # Selenium 4.x incluye selenium-manager que descarga automáticamente
        # el chromedriver correcto para la versión de Chrome instalada.
        # No se usa webdriver-manager para evitar el bug de arquitectura en Windows.
        driver = webdriver.Chrome(options=options)

        # Deshabilitar implicit wait — usar siempre explicit waits
        driver.implicitly_wait(0)
        driver.set_page_load_timeout(self.settings.timeout)

        if not self.settings.headless:
            driver.maximize_window()

        logger.info("Driver Chrome creado exitosamente.")
        return driver

    @staticmethod
    def quit_driver(driver: WebDriver) -> None:
        """
        Cierra el WebDriver de forma segura.

        Captura excepciones para evitar que el cierre fallido
        enmascare errores del test en curso.

        Args:
            driver: Instancia de WebDriver a cerrar. Acepta None.
        """
        if driver is None:
            return
        try:
            driver.quit()
            logger.info("Driver cerrado exitosamente.")
        except Exception as exc:
            logger.warning(f"Error al cerrar driver (puede ignorarse): {exc}")
