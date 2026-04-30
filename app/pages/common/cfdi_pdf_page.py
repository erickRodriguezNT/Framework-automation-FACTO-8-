"""
cfdi_pdf_page.py — Page Object para el visor de PDF embebido en el portal CFDI.

Compartido entre todos los flujos que muestran un preview de PDF post-timbrado.

Responsabilidades:
1. Detectar el contenedor del PDF (iframe / embed / object / Angular viewer).
2. Cambiar contexto de Selenium al iframe si aplica.
3. Extraer el contenido base64 del DOM cuando el render visual falla.
4. Guardar el PDF desde base64 como alternativa robusta al render visual.
5. Validar el archivo PDF descargado (magic bytes, tamaño, existencia).

Estrategia de validación (en orden de confiabilidad):
  PRIMARIA  → validar el archivo descargado en disco (validate_pdf_file)
  SECUNDARIA → extraer base64 del DOM y guardar (save_pdf_from_base64)
  FALLBACK   → verificar que el botón de descarga sea clickeable

Uso:
    from app.pages.common.cfdi_pdf_page import CfdiPdfPage

    pdf_page = CfdiPdfPage(driver)

    # Opción A: Esperar visor + validar archivo descargado
    pdf_page.wait_for_pdf_viewer(timeout=10)
    resultado = pdf_page.validate_pdf_descargado(download_dir, timeout=30)

    # Opción B: Extraer base64 si el render falla
    path = pdf_page.save_pdf_from_base64(Path("outputs/factura/F001/preview.pdf"))
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from app.core.base_page import BasePage
from app.utils.logger import get_logger
from app.utils.pdf_validator import (
    save_pdf_from_base64 as _save_b64,
    validate_pdf_file,
    wait_for_pdf_download,
)

logger = get_logger(__name__)


class CfdiPdfPage(BasePage):
    """
    Page Object para interactuar con el visor de PDF post-timbrado.

    Compatible con los módulos Factura, Nota de Crédito y cualquier
    flujo futuro que use el componente ``app-factura-timbrada``.
    """

    # ── Visor Angular del portal ──────────────────────────────────────────
    _VISOR_ANGULAR = (By.CSS_SELECTOR, "app-factura-timbrada")

    # ── Contenedores de PDF dentro del visor (iframe > embed > object) ────
    _IFRAME_EN_VISOR = (By.CSS_SELECTOR, "app-factura-timbrada iframe")
    _EMBED_EN_VISOR  = (By.CSS_SELECTOR, "app-factura-timbrada embed")
    _OBJECT_EN_VISOR = (By.CSS_SELECTOR, "app-factura-timbrada object")

    # ── Contenedores genéricos (fallback si no es el visor Angular) ───────
    _LOCATORS_PDF_GENERICO = [
        (By.CSS_SELECTOR, "iframe[src*='.pdf']"),
        (By.CSS_SELECTOR, "iframe[src*='application/pdf']"),
        (By.CSS_SELECTOR, "embed[type='application/pdf']"),
        (By.CSS_SELECTOR, "embed[src*='data:application/pdf']"),
        (By.CSS_SELECTOR, "object[type='application/pdf']"),
        (By.CSS_SELECTOR, "object[data*='.pdf']"),
    ]

    # ── JS para extraer data URI base64 del DOM ───────────────────────────
    _JS_EXTRACT_BASE64 = """
        (function() {
            var selectors = [
                'app-factura-timbrada embed',
                'app-factura-timbrada iframe',
                'app-factura-timbrada object',
                'embed[type="application/pdf"]',
                'embed[src*="data:application/pdf"]',
                'object[type="application/pdf"]',
                'object[data*="data:application/pdf"]',
                'iframe[src*="data:application/pdf"]'
            ];
            for (var i = 0; i < selectors.length; i++) {
                var el = document.querySelector(selectors[i]);
                if (!el) continue;
                var src = el.getAttribute('src')
                         || el.getAttribute('data')
                         || '';
                if (src.indexOf('application/pdf') !== -1
                    || src.startsWith('data:')
                    || src.indexOf('%PDF') !== -1) {
                    return src;
                }
            }
            return null;
        })();
    """

    # ─────────────────────────────────────────────────────────────────────
    # Métodos públicos
    # ─────────────────────────────────────────────────────────────────────

    def wait_for_pdf_viewer(self, timeout: int = 10) -> bool:
        """
        Espera a que aparezca algún contenedor de PDF en el DOM.

        Orden de búsqueda:
        1. Visor Angular ``app-factura-timbrada``
        2. iframe / embed / object con PDF genérico

        Args:
            timeout: Segundos máximos de espera. Default: 10.

        Returns:
            ``True`` si se encontró un contenedor; ``False`` si expiró.
        """
        # 1) Visor Angular
        if self.is_visible(self._VISOR_ANGULAR, timeout=timeout):
            logger.info("[PDF PAGE] Visor Angular detectado: app-factura-timbrada")
            return True

        # 2) Contenedores genéricos (2 s cada uno para no bloquear)
        for locator in self._LOCATORS_PDF_GENERICO:
            if self.is_visible(locator, timeout=2):
                logger.info(
                    "[PDF PAGE] Contenedor PDF genérico detectado: %s = %s", *locator
                )
                return True

        logger.warning("[PDF PAGE] No se detectó visor de PDF en %ds", timeout)
        return False

    def switch_to_pdf_iframe(self) -> bool:
        """
        Cambia el contexto de Selenium al iframe que contiene el PDF.

        Busca primero dentro de ``app-factura-timbrada``, luego genérico.
        Usar :meth:`switch_back_to_default` para restaurar el contexto.

        Returns:
            ``True`` si el cambio fue exitoso; ``False`` si no hay iframe.
        """
        iframe_locators = [
            self._IFRAME_EN_VISOR,
            (By.CSS_SELECTOR, "iframe[src*='.pdf']"),
            (By.CSS_SELECTOR, "iframe[src*='application/pdf']"),
        ]

        for locator in iframe_locators:
            try:
                iframe = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located(locator)
                )
                self.driver.switch_to.frame(iframe)
                logger.info(
                    "[PDF PAGE] Contexto cambiado a iframe: %s = %s", *locator
                )
                return True
            except Exception:
                continue

        logger.warning("[PDF PAGE] No se encontró iframe de PDF")
        return False

    def switch_back_to_default(self) -> None:
        """Restaura el contexto de Selenium al frame principal (default content)."""
        try:
            self.driver.switch_to.default_content()
            logger.info("[PDF PAGE] Contexto restaurado al frame principal")
        except Exception as exc:
            logger.warning("[PDF PAGE] Error restaurando frame principal: %s", exc)

    def extract_base64_pdf(self) -> Optional[str]:
        """
        Extrae el contenido base64 de un PDF embebido en el DOM.

        Busca el atributo ``src`` / ``data`` de embed/object/iframe que
        contenga un data URI de tipo ``application/pdf``.

        Returns:
            String base64 (puede incluir prefijo ``data:application/pdf;base64,``),
            o ``None`` si no se encontró ningún contenedor con PDF base64.
        """
        try:
            result = self.driver.execute_script(self._JS_EXTRACT_BASE64)
            if result:
                is_b64 = "base64" in result
                logger.info(
                    "[PDF PAGE] Contenido PDF extraído: %s (longitud=%d)",
                    "base64" if is_b64 else "URL directa",
                    len(result),
                )
                return result

            logger.warning("[PDF PAGE] No se encontró PDF base64 en el DOM")
            return None

        except Exception as exc:
            logger.exception("[PDF PAGE] Error extrayendo base64 del DOM: %s", exc)
            return None

    def save_pdf_from_base64(self, dest_path: Path) -> Optional[Path]:
        """
        Extrae el base64 del DOM y lo guarda como archivo PDF en disco.

        Método alternativo cuando el render visual del PDF no está disponible
        (por ejemplo, en Selenium donde el visor puede mostrar "Abrir" en lugar
        del PDF renderizado).

        Args:
            dest_path: Ruta destino para guardar el archivo PDF.

        Returns:
            ``Path`` al archivo guardado, o ``None`` si falló.
        """
        b64 = self.extract_base64_pdf()
        if not b64:
            logger.warning("[PDF PAGE] No hay base64 para guardar en %s", dest_path)
            return None

        saved = _save_b64(b64, dest_path)
        if saved:
            logger.info("[PDF PAGE] PDF guardado desde base64: %s", saved)
        return saved

    def validate_pdf_descargado(
        self,
        download_dir,
        timeout: int = 30,
    ) -> dict:
        """
        Validación robusta del PDF descargado en disco.

        Espera a que aparezca el archivo y verifica:
        - Existencia del archivo.
        - Tamaño > 0.
        - Magic bytes ``%PDF-``.

        Esta es la validación PRIMARIA (más confiable que el render visual).

        Args:
            download_dir: Directorio donde Chrome guarda las descargas.
            timeout:       Segundos máximos de espera. Default: 30.

        Returns:
            Diccionario con claves ``exists``, ``size_bytes``,
            ``is_valid_pdf``, ``error``, ``path``.
        """
        result: dict = {
            "exists": False,
            "size_bytes": 0,
            "is_valid_pdf": False,
            "error": None,
            "path": None,
        }

        try:
            pdf_path = wait_for_pdf_download(
                download_dir=download_dir,
                timeout=timeout,
            )

            if pdf_path is None:
                result["error"] = (
                    f"PDF no descargado en {timeout}s. "
                    f"Directorio: {download_dir}"
                )
                logger.warning("[PDF PAGE] %s", result["error"])
                return result

            validation = validate_pdf_file(pdf_path)
            result.update(validation)
            result["path"] = str(pdf_path)

            if result["is_valid_pdf"]:
                logger.info(
                    "[PDF PAGE] Validación PDF exitosa: %s (%d bytes)",
                    pdf_path.name,
                    result["size_bytes"],
                )
            else:
                logger.warning(
                    "[PDF PAGE] Validación PDF fallida: %s — %s",
                    pdf_path.name,
                    result["error"],
                )

        except Exception as exc:
            result["error"] = str(exc)
            logger.exception("[PDF PAGE] Error en validate_pdf_descargado: %s", exc)

        return result
