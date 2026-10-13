# -*- coding: utf-8 -*-

from datetime import date, timedelta

from odoo import _
from odoo.tests.common import TransactionCase, tagged

from odoo.addons.zue_testing_dashboard.tests.test_hr_configuration import HrConfigurationCases


class HrEmployeeContractCases(HrConfigurationCases):
    """Escenarios de Empleados y contratos compartidos por el panel y TransactionCase."""

    def resolveExistingEmployee(self, input_values=None):
        """Obtiene un empleado existente desde params o desde BD."""
        input_values = input_values or {}
        employee_model = self.getDashboardModel("hr.employee")
        employee_id = input_values.get("employee_id")
        if employee_id:
            employee = employee_model.browse(int(employee_id))
            if not employee.exists():
                raise AssertionError(_("No se encontro el empleado indicado."))
            return employee
        employee = employee_model.search([("active", "=", True)], limit=1)
        if not employee:
            employee = employee_model.search([], limit=1)
        if not employee:
            raise AssertionError(_("No hay empleados disponibles en la base de datos."))
        return employee

    def resolveExistingVersion(self, input_values=None, employee=None):
        """Obtiene un contrato/version existente desde params, empleado o BD."""
        input_values = input_values or {}
        version_model = self.getDashboardModel("hr.version")
        if input_values.get("version_id"):
            version = version_model.browse(int(input_values["version_id"]))
            if not version.exists():
                raise AssertionError(_("No se encontro el contrato indicado."))
            return version
        domain = [("retirement_date", "=", False)]
        if employee:
            domain = [("employee_id", "=", employee.id)] + domain
        version = version_model.search(domain, limit=1, order="id desc")
        if not version and employee:
            version = version_model.search([("employee_id", "=", employee.id)], limit=1, order="id desc")
        if not version:
            version = version_model.search([], limit=1, order="id desc")
        if not version:
            raise AssertionError(_("No hay contratos disponibles en la base de datos."))
        return version

    def resolvePartnerForEmployee(self, input_values=None):
        """Resuelve un tercero con VAT para crear empleado."""
        input_values = input_values or {}
        partner_model = self.getDashboardModel("res.partner")
        partner_id = input_values.get("partner_encab_id") or input_values.get("work_contact_id")
        if partner_id:
            partner = partner_model.browse(int(partner_id))
            if not partner.exists():
                raise AssertionError(_("No se encontro el tercero indicado."))
            return partner
        partner = partner_model.search([("vat", "!=", False), ("vat", "!=", "")], limit=1)
        if not partner:
            raise AssertionError(_("No hay terceros con identificacion (VAT) disponibles en la base de datos."))
        return partner

    def buildVersionStartDate(self, values):
        """Normaliza fecha de inicio del contrato segun campos disponibles en hr.version."""
        start = values.get("contract_date_start") or values.get("date_start") or date.today()
        version_model = self.getDashboardModel("hr.version")
        if "contract_date_start" in version_model._fields:
            values.setdefault("contract_date_start", start)
        if "date_start" in version_model._fields:
            values.setdefault("date_start", start)
        return values

    def testCreateEmployee(self, input_values=None):
        """Crea/configura un empleado basico con datos de BD o del panel."""
        input_values = input_values or {}
        self.logFunctionalStep(_("Abrir el formulario de empleados."))
        values = self.buildValuesFromTestParams("hr.employee", input_values)
        partner = False
        if not values.get("partner_encab_id") and not values.get("work_contact_id"):
            partner = self.resolvePartnerForEmployee(input_values)
            values["partner_encab_id"] = partner.id
            values["work_contact_id"] = partner.id
        elif values.get("partner_encab_id") and not values.get("work_contact_id"):
            values["work_contact_id"] = values["partner_encab_id"]
        elif values.get("work_contact_id") and not values.get("partner_encab_id"):
            values["partner_encab_id"] = values["work_contact_id"]

        if not values.get("type_employee"):
            type_employee = self.getDashboardModel("hr.types.employee").search([], limit=1)
            if type_employee:
                values["type_employee"] = type_employee.id

        if not values.get("name"):
            partner = partner or self.getDashboardModel("res.partner").browse(
                values.get("partner_encab_id") or values.get("work_contact_id")
            )
            values["name"] = partner.name if partner else _("Empleado dashboard prueba")

        self.logFunctionalField(_("Asignar tercero del empleado."), values.get("partner_encab_id"))
        self.logFunctionalField(_("Asignar tipo de empleado."), values.get("type_employee"), optional=True)
        self.logFunctionalField(_("Asignar nombre del empleado."), values.get("name"))
        record = self.createDashboardRecord(
            "hr.employee",
            values,
            _("Validar restriccion de unicidad del empleado."),
        )
        self.logFunctionalStep(_("Guardar el empleado."))
        if not record.id:
            raise AssertionError(_("No se creo correctamente el empleado."))
        self.logFunctionalStep(_("Validar la creacion del empleado."))
        return record

    def testCreateContractVersion(self, input_values=None):
        """Alta inicial de contrato como hr.version en Odoo 19."""
        input_values = input_values or {}
        self.logFunctionalStep(_("Abrir el formulario de contratos (hr.version)."))
        values = self.buildValuesFromTestParams("hr.version", input_values)
        if not values.get("employee_id"):
            values["employee_id"] = self.resolveExistingEmployee(input_values).id
        values.setdefault("contract_type", "obra")
        values.setdefault("modality_salary", "basico")
        if not values.get("risk_id"):
            risk = self.getDashboardModel("hr.contract.risk").search([], limit=1)
            if risk:
                values["risk_id"] = risk.id
        values = self.buildVersionStartDate(values)
        wage = values.pop("wage", None)
        job_id = values.pop("job_id", None)
        if wage in (None, False, ""):
            wage = 1500000.0
        start_date = values.get("contract_date_start") or values.get("date_start") or date.today()
        if "change_wage_ids" not in values:
            values["change_wage_ids"] = [(0, 0, {
                "date_start": start_date,
                "wage": float(wage),
                "job_id": job_id or False,
            })]

        self.logFunctionalField(_("Asignar empleado del contrato."), values.get("employee_id"))
        self.logFunctionalField(_("Asignar tipo de contrato."), values.get("contract_type"))
        self.logFunctionalField(_("Asignar modalidad de salario."), values.get("modality_salary"))
        self.logFunctionalField(_("Asignar riesgo profesional."), values.get("risk_id"), optional=True)
        self.logFunctionalField(_("Asignar salario inicial."), wage)
        record = self.createDashboardRecord(
            "hr.version",
            values,
            _("Validar restriccion de creacion del contrato."),
        )
        self.logFunctionalStep(_("Guardar el contrato."))
        if not record.id or record.employee_id.id != values["employee_id"]:
            raise AssertionError(_("No se creo correctamente el contrato (hr.version)."))
        self.logFunctionalStep(_("Validar la creacion del contrato."))
        return record

    def testCreateWageChangeVersion(self, input_values=None):
        """Crea una nueva version contractual sobre un empleado existente y valida el historial salarial."""
        input_values = input_values or {}
        self.logFunctionalStep(_("Preparar cambio salarial como nueva version contractual."))
        values = self.buildValuesFromTestParams("hr.version", input_values)
        base_employee = self.resolveExistingEmployee(input_values)
        if values.get("employee_id"):
            base_employee = self.getDashboardModel("hr.employee").browse(int(values["employee_id"]))
            if not base_employee.exists():
                raise AssertionError(_("No se encontro el empleado indicado para el cambio salarial."))
        values["employee_id"] = base_employee.id
        previous_versions = self.getDashboardModel("hr.version").search([
            ("employee_id", "=", base_employee.id),
        ])
        previous_count = len(previous_versions)
        values.setdefault("contract_type", "obra")
        values.setdefault("modality_salary", "basico")
        if not values.get("risk_id"):
            risk = self.getDashboardModel("hr.contract.risk").search([], limit=1)
            if risk:
                values["risk_id"] = risk.id
        values = self.buildVersionStartDate(values)
        wage = values.pop("wage", None)
        job_id = values.pop("job_id", None)
        if wage in (None, False, ""):
            wage = 1800000.0
        start_date = values.get("contract_date_start") or values.get("date_start") or (date.today() + timedelta(days=1))
        if "contract_date_start" in self.getDashboardModel("hr.version")._fields:
            values["contract_date_start"] = start_date
        if "date_start" in self.getDashboardModel("hr.version")._fields:
            values["date_start"] = start_date
        values["change_wage_ids"] = [(0, 0, {
            "date_start": start_date,
            "wage": float(wage),
            "job_id": job_id or False,
        })]

        self.logFunctionalField(_("Asignar empleado existente."), base_employee.display_name)
        self.logFunctionalField(_("Asignar nuevo salario."), wage)
        record = self.createDashboardRecord(
            "hr.version",
            values,
            _("Validar restriccion de creacion de la nueva version contractual."),
        )
        self.logFunctionalStep(_("Guardar la nueva version."))
        current_count = self.getDashboardModel("hr.version").search_count([
            ("employee_id", "=", base_employee.id),
        ])
        if current_count <= previous_count:
            raise AssertionError(_("No se creo una nueva version para el empleado existente."))
        if not record.change_wage_ids:
            raise AssertionError(_("La nueva version no tiene historial salarial (hr.contract.change.wage)."))
        last_change = max(record.change_wage_ids, key=lambda item: item.date_start or date.min)
        if float(last_change.wage or 0.0) != float(wage):
            raise AssertionError(_("El historial salarial no refleja el salario del cambio."))
        self.logFunctionalStep(_("Validar historial salarial de la nueva version."))
        return record

    def testCreateContractConcept(self, input_values=None):
        """Crea un concepto fijo del contrato sin ejecutar liquidacion."""
        input_values = input_values or {}
        self.logFunctionalStep(_("Abrir el formulario de conceptos fijos del contrato."))
        values = self.buildValuesFromTestParams("hr.contract.concepts", input_values)
        if not values.get("version_id"):
            values["version_id"] = self.resolveExistingVersion(input_values).id
        if not values.get("input_id"):
            salary_rule = self.getDashboardModel("hr.salary.rule").search([], limit=1)
            if not salary_rule:
                raise AssertionError(_("No hay reglas salariales disponibles para el concepto fijo."))
            values["input_id"] = salary_rule.id
        values.setdefault("period", "indefinite")
        values.setdefault("aplicar", "0")
        values.setdefault("amount", 100000.0)
        values.setdefault("state", "draft")
        values.setdefault("show_voucher", True)
        values.setdefault("detail", _("Simulacion dashboard conceptos fijos"))

        self.logFunctionalField(_("Asignar contrato del concepto."), values.get("version_id"))
        self.logFunctionalField(_("Asignar regla salarial."), values.get("input_id"))
        self.logFunctionalField(_("Asignar valor del concepto."), values.get("amount"))
        record = self.createDashboardRecord(
            "hr.contract.concepts",
            values,
            _("Validar restriccion de unicidad del concepto fijo."),
        )
        self.logFunctionalStep(_("Guardar el concepto fijo."))
        if record.state != "done":
            record.change_state_done()
            self.logFunctionalStep(_("Aprobar el concepto fijo."))
        if not record.id or record.state != "done":
            raise AssertionError(_("No se creo/aprobo correctamente el concepto fijo."))
        self.logFunctionalStep(_("Validar la creacion del concepto fijo."))
        return record

    def testUpdateContractualModifications(self, input_values=None):
        """Aplica cambios de cargo, jornada o sucursal sobre hr.version."""
        input_values = input_values or {}
        self.logFunctionalStep(_("Preparar modificaciones contractuales sobre hr.version."))
        values = self.buildValuesFromTestParams("hr.version", input_values)
        version = self.resolveExistingVersion(input_values)
        if values.get("employee_id") and int(values["employee_id"]) != version.employee_id.id:
            version = self.resolveExistingVersion(input_values, employee=self.getDashboardModel("hr.employee").browse(int(values["employee_id"])))

        write_vals = {}
        if values.get("resource_calendar_id"):
            write_vals["resource_calendar_id"] = values["resource_calendar_id"]
        elif "resource_calendar_id" in version._fields:
            calendar = self.getDashboardModel("resource.calendar").search([], limit=1)
            if calendar and calendar.id != version.resource_calendar_id.id:
                write_vals["resource_calendar_id"] = calendar.id

        job = False
        if values.get("job_id"):
            job = self.getDashboardModel("hr.job").browse(int(values["job_id"]))
        elif "job_id" in version._fields:
            job = self.getDashboardModel("hr.job").search(
                [("id", "!=", version.job_id.id)] if version.job_id else [],
                limit=1,
            )
        if job and job.exists():
            self.getDashboardModel("hr.contract.change.wage").create({
                "version_id": version.id,
                "date_start": date.today(),
                "wage": float(version.wage or 1000000.0),
                "job_id": job.id,
            })
            self.logFunctionalField(_("Asignar nuevo cargo via historial salarial."), job.display_name)

        branch_id = values.get("branch_id")
        if not branch_id and "branch_id" in version.employee_id._fields and "zue.res.branch" in self.env:
            branch_domain = [("id", "!=", version.employee_id.branch_id.id)] if version.employee_id.branch_id else []
            branch = self.getDashboardModel("zue.res.branch").search(branch_domain, limit=1)
            if branch:
                branch_id = branch.id
        if branch_id and "branch_id" in version.employee_id._fields:
            version.employee_id.write({"branch_id": int(branch_id)})
            self.logFunctionalField(_("Asignar nueva sucursal del empleado."), branch_id)

        if write_vals:
            version.write(write_vals)
            self.logFunctionalField(_("Asignar jornada/calendario."), write_vals.get("resource_calendar_id"), optional=True)

        modification_model = self.getDashboardModel("hr.contractual.modifications")
        modification = modification_model.create({
            "version_id": version.id,
            "date": date.today(),
            "description": _("Modificacion contractual dashboard prueba"),
        })
        self.logFunctionalStep(_("Registrar bitacora de modificacion contractual."))
        version.invalidate_recordset()
        if not modification.id:
            raise AssertionError(_("No se registro la modificacion contractual."))
        if job and version.job_id and version.job_id.id != job.id:
            raise AssertionError(_("El cargo del contrato no se actualizo correctamente."))
        self.logFunctionalStep(_("Validar modificaciones contractuales."))
        return version

    def testTerminateContractVersion(self, input_values=None):
        """Valida el flujo de retiro/fecha de fin del contrato sobre hr.version."""
        input_values = input_values or {}
        self.logFunctionalStep(_("Preparar terminacion de contrato."))
        values = self.buildValuesFromTestParams("hr.version", input_values)
        version = self.resolveExistingVersion(input_values)
        retirement_date = values.get("retirement_date") or date.today()
        write_vals = {
            "retirement_date": retirement_date,
        }
        if "date_end" in version._fields and values.get("date_end"):
            write_vals["date_end"] = values["date_end"]
        elif "date_end" in version._fields:
            write_vals["date_end"] = retirement_date
        if "z_state_finished" in version._fields:
            write_vals["z_state_finished"] = True if values.get("z_state_finished") in (None, True, "true", "1", 1) else bool(values.get("z_state_finished"))

        self.logFunctionalField(_("Asignar fecha de retiro."), retirement_date)
        self.logFunctionalField(_("Marcar contrato finalizado por liquidar."), write_vals.get("z_state_finished"), optional=True)
        version.write(write_vals)
        self.logFunctionalStep(_("Guardar la terminacion del contrato."))
        version.invalidate_recordset()
        if not version.retirement_date:
            raise AssertionError(_("El contrato no quedo con fecha de retiro."))
        if version.retirement_date != retirement_date:
            raise AssertionError(_("La fecha de retiro del contrato no coincide con la esperada."))
        active_version = self.getDashboardModel("hr.version").search([
            ("employee_id", "=", version.employee_id.id),
            ("retirement_date", "=", False),
            ("id", "=", version.id),
        ], limit=1)
        if active_version:
            raise AssertionError(_("El contrato retirado sigue apareciendo como activo."))
        self.logFunctionalStep(_("Validar que el contrato ya no esta activo."))
        return version

    def payrollProcessCases(self):
        from odoo.addons.zue_testing_dashboard.tests.test_hr_payroll_process import HrPayrollProcessCases

        return HrPayrollProcessCases(
            self.env,
            provider=self.provider,
            session_id=self.session_id,
        )

    def resolveAbsenceScenarioDefaults(self, technical_name):
        """Defaults de tipo y estado destino por escenario, sin producto cartesiano."""
        defaults = {
            "test_create_leave_draft": {
                "leave_code": "LICENCIA_REMUNERADA",
                "destination_state": "draft",
            },
            "test_create_leave_validate_real": {
                "leave_code": "LICENCIA_REMUNERADA",
                "destination_state": "real",
            },
            "test_create_leave_validate_forced": {
                "leave_code": "LICENCIA_REMUNERADA",
                "destination_state": "forced",
            },
            "test_create_leave_incapacidad": {
                "leave_code": "EGA",
                "destination_state": "forced",
            },
            "test_create_leave_licencia_no_remunerada": {
                "leave_code": "LICENCIA_NO_REMUNERADA",
                "destination_state": "forced",
            },
            "test_create_leave_inasistencia": {
                "leave_code": "INAS_INJU",
                "destination_state": "forced",
            },
            "test_create_leave_vacaciones": {
                "leave_code": "VACDISFRUTADAS",
                "destination_state": "forced",
            },
        }
        return defaults.get(technical_name) or {
            "leave_code": "LICENCIA_REMUNERADA",
            "destination_state": "forced",
        }

    def resolveLeaveTypeForAbsenceTest(self, input_values, default_code):
        """Resuelve hr.leave.type desde el panel o el codigo del escenario."""
        leave_model = self.getDashboardModel("hr.leave.type")
        leave_type_id = input_values.get("leave_type_id")
        if leave_type_id:
            leave_type = leave_model.browse(int(leave_type_id))
            if not leave_type.exists():
                raise AssertionError(_("No se encontro el tipo de ausencia indicado."))
            return leave_type
        if default_code:
            leave_type = leave_model.search([("code", "=", default_code)], limit=1)
            if leave_type:
                return leave_type
        raise AssertionError(_(
            "No hay tipo de ausencia con codigo %s en la base de datos."
        ) % (default_code or "-"))

    def testCreateLeave(self, input_values=None):
        """Crea hr.leave reutilizando los helpers de novedades del panel."""
        input_values = input_values or {}
        helpers = self.payrollProcessCases()
        technical_name = input_values.get("technical_name") or "test_create_leave_validate_forced"
        defaults = self.resolveAbsenceScenarioDefaults(technical_name)
        destination_state = input_values.get("destination_state") or defaults["destination_state"]
        if destination_state not in ("draft", "real", "forced"):
            raise AssertionError(_("Estado destino invalido: %s") % destination_state)

        version = helpers.resolveVersionForProcessTest(input_values)
        leave_type = self.resolveLeaveTypeForAbsenceTest(input_values, defaults["leave_code"])
        work_entry_type = helpers.resolveWorkEntryTypeForLeaveType(leave_type)
        date_from = helpers.parseProcessTestDate(
            input_values.get("date_from") or input_values.get("date_start")
        )
        date_to = helpers.parseProcessTestDate(
            input_values.get("date_to") or input_values.get("date_end")
        )
        if self.hasDashboardProvider():
            if not date_from or not date_to:
                raise AssertionError(_("Debe indicar Fecha desde y Fecha hasta de la ausencia."))
        else:
            date_from = date_from or date.today()
            date_to = date_to or (date_from + timedelta(days=2))
        if date_from > date_to:
            raise AssertionError(_("La fecha desde de la ausencia no puede ser posterior a la fecha hasta."))

        destination_labels = {
            "draft": _("Borrador"),
            "real": _("Validada (flujo real)"),
            "forced": _("Validada (forzada)"),
        }
        state_labels = {
            "draft": _("Borrador"),
            "confirm": _("Por aprobar"),
            "validate1": _("Segundo aprobador"),
            "validate": _("Validada"),
            "refuse": _("Rechazada"),
            "cancel": _("Cancelada"),
        }
        self.logFunctionalStep(_("Crear ausencia %s.") % (leave_type.display_name or leave_type.code or leave_type.name))
        self.logFunctionalField(_("Empleado/Contrato"), version.display_name or version.employee_id.name)
        self.logFunctionalField(_("Tipo de entrada"), leave_type.display_name or leave_type.code)
        self.logFunctionalField(_("Fecha desde"), date_from)
        self.logFunctionalField(_("Fecha hasta"), date_to)
        self.logFunctionalField(_("Estado destino"), destination_labels.get(destination_state, destination_state))

        novelty = {
            "leave_type": leave_type,
            "work_entry_type": work_entry_type,
            "date_from": date_from,
            "date_to": date_to,
            "days": helpers.countInclusiveDays(date_from, date_to),
            "validate_mode": destination_state,
        }
        created_leaves = helpers.applyProcessTestWorkEntries(version, date_from, date_to, [novelty])
        if not created_leaves:
            raise AssertionError(_("No se creo la ausencia para el tipo %s.") % (
                leave_type.display_name or leave_type.code or leave_type.name
            ))
        leave = created_leaves[0]
        final_state = leave.state or "-"
        self.logFunctionalField(
            _("Estado final de hr.leave"),
            "%s (%s)" % (state_labels.get(final_state, final_state), final_state),
        )
        if leave.unpaid_absences:
            vacation_history = self.getDashboardModel("hr.vacation").search([("leave_id", "=", leave.id)])
            if vacation_history:
                history_value = _("Si (%s registros)") % len(vacation_history)
            else:
                history_value = _("No")
            self.logFunctionalField(_("Historial hr.vacation (licencia no remunerada)"), history_value)

        if destination_state == "draft":
            if final_state not in ("draft", "confirm"):
                raise AssertionError(_(
                    "La ausencia en modo borrador no debio validarse (estado: %s)."
                ) % final_state)
        elif final_state != "validate":
            raise AssertionError(_(
                "La ausencia no quedo validada (estado: %s)."
            ) % final_state)
        return leave


