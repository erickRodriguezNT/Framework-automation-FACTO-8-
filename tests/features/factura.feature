# language: es
# tests/features/factura.feature
# Escenarios de prueba para Factura CFDI 4.0

Característica: Generación manual de Factura CFDI 4.0
  Como usuario del portal FACTO 8
  Quiero generar Facturas de forma manual
  Para timbrar comprobantes fiscales válidos ante el SAT

  @smoke @factura
  Escenario: Ejecutar facturas manuales desde Excel
    Dado que existen casos de factura cargados desde Excel
    Cuando ejecuto el flujo manual de factura para cada caso marcado como ejecutable
    Entonces cada caso debe generar su resultado esperado
    Y se deben guardar evidencias por caso ejecutado
