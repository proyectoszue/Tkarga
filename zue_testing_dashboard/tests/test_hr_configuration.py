# -*- coding: utf-8 -*-

from datetime import date

from odoo import _
from odoo.tests.common import TransactionCase, tagged


class HrConfigurationCases:
    """Escenarios de Configuracion HR compartidos por el panel y TransactionCase."""

    def __init__(self, env, provider=None, session_id=None):
        self.env = env
        self.provider = provider
        self.session_id = session_id

    def hasDashboardProvider(self):
        """Indica si el escenario corre desde el panel visual.

        El provider es un AbstractModel sin ids, por lo que su valor booleano es
        False y no puede evaluarse con `if self.provider:`.
        """
        return self.provider is not None

    def logFunctionalStep(self, description):
        from odoo.addons.zue_testing_dashboard.models.functional_log_buffer import appendFunctionalLogStep

        session_id = self.session_id
        if not session_id and self.hasDashboardProvider():
            session_id = self.provider.getFunctionalLogSessionId()
        if session_id:
            appendFunctionalLogStep(session_id, description)

    def logFunctionalField(self, description, value=None, optional=False):
        if optional and (value is None or value is False or value == ""):
            return
        self.logFunctionalStep(description)

    def isDashboardConstraintError(self, error):
        """Replica la deteccion del provider para TransactionCase sin sesion visual."""
        from odoo.addons.zue_testing_dashboard.models.functional_log_buffer import isControlledConstraintErrorValue

        if self.hasDashboardProvider():
            return self.provider.isControlledConstraintError(error)
        return isControlledConstraintErrorValue(error)

    def createOrControlled(self, callback, controlled_message):
        """Ejecuta una creacion y clasifica restricciones SQL como controladas.

        Si el registro se crea correctamente, retorna el resultado. Si el sistema
        bloquea por unicidad, la prueba visual queda en estado controlado.
        """
        try:
            result = callback()
            self.env.flush_all()
            return result
        except Exception as error:
            if not self.isDashboardConstraintError(error):
                raise
            self.logFunctionalStep(controlled_message)
            if self.hasDashboardProvider():
                self.provider.raiseControlledBehavior(str(error))
            raise error

    def createDashboardRecord(self, model_name, values, controlled_message):
        """Crea un registro del escenario aplicando la regla createOrControlled."""
        return self.createOrControlled(
            lambda: self.getDashboardModel(model_name).create(values),
            controlled_message,
        )

    def getDashboardModel(self, model_name):
        # sudo: required to create configuration records during dashboard test execution
        return self.env[model_name].sudo()

    def getAnnualParametersRequiredValues(self, year):
        return {
            "year": year,
            "smmlv_monthly": 1300000.0,
            "transportation_assistance_monthly": 162000.0,
            "porc_integral_salary": 70,
            "hours_daily": 8.0,
            "hours_weekly": 56.0,
            "hours_fortnightly": 120.0,
            "hours_monthly": 240.0,
            "value_porc_health_company": 8.5,
            "value_porc_health_employee": 4.0,
            "value_porc_health_employee_foreign": 4.0,
            "value_porc_pension_company": 12.0,
            "value_porc_pension_employee": 4.0,
            "value_porc_compensation_box_company": 4.0,
            "value_porc_sena_company": 2.0,
            "value_porc_icbf_company": 3.0,
            "value_porc_provision_bonus": 8.33,
            "value_porc_provision_cesantias": 8.33,
            "value_porc_provision_intcesantias": 1.0,
            "value_porc_provision_vacation": 4.17,
            "value_porc_statute_1395": 40,
            "value_uvt": 47000.0,
            "value_top_source_retention": 95.0,
            "value_porc_increment_smlv": 10.0,
            "value_porc_ipc": 5.0,
        }

    def createAnnualParametersRecord(self, year, extra_values=None, input_values=None):
        values = self.getAnnualParametersRequiredValues(year)
        if extra_values:
            values.update(extra_values)
        values.update(self.buildValuesFromTestParams("hr.annual.parameters", input_values))
        return self.createDashboardRecord(
            "hr.annual.parameters",
            values,
            _("Validar restriccion de unicidad del ano de parametros anuales."),
        )

    def testCreateContributionRegister(self, input_values=None):
        self.logFunctionalStep(_("Abrir el formulario de tipos de entidades."))
        values = self.buildValuesFromTestParams("hr.contribution.register", input_values)
        values.setdefault("name", "EPS prueba dashboard")
        values.setdefault("type_entities", "eps")
        self.logFunctionalStep(_("Asignar nombre de la entidad."))
        self.logFunctionalStep(_("Seleccionar el tipo de entidad."))
        record = self.createDashboardRecord(
            "hr.contribution.register",
            values,
            _("Validar restriccion de unicidad del tipo de entidad."),
        )
        self.logFunctionalStep(_("Guardar el registro."))
        if not record.id or record.type_entities != values["type_entities"]:
            raise AssertionError(_("No se creo correctamente el tipo de entidad."))
        self.logFunctionalStep(_("Validar la creacion de la entidad."))
        return record

    def testCreateEmployeeEntity(self, input_values=None):
        self.logFunctionalStep(_("Abrir el formulario de entidades."))
        values = self.buildValuesFromTestParams("hr.employee.entities", input_values)
        if not values.get("types_entities"):
            entity_type = self.createDashboardRecord(
                "hr.contribution.register",
                {
                    "name": "EPS entidad dashboard prueba",
                    "type_entities": "eps",
                },
                _("Validar restriccion de unicidad del tipo de entidad."),
            )
            values["types_entities"] = [(6, 0, entity_type.ids)]
        else:
            entity_type = False
        if not values.get("partner_id"):
            self.logFunctionalStep(_("Crear o seleccionar el tercero asociado a la entidad."))
            partner = self.getDashboardModel("res.partner").create({"name": "Sanitas dashboard prueba"})
            values["partner_id"] = partner.id
        self.logFunctionalStep(_("Asignar el tercero a la entidad."))
        self.logFunctionalStep(_("Seleccionar el tipo de entidad."))
        entity = self.createDashboardRecord(
            "hr.employee.entities",
            values,
            _("Validar restriccion de unicidad de la entidad por tercero."),
        )
        self.logFunctionalStep(_("Guardar el registro."))
        if not entity.id:
            raise AssertionError(_("No se creo correctamente la entidad."))
        if entity_type and entity_type not in entity.types_entities:
            raise AssertionError(_("No se creo correctamente la entidad."))
        self.logFunctionalStep(_("Validar la creacion de la entidad."))
        return entity

    def testCreateTipoCotizante(self, input_values=None):
        self.logFunctionalStep(_("Abrir el formulario de tipos de cotizante."))
        values = self.buildValuesFromTestParams("hr.tipo.cotizante", input_values)
        values.setdefault("code", "TC99")
        values.setdefault("name", "Tipo cotizante dashboard prueba")
        self.logFunctionalStep(_("Asignar codigo del tipo de cotizante."))
        self.logFunctionalStep(_("Asignar nombre del tipo de cotizante."))
        record = self.createDashboardRecord(
            "hr.tipo.cotizante",
            values,
            _("Validar restriccion de creacion del tipo de cotizante."),
        )
        self.logFunctionalStep(_("Guardar el registro."))
        if not record.id or record.code != values["code"]:
            raise AssertionError(_("No se creo correctamente el tipo de cotizante."))
        self.logFunctionalStep(_("Validar la creacion del tipo de cotizante."))
        return record

    def testCreateSubtipoCotizante(self, input_values=None):
        self.logFunctionalStep(_("Abrir el formulario de subtipos de cotizante."))
        values = self.buildValuesFromTestParams("hr.subtipo.cotizante", input_values)
        values.setdefault("code", "SC99")
        values.setdefault("name", "Subtipo cotizante dashboard prueba")
        self.logFunctionalStep(_("Asignar codigo del subtipo de cotizante."))
        self.logFunctionalStep(_("Asignar nombre del subtipo de cotizante."))
        self.logFunctionalField(
            _("Marcar que no aporta pension."),
            values.get("not_contribute_pension"),
            optional=True,
        )
        record = self.createDashboardRecord(
            "hr.subtipo.cotizante",
            values,
            _("Validar restriccion de creacion del subtipo de cotizante."),
        )
        self.logFunctionalStep(_("Guardar el registro."))
        if not record.id or record.name != values["name"]:
            raise AssertionError(_("No se creo correctamente el subtipo de cotizante."))
        self.logFunctionalStep(_("Validar la creacion del subtipo de cotizante."))
        return record

    def testCreateParameterizationContributors(self, input_values=None):
        self.logFunctionalStep(_("Abrir el formulario de parametrizacion de cotizantes."))
        values = self.buildValuesFromTestParams("hr.parameterization.of.contributors", input_values)
        if not values.get("type_of_contributor"):
            contributor_type = self.getDashboardModel("hr.tipo.cotizante").create({
                "code": "PC99",
                "name": "Tipo cotizante parametrizacion dashboard",
            })
            values["type_of_contributor"] = contributor_type.id
        else:
            contributor_type = self.getDashboardModel("hr.tipo.cotizante").browse(values["type_of_contributor"])
        if not values.get("contributor_subtype"):
            contributor_subtype = self.getDashboardModel("hr.subtipo.cotizante").create({
                "code": "PS99",
                "name": "Subtipo cotizante parametrizacion dashboard",
            })
            values["contributor_subtype"] = contributor_subtype.id
        values.setdefault("liquidated_eps_employee", True)
        values.setdefault("liquidate_employee_pension", True)
        self.logFunctionalStep(_("Seleccionar el tipo de cotizante."))
        self.logFunctionalStep(_("Seleccionar el subtipo de cotizante."))
        self.logFunctionalField(_("Marcar liquidacion EPS empleado."), values.get("liquidated_eps_employee"), optional=True)
        self.logFunctionalField(_("Marcar liquidacion pension empleado."), values.get("liquidate_employee_pension"), optional=True)
        record = self.createDashboardRecord(
            "hr.parameterization.of.contributors",
            values,
            _("Validar restriccion de unicidad de la parametrizacion de cotizantes."),
        )
        self.logFunctionalStep(_("Guardar el registro."))
        if not record.id or record.type_of_contributor != contributor_type:
            raise AssertionError(_("No se creo correctamente la parametrizacion de cotizantes."))
        self.logFunctionalStep(_("Validar la creacion de la parametrizacion."))
        return record

    def testCreateJobPosition(self, input_values=None):
        self.logFunctionalStep(_("Abrir el formulario de puestos de trabajo."))
        values = self.buildValuesFromTestParams("hr.job", input_values)
        values.setdefault("name", "Puesto dashboard prueba")
        self.logFunctionalStep(_("Asignar nombre del puesto de trabajo."))
        self.logFunctionalField(_("Registrar funciones del puesto."), values.get("z_functions"), optional=True)
        record = self.createDashboardRecord(
            "hr.job",
            values,
            _("Validar restriccion de creacion del puesto de trabajo."),
        )
        self.logFunctionalStep(_("Guardar el registro."))
        if not record.id or record.name != values["name"]:
            raise AssertionError(_("No se creo correctamente el puesto de trabajo."))
        self.logFunctionalStep(_("Validar la creacion del puesto de trabajo."))
        return record

    def testCreateSkillType(self, input_values=None):
        self.logFunctionalStep(_("Abrir el formulario de tipos de habilidad."))
        values = self.buildValuesFromTestParams("hr.skill.type", input_values)
        values.setdefault("name", "Tipo habilidad dashboard prueba")
        self.logFunctionalStep(_("Asignar nombre del tipo de habilidad."))
        record = self.createDashboardRecord(
            "hr.skill.type",
            values,
            _("Validar restriccion de creacion del tipo de habilidad."),
        )
        self.logFunctionalStep(_("Guardar el registro."))
        if not record.id or record.name != values["name"]:
            raise AssertionError(_("No se creo correctamente el tipo de habilidad."))
        self.logFunctionalStep(_("Validar la creacion del tipo de habilidad."))
        return record

    def testCreateHoliday(self, input_values=None):
        self.logFunctionalStep(_("Abrir el formulario de dias festivos."))
        values = self.buildValuesFromTestParams("zue.holidays", input_values)
        values.setdefault("name", "Festivo dashboard prueba")
        values.setdefault("date", date(2099, 12, 25))
        self.logFunctionalStep(_("Asignar descripcion del dia festivo."))
        self.logFunctionalStep(_("Asignar fecha del dia festivo."))
        record = self.createDashboardRecord(
            "zue.holidays",
            values,
            _("Validar restriccion de unicidad de la fecha del dia festivo."),
        )
        self.logFunctionalStep(_("Guardar el registro."))
        if not record.id or record.date != values["date"]:
            raise AssertionError(_("No se creo correctamente el dia festivo."))
        self.logFunctionalStep(_("Validar la creacion del dia festivo."))
        return record

    def buildValuesFromTestParams(self, model_name, input_values):
        """Convierte parametros dinamicos de la UI a valores ORM del modelo."""
        input_values = input_values or {}
        model = self.getDashboardModel(model_name)
        values = {}
        for field_name, raw_value in input_values.items():
            if field_name not in model._fields:
                continue
            if raw_value is None or raw_value == "":
                continue
            field = model._fields[field_name]
            values[field_name] = self.castDashboardFieldValue(field, raw_value)
        return values

    def castDashboardFieldValue(self, field, raw_value):
        if field.type == "many2one":
            return int(raw_value)
        if field.type == "integer":
            return int(raw_value)
        if field.type in ("float", "monetary"):
            return float(raw_value)
        if field.type == "boolean":
            if isinstance(raw_value, bool):
                return raw_value
            return str(raw_value).lower() in ("1", "true", "yes", "si")
        return raw_value

    def testCreateOvertimeType(self, input_values=None):
        input_values = input_values or {}
        self.logFunctionalStep(_("Abrir el formulario de tipos de horas extra."))
        type_candidates = [
            "overtime_ext_d", "overtime_ext_n", "overtime_rn", "overtime_eddf",
            "overtime_endf", "overtime_dof", "overtime_rndf", "overtime_rdf", "overtime_rnf",
        ]
        used_types = set(self.getDashboardModel("hr.type.overtime").search([]).mapped("type_overtime"))
        values = self.buildValuesFromTestParams("hr.type.overtime", input_values)

        if values.get("type_overtime"):
            selected_type = values["type_overtime"]
        else:
            selected_type = next((item for item in type_candidates if item not in used_types), False)
            values["type_overtime"] = selected_type or type_candidates[0]

        if not values.get("salary_rule"):
            salary_rule = self.getDashboardModel("hr.salary.rule").search([], limit=1)
            if not salary_rule:
                raise AssertionError(_("No existe una regla salarial para probar tipos de horas extra."))
            values["salary_rule"] = salary_rule.id

        values.setdefault("name", "Tipo hora extra dashboard prueba")
        values.setdefault("percentage", 25.0)

        type_available = values["type_overtime"] not in used_types
        if type_available:
            self.logFunctionalStep(_("Asignar descripcion del tipo de hora extra."))
            self.logFunctionalStep(_("Seleccionar la regla salarial asociada."))
            self.logFunctionalStep(_("Seleccionar el tipo de hora extra."))
            self.logFunctionalField(_("Asignar porcentaje del tipo."), values.get("percentage"), optional=True)
            record = self.createDashboardRecord(
                "hr.type.overtime",
                values,
                _("Validar restriccion de unicidad del tipo de hora extra."),
            )
            self.logFunctionalStep(_("Guardar el registro."))
            if not record.id or record.type_overtime != values["type_overtime"]:
                raise AssertionError(_("No se creo correctamente el tipo de horas extra."))
            self.logFunctionalStep(_("Validar la creacion del tipo de horas extra."))
            return record

        self.logFunctionalStep(_("El tipo de hora extra ya existe; se validara la restriccion del sistema."))
        self.createOrControlled(
            lambda: self.getDashboardModel("hr.type.overtime").create(values),
            _("Validar restriccion de unicidad del tipo de hora extra."),
        )
        return self.getDashboardModel("hr.type.overtime").search(
            [("type_overtime", "=", values["type_overtime"])],
            limit=1,
        )

    def testAnnualParametersBasics(self, input_values=None):
        self.logFunctionalStep(_("Abrir el formulario de parametros anuales."))
        self.logFunctionalStep(_("Ir a la pestaña Basicos."))
        values = {
            "smmlv_monthly": 1423500.0,
            "transportation_assistance_monthly": 200000.0,
            "porc_integral_salary": 75,
            "hours_daily": 7.5,
            "hours_weekly": 52.5,
            "hours_fortnightly": 112.5,
            "hours_monthly": 225.0,
        }
        values.update(self.buildValuesFromTestParams("hr.annual.parameters", input_values))
        self.logFunctionalField(_("Asignar valor mensual SMMLV."), values["smmlv_monthly"])
        self.logFunctionalField(_("Asignar valor mensual auxilio de transporte."), values["transportation_assistance_monthly"])
        self.logFunctionalField(_("Asignar porcentaje salarial integral."), values["porc_integral_salary"])
        self.logFunctionalField(_("Asignar horas diarias."), values["hours_daily"])
        record = self.createAnnualParametersRecord(values.get("year") or 2090, values)
        self.logFunctionalStep(_("Guardar el registro."))
        if not record.id or record.smmlv_monthly != values["smmlv_monthly"]:
            raise AssertionError(_("No se parametrizo correctamente la pestaña Basicos."))
        if record.smmlv_daily != values["smmlv_monthly"] / 30:
            raise AssertionError(_("No se calcularon correctamente los valores basicos derivados."))
        self.logFunctionalStep(_("Validar la parametrizacion de la pestaña Basicos."))
        return record

    def testAnnualParametersSocialSecurity(self, input_values=None):
        self.logFunctionalStep(_("Abrir el formulario de parametros anuales."))
        self.logFunctionalStep(_("Ir a la pestaña Seguridad Social."))
        values = {
            "weight_contribution_calculations": True,
            "z_enable_ibc_previous_month": True,
            "value_porc_health_company": 9.0,
            "value_porc_health_employee": 4.5,
            "value_porc_health_employee_foreign": 4.5,
            "value_porc_pension_company": 13.0,
            "value_porc_pension_employee": 4.5,
            "value_porc_compensation_box_company": 4.5,
            "value_porc_sena_company": 2.5,
            "value_porc_icbf_company": 3.5,
            "value_porc_provision_bonus": 8.5,
            "value_porc_provision_cesantias": 8.5,
            "value_porc_provision_intcesantias": 1.2,
            "value_porc_provision_vacation": 4.5,
            "value_porc_statute_1395": 45,
        }
        values.update(self.buildValuesFromTestParams("hr.annual.parameters", input_values))
        self.logFunctionalField(_("Marcar calculos de aportes al peso."), values["weight_contribution_calculations"])
        self.logFunctionalField(_("Configurar porcentajes de salud."), values["value_porc_health_company"])
        self.logFunctionalField(_("Configurar porcentajes de pension."), values["value_porc_pension_company"])
        self.logFunctionalField(_("Configurar aportes parafiscales."), values["value_porc_sena_company"])
        self.logFunctionalField(_("Configurar provisiones de prestaciones."), values["value_porc_provision_bonus"])
        record = self.createAnnualParametersRecord(values.get("year") or 2091, values)
        self.logFunctionalStep(_("Guardar el registro."))
        if not record.id or not record.weight_contribution_calculations:
            raise AssertionError(_("No se parametrizo correctamente la pestaña Seguridad Social."))
        if record.value_porc_health_total != values["value_porc_health_company"] + values["value_porc_health_employee"]:
            raise AssertionError(_("No se calcularon correctamente los totales de seguridad social."))
        self.logFunctionalStep(_("Validar la parametrizacion de la pestaña Seguridad Social."))
        return record

    def testAnnualParametersTax(self, input_values=None):
        self.logFunctionalStep(_("Abrir el formulario de parametros anuales."))
        self.logFunctionalStep(_("Ir a la pestaña Tributario."))
        values = {
            "value_uvt": 48500.0,
            "value_top_source_retention": 96.0,
            "value_porc_increment_smlv": 12.0,
            "value_porc_ipc": 6.5,
        }
        values.update(self.buildValuesFromTestParams("hr.annual.parameters", input_values))
        self.logFunctionalField(_("Asignar valor UVT."), values["value_uvt"])
        self.logFunctionalField(_("Asignar tope de retencion en la fuente."), values["value_top_source_retention"])
        self.logFunctionalField(_("Asignar incremento SMLV."), values["value_porc_increment_smlv"])
        self.logFunctionalField(_("Asignar porcentaje IPC."), values["value_porc_ipc"])
        record = self.createAnnualParametersRecord(values.get("year") or 2092, values)
        self.logFunctionalStep(_("Guardar el registro."))
        if not record.id or record.value_uvt != values["value_uvt"]:
            raise AssertionError(_("No se parametrizo correctamente la pestaña Tributario."))
        self.logFunctionalStep(_("Validar la parametrizacion de la pestaña Tributario."))
        return record

    def testAnnualParametersPublic(self, input_values=None):
        self.logFunctionalStep(_("Abrir el formulario de parametros anuales."))
        self.logFunctionalStep(_("Ir a la pestaña Publicos."))
        values = {
            "z_food_subsidy_amount": 250000,
            "z_percentage_public": 18,
            "z_bonus_services_rendered": 5000000,
            "z_food_subsidy_tope": 300000,
        }
        values.update(self.buildValuesFromTestParams("hr.annual.parameters", input_values))
        self.logFunctionalField(_("Asignar subsidio de alimentacion."), values["z_food_subsidy_amount"])
        self.logFunctionalField(_("Asignar porcentaje empleados publicos."), values["z_percentage_public"])
        self.logFunctionalField(_("Asignar tope bonificacion por servicios prestados."), values["z_bonus_services_rendered"])
        self.logFunctionalField(_("Asignar tope subsidio de alimentacion."), values["z_food_subsidy_tope"])
        record = self.createAnnualParametersRecord(values.get("year") or 2093, values)
        self.logFunctionalStep(_("Guardar el registro."))
        if not record.id or record.z_percentage_public != values["z_percentage_public"]:
            raise AssertionError(_("No se parametrizo correctamente la pestaña Publicos."))
        self.logFunctionalStep(_("Validar la parametrizacion de la pestaña Publicos."))
        return record

    def testAnnualParametersUpc(self, input_values=None):
        self.logFunctionalStep(_("Abrir el formulario de parametros anuales."))
        self.logFunctionalStep(_("Ir a la pestaña UPC."))
        upc_line = {
            "z_age_group_upc": "age<1",
            "z_normal_zone_upc": 150000.0,
            "z_special_zone_upc": 160000.0,
            "z_cities_upc": 170000.0,
            "z_islands_upc": 180000.0,
            "z_gender_upc": "masculino",
        }
        self.logFunctionalField(_("Agregar grupo de edades UPC."), upc_line["z_age_group_upc"])
        self.logFunctionalField(_("Asignar valores por zona UPC."), upc_line["z_normal_zone_upc"])
        values = {"z_upc_lines_ids": [(0, 0, upc_line)]}
        values.update(self.buildValuesFromTestParams("hr.annual.parameters", input_values))
        if "z_upc_lines_ids" not in values:
            values["z_upc_lines_ids"] = [(0, 0, upc_line)]
        record = self.createAnnualParametersRecord(values.get("year") or 2094, values)
        self.logFunctionalStep(_("Guardar el registro."))
        if not record.id or not record.z_upc_lines_ids:
            raise AssertionError(_("No se parametrizo correctamente la pestaña UPC."))
        if record.z_upc_lines_ids[0].z_gender_upc != upc_line["z_gender_upc"]:
            raise AssertionError(_("No se guardo correctamente la linea UPC."))
        self.logFunctionalStep(_("Validar la parametrizacion de la pestaña UPC."))
        return record

    def testAnnualParametersCertificate(self, input_values=None):
        self.logFunctionalStep(_("Abrir el formulario de parametros anuales."))
        self.logFunctionalStep(_("Ir a la pestaña Certificado de Ingresos y Retenciones."))
        certificate_line = {
            "sequence": 99,
            "calculation": "date_issue",
        }
        values = {
            "taxable_year": 2095,
            "gross_equity": 150000000.0,
            "total_revenues": 85000000.0,
            "credit_card": 12000000.0,
            "purchases_and_consumption": 25000000.0,
            "conf_certificate_income_ids": [(0, 0, certificate_line)],
        }
        values.update(self.buildValuesFromTestParams("hr.annual.parameters", input_values))
        if "conf_certificate_income_ids" not in values:
            values["conf_certificate_income_ids"] = [(0, 0, certificate_line)]
        self.logFunctionalField(_("Asignar año gravable."), values["taxable_year"])
        self.logFunctionalField(_("Asignar patrimonio bruto."), values["gross_equity"])
        self.logFunctionalField(_("Agregar configuracion de reglas salariales."), certificate_line["sequence"])
        record = self.createAnnualParametersRecord(values.get("year") or 2095, values)
        self.logFunctionalStep(_("Guardar el registro."))
        if not record.id or record.taxable_year != values["taxable_year"]:
            raise AssertionError(_("No se parametrizo correctamente la pestaña Certificado de Ingresos y Retenciones."))
        if not record.conf_certificate_income_ids:
            raise AssertionError(_("No se guardo la configuracion del certificado de ingresos y retenciones."))
        self.logFunctionalStep(_("Validar la parametrizacion de la pestaña Certificado de Ingresos y Retenciones."))
        return record

    def testAnnualParametersFds(self, input_values=None):
        self.logFunctionalStep(_("Abrir el formulario de parametros anuales."))
        self.logFunctionalStep(_("Ir a la pestaña Fondo de solidaridad y subsistencia."))
        fds_line = {
            "z_initial_value": 1.0,
            "z_final_value": 4.0,
            "z_porcentage_solidarity_fund": 1.0,
            "z_porcentage_subsistence_fund": 0.5,
        }
        self.logFunctionalField(_("Agregar rango inicial FDS."), fds_line["z_initial_value"])
        self.logFunctionalField(_("Agregar rango final FDS."), fds_line["z_final_value"])
        self.logFunctionalField(_("Asignar porcentaje fondo de solidaridad."), fds_line["z_porcentage_solidarity_fund"])
        values = {"z_fds_lines_ids": [(0, 0, fds_line)]}
        values.update(self.buildValuesFromTestParams("hr.annual.parameters", input_values))
        if "z_fds_lines_ids" not in values:
            values["z_fds_lines_ids"] = [(0, 0, fds_line)]
        record = self.createAnnualParametersRecord(values.get("year") or 2096, values)
        self.logFunctionalStep(_("Guardar el registro."))
        if not record.id or not record.z_fds_lines_ids:
            raise AssertionError(_("No se parametrizo correctamente la pestaña Fondo de solidaridad y subsistencia."))
        if record.z_fds_lines_ids[0].z_porcentage_subsistence_fund != fds_line["z_porcentage_subsistence_fund"]:
            raise AssertionError(_("No se guardo correctamente la linea FDS."))
        self.logFunctionalStep(_("Validar la parametrizacion de la pestaña Fondo de solidaridad y subsistencia."))
        return record

    def testCreateTypesEmployee(self, input_values=None):
        self.logFunctionalStep(_("Abrir el formulario de tipos de empleado."))
        values = self.buildValuesFromTestParams("hr.types.employee", input_values)
        values.setdefault("code", "TE99")
        values.setdefault("name", "Tipo empleado dashboard prueba")
        self.logFunctionalStep(_("Asignar codigo del tipo de empleado."))
        self.logFunctionalStep(_("Asignar nombre del tipo de empleado."))
        record = self.createDashboardRecord(
            "hr.types.employee",
            values,
            _("Validar restriccion de unicidad del codigo de tipo de empleado."),
        )
        self.logFunctionalStep(_("Guardar el registro."))
        if not record.id or record.code != values["code"]:
            raise AssertionError(_("No se creo correctamente el tipo de empleado."))
        self.logFunctionalStep(_("Validar la creacion del tipo de empleado."))
        return record

    def testCreateContractRisk(self, input_values=None):
        self.logFunctionalStep(_("Abrir el formulario de riesgos profesionales."))
        values = self.buildValuesFromTestParams("hr.contract.risk", input_values)
        values.setdefault("code", "R99")
        values.setdefault("name", "Riesgo dashboard prueba")
        values.setdefault("percent", 2.436)
        self.logFunctionalStep(_("Asignar codigo del riesgo."))
        self.logFunctionalStep(_("Asignar nombre del riesgo."))
        self.logFunctionalStep(_("Asignar porcentaje del riesgo."))
        record = self.createDashboardRecord(
            "hr.contract.risk",
            values,
            _("Validar restriccion de unicidad del codigo de riesgo profesional."),
        )
        self.logFunctionalStep(_("Guardar el registro."))
        if not record.id or record.code != values["code"]:
            raise AssertionError(_("No se creo correctamente el riesgo profesional."))
        self.logFunctionalStep(_("Validar la creacion del riesgo profesional."))
        return record

    def testCreateCiiu(self, input_values=None):
        self.logFunctionalStep(_("Abrir el formulario de CIIU."))
        values = self.buildValuesFromTestParams("zue.ciiu", input_values)
        values.setdefault("code", "9999")
        values.setdefault("name", "CIIU dashboard prueba")
        self.logFunctionalStep(_("Asignar codigo CIIU."))
        self.logFunctionalStep(_("Asignar nombre CIIU."))
        record = self.createDashboardRecord(
            "zue.ciiu",
            values,
            _("Validar restriccion de creacion del CIIU."),
        )
        self.logFunctionalStep(_("Guardar el registro."))
        if not record.id or record.code != values["code"]:
            raise AssertionError(_("No se creo correctamente el CIIU."))
        self.logFunctionalStep(_("Validar la creacion del CIIU."))
        return record

    def testCreateEconomicActivityLevelRisk(self, input_values=None):
        self.logFunctionalStep(_("Abrir el formulario de actividad economica por nivel de riesgo."))
        values = self.buildValuesFromTestParams("zue.economic.activity.level.risk", input_values)
        if not values.get("z_risk_class_id"):
            risk = self.testCreateContractRisk({
                "code": "R98",
                "name": "Riesgo actividad dashboard",
                "percent": 1.044,
            })
            values["z_risk_class_id"] = risk.id
        if not values.get("z_code_ciiu_id"):
            ciiu = self.testCreateCiiu({
                "code": "9998",
                "name": "CIIU actividad dashboard",
            })
            values["z_code_ciiu_id"] = ciiu.id
        values.setdefault("z_code", "01")
        values.setdefault("name", "Actividad economica dashboard prueba")
        self.logFunctionalStep(_("Seleccionar la clase de riesgo."))
        self.logFunctionalStep(_("Seleccionar el CIIU."))
        self.logFunctionalStep(_("Asignar codigo de la actividad."))
        self.logFunctionalStep(_("Asignar descripcion de la actividad."))
        record = self.createDashboardRecord(
            "zue.economic.activity.level.risk",
            values,
            _("Validar restriccion de unicidad de la actividad economica por nivel de riesgo."),
        )
        self.logFunctionalStep(_("Guardar el registro."))
        if not record.id or record.z_code != values["z_code"]:
            raise AssertionError(_("No se creo correctamente la actividad economica por nivel de riesgo."))
        self.logFunctionalStep(_("Validar la creacion de la actividad economica."))
        return record

    def testCreateNonEpsContributionRegisters(self, input_values=None):
        self.logFunctionalStep(_("Abrir el formulario de tipos de entidades no EPS."))
        type_map = [
            ("pension", "Pension dashboard prueba"),
            ("caja", "Caja dashboard prueba"),
            ("cesantias", "Cesantias dashboard prueba"),
            ("riesgo", "ARL dashboard prueba"),
        ]
        created = []
        for type_entities, name in type_map:
            self.logFunctionalStep(_("Asignar nombre de la entidad %s.") % name)
            self.logFunctionalStep(_("Seleccionar el tipo de entidad %s.") % type_entities)
            values = self.buildValuesFromTestParams("hr.contribution.register", input_values)
            values["name"] = name
            values["type_entities"] = type_entities
            record = self.createDashboardRecord(
                "hr.contribution.register",
                values,
                _("Validar restriccion de unicidad del tipo de entidad."),
            )
            if not record.id or record.type_entities != type_entities:
                raise AssertionError(_("No se creo correctamente el tipo de entidad %s.") % type_entities)
            created.append(record)
        self.logFunctionalStep(_("Guardar los tipos de entidad pension, caja, cesantias y ARL."))
        self.logFunctionalStep(_("Validar la creacion de los tipos de entidad no EPS."))
        return self.getDashboardModel("hr.contribution.register").browse([item.id for item in created])

    def testCreateNonEpsEmployeeEntities(self, input_values=None):
        self.logFunctionalStep(_("Abrir el formulario de entidades no EPS."))
        type_map = [
            ("pension", "Pension entidad dashboard", "Fondo pension dashboard"),
            ("caja", "Caja entidad dashboard", "Caja compensacion dashboard"),
            ("cesantias", "Cesantias entidad dashboard", "Fondo cesantias dashboard"),
            ("riesgo", "ARL entidad dashboard", "ARL dashboard tercero"),
        ]
        created = []
        for type_entities, type_name, partner_name in type_map:
            entity_type = self.createDashboardRecord(
                "hr.contribution.register",
                {"name": type_name, "type_entities": type_entities},
                _("Validar restriccion de unicidad del tipo de entidad."),
            )
            partner = self.getDashboardModel("res.partner").create({"name": partner_name})
            self.logFunctionalStep(_("Crear o seleccionar el tercero asociado a la entidad %s.") % type_entities)
            values = self.buildValuesFromTestParams("hr.employee.entities", input_values)
            values["partner_id"] = partner.id
            values["types_entities"] = [(6, 0, entity_type.ids)]
            self.logFunctionalStep(_("Asignar el tercero a la entidad."))
            self.logFunctionalStep(_("Seleccionar el tipo de entidad %s.") % type_entities)
            entity = self.createDashboardRecord(
                "hr.employee.entities",
                values,
                _("Validar restriccion de unicidad de la entidad por tercero."),
            )
            if not entity.id or entity_type not in entity.types_entities:
                raise AssertionError(_("No se creo correctamente la entidad %s.") % type_entities)
            created.append(entity)
        self.logFunctionalStep(_("Guardar las entidades no EPS."))
        self.logFunctionalStep(_("Validar la creacion de las entidades no EPS."))
        return self.getDashboardModel("hr.employee.entities").browse([item.id for item in created])

    def testCreateTypeThirdpartyFuncionario(self, input_values=None):
        self.logFunctionalStep(_("Abrir el formulario de tipos de tercero."))
        values = self.buildValuesFromTestParams("zue.type_thirdparty", input_values)
        values.setdefault("code", "FUNC99")
        values.setdefault("name", "Funcionario dashboard prueba")
        values.setdefault("types", "4")
        values.setdefault("is_individual", True)
        self.logFunctionalStep(_("Asignar codigo del tipo de tercero."))
        self.logFunctionalStep(_("Asignar nombre del tipo de tercero."))
        self.logFunctionalStep(_("Seleccionar el tipo Funcionario / Contratista."))
        record = self.createDashboardRecord(
            "zue.type_thirdparty",
            values,
            _("Validar restriccion de unicidad del tipo de tercero funcionario."),
        )
        self.logFunctionalStep(_("Guardar el registro."))
        if not record.id or record.types != values["types"]:
            raise AssertionError(_("No se creo correctamente el tipo de tercero funcionario."))
        self.logFunctionalStep(_("Validar la creacion del tipo de tercero funcionario."))
        return record

    def testCreatePayrollStructure(self, input_values=None):
        self.logFunctionalStep(_("Abrir el formulario de estructuras salariales."))
        values = self.buildValuesFromTestParams("hr.payroll.structure", input_values)
        if not values.get("type_id"):
            structure_type = self.getDashboardModel("hr.payroll.structure.type").search([], limit=1)
            if not structure_type:
                structure_type = self.getDashboardModel("hr.payroll.structure.type").create({
                    "name": "Tipo estructura dashboard prueba",
                })
            values["type_id"] = structure_type.id
        values.setdefault("name", "Estructura nomina dashboard prueba")
        values.setdefault("process", "nomina")
        self.logFunctionalStep(_("Asignar nombre de la estructura."))
        self.logFunctionalStep(_("Seleccionar el tipo de estructura."))
        self.logFunctionalStep(_("Seleccionar el proceso Nomina."))
        record = self.createDashboardRecord(
            "hr.payroll.structure",
            values,
            _("Validar restriccion de creacion de la estructura salarial."),
        )
        self.logFunctionalStep(_("Guardar el registro."))
        if not record.id or record.process != values["process"]:
            raise AssertionError(_("No se creo correctamente la estructura salarial."))
        self.logFunctionalStep(_("Validar la creacion de la estructura salarial."))
        return record

    def testCreateSalaryRule(self, input_values=None):
        self.logFunctionalStep(_("Abrir el formulario de reglas salariales."))
        values = self.buildValuesFromTestParams("hr.salary.rule", input_values)
        if not values.get("category_id"):
            category = self.getDashboardModel("hr.salary.rule.category").search([], limit=1)
            if not category:
                category = self.getDashboardModel("hr.salary.rule.category").create({
                    "name": "Categoria dashboard prueba",
                    "code": "CAT99",
                })
            values["category_id"] = category.id
        if not values.get("struct_id"):
            structure = self.getDashboardModel("hr.payroll.structure").search([], limit=1)
            if not structure:
                structure = self.testCreatePayrollStructure()
            values["struct_id"] = structure.id
        values.setdefault("name", "Regla salarial dashboard prueba")
        values.setdefault("code", "RULE99")
        values.setdefault("sequence", 100)
        values.setdefault("type_concept", "contrato")
        values.setdefault("dev_or_ded", "devengo")
        values.setdefault("appears_on_payslip", True)
        self.logFunctionalStep(_("Asignar nombre de la regla salarial."))
        self.logFunctionalStep(_("Asignar codigo de la regla salarial."))
        self.logFunctionalStep(_("Seleccionar la categoria de la regla."))
        self.logFunctionalStep(_("Seleccionar la estructura salarial."))
        record = self.createDashboardRecord(
            "hr.salary.rule",
            values,
            _("Validar restriccion de creacion de la regla salarial."),
        )
        self.logFunctionalStep(_("Guardar el registro."))
        if not record.id or record.code != values["code"]:
            raise AssertionError(_("No se creo correctamente la regla salarial."))
        self.logFunctionalStep(_("Validar la creacion de la regla salarial."))
        return record

    def testCreateLeaveType(self, input_values=None):
        self.logFunctionalStep(_("Abrir el formulario de tipos de ausencia."))
        values = self.buildValuesFromTestParams("hr.leave.type", input_values)
        values.setdefault("name", "Ausencia dashboard prueba")
        values.setdefault("code", "ABS99")
        self.logFunctionalStep(_("Asignar nombre del tipo de ausencia."))
        self.logFunctionalStep(_("Asignar codigo de nomina del tipo de ausencia."))
        record = self.createDashboardRecord(
            "hr.leave.type",
            values,
            _("Validar restriccion de unicidad del codigo de tipo de ausencia."),
        )
        self.logFunctionalStep(_("Guardar el registro."))
        if not record.id or record.code != values["code"]:
            raise AssertionError(_("No se creo correctamente el tipo de ausencia."))
        self.logFunctionalStep(_("Validar la creacion del tipo de ausencia."))
        return record

    def testCreateCalculationRtefteOrdinary(self, input_values=None):
        self.logFunctionalStep(_("Abrir el formulario de calculo de retencion en la fuente ordinaria."))
        values = self.buildValuesFromTestParams("hr.calculation.rtefte.ordinary", input_values)
        values.setdefault("range_initial", 9000)
        values.setdefault("range_finally", 9100)
        values.setdefault("subtract_uvt", 0)
        values.setdefault("addition_uvt", 0)
        values.setdefault("porc", 19)
        self.logFunctionalStep(_("Asignar rango inicial UVT."))
        self.logFunctionalStep(_("Asignar rango final UVT."))
        self.logFunctionalStep(_("Asignar UVTs a restar."))
        self.logFunctionalStep(_("Asignar UVTs a sumar."))
        self.logFunctionalStep(_("Asignar porcentaje."))
        record = self.createDashboardRecord(
            "hr.calculation.rtefte.ordinary",
            values,
            _("Validar restriccion de unicidad de los rangos UVT de retencion."),
        )
        self.logFunctionalStep(_("Guardar el registro."))
        if not record.id or record.range_initial != values["range_initial"]:
            raise AssertionError(_("No se creo correctamente el calculo de retencion en la fuente ordinaria."))
        self.logFunctionalStep(_("Validar la creacion del calculo de retencion en la fuente ordinaria."))
        return record


