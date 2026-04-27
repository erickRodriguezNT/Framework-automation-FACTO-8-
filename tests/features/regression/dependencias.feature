# language: es
# encoding: UTF-8
# tests/features/regression/dependencias.feature

Característica: Verificación de dependencias entre flujos — FACTO 8
  Como equipo de QA
  Quiero verificar que el sistema maneja correctamente las dependencias entre flujos
  Para asegurar que un flujo no se ejecuta sin sus prerequisitos

  @dependencias
  Escenario: Complemento de Pago requiere PPD previo
    Dado que el usuario está autenticado en el portal FACTO 8
    Cuando el sistema intenta ejecutar el flujo de Complemento de Pago sin un PPD previo
    Entonces el sistema lanza un error de dependencia indicando que se requiere un CFDI PPD

  @dependencias
  Escenario: Nota de Crédito requiere Factura previa
    Dado que el usuario está autenticado en el portal FACTO 8
    Cuando el sistema intenta ejecutar el flujo de Nota de Crédito sin una factura previa
    Entonces el sistema lanza un error de dependencia indicando que se requiere un CFDI de ingreso

  @dependencias
  Escenario: Datos del PPD se propagan al contexto para Complemento de Pago
    Dado que el usuario está autenticado en el portal FACTO 8
    Cuando el usuario emite una factura PPD exitosamente
    Entonces el UUID del PPD está disponible en el contexto de ejecución
    Y el flujo de Complemento de Pago puede acceder al UUID del PPD automáticamente
