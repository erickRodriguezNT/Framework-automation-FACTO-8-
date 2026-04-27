# language: es
# encoding: UTF-8
# tests/features/ppd.feature
# Escenarios de prueba para el flujo de Factura con método de pago PPD

Característica: Emisión de Factura PPD en el portal FACTO 8
  Como usuario del portal FACTO 8
  Quiero emitir una Factura con método de pago PPD
  Para registrar ventas que serán pagadas en fecha posterior o en parcialidades

  Antecedentes:
    Dado que el usuario está autenticado en el portal FACTO 8

  @smoke @ppd
  Escenario: Emitir factura con método de pago PPD exitosamente
    Dado que el usuario navega al módulo de Factura PPD
    Cuando el usuario captura los datos del receptor con RFC válido
    Y el usuario selecciona el método de pago "PPD - Pago en parcialidades o diferido"
    Y el usuario selecciona la forma de pago "99 - Por definir"
    Y el usuario captura los datos del concepto y el importe
    Entonces el portal timbra la factura PPD exitosamente
    Y el portal muestra un UUID CFDI de PPD válido
    Y el UUID del PPD queda disponible para el flujo de Complemento de Pago

  @regression @ppd
  Escenario: Verificar que la factura PPD queda en estado pendiente de pago
    Dado que el usuario navega al módulo de Factura PPD
    Cuando el usuario emite una factura con método de pago PPD
    Entonces el portal timbra la factura PPD exitosamente
    Y el portal muestra el estado del CFDI como pendiente de pago

  @regression @ppd
  Escenario: Descargar archivos de factura PPD timbrada
    Dado que el usuario navega al módulo de Factura PPD
    Cuando el usuario emite una factura con método de pago PPD
    Entonces el portal timbra la factura PPD exitosamente
    Y el usuario puede descargar el PDF de la factura PPD
    Y el usuario puede descargar el XML de la factura PPD
