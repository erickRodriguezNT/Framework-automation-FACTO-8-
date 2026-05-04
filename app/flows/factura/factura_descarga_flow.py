"""
factura_descarga_flow.py - Sub-flujo de descarga de archivos de Factura timbrada.

Thin subclass de CfdiDescargaFlow. Toda la logica real de descarga
(CDP, screenshot visor, click PDF/XML) vive en el base comun.
"""
from app.flows.common.cfdi_descarga_flow import CfdiDescargaFlow
from app.pages.factura.factura_resultado_page import FacturaResultadoPage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FacturaDescargaFlow(CfdiDescargaFlow):
    """Sub-flujo de descarga de comprobantes de Factura timbrada."""

    def _get_resultado_page(self) -> FacturaResultadoPage:
        return FacturaResultadoPage(self.driver)

