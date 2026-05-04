# language: es
# encoding: UTF-8
# tests/features/ppd.feature

@ppd
Característica: Generación manual de CFDI PPD

  @ppd
  Escenario: Ejecutar CFDI PPD desde Excel
    Dado que existen casos PPD cargados desde Excel
    Cuando ejecuto el flujo PPD para cada caso marcado como ejecutable
    Entonces cada caso PPD debe generar su resultado esperado
    Y se deben guardar evidencias por caso PPD ejecutado
