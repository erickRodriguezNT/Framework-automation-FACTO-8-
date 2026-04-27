"""
validation_flow.py - Flujo de validaciones comunes del framework FACTO.

Centraliza validaciones reutilizables que se aplican después de
completar un flujo funcional:
- Validar UUID CFDI generado
- Validar que los archivos descargados existen y no están vacíos
- Validar que el portal muestra estado de éxito

Uso:
    from app.flows.common.validation_flow import ValidationFlow
    flow = ValidationFlow(driver, execution_context)
    result = flow.run(validar_uuid=True, validar_archivos=["pdf", "xml"])
"""
from pathlib import Path

from app.core.base_flow import BaseFlow
from app.utils.logger import get_logger
from app.utils.validations import (
    assert_not_empty,
    assert_valid_uuid_cfdi,
    is_valid_uuid_cfdi,
)

logger = get_logger(__name__)


class ValidationFlow(BaseFlow):
    """
    Flow de validaciones post-ejecución para cualquier flujo CFDI.

    Verifica los resultados almacenados en el execution_context
    para confirmar que el flujo fue completado correctamente.
    """

    def run(self, **kwargs) -> dict:
        """
        Ejecuta las validaciones configuradas.

        Args:
            validar_uuid:    (bool) Validar que el UUID CFDI en el contexto sea válido.
            validar_archivos:(list) Lista de tipos de archivo a validar (['pdf', 'xml']).
            uuid_key:        (str)  Clave del UUID en datos_dinamicos. Default: 'uuid_cfdi'.

        Returns:
            Resultado del flow con lista de validaciones ejecutadas.
        """
        self._registrar_inicio()

        validar_uuid     = kwargs.get("validar_uuid", True)
        validar_archivos = kwargs.get("validar_archivos", [])
        uuid_key         = kwargs.get("uuid_key", "uuid_cfdi")

        errores = []

        # --- Validación de UUID CFDI ---
        if validar_uuid:
            uuid_value = self.context.get_dato(uuid_key, "")
            try:
                assert_not_empty(uuid_value, uuid_key)
                assert_valid_uuid_cfdi(uuid_value)
                self._registrar_paso("validar_uuid_cfdi", "exitoso", f"UUID: {uuid_value}")
                logger.info(f"UUID CFDI válido: {uuid_value}")
            except Exception as exc:
                errores.append(str(exc))
                self._registrar_paso("validar_uuid_cfdi", "fallido", str(exc))
                logger.error(f"UUID CFDI inválido: {exc}")

        # --- Validación de archivos descargados ---
        for tipo in validar_archivos:
            archivo_path = self.context.archivos_generados.get(tipo)
            try:
                if archivo_path is None:
                    raise FileNotFoundError(f"No se registró archivo de tipo '{tipo}' en el contexto.")
                path = Path(archivo_path)
                if not path.exists():
                    raise FileNotFoundError(f"Archivo {tipo.upper()} no existe: {path}")
                if path.stat().st_size == 0:
                    raise ValueError(f"Archivo {tipo.upper()} está vacío: {path}")

                self._registrar_paso(f"validar_archivo_{tipo}", "exitoso", str(path))
                logger.info(f"Archivo {tipo.upper()} válido: {path}")

            except Exception as exc:
                errores.append(str(exc))
                self._registrar_paso(f"validar_archivo_{tipo}", "fallido", str(exc))
                logger.error(f"Validación de archivo {tipo.upper()} falló: {exc}")

        # --- Resultado final ---
        if errores:
            return self._marcar_fallido(f"Validaciones fallidas: {'; '.join(errores)}")

        return self._marcar_exitoso()
