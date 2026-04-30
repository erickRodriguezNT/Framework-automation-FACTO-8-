"""
factura_resultado_page.py - Page Object de la pantalla de resultado post-timbrado de Factura.

Subclase delgada de CfdiResultadoPage. Toda la logica compartida vive en el base.
"""
from app.pages.common.cfdi_resultado_page import CfdiResultadoPage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class FacturaResultadoPage(CfdiResultadoPage):
    """Page Object para la pantalla de resultado del timbrado de Factura."""
