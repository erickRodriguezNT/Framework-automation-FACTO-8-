"""
navigation_flow.py - Flujo de navegación entre módulos del portal FACTO.

Encapsula la lógica de navegación entre módulos a través del menú principal.
Cualquier flow que necesite cambiar de sección puede usar este flow.

Uso:
    from app.flows.common.navigation_flow import NavigationFlow
    flow = NavigationFlow(driver, execution_context)
    flow.run(destino="factura")
"""
from app.core.base_flow import BaseFlow
from app.pages.common.loader_page import LoaderPage
from app.pages.common.menu_page import MenuPage
from app.utils.exceptions import FlowExecutionError, NavigationError
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Módulos disponibles y su acción de navegación
NAVEGACION_MAP = {
    "factura":          "navigate_to_factura",
    "nota_credito":     "navigate_to_nota_credito",
    "ppd":              "navigate_to_ppd",
    "complemento_pago": "navigate_to_complemento_pago",
    "adenda":           "navigate_to_adenda",
}


class NavigationFlow(BaseFlow):
    """
    Flow de navegación entre módulos del portal FACTO.

    Usa el MenuPage para navegar a cualquier módulo del portal
    y verifica que la navegación fue exitosa.
    """

    def run(self, **kwargs) -> dict:
        """
        Navega al módulo especificado.

        Args:
            destino: (str) Nombre del módulo destino.
                     Opciones: 'factura', 'nota_credito', 'ppd',
                               'complemento_pago', 'adenda'

        Returns:
            Resultado del flow.
        """
        self._registrar_inicio()

        destino = kwargs.get("destino", "")
        if not destino:
            return self._marcar_fallido("Se requiere el parámetro 'destino' para NavigationFlow.")

        if destino not in NAVEGACION_MAP:
            return self._marcar_fallido(
                f"Módulo '{destino}' no reconocido. Opciones: {list(NAVEGACION_MAP.keys())}"
            )

        try:
            menu_page = MenuPage(self.driver)
            loader_page = LoaderPage(self.driver)

            # Verificar que el menú está visible
            if not menu_page.is_menu_visible():
                return self._marcar_fallido(
                    "El menú de navegación no está visible. "
                    "Verificar que el usuario esté autenticado."
                )

            # Ejecutar la acción de navegación correspondiente
            action_name = NAVEGACION_MAP[destino]
            nav_action = getattr(menu_page, action_name)
            nav_action()

            self._registrar_paso(f"navegar_a_{destino}", "exitoso")

            # Esperar a que el loader desaparezca
            loader_page.wait_for_loader_to_disappear()
            self._tomar_screenshot(f"navegacion_{destino}")

            self._guardar_resultado("modulo_actual", destino)
            return self._marcar_exitoso()

        except Exception as exc:
            logger.exception(f"Error en NavigationFlow hacia '{destino}': {exc}")
            self._tomar_screenshot(f"error_navegacion_{destino}")
            return self._marcar_fallido(str(exc))