@tagged("post_install", "-at_install")
class TestHrEmployeeContract(TransactionCase):

    def _cases(self):
        return HrEmployeeContractCases(self.env)

    def test_create_employee(self):
        record = self._cases().testCreateEmployee()
        self.assertTrue(record.id)

    def test_create_contract_version(self):
        record = self._cases().testCreateContractVersion()
        self.assertTrue(record.id)
        self.assertTrue(record.employee_id)

    def test_create_wage_change_version(self):
        record = self._cases().testCreateWageChangeVersion()
        self.assertTrue(record.change_wage_ids)

    def test_create_contract_concept(self):
        record = self._cases().testCreateContractConcept()
        self.assertEqual(record.state, "done")

    def test_update_contractual_modifications(self):
        record = self._cases().testUpdateContractualModifications()
        self.assertTrue(record.id)

    def test_terminate_contract_version(self):
        record = self._cases().testTerminateContractVersion()
        self.assertTrue(record.retirement_date)

    # def test_create_leave_draft(self):
    #     record = self._cases().testCreateLeave({"technical_name": "test_create_leave_draft"})
    #     self.assertIn(record.state, ("draft", "confirm"))
    #
    # def test_create_leave_validate_real(self):
    #     record = self._cases().testCreateLeave({"technical_name": "test_create_leave_validate_real"})
    #     self.assertEqual(record.state, "validate")
    #
    # def test_create_leave_validate_forced(self):
    #     record = self._cases().testCreateLeave({"technical_name": "test_create_leave_validate_forced"})
    #     self.assertEqual(record.state, "validate")
    #
    # def test_create_leave_incapacidad(self):
    #     record = self._cases().testCreateLeave({"technical_name": "test_create_leave_incapacidad"})
    #     self.assertEqual(record.state, "validate")
    #
    # def test_create_leave_licencia_no_remunerada(self):
    #     record = self._cases().testCreateLeave({"technical_name": "test_create_leave_licencia_no_remunerada"})
    #     self.assertEqual(record.state, "validate")
    #
    # def test_create_leave_inasistencia(self):
    #     record = self._cases().testCreateLeave({"technical_name": "test_create_leave_inasistencia"})
    #     self.assertEqual(record.state, "validate")
    #
    # def test_create_leave_vacaciones(self):
    #     record = self._cases().testCreateLeave({"technical_name": "test_create_leave_vacaciones"})
    #     self.assertEqual(record.state, "validate")
