# language: es
# encoding: UTF-8
# tests/features/nota_credito.feature
# Escenarios de prueba para el flujo de emisión de Nota de Crédito (CFDI tipo E - Egreso)

Característica: Emisión de Nota de Crédito en el portal FACTO 8
  Como usuario del portal FACTO 8
  Quiero emitir una Nota de Crédito (CFDI tipo Egreso)
  Para registrar descuentos, devoluciones o bonificaciones sobre una factura emitida

  Antecedentes:
    Dado que el usuario está autenticado en el portal FACTO 8
    Y existe una factura previamente timbrada con UUID válido en el sistema

  @smoke @nota_credito
  Escenario: Emitir nota de crédito relacionada a una factura válida
    Dado que el usuario navega al módulo de Nota de Crédito
    Cuando el usuario captura el UUID de la factura relacionada
    Y el usuario selecciona el tipo de relación "01 - Nota de crédito de los documentos relacionados"
    Y el usuario captura los datos del receptor y el motivo de la nota
    Y el usuario captura el importe de la nota de crédito
    Entonces el portal timbra la nota de crédito exitosamente
    Y el portal muestra un UUID CFDI de nota de crédito válido
    Y el usuario puede descargar el PDF de la nota de crédito
    Y el usuario puede descargar el XML de la nota de crédito

  @regression @nota_credito
  Escenario: Verificar error al relacionar nota de crédito con UUID inexistente
    Dado que el usuario navega al módulo de Nota de Crédito
    Cuando el usuario captura un UUID de factura que no existe en el sistema
    Entonces el portal muestra un mensaje de error de documento no encontrado

  @regression @nota_credito
  Escenario: Emitir nota de crédito por devolución parcial
    Dado que el usuario navega al módulo de Nota de Crédito
    Cuando el usuario captura el UUID de la factura relacionada
    Y el usuario selecciona el tipo de relación "01 - Nota de crédito de los documentos relacionados"
    Y el usuario captura un importe parcial de la factura original
    Entonces el portal timbra la nota de crédito exitosamente
    Y el importe de la nota de crédito es menor al total de la factura relacionada