@tagged("post_install", "-at_install")
class TestHrConfiguration(TransactionCase):

    def _cases(self):
        return HrConfigurationCases(self.env)

    def test_create_contribution_register(self):
        record = self._cases().testCreateContributionRegister()
        self.assertTrue(record.id)
        self.assertEqual(record.type_entities, "eps")

    def test_create_employee_entity(self):
        entity = self._cases().testCreateEmployeeEntity()
        self.assertTrue(entity.id)
        self.assertTrue(entity.partner_id)

    def test_create_tipo_cotizante(self):
        record = self._cases().testCreateTipoCotizante()
        self.assertEqual(record.code, "TC99")

    def test_create_subtipo_cotizante(self):
        record = self._cases().testCreateSubtipoCotizante()
        self.assertEqual(record.name, "Subtipo cotizante dashboard prueba")

    def test_create_parameterization_contributors(self):
        record = self._cases().testCreateParameterizationContributors()
        self.assertTrue(record.type_of_contributor)

    def test_create_job_position(self):
        record = self._cases().testCreateJobPosition()
        self.assertEqual(record.name, "Puesto dashboard prueba")

    def test_create_skill_type(self):
        record = self._cases().testCreateSkillType()
        self.assertEqual(record.name, "Tipo habilidad dashboard prueba")

    def test_create_holiday(self):
        record = self._cases().testCreateHoliday()
        self.assertEqual(record.date, date(2099, 12, 25))

    def test_create_overtime_type(self):
        record = self._cases().testCreateOvertimeType()
        self.assertTrue(record.type_overtime)

    def test_annual_parameters_basics(self):
        record = self._cases().testAnnualParametersBasics()
        self.assertEqual(record.smmlv_monthly, 1423500.0)

    def test_annual_parameters_social_security(self):
        record = self._cases().testAnnualParametersSocialSecurity()
        self.assertTrue(record.weight_contribution_calculations)

    def test_annual_parameters_tax(self):
        record = self._cases().testAnnualParametersTax()
        self.assertEqual(record.value_uvt, 48500.0)

    def test_annual_parameters_public(self):
        record = self._cases().testAnnualParametersPublic()
        self.assertEqual(record.z_percentage_public, 18)

    def test_annual_parameters_upc(self):
        record = self._cases().testAnnualParametersUpc()
        self.assertEqual(len(record.z_upc_lines_ids), 1)

    def test_annual_parameters_certificate(self):
        record = self._cases().testAnnualParametersCertificate()
        self.assertEqual(record.taxable_year, 2095)

    def test_annual_parameters_fds(self):
        record = self._cases().testAnnualParametersFds()
        self.assertEqual(len(record.z_fds_lines_ids), 1)

    def test_create_types_employee(self):
        record = self._cases().testCreateTypesEmployee()
        self.assertEqual(record.code, "TE99")

    def test_create_contract_risk(self):
        record = self._cases().testCreateContractRisk()
        self.assertEqual(record.code, "R99")

    def test_create_ciiu(self):
        record = self._cases().testCreateCiiu()
        self.assertEqual(record.code, "9999")

    def test_create_economic_activity_level_risk(self):
        record = self._cases().testCreateEconomicActivityLevelRisk()
        self.assertEqual(record.z_code, "01")

    def test_create_non_eps_contribution_registers(self):
        records = self._cases().testCreateNonEpsContributionRegisters()
        self.assertEqual(len(records), 4)

    def test_create_non_eps_employee_entities(self):
        records = self._cases().testCreateNonEpsEmployeeEntities()
        self.assertEqual(len(records), 4)

    def test_create_type_thirdparty_funcionario(self):
        record = self._cases().testCreateTypeThirdpartyFuncionario()
        self.assertEqual(record.types, "4")

    def test_create_payroll_structure(self):
        record = self._cases().testCreatePayrollStructure()
        self.assertEqual(record.process, "nomina")

    def test_create_salary_rule(self):
        record = self._cases().testCreateSalaryRule()
        self.assertEqual(record.code, "RULE99")

    def test_create_leave_type(self):
        record = self._cases().testCreateLeaveType()
        self.assertEqual(record.code, "ABS99")

    def test_create_calculation_rtefte_ordinary(self):
        record = self._cases().testCreateCalculationRtefteOrdinary()
        self.assertEqual(record.range_initial, 9000)
