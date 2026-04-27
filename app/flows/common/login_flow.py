"""
login_flow.py - Flujo de autenticación en el portal FACTO.

Encapsula el proceso completo de login:
1. Navegar a la página de login
2. Ingresar credenciales
3. Verificar que el login fue exitoso
4. Manejar errores de autenticación

Uso:
    from app.flows.common.login_flow import LoginFlow
    flow = LoginFlow(driver, execution_context)
    result = flow.run(username="user@example.com", password="secret")
"""
import os

from selenium.webdriver.support.ui import WebDriverWait

from app.core.base_flow import BaseFlow
from app.pages.common.home_page import HomePage
from app.pages.common.login_page import LoginPage
from app.utils.exceptions import FlowExecutionError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LoginFlow(BaseFlow):
    """
    Flow de autenticación en el portal FACTO.

    Gestiona el proceso de login y verifica el acceso exitoso.
    Puede reutilizarse como primer paso en todos los flows del portal.
    """

    def run(self, **kwargs) -> dict:
        """
        Ejecuta el flujo de login completo.

        Args:
            username: (str) Nombre de usuario o email.
            password: (str) Contraseña.
            base_url: (str) URL base del portal. Si no se provee,
                      usa el dato guardado en el contexto.

        Returns:
            Resultado del flow con estado 'exitoso' o 'fallido'.
        """
        self._registrar_inicio()

        username = kwargs.get("username") or self.context.get_dato("username")
        password = kwargs.get("password") or self.context.get_dato("password")
        base_url = kwargs.get("base_url") or self.context.get_dato("base_url", "")

        if not username or not password:
            return self._marcar_fallido("username y password son requeridos para el login.")

        try:
            # --- Paso 1: Navegar a la página de login ---
            login_page = LoginPage(self.driver)

            # El portal redirige automáticamente a Auth0 desde la raíz.
            # Navegar a /login en Angular puede no activar la redirección.
            login_url = base_url.rstrip("/") + "/"
            logger.info(f"Navegando a: {login_url}")
            login_page.navigate_to(login_url)
            self._registrar_paso("navegar_login", "exitoso")
            self._tomar_screenshot("01_pagina_login")

            # --- Paso 2: Ingresar credenciales ---
            login_page.login(username=username, password=password)
            self._registrar_paso("ingresar_credenciales", "exitoso")
            self._tomar_screenshot("02_credenciales_ingresadas")
            logger.info(f"[DIAG] URL inmediata post-click: {self.driver.current_url}")
            logger.info(f"[DIAG] Título post-click: {self.driver.title}")

            # --- Esperar a que Auth0 complete la redirección de vuelta al portal ---
            # Auth0 procesa el login y redirige; puede tomar 5-30 segundos.
            logger.info("Esperando redirección de Auth0 de vuelta al portal...")
            try:
                WebDriverWait(self.driver, 30).until(
                    lambda d: "auth0.com" not in d.current_url
                )
                logger.info(f"Redirección completada. URL actual: {self.driver.current_url}")
            except Exception:
                logger.warning("Timeout esperando redirección de Auth0; guardando diagnóstico...")
                logger.warning(f"[DIAG] URL en timeout: {self.driver.current_url}")
                logger.warning(f"[DIAG] Título en timeout: {self.driver.title}")
                # Guardar HTML de la página Auth0 para inspección
                try:
                    debug_path = os.path.join("reports", "auth0_timeout_debug.html")
                    os.makedirs("reports", exist_ok=True)
                    with open(debug_path, "w", encoding="utf-8") as f:
                        f.write(self.driver.page_source)
                    logger.warning(f"[DIAG] HTML guardado en: {debug_path}")
                    # Imprimir texto visible de la página para diagnóstico rápido
                    body_text = self.driver.find_element("tag name", "body").text
                    logger.warning(f"[DIAG] Texto visible en Auth0:\n{body_text[:1500]}")
                except Exception as diag_exc:
                    logger.warning(f"[DIAG] No se pudo guardar diagnóstico: {diag_exc}")

            # --- Paso 3: Verificar error de autenticación ---
            if login_page.has_error():
                error_msg = login_page.get_error_message()
                self._tomar_screenshot("03_error_login")
                return self._marcar_fallido(f"Error de autenticación: {error_msg}")

            # --- Paso 4: Verificar que el home es accesible ---
            home_page = HomePage(self.driver)
            if not home_page.is_logged_in():
                self._tomar_screenshot("03_login_no_verificado")
                return self._marcar_fallido(
                    "Login no verificado: el portal no mostró el dashboard después del login."
                )

            self._registrar_paso("verificar_login", "exitoso")
            self._tomar_screenshot("03_login_exitoso")
            logger.info("Login exitoso")

            return self._marcar_exitoso()

        except Exception as exc:
            logger.exception(f"Error en LoginFlow: {exc}")
            self._tomar_screenshot("error_login")
            return self._marcar_fallido(str(exc))
