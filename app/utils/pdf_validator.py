"""
pdf_validator.py — Utilidades de validación de archivos PDF descargados.

Funciones puras (sin Selenium) para:
- Validar que un archivo es un PDF real (magic bytes %PDF-).
- Esperar a que un PDF aparezca en el directorio de descargas.
- Decodificar base64 y guardar como archivo PDF.

Estas funciones son el mecanismo de validación ROBUSTO cuando el render
visual del PDF en el navegador no es confiable.

Uso:
    from app.utils.pdf_validator import validate_pdf_file, wait_for_pdf_download

    path = wait_for_pdf_download(download_dir="outputs/factura/F001", timeout=30)
    if path:
        result = validate_pdf_file(path)
        assert result["is_valid_pdf"]
"""
import base64
import time
from pathlib import Path
from typing import Optional

from app.utils.logger import get_logger

logger = get_logger(__name__)

# Magic bytes que inician todo PDF válido
_PDF_MAGIC = b"%PDF-"


def validate_pdf_file(file_path) -> dict:
    """
    Valida que un archivo en disco es un PDF válido.

    Comprueba:
    - El archivo existe.
    - El tamaño es mayor a 0 bytes.
    - Los primeros 5 bytes son ``%PDF-`` (magic bytes estándar).

    Args:
        file_path: Ruta al archivo (str o Path).

    Returns:
        Diccionario con claves:
          - ``exists``       (bool)
          - ``size_bytes``   (int)
          - ``is_valid_pdf`` (bool)
          - ``error``        (str | None)
    """
    result: dict = {
        "exists": False,
        "size_bytes": 0,
        "is_valid_pdf": False,
        "error": None,
    }

    try:
        path = Path(file_path)
        result["exists"] = path.exists()

        if not result["exists"]:
            result["error"] = f"Archivo no encontrado: {path}"
            logger.warning("[PDF VALIDATOR] %s", result["error"])
            return result

        size = path.stat().st_size
        result["size_bytes"] = size

        if size == 0:
            result["error"] = f"El archivo está vacío: {path.name}"
            logger.warning("[PDF VALIDATOR] %s", result["error"])
            return result

        with open(path, "rb") as fh:
            header = fh.read(5)

        result["is_valid_pdf"] = header == _PDF_MAGIC

        if not result["is_valid_pdf"]:
            result["error"] = (
                f"No es un PDF válido. Header encontrado: {header!r} "
                f"(esperado: {_PDF_MAGIC!r})"
            )
            logger.warning("[PDF VALIDATOR] %s — %s", path.name, result["error"])
        else:
            logger.info(
                "[PDF VALIDATOR] PDF válido: %s (%d bytes)",
                path.name,
                size,
            )

    except Exception as exc:
        result["error"] = str(exc)
        logger.exception("[PDF VALIDATOR] Error validando %s: %s", file_path, exc)

    return result


def wait_for_pdf_download(
    download_dir,
    timeout: int = 30,
    poll_interval: float = 0.5,
) -> Optional[Path]:
    """
    Espera a que un PDF aparezca y termine de descargarse en el directorio.

    Considera la descarga completa cuando:
    - Existe un archivo ``.pdf`` (no ``.crdownload`` ni ``.tmp``).
    - El tamaño es > 0 y estable entre dos polls consecutivos.

    Nota: Esta función usa ``time.sleep`` intencionalmente porque es un
    sondeo del sistema de archivos (no del DOM), donde WebDriverWait no aplica.

    Args:
        download_dir: Directorio a monitorear (str o Path).
        timeout:       Segundos máximos de espera. Default: 30.
        poll_interval: Segundos entre cada sondeo. Default: 0.5.

    Returns:
        ``Path`` al PDF descargado, o ``None`` si se agota el timeout.
    """
    dir_path = Path(download_dir)
    deadline = time.monotonic() + timeout
    last_size: int = -1
    candidate: Optional[Path] = None

    logger.info(
        "[PDF VALIDATOR] Esperando descarga PDF en: %s (timeout=%ds)",
        dir_path,
        timeout,
    )

    while time.monotonic() < deadline:
        # Excluir .crdownload (Chrome in-progress) y .tmp
        pdfs = [
            p
            for p in dir_path.glob("*.pdf")
            if p.suffix.lower() == ".pdf"
        ]

        if pdfs:
            # Tomar el más reciente si hay múltiples
            candidate = max(pdfs, key=lambda p: p.stat().st_mtime)
            current_size = candidate.stat().st_size

            # Tamaño estable y > 0 → descarga completa
            if current_size > 0 and current_size == last_size:
                logger.info(
                    "[PDF VALIDATOR] Descarga completada: %s (%d bytes)",
                    candidate.name,
                    current_size,
                )
                return candidate

            last_size = current_size

        time.sleep(poll_interval)  # sondeo de sistema de archivos, no DOM

    logger.warning(
        "[PDF VALIDATOR] Timeout (%ds) esperando PDF en: %s",
        timeout,
        dir_path,
    )
    return None


def save_pdf_from_base64(b64_data: str, dest_path) -> Optional[Path]:
    """
    Decodifica base64 y guarda el resultado como archivo PDF.

    Útil cuando el portal embebe el PDF como data URI y el render visual
    no está disponible en el navegador automatizado.

    Args:
        b64_data:  String base64 del PDF. Puede incluir el prefijo de
                   data URI: ``data:application/pdf;base64,``.
        dest_path: Ruta destino para guardar el archivo (str o Path).

    Returns:
        ``Path`` al archivo guardado, o ``None`` si falló la decodificación
        o la escritura.
    """
    try:
        # Limpiar prefijo de data URI si está presente
        if "," in b64_data:
            b64_data = b64_data.split(",", 1)[1]

        raw: bytes = base64.b64decode(b64_data)

        if not raw.startswith(_PDF_MAGIC):
            logger.warning(
                "[PDF VALIDATOR] El contenido base64 decodificado no empieza "
                "con %%PDF-. Header: %r",
                raw[:8],
            )

        path = Path(dest_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

        logger.info(
            "[PDF VALIDATOR] PDF guardado desde base64: %s (%d bytes)",
            path.name,
            len(raw),
        )
        return path

    except Exception as exc:
        logger.exception(
            "[PDF VALIDATOR] Error guardando base64 como PDF en %s: %s",
            dest_path,
            exc,
        )
        return None
