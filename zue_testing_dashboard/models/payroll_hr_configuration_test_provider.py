# -*- coding: utf-8 -*-
# Payroll: provider de pruebas de configuración HR.

from odoo import _, api, models
from odoo.exceptions import UserError


class ZueHrConfigurationTestingDashboardProvider(models.AbstractModel):
    _name = "zue.testing.dashboard.hr.configuration.provider"
    _inherit = "zue.testing.dashboard.test.provider"
    _description = "Pruebas de configuracion HR"
    _zue_testing_dashboard_module_key = "payroll"
    _zue_testing_dashboard_module_name = "Nómina"
    _zue_testing_dashboard_provider_name = "Configuración HR"
    _zue_testing_dashboard_provider_description = (
        "Pruebas de creacion para la parametrizacion de nomina y recursos humanos."
    )

    @api.model
    def _get_zue_testing_dashboard_test_specs(self):
        module_name = "zue_hr_employee"
        return [
            self.buildDashboardSpec(
                module_name,
                "test_create_contribution_register",
                _("Crea un tipo de entidad EPS."),
                self.testCreateContributionRegister,
                tags=["contribution_register"],
                test_model="hr.contribution.register",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                module_name,
                "test_create_employee_entity",
                _("Crea una entidad asociada a un tercero y un tipo EPS."),
                self.testCreateEmployeeEntity,
                tags=["employee_entities"],
                test_model="hr.employee.entities",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                module_name,
                "test_create_tipo_cotizante",
                _("Crea un tipo de cotizante."),
                self.testCreateTipoCotizante,
                tags=["tipo_cotizante"],
                test_model="hr.tipo.cotizante",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                module_name,
                "test_create_subtipo_cotizante",
                _("Crea un subtipo de cotizante."),
                self.testCreateSubtipoCotizante,
                tags=["subtipo_cotizante"],
                test_model="hr.subtipo.cotizante",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                module_name,
                "test_create_parameterization_contributors",
                _("Crea una parametrizacion de cotizantes."),
                self.testCreateParameterizationContributors,
                tags=["parameterization_contributors"],
                test_model="hr.parameterization.of.contributors",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                module_name,
                "test_create_job_position",
                _("Crea un puesto de trabajo."),
                self.testCreateJobPosition,
                tags=["job_position"],
                test_model="hr.job",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                "hr_skills",
                "test_create_skill_type",
                _("Crea un tipo de habilidad."),
                self.testCreateSkillType,
                tags=["skill_type"],
                test_model="hr.skill.type",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                "zue_erp",
                "test_create_holiday",
                _("Crea un dia festivo."),
                self.testCreateHoliday,
                tags=["holidays"],
                test_model="zue.holidays",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                "zue_hr_payroll",
                "test_create_overtime_type",
                _("Crea un tipo de horas extra."),
                self.testCreateOvertimeType,
                tags=["overtime_type"],
                test_model="hr.type.overtime",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                "zue_hr_employee",
                "test_annual_parameters_basics",
                _("Parametriza la pestaña Básicos de parámetros anuales."),
                self.testAnnualParametersBasics,
                tags=["annual_parameters"],
                test_model="hr.annual.parameters",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                "zue_hr_employee",
                "test_annual_parameters_social_security",
                _("Parametriza la pestaña Seguridad Social de parámetros anuales."),
                self.testAnnualParametersSocialSecurity,
                tags=["annual_parameters"],
                test_model="hr.annual.parameters",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                "zue_hr_employee",
                "test_annual_parameters_tax",
                _("Parametriza la pestaña Tributario de parámetros anuales."),
                self.testAnnualParametersTax,
                tags=["annual_parameters"],
                test_model="hr.annual.parameters",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                "zue_hr_employee",
                "test_annual_parameters_public",
                _("Parametriza la pestaña Públicos de parámetros anuales."),
                self.testAnnualParametersPublic,
                tags=["annual_parameters"],
                test_model="hr.annual.parameters",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                "zue_hr_employee",
                "test_annual_parameters_upc",
                _("Parametriza la pestaña UPC de parámetros anuales."),
                self.testAnnualParametersUpc,
                tags=["annual_parameters"],
                test_model="hr.annual.parameters",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                "zue_hr_employee",
                "test_annual_parameters_certificate",
                _("Parametriza la pestaña Certificado de Ingresos y Retenciones de parámetros anuales."),
                self.testAnnualParametersCertificate,
                tags=["annual_parameters"],
                test_model="hr.annual.parameters",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                "zue_hr_employee",
                "test_annual_parameters_fds",
                _("Parametriza la pestaña Fondo de solidaridad y subsistencia de parámetros anuales."),
                self.testAnnualParametersFds,
                tags=["annual_parameters"],
                test_model="hr.annual.parameters",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                "zue_hr_employee",
                "test_create_types_employee",
                _("Crea un tipo de empleado."),
                self.testCreateTypesEmployee,
                tags=["types_employee"],
                test_model="hr.types.employee",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                "zue_hr_employee",
                "test_create_contract_risk",
                _("Crea un riesgo profesional."),
                self.testCreateContractRisk,
                tags=["contract_risk"],
                test_model="hr.contract.risk",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                "zue_erp",
                "test_create_ciiu",
                _("Crea un CIIU."),
                self.testCreateCiiu,
                tags=["ciiu"],
                test_model="zue.ciiu",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                "zue_hr_employee",
                "test_create_economic_activity_level_risk",
                _("Crea una actividad económica por nivel de riesgo."),
                self.testCreateEconomicActivityLevelRisk,
                tags=["economic_activity_level_risk"],
                test_model="zue.economic.activity.level.risk",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                "zue_hr_employee",
                "test_create_non_eps_contribution_registers",
                _("Crea tipos de entidad pensión, caja, cesantías y ARL."),
                self.testCreateNonEpsContributionRegisters,
                tags=["contribution_register"],
                test_model="hr.contribution.register",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                "zue_hr_employee",
                "test_create_non_eps_employee_entities",
                _("Crea entidades de pensión, caja, cesantías y ARL."),
                self.testCreateNonEpsEmployeeEntities,
                tags=["employee_entities"],
                test_model="hr.employee.entities",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                "zue_erp",
                "test_create_type_thirdparty_funcionario",
                _("Crea el tipo de tercero Funcionario / Contratista."),
                self.testCreateTypeThirdpartyFuncionario,
                tags=["type_thirdparty"],
                test_model="zue.type_thirdparty",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                "zue_hr_payroll",
                "test_create_payroll_structure",
                _("Crea una estructura salarial de nómina."),
                self.testCreatePayrollStructure,
                tags=["payroll_structure"],
                test_model="hr.payroll.structure",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                "zue_hr_payroll",
                "test_create_salary_rule",
                _("Crea una regla salarial mínima."),
                self.testCreateSalaryRule,
                tags=["salary_rule"],
                test_model="hr.salary.rule",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                "zue_hr_employee",
                "test_create_leave_type",
                _("Crea un tipo de ausencia."),
                self.testCreateLeaveType,
                tags=["leave_type"],
                test_model="hr.leave.type",
                test_type="parametric",
            ),
            self.buildDashboardSpec(
                "zue_hr_payroll",
                "test_create_calculation_rtefte_ordinary",
                _("Crea un rango de retención en la fuente ordinaria."),
                self.testCreateCalculationRtefteOrdinary,
                tags=["rtefte_ordinary"],
                test_model="hr.calculation.rtefte.ordinary",
                test_type="parametric",
            ),
        ]

    @api.model
    def _get_zue_testing_dashboard_scope_labels(self):
        return {
            "all": _("Todas"),
            "contribution_register": _("Tipos de entidades"),
            "employee_entities": _("Entidades"),
            "tipo_cotizante": _("Tipos de cotizante"),
            "subtipo_cotizante": _("Subtipos de cotizante"),
            "parameterization_contributors": _("Parametrizacion Cotizantes"),
            "job_position": _("Puestos de trabajo"),
            "skill_type": _("Tipos de habilidad"),
            "holidays": _("Dias Festivos"),
            "overtime_type": _("Tipos de horas extra"),
            "annual_parameters": _("Parámetros anuales"),
            "types_employee": _("Tipos de empleado"),
            "contract_risk": _("Riesgos profesionales"),
            "ciiu": _("CIIU"),
            "economic_activity_level_risk": _("Actividad económica por riesgo"),
            "type_thirdparty": _("Tipos de tercero"),
            "payroll_structure": _("Estructuras salariales"),
            "salary_rule": _("Reglas salariales"),
            "leave_type": _("Tipos de ausencia"),
            "rtefte_ordinary": _("Retención en la fuente"),
        }

    def _run_zue_testing_dashboard_test(self, technical_name):
        spec = self.findDashboardSpec(technical_name)
        if not spec:
            raise UserError(_("No se encontro la prueba solicitada: %s") % technical_name)
        cases = self.hrConfigurationCases()
        params = self.getDashboardTestParams()
        method = getattr(cases, spec["method_name"])
        if spec.get("test_model"):
            method(params)
            return
        method()

    def hrConfigurationCases(self):
        from odoo.addons.zue_testing_dashboard.tests.payroll_test_hr_configuration import HrConfigurationCases

        return HrConfigurationCases(
            self.env,
            provider=self,
            session_id=self.getFunctionalLogSessionId(),
        )

    def testCreateContributionRegister(self):
        self.hrConfigurationCases().testCreateContributionRegister()

    def testCreateEmployeeEntity(self):
        self.hrConfigurationCases().testCreateEmployeeEntity()

    def testCreateTipoCotizante(self):
        self.hrConfigurationCases().testCreateTipoCotizante()

    def testCreateSubtipoCotizante(self):
        self.hrConfigurationCases().testCreateSubtipoCotizante()

    def testCreateParameterizationContributors(self):
        self.hrConfigurationCases().testCreateParameterizationContributors()

    def testCreateJobPosition(self):
        self.hrConfigurationCases().testCreateJobPosition()

    def testCreateSkillType(self):
        self.hrConfigurationCases().testCreateSkillType()

    def testCreateHoliday(self):
        self.hrConfigurationCases().testCreateHoliday()

    def testCreateOvertimeType(self):
        self.hrConfigurationCases().testCreateOvertimeType()

    def testAnnualParametersBasics(self):
        self.hrConfigurationCases().testAnnualParametersBasics()

    def testAnnualParametersSocialSecurity(self):
        self.hrConfigurationCases().testAnnualParametersSocialSecurity()

    def testAnnualParametersTax(self):
        self.hrConfigurationCases().testAnnualParametersTax()

    def testAnnualParametersPublic(self):
        self.hrConfigurationCases().testAnnualParametersPublic()

    def testAnnualParametersUpc(self):
        self.hrConfigurationCases().testAnnualParametersUpc()

    def testAnnualParametersCertificate(self):
        self.hrConfigurationCases().testAnnualParametersCertificate()

    def testAnnualParametersFds(self):
        self.hrConfigurationCases().testAnnualParametersFds()

    def testCreateTypesEmployee(self):
        self.hrConfigurationCases().testCreateTypesEmployee()

    def testCreateContractRisk(self):
        self.hrConfigurationCases().testCreateContractRisk()

    def testCreateCiiu(self):
        self.hrConfigurationCases().testCreateCiiu()

    def testCreateEconomicActivityLevelRisk(self):
        self.hrConfigurationCases().testCreateEconomicActivityLevelRisk()

    def testCreateNonEpsContributionRegisters(self):
        self.hrConfigurationCases().testCreateNonEpsContributionRegisters()

    def testCreateNonEpsEmployeeEntities(self):
        self.hrConfigurationCases().testCreateNonEpsEmployeeEntities()

    def testCreateTypeThirdpartyFuncionario(self):
        self.hrConfigurationCases().testCreateTypeThirdpartyFuncionario()

    def testCreatePayrollStructure(self):
        self.hrConfigurationCases().testCreatePayrollStructure()

    def testCreateSalaryRule(self):
        self.hrConfigurationCases().testCreateSalaryRule()

    def testCreateLeaveType(self):
        self.hrConfigurationCases().testCreateLeaveType()

    def testCreateCalculationRtefteOrdinary(self):
        self.hrConfigurationCases().testCreateCalculationRtefteOrdinary()
