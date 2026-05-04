"""
cfdi_manual_flow.py — Flujo común de emisión manual de CFDI 4.0.

Orquesta los pasos del formulario de emisión, timbrado y descarga que son
comunes a todos los módulos de CFDI manual del portal FACTO 8:

  - factura   (Factura estándar PUE)
  - ppd       (Pago en Parcialidades o Diferido)

El formulario de emisión en FACTO 8 es idéntico para todos los tipos.
La única diferencia funcional entre Factura y PPD está en el valor del
campo metodo_pago, que proviene del Excel de cada módulo.

Método principal:
    ejecutar_cfdi_manual(caso, tipo_flujo)

    donde tipo_flujo controla:
      - Destino de navegación (NavigationFlow recibe destino=tipo_flujo)
      - Context keys de run_dir / case_dir  (ej: run_dir_ppd, case_dir_ppd)
      - Ruta de outputs  (outputs/{tipo_flujo}/{timestamp}/{caso_id}/)

La lógica específica de cada módulo vive en su propio flow ligero
(FacturaFlow, PPDFlow) que delega aquí.

Uso:
    from app.flows.common.cfdi_manual_flow import CfdiManualFlow
    flow = CfdiManualFlow(driver, execution_context)
    result = flow.ejecutar_cfdi_manual(caso=caso, tipo_flujo="ppd")
"""
import time as _time
from pathlib import Path

from app.core.base_flow import BaseFlow
from app.flows.common.login_flow import LoginFlow
from app.flows.common.navigation_flow import NavigationFlow
from app.flows.factura.factura_descarga_flow import FacturaDescargaFlow
from app.flows.factura.factura_timbrado_flow import FacturaTimbradoFlow
from app.pages.factura.factura_cargos_no_facturables_page import FacturaCargosNoFacturablesPage
from app.pages.factura.factura_comprobante_page import FacturaComprobantePage
from app.pages.factura.factura_conceptos_page import FacturaConceptosPage
from app.pages.factura.factura_emisor_page import FacturaEmisorPage
from app.pages.factura.factura_impuestos_page import FacturaImpuestosPage
from app.pages.factura.factura_page import FacturaPage
from app.pages.factura.factura_receptor_page import FacturaReceptorPage
from app.utils.logger import get_logger
from app.utils.output_manager import (
    _PROJECT_ROOT,
    create_case_output_dir,
    get_screenshot_dir,
)

logger = get_logger(__name__)


