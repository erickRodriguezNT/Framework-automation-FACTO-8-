"""
xml_service.py - Servicio de procesamiento de archivos XML (CFDI).

Usa lxml para parsear, validar y extraer datos de los XMLs
descargados del portal FACTO.

Uso:
    from app.services.xml_service import XMLService
    service = XMLService()
    uuid = service.extraer_uuid(Path("outputs/xml/factura.xml"))
    datos = service.extraer_datos_cfdi(Path("outputs/xml/factura.xml"))
"""
from pathlib import Path

from lxml import etree

from app.utils.exceptions import ValidationError
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Namespaces del SAT para CFDI 4.0
CFDI_NS = {
    "cfdi": "http://www.sat.gob.mx/cfd/4",
    "tfd":  "http://www.sat.gob.mx/TimbreFiscalDigital",
    "pago20": "http://www.sat.gob.mx/Pagos20",
}


class XMLService:
    """
    Servicio de parsing y validación de XMLs CFDI descargados del portal FACTO.
    """

    def parse(self, xml_path: Path) -> etree._Element:
        """
        Parsea un archivo XML y retorna el elemento raíz.

        Args:
            xml_path: Ruta al archivo XML.

        Returns:
            Elemento raíz del árbol XML.

        Raises:
            ValidationError: Si el archivo no existe o tiene XML malformado.
        """
        if not xml_path.exists():
            raise ValidationError(f"Archivo XML no encontrado: {xml_path}")

        try:
            tree = etree.parse(str(xml_path))
            return tree.getroot()
        except etree.XMLSyntaxError as exc:
            raise ValidationError(f"XML malformado en {xml_path}: {exc}") from exc

    def extraer_uuid(self, xml_path: Path) -> str:
        """
        Extrae el UUID (folio fiscal) del nodo TimbreFiscalDigital.

        Args:
            xml_path: Ruta al archivo XML del CFDI.

        Returns:
            UUID del CFDI como string.

        Raises:
            ValidationError: Si no se encuentra el nodo de timbre.
        """
        root = self.parse(xml_path)
        nodo_tfd = root.find(".//tfd:TimbreFiscalDigital", CFDI_NS)

        if nodo_tfd is None:
            raise ValidationError(
                f"No se encontró TimbreFiscalDigital en {xml_path}. "
                f"Verificar que el CFDI está timbrado."
            )

        uuid = nodo_tfd.get("UUID", "")
        if not uuid:
            raise ValidationError(f"Atributo UUID vacío en TimbreFiscalDigital de {xml_path}")

        logger.debug(f"UUID extraído de {xml_path.name}: {uuid}")
        return uuid

    def extraer_datos_cfdi(self, xml_path: Path) -> dict:
        """
        Extrae los datos principales del CFDI (cabecera + timbre).

        Returns:
            Diccionario con: uuid, fecha, total, emisor_rfc, receptor_rfc,
            tipo_comprobante, folio, serie, version.
        """
        root = self.parse(xml_path)
        nodo_tfd = root.find(".//tfd:TimbreFiscalDigital", CFDI_NS)

        datos = {
            "uuid":              nodo_tfd.get("UUID", "") if nodo_tfd is not None else "",
            "version":           root.get("Version", ""),
            "tipo_comprobante":  root.get("TipoDeComprobante", ""),
            "fecha":             root.get("Fecha", ""),
            "folio":             root.get("Folio", ""),
            "serie":             root.get("Serie", ""),
            "total":             root.get("Total", ""),
            "subtotal":          root.get("SubTotal", ""),
            "metodo_pago":       root.get("MetodoPago", ""),
            "forma_pago":        root.get("FormaPago", ""),
            "moneda":            root.get("Moneda", "MXN"),
        }

        # Emisor
        emisor = root.find("cfdi:Emisor", CFDI_NS)
        if emisor is not None:
            datos["emisor_rfc"]    = emisor.get("Rfc", "")
            datos["emisor_nombre"] = emisor.get("Nombre", "")

        # Receptor
        receptor = root.find("cfdi:Receptor", CFDI_NS)
        if receptor is not None:
            datos["receptor_rfc"]    = receptor.get("Rfc", "")
            datos["receptor_nombre"] = receptor.get("Nombre", "")
            datos["uso_cfdi"]        = receptor.get("UsoCFDI", "")

        return datos

    def validate_schema(self, xml_path: Path, xsd_path: Path) -> bool:
        """
        Valida un XML contra un schema XSD del SAT.

        TODO: Descargar XSDs del SAT y colocarlos en docs/xsd/

        Args:
            xml_path: Ruta al XML a validar.
            xsd_path: Ruta al archivo XSD.

        Returns:
            True si el XML es válido contra el schema.
        """
        if not xsd_path.exists():
            logger.warning(f"XSD no encontrado: {xsd_path}. Validación de schema omitida.")
            return True

        schema_doc = etree.parse(str(xsd_path))
        schema = etree.XMLSchema(schema_doc)
        tree = etree.parse(str(xml_path))
        is_valid = schema.validate(tree)

        if not is_valid:
            logger.warning(f"XML {xml_path.name} no válido contra XSD: {schema.error_log}")

        return is_valid
