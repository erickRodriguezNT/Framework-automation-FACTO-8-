# FACTO 8 Automation Framework

Framework de automatización de pruebas web para el sistema de facturación electrónica **FACTO 8**, construido con Python 3.11+, Selenium WebDriver, Pytest y pytest-bdd.

---

## Índice

1. [Propósito](#propósito)
2. [Arquitectura de capas](#arquitectura-de-capas)
3. [Estructura del proyecto](#estructura-del-proyecto)
4. [Requisitos previos](#requisitos-previos)
5. [Configuración inicial](#configuración-inicial)
6. [Ejecución local](#ejecución-local)
7. [Ejecución con Docker](#ejecución-con-docker)
8. [Outputs generados](#outputs-generados)
9. [Agregar un nuevo flujo](#agregar-un-nuevo-flujo)
10. [Convenciones del proyecto](#convenciones-del-proyecto)

---

## Propósito

Automatizar los flujos web críticos de facturación electrónica del portal FACTO 8:

| Flujo               | Estado       |
|---------------------|--------------|
| Factura             | Estructura base lista |
| Nota de Crédito     | Estructura base lista |
| PPD                 | Estructura base lista |
| Complemento de Pago | Estructura base lista |
| Adenda              | Estructura base lista |
| Cancelaciones       | Pendiente de implementación |

---

## Arquitectura de capas

```
┌─────────────────────────────────────────────────┐
│                   TESTS (pytest-bdd)             │
│  features/ → step_definitions/ → hooks/          │
└─────────────────────┬───────────────────────────┘
                      │ llaman
┌─────────────────────▼───────────────────────────┐
│                   FLOWS (app/flows/)             │
│  Lógica de negocio completa por proceso          │
│  LoginFlow, FacturaFlow, PPDFlow, ...            │
└─────────────────────┬───────────────────────────┘
                      │ usan
┌─────────────────────▼───────────────────────────┐
│                   PAGES (app/pages/)             │
│  Page Objects: selectores + acciones UI          │
│  LoginPage, FacturaPage, ResultadoPage, ...      │
└─────────────────────┬───────────────────────────┘
                      │ usan
┌─────────────────────▼───────────────────────────┐
│                   CORE (app/core/)               │
│  BasePage, BaseFlow, ExecutionContext            │
└─────────────────────────────────────────────────┘
```

### Regla principal
- **Pages** = pantallas del portal. Solo selectores y acciones atómicas.
- **Flows** = operaciones de negocio. Coordinan múltiples páginas.
- **Steps** = únicamente llaman a Flows. Sin Selenium directo.

---

## Estructura del proyecto

```
automation_framework/
│
├── app/
│   ├── core/             # BasePage, BaseFlow, ExecutionContext
│   ├── config/           # Settings, paths, browser config, entornos
│   ├── drivers/          # DriverFactory, ChromeOptions
│   ├── pages/            # Page Objects por módulo
│   │   ├── common/       # Login, Home, Menu, Modal, Loader, Download
│   │   ├── factura/
│   │   ├── nota_credito/
│   │   ├── ppd/
│   │   ├── complemento_pago/
│   │   └── adenda/
│   ├── flows/            # Lógica de negocio por módulo
│   │   ├── common/       # Login, Navigation, Download, Validation
│   │   ├── factura/
│   │   ├── nota_credito/
│   │   ├── ppd/
│   │   ├── complemento_pago/
│   │   ├── adenda/
│   │   └── orchestrator/ # FlowRegistry, DependencyResolver
│   ├── services/         # XML, PDF, ZIP, Data, Report services
│   ├── utils/            # Logger, Waits, Dates, Strings, Retry
│   ├── evidence/         # Screenshots, EvidenceCollector
│   └── reporting/        # PDF, XML, JSON, ZIP reports
│
├── tests/
│   ├── features/         # Archivos .feature en Gherkin/Español
│   │   └── regression/   # smoke, end_to_end, dependencias
│   ├── step_definitions/ # Implementación de steps (solo llaman flows)
│   ├── hooks/            # Setup/teardown por escenario
│   ├── runners/          # Scripts de ejecución por flujo/suite
│   └── test_data/        # JSONs de datos de prueba
│
├── outputs/              # Generado en ejecución (ignorado por git)
│   ├── screenshots/
│   ├── pdf/
│   ├── xml/
│   ├── logs/
│   ├── json/
│   └── zip/
│
├── docker/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── cloudrun.env.example
│
├── docs/
│   ├── arquitectura/
│   ├── flujos/
│   ├── ejecucion/
│   └── presentacion/
│
├── requirements.txt
├── pytest.ini
├── conftest.py
├── .env.example
├── .gitignore
└── run.py
```

---

## Requisitos previos

- Python 3.11+
- Google Chrome (última versión estable)
- pip

Para Docker:
- Docker Engine 24+

---

## Configuración inicial

```bash
# 1. Clonar el repositorio
git clone <url-del-repo>
cd automation_framework

# 2. Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
copy .env.example .env          # Windows
# cp .env.example .env          # macOS/Linux
# Editar .env con los valores reales (BASE_URL, USERNAME, PASSWORD, etc.)
```

---

## Ejecución local

### Por flujo individual

```bash
python run.py --flow factura
python run.py --flow nota_credito
python run.py --flow ppd
python run.py --flow complemento_pago
python run.py --flow adenda
```

### Por suite

```bash
python run.py --suite smoke          # Tests de humo rápidos
python run.py --suite regression     # Regresión completa
python run.py --suite full           # Toda la suite sin filtro
```

### Opciones adicionales

```bash
python run.py --flow factura --headless   # Modo headless (sin ventana)
python run.py --suite smoke --dry-run     # Solo recolectar (no ejecutar)
python run.py --suite regression -q      # Modo silencioso
```

### Por feature file directamente

```bash
python run.py --feature tests/features/factura.feature
pytest tests/features/factura.feature -v
```

### Ver reporte Allure

```bash
allure serve allure-results
```

---

## Ejecución con Docker

```bash
# Construir imagen
docker build -f docker/Dockerfile -t facto8-automation .

# Ejecutar suite smoke en headless
docker run --rm \
  --env-file .env \
  -e HEADLESS=true \
  -v $(pwd)/outputs:/app/outputs \
  -v $(pwd)/allure-results:/app/allure-results \
  facto8-automation --suite smoke

# Ejecutar flujo específico
docker run --rm \
  --env-file .env \
  -e HEADLESS=true \
  facto8-automation --flow factura
```

---

## Outputs generados

Todos los outputs se guardan en `outputs/` organizados por ejecución:

| Directorio           | Contenido                              |
|----------------------|----------------------------------------|
| `outputs/screenshots/` | Capturas por escenario/paso          |
| `outputs/pdf/`       | Reportes PDF ejecutivos               |
| `outputs/xml/`       | Reportes XML técnicos                 |
| `outputs/json/`      | Resultados en formato JSON            |
| `outputs/logs/`      | Logs de ejecución con rotación diaria |
| `outputs/zip/`       | ZIP consolidado de evidencias         |
| `allure-results/`    | Datos para dashboard Allure           |

---

## Agregar un nuevo flujo

1. **Crear el Page Object** en `app/pages/{nuevo_flujo}/{nuevo_flujo}_page.py`
2. **Crear el Flow** en `app/flows/{nuevo_flujo}/{nuevo_flujo}_flow.py` heredando de `BaseFlow`
3. **Registrar el flow** en `app/flows/orchestrator/flow_registry.py`
4. **Definir dependencias** en `app/flows/orchestrator/dependency_resolver.py` si aplica
5. **Crear feature file** en `tests/features/{nuevo_flujo}.feature`
6. **Crear step definitions** en `tests/step_definitions/{nuevo_flujo}_steps.py`
7. **Agregar test data** en `tests/test_data/{nuevo_flujo}/{nuevo_flujo}_valido.json`
8. **Agregar runner** en `tests/runners/run_{nuevo_flujo}.py`
9. **Agregar marker** en `pytest.ini`

---

## Convenciones del proyecto

- Nombres de archivos y variables: `snake_case`
- Nombres de clases: `PascalCase`
- Sin credenciales hardcodeadas — usar siempre variables de entorno
- Sin Selenium directo en steps o en lógica de negocio de pages
- Sin lógica de negocio compleja en Page Objects
- Selectores priorizados: `id > name > data-testid > data-cy > aria-label > CSS estable`
- Evitar: XPath absoluto, selectores por posición, texto dinámico
- Cada módulo tiene su `__init__.py`
- TODOs documentados donde faltan selectores o implementaciones reales
