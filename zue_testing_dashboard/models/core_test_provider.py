# -*- coding: utf-8 -*-
# Core: contrato base que deben heredar todos los providers del panel.

import json

from odoo import _, models

from .core_functional_log_buffer import (
    SESSION_CTX_KEY,
    TEST_PARAMS_CTX_KEY,
    TRACE_SEPARATOR,
    appendFunctionalLogStep,
    getFunctionalLogText,
    isControlledConstraintErrorValue,
)


class ZueTestingDashboardTestProvider(models.AbstractModel):
    """Estándar del panel: API que cada provider de dominio debe cumplir."""

    _name = "zue.testing.dashboard.test.provider"
    _description = "Proveedor de pruebas del panel ZUE"

    def _get_zue_testing_dashboard_test_specs(self):
        """Catálogo de pruebas (lista de specs) que publica este provider."""
        return []

    def _get_zue_testing_dashboard_scope_labels(self):
        """Nombres visibles de los filtros (tags) del provider."""
        return {}

    def _get_zue_testing_dashboard_source_labels(self):
        """Nombres visibles para el origen/fuente de cada prueba."""
        return {}

    def _run_zue_testing_dashboard_test(self, technical_name):
        """Ejecuta una prueba por su nombre técnico (punto de entrada del Core)."""
        raise NotImplementedError("Los proveedores de pruebas deben implementar _run_zue_testing_dashboard_test.")

    def findDashboardSpec(self, technical_name):
        """Localiza una spec por technical_name; False si no existe."""
        for spec in self._get_zue_testing_dashboard_test_specs():
            if spec.get("technical_name") == technical_name:
                return spec
        return False

    def buildDashboardSpec(
        self,
        module_name,
        technical_name,
        summary,
        method,
        tags=None,
        test_model=None,
        test_type=None,
    ):
        """Arma el diccionario estándar de una prueba para el catálogo."""
        return {
            "module_name": module_name,
            "technical_name": technical_name,
            "summary": summary,
            "method_name": method.__name__ if callable(method) else method,
            "tags": list(tags or []),
            "test_model": test_model,
            "test_type": test_type,
        }

    def getFunctionalLogSessionId(self):
        """Id de sesión activa del panel (contexto de ejecución)."""
        session_id = self.env.context.get(SESSION_CTX_KEY)
        return int(session_id) if session_id else False

    def getDashboardTestParams(self):
        """Parámetros enviados desde la UI para la prueba en curso."""
        params = self.env.context.get(TEST_PARAMS_CTX_KEY) or {}
        return params if isinstance(params, dict) else {}

    def logFunctionalStep(self, description):
        """Agrega un paso al log funcional visible en el detalle."""
        session_id = self.getFunctionalLogSessionId()
        if session_id:
            appendFunctionalLogStep(session_id, description)

    def logFunctionalField(self, description, value=None, optional=False):
        """Log de campo; si optional y vacío, no registra."""
        if optional and (value is None or value is False or value == ""):
            return
        self.logFunctionalStep(description)

    def isControlledConstraintError(self, error):
        """True si el error es una restricción/validación esperada del sistema."""
        return isControlledConstraintErrorValue(error)

    def raiseControlledBehavior(self, message):
        """Marca la prueba como controlada (no fallo) y conserva el log."""
        from .core_adapter_session import ZueTestingDashboardControlled

        session_id = self.getFunctionalLogSessionId()
        functional_log = getFunctionalLogText(session_id) if session_id else ""
        raise ZueTestingDashboardControlled(str(message), functional_log=functional_log)

    def serializeProcessPayload(self, payload):
        """Convierte payload de proceso a JSON texto para persistirlo."""
        if payload is None:
            return ""
        if isinstance(payload, str):
            return payload
        return json.dumps(payload, ensure_ascii=False)

    def completeProcessTest(
        self,
        calculated_lines=None,
        worked_days_lines=None,
        not_applied_lines=None,
        obtained_info=None,
        message=None,
    ):
        """Cierra OK una prueba tipo process y entrega tablas al viewer."""
        from .core_adapter_session import ZueTestingDashboardProcessComplete

        session_id = self.getFunctionalLogSessionId()
        functional_log = getFunctionalLogText(session_id) if session_id else ""
        raise ZueTestingDashboardProcessComplete(
            status="ok",
            message=message or _("Proceso simulado correctamente."),
            functional_log=functional_log,
            calculated_lines=self.serializeProcessPayload(calculated_lines or []),
            worked_days_lines=self.serializeProcessPayload(worked_days_lines or []),
            not_applied_lines=self.serializeProcessPayload(not_applied_lines or []),
            obtained_info=self.serializeProcessPayload(obtained_info or []),
        )
