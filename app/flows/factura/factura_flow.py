"""
factura_flow.py - Flujo principal de emisión de Factura manual en el portal FACTO 8.

Orquesta el proceso completo de emisión de una Factura (CFDI tipo I - Ingreso)
usando la interfaz de generación manual del portal:

  1. Navegar al portal de emisión
  2. Verificar pantalla de generación de factura
  3. Capturar datos del Emisor (Centro de Consumo / Serie)
  4. Capturar datos del Receptor
  5. Capturar datos del Comprobante
  6. Agregar Conceptos
  7. Validar totales calculados
  8. Ejecutar timbrado (FacturaTimbradoFlow)
  9. Descargar documentos (FacturaDescargaFlow)

Uso:
    from app.flows.factura.factura_flow import FacturaFlow
    flow = FacturaFlow(driver, execution_context)
    result = flow.ejecutar_factura_manual(test_data)
"""
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

logger = get_logger(__name__)


class FacturaFlow(BaseFlow):
    """
    Flujo de emisión de Factura manual (CFDI tipo I - Ingreso).

    Coordina todos los page objects del módulo de Factura para
    completar el proceso de timbrado de principio a fin.

    Cada método helper representa un paso funcional del proceso.
    El método principal es ejecutar_factura_manual().
    """

    def run(self, **kwargs) -> dict:
        """
        Punto de entrada estándar del BaseFlow.

        Delega directamente a ejecutar_factura_manual() usando
        test_data del kwarg.

        Args:
            test_data: (dict) Datos estructurados del formulario.

        Returns:
            Resultado del flujo con estado, datos y error.
        """
        return self.ejecutar_factura_manual(kwargs.get("test_data", {}))

    # ------------------------------------------------------------------
    # Método principal de orquestación
    # ------------------------------------------------------------------

    def ejecutar_factura_manual(self, test_data: dict) -> dict:
        """
        Ejecuta el flujo completo de generación de factura manual.

        Acepta DOS formatos de entrada:
        1. Dict PLANO (Excel data-driven): claves directas como rfc_receptor,
           razon_social, moneda, concepto_descripcion, etc.
        2. Dict ANIDADO (legacy JSON): claves emisor/receptor/comprobante/conceptos.

        Detección automática: si el dict tiene clave 'rfc_receptor' o 'caso_id'
        se trata como plano; si tiene 'receptor' (dict) se trata como anidado.

        Args:
            test_data: Dict plano del Excel o dict anidado del JSON legacy.

        Returns:
            Diccionario estándar del BaseFlow:
            { "estado": "exitoso"|"fallido", "datos": dict, "error": str|None }
        """
        from pathlib import Path

        # --- Detectar formato y normalizar a estructura interna ---
        es_plano = "rfc_receptor" in test_data or "caso_id" in test_data
        caso_id  = str(test_data.get("caso_id", "FACTURA_RUN")).strip()

        if es_plano:
            emisor_data      = {"centro_consumo": test_data.get("centro_consumo", ""),
                                "serie":          test_data.get("serie", "")}
            receptor_data    = {"rfc":            test_data.get("rfc_receptor", ""),
                                "razon_social":   test_data.get("razon_social", ""),
                                "codigo_postal":  test_data.get("codigo_postal", ""),
                                "regimen_fiscal": test_data.get("regimen_fiscal", ""),
                                "uso_cfdi":       test_data.get("uso_cfdi", ""),
                                "email":          test_data.get("email", "")}
            comprobante_data = test_data  # fill_comprobante_desde_caso lee desde el mismo dict
            conceptos        = None       # se usa agregar_concepto_desde_caso
            validaciones     = {"descargar_pdf": test_data.get("descargar_pdf", False),
                                "descargar_xml": test_data.get("descargar_xml", False)}
        else:
            emisor_data      = test_data.get("emisor", {})
            receptor_data    = test_data.get("receptor", {})
            comprobante_data = test_data.get("comprobante", {})
            conceptos        = test_data.get("conceptos", [])
            validaciones     = test_data.get("validaciones", {})

        # --- Crear directorio de evidencias por caso_id ---
        evidence_dir = Path("outputs") / "factura" / caso_id / "screenshots"
        try:
            evidence_dir.mkdir(parents=True, exist_ok=True)
            self.context.set_dato("evidence_dir", str(evidence_dir))
            logger.info(f"[FACTURA FLOW] Directorio de evidencias: {evidence_dir}")
        except Exception as exc:
            logger.warning(f"[FACTURA FLOW] No se pudo crear evidence_dir: {exc}")

        self._registrar_inicio()

        try:
            # ----------------------------------------------------------
            # PASO 0: Login en el portal
            # ----------------------------------------------------------
            logger.info(f"[FACTURA FLOW] [{caso_id}] Paso 0: Autenticación.")
            self._login_portal()

            # ----------------------------------------------------------
            # PASO 1: Navegar al portal de emisión de Factura
            # ----------------------------------------------------------
            logger.info(f"[FACTURA FLOW] [{caso_id}] Paso 1: Navegar al portal.")
            self._navegar_portal()

            # ----------------------------------------------------------
            # PASO 2: Verificar que la pantalla de Factura está cargada
            # ----------------------------------------------------------
            logger.info(f"[FACTURA FLOW] [{caso_id}] Paso 2: Verificar pantalla.")
            factura_page = FacturaPage(self.driver)
            factura_page.wait_for_pantalla_factura()
            self._registrar_paso("pantalla_factura_cargada", "exitoso")
            factura_page.tomar_evidencia_pantalla(caso_id, "01_pantalla_factura_cargada")

            # ----------------------------------------------------------
            # PASO 3: Capturar datos del Emisor
            # ----------------------------------------------------------
            logger.info(f"[FACTURA FLOW] [{caso_id}] Paso 3: Emisor.")
            self.capturar_emisor(emisor_data)
            factura_page.tomar_evidencia_pantalla(caso_id, "02_emisor_capturado")

            # ----------------------------------------------------------
            # PASO 4: Capturar datos del Receptor
            # ----------------------------------------------------------
            logger.info(f"[FACTURA FLOW] [{caso_id}] Paso 4: Receptor.")
            if es_plano:
                self.capturar_receptor_desde_caso(test_data)
            else:
                self.capturar_receptor(receptor_data)
            factura_page.tomar_evidencia_pantalla(caso_id, "03_receptor_capturado")

            # ----------------------------------------------------------
            # PASO 5: Capturar datos del Comprobante
            # ----------------------------------------------------------
            logger.info(f"[FACTURA FLOW] [{caso_id}] Paso 5: Comprobante.")
            if es_plano:
                self.capturar_comprobante_desde_caso(comprobante_data)
            else:
                self.capturar_comprobante(comprobante_data)
            factura_page.tomar_evidencia_pantalla(caso_id, "04_comprobante_capturado")

            # ----------------------------------------------------------
            # PASO 6: Cargos No Facturables (condicional)
            # ----------------------------------------------------------
            if es_plano and test_data.get("cargo_no_facturable_nombre"):
                logger.info(f"[FACTURA FLOW] [{caso_id}] Paso 6a: Cargos no facturables.")
                cargos_page = FacturaCargosNoFacturablesPage(self.driver)
                cargos_page.agregar_cargo_desde_caso(test_data)
                factura_page.tomar_evidencia_pantalla(caso_id, "05a_cargo_no_facturable")

            # ----------------------------------------------------------
            # PASO 7: Agregar Conceptos
            # ----------------------------------------------------------
            logger.info(f"[FACTURA FLOW] [{caso_id}] Paso 7: Conceptos.")
            if es_plano:
                self.agregar_concepto_desde_caso(test_data)
            else:
                self.agregar_conceptos(conceptos or [])
            factura_page.tomar_evidencia_pantalla(caso_id, "05_conceptos_agregados")

            # ----------------------------------------------------------
            # PASO 7.5: Validar que Guardar Concepto fue ejecutado
            #           y capturar evidencia de impuestos calculados
            # ----------------------------------------------------------
            logger.info(f"[FACTURA FLOW] [{caso_id}] Paso 7.5: Validar concepto guardado e impuestos.")
            conceptos_page = FacturaConceptosPage(self.driver)
            cantidad_conceptos = conceptos_page.get_cantidad_conceptos()
            if cantidad_conceptos == 0:
                raise AssertionError(
                    "[PRE-TIMBRADO] No se encontró ningún concepto en la tabla. "
                    "Verifica que el botón 'Guardar Concepto' fue ejecutado correctamente."
                )
            logger.info(
                f"[FACTURA FLOW] [{caso_id}] ✔ Concepto(s) confirmado(s) en tabla: {cantidad_conceptos}"
            )
            self._registrar_paso(
                "validar_concepto_guardado", "exitoso",
                f"conceptos en tabla: {cantidad_conceptos}"
            )
            # Screenshot con la tabla de conceptos visible (prueba de guardar)
            factura_page.tomar_evidencia_pantalla(caso_id, "05b_concepto_guardado_verificacion")

            # Scroll al final para mostrar la sección de Impuestos y capturar evidencia
            factura_page.scroll_to_bottom()
            impuestos_page = FacturaImpuestosPage(self.driver)
            totales_imp = impuestos_page.registrar_totales_impuestos()
            self._registrar_paso(
                "validar_impuestos_pre_timbrado", "exitoso", str(totales_imp)
            )
            factura_page.tomar_evidencia_pantalla(caso_id, "05c_impuestos_pre_timbrado")
            factura_page.scroll_to_top()

            # ----------------------------------------------------------
            # PASO 8: Validar totales calculados antes de timbrar
            # ----------------------------------------------------------
            logger.info(f"[FACTURA FLOW] [{caso_id}] Paso 8: Totales.")
            totales = factura_page.validar_totales()
            self._guardar_resultado("totales_pre_timbrado", totales)
            self._registrar_paso("validar_totales", "exitoso", str(totales))
            factura_page.tomar_evidencia_pantalla(caso_id, "06_totales_validados")

            # ----------------------------------------------------------
            # PASO 9: Timbrar CFDI
            # ----------------------------------------------------------
            logger.info(f"[FACTURA FLOW] [{caso_id}] Paso 9: Timbrar.")
            resultado_timbrado = self.timbrar()
            if resultado_timbrado["estado"] == "fallido":
                factura_page.tomar_evidencia_pantalla(caso_id, "error_timbrado")
                return self._marcar_fallido(
                    f"Timbrado falló: {resultado_timbrado.get('error')}"
                )
            factura_page.tomar_evidencia_pantalla(caso_id, "07_timbrado_completado")

            # ----------------------------------------------------------
            # PASO 10: Validar resultado post-timbrado
            # ----------------------------------------------------------
            logger.info(f"[FACTURA FLOW] [{caso_id}] Paso 10: Validar resultado.")
            self.validar_resultado()

            # ----------------------------------------------------------
            # PASO 11: Descargar documentos (condicional)
            # ----------------------------------------------------------
            if validaciones.get("descargar_pdf") or validaciones.get("descargar_xml"):
                logger.info(f"[FACTURA FLOW] [{caso_id}] Paso 11: Descargar documentos.")
                self.descargar_documentos(validaciones)
                factura_page.tomar_evidencia_pantalla(caso_id, "08_descarga_completada")

            logger.info(f"[FACTURA FLOW] [{caso_id}] Flujo completado exitosamente.")
            return self._marcar_exitoso()

        except Exception as exc:
            logger.exception(f"[FACTURA FLOW] [{caso_id}] Error: {exc}")
            try:
                FacturaPage(self.driver).tomar_evidencia_pantalla(caso_id, "error_factura_flow")
            except Exception:
                pass
            return self._marcar_fallido(str(exc))

    # ------------------------------------------------------------------
    # Métodos helper por sección del formulario
    # ------------------------------------------------------------------

    def _login_portal(self) -> None:
        """
        Autentica al usuario en el portal FACTO usando LoginFlow.

        Lee las credenciales del contexto de ejecución (inyectadas por conftest).

        Raises:
            RuntimeError: Si el login falla.
        """
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

    def _navegar_portal(self) -> None:
        """
        Navega al portal de emisión de Factura usando NavigationFlow.

        Raises:
            RuntimeError: Si el menú no está disponible o la navegación falla.
        """
        nav_flow = NavigationFlow(self.driver, self.context)
        result = nav_flow.run(destino="factura")
        if result["estado"] == "fallido":
            raise RuntimeError(
                f"Navegación a factura falló: {result.get('error')}. "
                "Verificar: 1) usuario autenticado, 2) menú visible, "
                "3) URL del portal en .env configurada."
            )
        self._registrar_paso("navegar_portal_factura", "exitoso")

    def _wait_for_angular_stable(self, timeout: int = 5) -> None:
        """
        Espera a que Angular termine de procesar cambios en el DOM.

        Usa document.readyState como proxy de estabilidad. Angular puede
        tardar en recalcular bindings y totales tras interacciones.

        Args:
            timeout: Segundos máximos de espera.
        """
        try:
            factura_page = FacturaPage(self.driver)
            factura_page.wait_for_page_load(timeout=timeout)
            logger.debug("[FACTURA FLOW] DOM estable (readyState = complete).")
        except Exception as exc:
            logger.debug(f"[FACTURA FLOW] wait_for_angular_stable ignorado: {exc}")

    def capturar_emisor(self, emisor_data: dict) -> None:
        """
        Captura los datos del Emisor (Centro de Consumo y Serie).

        En FACTO 8, el emisor tiene datos pre-cargados (readonly). Solo
        Centro de Consumo y Serie pueden ser seleccionables.

        Args:
            emisor_data: { "centro_consumo": str, "serie": str }
        """
        emisor_page = FacturaEmisorPage(self.driver)

        centro_consumo = emisor_data.get("centro_consumo", "")
        serie = emisor_data.get("serie", "")

        if centro_consumo:
            emisor_page.select_centro_consumo(centro_consumo)

        if serie:
            emisor_page.select_serie(serie)

        self._registrar_paso(
            "capturar_emisor",
            "exitoso",
            f"centro_consumo={centro_consumo!r}, serie={serie!r}",
        )

    def capturar_receptor_desde_caso(self, caso: dict) -> None:
        """
        Captura los datos del Receptor usando el dict plano del Excel.

        Llama a los métodos alias de FacturaReceptorPage que aceptan
        el formato del dict plano.

        Args:
            caso: Dict plano del Excel con claves rfc_receptor, razon_social,
                  codigo_postal, regimen_fiscal, uso_cfdi, email, etc.
        """
        receptor_page = FacturaReceptorPage(self.driver)

        rfc = str(caso.get("rfc_receptor", "")).strip()
        if not rfc:
            logger.warning("[FACTURA FLOW] rfc_receptor vacío en el caso.")

        receptor_page.capturar_rfc_receptor(rfc)
        receptor_page.click_buscar_rfc()
        receptor_page.capturar_razon_social(str(caso.get("razon_social", "")).strip())
        receptor_page.capturar_codigo_postal(str(caso.get("codigo_postal", "")).strip())
        receptor_page.seleccionar_regimen_fiscal_receptor(str(caso.get("regimen_fiscal_receptor", "")).strip())
        receptor_page.seleccionar_uso_cfdi(str(caso.get("uso_cfdi", "")).strip())
        receptor_page.capturar_email(str(caso.get("email", "")).strip())

        # Domicilio fiscal (opcional)
        if receptor_page.activar_domicilio_fiscal_si_aplica(caso):
            receptor_page.capturar_domicilio_fiscal(caso)

        self._registrar_paso("capturar_receptor", "exitoso", f"rfc={rfc!r}")

    def capturar_comprobante_desde_caso(self, caso: dict) -> None:
        """
        Captura los datos del Comprobante usando el dict plano del Excel.

        Args:
            caso: Dict plano del Excel con claves fecha_emision, exportacion,
                  moneda, tipo_cambio, metodo_pago, forma_pago, etc.
        """
        comprobante_page = FacturaComprobantePage(self.driver)
        comprobante_page.fill_comprobante_desde_caso(caso)
        self._registrar_paso(
            "capturar_comprobante", "exitoso",
            f"moneda={caso.get('moneda', 'MXN')!r}",
        )

    def agregar_concepto_desde_caso(self, caso: dict) -> None:
        """
        Agrega el concepto del caso usando el dict plano del Excel.

        Solo agrega un concepto por caso (el Excel define un concepto por fila).
        Si concepto_descripcion está vacío, se omite.

        Args:
            caso: Dict plano del Excel con claves concepto_descripcion,
                  concepto_cantidad, concepto_valor_unitario, etc.
        """
        descripcion = str(caso.get("descripcion_concepto", "")).strip()
        if not descripcion:
            logger.warning("[FACTURA FLOW] descripcion_concepto vacío — se omite concepto.")
            return

        conceptos_page = FacturaConceptosPage(self.driver)
        conceptos_page.agregar_concepto_desde_caso(caso)

        count = conceptos_page.get_cantidad_conceptos()
        self._guardar_resultado("cantidad_conceptos", count)
        self._registrar_paso("agregar_concepto", "exitoso", descripcion)

        # Registrar totales de impuestos disponibles (no bloquea si no hay sección)
        impuestos_page = FacturaImpuestosPage(self.driver)
        totales_imp = impuestos_page.registrar_totales_impuestos()
        self._guardar_resultado("totales_impuestos", totales_imp)

    def capturar_receptor(self, receptor_data: dict) -> None:
        """
        Captura los datos del Receptor usando FacturaReceptorPage (formato anidado).

        Args:
            receptor_data: {
                "rfc":            str,
                "razon_social":   str,
                "codigo_postal":  str,
                "regimen_fiscal": str,  # código SAT (ej: '616')
                "uso_cfdi":       str,  # código SAT (ej: 'S01')
                "email":          str
            }
        """
        if not receptor_data:
            logger.warning("[FACTURA FLOW] No hay datos de receptor en test_data.")
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
            "capturar_receptor",
            "exitoso",
            f"rfc={receptor_data.get('rfc', '')!r}",
        )

    def capturar_comprobante(self, comprobante_data: dict) -> None:
        """
        Captura los datos del Comprobante usando FacturaComprobantePage.

        Args:
            comprobante_data: {
                "fecha_emision":    str,  # ISO o 'AUTO'
                "exportacion":      str,  # '01', '02', '03'
                "moneda":           str,  # 'MXN', 'USD', etc.
                "tipo_cambio":      str,  # solo si moneda != 'MXN'
                "metodo_pago":      str,  # texto visible: 'PUE - Pago en una sola exhibición'
                "forma_pago":       str,  # texto visible: '01 - Efectivo'
                "condiciones_pago": str,
                "observaciones":    str,
                "idioma":           str,  # 'ES' o 'EN'
                "referencia":       str
            }
        """
        if not comprobante_data:
            logger.warning("[FACTURA FLOW] No hay datos de comprobante en test_data.")
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
            "capturar_comprobante",
            "exitoso",
            f"moneda={comprobante_data.get('moneda', 'MXN')!r}, "
            f"metodo_pago={comprobante_data.get('metodo_pago', '')!r}",
        )

    def agregar_conceptos(self, conceptos: list) -> None:
        """
        Agrega uno o más conceptos al formulario de Factura.

        Itera sobre la lista de conceptos y agrega cada uno a través
        del modal de captura. Toma screenshot después de cada concepto.

        Args:
            conceptos: Lista de dicts, cada uno con:
                {
                    "descripcion":             str,
                    "cantidad":                str,
                    "unidad":                  str,   # clave SAT (ej: 'E48')
                    "clave_producto_servicio": str,   # clave SAT (ej: '90111501')
                    "valor_unitario":          str,
                    "descuento":               str,   # opcional
                    "objeto_impuesto":         str    # '01' o '02'
                }
        """
        if not conceptos:
            logger.warning("[FACTURA FLOW] No hay conceptos en test_data. Se salta la sección.")
            return

        conceptos_page = FacturaConceptosPage(self.driver)
        impuestos_page = FacturaImpuestosPage(self.driver)

        for idx, concepto in enumerate(conceptos, start=1):
            descripcion = concepto.get("descripcion", f"Concepto {idx}")
            logger.info(f"[FACTURA FLOW] Agregando concepto {idx}/{len(conceptos)}: {descripcion!r}")
            try:
                conceptos_page.agregar_concepto_completo(concepto)
            except Exception as exc:
                logger.exception(
                    f"[FACTURA FLOW] Error al agregar concepto {idx} '{descripcion}': {exc}"
                )
                self._tomar_screenshot(f"error_concepto_{idx:02d}")
                raise
            self._registrar_paso(
                f"agregar_concepto_{idx}",
                "exitoso",
                descripcion,
            )
            self._tomar_screenshot(f"05_{idx:02d}_concepto_agregado")

        count = conceptos_page.get_cantidad_conceptos()
        self._guardar_resultado("cantidad_conceptos", count)
        logger.info(f"[FACTURA FLOW] Total conceptos en formulario: {count}")

        # Registrar totales de impuestos disponibles (no bloquea si no hay sección)
        totales_imp = impuestos_page.registrar_totales_impuestos()
        self._guardar_resultado("totales_impuestos", totales_imp)

    def timbrar(self) -> dict:
        """
        Ejecuta el timbrado del CFDI.

        Verifica que el botón TIMBRAR esté habilitado antes de hacer click.
        Espera estabilidad Angular, luego delega a FacturaTimbradoFlow.

        Returns:
            Resultado de FacturaTimbradoFlow con uuid_cfdi y datos.
        """
        factura_page = FacturaPage(self.driver)

        # Esperar estabilidad del DOM antes de timbrar
        self._wait_for_angular_stable(timeout=5)

        # Verificar que el botón está habilitado (no disabled)
        if not factura_page.is_boton_timbrar_habilitado():
            logger.warning(
                "[FACTURA FLOW] Botón TIMBRAR CFDI está disabled. "
                "Posibles causas: campos obligatorios vacíos, errores de validación, "
                "o falta de conceptos en el formulario."
            )

        factura_page.click_timbrar()
        self._registrar_paso("click_timbrar_cfdi", "exitoso")

        timbrado_flow = FacturaTimbradoFlow(self.driver, self.context)
        return timbrado_flow.run()

    def validar_resultado(self) -> None:
        """
        Valida que el timbrado fue exitoso y registra el UUID en el contexto.

        El UUID es leído del contexto (guardado por FacturaTimbradoFlow).
        Si no hay UUID, lanza advertencia pero no detiene el flujo.
        """
        uuid_cfdi = self._obtener_dato("uuid_cfdi", "")
        if uuid_cfdi:
            self._registrar_paso(
                "resultado_timbrado_validado",
                "exitoso",
                f"UUID: {uuid_cfdi}",
            )
            logger.info(f"[FACTURA FLOW] UUID CFDI obtenido: {uuid_cfdi}")
        else:
            logger.warning(
                "[FACTURA FLOW] UUID no disponible en contexto post-timbrado. "
                "Verificar implementación de FacturaTimbradoFlow."
            )
            self._registrar_paso(
                "resultado_timbrado_validado",
                "advertencia",
                "UUID no disponible (TODO: actualizar FacturaTimbradoFlow)",
            )

    def descargar_documentos(self, validaciones: dict) -> None:
        """
        Descarga PDF y/o XML según las instrucciones de validaciones.

        Args:
            validaciones: {
                "descargar_pdf": bool,
                "descargar_xml": bool
            }
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
        self._registrar_paso(
            "descargar_documentos",
            estado,
            f"tipos={tipos}",
        )
        if estado == "fallido":
            logger.warning(
                f"[FACTURA FLOW] Descarga de documentos falló: {result.get('error')}. "
                "El flujo continúa (descarga no es crítica)."
            )
