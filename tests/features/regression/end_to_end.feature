# language: es
# encoding: UTF-8
# tests/features/regression/end_to_end.feature

Característica: Flujo End-to-End completo — FACTO 8
  Como equipo de QA
  Quiero ejecutar el flujo completo de facturación
  Para verificar que todos los módulos del portal funcionan en conjunto

  @end_to_end
  Escenario: Flujo completo PPD → Complemento de Pago
    Dado que el usuario está autenticado en el portal FACTO 8
    Cuando el usuario emite una factura con método de pago PPD
    Entonces el portal timbra la factura PPD exitosamente
    Cuando el usuario navega al módulo de Complemento de Pago
    Y el usuario relaciona la factura PPD recién emitida
    Y el usuario captura los datos del pago recibido
    Entonces el portal timbra el complemento de pago exitosamente
    Y el complemento de pago queda relacionado con la factura PPD

  @end_to_end
  Escenario: Flujo completo Factura → Nota de Crédito
    Dado que el usuario está autenticado en el portal FACTO 8
    Cuando el usuario emite una factura de ingreso con datos válidos
    Entonces el portal timbra la factura exitosamente
    Cuando el usuario navega al módulo de Nota de Crédito
    Y el usuario relaciona la factura recién emitida
    Y el usuario captura los datos de la nota de crédito
    Entonces el portal timbra la nota de crédito exitosamente
    Y la nota de crédito queda relacionada con la factura de ingreso
