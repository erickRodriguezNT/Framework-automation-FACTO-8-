"""
nota_credito_flow.py - Flujo principal de Nota de Credito (CFDI tipo E - Egreso) en FACTO 8.

Etapa 1: Valida que el modulo de NC corre correctamente replicando el mismo
flujo de Factura Manual.

Uso:
    from app.flows.nota_credito.nota_credito_flow import NotaCreditoFlow
    flow = NotaCreditoFlow(driver, execution_context)
    result = flow.run(test_data={...})
"""
import time

from app.core.base_flow import BaseFlow
from app.flows.common.login_flow import LoginFlow
from app.flows.common.navigation_flow import NavigationFlow
from app.flows.nota_credito.nota_credito_descarga_flow import NotaCreditoDescargaFlow
from app.flows.nota_credito.nota_credito_timbrado_flow import NotaCreditoTimbradoFlow
from app.pages.nota_credito.nota_credito_cargos_no_facturables_page import NotaCreditoCargosNoFacturablesPage
from app.pages.nota_credito.nota_credito_comprobante_page import NotaCreditoComprobantePage
from app.pages.nota_credito.nota_credito_configuracion_page import NotaCreditoConfiguracionPage
from app.pages.nota_credito.nota_credito_conceptos_page import NotaCreditoConceptosPage
from app.pages.nota_credito.nota_credito_emisor_page import NotaCreditoEmisorPage
from app.pages.nota_credito.nota_credito_impuestos_page import NotaCreditoImpuestosPage
from app.pages.nota_credito.nota_credito_page import NotaCreditoPage
from app.pages.nota_credito.nota_credito_receptor_page import NotaCreditoReceptorPage
from app.utils.logger import get_logger
from app.utils.output_manager import create_case_output_dir, get_screenshot_dir

logger = get_logger(__name__)


