# -*- coding: utf-8 -*-

import json

from odoo import _, models

from .functional_log_buffer import (
    SESSION_CTX_KEY,
    TEST_PARAMS_CTX_KEY,
    TRACE_SEPARATOR,
    appendFunctionalLogStep,
    getFunctionalLogText,
    isControlledConstraintErrorValue,
)


class ZueTestingDashboardTestProvider(models.AbstractModel):
    """Contrato base que deben heredar los modulos que publican pruebas.

    Este modelo no ejecuta escenarios por si mismo. Solo define los metodos
    que el adapter espera encontrar en cada provider instalado.
    """

    _name = "zue.testing.dashboard.test.provider"
    _description = "Proveedor de pruebas del panel ZUE"

    def _get_zue_testing_dashboard_test_specs(self):
        """Devuelve la lista de pruebas que este provider publica al adapter.

        Cada elemento debe ser un diccionario con el identificador tecnico,
        resumen funcional, origen visible y tags usados como filtros.
        """
        return []

    def _get_zue_testing_dashboard_scope_labels(self):
        """Devuelve los nombres visibles para los tags/filtros del provider.

        La clave del diccionario es el tag tecnico y el valor es el texto que
        se muestra en la interfaz. El tag all puede redefinir el label global.
        """
        return {}

    def _get_zue_testing_dashboard_source_labels(self):
        """Devuelve nombres visibles para las fuentes tecnicas de cada prueba.

        Sirve para traducir nombres internos de archivos, modelos o areas a un
        texto mas claro en la tabla de resultados.
        """
        return {}

    def _run_zue_testing_dashboard_test(self, technical_name):
        """Ejecuta una prueba concreta identificada por su nombre tecnico.

        Cada provider debe localizar la spec recibida y llamar al metodo real
        que crea data, ejecuta la accion y valida el resultado esperado.
        """
        raise NotImplementedError("Los proveedores de pruebas deben implementar _run_zue_testing_dashboard_test.")

    def getFunctionalLogSessionId(self):
        """Devuelve la sesion activa que coordina la ejecucion visual."""
        session_id = self.env.context.get(SESSION_CTX_KEY)
        return int(session_id) if session_id else False

    def getDashboardTestParams(self):
        """Devuelve los parametros opcionales enviados desde la UI para la prueba."""
        params = self.env.context.get(TEST_PARAMS_CTX_KEY) or {}
        return params if isinstance(params, dict) else {}

    def logFunctionalStep(self, description):
        """Registra un paso del flujo funcional ejecutado por la prueba."""
        session_id = self.getFunctionalLogSessionId()
        if session_id:
            appendFunctionalLogStep(session_id, description)

    def logFunctionalField(self, description, value=None, optional=False):
        """Registra un paso solo si el campo se utiliza en el escenario."""
        if optional and (value is None or value is False or value == ""):
            return
        self.logFunctionalStep(description)

    def isControlledConstraintError(self, error):
        """Identifica errores de restriccion SQL o validacion esperados del sistema.

        Cuando una prueba intenta crear un registro duplicado, el resultado debe
        clasificarse como controlado y no como fallo funcional.
        """
        return isControlledConstraintErrorValue(error)

    def raiseControlledBehavior(self, message):
        """Marca la prueba como controlada conservando el log funcional acumulado."""
        from .adapter_session import ZueTestingDashboardControlled

        session_id = self.getFunctionalLogSessionId()
        functional_log = getFunctionalLogText(session_id) if session_id else ""
        raise ZueTestingDashboardControlled(str(message), functional_log=functional_log)

    def serializeProcessPayload(self, payload):
        """Serializa listas/dicts de datos obtenidos de la liquidacion."""
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
        """Finaliza correctamente una simulacion completa de liquidacion."""
        from .adapter_session import ZueTestingDashboardProcessComplete

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
