#!/bin/bash
# =============================================================================
# entrypoint.sh - Punto de entrada del contenedor de automatización FACTO 8
# =============================================================================
# Inicia Xvfb (display virtual) y luego ejecuta los tests via run.py.
# Las variables de entorno se pasan desde Cloud Run o docker run -e.
# =============================================================================

set -euo pipefail

echo "=== Auto FACTO 8 - Iniciando Ejecución ==="
echo "Timestamp: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "Ambiente: ${ENVIRONMENT:-staging}"
echo "Suite: ${TEST_SUITE:-smoke}"

# ---------------------------------------------------------------------------
# Iniciar display virtual (Xvfb) para Chrome headless alternativo
# ---------------------------------------------------------------------------
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
sleep 1
echo "Xvfb iniciado en DISPLAY=:99"

# ---------------------------------------------------------------------------
# Verificar Chrome disponible
# ---------------------------------------------------------------------------
CHROME_VERSION=$(google-chrome --version 2>&1 || echo "No disponible")
echo "Chrome: $CHROME_VERSION"

# ---------------------------------------------------------------------------
# Construir comando pytest según la suite solicitada
# ---------------------------------------------------------------------------
SUITE="${TEST_SUITE:-smoke}"
HEADLESS_FLAG="${HEADLESS:-true}"

case "$SUITE" in
  smoke)
    PYTEST_ARGS="-m smoke"
    ;;
  factura)
    PYTEST_ARGS="tests/features/factura.feature"
    ;;
  nota_credito)
    PYTEST_ARGS="tests/features/nota_credito.feature"
    ;;
  ppd)
    PYTEST_ARGS="tests/features/ppd.feature"
    ;;
  complemento_pago)
    PYTEST_ARGS="tests/features/complemento_pago.feature"
    ;;
  adenda)
    PYTEST_ARGS="tests/features/adenda.feature"
    ;;
  end_to_end)
    PYTEST_ARGS="-m end_to_end"
    ;;
  all)
    PYTEST_ARGS="tests/features/"
    ;;
  *)
    echo "ADVERTENCIA: Suite '$SUITE' desconocida. Ejecutando smoke por defecto."
    PYTEST_ARGS="-m smoke"
    ;;
esac

echo "Ejecutando suite: $SUITE"
echo "Args pytest: $PYTEST_ARGS"

# ---------------------------------------------------------------------------
# Ejecutar tests
# ---------------------------------------------------------------------------
python -m pytest \
  $PYTEST_ARGS \
  --tb=short \
  -v \
  --alluredir=allure-results \
  --headless \
  ; EXIT_CODE=$?

echo "=== Ejecución finalizada con código: $EXIT_CODE ==="

# ---------------------------------------------------------------------------
# Copiar resultados a bucket GCS si está configurado
# ---------------------------------------------------------------------------
if [ -n "${GCS_BUCKET:-}" ]; then
  echo "Copiando resultados a gs://${GCS_BUCKET}/allure-results/..."
  gsutil -m cp -r allure-results/ "gs://${GCS_BUCKET}/allure-results/" || true
  gsutil -m cp -r outputs/ "gs://${GCS_BUCKET}/outputs/" || true
  echo "Resultados copiados."
fi

exit $EXIT_CODE
