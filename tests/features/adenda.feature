# language: es
# encoding: UTF-8
# tests/features/adenda.feature
# Escenarios de prueba para el flujo de Adenda

Característica: Agregar Adenda a CFDI en el portal FACTO 8
  Como usuario del portal FACTO 8
  Quiero agregar una Adenda a un CFDI ya emitido
  Para incluir información comercial adicional requerida por el receptor

  Antecedentes:
    Dado que el usuario está autenticado en el portal FACTO 8

  @smoke @adenda
  Escenario: Agregar adenda a una factura válida
    Dado que el usuario navega al módulo de Adenda
    Cuando el usuario captura el UUID del CFDI al que desea agregar la adenda
    Y el usuario captura los datos comerciales de la adenda
    Entonces el portal procesa y guarda la adenda exitosamente
    Y el portal confirma que la adenda fue agregada al CFDI

  @regression @adenda
  Escenario: Verificar que la adenda incluye referencia de orden de compra
    Dado que el usuario navega al módulo de Adenda
    Cuando el usuario captura el UUID del CFDI al que desea agregar la adenda
    Y el usuario captura la referencia de orden de compra en la adenda
    Entonces el portal procesa y guarda la adenda exitosamente
    Y la adenda contiene la referencia de orden de compra capturada

  @regression @adenda
  Escenario: Descargar CFDI con adenda
    Dado que el usuario navega al módulo de Adenda
    Cuando el usuario agrega una adenda a un CFDI válido
    Entonces el portal procesa y guarda la adenda exitosamente
    Y el usuario puede descargar el PDF del CFDI con la adenda incluida
    Y el usuario puede descargar el XML del CFDI con la adenda incluida
