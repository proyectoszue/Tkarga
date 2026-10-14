# Panel de pruebas ZUE — Guía del Core

El **Core** es la **base / estándar** del panel de pruebas funcionales.

---

## Estándar: qué es el Core y qué incluye

### Rol

| | |
|-|-|
| **Core** | Motor + UI genérica. No conoce reglas de negocio de un dominio concreto. |
| **Dominio** | Publica pruebas, campos y detectores propios heredando / extendiendo el Core. |

Separación por **prefijo de archivo**: `core_*` solo para el estándar; cada dominio usa su propio prefijo.

### Qué incluye el Core (base)

**Backend**

| Pieza | Uso |
|-------|-----|
| `core_test_provider.py` | Contrato `zue.testing.dashboard.test.provider` + helpers (`buildDashboardSpec`, `findDashboardSpec`, log, controlados, `completeProcessTest`). |
| `core_adapter_session.py` | Sesión: descubrir providers, `prepare_run` / `run_case` / `finish_run`, savepoint y rollback. |
| `core_functional_log_buffer.py` | Log paso a paso de cada prueba. |
| `core_run_history.py` | Modelos del Historial. |
| `core_test_model_fields.py` | Field picker “+ Agregar dato”. |
| `views/core_*.xml` | Menú Panel + Historial. |

**Frontend**

| Pieza | Uso |
|-------|-----|
| `core_zue_testing_dashboard.js/xml` | Pantalla: toolbar, catálogo, tabla, drawers, **bloque Configuración compartida** (sin campos). |
| `SharedConfigFields` (vacío) | Contenedor estándar; cada dominio agrega campos con `t-inherit`. |
| Ganchos JS | `showGroupSharedConfig`, `applyGroupSharedConfig`, `emptyGroupSharedConfig`, `needsTestInputState`, `showParametricFieldPicker`, `validateBeforeRun`. |
| `core_process_result_viewer.*` | Viewer genérico de resultados de proceso. |
| `core_*.scss` | Estilos base del panel. |

### Qué debe ir en el dominio (no en `core_*`)

- Campos de la configuración compartida (`t-inherit` de `SharedConfigFields`).
- Formularios / inputs propios de las pruebas del dominio.
- Detectores y validaciones de negocio del dominio.
- Layouts especiales del viewer, si el dominio los necesita.
- Providers y casos de prueba del dominio.

### Prefijos de archivo (obligatorio)

| Prefijo | Uso |
|---------|-----|
| `core_` | Solo motor / UI estándar |
| `<dominio>_` | Archivos del dominio (ej. `inventory_stock_test_provider.py`) |

Aplica a `models/`, `tests/` y `static/src/{js,xml,scss}/`.

---

## Cómo funciona una ejecución

```text
Panel → Core descubre providers → usuario elige y ejecuta
  → por prueba: savepoint → _run_zue_testing_dashboard_test
  → findDashboardSpec + escenario → resultado → rollback
```

---

## Métodos del estándar (provider)

Viven en `zue.testing.dashboard.test.provider`. Los dominios los heredan.

### Atributos UI

| Atributo | Uso |
|----------|-----|
| `_zue_testing_dashboard_module_key` | Clave interna del módulo |
| `_zue_testing_dashboard_module_name` | Combo Módulo |
| `_zue_testing_dashboard_provider_name` | Combo Grupo |
| `_zue_testing_dashboard_provider_description` | Descripción del grupo |

### Contrato (implementar)

| Método | Uso |
|--------|-----|
| `_get_zue_testing_dashboard_test_specs` | Lista de pruebas (specs) |
| `_get_zue_testing_dashboard_scope_labels` | Labels del filtro |
| `_get_zue_testing_dashboard_source_labels` | Labels de origen (opcional) |
| `_run_zue_testing_dashboard_test` | Ejecutar una prueba por `technical_name` |

### Specs

