"""
login_page.py - Page Object de la página de inicio de sesión del portal FACTO.

Responsabilidades:
- Localizar y manejar los campos del formulario de login
- Ingresar credenciales
- Detectar errores de autenticación

NOTA: Este Page Object NO decide si el login fue exitoso ni redirige.
      Esa lógica vive en LoginFlow (app/flows/common/login_flow.py).

TODO: Reemplazar los placeholders de selectores cuando se tenga acceso
      al HTML real del portal FACTO. Priorizar: id > name > data-testid
      > data-cy > aria-label > CSS estable.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from app.core.base_page import BasePage


class LoginPage(BasePage):
    """
    Page Object para la página de login del portal FACTO.
    """

    # ------------------------------------------------------------------
    # Locators
    # TODO: Reemplazar con selectores reales del portal
    # ------------------------------------------------------------------

    # Campo de usuario / email (Auth0)
    USERNAME_INPUT = (By.ID, "username")

    # Campo de contraseña (Auth0)
    PASSWORD_INPUT = (By.ID, "password")

    # Botón de login (Auth0: "Continuar" — seleccionado por texto para evitar
    # clickear "Continuar con Google" u otros botones submit)
    LOGIN_BUTTON = (By.XPATH, "//button[@type='submit' and not(@aria-hidden='true') and normalize-space(.)='Continuar']")

    # Mensaje de error de autenticación (Auth0)
    ERROR_MESSAGE = (By.CSS_SELECTOR, "[data-testid='login-error'], .error-message, .alert-danger, #login-error, [class*='alert'], .ulp-input-error")

    # ------------------------------------------------------------------
    # Acciones
    # ------------------------------------------------------------------

    def enter_username(self, username: str) -> None:
        """Ingresa el nombre de usuario en el campo correspondiente."""
        self.type_text(self.USERNAME_INPUT, username)

    def enter_password(self, password: str) -> None:
        """Ingresa la contraseña en el campo correspondiente."""
        self.type_text(self.PASSWORD_INPUT, password)

    def click_login(self) -> None:
        """Hace click en el botón de login."""
        self.click(self.LOGIN_BUTTON)

    def login(self, username: str, password: str) -> None:
        """
        Método de conveniencia: ingresa credenciales y hace submit.

        Args:
            username: Nombre de usuario o email.
            password: Contraseña.
        """
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()

    # ------------------------------------------------------------------
    # Verificaciones
    # ------------------------------------------------------------------

    def get_error_message(self) -> str:
        """
        Obtiene el texto del mensaje de error de autenticación.

        Returns:
            Texto del mensaje de error, o '' si no hay error visible.
        """
        if self.is_visible(self.ERROR_MESSAGE, timeout=3):
            return self.get_text(self.ERROR_MESSAGE)
        return ""

    def has_error(self) -> bool:
        """Verifica si hay un mensaje de error visible en la página."""
        return self.is_visible(self.ERROR_MESSAGE, timeout=3)

    def is_login_page(self) -> bool:
        """
        Verifica si la página actual es la de login.

        TODO: Ajustar según la URL real o elemento identificador del portal.
        """
        # TODO: Actualizar con la URL real o un elemento identificador del portal
        return (
            self.is_present(self.USERNAME_INPUT, timeout=5)
            or "login" in self.get_current_url().lower()
        )