class CfdiManualFlow(BaseFlow):
    """
    Flujo común reutilizable de emisión manual de CFDI 4.0.

    Centraliza toda la orquestación que Factura y PPD comparten:
      - Login en el portal
      - Navegación al módulo (factura o ppd)
      - Captura de Emisor, Receptor, Comprobante, Conceptos, Impuestos
      - Cargos No Facturables (condicional)
      - Timbrado y validación del resultado
      - Descarga de PDF/XML
      - Gestión de evidencias con rutas por corrida/caso

    Los page objects de app/pages/factura/ son reusados para todos los
    tipos, ya que el formulario es el mismo en el portal FACTO 8.

    Subclases/delegadores: FacturaFlow, PPDFlow.
    """

    # ------------------------------------------------------------------
    # Punto de entrada genérico (BaseFlow.run)
    # ------------------------------------------------------------------

    def run(self, **kwargs) -> dict:
        """
        Punto de entrada estándar del BaseFlow.

        Args:
            caso:        Dict plano del Excel o anidado legacy.
            tipo_flujo:  "factura" | "ppd"  (default: "factura")

        Returns:
            Resultado estándar BaseFlow.
        """
        return self.ejecutar_cfdi_manual(
            caso=kwargs.get("caso", {}),
            tipo_flujo=kwargs.get("tipo_flujo", "factura"),
        )

    # ------------------------------------------------------------------
    # Método principal de orquestación
    # ------------------------------------------------------------------

    def ejecutar_cfdi_manual(self, caso: dict, tipo_flujo: str = "factura") -> dict:
        """
        Ejecuta el flujo completo de emisión de un CFDI manual.

        Acepta DOS formatos de entrada:
          1. Dict PLANO  (Excel data-driven): claves rfc_receptor, caso_id, ...
          2. Dict ANIDADO (legacy JSON): claves emisor/receptor/comprobante/conceptos.

        Detección automática: si tiene 'rfc_receptor' o 'caso_id' → plano.

        Args:
            caso:       Datos del caso (Excel plano o JSON anidado).
            tipo_flujo: Nombre del módulo. Determina contexto y rutas.
                        Valores: "factura", "ppd".

        Returns:
            Diccionario estándar BaseFlow:
            { "estado": "exitoso"|"fallido", "datos": dict, "error": str|None }
        """
        # ── Detectar formato y extraer campos estructurales ───────────
        es_plano = "rfc_receptor" in caso or "caso_id" in caso
        caso_id = str(caso.get("caso_id", f"{tipo_flujo.upper()}_RUN")).strip()

        if es_plano:
            emisor_data = {
                "centro_consumo": caso.get("centro_consumo", ""),
                "serie":          caso.get("serie", ""),
            }
            comprobante_data = caso          # fill_comprobante_desde_caso lee el dict completo
            conceptos        = None          # usar agregar_concepto_desde_caso
            validaciones = {
                "descargar_pdf": caso.get("descargar_pdf", False),
                "descargar_xml": caso.get("descargar_xml", False),
            }
        else:
            emisor_data      = caso.get("emisor", {})
            comprobante_data = caso.get("comprobante", {})
            conceptos        = caso.get("conceptos", [])
            validaciones     = caso.get("validaciones", {})

        # ── Crear directorio de caso para esta corrida ─────────────────
        run_dir_str = self.context.get_dato(f"run_dir_{tipo_flujo}")
        if run_dir_str:
            run_dir = Path(run_dir_str)
        else:
            # Retrocompatibilidad: si el step no creó run_dir
            run_dir = _PROJECT_ROOT / "outputs" / tipo_flujo
            run_dir.mkdir(parents=True, exist_ok=True)

        row_index = self.context.get_dato(f"{tipo_flujo}_row_index", 0)
        case_dir = create_case_output_dir(run_dir, caso_id, row_index=row_index)
        screenshot_dir = get_screenshot_dir(case_dir)

        # Registrar en contexto
        # evidence_dir es leído por CfdiDescargaFlow._obtener_case_dir()
        self.context.set_dato("evidence_dir", str(screenshot_dir))
        self.context.set_dato(f"case_dir_{tipo_flujo}", str(case_dir))
        logger.info(
            "[CFDI MANUAL] [%s] [%s] Case dir: %s",
            tipo_flujo.upper(), caso_id, case_dir,
        )

        self._registrar_inicio()

        try:
            # ── PASO 0: Login ─────────────────────────────────────────
            logger.info("[CFDI MANUAL] [%s] Paso 0: Autenticación.", caso_id)
            self._login_portal()

            # ── PASO 1: Navegar al módulo ────────────────────────────
            logger.info("[CFDI MANUAL] [%s] Paso 1: Navegar a '%s'.", caso_id, tipo_flujo)
            self._navegar_portal(tipo_flujo)

            # ── PASO 2: Verificar pantalla de emisión ─────────────────
            logger.info("[CFDI MANUAL] [%s] Paso 2: Verificar pantalla.", caso_id)
            factura_page = FacturaPage(self.driver)
            factura_page._screenshot_dir = screenshot_dir
            factura_page.wait_for_pantalla_factura()
            self._registrar_paso("pantalla_cfdi_cargada", "exitoso")
            factura_page.tomar_evidencia_pantalla(caso_id, "01_pantalla_cfdi_cargada")

            # ── PASO 3: Emisor ─────────────────────────────────────────
            logger.info("[CFDI MANUAL] [%s] Paso 3: Emisor.", caso_id)
            self.capturar_emisor(emisor_data)
            factura_page.tomar_evidencia_pantalla(caso_id, "02_emisor_capturado")

            # ── PASO 4: Receptor ───────────────────────────────────────
            logger.info("[CFDI MANUAL] [%s] Paso 4: Receptor.", caso_id)
            if es_plano:
                self.capturar_receptor_desde_caso(caso)
            else:
                self.capturar_receptor(caso.get("receptor", {}))
            factura_page.tomar_evidencia_pantalla(caso_id, "03_receptor_capturado")

            # ── PASO 5: Comprobante ───────────────────────────────────
            logger.info("[CFDI MANUAL] [%s] Paso 5: Comprobante.", caso_id)
            if es_plano:
                self.capturar_comprobante_desde_caso(comprobante_data)
            else:
                self.capturar_comprobante(comprobante_data)
            factura_page.tomar_evidencia_pantalla(caso_id, "04_comprobante_capturado")

            # ── PASO 6: Cargos No Facturables (condicional) ───────────
            if es_plano and caso.get("cargo_no_facturable_nombre"):
                logger.info("[CFDI MANUAL] [%s] Paso 6a: Cargos no facturables.", caso_id)
                cargos_page = FacturaCargosNoFacturablesPage(self.driver)
                cargos_page.agregar_cargo_desde_caso(caso)
                factura_page.tomar_evidencia_pantalla(caso_id, "05a_cargo_no_facturable")

            # ── PASO 7: Conceptos ──────────────────────────────────────
            logger.info("[CFDI MANUAL] [%s] Paso 7: Conceptos.", caso_id)
            if es_plano:
                self.agregar_concepto_desde_caso(caso)
            else:
                self.agregar_conceptos(conceptos or [])
            factura_page.tomar_evidencia_pantalla(caso_id, "05_conceptos_agregados")

            # ── PASO 7.5: Validar que el concepto quedó guardado ──────
            logger.info(
                "[CFDI MANUAL] [%s] Paso 7.5: Validar concepto guardado e impuestos.", caso_id
            )
            conceptos_page = FacturaConceptosPage(self.driver)
            cantidad_conceptos = conceptos_page.get_cantidad_conceptos()
            if cantidad_conceptos == 0:
                raise AssertionError(
                    "[PRE-TIMBRADO] No se encontró ningún concepto en la tabla. "
                    "Verifica que el botón 'Guardar Concepto' fue ejecutado correctamente."
                )
            logger.info(
                "[CFDI MANUAL] [%s] ✔ Concepto(s) confirmado(s) en tabla: %s",
                caso_id, cantidad_conceptos,
            )
            self._registrar_paso(
                "validar_concepto_guardado", "exitoso",
                f"conceptos en tabla: {cantidad_conceptos}",
            )
            factura_page.tomar_evidencia_pantalla(caso_id, "05b_concepto_guardado_verificacion")

            factura_page.scroll_to_bottom()
            impuestos_page = FacturaImpuestosPage(self.driver)
            totales_imp = impuestos_page.registrar_totales_impuestos()
            self._registrar_paso("validar_impuestos_pre_timbrado", "exitoso", str(totales_imp))
            factura_page.tomar_evidencia_pantalla(caso_id, "05c_impuestos_pre_timbrado")
            factura_page.scroll_to_top()

            # ── PASO 8: Totales pre-timbrado ──────────────────────────
            logger.info("[CFDI MANUAL] [%s] Paso 8: Totales.", caso_id)
            totales = factura_page.validar_totales()
            self._guardar_resultado("totales_pre_timbrado", totales)
            self._registrar_paso("validar_totales", "exitoso", str(totales))
            factura_page.tomar_evidencia_pantalla(caso_id, "06_totales_validados")

            # ── PASO 9: Timbrar ───────────────────────────────────────
            logger.info("[CFDI MANUAL] [%s] Paso 9: Timbrar.", caso_id)
            resultado_timbrado = self.timbrar()
            if resultado_timbrado["estado"] == "fallido":
                factura_page.tomar_evidencia_pantalla(caso_id, "error_timbrado")
                return self._marcar_fallido(
                    f"Timbrado falló: {resultado_timbrado.get('error')}"
                )
            factura_page.tomar_evidencia_pantalla(caso_id, "07_timbrado_completado")

            # ── PASO 10: Validar resultado post-timbrado ──────────────
            logger.info("[CFDI MANUAL] [%s] Paso 10: Validar resultado.", caso_id)
            self.validar_resultado()

            # ── PASO 11: Descargar PDF / XML ──────────────────────────
            logger.info("[CFDI MANUAL] [%s] Paso 11: Descargar documentos.", caso_id)
            self.descargar_documentos(validaciones)
            factura_page.tomar_evidencia_pantalla(caso_id, "08_descarga_completada")

            logger.info(
                "[CFDI MANUAL] [%s] [%s] Flujo completado exitosamente.",
                tipo_flujo.upper(), caso_id,
            )
            return self._marcar_exitoso()

        except Exception as exc:
            logger.exception("[CFDI MANUAL] [%s] Error: %s", caso_id, exc)
            try:
                err_page = FacturaPage(self.driver)
                err_page._screenshot_dir = screenshot_dir
                err_page.tomar_evidencia_pantalla(caso_id, f"error_{tipo_flujo}_flow")
            except Exception:
                pass
            return self._marcar_fallido(str(exc))

    # ------------------------------------------------------------------
    # Helpers de sesión / navegación
    # ------------------------------------------------------------------

    def _login_portal(self) -> None:
        """Autentica en el portal usando credenciales del execution_context."""
        login_flow = LoginFlow(self.driver, self.context)
        result = login_flow.run(
            username=self._obtener_dato("username"),
            password=self._obtener_dato("password"),
            base_url=self._obtener_dato("base_url"),
        )
        if result["estado"] == "fallido":
            raise RuntimeError(
                f"Login falló: {result.get('error')}. "
                "Verificar credenciales en .env (USERNAME / PASSWORD)."
            )
        self._registrar_paso("login_portal", "exitoso")

    # Módulos que comparten la pantalla de Factura Manual (app-factura).
    # PPD no tiene pantalla propia; se genera desde el módulo Factura.
    _DESTINO_NAVEGACION: dict[str, str] = {
        "ppd": "factura",
    }

    def _navegar_portal(self, tipo_flujo: str) -> None:
        """
        Navega al módulo de emisión correspondiente al tipo_flujo.

        PPD no tiene pantalla propia en el portal FACTO 8; se emite desde
        el módulo de Factura Manual seleccionando metodo_pago=PPD en
        la sección Comprobante. Por eso se navega siempre a 'factura'.

        Args:
            tipo_flujo: "factura" | "ppd" — controla outputs y context keys,
                        NO el destino de navegación cuando comparten pantalla.
        """
        destino = self._DESTINO_NAVEGACION.get(tipo_flujo, tipo_flujo)
        nav_flow = NavigationFlow(self.driver, self.context)
        result = nav_flow.run(destino=destino)
        if result["estado"] == "fallido":
            raise RuntimeError(
                f"Navegación a '{destino}' (tipo_flujo='{tipo_flujo}') falló: "
                f"{result.get('error')}. "
                "Verificar: 1) usuario autenticado, 2) menú visible, "
                "3) URL del portal en .env configurada."
            )
        self._registrar_paso(f"navegar_portal_{tipo_flujo}", "exitoso")

    def _wait_for_angular_stable(self, timeout: int = 5) -> None:
        """Espera a que Angular termine de procesar el DOM."""
        try:
            FacturaPage(self.driver).wait_for_page_load(timeout=timeout)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Helpers por sección del formulario
    # ------------------------------------------------------------------

    def capturar_emisor(self, emisor_data: dict) -> None:
        """
        Captura Centro de Consumo y Serie del Emisor.

        Args:
            emisor_data: { "centro_consumo": str, "serie": str }
        """
        emisor_page = FacturaEmisorPage(self.driver)
        centro_consumo = emisor_data.get("centro_consumo", "")
        serie          = emisor_data.get("serie", "")
        if centro_consumo:
            emisor_page.select_centro_consumo(centro_consumo)
        if serie:
            emisor_page.select_serie(serie)
        self._registrar_paso(
            "capturar_emisor", "exitoso",
            f"centro_consumo={centro_consumo!r}, serie={serie!r}",
        )

    def capturar_receptor_desde_caso(self, caso: dict) -> None:
        """
        Captura datos del Receptor desde el dict plano del Excel.

        Args:
            caso: Dict plano con rfc_receptor, razon_social, codigo_postal,
                  regimen_fiscal_receptor, uso_cfdi, email, y campos domicilio.
        """
        receptor_page = FacturaReceptorPage(self.driver)
        rfc              = str(caso.get("rfc_receptor", "")).strip()
        razon_social_xl  = str(caso.get("razon_social", "")).strip()

        receptor_page.capturar_rfc_receptor(rfc)
        receptor_page.click_buscar_rfc()

        # Esperar auto-relleno del portal antes de sobreescribir
        _time.sleep(2)

        receptor_page.capturar_razon_social(razon_social_xl)
        razon_social_dom = receptor_page.leer_razon_social()
        logger.info(
            "[CFDI MANUAL] RECEPTOR — Excel: '%s' | DOM: '%s'",
            razon_social_xl, razon_social_dom,
        )
        if razon_social_xl.upper() != razon_social_dom.upper():
            logger.warning(
                "[CFDI MANUAL] razón social DOM ('%s') difiere del Excel ('%s')",
                razon_social_dom, razon_social_xl,
            )

        receptor_page.capturar_codigo_postal(str(caso.get("codigo_postal", "")).strip())
        receptor_page.seleccionar_regimen_fiscal_receptor(
            str(caso.get("regimen_fiscal_receptor", "")).strip()
        )
        receptor_page.seleccionar_uso_cfdi(str(caso.get("uso_cfdi", "")).strip())
        receptor_page.capturar_email(str(caso.get("email", "")).strip())

        if receptor_page.activar_domicilio_fiscal_si_aplica(caso):
            receptor_page.capturar_domicilio_fiscal(caso)

        self._registrar_paso("capturar_receptor", "exitoso", f"rfc={rfc!r}")

    def capturar_comprobante_desde_caso(self, caso: dict) -> None:
        """
        Captura la sección Comprobante desde el dict plano del Excel.

        Args:
            caso: Dict plano con fecha_emision, exportacion, moneda, tipo_cambio,
                  metodo_pago, forma_pago, condiciones_pago, observaciones_pdf, etc.
        """
        comprobante_page = FacturaComprobantePage(self.driver)
        comprobante_page.fill_comprobante_desde_caso(caso)
        self._registrar_paso(
            "capturar_comprobante", "exitoso",
            f"moneda={caso.get('moneda', 'MXN')!r}, metodo_pago={caso.get('metodo_pago', '')!r}",
        )

    def agregar_concepto_desde_caso(self, caso: dict) -> None:
        """
        Agrega el único concepto definido en el dict plano del Excel.

        Args:
            caso: Dict plano con descripcion_concepto, clave_unidad, cantidad,
                  clave_prod_serv, valor_unitario, descuento, objeto_impuesto,
                  impuesto, ret_tras, tipo_factor, tasa_o_cuota.
        """
        descripcion = str(caso.get("descripcion_concepto", "")).strip()
        if not descripcion:
            logger.warning("[CFDI MANUAL] descripcion_concepto vacío — se omite concepto.")
            return

        conceptos_page = FacturaConceptosPage(self.driver)
        conceptos_page.agregar_concepto_desde_caso(caso)

        count = conceptos_page.get_cantidad_conceptos()
        self._guardar_resultado("cantidad_conceptos", count)
        self._registrar_paso("agregar_concepto", "exitoso", descripcion)

        impuestos_page = FacturaImpuestosPage(self.driver)
        totales_imp    = impuestos_page.registrar_totales_impuestos()
        self._guardar_resultado("totales_impuestos", totales_imp)

    def capturar_receptor(self, receptor_data: dict) -> None:
        """
        Captura datos del Receptor desde dict anidado (formato legacy JSON).

        Args:
            receptor_data: { rfc, razon_social, codigo_postal,
                             regimen_fiscal, uso_cfdi, email }
        """
        if not receptor_data:
            logger.warning("[CFDI MANUAL] No hay datos de receptor.")
            return

        receptor_page = FacturaReceptorPage(self.driver)
        receptor_page.fill_receptor_completo(
            rfc=receptor_data.get("rfc", ""),
            razon_social=receptor_data.get("razon_social", ""),
            codigo_postal=receptor_data.get("codigo_postal", ""),
            regimen_fiscal=receptor_data.get("regimen_fiscal", ""),
            uso_cfdi=receptor_data.get("uso_cfdi", ""),
            email=receptor_data.get("email", ""),
            buscar_rfc=True,
        )
        self._registrar_paso(
            "capturar_receptor", "exitoso",
            f"rfc={receptor_data.get('rfc', '')!r}",
        )

    def capturar_comprobante(self, comprobante_data: dict) -> None:
        """
        Captura la sección Comprobante desde dict anidado (formato legacy JSON).

        Args:
            comprobante_data: { fecha_emision, exportacion, moneda, tipo_cambio,
                                metodo_pago, forma_pago, condiciones_pago,
                                observaciones, idioma, referencia }
        """
        if not comprobante_data:
            logger.warning("[CFDI MANUAL] No hay datos de comprobante.")
            return

        comprobante_page = FacturaComprobantePage(self.driver)
        comprobante_page.fill_comprobante_completo(
            fecha_emision=comprobante_data.get("fecha_emision", "AUTO"),
            exportacion=comprobante_data.get("exportacion", "01"),
            moneda=comprobante_data.get("moneda", "MXN"),
            tipo_cambio=comprobante_data.get("tipo_cambio"),
            metodo_pago=comprobante_data.get("metodo_pago"),
            forma_pago=comprobante_data.get("forma_pago"),
            condiciones_pago=comprobante_data.get("condiciones_pago"),
            notas=comprobante_data.get("observaciones"),
            idioma=comprobante_data.get("idioma", "ES"),
            referencia=comprobante_data.get("referencia"),
        )
        self._registrar_paso(
            "capturar_comprobante", "exitoso",
            f"moneda={comprobante_data.get('moneda', 'MXN')!r}, "
            f"metodo_pago={comprobante_data.get('metodo_pago', '')!r}",
        )

    def agregar_conceptos(self, conceptos: list) -> None:
        """
        Agrega múltiples conceptos desde una lista (formato legacy JSON).

        Args:
            conceptos: Lista de dicts con descripcion, cantidad, unidad,
                       clave_producto_servicio, valor_unitario, descuento, objeto_impuesto.
        """
        if not conceptos:
            logger.warning("[CFDI MANUAL] No hay conceptos — se salta la sección.")
            return

        conceptos_page = FacturaConceptosPage(self.driver)
        impuestos_page = FacturaImpuestosPage(self.driver)

        for idx, concepto in enumerate(conceptos, start=1):
            descripcion = concepto.get("descripcion", f"Concepto {idx}")
            logger.info(
                "[CFDI MANUAL] Agregando concepto %d/%d: %r",
                idx, len(conceptos), descripcion,
            )
            try:
                conceptos_page.agregar_concepto_completo(concepto)
            except Exception as exc:
                logger.exception(
                    "[CFDI MANUAL] Error al agregar concepto %d '%s': %s",
                    idx, descripcion, exc,
                )
                self._tomar_screenshot(f"error_concepto_{idx:02d}")
                raise
            self._registrar_paso(f"agregar_concepto_{idx}", "exitoso", descripcion)
            self._tomar_screenshot(f"05_{idx:02d}_concepto_agregado")

        count = conceptos_page.get_cantidad_conceptos()
        self._guardar_resultado("cantidad_conceptos", count)
        logger.info("[CFDI MANUAL] Total conceptos en formulario: %s", count)

        totales_imp = impuestos_page.registrar_totales_impuestos()
        self._guardar_resultado("totales_impuestos", totales_imp)

    def timbrar(self) -> dict:
        """
        Hace click en TIMBRAR CFDI y espera la respuesta del PAC/SAT.

        Returns:
            Resultado de FacturaTimbradoFlow con uuid_cfdi y datos.
        """
        factura_page = FacturaPage(self.driver)
        self._wait_for_angular_stable(timeout=5)

        if not factura_page.is_boton_timbrar_habilitado():
            logger.warning(
                "[CFDI MANUAL] Botón TIMBRAR CFDI está disabled. "
                "Posibles causas: campos obligatorios vacíos, errores de validación "
                "o falta de conceptos."
            )

        factura_page.click_timbrar()
        self._registrar_paso("click_timbrar_cfdi", "exitoso")

        timbrado_flow = FacturaTimbradoFlow(self.driver, self.context)
        return timbrado_flow.run()

    def validar_resultado(self) -> None:
        """Valida el UUID post-timbrado y lo registra en el contexto."""
        uuid_cfdi = self._obtener_dato("uuid_cfdi", "")
        if uuid_cfdi:
            self._registrar_paso(
                "resultado_timbrado_validado", "exitoso",
                f"UUID: {uuid_cfdi}",
            )
            logger.info("[CFDI MANUAL] UUID CFDI obtenido: %s", uuid_cfdi)
        else:
            logger.warning(
                "[CFDI MANUAL] UUID no disponible en contexto post-timbrado. "
                "Verificar implementación de FacturaTimbradoFlow."
            )
            self._registrar_paso(
                "resultado_timbrado_validado", "advertencia",
                "UUID no disponible (TODO: actualizar FacturaTimbradoFlow)",
            )

    def descargar_documentos(self, validaciones: dict) -> None:
        """
        Descarga PDF y/o XML según las instrucciones de validaciones.

        Usa FacturaDescargaFlow que a su vez usa FacturaResultadoPage —
        la pantalla de resultado es la misma para todos los tipos CFDI manual.

        Args:
            validaciones: { "descargar_pdf": bool, "descargar_xml": bool }
        """
        tipos = []
        if validaciones.get("descargar_pdf"):
            tipos.append("pdf")
        if validaciones.get("descargar_xml"):
            tipos.append("xml")

        if not tipos:
            return

        descarga_flow = FacturaDescargaFlow(self.driver, self.context)
        result = descarga_flow.run(tipos=tipos)

        estado = result.get("estado", "fallido")
        self._registrar_paso("descargar_documentos", estado, f"tipos={tipos}")

        if estado == "fallido":
            logger.warning(
                "[CFDI MANUAL] Descarga de documentos falló: %s. "
                "El flujo continúa (descarga no es crítica).",
                result.get("error"),
            )
