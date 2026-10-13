# -*- coding: utf-8 -*-

import json
import time
import traceback

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang

from .functional_log_buffer import (
    SESSION_CTX_KEY,
    TEST_PARAMS_CTX_KEY,
    TRACE_SEPARATOR,
    clearFunctionalLogBuffer,
    getFunctionalLogText,
    resetFunctionalLogBuffer,
)

# Columnas usadas para volcar los datos de liquidacion como texto legible en el Historial.
PROCESS_RESULT_MONETARY_KEYS = frozenset({"amount", "total"})
PROCESS_RESULT_COLUMNS = {
    "worked_days_lines": [
        ("code", "Codigo"),
        ("name", "Descripcion"),
        ("number_of_days", "Dias"),
        ("number_of_hours", "Horas"),
    ],
    "calculated_lines": [
        ("code", "Codigo"),
        ("name", "Concepto"),
        ("category", "Categoria"),
        ("quantity", "Cantidad"),
        ("amount", "Importe"),
        ("total", "Total"),
    ],
    "not_applied_lines": [
        ("code", "Codigo"),
        ("name", "Concepto"),
        ("category", "Categoria"),
        ("quantity", "Cantidad"),
        ("amount", "Importe"),
        ("total", "Total"),
    ],
}


class ZueTestingDashboardRollback(Exception):
    """Excepcion interna usada para revertir datos de prueba sin marcar fallo."""

    def __init__(self, functional_log=""):
        super().__init__(functional_log)
        self.functional_log = functional_log


class ZueTestingDashboardControlled(Exception):
    """Excepcion interna para comportamientos esperados del sistema.

    Se usa cuando una restriccion SQL o regla de unicidad responde como debe,
    sin representar un fallo funcional de la prueba.
    """

    def __init__(self, message, functional_log=""):
        super().__init__(message)
        self.message = message
        self.functional_log = functional_log


class ZueTestingDashboardProcessComplete(Exception):
    """Excepcion interna para finalizar pruebas de proceso con metricas de liquidacion."""

    def __init__(
        self,
        status,
        message,
        functional_log="",
        calculated_lines=None,
        worked_days_lines=None,
        not_applied_lines=None,
        obtained_info=None,
    ):
        super().__init__(message)
        self.status = status
        self.message = message
        self.functional_log = functional_log
        self.calculated_lines = calculated_lines or ""
        self.worked_days_lines = worked_days_lines or ""
        self.not_applied_lines = not_applied_lines or ""
        self.obtained_info = obtained_info or ""

    def getProcessResultValues(self):
        return {
            "calculated_lines": self.calculated_lines,
            "worked_days_lines": self.worked_days_lines,
            "not_applied_lines": self.not_applied_lines,
            "obtained_info": self.obtained_info,
        }


