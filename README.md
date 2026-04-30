# FACTO 8 Automation Framework

Framework de automatización de pruebas web para el sistema de facturación electrónica **FACTO 8**, construido con Python 3.13+, Selenium 4.20, Pytest y pytest-bdd.

---

## Índice

1. [Propósito](#propósito)
2. [Arquitectura de capas](#arquitectura-de-capas)
3. [Capa común de Page Objects](#capa-común-de-page-objects)
4. [Capa común de Flows](#capa-común-de-flows)
5. [Estructura del proyecto](#estructura-del-proyecto)
6. [Requisitos previos](#requisitos-previos)
7. [Configuración inicial](#configuración-inicial)
8. [Ejecución local](#ejecución-local)
9. [Ejecución con Docker](#ejecución-con-docker)
10. [Outputs generados](#outputs-generados)
11. [Agregar un nuevo flujo](#agregar-un-nuevo-flujo)
12. [Convenciones del proyecto](#convenciones-del-proyecto)

---

## Propósito

Automatizar los flujos web críticos de facturación electrónica del portal FACTO 8:

| Flujo               | Estado                        |
|---------------------|-------------------------------|
| Factura             | Implementado y validado        |
| Nota de Crédito     | Implementado y validado        |
| PPD                 | Estructura base lista          |
| Complemento de Pago | Estructura base lista          |
| Adenda              | Estructura base lista          |
| Cancelaciones       | Pendiente de implementación    |

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
│  LoginFlow, FacturaFlow, NotaCreditoFlow, ...    │
└─────────────────────┬───────────────────────────┘
                      │ usan
┌─────────────────────▼───────────────────────────┐
│               PAGES (app/pages/)                 │
│  ┌───────────────────────────────────────────┐   │
│  │  app/pages/common/  ← CAPA COMPARTIDA     │   │
│  │  CfdiEmisionPage, CfdiResultadoPage       │   │
│  │  LoginPage, HomePage, MenuPage, ...       │   │
│  └───────────────────────────────────────────┘   │
│  ┌──────────────────┐  ┌─────────────────────┐  │
│  │ pages/factura/   │  │ pages/nota_credito/ │  │
│  │ (thin subclasses)│  │ (thin subclasses)   │  │
│  └──────────────────┘  └─────────────────────┘  │
└─────────────────────┬───────────────────────────┘
                      │ usan
┌─────────────────────▼───────────────────────────┐
│                   CORE (app/core/)               │
│  BasePage, BaseFlow, ExecutionContext            │
└─────────────────────────────────────────────────┘
```

### Regla principal
- **Pages** = pantallas del portal. Solo selectores y acciones atómicas.
- **Pages/common** = lógica compartida entre módulos. Las subclases sólo añaden comportamiento exclusivo.
- **Flows** = operaciones de negocio. Coordinan múltiples páginas.
- **Steps** = únicamente llaman a Flows. Sin Selenium directo.

---

## Capa común de Page Objects

`app/pages/common/` contiene Page Objects base reutilizados por múltiples módulos, eliminando duplicación de código.

### `CfdiEmisionPage` — Sección Conceptos y Servicios

Base para la sección de conceptos del formulario CFDI. Implementa el flujo completo de alta de un concepto:

| Responsabilidad | Método |
|---|---|
| Abrir modal | `click_agregar_concepto()` |
| Llenar 12 campos del modal | `fill_descripcion`, `fill_cantidad`, `fill_valor_unitario`, `fill_clave_prod_serv`, `fill_clave_unidad`, `select_objeto_impuesto`, `fill_descuento`, `select_impuesto`, `select_retencion_o_traslado`, `select_tipo_factor`, `fill_tasa_o_cuota`, `fill_no_identificacion` |
| Guardar y confirmar en tabla | `wait_for_nuevo_concepto_guardado()` |
| Orquestar flujo completo | `agregar_concepto_completo(concepto)` |
| Adaptador desde Excel | `agregar_concepto_desde_caso(caso)` |
| Hooks sobreescribibles | `_post_agregar_impuesto_hook()`, `_post_guardar_hook(descripcion)` |

**Subclases:**

```
CfdiEmisionPage (app/pages/common/cfdi_emision_page.py)
    ├── FacturaConceptosPage  — agrega screenshot tras guardar cada concepto
    └── NotaCreditoConceptosPage — agrega pause(5) tras impuesto; screenshot pre-guardar
```

### `CfdiResultadoPage` — Pantalla de Resultado del Timbrado

Base para la pantalla que muestra el visor de timbrado, UUID, errores y botones de descarga tras el timbrado:

| Método | Descripción |
|---|---|
| `wait_for_visor_timbrado(timeout=3)` | Espera el visor `app-factura-timbrada`; retorna `bool`, no lanza excepción |
| `is_timbrado_exitoso()` | Detecta visor visible (30 s); fallback por UUID o mensaje de éxito |
| `has_error()` | Detecta mensaje de error de PAC/SAT |
| `get_error_message()` | Extrae la primera línea de error significativa |
| `get_uuid_cfdi()` | Lee el UUID del CFDI timbrado |
| `get_fecha_timbrado()` | Lee la fecha de timbrado |
| `click_descargar_pdf()` / `click_descargar_xml()` | Hace click en los botones reales del portal (`app-factura-timbrada button:nth-child(1/2)`) |
| `click_nueva_factura()` | Regresa al formulario vacío |

**Locators reales del portal (definidos en la base):**

| Locator | Selector |
|---|---|
| `PANTALLA_VISOR` | `app-factura-timbrada` |
| `BTN_DESCARGAR_PDF` | `app-factura-timbrada div.flex.flex-col.gap-4.w-full button:nth-child(1)` |
| `BTN_DESCARGAR_XML` | `app-factura-timbrada div.flex.flex-col.gap-4.w-full button:nth-child(2)` |

**Subclases:**

```
CfdiResultadoPage (app/pages/common/cfdi_resultado_page.py)
    ├── FacturaResultadoPage   — thin subclass (sin lógica adicional)
    └── NotaCreditoResultadoPage — thin subclass (sin lógica adicional)
```

---

## Capa común de Flows

`app/flows/common/` contiene Flows base reutilizados por todos los módulos.

### `CfdiDescargaFlow` — Descarga de PDF y XML post-timbrado

Gestiona el ciclo completo de descarga tras el timbrado CFDI sin necesidad de reescribir la lógica en cada módulo:

| Paso | Descripción |
|---|---|
| 1 | Espera el visor `app-factura-timbrada` (máx 3 s, no bloquea si no aparece) y toma screenshot |
| 2 | Configura Chrome vía CDP (`Page.setDownloadBehavior`) para descargar en `outputs/{modulo}/{caso_id}/` sin diálogos |
| 3 | Click en Descargar PDF → `time.sleep(2)` → screenshot |
| 4 | Re-aplica CDP → Click en Descargar XML → `time.sleep(2)` → screenshot |
| 5 | Registra `archivos_descargados` en el `execution_context` |

**Subclases** (solo implementan `_get_resultado_page()`):

```
CfdiDescargaFlow (app/flows/common/cfdi_descarga_flow.py)
    ├── FacturaDescargaFlow       — retorna FacturaResultadoPage
    └── NotaCreditoDescargaFlow   — retorna NotaCreditoResultadoPage
                                    + override _obtener_download_dir (clave evidence_dir_nc)
```

**Agregar un módulo nuevo:**

```python
from app.flows.common.cfdi_descarga_flow import CfdiDescargaFlow
from app.pages.nuevo_flujo.nuevo_resultado_page import NuevoResultadoPage

class NuevoDescargaFlow(CfdiDescargaFlow):
    def _get_resultado_page(self):
        return NuevoResultadoPage(self.driver)
```

Si el contexto registra el directorio de evidencias con una clave diferente a `"evidence_dir"`, sobreescribir también `_obtener_download_dir()`.

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
│   │   ├── common/       # Capa compartida (Login, Home, Menu, Modal,
│   │   │   │             #   Loader, Download, CfdiEmision, CfdiResultado)
│   │   │   ├── cfdi_emision_page.py    ← base Conceptos (Factura + NC)
│   │   │   ├── cfdi_resultado_page.py  ← base Resultado timbrado
│   │   │   ├── login_page.py
│   │   │   ├── home_page.py
│   │   │   ├── menu_page.py
│   │   │   ├── modal_page.py
│   │   │   ├── loader_page.py
│   │   │   └── download_page.py
│   │   ├── factura/      # Thin subclasses + páginas exclusivas Factura
│   │   │   ├── factura_conceptos_page.py   ← extiende CfdiEmisionPage
│   │   │   ├── factura_resultado_page.py   ← extiende CfdiResultadoPage
│   │   │   ├── factura_page.py
│   │   │   ├── factura_emisor_page.py
│   │   │   ├── factura_receptor_page.py
│   │   │   ├── factura_comprobante_page.py
│   │   │   ├── factura_impuestos_page.py
│   │   │   └── factura_cargos_no_facturables_page.py
│   │   ├── nota_credito/ # Thin subclasses + páginas exclusivas NC
│   │   │   ├── nota_credito_conceptos_page.py   ← extiende CfdiEmisionPage
│   │   │   ├── nota_credito_resultado_page.py   ← extiende CfdiResultadoPage
│   │   │   ├── nota_credito_page.py
│   │   │   ├── nota_credito_emisor_page.py
│   │   │   ├── nota_credito_receptor_page.py
│   │   │   ├── nota_credito_comprobante_page.py
│   │   │   ├── nota_credito_configuracion_page.py
│   │   │   ├── nota_credito_impuestos_page.py
│   │   │   └── nota_credito_cargos_no_facturables_page.py
│   │   ├── ppd/
│   │   ├── complemento_pago/
│   │   └── adenda/
│   ├── flows/            # Lógica de negocio por módulo
│   │   ├── common/       # Login, Navigation, Validation
│   │   │   ├── cfdi_descarga_flow.py  ← base descarga PDF/XML (CDP + visor)
│   │   │   ├── login_flow.py
│   │   │   ├── navigation_flow.py
│   │   │   └── validation_flow.py
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

- Python 3.13+
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

### Factura (pytest-bdd)

```bash
cd automation_framework
.venv\Scripts\python.exe -m pytest tests/step_definitions/factura_steps.py -m factura -v -s
```

### Nota de Crédito (runner directo)

```bash
cd automation_framework
.venv\Scripts\python.exe tests/runners/run_nota_credito.py
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

Todos los outputs se guardan en `outputs/` organizados por módulo y caso:

| Directorio | Contenido |
|---|---|
| `outputs/factura/{caso_id}/` | PDF y XML descargados del portal (por caso) |
| `outputs/factura/{caso_id}/screenshots/` | Capturas de evidencia por caso Factura |
| `outputs/nota_credito/{caso_id}/` | PDF y XML descargados del portal (por caso) |
| `outputs/nota_credito/{caso_id}/screenshots/` | Capturas de evidencia por caso NC |
| `outputs/logs/facto8_YYYY-MM-DD.log` | Log diario de ejecución con rotación |
| `outputs/pdf/` | Reportes PDF ejecutivos |
| `outputs/xml/` | Reportes XML técnicos |
| `outputs/json/` | Resultados en formato JSON |
| `outputs/zip/` | ZIP consolidado de evidencias |
| `allure-results/` | Datos para dashboard Allure |

### Capturas automáticas por flujo

El framework toma screenshots automáticos en puntos clave:

| Evento | Archivo generado |
|---|---|
| Pantalla inicial cargada | `01_pantalla_*_cargada.png` |
| Cada sección completada | `02_emisor_capturado.png`, `03_receptor_capturado.png`, etc. |
| Concepto guardado (Factura) | `concepto_guardado_{descripcion}.png` |
| Pre-guardar concepto (NC) | `nc_pre_guardar_concepto.png` (en `outputs/screenshots/`) |
| Totales validados | `08_totales_validados.png` |
| Visor de timbrado | `visor_timbrado.png` |
| PDF descargado | `descarga_pdf_iniciada.png` |
| XML descargado | `descarga_xml_iniciada.png` |
| Descarga completada | `08_descarga_completada.png` |
| Error de timbrado | `error_timbrado.png` |

---

## Agregar un nuevo flujo

1. **Evaluar reutilización** — si el nuevo módulo tiene sección de conceptos o pantalla de resultado, heredar de `CfdiEmisionPage` y/o `CfdiResultadoPage` en lugar de reimplementar desde cero.
2. **Crear Page Objects** en `app/pages/{nuevo_flujo}/`:
   - Para conceptos: `class NuevoConceptosPage(CfdiEmisionPage)` — sólo sobreescribir `_post_guardar_hook` o `_post_agregar_impuesto_hook` si hay comportamiento exclusivo.
   - Para resultado: `class NuevoResultadoPage(CfdiResultadoPage)` — thin subclass; hereda automáticamente locators del visor y métodos de descarga.
   - Para páginas exclusivas: heredar directamente de `BasePage`.
3. **Crear el Flow de descarga** en `app/flows/{nuevo_flujo}/{nuevo_flujo}_descarga_flow.py`:
   ```python
   from app.flows.common.cfdi_descarga_flow import CfdiDescargaFlow
   from app.pages.{nuevo_flujo}.{nuevo_flujo}_resultado_page import NuevoResultadoPage

   class NuevoDescargaFlow(CfdiDescargaFlow):
       def _get_resultado_page(self):
           return NuevoResultadoPage(self.driver)
   ```
   Si el contexto usa una clave distinta para `evidence_dir`, sobreescribir `_obtener_download_dir()` también.
4. **Crear el Flow principal** en `app/flows/{nuevo_flujo}/{nuevo_flujo}_flow.py` heredando de `BaseFlow`.
5. **Registrar el flow** en `app/flows/orchestrator/flow_registry.py`.
6. **Definir dependencias** en `app/flows/orchestrator/dependency_resolver.py` si aplica.
7. **Crear feature file** en `tests/features/{nuevo_flujo}.feature`.
8. **Crear step definitions** en `tests/step_definitions/{nuevo_flujo}_steps.py`.
9. **Agregar test data** en `tests/test_data/{nuevo_flujo}/{nuevo_flujo}_valido.json`.
10. **Agregar runner** en `tests/runners/run_{nuevo_flujo}.py`.
11. **Agregar marker** en `pytest.ini`.

---

## Convenciones del proyecto

- Nombres de archivos y variables: `snake_case`
- Nombres de clases: `PascalCase`
- Sin credenciales hardcodeadas — usar siempre variables de entorno
- Sin Selenium directo en steps o en lógica de negocio de pages
- Sin lógica de negocio compleja en Page Objects
- **Máxima reutilización**: lógica compartida va en `app/pages/common/`, las subclases sólo añaden lo exclusivo
- Selectores priorizados: `id > name > data-testid > data-cy > aria-label > CSS estable`
- Evitar: XPath absoluto, selectores por posición, texto dinámico
- Timeouts de espera en getters de texto: máximo `timeout=2` para no bloquear el flujo ante campos opcionales o ausentes
- Cada módulo tiene su `__init__.py`
- TODOs documentados donde faltan selectores o implementaciones reales