Una **spec** describe una prueba: `technical_name`, `summary`, `method_name`, `tags`, `test_model`, `test_type`, `module_name`.

#### `buildDashboardSpec(...)`

Arma el dict estándar de una prueba. Se usa dentro de `_get_zue_testing_dashboard_test_specs`.

#### `findDashboardSpec(technical_name)`

Busca esa spec en el catálogo. Se usa al inicio de `_run_zue_testing_dashboard_test` para saber qué método correr.

```python
spec = self.findDashboardSpec(technical_name)
if not spec:
    raise UserError(...)
method = getattr(self, spec["method_name"])
```

### Helpers de ejecución

| Método | Uso |
|--------|-----|
| `getDashboardTestParams()` | Params desde la UI |
| `logFunctionalStep` / `logFunctionalField` | Log visible |
| `isControlledConstraintError` | ¿Error de restricción esperado? |
| `raiseControlledBehavior` | Marca resultado **controlado** |
| `completeProcessTest` | Cierra OK una prueba **process** con tablas |

---

## Extender el Core (nuevo dominio)

1. Archivos con prefijo del dominio.
2. Provider que herede `zue.testing.dashboard.test.provider`.
3. Specs con `buildDashboardSpec`; ejecución con `findDashboardSpec`.
4. Si necesita config compartida: `t-inherit` de `SharedConfigFields`.
5. Si necesita inputs de proceso u otros formularios: plantillas / `patch` del dominio.
6. Lógica de negocio solo en archivos del prefijo del dominio; nunca en `core_*`.

### Plantilla mínima

```python
class MiProvider(models.AbstractModel):
    _name = "mi.dominio.zue.testing.dashboard.provider"
    _inherit = "zue.testing.dashboard.test.provider"
    _zue_testing_dashboard_module_key = "mi_dominio"
    _zue_testing_dashboard_module_name = "Mi Dominio"
    _zue_testing_dashboard_provider_name = "Casos básicos"

    @api.model
    def _get_zue_testing_dashboard_test_specs(self):
        return [
            self.buildDashboardSpec(
                "mi_dominio",
                "test_ejemplo",
                _("Valida el escenario X."),
                self.testEjemplo,
                tags=["basicos"],
                test_type="parametric",
            ),
        ]

    @api.model
    def _get_zue_testing_dashboard_scope_labels(self):
        return {"all": _("Todas"), "basicos": _("Básicos")}

    def _run_zue_testing_dashboard_test(self, technical_name):
        spec = self.findDashboardSpec(technical_name)
        if not spec:
            raise UserError(_("No se encontró la prueba: %s") % technical_name)
        getattr(self, spec["method_name"])(self.getDashboardTestParams())

    def testEjemplo(self, params=None):
        self.logFunctionalStep("Ejecutar escenario")
        # preparar → actuar → validar
```

---

## Ejemplo real: cómo se extendió el Core para Nómina

Nómina es la primera extensión del estándar. Sirve de **guía de implementación** para otros módulos: copia la estructura, cambia el prefijo y los modelos de negocio.

### Prefijo y ubicación

Todo lo de Nómina usa el prefijo `payroll_`:

| Tipo | Archivos |
|------|----------|
| Providers | `models/payroll_hr_*.py` |
| Escenarios | `tests/payroll_test_*.py` |
| UI / patch | `static/src/js/payroll_*.js`, `static/src/xml/payroll_*.xml`, `static/src/scss/payroll_*.scss` |
| Extensiones backend | `models/payroll_adapter_session.py`, `models/payroll_test_model_fields.py` |

### 1. Provider que hereda el contrato Core

Ejemplo: configuración HR.