class ZueTestingDashboardSession(models.TransientModel):
    """Sesion temporal usada por la pantalla OWL para ejecutar pruebas.

    El modelo coordina la ejecucion visual: descubre providers, prepara la
    ejecucion, ejecuta cada caso y conserva resultados transient para la UI.
    """

    _name = "zue.testing.dashboard.session"
    _description = "Sesion del panel de pruebas ZUE"
    _order = "id desc"

    name = fields.Char(string="Nombre", default="Ejecucion de pruebas ZUE", readonly=True)
    provider_model = fields.Char(string="Modelo proveedor", readonly=True)
    provider_name = fields.Char(string="Proveedor", readonly=True)
    module_key = fields.Char(string="Clave modulo", readonly=True)
    module_name = fields.Char(string="Modulo", readonly=True)
    scope_label = fields.Char(string="Etiqueta filtro", readonly=True)
    suite_scope = fields.Char(string="Filtro", default="all", required=True, readonly=True)
    state = fields.Selection(
        selection=[
            ("draft", "Borrador"),
            ("running", "En ejecucion"),
            ("success", "Exitoso"),
            ("error", "Error"),
        ],
        string="Estado",
        default="draft",
        readonly=True,
    )
    started_at = fields.Datetime(string="Inicio", readonly=True)
    finished_at = fields.Datetime(string="Fin", readonly=True)
    line_ids = fields.One2many(
        comodel_name="zue.testing.dashboard.line",
        inverse_name="session_id",
        string="Resultados de pruebas",
        readonly=True,
    )
    total_count = fields.Integer(string="Total", compute="_compute_counts")
    passed_count = fields.Integer(string="Aprobadas", compute="_compute_counts")
    failed_count = fields.Integer(string="Fallidas", compute="_compute_counts")
    controlled_count = fields.Integer(string="Controladas", compute="_compute_counts")
    skipped_count = fields.Integer(string="Omitidas", compute="_compute_counts")

    @api.depends("line_ids.status")
    def _compute_counts(self):
        """Calcula los contadores visibles de resultados por estado."""
        for session in self:
            session.total_count = len(session.line_ids)
            session.passed_count = len(session.line_ids.filtered(lambda line: line.status == "ok"))
            session.failed_count = len(session.line_ids.filtered(lambda line: line.status == "failed"))
            session.controlled_count = len(session.line_ids.filtered(lambda line: line.status == "controlled"))
            session.skipped_count = len(session.line_ids.filtered(lambda line: line.status == "skipped"))

    @api.model
    def get_adapter_data(self):
        """Entrega a OWL los datos iniciales de la pantalla.

        Incluye modulos agrupados, notas funcionales, leyenda de estados y la
        ultima ejecucion transient del usuario si todavia existe.
        """
        modules = self._modules_payload()
        provider_models = [
            group["model"]
            for module in modules
            for group in module["groups"]
        ]
        return {
            "modules": modules,
            "notes": self._notes_payload(),
            "status_legends": self._status_legends_payload(),
            "last_run": self._last_run_payload(provider_models),
        }

    @api.model
    def prepare_run(self, provider_model, suite_scope="all", module_key=False, module_name=False, scope_label=False):
        """Prepara una nueva ejecucion visual para un provider y un filtro.

        Crea la sesion transient en estado running y devuelve a OWL solo las
        specs que pertenecen al tag seleccionado.
        """
        if not provider_model:
            raise UserError(_("Debe seleccionar un proveedor de pruebas."))
        if not suite_scope:
            suite_scope = "all"
        provider_payload = self._provider_payload(provider_model)
        specs = self._specs_for_scope(provider_payload["specs"], suite_scope)
        session = self.create({
            "provider_model": provider_model,
            "provider_name": provider_payload["name"],
            "module_key": module_key or False,
            "module_name": module_name or False,
            "scope_label": scope_label or suite_scope,
            "suite_scope": suite_scope,
            "state": "running",
            "started_at": fields.Datetime.now(),
            "finished_at": False,
        })
        return {
            "session_id": session.id,
            "state": session.state,
            "scope": session.suite_scope,
            "provider": provider_payload,
            "specs": specs,
            "counts": session._counts_payload(),
        }

    @api.model
    def run_case(self, session_id, technical_name, sequence, test_params=None, test_data_lines=None):
        """Ejecuta una prueba individual solicitada por OWL.

        Localiza la spec, llama al provider dentro de savepoint y crea la linea
        de resultado que la pantalla muestra inmediatamente.
        """
        session = self.browse(session_id).exists()
        if not session:
            raise UserError(_("La sesion de pruebas ya no existe."))
        provider = self._provider(session.provider_model).with_context(
            **{
                SESSION_CTX_KEY: session.id,
                TEST_PARAMS_CTX_KEY: test_params or {},
            },
        )
        spec = self._find_spec(provider, technical_name)
        if not spec:
            raise UserError(_("No se encontro la prueba solicitada: %s") % technical_name)
        status, message, detail, duration, functional_log, process_result = session._run_provider_test(provider, spec)
        line = session._create_result_line(
            sequence,
            spec,
            status,
            message,
            detail,
            duration,
            functional_log,
            test_params=test_params,
            test_data_lines=test_data_lines,
            process_result=process_result,
        )
        return {
            "line": line._line_payload(),
            "counts": session._counts_payload(),
            "state": session.state,
        }

    @api.model
    def finish_run(self, session_id, stopped_early=False):
        """Cierra la ejecucion despues de ejecutar todas las pruebas.

        Si alguna linea fallo, la sesion queda en error. Las lineas controladas
        no se consideran fallo y permiten cerrar la ejecucion en success.
        """
        session = self.browse(session_id).exists()
        if not session:
            raise UserError(_("La sesion de pruebas ya no existe."))
        failed = session.line_ids.filtered(lambda line: line.status == "failed")
        history_state = "partial" if stopped_early else ("error" if failed else "success")
        session.write({
            "state": "error" if failed else "success",
            "finished_at": fields.Datetime.now(),
        })
        history_id = session.archiveRunHistory(history_state)
        return {
            "session_id": session.id,
            "state": session.state,
            "counts": session._counts_payload(),
            "history_id": history_id,
        }

    def archiveRunHistory(self, run_state):
        """Persiste la ejecucion para consulta posterior en Historial."""
        self.ensure_one()
        if not self.line_ids:
            return False
        module_key = self.module_key
        module_name = self.module_name
        if not module_name and self.provider_model in self.env.registry.models:
            provider = self.env[self.provider_model]
            module_key = module_key or getattr(provider, "_zue_testing_dashboard_module_key", False)
            module_name = module_name or getattr(provider, "_zue_testing_dashboard_module_name", False)
        module_name = module_name or self.provider_name
        counts = self._counts_payload()
        line_vals = []
        technical_names = []
        for line in self.line_ids.sorted("sequence"):
            functional_log, technical_detail = line._splitResultDetail()
            technical_names.append(line.technical_name or "")
            line_vals.append((0, 0, {
                "sequence": line.sequence,
                "provider_model": line.provider_model,
                "provider_name": line.provider_name,
                "technical_name": line.technical_name,
                "module_name": line.module_name,
                "summary": line.summary,
                "test_type": line.test_type,
                "status": line.status,
                "message": line.message,
                "functional_log": functional_log,
                "detail": technical_detail,
                "test_data": line.test_data or "",
                "calculated_lines": line.formatProcessResultText("calculated_lines"),
                "worked_days_lines": line.formatProcessResultText("worked_days_lines"),
                "not_applied_lines": line.formatProcessResultText("not_applied_lines"),
                "obtained_info": line.formatProcessResultText("obtained_info"),
                "result_payload": line.buildProcessResultPayload(),
                "duration": line.duration,
            }))
        started_label = fields.Datetime.to_string(self.started_at) if self.started_at else ""
        # sudo: required to persist history while keeping read-only ACL for dashboard users
        run = self.env["zue.testing.dashboard.run"].sudo().create({
            "name": _("Ejecucion %s - %s") % (started_label, self.provider_name),
            "user_id": self.env.user.id,
            "module_key": module_key or "other",
            "module_name": module_name,
            "provider_model": self.provider_model,
            "provider_name": self.provider_name,
            "suite_scope": self.suite_scope,
            "scope_label": self.scope_label or self.suite_scope,
            "state": run_state,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "ok_count": counts["ok"],
            "controlled_count": counts["controlled"],
            "failed_count": counts["failed"],
            "skipped_count": counts["skipped"],
            "total_count": counts["total"],
            "test_catalog": "\n".join(filter(None, technical_names)),
            "line_ids": line_vals,
        })
        return run.id

    @api.model
    def clear_last_run(self, session_id=False):
        """Elimina la ultima sesion transient visible para el usuario.

        La UI lo usa para limpiar la pantalla sin tocar data funcional, porque
        las sesiones y lineas son temporales.
        """
        domain = [("create_uid", "=", self.env.user.id)]
        if session_id:
            domain.append(("id", "=", session_id))
        session = self.search(domain, order="id desc", limit=1)
        if session:
            session.unlink()
        return {
            "session_id": False,
            "state": "draft",
            "counts": {"total": 0, "ok": 0, "failed": 0, "controlled": 0, "skipped": 0},
            "current_index": 0,
            "total_to_run": 0,
            "lines": [],
        }

    def _create_result_line(
        self,
        sequence,
        spec,
        status,
        message,
        detail,
        duration,
        functional_log="",
        test_params=None,
        test_data_lines=None,
        process_result=None,
    ):
        """Crea la linea transient que OWL muestra en la tabla de resultados.

        La linea se crea fuera del savepoint de la prueba para que el resultado
        permanezca visible aunque la data del escenario sea revertida.
        """
        process_result = process_result or {}
        values = {
            "session_id": self.id,
            "sequence": sequence,
            "provider_model": self.provider_model,
            "provider_name": self.provider_name,
            "technical_name": spec["technical_name"],
            "module_name": spec.get("module_name") or self.provider_name,
            "summary": str(spec.get("summary") or ""),
            "test_type": spec.get("test_type") or False,
            "status": status,
            "message": message,
            "functional_log": functional_log or "",
            "detail": self._buildResultDetail(status, detail, functional_log),
            "test_data": self.formatTestDataDisplay(test_data_lines, test_params),
            "calculated_lines": process_result.get("calculated_lines") or "",
            "worked_days_lines": process_result.get("worked_days_lines") or "",
            "not_applied_lines": process_result.get("not_applied_lines") or "",
            "obtained_info": process_result.get("obtained_info") or "",
            "duration": duration,
        }
        return self.env["zue.testing.dashboard.line"].create(values)

    def formatTestDataDisplay(self, test_data_lines=None, test_params=None):
        """Arma el texto visible de Datos de prueba a partir de + Agregar dato."""
        lines = []
        for item in test_data_lines or []:
            if not isinstance(item, dict):
                continue
            label = item.get("label") or item.get("name") or ""
            value = item.get("value")
            if value is None or value is False or value == "":
                continue
            lines.append("%s: %s" % (label, value))
        if lines:
            return "\n".join(lines)
        test_params = test_params or {}
        if not isinstance(test_params, dict) or not test_params:
            return ""
        return "\n".join("%s: %s" % (key, value) for key, value in test_params.items())

    def _buildResultDetail(self, status, detail, functional_log):
        """Combina log funcional y detalle tecnico en un solo campo persistente."""
        detail = detail or ""
        functional_log = functional_log or ""
        if status in ("ok", "controlled"):
            return detail
        if functional_log and detail:
            return "%s%s%s" % (functional_log, TRACE_SEPARATOR, detail)
        return functional_log or detail

    def _run_provider_test(self, provider, spec):
        """Ejecuta un metodo del provider dentro de un savepoint aislado.

        Si la prueba pasa, se levanta una excepcion interna controlada para
        forzar rollback y limpiar la data creada por el escenario. Si el
        sistema responde con una restriccion esperada, la prueba queda controlada.
        """
        self.ensure_one()
        started = time.perf_counter()
        resetFunctionalLogBuffer(self.id)
        try:
            try:
                with self.env.cr.savepoint():
                    provider._run_zue_testing_dashboard_test(spec["technical_name"])
                    functional_log = getFunctionalLogText(self.id)
                    raise ZueTestingDashboardRollback(functional_log)
            except ZueTestingDashboardRollback as rollback:
                duration = time.perf_counter() - started
                functional_log = rollback.functional_log or getFunctionalLogText(self.id)
                return "ok", _("Prueba aprobada y datos revertidos."), "", duration, functional_log, {}
            except ZueTestingDashboardControlled as controlled:
                duration = time.perf_counter() - started
                functional_log = controlled.functional_log or getFunctionalLogText(self.id)
                return "controlled", controlled.message, controlled.message, duration, functional_log, {}
            except ZueTestingDashboardProcessComplete as process_result:
                duration = time.perf_counter() - started
                functional_log = process_result.functional_log or getFunctionalLogText(self.id)
                return (
                    process_result.status,
                    process_result.message,
                    "",
                    duration,
                    functional_log,
                    process_result.getProcessResultValues(),
                )
        except Exception as error:
            duration = time.perf_counter() - started
            functional_log = getFunctionalLogText(self.id)
            if getattr(provider, "isControlledConstraintError", None) and provider.isControlledConstraintError(error):
                return "controlled", str(error), str(error), duration, functional_log, {}
            detail = traceback.format_exc(limit=8)
            return "failed", "%s: %s" % (error.__class__.__name__, error), detail, duration, functional_log, {}
        finally:
            clearFunctionalLogBuffer(self.id)

    def _counts_payload(self):
        """Convierte los contadores de la sesion al formato esperado por OWL."""
        self.ensure_one()
        return {
            "total": len(self.line_ids),
            "ok": len(self.line_ids.filtered(lambda line: line.status == "ok")),
            "failed": len(self.line_ids.filtered(lambda line: line.status == "failed")),
            "controlled": len(self.line_ids.filtered(lambda line: line.status == "controlled")),
            "skipped": len(self.line_ids.filtered(lambda line: line.status == "skipped")),
        }

    def _notes_payload(self):
        """Devuelve las notas funcionales mostradas en el panel lateral."""
        return [
            _("Cada prueba se ejecuta en su propio punto de guardado y revierte los datos creados."),
            _("Este adaptador ejecuta pruebas compatibles con interfaz. Las pruebas formales TransactionCase deben ejecutarse con la automatizacion de Odoo."),
        ]

    def _status_legends_payload(self):
        """Serializa la leyenda de estados de ejecucion para la UI."""
        return [
            {
                "status": "ok",
                "label": _("Correcto"),
                "color": "success",
                "description": _("La prueba finalizo correctamente y los datos del escenario fueron revertidos."),
            },
            {
                "status": "controlled",
                "label": _("Controlado"),
                "color": "controlled",
                "description": _("Comportamiento esperado del sistema, como restricciones SQL o reglas de unicidad, sin representar un error funcional."),
            },
            {
                "status": "failed",
                "label": _("Fallido"),
                "color": "danger",
                "description": _("La prueba no cumplio el resultado esperado o se presento un error no controlado."),
            },
            {
                "status": "skipped",
                "label": _("Omitido"),
                "color": "secondary",
                "description": _("La prueba no se ejecuto dentro de la ejecución actual."),
            },
        ]

    def _session_payload(self):
        """Serializa una sesion existente para restaurarla al abrir la pantalla.

        Permite que el usuario cambie de menu y vuelva a ver la ultima ejecucion
        mientras el registro transient no haya sido limpiado por Odoo.
        """
        self.ensure_one()
        lines = self.line_ids.sorted("sequence")
        source_labels = self._session_source_labels()
        total_to_run = len(lines)
        if self.provider_model in self.env.registry.models:
            provider_payload = self._provider_payload(self.provider_model)
            total_to_run = max(total_to_run, len(self._specs_for_scope(provider_payload["specs"], self.suite_scope)))
        return {
            "session_id": self.id,
            "provider_model": self.provider_model,
            "provider_name": self.provider_name,
            "scope": self.suite_scope,
            "state": self.state,
            "counts": self._counts_payload(),
            "current_index": len(lines),
            "total_to_run": total_to_run,
            "lines": [line._line_payload(source_labels) for line in lines],
        }

    def _session_source_labels(self):
        """Obtiene labels de fuente desde el provider de la sesion restaurada."""
        if self.provider_model not in self.env.registry.models:
            return {}
        provider = self.env[self.provider_model]
        labels_method = getattr(provider, "_get_zue_testing_dashboard_source_labels", None)
        if not labels_method:
            return {}
        return labels_method() or {}

    def _last_run_payload(self, provider_models):
        """Busca la ultima sesion transient del usuario para los providers activos."""
        domain = [("create_uid", "=", self.env.user.id)]
        if provider_models:
            domain.append(("provider_model", "in", provider_models))
        last_session = self.search(domain, order="id desc", limit=1)
        return last_session._session_payload() if last_session else False

    def _provider_model_names(self):
        """Descubre modelos instalados que publican specs del dashboard.

        El adapter no tiene una lista fija de modulos. Recorre el registry y se
        queda con modelos que implementan el contrato del provider.
        """
        providers = []
        for model_name in sorted(self.env.registry.models):
            if model_name == "zue.testing.dashboard.test.provider":
                continue
            model = self.env[model_name]
            specs_method = getattr(model, "_get_zue_testing_dashboard_test_specs", None)
            if not specs_method:
                continue
            try:
                specs = specs_method()
            except NotImplementedError:
                specs = []
            provider_name = getattr(model, "_zue_testing_dashboard_provider_name", None)
            # Incluye providers con specs o solo estructura (filtros sin pruebas aun).
            if specs or provider_name:
                providers.append(model_name)
        return providers


    def _modules_payload(self):
        """Agrupa providers por modulo funcional para el selector de tres niveles."""
        modules = {}
        for model_name in self._provider_model_names():
            provider = self._provider(model_name)
            module_key = getattr(provider, "_zue_testing_dashboard_module_key", None) or "other"
            module_name = getattr(provider, "_zue_testing_dashboard_module_name", None) or _("Otros")
            group_payload = self._provider_payload(model_name)
            module_data = modules.setdefault(module_key, {
                "key": module_key,
                "name": module_name,
                "groups": [],
            })
            module_data["groups"].append({
                "model": model_name,
                "name": group_payload["name"],
                "description": group_payload["description"],
                "specs": group_payload["specs"],
                "scopes": group_payload["scopes"],
            })
        for module_data in modules.values():
            module_data["groups"].sort(key=lambda item: item["name"])
        return sorted(modules.values(), key=lambda item: item["name"])

    def _providers_payload(self):
        """Construye el payload completo de todos los providers detectados."""
        return [self._provider_payload(model_name) for model_name in self._provider_model_names()]

    def _provider_payload(self, provider_model):
        """Normaliza un provider con metadata, specs y filtros disponibles.

        Este payload es el que consume OWL para llenar el selector de provider,
        el selector de filtros y el catalogo de pruebas detectadas.
        """
        provider = self._provider(provider_model)
        specs = self._normalized_specs(provider, provider._get_zue_testing_dashboard_test_specs())
        labels = self._provider_scope_labels(provider)
        return {
            "model": provider_model,
            "name": getattr(provider, "_zue_testing_dashboard_provider_name", provider._description or provider_model),
            "description": getattr(provider, "_zue_testing_dashboard_provider_description", ""),
            "specs": specs,
            "scopes": self._scopes_payload(specs, labels),
        }

    def _provider(self, provider_model):
        """Valida y devuelve el modelo provider solicitado por la UI."""
        if provider_model not in self.env.registry.models:
            raise UserError(_("No se encontro el proveedor de pruebas: %s") % provider_model)
        return self.env[provider_model]

    def _normalized_specs(self, provider, specs):
        """Convierte specs libres del provider a una estructura estable para OWL.

        Los providers pueden construir sus specs como prefieran, pero la UI
        recibe siempre los mismos campos normalizados.
        """
        normalized = []
        provider_name = getattr(provider, "_zue_testing_dashboard_provider_name", provider._description or provider._name)
        test_type_labels = dict(self.env["zue.testing.dashboard.line"]._fields["test_type"].selection)
        for spec in specs:
            tags = self._normalized_tags(spec)
            test_type = spec.get("test_type")
            if test_type not in test_type_labels:
                raise UserError(_(
                    "La prueba %(name)s debe declarar test_type explicitamente "
                    "('parametric' o 'process')."
                ) % {"name": spec.get("technical_name") or _("sin nombre")})
            normalized_spec = {
                "provider_model": provider._name,
                "provider_name": provider_name,
                "technical_name": spec["technical_name"],
                "module_name": spec.get("module_name") or provider_name,
                "summary": spec["summary"],
                "tags": tags,
                "test_type": test_type,
                "test_type_label": test_type_labels[test_type],
            }
            if spec.get("test_model"):
                normalized_spec["test_model"] = spec["test_model"]
            normalized.append(normalized_spec)
        return normalized

    def _specs_for_scope(self, specs, suite_scope):
        """Filtra specs por tag; all o valor vacio ejecuta todo el provider."""
        if not suite_scope or suite_scope == "all":
            return specs
        return [spec for spec in specs if suite_scope in spec.get("tags", [])]

    def _normalized_tags(self, spec):
        """Limpia tags duplicados y conserva compatibilidad con specs core antiguos."""
        tag_values = list(spec.get("tags") or [])
        if spec.get("core"):
            tag_values.append("core")
        tags = []
        for tag in tag_values:
            if tag and tag not in tags:
                tags.append(tag)
        return tags

    def _provider_scope_labels(self, provider):
        """Lee los labels de filtros definidos por el provider, si existen."""
        labels_method = getattr(provider, "_get_zue_testing_dashboard_scope_labels", None)
        if not labels_method:
            return {}
        return labels_method() or {}

    def _scopes_payload(self, specs, labels):
        """Construye las opciones del selector de filtros con sus conteos.

        Usa el orden de labels del provider (aunque no haya pruebas) y agrega tags
        declarados solo en specs. El filtro all queda al final.
        """
        spec_tags = {tag for spec in specs for tag in spec.get("tags", [])}
        tag_values = [
            tag for tag in labels
            if tag not in ("all", "core")
        ]
        for tag in sorted(spec_tags):
            if tag not in tag_values and tag != "core":
                tag_values.append(tag)
        scopes = []
        if "core" in spec_tags:
            scopes.append(self._scope_payload("core", labels, specs))
        for tag in tag_values:
            scopes.append(self._scope_payload(tag, labels, specs))
        scopes.append({
            "value": "all",
            "label": labels.get("all", _("Todas")),
            "count": len(specs),
        })
        return scopes

    def _scope_payload(self, tag, labels, specs):
        """Construye una opcion individual de filtro para el frontend."""
        return {
            "value": tag,
            "label": labels.get(tag, tag.replace("_", " ").title()),
            "count": len([spec for spec in specs if tag in spec.get("tags", [])]),
        }

    def _find_spec(self, provider, technical_name):
        """Localiza una spec normalizada por su nombre tecnico."""
        for spec in self._normalized_specs(provider, provider._get_zue_testing_dashboard_test_specs()):
            if spec["technical_name"] == technical_name:
                return spec
        return False


