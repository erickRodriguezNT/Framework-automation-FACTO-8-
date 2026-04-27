# Arquitectura del Framework de Automatización — Auto FACTO 8

## Visión General

El framework es una arquitectura en capas que separa responsabilidades de forma estricta:

```
tests/step_definitions/   ← BDD (pytest-bdd) — SOLO llaman flows
app/flows/                ← Lógica de negocio — coordinan páginas
app/pages/                ← UI Selenium — SOLO localizadores + acciones atómicas
app/services/             ← Servicios transversales (PDF, XML, Data, ZIP)
app/core/                 ← Base classes + ExecutionContext
app/config/               ← Settings, paths, browser config
app/drivers/              ← DriverFactory + ChromeOptions
app/evidence/             ← Screenshots + empaquetado de evidencia
app/reporting/            ← Builders JSON, XML, PDF, ZIP
```

---

## Capas y Responsabilidades

### 1. Pages (`app/pages/`)
- **Responsabilidad única**: Localizadores CSS + acciones atómicas de UI.
- **Prohibido**: lógica de negocio, assert de dominio, llamadas a otros pages.
- **Hereda**: `BasePage` (webdriver_wait helpers, click, fill, is_visible).
- **Selector priority**: `[data-testid='x'] > #id > input[name='x'] > CSS-stable`. Nunca XPath.

### 2. Flows (`app/flows/`)
- **Responsabilidad única**: Orquestar páginas para ejecutar un caso de uso completo.
- **Recibe**: `ExecutionContext` + `test_data: dict`.
- **Devuelve**: `{"estado": "exitoso|fallido", "error": None|str, ...}`.
- **Escribe**: en `execution_context.datos_dinamicos` (uuid_cfdi, uuid_cfdi_ppd, etc.)

### 3. Steps (`tests/step_definitions/`)
- **Responsabilidad única**: Traducir BDD → llamadas a flows. Nada más.
- **Prohibido**: instanciar Pages, usar `driver` directamente, lógica de negocio.

### 4. ExecutionContext (`app/core/execution_context.py`)
- Objeto compartido por la duración de un escenario.
- Almacena: `execution_id`, `datos_dinamicos`, `archivos_generados`, `pasos_ejecutados`, `estado`.
- Creado en `conftest.py` como fixture de scope `function`.

### 5. Orchestrator (`app/flows/orchestrator/`)
- `FlowRegistry`: carga flows por nombre via importlib.
- `DependencyResolver`: valida pre-requisitos antes de ejecutar un flow.
- `ExecutionOrchestrator`: ejecuta flows individuales o secuencias.

---

## Mapa de Dependencias entre Flujos

```
login_flow
    └── navigation_flow
            ├── factura_flow
            │       ├── factura_timbrado_flow
            │       └── factura_descarga_flow
            ├── nota_credito_flow         ← requiere uuid_factura_relacionada
            │       └── nota_credito_relacion_flow
            ├── ppd_flow
            │       └── ppd_validacion_flow
            ├── complemento_pago_flow     ← requiere uuid_cfdi_ppd
            │       ├── complemento_pago_relacion_ppd_flow
            │       └── complemento_pago_validacion_flow
            └── adenda_flow               ← requiere uuid_cfdi_base
                    └── adenda_validacion_flow
```

---

## Tecnologías

| Librería              | Versión   | Uso                          |
|-----------------------|-----------|------------------------------|
| Python                | 3.11+     | Lenguaje base                |
| Selenium              | 4.20.0    | UI automation                |
| webdriver-manager     | 4.0.1     | ChromeDriver auto-install    |
| pytest                | 8.2.0     | Test runner                  |
| pytest-bdd            | 7.2.0     | BDD (Gherkin)                |
| allure-pytest         | 2.13.5    | Reportes Allure              |
| reportlab             | 4.1.0     | Generación PDF               |
| loguru                | 0.7.2     | Logging estructurado         |
| tenacity              | 8.3.0     | Retry decorator              |
| lxml                  | 5.2.1     | Procesamiento XML/CFDI       |
| python-dotenv         | 1.0.1     | Variables de entorno         |

---

## Estructura de Directorios

```
automation_framework/
├── app/
│   ├── config/           settings, environment_config, browser_config, paths
│   ├── core/             base_page, base_flow, execution_context
│   ├── drivers/          driver_factory, chrome_options
│   ├── evidence/         evidence_collector, evidence_naming, screenshot_manager
│   ├── flows/            login, navigation, download, validation, factura,
│   │                     nota_credito, ppd, complemento_pago, adenda, orchestrator
│   ├── pages/            common, factura, nota_credito, ppd, complemento_pago, adenda
│   ├── reporting/        json, xml, pdf, zip builders + execution_summary
│   ├── services/         data, file, xml, pdf, zip, report, dependency
│   └── utils/            exceptions, logger, waits, validations, retry
├── docker/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── cloudrun.env.example
├── docs/
│   ├── arquitectura/
│   ├── ejecucion/
│   ├── flujos/
│   └── presentacion/
├── outputs/              screenshots, pdf, xml, logs, json, zip
├── tests/
│   ├── features/         factura, nota_credito, ppd, complemento_pago, adenda
│   │   └── regression/   smoke, end_to_end, dependencias
│   ├── hooks/
│   ├── runners/
│   ├── step_definitions/
│   └── test_data/
├── conftest.py
├── pytest.ini
├── requirements.txt
├── run.py
└── .env.example
```
