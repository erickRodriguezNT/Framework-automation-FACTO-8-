"""
nota_credito_descarga_flow.py - Sub-flujo de descarga de archivos de Nota de Crédito timbrada.

Thin subclass de CfdiDescargaFlow. Toda la lógica real de descarga
(CDP, screenshot visor, click PDF/XML) vive en el base común.
"""
from pathlib import Path

from app.flows.common.cfdi_descarga_flow import CfdiDescargaFlow
from app.pages.nota_credito.nota_credito_resultado_page import NotaCreditoResultadoPage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NotaCreditoDescargaFlow(CfdiDescargaFlow):
    """Sub-flujo de descarga de comprobantes de Nota de Crédito timbrada."""

    def _get_resultado_page(self) -> NotaCreditoResultadoPage:
        return NotaCreditoResultadoPage(self.driver)

    def _obtener_case_dir(self) -> Path:
        """NC usa la clave 'evidence_dir_nc' en el contexto (apunta a case_dir/screenshots)."""
        evidence_dir = self.context.get_dato(
            "evidence_dir_nc",
            "outputs/nota_credito/RUN/screenshots",
        )
        case_dir = Path(evidence_dir).parent.resolve()
        case_dir.mkdir(parents=True, exist_ok=True)
        return case_dir

