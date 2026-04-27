"""
complemento_pago_relacion_ppd_flow.py - Sub-flujo de relación de documentos PPD.

Gestiona el proceso de agregar los documentos PPD al Complemento de Pago.
Soporta agregar múltiples documentos relacionados en una sola ejecución.

Uso:
    from app.flows.complemento_pago.complemento_pago_relacion_ppd_flow import RelacionPPDFlow
    flow = RelacionPPDFlow(driver, execution_context)
    result = flow.run(documentos=[{"uuid_ppd": "...", "importe": 1000.0, ...}])
"""
from app.core.base_flow import BaseFlow
from app.pages.complemento_pago.relacion_ppd_page import RelacionPPDPage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RelacionPPDFlow(BaseFlow):
    """
    Sub-flujo para relacionar documentos PPD en el formulario de Complemento de Pago.
    """

    def run(self, **kwargs) -> dict:
        """
        Agrega uno o más documentos PPD al Complemento de Pago.

        Args:
            documentos: (list[dict]) Lista de documentos a relacionar.
                        Cada dict debe tener:
                        - uuid_ppd:            UUID del CFDI PPD
                        - num_parcialidad:     Número de parcialidad (int)
                        - importe_saldo_ant:   Saldo anterior
                        - importe_pagado:      Importe del pago
                        - importe_saldo_ins:   Saldo insoluto (= ant - pagado)

        Returns:
            Resultado con los documentos relacionados.
        """
        self._registrar_inicio()
        documentos: list = kwargs.get("documentos", [])

        if not documentos:
            return self._marcar_fallido("Se requiere al menos un documento en 'documentos'.")

        try:
            relacion_page = RelacionPPDPage(self.driver)
            documentos_registrados = []

            for idx, doc in enumerate(documentos, start=1):
                uuid_ppd = doc.get("uuid_ppd", "")
                if not uuid_ppd:
                    logger.warning(f"Documento {idx} no tiene uuid_ppd, se omite.")
                    continue

                # TODO: Implementar con selectores reales
                # relacion_page.click_agregar_documento()
                # relacion_page.fill_uuid_documento_ppd(uuid_ppd)
                # relacion_page.fill_num_parcialidad(str(doc.get("num_parcialidad", 1)))
                # relacion_page.fill_importe_saldo_anterior(str(doc.get("importe_saldo_ant", "")))
                # relacion_page.fill_importe_pagado(str(doc.get("importe_pagado", "")))
                # relacion_page.fill_importe_saldo_insoluto(str(doc.get("importe_saldo_ins", "0.00")))
                # relacion_page.click_guardar_documento()

                self._registrar_paso(
                    f"agregar_doc_ppd_{idx}",
                    "omitido",
                    f"TODO: uuid={uuid_ppd}",
                )
                documentos_registrados.append(uuid_ppd)

            self._guardar_resultado("documentos_ppd_relacionados", documentos_registrados)
            self._tomar_screenshot("relacion_ppd_documentos")
            return self._marcar_exitoso()

        except Exception as exc:
            logger.exception(f"Error en RelacionPPDFlow: {exc}")
            self._tomar_screenshot("error_relacion_ppd")
            return self._marcar_fallido(str(exc))
