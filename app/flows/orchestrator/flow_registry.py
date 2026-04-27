"""
flow_registry.py - Registro central de todos los flujos del framework FACTO.

Mapea nombres de flujo a sus clases correspondientes.
Permite al orchestrator y al CLI instanciar flujos por nombre
sin imports directos en cada módulo.

Uso:
    from app.flows.orchestrator.flow_registry import FlowRegistry
    flow_class = FlowRegistry.get("factura")
    flow = flow_class(driver, execution_context)
    result = flow.run(test_data={...})
"""
from typing import Type

from app.core.base_flow import BaseFlow

# Importaciones diferidas para evitar circular imports en tiempo de carga.
# Se usa un diccionario de strings que se resuelven en get().
_REGISTRY: dict[str, str] = {
    # Flujos comunes
    "login":                   "app.flows.common.login_flow:LoginFlow",
    "navigation":              "app.flows.common.navigation_flow:NavigationFlow",
    "download":                "app.flows.common.download_flow:DownloadFlow",
    "validation":              "app.flows.common.validation_flow:ValidationFlow",

    # Flujos de Factura
    "factura":                 "app.flows.factura.factura_flow:FacturaFlow",
    "factura_timbrado":        "app.flows.factura.factura_timbrado_flow:FacturaTimbradoFlow",
    "factura_descarga":        "app.flows.factura.factura_descarga_flow:FacturaDescargaFlow",

    # Flujos de Nota de Crédito
    "nota_credito":            "app.flows.nota_credito.nota_credito_flow:NotaCreditoFlow",
    "nota_credito_relacion":   "app.flows.nota_credito.nota_credito_relacion_flow:NotaCreditoRelacionFlow",

    # Flujos de PPD
    "ppd":                     "app.flows.ppd.ppd_flow:PPDFlow",
    "ppd_validacion":          "app.flows.ppd.ppd_validacion_flow:PPDValidacionFlow",

    # Flujos de Complemento de Pago
    "complemento_pago":           "app.flows.complemento_pago.complemento_pago_flow:ComplementoPagoFlow",
    "complemento_pago_relacion":  "app.flows.complemento_pago.complemento_pago_relacion_ppd_flow:RelacionPPDFlow",
    "complemento_pago_validacion":"app.flows.complemento_pago.complemento_pago_validacion_flow:ComplementoPagoValidacionFlow",

    # Flujos de Adenda
    "adenda":                  "app.flows.adenda.adenda_flow:AdendaFlow",
    "adenda_validacion":       "app.flows.adenda.adenda_validacion_flow:AdendaValidacionFlow",
}


class FlowRegistry:
    """
    Registro central de flujos del framework.

    Provee acceso a clases de flujo por nombre sin imports circulares.
    """

    @staticmethod
    def get(name: str) -> Type[BaseFlow]:
        """
        Obtiene la clase de flujo por nombre.

        Args:
            name: Nombre del flujo (clave en _REGISTRY).

        Returns:
            Clase del flujo (no instancia).

        Raises:
            KeyError: Si el nombre no está registrado.
            ImportError: Si el módulo no puede importarse.
        """
        import importlib

        entry = _REGISTRY.get(name)
        if entry is None:
            available = list(_REGISTRY.keys())
            raise KeyError(
                f"Flujo '{name}' no registrado. Disponibles: {available}"
            )

        module_path, class_name = entry.split(":")
        module = importlib.import_module(module_path)
        return getattr(module, class_name)

    @staticmethod
    def list_flows() -> list[str]:
        """Retorna la lista de nombres de flujos registrados."""
        return list(_REGISTRY.keys())

    @staticmethod
    def register(name: str, module_path: str, class_name: str) -> None:
        """
        Registra un flujo adicional en tiempo de ejecución.

        Args:
            name:        Nombre con el que se registra el flujo.
            module_path: Ruta de módulo Python (ej. 'app.flows.custom.my_flow').
            class_name:  Nombre de la clase (ej. 'MyFlow').
        """
        _REGISTRY[name] = f"{module_path}:{class_name}"