```python
# models/payroll_hr_configuration_test_provider.py

class ZueHrConfigurationTestingDashboardProvider(models.AbstractModel):
    _name = "zue.testing.dashboard.hr.configuration.provider"
    _inherit = "zue.testing.dashboard.test.provider"  # ← estándar Core

    _zue_testing_dashboard_module_key = "payroll"
    _zue_testing_dashboard_module_name = "Nómina"
    _zue_testing_dashboard_provider_name = "Configuración HR"

    @api.model
    def _get_zue_testing_dashboard_test_specs(self):
        return [
            self.buildDashboardSpec(  # helper del Core
                "zue_hr_employee",
                "test_create_contribution_register",
                _("Crea un tipo de entidad EPS."),
                self.testCreateContributionRegister,
                tags=["contribution_register"],
                test_model="hr.contribution.register",
                test_type="parametric",
            ),
            # ... más specs
        ]

    def _run_zue_testing_dashboard_test(self, technical_name):
        spec = self.findDashboardSpec(technical_name)  # helper del Core
        # ... llama al escenario en tests/payroll_test_hr_configuration.py
```

Otros providers de Nómina siguen el mismo patrón:

- `payroll_hr_employee_contract_test_provider.py`
- `payroll_hr_payroll_liquidation_test_provider.py` (mixin + grupos de liquidación)
- `payroll_hr_social_security_test_provider.py` (cierres SS / provisiones)

### 2. Campos de Configuración compartida (herencia XML)

El Core deja `SharedConfigFields` vacío. Nómina inyecta contrato / fechas / año-mes:

```xml
<!-- static/src/xml/payroll_zue_testing_dashboard.xml -->
<t t-name="zue_testing_dashboard.SharedConfigFields.payroll"
   t-inherit="zue_testing_dashboard.SharedConfigFields"
   t-inherit-mode="extension"
   owl="1">
    <xpath expr="//div[hasclass('o_zue_testing_dashboard_shared_config_fields')]" position="inside">
        <!-- campos de Nómina: Contrato, fechas, año, mes -->
    </xpath>
</t>
```

### 3. Inputs de proceso propios del dominio

Nómina define `ProcessTestInputs` (formularios por prueba: liquidación, novedades, etc.) en el mismo XML `payroll_zue_testing_dashboard.xml`.  
El Core solo hace `t-call` a esa plantilla; no contiene los campos.

### 4. Lógica UI por `patch` JS

```javascript
// static/src/js/payroll_zue_testing_dashboard.js
patch(ZueTestingDashboard.prototype, {
    // showGroupSharedConfig, applyGroupSharedConfig, emptyGroupSharedConfig
    // detectores de proceso, validateBeforeRun, etc.
});
```

El viewer de SS/provisiones se extiende igual:

```javascript
// static/src/js/payroll_process_result_viewer.js
patch(ZueProcessResultViewer.prototype, { /* layouts SS / provisiones */ });
```

### 5. Cómo replicarlo en otro módulo

| Paso en Nómina | Qué hacer en tu dominio |
|----------------|-------------------------|
| Prefijo `payroll_` | Usa tu prefijo (`inventory_`, `purchase_`, …) |
| `_inherit` del provider Core | Igual |
| `buildDashboardSpec` / `findDashboardSpec` | Igual |
| `t-inherit` de `SharedConfigFields` | Solo si necesitas config compartida; con **tus** campos |
| `ProcessTestInputs` / patch JS | Solo si necesitas formularios o detectores propios |
| Escenarios en `tests/payroll_test_*.py` | `tests/<dominio>_test_*.py` |

No copies lógica de `hr.*` a otro dominio: copia **solo la estructura** de extensión.

---

## Buenas prácticas

1. Prefijo de dominio en cada archivo nuevo.
2. Pruebas autónomas y con data mínima.
3. Fallos con mensajes claros; usar `logFunctionalStep`.
4. No mezclar lógica de un dominio en `core_*` ni en archivos de otro dominio.

---

## Resumen

> El Core es el estándar: contrato, sesión, UI base, config compartida vacía y ganchos.  
> Cada dominio agrega providers, campos e inputs por herencia/`patch`, sin meter negocio en `core_*`.