class NotaCreditoFlow(BaseFlow):
    """Flujo base de Nota de Credito - Etapa 1."""

    def run(self, **kwargs) -> dict:
        return self.ejecutar_nota_credito_base(kwargs.get("test_data", {}))

    def ejecutar_nota_credito_base(self, test_data: dict) -> dict:
        from pathlib import Path

        es_plano = "rfc_receptor" in test_data or "caso_id" in test_data
        caso_id  = str(test_data.get("caso_id", "NC_RUN")).strip()

        if es_plano:
            emisor_data = {"centro_consumo": test_data.get("centro_consumo", ""),
                           "serie":          test_data.get("serie", "")}
        else:
            emisor_data = test_data.get("emisor", {})

        uuid_relacionado = str(test_data.get("uuid_relacionado", "")).strip()
        tipo_relacion    = str(test_data.get("tipo_relacion", "")).strip()
        uuids_seleccionados = str(test_data.get("uuids_seleccionados", "")).strip()
        if uuid_relacionado:
            logger.info(f"[NC FLOW] [{caso_id}] UUID relacionado: {uuid_relacionado}")
        if tipo_relacion:
            logger.info(f"[NC FLOW] [{caso_id}] Tipo relacion: {tipo_relacion}")

        # --- Crear directorio de caso dentro del run_dir de esta corrida ---
        run_dir_str = self.context.get_dato("run_dir_nc")
        if run_dir_str:
            run_dir = Path(run_dir_str)
        else:
            # Retrocompatibilidad: si el step no creó run_dir, usar ruta sin timestamp
            from app.utils.output_manager import _PROJECT_ROOT
            run_dir = _PROJECT_ROOT / "outputs" / "nota_credito"
            run_dir.mkdir(parents=True, exist_ok=True)

        row_index = self.context.get_dato("nc_row_index", 0)
        case_dir = create_case_output_dir(run_dir, caso_id, row_index=row_index)
        screenshot_dir = get_screenshot_dir(case_dir)

        # Registrar en contexto para uso en NotaCreditoDescargaFlow
        self.context.set_dato("evidence_dir_nc", str(screenshot_dir))
        self.context.set_dato("case_dir_nc", str(case_dir))
        logger.info(f"[NC FLOW] [{caso_id}] Case dir: {case_dir}")

        self._registrar_inicio()

        try:
            logger.info(f"[NC FLOW] [{caso_id}] Paso 0: Login.")
            self._login_portal()

            logger.info(f"[NC FLOW] [{caso_id}] Paso 1: Navegar.")
            self._navegar_portal()

            logger.info(f"[NC FLOW] [{caso_id}] Paso 2: Verificar pantalla.")
            nc_page = NotaCreditoPage(self.driver)
            # Inyectar ruta de screenshots con timestamp para esta corrida
            nc_page._screenshot_dir = screenshot_dir
            nc_page.wait_for_pantalla_nota_credito()
            self._registrar_paso("pantalla_nc_cargada", "exitoso")
            nc_page.tomar_evidencia_pantalla(caso_id, "01_pantalla_nc_cargada")

            # ----------------------------------------------------------
            # PASO 2b: Personalizar — habilitar CFDI Relacionado ANTES
            # de llenar el formulario para evitar que el drawer resetee
            # los campos ya llenados (centro de consumo, receptor, etc.).
            # ----------------------------------------------------------
            if tipo_relacion or uuid_relacionado:
                logger.info(f"[NC FLOW] [{caso_id}] Paso 2b: Activar toggle CFDI Relacionado (drawer — antes de llenar formulario).")
                config_page = NotaCreditoConfiguracionPage(self.driver)
                config_page.configurar_cfdi_relacionado()
                self._registrar_paso("configurar_cfdi_relacionado", "exitoso")
                nc_page.tomar_evidencia_pantalla(caso_id, "01b_cfdi_relacionado_toggle_activado")

            logger.info(f"[NC FLOW] [{caso_id}] Paso 3: Emisor.")
            emisor_page = NotaCreditoEmisorPage(self.driver)
            centro_consumo = emisor_data.get("centro_consumo", "")
            serie = emisor_data.get("serie", "")
            if centro_consumo:
                emisor_page.select_centro_consumo(centro_consumo)
            if serie:
                emisor_page.select_serie(serie)
            # Leer DOM para confirmar qué quedó seleccionado realmente
            centro_dom = emisor_page.leer_centro_consumo_seleccionado()
            logger.info(
                f"[NC FLOW] [{caso_id}] EMISOR DIAGNÓSTICO\n"
                f"  Excel centro_consumo : {centro_consumo!r}\n"
                f"  DOM  centro_consumo  : {centro_dom!r}"
            )
            self._registrar_paso("capturar_emisor", "exitoso",
                                 f"centro_consumo={centro_consumo!r}, serie={serie!r}")
            nc_page.tomar_evidencia_pantalla(caso_id, "02_emisor_capturado")

            logger.info(f"[NC FLOW] [{caso_id}] Paso 4: Receptor.")
            receptor_page = NotaCreditoReceptorPage(self.driver)
            rfc = str(test_data.get("rfc_receptor", "")).strip()
            if rfc:
                receptor_page.capturar_rfc_receptor(rfc)
                receptor_page.click_buscar_rfc()
            receptor_page.capturar_razon_social(str(test_data.get("razon_social", "")).strip())
            receptor_page.capturar_codigo_postal(str(test_data.get("codigo_postal", "")).strip())
            receptor_page.seleccionar_regimen_fiscal_receptor(
                str(test_data.get("regimen_fiscal_receptor", "")).strip())
            receptor_page.seleccionar_uso_cfdi(str(test_data.get("uso_cfdi", "")).strip())
            receptor_page.capturar_email(str(test_data.get("email", "")).strip())
            if receptor_page.activar_domicilio_fiscal_si_aplica(test_data):
                receptor_page.capturar_domicilio_fiscal(test_data)
            self._registrar_paso("capturar_receptor", "exitoso", f"rfc={rfc!r}")
            nc_page.tomar_evidencia_pantalla(caso_id, "03_receptor_capturado")

            logger.info(f"[NC FLOW] [{caso_id}] Paso 5: Comprobante.")
            comprobante_page = NotaCreditoComprobantePage(self.driver)
            comprobante_page.fill_comprobante_desde_caso(test_data)
            self._registrar_paso("capturar_comprobante", "exitoso")
            nc_page.tomar_evidencia_pantalla(caso_id, "04_comprobante_capturado")

            # ----------------------------------------------------------
            # PASO 6: Personalizar — habilitar CFDI Relacionado
            # Solo se ejecuta si NO se activó ya en el Paso 2b
            # (cuando no hay tipo_relacion ni uuid_relacionado).
            # ----------------------------------------------------------
            if not (tipo_relacion or uuid_relacionado):
                logger.info(f"[NC FLOW] [{caso_id}] Paso 6: Configurar CFDI Relacionado (drawer).")
                config_page = NotaCreditoConfiguracionPage(self.driver)
                config_page.configurar_cfdi_relacionado()
                self._registrar_paso("configurar_cfdi_relacionado", "exitoso")
                nc_page.tomar_evidencia_pantalla(caso_id, "05_cfdi_relacionado_toggle_activado")

            # ----------------------------------------------------------
            # PASO 6b: Llenar formulario CFDI Relacionado (página principal)
            # ----------------------------------------------------------
            if tipo_relacion or uuid_relacionado:
                logger.info(f"[NC FLOW] [{caso_id}] Paso 6b: Llenar CFDI Relacionado.")
                cfdi_page = NotaCreditoConfiguracionPage(self.driver)
                cfdi_page.fill_cfdi_relacionado(tipo_relacion, uuid_relacionado)
                self._registrar_paso("fill_cfdi_relacionado", "exitoso",
                                     f"tipo={tipo_relacion!r}, uuid={uuid_relacionado!r}")
                nc_page.tomar_evidencia_pantalla(caso_id, "06_cfdi_relacionado_llenado")
            else:
                logger.info(f"[NC FLOW] [{caso_id}] Paso 6b: Sin UUID relacionado — omitido.")

            if test_data.get("cargo_no_facturable_nombre"):
                logger.info(f"[NC FLOW] [{caso_id}] Paso 7a: Cargos no facturables.")
                cargos_page = NotaCreditoCargosNoFacturablesPage(self.driver)
                cargos_page.agregar_cargo_desde_caso(test_data)
                nc_page.tomar_evidencia_pantalla(caso_id, "07a_cargo_no_facturable")

            logger.info(f"[NC FLOW] [{caso_id}] Paso 7: Conceptos y Servicios.")
            conceptos_page = NotaCreditoConceptosPage(self.driver)
            conceptos_page.agregar_concepto_desde_caso(test_data)

            logger.info(f"[NC FLOW] [{caso_id}] Paso 7.5: Validar concepto guardado.")
            cantidad_conceptos = conceptos_page.get_cantidad_conceptos()
            if cantidad_conceptos == 0:
                raise AssertionError(
                    "[PRE-TIMBRADO NC] No se encontro ningun concepto en la tabla."
                )
            logger.info(f"[NC FLOW] [{caso_id}] Concepto(s) en tabla: {cantidad_conceptos}")
            self._registrar_paso("validar_concepto_guardado", "exitoso",
                                 f"conceptos en tabla: {cantidad_conceptos}")

            nc_page.scroll_to_bottom()
            impuestos_page = NotaCreditoImpuestosPage(self.driver)
            totales_imp = impuestos_page.registrar_totales_impuestos()
            self._registrar_paso("validar_impuestos_pre_timbrado", "exitoso", str(totales_imp))
            nc_page.scroll_to_top()

            logger.info(f"[NC FLOW] [{caso_id}] Paso 8: Totales.")
            totales = nc_page.validar_totales()
            self._guardar_resultado("totales_pre_timbrado", totales)
            self._registrar_paso("validar_totales", "exitoso", str(totales))
            nc_page.tomar_evidencia_pantalla(caso_id, "08_totales_validados")

            logger.info(f"[NC FLOW] [{caso_id}] Paso 9: Timbrar.")
            resultado_timbrado = self._timbrar()
            if resultado_timbrado["estado"] == "fallido":
                nc_page.tomar_evidencia_pantalla(caso_id, "error_timbrado")
                time.sleep(10)
                return self._marcar_fallido(f"Timbrado fallo: {resultado_timbrado.get('error')}")
            nc_page.tomar_evidencia_pantalla(caso_id, "09_timbrado_completado")

            logger.info(f"[NC FLOW] [{caso_id}] Paso 10: Validar resultado.")
            self._validar_resultado()

            # ----------------------------------------------------------
            # PASO 11: Descargar PDF y XML del visor de timbrado
            # ----------------------------------------------------------
            logger.info(f"[NC FLOW] [{caso_id}] Paso 11: Descargar documentos.")
            descarga_flow = NotaCreditoDescargaFlow(self.driver, self.context)
            descarga_flow.run(tipos=["pdf", "xml"])
            nc_page.tomar_evidencia_pantalla(caso_id, "10_descarga_completada")

            logger.info(f"[NC FLOW] [{caso_id}] Flujo completado exitosamente.")
            self._generar_reporte(caso_id, test_data, "exitoso", case_dir=case_dir)
            return self._marcar_exitoso()

        except Exception as exc:
            logger.exception(f"[NC FLOW] [{caso_id}] Error: {exc}")
            try:
                err_page = NotaCreditoPage(self.driver)
                err_page._screenshot_dir = screenshot_dir
                err_page.tomar_evidencia_pantalla(caso_id, "error_nc_flow")
            except Exception:
                pass
            self._generar_reporte(caso_id, test_data, "fallido", str(exc), case_dir)
            time.sleep(10)
            return self._marcar_fallido(str(exc))

    def _login_portal(self) -> None:
        login_flow = LoginFlow(self.driver, self.context)
        result = login_flow.run(
            username=self._obtener_dato("username"),
            password=self._obtener_dato("password"),
            base_url=self._obtener_dato("base_url"),
        )
        if result["estado"] == "fallido":
            raise RuntimeError(f"Login fallo: {result.get('error')}")
        self._registrar_paso("login_portal", "exitoso")

    def _navegar_portal(self) -> None:
        nav_flow = NavigationFlow(self.driver, self.context)
        result = nav_flow.run(destino="nota_credito")
        if result["estado"] == "fallido":
            raise RuntimeError(f"Navegacion a nota_credito fallo: {result.get('error')}")
        self._registrar_paso("navegar_portal_nc", "exitoso")

    def _timbrar(self) -> dict:
        nc_page = NotaCreditoPage(self.driver)
        nc_page.click_timbrar()
        timbrado_flow = NotaCreditoTimbradoFlow(self.driver, self.context)
        return timbrado_flow.run()

    def _validar_resultado(self) -> None:
        # El UUID ya fue capturado en NotaCreditoTimbradoFlow (con timeout=2).
        # Solo registramos el paso usando el valor que ya está en contexto.
        uuid_nc = self.context.get_dato("uuid_nota_credito", "")
        self._registrar_paso("validar_resultado_nc", "exitoso", f"uuid_nota_credito={uuid_nc!r}")

    def _generar_reporte(self, caso_id: str, test_data: dict, estado: str, error: str = "", case_dir=None) -> None:
        """Genera reporte JSON con los campos del Excel y el estado final del caso."""
        import json
        from datetime import datetime
        from pathlib import Path

        campos_reporte = [
            "ejecutar", "caso_id", "descripcion",
            "centro_consumo", "serie",
            "rfc_receptor", "razon_social", "codigo_postal",
            "regimen_fiscal_receptor", "uso_cfdi", "email",
            "calle", "num_exterior", "num_interior", "colonia", "municipio", "estado",
            "fecha_emision", "exportacion", "moneda", "tipo_cambio",
            "metodo_pago", "forma_pago", "condiciones_pago",
            "observaciones_pdf", "idioma", "integraciones", "referencia",
            "clave_unidad", "cantidad", "no_identificacion",
            "clave_prod_serv", "descripcion_concepto",
            "valor_unitario", "descuento",
            "objeto_impuesto", "impuesto", "ret_tras", "tipo_factor", "tasa_o_cuota",
            "cargo_no_facturable_nombre", "cargo_no_facturable_importe",
            "descargar_pdf", "descargar_xml",
            "tipo_relacion", "uuids_seleccionados", "uuid_relacionado",
            "resultado_esperado",
        ]

        reporte = {
            "caso_id":     caso_id,
            "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "estado":      estado,
            "error":       error,
            "datos_excel": {campo: str(test_data.get(campo, "")) for campo in campos_reporte},
        }

        try:
            # Usar case_dir si se proporcionó (ruta con timestamp), sino fallback legacy
            if case_dir is not None:
                output_dir = Path(case_dir)
            else:
                output_dir = Path("outputs") / "nota_credito" / caso_id
            output_dir.mkdir(parents=True, exist_ok=True)
            ruta = output_dir / f"reporte_{caso_id}.json"
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(reporte, f, ensure_ascii=False, indent=2)
            logger.info(f"[NC FLOW] Reporte guardado: {ruta}")
        except Exception as exc_rep:
            logger.warning(f"[NC FLOW] No se pudo guardar el reporte: {exc_rep}")
