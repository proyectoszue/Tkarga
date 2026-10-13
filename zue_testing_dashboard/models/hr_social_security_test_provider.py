# -*- coding: utf-8 -*-

from odoo import _, api, models


class ZueHrPeriodClosureTestingDashboardProvider(models.AbstractModel):
    _name = "zue.testing.dashboard.hr.social.security.provider"
    _inherit = "zue.testing.dashboard.hr.liq.mixin"
    _description = "Pruebas de cierres de periodo"
    _zue_testing_dashboard_module_key = "payroll"
    _zue_testing_dashboard_module_name = "Nómina"
    _zue_testing_dashboard_provider_name = "Cierres de periodo"
    _zue_testing_dashboard_provider_description = (
        "Cierres mensuales: seguridad social y provisiones de prestaciones."
    )

    @api.model
    def _get_zue_testing_dashboard_test_specs(self):
        return [
            self.buildDashboardSpec(
                "hr_payroll_social_security",
                "test_simulate_seguridad_social",
                _("Simula ejecución de seguridad social para un contrato."),
                self.testSimulateSeguridadSocial,
                tags=["seguridad_social"],
                test_type="process",
            ),
            self.buildDashboardSpec(
                "hr_provisions",
                "test_simulate_provisiones",
                _("Simula ejecución de provisiones para un contrato."),
                self.testSimulateProvisiones,
                tags=["provisiones"],
                test_type="process",
            ),
        ]

    @api.model
    def _get_zue_testing_dashboard_scope_labels(self):
        return {
            "seguridad_social": _("Seguridad Social"),
            "provisiones": _("Provisiones"),
            "all": _("Todas"),
        }

    @api.model
    def _get_zue_testing_dashboard_source_labels(self):
        return {
            "hr_payroll_social_security": _("Seguridad Social"),
            "hr_provisions": _("Provisiones"),
        }

    def testSimulateSeguridadSocial(self):
        self.payrollProcessCases().testSimulateSeguridadSocial()

    def testSimulateProvisiones(self):
        self.payrollProcessCases().testSimulateProvisiones()
