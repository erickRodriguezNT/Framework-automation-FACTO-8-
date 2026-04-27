"""
home_page.py - Page Object del dashboard / página de inicio del portal FACTO.

Responsabilidades:
- Detectar que el login fue exitoso (usuario está en home)
- Acceder al menú de navegación principal
- Obtener información básica de la sesión activa

TODO: Reemplazar placeholders cuando se tenga el HTML real del portal.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from app.core.base_page import BasePage


class HomePage(BasePage):
    """
    Page Object para el dashboard / página de inicio del portal FACTO.
    """

    # ------------------------------------------------------------------
    # Locators
    # TODO: Reemplazar con selectores reales del portal
    # ------------------------------------------------------------------

    # Elemento que confirma que el usuario está logueado (ej: nombre de usuario)
    # TODO: Identificar el elemento de bienvenida o indicador de sesión activa
    WELCOME_MESSAGE = (By.CSS_SELECTOR, "[data-testid='welcome-user'], .user-name, #welcome-msg, .navbar-user")

    # Menú de navegación principal
    # TODO: Actualizar con el selector real del menú principal
    MAIN_MENU = (By.CSS_SELECTOR, "[data-testid='main-menu'], nav.main-nav, #main-navigation, .sidebar-menu")

    # Botón de cierre de sesión
    # TODO: Identificar el botón de logout del portal
    LOGOUT_BUTTON = (By.CSS_SELECTOR, "[data-testid='logout-btn'], #btn-logout, .logout-link, a[href*='logout']")

    # ------------------------------------------------------------------
    # Verificaciones de estado
    # ------------------------------------------------------------------

    def is_logged_in(self) -> bool:
        """
        Verifica si el usuario está correctamente autenticado.

        Después de Auth0 el usuario regresa al portal (run.app),
        no a auth0.com. Si la URL es del portal se considera logueado.

        Returns:
            True si el usuario está logueado.
        """
        current_url = self.get_current_url()
        # Si seguimos en auth0.com, no hemos terminado el login
        if "auth0.com" in current_url:
            return False
        # Si estamos en el portal (cualquier ruta de run.app o localhost)
        portal_ok = "run.app" in current_url or "localhost" in current_url
        element_ok = self.is_present(self.WELCOME_MESSAGE, timeout=5)
        return portal_ok or element_ok

    def get_user_name(self) -> str:
        """
        Obtiene el nombre del usuario logueado desde la barra de navegación.

        Returns:
            Nombre del usuario visible en la UI, o '' si no se encuentra.
        """
        if self.is_visible(self.WELCOME_MESSAGE, timeout=3):
            return self.get_text(self.WELCOME_MESSAGE)
        return ""

    # ------------------------------------------------------------------
    # Navegación
    # ------------------------------------------------------------------

    def navigate_to_home(self, base_url: str) -> None:
        """Navega directamente a la página de inicio."""
        # TODO: Actualizar con la ruta real del home del portal
        self.navigate_to(f"{base_url.rstrip('/')}/home")

    def click_logout(self) -> None:
        """Hace click en el botón de cierre de sesión."""
        self.click(self.LOGOUT_BUTTON)

    def is_main_menu_visible(self) -> bool:
        """Verifica si el menú principal está visible."""
        return self.is_visible(self.MAIN_MENU, timeout=5)
