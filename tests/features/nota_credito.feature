# language: es
# tests/features/nota_credito.feature

Característica: Flujo base de Nota de Crédito CFDI 4.0
  Como usuario del portal FACTO 8
  Quiero ejecutar el flujo base de Nota de Crédito
  Para validar que el módulo corre correctamente replicando el flujo de Factura Manual

  @smoke @nota_credito
  Escenario: Ejecutar notas de crédito desde Excel replicando flujo de factura manual
    Dado que existen casos de nota de crédito cargados desde Excel
    Cuando ejecuto el flujo base de nota de crédito para cada caso marcado como ejecutable
    Entonces cada caso debe generar su resultado esperado
    Y se deben guardar evidencias por caso ejecutado en outputs de nota de crédito
