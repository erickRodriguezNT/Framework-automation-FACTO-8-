# language: es
# encoding: UTF-8
# tests/features/complemento_pago.feature
# Escenarios de prueba para el flujo de Complemento de Pago (CFDI tipo P)

Característica: Emisión de Complemento de Pago en el portal FACTO 8
  Como usuario del portal FACTO 8
  Quiero emitir un Complemento de Pago (CFDI tipo P)
  Para registrar el pago recibido de una factura con método PPD

  Antecedentes:
    Dado que el usuario está autenticado en el portal FACTO 8
    Y existe una factura PPD previamente timbrada con UUID disponible en el contexto

  @smoke @complemento_pago
  Escenario: Emitir complemento de pago para una factura PPD válida
    Dado que el usuario navega al módulo de Complemento de Pago
    Cuando el usuario captura la fecha de pago
    Y el usuario selecciona la forma de pago "03 - Transferencia electrónica de fondos"
    Y el usuario captura el monto del pago y el número de operación
    Y el usuario relaciona el UUID del CFDI PPD pendiente de pago
    Y el usuario captura el número de parcialidad e importes del documento relacionado
    Entonces el portal timbra el complemento de pago exitosamente
    Y el portal muestra un UUID CFDI de complemento de pago válido
    Y el usuario puede descargar el PDF del complemento de pago
    Y el usuario puede descargar el XML del complemento de pago

  @regression @complemento_pago
  Escenario: Verificar error al relacionar UUID de PPD inexistente
    Dado que el usuario navega al módulo de Complemento de Pago
    Cuando el usuario captura los datos del pago
    Y el usuario intenta relacionar un UUID de PPD que no existe
    Entonces el portal muestra un mensaje de error de documento no encontrado

  @regression @complemento_pago
  Escenario: Emitir complemento de pago con pago total de la factura PPD
    Dado que el usuario navega al módulo de Complemento de Pago
    Cuando el usuario captura la fecha y datos del pago
    Y el usuario relaciona el UUID del PPD con saldo insoluto igual al total original
    Y el usuario captura el importe pagado igual al total de la factura
    Entonces el portal timbra el complemento de pago exitosamente
    Y el saldo insoluto del documento relacionado queda en cero
