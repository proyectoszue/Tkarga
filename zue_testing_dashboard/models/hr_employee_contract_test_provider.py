# -*- coding: utf-8 -*-

from odoo import _, api, models
from odoo.exceptions import UserError


class ZueHrEmployeeContractTestingDashboardProvider(models.AbstractModel):
    _name = "zue.testing.dashboard.hr.employee.contract.provider"
    _inherit = "zue.testing.dashboard.test.provider"
    _description = "Pruebas de empleados y contratos"
    _zue_testing_dashboard_module_key = "payroll"
    _zue_testing_dashboard_module_name = "Nómina"
    _zue_testing_dashboard_provider_name = "Empleados y contratos"
    _zue_testing_dashboard_provider_description = (
        "Pruebas de creación de empleados, contratos, conceptos fijos, cambios salariales y ausencias."
    )

    @api.model
    def _get_zue_testing_dashboard_test_specs(self):
        module_name = "zue_hr_employee"
        return [
            self.buildDashboardSpec(
                module_name,
                "test_create_employee",
                _("Crea/configura un empleado basico."),
                self.testCreateEmployee,
                tags=["employees"],
                test_model="hr.employee",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                module_name,
                "test_create_contract_version",
                _("Crea un contrato inicial como hr.version."),
                self.testCreateContractVersion,
                tags=["contracts"],
                test_model="hr.version",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                module_name,
                "test_create_contract_concept",
                _("Crea y aprueba un concepto fijo del contrato."),
                self.testCreateContractConcept,
                tags=["fixed_concepts"],
                test_model="hr.contract.concepts",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                module_name,
                "test_create_wage_change_version",
                _("Crea una nueva version contractual y valida el historial salarial."),
                self.testCreateWageChangeVersion,
                tags=["wage_changes"],
                test_model="hr.version",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                module_name,
                "test_update_contractual_modifications",
                _("Aplica cambios de cargo, jornada o sucursal sobre hr.version."),
                self.testUpdateContractualModifications,
                tags=["contractual_modifications"],
                test_model="hr.version",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                module_name,
                "test_terminate_contract_version",
                _("Valida el retiro/fecha de fin del contrato."),
                self.testTerminateContractVersion,
                tags=["termination"],
                test_model="hr.version",
                test_type="parametric",
            ),
            # self.buildDashboardSpec(
            #     module_name,
            #     "test_create_leave_draft",
            #     _("Crea una ausencia y la deja en borrador."),
            #     self.testCreateLeave,
            #     tags=["absences"],
            #     test_type="parametric",
            # ),
            # self.buildDashboardSpec(
            #     module_name,
            #     "test_create_leave_validate_real",
            #     _("Crea una ausencia y la valida con el flujo real."),
            #     self.testCreateLeave,
            #     tags=["absences"],
            #     test_type="parametric",
            # ),
            # self.buildDashboardSpec(
            #     module_name,
            #     "test_create_leave_validate_forced",
            #     _("Crea una ausencia y, si el flujo real falla, fuerza la validación."),
            #     self.testCreateLeave,
            #     tags=["absences"],
            #     test_type="parametric",
            # ),
            # self.buildDashboardSpec(
            #     module_name,
            #     "test_create_leave_incapacidad",
            #     _("Crea una incapacidad validada."),
            #     self.testCreateLeave,
            #     tags=["absences"],
            #     test_type="parametric",
            # ),
            # self.buildDashboardSpec(
            #     module_name,
            #     "test_create_leave_licencia_no_remunerada",
            #     _("Crea una licencia no remunerada validada."),
            #     self.testCreateLeave,
            #     tags=["absences"],
            #     test_type="parametric",
            # ),
            # self.buildDashboardSpec(
            #     module_name,
            #     "test_create_leave_inasistencia",
            #     _("Crea una inasistencia injustificada validada."),
            #     self.testCreateLeave,
            #     tags=["absences"],
            #     test_type="parametric",
            # ),
            # self.buildDashboardSpec(
            #     module_name,
            #     "test_create_leave_vacaciones",
            #     _("Crea vacaciones disfrutadas validadas."),
            #     self.testCreateLeave,
            #     tags=["absences"],
            #     test_type="parametric",
            # ),
        ]

    @api.model
    def _get_zue_testing_dashboard_scope_labels(self):
        return {
            "all": _("Todas"),
            "employees": _("Empleados"),
            "contracts": _("Contratos"),
            "fixed_concepts": _("Conceptos fijos"),
            "wage_changes": _("Cambios salariales"),
            "contractual_modifications": _("Modificaciones contractuales"),
            "termination": _("Terminacion de contrato"),
            # "absences": _("Ausencias"),
        }

    def _run_zue_testing_dashboard_test(self, technical_name):
        spec = self.findDashboardSpec(technical_name)
        if not spec:
            raise UserError(_("No se encontro la prueba solicitada: %s") % technical_name)
        cases = self.hrEmployeeContractCases()
        params = dict(self.getDashboardTestParams() or {})
        params["technical_name"] = technical_name
        method = getattr(cases, spec["method_name"])
        if spec.get("test_model") or spec.get("test_type") == "parametric":
            method(params)
            return
        method()

    def findDashboardSpec(self, technical_name):
        for spec in self._get_zue_testing_dashboard_test_specs():
            if spec["technical_name"] == technical_name:
                return spec
        return False

    def buildDashboardSpec(self, module_name, technical_name, summary, method, tags=None, test_model=None, test_type=None):
        return {
            "module_name": module_name,
            "technical_name": technical_name,
            "summary": summary,
            "method_name": method.__name__ if callable(method) else method,
            "tags": list(tags or []),
            "test_model": test_model,
            "test_type": test_type,
        }

    def hrEmployeeContractCases(self):
        from odoo.addons.zue_testing_dashboard.tests.test_hr_employee_contract import HrEmployeeContractCases

        return HrEmployeeContractCases(
            self.env,
            provider=self,
            session_id=self.getFunctionalLogSessionId(),
        )

    def testCreateEmployee(self):
        self.hrEmployeeContractCases().testCreateEmployee()

    def testCreateContractVersion(self):
        self.hrEmployeeContractCases().testCreateContractVersion()

    def testCreateWageChangeVersion(self):
        self.hrEmployeeContractCases().testCreateWageChangeVersion()

    def testCreateContractConcept(self):
        self.hrEmployeeContractCases().testCreateContractConcept()

    def testUpdateContractualModifications(self):
        self.hrEmployeeContractCases().testUpdateContractualModifications()

    def testTerminateContractVersion(self):
        self.hrEmployeeContractCases().testTerminateContractVersion()

    def testCreateLeave(self):
        self.hrEmployeeContractCases().testCreateLeave()
