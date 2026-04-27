# language: es
# encoding: UTF-8
# tests/features/regression/smoke.feature

Característica: Suite de Smoke Test — FACTO 8
  Como equipo de QA
  Quiero ejecutar un smoke test rápido de todos los módulos
  Para verificar que el portal FACTO 8 está operativo al inicio de cada sprint

  @smoke
  Escenario: Verificar acceso al portal y login exitoso
    Dado que el portal FACTO 8 está disponible
    Cuando el usuario se autentica con credenciales válidas
    Entonces el usuario ve el dashboard principal del portal

  @smoke @factura
  Escenario: Smoke test — emisión de factura básica
    Dado que el usuario está autenticado en el portal FACTO 8
    Cuando el usuario navega al módulo de Factura
    Entonces el módulo de Factura carga correctamente

  @smoke @nota_credito
  Escenario: Smoke test — acceso al módulo de Nota de Crédito
    Dado que el usuario está autenticado en el portal FACTO 8
    Cuando el usuario navega al módulo de Nota de Crédito
    Entonces el módulo de Nota de Crédito carga correctamente

  @smoke @ppd
  Escenario: Smoke test — acceso al módulo de PPD
    Dado que el usuario está autenticado en el portal FACTO 8
    Cuando el usuario navega al módulo de Factura PPD
    Entonces el módulo PPD carga correctamente

  @smoke @complemento_pago
  Escenario: Smoke test — acceso al módulo de Complemento de Pago
    Dado que el usuario está autenticado en el portal FACTO 8
    Cuando el usuario navega al módulo de Complemento de Pago
    Entonces el módulo de Complemento de Pago carga correctamente