class ZueTestingDashboardLine(models.TransientModel):
    """Linea temporal con el resultado de una prueba ejecutada.

    Cada registro representa un caso visible en la tabla de resultados y queda
    asociado a la sesion transient que lo genero.
    """

    _name = "zue.testing.dashboard.line"
    _description = "Linea del panel de pruebas ZUE"
    _order = "sequence, id"

    session_id = fields.Many2one(
        comodel_name="zue.testing.dashboard.session",
        string="Sesion",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(string="Secuencia", default=10, readonly=True)
    provider_model = fields.Char(string="Modelo proveedor", readonly=True)
    provider_name = fields.Char(string="Proveedor", readonly=True)
    technical_name = fields.Char(string="Nombre tecnico", readonly=True)
    module_name = fields.Char(string="Origen", readonly=True)
    summary = fields.Char(string="Resumen", readonly=True)
    test_type = fields.Selection(selection=[("parametric", "Paramétrica"), ("process", "Proceso")], string="Tipo de prueba", readonly=True)
    status = fields.Selection(
        selection=[
            ("ok", "Correcto"),
            ("controlled", "Controlado"),
            ("failed", "Fallido"),
            ("skipped", "Omitido"),
        ],
        string="Estado",
        readonly=True,
    )
    message = fields.Char(string="Mensaje", readonly=True)
    functional_log = fields.Text(string="Log funcional", readonly=True)
    detail = fields.Text(string="Detalle", readonly=True)
    test_data = fields.Text(string="Datos de prueba", readonly=True)
    calculated_lines = fields.Text(string="Conceptos calculados", readonly=True)
    worked_days_lines = fields.Text(string="Dias trabajados", readonly=True)
    not_applied_lines = fields.Text(string="Reglas no aplicadas", readonly=True)
    obtained_info = fields.Text(string="Informacion del recibo", readonly=True)
    duration = fields.Float(string="Segundos", digits=(12, 3), readonly=True)

    def _splitResultDetail(self):
        """Separa log funcional y detalle tecnico almacenados en detail."""
        self.ensure_one()
        detail = self.detail or ""
        separator = TRACE_SEPARATOR
        if separator in detail:
            functional_log, technical_detail = detail.split(separator, 1)
            return functional_log.strip(), technical_detail.strip()
        if self.functional_log:
            if detail and detail != self.functional_log:
                return self.functional_log, detail
            return self.functional_log, ""
        if self.status == "ok":
            return detail, ""
        return "", detail

    def parseJsonListField(self, field_name):
        """Parsea un campo Text con lista JSON para la UI OWL."""
        raw_value = getattr(self, field_name, "") or ""
        if not raw_value:
            return []
        try:
            parsed = json.loads(raw_value)
            if isinstance(parsed, list):
                return parsed
        except (TypeError, ValueError, json.JSONDecodeError):
            return []
        return []

    def buildProcessResultPayload(self):
        """Serializa el resultado de proceso tal como lo consume la vista en vivo.

        El Historial reutiliza el mismo componente OWL, por lo que necesita los
        datos estructurados y no el texto tabulado.
        """
        self.ensure_one()
        if self.test_type != "process":
            return ""
        payload = {
            "sequence": self.sequence,
            "technical_name": self.technical_name or "",
            "test_type": self.test_type,
            "calculated_lines": self.parseJsonListField("calculated_lines"),
            "worked_days_lines": self.parseJsonListField("worked_days_lines"),
            "not_applied_lines": self.parseJsonListField("not_applied_lines"),
            "obtained_info": self.parseJsonListField("obtained_info"),
        }
        if not any(payload[key] for key in (
            "calculated_lines",
            "worked_days_lines",
            "not_applied_lines",
            "obtained_info",
        )):
            return ""
        return json.dumps(payload)

    def formatProcessResultText(self, field_name):
        """Convierte los datos de liquidacion en texto tabulado para el Historial."""
        self.ensure_one()
        records = self.parseJsonListField(field_name)
        if not records:
            return ""
        if field_name == "obtained_info":
            if (
                len(records) == 1
                and isinstance(records[0], dict)
                and records[0].get("layout") == "social_security"
            ):
                return self.formatSocialSecurityResultText(records[0])
            if (
                len(records) == 1
                and isinstance(records[0], dict)
                and records[0].get("layout") == "provisions"
            ):
                return self.formatProvisionsResultText(records[0])
            return "\n".join(
                "%s: %s" % (
                    item.get("label") or "-",
                    self.formatProcessResultCell(item.get("value"), monetary=isinstance(item.get("value"), (int, float))),
                )
                for item in records
                if isinstance(item, dict)
            )
        columns = PROCESS_RESULT_COLUMNS.get(field_name)
        if not columns:
            return ""
        rows = [[label for _key, label in columns]]
        for item in records:
            if not isinstance(item, dict):
                continue
            rows.append([
                self.formatProcessResultCell(
                    item.get(key),
                    monetary=key in PROCESS_RESULT_MONETARY_KEYS,
                )
                for key, _label in columns
            ])
        widths = [max(len(row[index]) for row in rows) for index in range(len(columns))]
        return "\n".join(
            "  ".join(cell.ljust(widths[index]) for index, cell in enumerate(row))
            for row in rows
        )

    def formatSocialSecurityResultText(self, payload):
        """Texto legible del resultado SS para el historial."""
        header_info = payload.get("header_info") or {}
        lines = [
            "Empleado: %s" % (payload.get("employee") or header_info.get("employee") or "-"),
            "Contrato: %s" % (payload.get("contract") or header_info.get("contract") or "-"),
            "Periodo: %s" % (payload.get("period") or header_info.get("period") or "-"),
            "Compania: %s" % (header_info.get("company") or "-"),
            "Lineas: %s" % (header_info.get("line_count") if header_info.get("line_count") is not None else "-"),
            "Tiempo: %s" % (header_info.get("time_process") or "-"),
            "Estado: %s" % (header_info.get("state_label") or payload.get("header_state") or "-"),
            "Cabecera: %s" % (payload.get("header") or header_info.get("header_name") or "-"),
        ]
        for segment in payload.get("segments") or []:
            if not isinstance(segment, dict):
                continue
            lines.append("")
            lines.append(segment.get("label") or "Tramo")
            for section_key, section_label in (
                ("info_days", "Info y dias"),
                ("health", "Salud"),
                ("pension", "Pension"),
                ("arp", "ARP"),
                ("parafiscales", "Parafiscales"),
                ("absence_dates", "Ausencia y fechas"),
            ):
                fields = segment.get(section_key) or []
                if not fields:
                    continue
                lines.append("  [%s]" % section_label)
                for field_row in fields:
                    if not isinstance(field_row, dict):
                        continue
                    value_type = field_row.get("value_type") or "text"
                    lines.append("    %s: %s" % (
                        field_row.get("label") or "-",
                        self.formatProcessResultCell(
                            field_row.get("value"),
                            monetary=value_type == "monetary",
                        ),
                    ))
        warnings = payload.get("warnings") or []
        if warnings:
            lines.append("")
            lines.append("[Advertencias]")
            for warning in warnings:
                if isinstance(warning, dict):
                    lines.append(
                        "  - %s | %s | %s"
                        % (
                            warning.get("employee") or "-",
                            warning.get("branch") or "-",
                            warning.get("description") or "-",
                        )
                    )
        accounting = payload.get("accounting") or False
        if isinstance(accounting, dict):
            lines.append("")
            lines.append("[Contabilizacion]")
            lines.append("  Asiento: %s" % (accounting.get("move_name") or "-"))
            lines.append("  Referencia: %s" % (accounting.get("move_ref") or "-"))
            lines.append("  Estado: %s" % (accounting.get("move_state") or "-"))
            lines.append("  Fecha: %s" % (accounting.get("move_date") or "-"))
            for process in accounting.get("processes") or []:
                if not isinstance(process, dict):
                    continue
                lines.append("  [%s]" % (process.get("label") or process.get("code") or "-"))
                for move_line in process.get("lines") or []:
                    if not isinstance(move_line, dict):
                        continue
                    lines.append(
                        "    %s | %s | D:%s C:%s"
                        % (
                            move_line.get("name") or "-",
                            move_line.get("account") or "-",
                            self.formatProcessResultCell(move_line.get("debit"), monetary=True),
                            self.formatProcessResultCell(move_line.get("credit"), monetary=True),
                        )
                    )
        return "\n".join(lines)

    def formatProvisionsResultText(self, payload):
        """Texto legible del resultado de provisiones para el historial."""
        header_info = payload.get("header_info") or {}
        lines = [
            "Empleado: %s" % (payload.get("employee") or header_info.get("employee") or "-"),
            "Contrato: %s" % (payload.get("contract") or header_info.get("contract") or "-"),
            "Periodo: %s" % (payload.get("period") or header_info.get("period") or "-"),
            "Compania: %s" % (header_info.get("company") or "-"),
            "Lineas: %s" % (header_info.get("line_count") if header_info.get("line_count") is not None else "-"),
            "Tiempo: %s" % (header_info.get("time_process") or "-"),
            "Estado: %s" % (header_info.get("state_label") or payload.get("header_state") or "-"),
            "Cabecera: %s" % (payload.get("header") or header_info.get("header_name") or "-"),
            "",
            "[Provisiones]",
        ]
        for row in payload.get("rows") or []:
            if not isinstance(row, dict):
                continue
            lines.append(
                "  %s | liquidado:%s | pagos:%s | a pagar:%s | provision mes:%s%s"
                % (
                    row.get("label") or row.get("code") or "-",
                    self.formatProcessResultCell(row.get("amount"), monetary=True),
                    self.formatProcessResultCell(row.get("value_payments"), monetary=True),
                    self.formatProcessResultCell(row.get("current_payable_value"), monetary=True),
                    self.formatProcessResultCell(row.get("value_balance"), monetary=True),
                    " (sin detalle)" if row.get("missing") else "",
                )
            )
            detail = row.get("detail") or {}
            if isinstance(detail, dict):
                for column_key, column_label in (
                    ("column_left", "Columna izquierda"),
                    ("column_right", "Columna derecha"),
                ):
                    fields = detail.get(column_key) or []
                    if not fields:
                        continue
                    lines.append("    [%s]" % column_label)
                    for field_row in fields:
                        if not isinstance(field_row, dict):
                            continue
                        value_type = field_row.get("value_type") or "text"
                        lines.append("      %s: %s" % (
                            field_row.get("label") or "-",
                            self.formatProcessResultCell(
                                field_row.get("value"),
                                monetary=value_type == "monetary",
                            ),
                        ))
        warnings = payload.get("warnings") or []
        if warnings:
            lines.append("")
            lines.append("[Advertencias]")
            for warning in warnings:
                if isinstance(warning, dict):
                    lines.append(
                        "  - %s | %s | %s"
                        % (
                            warning.get("employee") or "-",
                            warning.get("contract") or "-",
                            warning.get("description") or "-",
                        )
                    )
        accounting = payload.get("accounting") or False
        if isinstance(accounting, dict):
            lines.append("")
            lines.append("[Contabilizacion]")
            lines.append("  Asiento: %s" % (accounting.get("move_name") or "-"))
            lines.append("  Referencia: %s" % (accounting.get("move_ref") or "-"))
            lines.append("  Estado: %s" % (accounting.get("move_state") or "-"))
            lines.append("  Fecha: %s" % (accounting.get("move_date") or "-"))
            for process in accounting.get("processes") or []:
                if not isinstance(process, dict):
                    continue
                lines.append("  [%s]" % (process.get("label") or process.get("code") or "-"))
                for move_line in process.get("lines") or []:
                    if not isinstance(move_line, dict):
                        continue
                    lines.append(
                        "    %s | %s | D:%s C:%s"
                        % (
                            move_line.get("name") or "-",
                            move_line.get("account") or "-",
                            self.formatProcessResultCell(move_line.get("debit"), monetary=True),
                            self.formatProcessResultCell(move_line.get("credit"), monetary=True),
                        )
                    )
        return "\n".join(lines)

    def formatProcessResultCell(self, value, monetary=False):
        """Normaliza un valor de liquidacion para mostrarlo como texto."""
        if value is None or value is False or value == "":
            return "-"
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if monetary:
                return formatLang(
                    self.env,
                    float(value),
                    currency_obj=self.env.company.currency_id,
                )
            return formatLang(self.env, float(value), digits=2)
        return str(value)

    def _line_payload(self, source_labels=None):
        """Convierte una linea de resultado al formato que consume OWL.

        Aplica labels de origen cuando el provider quiere mostrar nombres mas
        claros que los identificadores tecnicos guardados.
        """
        self.ensure_one()
        source_labels = source_labels or {}
        functional_log, technical_detail = self._splitResultDetail()
        return {
            "id": self.id,
            "sequence": self.sequence,
            "provider_model": self.provider_model,
            "provider_name": self.provider_name,
            "technical_name": self.technical_name,
            "module_name": source_labels.get(self.module_name, self.module_name.replace(".py", "")),
            "summary": self.summary,
            "test_type": self.test_type or "",
            "test_type_label": dict(self._fields["test_type"].selection).get(self.test_type, ""),
            "status": self.status,
            "status_label": dict(self._fields["status"].selection).get(self.status, self.status),
            "message": self.message,
            "detail": technical_detail,
            "functional_log": functional_log,
            "test_data": self.test_data or "",
            "calculated_lines": self.parseJsonListField("calculated_lines"),
            "worked_days_lines": self.parseJsonListField("worked_days_lines"),
            "not_applied_lines": self.parseJsonListField("not_applied_lines"),
            "obtained_info": self.parseJsonListField("obtained_info"),
            "duration": self.duration,
        }
