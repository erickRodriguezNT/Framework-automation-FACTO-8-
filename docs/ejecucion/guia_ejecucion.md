# Guía de Ejecución — Auto FACTO 8

## Requisitos Previos

- Python 3.11+
- Google Chrome instalado
- Variables de entorno configuradas (ver `.env.example`)

---

## Instalación

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd automation_framework

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
copy .env.example .env
# Editar .env con las credenciales reales del portal FACTO 8
```

---

## Ejecución Local

### Suite Completa
```bash
python run.py
```

### Por Módulo (Runners)
```bash
python tests/runners/run_factura.py
python tests/runners/run_nota_credito.py
python tests/runners/run_ppd.py
python tests/runners/run_complemento_pago.py
python tests/runners/run_smoke.py
python tests/runners/run_end_to_end.py
```

### Modo Headless
```bash
python tests/runners/run_factura.py --headless
```

### Por Feature File (directo con pytest)
```bash
python -m pytest tests/features/factura.feature -v
python -m pytest tests/features/nota_credito.feature -v
python -m pytest -m smoke -v
python -m pytest -m end_to_end -v
```

---

## Ejecución con Docker

### Build
```bash
docker build -f docker/Dockerfile -t facto8-automation .
```

### Run (smoke)
```bash
docker run --rm \
  --env-file .env \
  -e TEST_SUITE=smoke \
  -v $(pwd)/outputs:/app/outputs \
  -v $(pwd)/allure-results:/app/allure-results \
  facto8-automation
```

### Run (suite específica)
```bash
docker run --rm \
  --env-file .env \
  -e TEST_SUITE=factura \
  facto8-automation
```

---

## Reporte Allure

```bash
# Generar reporte HTML
allure serve allure-results

# O generar y abrir
allure generate allure-results -o allure-report --clean
allure open allure-report
```

---

## Variables de Entorno Clave

| Variable              | Descripción                          | Ejemplo                        |
|-----------------------|--------------------------------------|--------------------------------|
| `FACTO_URL`           | URL del portal FACTO 8               | `https://facto8.ejemplo.com`   |
| `FACTO_USER`          | Usuario de acceso                    | `usuario@empresa.com`          |
| `FACTO_PASSWORD`      | Contraseña                           | `***`                          |
| `ENVIRONMENT`         | Ambiente activo                      | `staging` / `prod`             |
| `HEADLESS`            | Ejecutar Chrome sin UI               | `true` / `false`               |
| `TEST_SUITE`          | Suite a ejecutar en Docker           | `smoke` / `factura` / `all`    |
| `OUTPUT_DIR`          | Directorio base de salidas           | `outputs`                      |

---

## Estructura de Salidas

```
outputs/
├── screenshots/      Capturas de pantalla (fallos + evidencia)
│   └── failures/     Screenshots automáticos de tests fallidos
├── pdf/              PDFs descargados + reportes de ejecución
├── xml/              CFDIs descargados
├── logs/             Logs de ejecución (rotación diaria)
├── json/             Reportes JSON de cada ejecución
└── zip/              Paquetes de evidencia completos

allure-results/       Datos crudos para Allure (auto-generado)
allure-report/        HTML del reporte (si se genera con `allure generate`)
```

---

## Agregar Nuevos Tests

1. Crear escenario en el feature file correspondiente (`tests/features/`)
2. Implementar step en `tests/step_definitions/step_MODULO.py`
3. Si requiere nuevo flujo: agregar en `app/flows/MODULO/nuevo_flow.py`
4. Registrar en `FlowRegistry` (`app/flows/orchestrator/flow_registry.py`)
5. Si hay pre-requisito: agregar en `DependencyResolver` y `DependencyService`
6. Agregar datos de prueba en `tests/test_data/MODULO/`

---

## Troubleshooting

| Problema                           | Solución                                                      |
|------------------------------------|---------------------------------------------------------------|
| `ChromeDriver not found`           | webdriver-manager lo instala automáticamente al primer run    |
| `SessionNotCreatedException`       | Versión Chrome incompatible — actualizar Chrome               |
| `FlowDependencyError`              | Falta un pre-requisito en el contexto (ej: uuid_cfdi_ppd)     |
| `ConfigurationError: archivo no encontrado` | Verificar ruta en `tests/test_data/`                |
| Tests fallan en CI                 | Asegurarse que `HEADLESS=true` en las variables de entorno    |
