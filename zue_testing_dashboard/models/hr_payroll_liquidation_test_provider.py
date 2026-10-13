# -*- coding: utf-8 -*-

from odoo import _, api, models
from odoo.exceptions import UserError


class ZueHrPayrollLiquidationTestingDashboardMixin(models.AbstractModel):
    """Helpers compartidos por los grupos de procesos de liquidación."""

    _name = "zue.testing.dashboard.hr.liq.mixin"
    _inherit = "zue.testing.dashboard.test.provider"
    _description = "Mixin de procesos de liquidación del panel de pruebas"

    def _run_zue_testing_dashboard_test(self, technical_name):
        spec = self.findDashboardSpec(technical_name)
        if not spec:
            raise UserError(_("No se encontro la prueba solicitada: %s") % technical_name)
        cases = self.payrollProcessCases()
        params = self.getDashboardTestParams()
        method = getattr(cases, spec["method_name"])
        if spec.get("test_type") == "process":
            method(params)
            return
        method()

    def findDashboardSpec(self, technical_name):
        for spec in self._get_zue_testing_dashboard_test_specs():
            if spec["technical_name"] == technical_name:
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
        return {
            "module_name": module_name,
            "technical_name": technical_name,
            "summary": summary,
            "method_name": method.__name__ if callable(method) else method,
            "tags": list(tags or []),
            "test_model": test_model,
            "test_type": test_type,
        }

    def payrollProcessCases(self):
        from odoo.addons.zue_testing_dashboard.tests.test_hr_payroll_process import HrPayrollProcessCases

        return HrPayrollProcessCases(
            self.env,
            provider=self,
            session_id=self.getFunctionalLogSessionId(),
        )


class ZueHrPayrollLiquidationGeneralTestingDashboardProvider(models.AbstractModel):
    _name = "zue.testing.dashboard.hr.liq.general.provider"
    _inherit = "zue.testing.dashboard.hr.liq.mixin"
    _description = "Pruebas de procesos de liquidación General"
    _zue_testing_dashboard_module_key = "payroll"
    _zue_testing_dashboard_module_name = "Nómina"
    _zue_testing_dashboard_provider_name = "Procesos de liquidación General"
    _zue_testing_dashboard_provider_description = (
        "Liquidaciones generales: nómina periódica, liquidación de contrato y nómina independiente."
    )

    @api.model
    def _get_zue_testing_dashboard_test_specs(self):
        return [
            self.buildDashboardSpec(
                "zue_hr_payroll",
                "test_simulate_periodic_payroll",
                _("Simula liquidación de nómina periódica."),
                self.testSimulatePeriodicPayroll,
                tags=["periodic_payroll"],
                test_type="process",
            ),
            self.buildDashboardSpec(
                "zue_hr_payroll",
                "test_simulate_liquidacion_contrato",
                _("Simula liquidación de contrato."),
                self.testSimulateLiquidacionContrato,
                tags=["contract_liquidation"],
                test_type="process",
            ),
            self.buildDashboardSpec(
                "zue_hr_payroll",
                "test_simulate_nomina_independiente",
                _("Simula liquidación de nómina independiente."),
                self.testSimulateNominaIndependiente,
                tags=["independent_payroll"],
                test_type="process",
            ),
        ]

    @api.model
    def _get_zue_testing_dashboard_scope_labels(self):
        return {
            "periodic_payroll": _("Nómina periódica"),
            "contract_liquidation": _("Liquidación de contrato"),
            "independent_payroll": _("Nómina independiente"),
            "all": _("Todas"),
        }

    def testSimulatePeriodicPayroll(self):
        self.payrollProcessCases().testSimulatePeriodicPayroll()

    def testSimulateLiquidacionContrato(self):
        self.payrollProcessCases().testSimulateLiquidacionContrato()

    def testSimulateNominaIndependiente(self):
        self.payrollProcessCases().testSimulateNominaIndependiente()


class ZueHrPayrollLiquidationSocialBenefitsTestingDashboardProvider(models.AbstractModel):
    _name = "zue.testing.dashboard.hr.liq.benefits.provider"
    _inherit = "zue.testing.dashboard.hr.liq.mixin"
    _description = "Pruebas de Liquidación Prestaciones Sociales"
    _zue_testing_dashboard_module_key = "payroll"
    _zue_testing_dashboard_module_name = "Nómina"
    _zue_testing_dashboard_provider_name = "Liquidación Prestaciones Sociales"
    _zue_testing_dashboard_provider_description = (
        "Prestaciones sociales: prima, cesantías, intereses de cesantías y vacaciones."
    )

    @api.model
    def _get_zue_testing_dashboard_test_specs(self):
        return [
            self.buildDashboardSpec(
                "zue_hr_payroll",
                "test_simulate_prima",
                _("Simula liquidación de prima."),
                self.testSimulatePrima,
                tags=["prima"],
                test_type="process",
            ),
            self.buildDashboardSpec(
                "zue_hr_payroll",
                "test_simulate_cesantias",
                _("Simula liquidación de cesantías."),
                self.testSimulateCesantias,
                tags=["cesantias"],
                test_type="process",
            ),
            self.buildDashboardSpec(
                "zue_hr_payroll",
                "test_simulate_intereses_cesantias",
                _("Simula liquidación de intereses de cesantías."),
                self.testSimulateInteresesCesantias,
                tags=["intereses_cesantias"],
                test_type="process",
            ),
            self.buildDashboardSpec(
                "zue_hr_payroll",
                "test_simulate_vacaciones",
                _("Simula liquidación de vacaciones."),
                self.testSimulateVacaciones,
                tags=["vacaciones"],
                test_type="process",
            ),
        ]

    @api.model
    def _get_zue_testing_dashboard_scope_labels(self):
        return {
            "prima": _("Prima"),
            "cesantias": _("Cesantías"),
            "intereses_cesantias": _("Intereses de cesantías"),
            "vacaciones": _("Vacaciones"),
            "all": _("Todas"),
        }

    def testSimulatePrima(self):
        self.payrollProcessCases().testSimulatePrima()

    def testSimulateCesantias(self):
        self.payrollProcessCases().testSimulateCesantias()

    def testSimulateInteresesCesantias(self):
        self.payrollProcessCases().testSimulateInteresesCesantias()

    def testSimulateVacaciones(self):
        self.payrollProcessCases().testSimulateVacaciones()
