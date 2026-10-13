# -*- coding: utf-8 -*-

import base64
from datetime import date, datetime, time, timedelta

from dateutil.relativedelta import relativedelta

from odoo import _
from odoo.fields import Date as OdooDate

from odoo.addons.zue_testing_dashboard.tests.payroll_test_hr_configuration import HrConfigurationCases


class HrPayrollProcessCases(HrConfigurationCases):
    """Escenarios de liquidacion de nomina para pruebas test_type=process."""

    def resolveVersionForProcessTest(self, input_values):
        version_model = self.getDashboardModel("hr.version")
        version_id = input_values.get("version_id")
        if version_id:
            version = version_model.browse(int(version_id))
            if not version.exists():
                raise AssertionError(_("No se encontro el contrato indicado para la liquidacion."))
            return version
        if self.hasDashboardProvider():
            raise AssertionError(_("Debe seleccionar un contrato existente en la base de datos."))
        version = version_model.search([
            ("employee_id.active", "=", True),
            ("retirement_date", "=", False),
        ], limit=1)
        if not version:
            version = version_model.search([], limit=1)
        if not version:
            raise AssertionError(_("No hay contratos disponibles para ejecutar la liquidacion."))
        return version

    def resolvePeriodicPayrollStructure(self):
        structure_model = self.getDashboardModel("hr.payroll.structure")
        structure = structure_model.search([("process", "=", "nomina")], limit=1)
        if not structure:
            raise AssertionError(_("No hay estructura salarial de nomina disponible en la base de datos."))
        return structure

    def resolvePrimaPayrollStructure(self):
        structure_model = self.getDashboardModel("hr.payroll.structure")
        structure = structure_model.search([("process", "=", "prima")], limit=1)
        if not structure:
            raise AssertionError(_("No hay estructura salarial de prima disponible en la base de datos."))
        return structure

    def resolveCesantiasPayrollStructure(self, structure_process):
        if structure_process not in ("cesantias", "intereses_cesantias"):
            raise AssertionError(_("Proceso de cesantías inválido: %s") % structure_process)
        structure_model = self.getDashboardModel("hr.payroll.structure")
        structure = structure_model.search([("process", "=", structure_process)], limit=1)
        if not structure:
            raise AssertionError(_(
                "No hay estructura salarial de %s disponible en la base de datos."
            ) % structure_process)
        return structure

    def sanitizeProcessHistoryAccrualDates(self, version, structure_process):
        """Dentro del savepoint: quita historiales sin final_accrual_date.

        El motor de prima/cesantías compara final_accrual_date con fechas y falla
        (date vs bool) si algún historial viene vacío. No se modifica zue_hr_payroll:
        solo se limpia data inválida del escenario de prueba (reversible por savepoint).
        """
        domains = []
        if structure_process == "prima":
            domains.append((
                self.getDashboardModel("hr.history.prima"),
                [
                    ("employee_id", "=", version.employee_id.id),
                    ("version_id", "=", version.id),
                    ("final_accrual_date", "=", False),
                ],
            ))
        elif structure_process in ("cesantias", "intereses_cesantias"):
            domains.append((
                self.getDashboardModel("hr.history.cesantias"),
                [
                    ("employee_id", "=", version.employee_id.id),
                    ("version_id", "=", version.id),
                    ("final_accrual_date", "=", False),
                ],
            ))
        elif structure_process == "contrato":
            domains.extend([
                (
                    self.getDashboardModel("hr.history.prima"),
                    [
                        ("employee_id", "=", version.employee_id.id),
                        ("version_id", "=", version.id),
                        ("final_accrual_date", "=", False),
                    ],
                ),
                (
                    self.getDashboardModel("hr.history.cesantias"),
                    [
                        ("employee_id", "=", version.employee_id.id),
                        ("version_id", "=", version.id),
                        ("final_accrual_date", "=", False),
                    ],
                ),
                (
                    self.getDashboardModel("hr.vacation"),
                    [
                        ("employee_id", "=", version.employee_id.id),
                        ("version_id", "=", version.id),
                        ("final_accrual_date", "=", False),
                    ],
                ),
            ])
        else:
            return
        removed = False
        for history_model, domain in domains:
            invalid = history_model.search(domain)
            if not invalid:
                continue
            removed = True
            invalid.unlink()
        if not removed:
            return
        self.logFunctionalStep(_(
            "Omitir historiales sin fecha final de causación para evitar error date/bool del motor."
        ))

    def resolveContratoPayrollStructure(self):
        structure_model = self.getDashboardModel("hr.payroll.structure")
        structure = structure_model.search([("process", "=", "contrato")], limit=1)
        if not structure:
            raise AssertionError(_(
                "No hay estructura salarial de liquidación de contrato disponible en la base de datos."
            ))
        return structure

    def resolveContratoAccrualDates(self, version):
        """Replica load_dates_liq_contrato: fechas de causación desde historiales."""
        if not version.contract_date_start:
            raise AssertionError(_(
                "El contrato seleccionado no tiene fecha de inicio (contract_date_start); "
                "es requerida para liquidar el contrato."
            ))
        date_prima = version.contract_date_start
        for history in sorted(
            self.getDashboardModel("hr.history.prima").search([
                ("employee_id", "=", version.employee_id.id),
                ("version_id", "=", version.id),
            ]),
            key=lambda item: item.final_accrual_date or date.min,
        ):
            if history.final_accrual_date and history.final_accrual_date > date_prima:
                date_prima = history.final_accrual_date + timedelta(days=1)

        date_vacaciones = version.contract_date_start
        for history in sorted(
            self.getDashboardModel("hr.vacation").search([
                ("employee_id", "=", version.employee_id.id),
                ("version_id", "=", version.id),
            ]),
            key=lambda item: item.final_accrual_date or date.min,
        ):
            if not history.final_accrual_date:
                continue
            if history.leave_id and history.leave_id.holiday_status_id.unpaid_absences:
                continue
            if history.final_accrual_date > date_vacaciones:
                date_vacaciones = history.final_accrual_date + timedelta(days=1)

        date_cesantias = version.contract_date_start
        for history in sorted(
            self.getDashboardModel("hr.history.cesantias").search([
                ("employee_id", "=", version.employee_id.id),
                ("version_id", "=", version.id),
            ]),
            key=lambda item: item.final_accrual_date or date.min,
        ):
            if history.final_accrual_date and history.final_accrual_date > date_cesantias:
                date_cesantias = history.final_accrual_date + timedelta(days=1)

        return {
            "date_prima": date_prima,
            "date_cesantias": date_cesantias,
            "date_vacaciones": date_vacaciones,
        }

    def resolveContratoLiquidacionDate(self, input_values, period_end):
        """Fecha de liquidación editable; por defecto = fecha hasta del recibo."""
        date_liquidacion = self.parseProcessTestDate(input_values.get("date_liquidacion"))
        return date_liquidacion or period_end

    def applyContratoPayslipFields(self, payslip, input_values, version, period_end):
        """Escribe campos de liq. contrato en el recibo y recalcula (generate_payslips no los setea)."""
        accrual = self.resolveContratoAccrualDates(version)
        date_liquidacion = self.resolveContratoLiquidacionDate(input_values, period_end)
        have_compensation = bool(input_values.get("have_compensation"))
        reason_retiro_id = input_values.get("reason_retiro_id")
        write_vals = {
            "date_liquidacion": date_liquidacion,
            "date_prima": accrual["date_prima"],
            "date_cesantias": accrual["date_cesantias"],
            "date_vacaciones": accrual["date_vacaciones"],
                "have_compensation": have_compensation,
        }
        if reason_retiro_id:
            reason = self.getDashboardModel("hr.departure.reason").browse(int(reason_retiro_id))
            if not reason.exists():
                raise AssertionError(_("El motivo de retiro indicado no existe."))
            write_vals["reason_retiro"] = reason.id
            self.logFunctionalField(_("Motivo de retiro."), reason.display_name)
        self.logFunctionalField(_("Fecha de liquidación."), date_liquidacion)
        self.logFunctionalField(_("Fecha causación prima."), accrual["date_prima"])
        self.logFunctionalField(_("Fecha causación cesantías."), accrual["date_cesantias"])
        self.logFunctionalField(_("Fecha causación vacaciones."), accrual["date_vacaciones"])
        self.logFunctionalField(_("Indemnización."), _("Sí") if have_compensation else _("No"))
        payslip.write(write_vals)
        self.logFunctionalStep(_("Recalcular recibo de liquidación de contrato con fechas y flags."))
        payslip.compute_sheet()
        return payslip

    def resolveCesantiasPeriodStart(self, version, structure_process):
        """Calcula fecha desde: historial.final_accrual_date + 1 o contract_date_start."""
        date_cesantias = version.contract_date_start
        if not date_cesantias:
            raise AssertionError(_(
                "El contrato seleccionado no tiene fecha de inicio (contract_date_start); "
                "es requerida para liquidar cesantías."
            ))
        history_model = self.getDashboardModel("hr.history.cesantias")
        histories = history_model.search([
            ("employee_id", "=", version.employee_id.id),
            ("version_id", "=", version.id),
            ("type_history", "=", "all"),
        ])
        if structure_process == "cesantias":
            histories |= history_model.search([
                ("employee_id", "=", version.employee_id.id),
                ("version_id", "=", version.id),
                ("type_history", "=", "cesantias"),
            ])
        elif structure_process == "intereses_cesantias":
            histories |= history_model.search([
                ("employee_id", "=", version.employee_id.id),
                ("version_id", "=", version.id),
                ("type_history", "=", "intcesantias"),
            ])
        for history in sorted(histories, key=lambda item: item.final_accrual_date or date.min):
            if history.final_accrual_date and (
                not date_cesantias or history.final_accrual_date > date_cesantias
            ):
                date_cesantias = history.final_accrual_date + timedelta(days=1)
        return date_cesantias

    def resolveCesantiasScenarioPeriod(self, input_values, version, structure_process):
        """Periodo de cesantías: fecha hasta del escenario y fecha desde automática."""
        date_end = self.parseProcessTestDate(input_values.get("date_end"))
        if self.hasDashboardProvider():
            if not date_end:
                raise AssertionError(_("Debe indicar Fecha hasta del escenario de cesantías."))
        else:
            date_end = date_end or date.today()
        date_start = self.resolveCesantiasPeriodStart(version, structure_process)
        if date_start > date_end:
            raise AssertionError(_(
                "La fecha desde calculada (%s) es posterior a la fecha hasta (%s)."
            ) % (date_start, date_end))
        return date_start, date_end

    def normalizeTestSeveranceAdvance(self, input_values):
        """Valida anticipo de cesantías del escenario."""
        is_advance = bool(input_values.get("z_is_advance_severance"))
        raw_value = input_values.get("z_value_advance_severance")
        if not is_advance:
            return {"is_advance": False, "value": 0.0}
        if raw_value in (None, False, ""):
            raise AssertionError(_("Debe indicar el valor del anticipo de cesantías."))
        value = float(raw_value)
        if value <= 0:
            raise AssertionError(_("El valor del anticipo de cesantías debe ser positivo."))
        return {"is_advance": True, "value": value}

    def applyProcessTestSeveranceAdvance(self, payslip, advance):
        """Marca anticipo en el recibo y recalcula para que el motor lo aplique."""
        if not advance or not advance.get("is_advance"):
            return payslip
        payslip.write({
            "z_is_advance_severance": True,
            "z_value_advance_severance": advance["value"],
        })
        self.logFunctionalField(_("Marcar anticipo de cesantías."), True)
        self.logFunctionalField(_("Valor del anticipo."), advance["value"])
        self.logFunctionalStep(_("Recalcular recibo con anticipo de cesantías."))
        payslip.compute_sheet()
        return payslip

    def parseProcessTestDate(self, value):
        """Normaliza fechas del escenario o de novedades a date."""
        if not value:
            return False
        if isinstance(value, date):
            return value
        return OdooDate.to_date(value)

    def resolveScenarioPeriod(self, input_values):
        """Obtiene el rango de fechas del escenario de liquidacion."""
        date_start = self.parseProcessTestDate(input_values.get("date_start"))
        date_end = self.parseProcessTestDate(input_values.get("date_end"))
        if self.hasDashboardProvider():
            if not date_start or not date_end:
                raise AssertionError(_("Debe indicar Fecha desde y Fecha hasta del escenario."))
        else:
            date_start = date_start or date.today().replace(day=1)
            date_end = date_end or date.today()
        if date_start > date_end:
            raise AssertionError(_("La fecha desde del escenario no puede ser posterior a la fecha hasta."))
        return date_start, date_end

    def countInclusiveDays(self, date_from, date_to):
        """Cuenta dias calendario inclusivos entre dos fechas."""
        return (date_to - date_from).days + 1

    def resolveAttendanceWorkEntryType(self):
        """Resuelve el tipo de entrada por defecto desde registros existentes en BD."""
        type_model = self.getDashboardModel("hr.work.entry.type")
        domain = [("active", "=", True)] if "active" in type_model._fields else []
        attendance = type_model.search(domain + [("code", "=", "WORK100")], limit=1)
        if not attendance and "is_leave" in type_model._fields:
            attendance = type_model.search(domain + [("is_leave", "=", False)], limit=1, order="sequence, id")
        if not attendance:
            attendance = type_model.search(domain + [("name", "ilike", "Asistencia")], limit=1)
        if not attendance:
            attendance = type_model.search(domain, limit=1, order="sequence, id")
        if not attendance:
            raise AssertionError(_("No hay tipos de entrada de trabajo disponibles en la base de datos."))
        return attendance

    def normalizeTestNovelties(self, input_values, period_start, period_end):
        """Valida y normaliza test_novelties del escenario de nomina periodica."""
        raw_novelties = input_values.get("test_novelties") or []
        if not raw_novelties:
            return []
        if not isinstance(raw_novelties, list):
            raise AssertionError(_("test_novelties debe ser una lista de novedades."))

        type_model = self.getDashboardModel("hr.work.entry.type")
        period_days = self.countInclusiveDays(period_start, period_end)
        normalized = []
        novelty_days_total = 0

        for index, raw in enumerate(raw_novelties, start=1):
            if not isinstance(raw, dict):
                raise AssertionError(_("La novedad #%s no tiene un formato valido.") % index)
            work_entry_type_id = raw.get("work_entry_type_id")
            if not work_entry_type_id:
                raise AssertionError(_("La novedad #%s debe indicar work_entry_type_id.") % index)
            work_entry_type = type_model.browse(int(work_entry_type_id))
            if not work_entry_type.exists():
                raise AssertionError(_("La novedad #%s referencia un tipo de entrada inexistente.") % index)

            date_from = self.parseProcessTestDate(raw.get("date_from"))
            date_to = self.parseProcessTestDate(raw.get("date_to"))
            if not date_from or not date_to:
                raise AssertionError(_("La novedad #%s debe indicar date_from y date_to.") % index)
            if date_from > date_to:
                raise AssertionError(
                    _("En la novedad #%s, date_from no puede ser posterior a date_to.") % index
                )
            if date_from < period_start or date_to > period_end:
                raise AssertionError(
                    _(
                        "La novedad #%s debe estar dentro del periodo del escenario (%s - %s)."
                    ) % (index, period_start, period_end)
                )

            days = self.countInclusiveDays(date_from, date_to)
            novelty_days_total += days
            normalized.append({
                "work_entry_type": work_entry_type,
                "date_from": date_from,
                "date_to": date_to,
                "days": days,
            })

        if novelty_days_total > period_days:
            raise AssertionError(
                _(
                    "La suma de dias de las novedades (%s) supera los dias del periodo (%s)."
                ) % (novelty_days_total, period_days)
            )

        for left_index, left in enumerate(normalized):
            for right_index, right in enumerate(normalized):
                if right_index <= left_index:
                    continue
                if left["date_from"] <= right["date_to"] and right["date_from"] <= left["date_to"]:
                    raise AssertionError(
                        _(
                            "Las novedades #%s y #%s se solapan en fechas; una misma fecha no puede tener dos tipos de entrada."
                        ) % (left_index + 1, right_index + 1)
                    )
        return normalized

    def resolveDailyWorkEntryDuration(self):
        """Horas diarias por defecto para una entrada de trabajo de un dia."""
        return 8.0

    def buildDayTypeMapForNovelties(self, period_start, period_end, novelties, attendance_type):
        """Mapa dia -> tipo: novedades definidas y Asistencia en el resto del periodo."""
        day_types = {}
        current = period_start
        while current <= period_end:
            day_types[current] = attendance_type
            current += timedelta(days=1)
        for novelty in novelties:
            work_entry_type = novelty.get("work_entry_type")
            if not work_entry_type:
                continue
            current = novelty["date_from"]
            while current <= novelty["date_to"]:
                day_types[current] = work_entry_type
                current += timedelta(days=1)
        return day_types

    def clearWorkEntriesInPeriod(self, version, period_start, period_end):
        """Elimina entradas de trabajo del contrato en el periodo para poder sobreescribirlas."""
        work_entry_model = self.getDashboardModel("hr.work.entry")
        domain = [
            ("employee_id", "=", version.employee_id.id),
            ("date", ">=", period_start),
            ("date", "<=", period_end),
        ]
        if "version_id" in work_entry_model._fields:
            domain.append(("version_id", "=", version.id))
        existing = work_entry_model.search(domain)
        if not existing:
            return
        if "state" in existing._fields:
            draft_entries = existing.filtered(lambda entry: entry.state != "draft")
            if draft_entries:
                draft_entries.write({"state": "draft"})
        existing.unlink()

    def resolveLeaveTypeForWorkEntryType(self, work_entry_type):
        """Mapea tipo de entrada a hr.leave.type por codigo de nomina compartido en BD."""
        code = work_entry_type.code
        if not code:
            return False
        return self.getDashboardModel("hr.leave.type").search([("code", "=", code)], limit=1)

    def resolveWorkEntryTypeForLeaveType(self, leave_type):
        """Mapea hr.leave.type a hr.work.entry.type por el mismo codigo de nomina."""
        code = leave_type.code
        if not code:
            return False
        return self.getDashboardModel("hr.work.entry.type").search([("code", "=", code)], limit=1)

    def resolveEmployeeEntityForLeaveType(self, employee, leave_type):
        """Resuelve la entidad del empleado segun el tipo de aporte asociado al leave type."""
        contribution = leave_type.type_of_entity_association
        if not contribution or "social_security_entities" not in employee._fields:
            return False
        for setting in employee.social_security_entities:
            if setting.contrib_id.id == contribution.id and setting.partner_id:
                return setting.partner_id
        return False

    def buildProcessLeaveDateTimes(self, employee, date_from, date_to):
        """Construye date_from/date_to datetime en UTC naive a partir de fechas de solicitud."""
        tz_name = employee.tz or self.env.user.tz or "UTC"
        try:
            from pytz import timezone as pytz_timezone
            holiday_tz = pytz_timezone(tz_name)
            from pytz import UTC
            dt_from = holiday_tz.localize(datetime.combine(date_from, time(0, 0, 0))).astimezone(UTC).replace(tzinfo=None)
            dt_to = holiday_tz.localize(datetime.combine(date_to, time(23, 59, 59))).astimezone(UTC).replace(tzinfo=None)
            return dt_from, dt_to
        except Exception:
            return datetime.combine(date_from, time(0, 0, 0)), datetime.combine(date_to, time(23, 59, 59))

    def ensureProcessLeaveAttachment(self, leave):
        """Crea un adjunto temporal si el tipo de ausencia lo exige para aprobar."""
        if not leave.holiday_status_id.obligatory_attachment:
            return
        attachment_model = self.getDashboardModel("ir.attachment")
        existing = attachment_model.search([
            ("res_model", "=", "hr.leave"),
            ("res_id", "=", leave.id),
        ], limit=1)
        if existing:
            return
        attachment_model.create({
            "name": "zue_testing_dashboard_leave.txt",
            "type": "binary",
            "datas": base64.b64encode(b"zue_testing_dashboard"),
            "res_model": "hr.leave",
            "res_id": leave.id,
        })

    def validateProcessLeave(self, leave, mode="forced"):
        """Aprueba/valida la ausencia según el modo de ciclo de vida.

        - draft: no toca el estado.
        - real: action_approve/action_validate; si no queda validate, falla.
        - forced: flujo real y, si falla, escribe state='validate' (fallback del panel).
        """
        if mode == "draft":
            return leave
        self.ensureProcessLeaveAttachment(leave)
        if leave.state == "validate":
            return leave
        leave_to_approve = leave
        if leave.employee_id.company_id:
            leave_to_approve = leave.with_company(leave.employee_id.company_id)
        try:
            if hasattr(leave_to_approve, "action_approve") and leave_to_approve.state in ("confirm", "draft"):
                leave_to_approve.action_approve()
            if leave_to_approve.state != "validate" and hasattr(leave_to_approve, "action_validate"):
                leave_to_approve.action_validate()
        except Exception as error:
            if mode == "real":
                raise AssertionError(_(
                    "No se pudo validar la ausencia con el flujo real: %s"
                ) % error) from error
            leave.write({"state": "validate"})
        if leave.state != "validate":
            if mode == "real":
                raise AssertionError(_(
                    "La ausencia no quedó en estado validado tras el flujo real (estado: %s)."
                ) % (leave.state or "-"))
            leave.write({"state": "validate"})
        return leave

    def createProcessLeaveForNovelty(self, version, novelty):
        """Crea hr.leave cuando el tipo de entrada tiene hr.leave.type con el mismo codigo."""
        work_entry_type = novelty.get("work_entry_type")
        leave_type = novelty.get("leave_type") or (
            self.resolveLeaveTypeForWorkEntryType(work_entry_type) if work_entry_type else False
        )
        if not leave_type:
            return False
        leave_model = self.getDashboardModel("hr.leave")
        employee = version.employee_id
        date_from = novelty["date_from"]
        date_to = novelty["date_to"]
        days = novelty["days"]
        date_from_dt, date_to_dt = self.buildProcessLeaveDateTimes(employee, date_from, date_to)
        values = {
            "name": leave_type.name or (work_entry_type.name if work_entry_type else "") or _("Simulacion dashboard"),
            "employee_id": employee.id,
            "holiday_status_id": leave_type.id,
            "request_date_from": date_from,
            "request_date_to": date_to,
            "date_from": date_from_dt,
            "date_to": date_to_dt,
            "number_of_days": days,
        }
        if leave_type.type_of_entity_association:
            values["type_of_entity"] = leave_type.type_of_entity_association.id
            entity = self.resolveEmployeeEntityForLeaveType(employee, leave_type)
            if entity:
                values["entity"] = entity.id
        if leave_type.is_vacation:
            computed = leave_model.onchange_number_of_massive_days_vacations(
                employee, date_from, date_to
            )
            values.update(computed)
            values["number_of_days"] = (
                (computed.get("business_days") or 0) + (computed.get("holidays") or 0)
            ) or days
        leave = leave_model.create(values)
        leave = self.validateProcessLeave(leave, mode=novelty.get("validate_mode") or "forced")
        self.logFunctionalField(
            _("Ausencia %s") % (leave_type.display_name or leave_type.code),
            "%s - %s" % (date_from, date_to),
        )
        return leave

    def createWorkEntriesForDayTypes(self, version, day_types, leave_by_date=None):
        """Crea en lote las entradas de trabajo del mapa dia -> tipo, con leave_id si aplica."""
        leave_by_date = leave_by_date or {}
        work_entry_model = self.getDashboardModel("hr.work.entry")
        duration = self.resolveDailyWorkEntryDuration()
        vals_list = []
        for entry_date, work_entry_type in sorted(day_types.items(), key=lambda item: item[0]):
            values = {
                "name": work_entry_type.name or work_entry_type.code or _("Entrada de trabajo"),
                "employee_id": version.employee_id.id,
                "work_entry_type_id": work_entry_type.id,
                "date": entry_date,
                "duration": duration,
                "company_id": version.company_id.id,
            }
            if "version_id" in work_entry_model._fields:
                values["version_id"] = version.id
            leave = leave_by_date.get(entry_date)
            if leave and "leave_id" in work_entry_model._fields:
                values["leave_id"] = leave.id
            vals_list.append(values)
        if vals_list:
            work_entry_model.create(vals_list)

    def applyProcessTestWorkEntries(self, version, period_start, period_end, novelties):
        """Crea/sobreescribe entradas de trabajo segun novedades y Asistencia por defecto."""
        attendance_type = self.resolveAttendanceWorkEntryType()
        day_types = self.buildDayTypeMapForNovelties(
            period_start, period_end, novelties, attendance_type
        )
        self.logFunctionalStep(_("Preparar entradas de trabajo del periodo con novedades simuladas."))
        leave_by_date = {}
        created_leaves = []
        for novelty in novelties:
            work_entry_type = novelty.get("work_entry_type")
            leave_type = novelty.get("leave_type")
            novelty_label = (
                (work_entry_type.display_name or work_entry_type.code)
                if work_entry_type
                else (leave_type.display_name or leave_type.code if leave_type else _("Novedad"))
            )
            self.logFunctionalField(
                _("Novedad %s") % novelty_label,
                "%s - %s" % (novelty["date_from"], novelty["date_to"]),
            )
            leave = self.createProcessLeaveForNovelty(version, novelty)
            if not leave:
                continue
            created_leaves.append(leave)
            current = novelty["date_from"]
            while current <= novelty["date_to"]:
                leave_by_date[current] = leave
                current += timedelta(days=1)
        self.clearWorkEntriesInPeriod(version, period_start, period_end)
        self.createWorkEntriesForDayTypes(version, day_types, leave_by_date)
        return created_leaves

    def resolveOvertimeTypeFields(self):
        """Campos float de hr.overtime que corresponden a tipos configurados en BD."""
        overtime_model = self.getDashboardModel("hr.overtime")
        type_model = self.getDashboardModel("hr.type.overtime")
        configured_types = {
            record.type_overtime
            for record in type_model.search([])
            if record.type_overtime
        }
        return [
            field_name
            for field_name in configured_types
            if field_name in overtime_model._fields and overtime_model._fields[field_name].type == "float"
        ]

    def normalizeTestOvertimes(self, input_values, period_start, period_end):
        """Valida horas extra a inyectar en hr.overtime desde tipos existentes en BD."""
        raw_rows = input_values.get("test_overtimes") or []
        if not raw_rows:
            return []
        if not isinstance(raw_rows, list):
            raise AssertionError(_("test_overtimes debe ser una lista."))
        type_model = self.getDashboardModel("hr.type.overtime")
        overtime_fields = set(self.resolveOvertimeTypeFields())
        normalized = []
        for index, raw in enumerate(raw_rows, start=1):
            if not isinstance(raw, dict):
                raise AssertionError(_("La hora extra #%s no tiene un formato valido.") % index)
            type_overtime_id = raw.get("type_overtime_id")
            if not type_overtime_id:
                raise AssertionError(_("La hora extra #%s debe indicar type_overtime_id.") % index)
            type_overtime = type_model.browse(int(type_overtime_id))
            if not type_overtime.exists():
                raise AssertionError(_("La hora extra #%s referencia un tipo inexistente en BD.") % index)
            overtime_field = type_overtime.type_overtime
            if overtime_field not in overtime_fields:
                raise AssertionError(
                    _("El tipo de hora extra #%s no tiene un campo float valido en hr.overtime.") % index
                )
            hours = float(raw.get("hours") or 0.0)
            if hours <= 0:
                raise AssertionError(_("La hora extra #%s debe tener horas mayores a 0.") % index)
            date_from = self.parseProcessTestDate(raw.get("date_from"))
            date_to = self.parseProcessTestDate(raw.get("date_to"))
            if not date_from or not date_to:
                raise AssertionError(_("La hora extra #%s debe indicar date_from y date_to.") % index)
            if date_from > date_to:
                raise AssertionError(_("En la hora extra #%s, date_from no puede ser posterior a date_to.") % index)
            if date_from < period_start or date_to > period_end:
                raise AssertionError(
                    _("La hora extra #%s debe estar dentro del periodo del escenario (%s - %s).")
                    % (index, period_start, period_end)
                )
            normalized.append({
                "type_overtime": type_overtime,
                "overtime_field": overtime_field,
                "hours": hours,
                "date_from": date_from,
                "date_to": date_to,
            })
        return normalized

    def applyProcessTestOvertimes(self, version, overtimes):
        """Crea registros hr.overtime para la simulacion."""
        if not overtimes:
            return
        employee = version.employee_id
        if not employee.branch_id:
            raise AssertionError(
                _("El empleado no tiene sucursal (branch_id); hr.overtime exige branch_id obligatorio.")
            )
        overtime_model = self.getDashboardModel("hr.overtime")
        overtime_fields = self.resolveOvertimeTypeFields()
        vals_list = []
        for overtime in overtimes:
            values = {
                "branch_id": employee.branch_id.id,
                "employee_id": employee.id,
                "date": overtime["date_from"],
                "date_end": overtime["date_to"],
                "justification": _("Simulacion dashboard"),
            }
            if "state" in overtime_model._fields:
                # Usa el primer valor de selection disponible en BD/modelo.
                state_selection = overtime_model._fields["state"].selection or []
                if callable(state_selection):
                    state_selection = state_selection(overtime_model)
                if state_selection:
                    preferred = next(
                        (key for key, _label in state_selection if key == "nuevo"),
                        state_selection[0][0],
                    )
                    values["state"] = preferred
            for field_name in overtime_fields:
                values[field_name] = (
                    overtime["hours"] if field_name == overtime["overtime_field"] else 0.0
                )
            vals_list.append(values)
            self.logFunctionalField(
                _("Hora extra %s") % (overtime["type_overtime"].display_name or overtime["overtime_field"]),
                "%s h | %s - %s" % (overtime["hours"], overtime["date_from"], overtime["date_to"]),
            )
        self.logFunctionalStep(_("Inyectar horas extra (hr.overtime) antes de liquidar."))
        overtime_model.create(vals_list)

    def normalizeTestLoans(self, input_values):
        """Valida prestamos a inyectar como hr.loans aprobado con cuota activa."""
        raw_rows = input_values.get("test_loans") or []
        if not raw_rows:
            return []
        if not isinstance(raw_rows, list):
            raise AssertionError(_("test_loans debe ser una lista."))
        loan_model = self.getDashboardModel("hr.loans")
        rule_model = self.getDashboardModel("hr.salary.rule")
        entity_model = self.getDashboardModel("hr.employee.entities")
        apply_choices = dict(loan_model._fields["apply_charge"].selection or [])
        normalized = []
        for index, raw in enumerate(raw_rows, start=1):
            if not isinstance(raw, dict):
                raise AssertionError(_("El prestamo #%s no tiene un formato valido.") % index)
            salary_rule_id = raw.get("salary_rule_id")
            entity_id = raw.get("entity_id")
            apply_charge = str(raw.get("apply_charge") or "")
            amount = float(raw.get("amount") or 0.0)
            if not salary_rule_id:
                raise AssertionError(_("El prestamo #%s debe indicar salary_rule_id.") % index)
            if not entity_id:
                raise AssertionError(_("El prestamo #%s debe indicar entity_id.") % index)
            if apply_charge not in apply_choices:
                raise AssertionError(_("El prestamo #%s debe indicar apply_charge valido (15/30/0).") % index)
            if amount <= 0:
                raise AssertionError(_("El prestamo #%s debe tener amount mayor a 0.") % index)
            salary_rule = rule_model.browse(int(salary_rule_id))
            entity = entity_model.browse(int(entity_id))
            if not salary_rule.exists():
                raise AssertionError(_("El prestamo #%s referencia una regla salarial inexistente.") % index)
            if not entity.exists():
                raise AssertionError(_("El prestamo #%s referencia una entidad inexistente.") % index)
            normalized.append({
                "salary_rule": salary_rule,
                "entity": entity,
                "apply_charge": apply_charge,
                "amount": amount,
                "final_settlement": bool(raw.get("final_settlement")),
            })
        return normalized

    def resolveLoanPaymentDateInPeriod(self, period_start, period_end, apply_charge):
        """Busca una fecha de cuota valida (15/30 o 28 feb) dentro del periodo."""
        current = period_start
        while current <= period_end:
            if apply_charge == "15" and current.day == 15:
                return current
            if apply_charge == "30":
                if current.month == 2 and current.day == 28:
                    return current
                if current.month != 2 and current.day == 30:
                    return current
            if apply_charge == "0" and current.day in (15, 28, 30):
                if current.month == 2 and current.day == 30:
                    current += timedelta(days=1)
                    continue
                if current.month != 2 and current.day == 28:
                    current += timedelta(days=1)
                    continue
                return current
            current += timedelta(days=1)
        raise AssertionError(
            _(
                "No hay una fecha de cuota valida (%s) dentro del periodo %s - %s para el prestamo."
            ) % (apply_charge, period_start, period_end)
        )

    def applyProcessTestLoans(self, version, period_start, period_end, loans):
        """Crea hr.loans con cuota pendiente y lo aprueba para generar el concepto del contrato."""
        if not loans:
            return
        loan_model = self.getDashboardModel("hr.loans")
        line_model = self.getDashboardModel("hr.loans.line")
        currency = version.company_id.currency_id
        if not currency:
            raise AssertionError(_("La compania del contrato no tiene moneda para crear el prestamo."))
        self.logFunctionalStep(_("Inyectar prestamos con cuota activa antes de liquidar."))
        for loan_data in loans:
            payment_date = self.resolveLoanPaymentDateInPeriod(
                period_start, period_end, loan_data["apply_charge"]
            )
            loan_vals = {
                "employee_id": version.employee_id.id,
                "version_id": version.id,
                "entity_id": loan_data["entity"].id,
                "type_installment": "counts",
                "installment_count": 1,
                "payment_date": payment_date,
                "payment_date_end": payment_date,
                "apply_charge": loan_data["apply_charge"],
                "salary_rule": loan_data["salary_rule"].id,
                "currency_id": currency.id,
                "prestamo_original_amount": loan_data["amount"],
                "prestamo_amount": loan_data["amount"],
                "description": _("Simulacion dashboard"),
                "state": "draft",
            }
            if loan_data.get("final_settlement") and "final_settlement_version" in loan_model._fields:
                loan_vals["final_settlement_version"] = True
            loan = loan_model.create(loan_vals)
            # create inmediato: la cuota se necesita antes de action_approve
            line_model.create({
                "prestamo_id": loan.id,
                "employee_id": version.employee_id.id,
                "currency_id": currency.id,
                "date": payment_date,
                "amount": loan_data["amount"],
                "paid": False,
            })
            loan.action_approve()
            loan_label = "%s | cuota %s | cobro %s" % (
                loan_data["amount"], payment_date, loan_data["apply_charge"],
            )
            if loan_data.get("final_settlement"):
                loan_label = "%s | finiquito saldo total" % loan_label
            self.logFunctionalField(
                _("Prestamo %s") % (loan_data["salary_rule"].display_name or loan_data["salary_rule"].code),
                loan_label,
            )

    def normalizeTestDifferentConcepts(self, input_values, period_start, period_end):
        """Valida conceptos diferentes a inyectar en hr.novelties.different.concepts."""
        raw_rows = input_values.get("test_different_concepts") or []
        if not raw_rows:
            return []
        if not isinstance(raw_rows, list):
            raise AssertionError(_("test_different_concepts debe ser una lista."))
        rule_model = self.getDashboardModel("hr.salary.rule")
        entity_model = self.getDashboardModel("hr.employee.entities")
        normalized = []
        for index, raw in enumerate(raw_rows, start=1):
            if not isinstance(raw, dict):
                raise AssertionError(_("El concepto diferente #%s no tiene un formato valido.") % index)
            salary_rule_id = raw.get("salary_rule_id")
            if not salary_rule_id:
                raise AssertionError(_("El concepto diferente #%s debe indicar salary_rule_id.") % index)
            salary_rule = rule_model.browse(int(salary_rule_id))
            if not salary_rule.exists():
                raise AssertionError(_("El concepto diferente #%s referencia una regla inexistente.") % index)
            concept_date = self.parseProcessTestDate(raw.get("date"))
            if not concept_date:
                raise AssertionError(_("El concepto diferente #%s debe indicar date.") % index)
            if concept_date < period_start or concept_date > period_end:
                raise AssertionError(
                    _("El concepto diferente #%s debe estar dentro del periodo del escenario (%s - %s).")
                    % (index, period_start, period_end)
                )
            if raw.get("amount") in (None, False, ""):
                raise AssertionError(_("El concepto diferente #%s debe indicar amount.") % index)
            amount = float(raw.get("amount"))
            partner = False
            partner_id = raw.get("partner_id")
            if partner_id:
                partner = entity_model.browse(int(partner_id))
                if not partner.exists():
                    raise AssertionError(_("El concepto diferente #%s referencia una entidad inexistente.") % index)
            normalized.append({
                "salary_rule": salary_rule,
                "date": concept_date,
                "amount": amount,
                "description": raw.get("description") or _("Simulacion dashboard"),
                "partner": partner,
            })
        return normalized

    def applyProcessTestDifferentConcepts(self, version, concepts):
        """Crea registros hr.novelties.different.concepts para la simulacion."""
        if not concepts:
            return
        concept_model = self.getDashboardModel("hr.novelties.different.concepts")
        vals_list = []
        for concept in concepts:
            values = {
                "employee_id": version.employee_id.id,
                "salary_rule_id": concept["salary_rule"].id,
                "date": concept["date"],
                "amount": concept["amount"],
                "description": concept["description"],
            }
            if concept["partner"]:
                values["partner_id"] = concept["partner"].id
            vals_list.append(values)
            self.logFunctionalField(
                _("Concepto diferente %s") % (concept["salary_rule"].display_name or concept["salary_rule"].code),
                "%s | %s" % (concept["amount"], concept["date"]),
            )
        self.logFunctionalStep(_("Inyectar conceptos diferentes antes de liquidar."))
        concept_model.create(vals_list)

    def normalizeTestIndependentNovelties(self, input_values, period_start, period_end):
        """Valida novedades a inyectar en hr.novelties.independents."""
        raw_rows = input_values.get("test_independent_novelties") or []
        if not raw_rows:
            return []
        if not isinstance(raw_rows, list):
            raise AssertionError(_("test_independent_novelties debe ser una lista."))
        rule_model = self.getDashboardModel("hr.salary.rule")
        normalized = []
        for index, raw in enumerate(raw_rows, start=1):
            if not isinstance(raw, dict):
                raise AssertionError(_("La novedad independiente #%s no tiene un formato válido.") % index)
            salary_rule_id = raw.get("salary_rule_id")
            if not salary_rule_id:
                raise AssertionError(_("La novedad independiente #%s debe indicar salary_rule_id.") % index)
            salary_rule = rule_model.browse(int(salary_rule_id))
            if not salary_rule.exists():
                raise AssertionError(_("La novedad independiente #%s referencia una regla inexistente.") % index)
            novelty_date = self.parseProcessTestDate(raw.get("date"))
            if not novelty_date:
                raise AssertionError(_("La novedad independiente #%s debe indicar date.") % index)
            if novelty_date < period_start or novelty_date > period_end:
                raise AssertionError(_(
                    "La novedad independiente #%s debe estar dentro del periodo del escenario (%s - %s)."
                ) % (index, period_start, period_end))
            if raw.get("amount") in (None, False, ""):
                raise AssertionError(_("La novedad independiente #%s debe indicar amount.") % index)
            amount = float(raw.get("amount"))
            if amount == 0:
                raise AssertionError(_("La novedad independiente #%s debe tener amount distinto de 0.") % index)
            if "dev_or_ded" in salary_rule._fields:
                if salary_rule.dev_or_ded == "deduccion" and amount > 0:
                    raise AssertionError(_(
                        "La novedad independiente #%s usa una regla de deducción; el valor debe ser negativo."
                    ) % index)
                if salary_rule.dev_or_ded == "devengo" and amount < 0:
                    raise AssertionError(_(
                        "La novedad independiente #%s usa una regla de devengo; el valor debe ser positivo."
                    ) % index)
            normalized.append({
                "salary_rule": salary_rule,
                "date": novelty_date,
                "amount": amount,
                "description": raw.get("description") or "",
            })
        return normalized

    def applyProcessTestIndependentNovelties(self, version, novelties):
        """Crea registros hr.novelties.independents para la simulación (reversible por savepoint)."""
        if not novelties:
            return
        novelty_model = self.getDashboardModel("hr.novelties.independents")
        vals_list = []
        for novelty in novelties:
            values = {
                "employee_id": version.employee_id.id,
                "salary_rule_id": novelty["salary_rule"].id,
                "date": novelty["date"],
                "amount": novelty["amount"],
            }
            if novelty["description"]:
                values["description"] = novelty["description"]
            vals_list.append(values)
            self.logFunctionalField(
                _("Novedad independiente %s") % (
                    novelty["salary_rule"].display_name or novelty["salary_rule"].code
                ),
                "%s | %s" % (novelty["amount"], novelty["date"]),
            )
        self.logFunctionalStep(_("Inyectar novedades independientes antes de liquidar."))
        novelty_model.create(vals_list)

    def normalizeTestWageChanges(self, input_values, period_start, period_end):
        """Valida cambios de salario del periodo para inyectar en hr.contract.change.wage."""
        raw_rows = input_values.get("test_wage_changes") or []
        if not raw_rows:
            return []
        if not isinstance(raw_rows, list):
            raise AssertionError(_("test_wage_changes debe ser una lista."))
        normalized = []
        for index, raw in enumerate(raw_rows, start=1):
            if not isinstance(raw, dict):
                raise AssertionError(_("El cambio de salario #%s no tiene un formato valido.") % index)
            change_date = self.parseProcessTestDate(raw.get("date") or raw.get("date_start"))
            if not change_date:
                raise AssertionError(_("El cambio de salario #%s debe indicar fecha.") % index)
            if change_date < period_start or change_date > period_end:
                raise AssertionError(_(
                    "El cambio de salario #%s esta fuera del periodo de liquidacion (%s - %s)."
                ) % (index, period_start, period_end))
            if raw.get("wage") in (None, False, ""):
                raise AssertionError(_("El cambio de salario #%s debe indicar wage.") % index)
            wage = float(raw.get("wage"))
            if wage <= 0:
                raise AssertionError(_("El cambio de salario #%s debe tener un valor positivo.") % index)
            normalized.append({
                "date_start": change_date,
                "wage": wage,
            })
        return normalized

    def ensurePrimaSalaryTakeForWageChanges(self, wage_changes):
        """Activa prima_salary_take dentro del savepoint cuando hay cambios de salario."""
        if not wage_changes:
            return
        # sudo: parametro global requerido por el motor de prima para promediar salarios
        param = self.env["ir.config_parameter"].sudo()
        current = param.get_param("zue_hr_payroll.prima_salary_take")
        if current in ("True", "1", True):
            return
        param.set_param("zue_hr_payroll.prima_salary_take", "True")
        self.logFunctionalStep(_(
            "Activar temporalmente prima_salary_take para promediar cambios de salario."
        ))

    def ensureCesantiasSalaryTakeForWageChanges(self, wage_changes):
        """Activa cesantias_salary_take dentro del savepoint cuando hay cambios de salario."""
        if not wage_changes:
            return
        # sudo: parametro global requerido por el motor de cesantías para promediar salarios
        param = self.env["ir.config_parameter"].sudo()
        current = param.get_param("zue_hr_payroll.cesantias_salary_take")
        if current in ("True", "1", True):
            return
        param.set_param("zue_hr_payroll.cesantias_salary_take", "True")
        self.logFunctionalStep(_(
            "Activar temporalmente cesantias_salary_take para promediar cambios de salario."
        ))

    def applyProcessTestWageChanges(self, version, wage_changes):
        """Crea registros hr.contract.change.wage para la simulacion de prima."""
        if not wage_changes:
            return
        change_model = self.getDashboardModel("hr.contract.change.wage")
        vals_list = []
        for change in wage_changes:
            values = {
                "version_id": version.id,
                "date_start": change["date_start"],
                "wage": change["wage"],
            }
            if version.job_id:
                values["job_id"] = version.job_id.id
            vals_list.append(values)
            self.logFunctionalField(
                _("Cambio de salario %s") % change["date_start"],
                change["wage"],
            )
        self.logFunctionalStep(_("Inyectar cambios de salario en el periodo antes de liquidar."))
        change_model.create(vals_list)

    def normalizeTestContractConcepts(self, input_values, period_start, period_end):
        """Valida conceptos fijos a inyectar en hr.contract.concepts."""
        raw_rows = input_values.get("test_contract_concepts") or []
        if not raw_rows:
            return []
        if not isinstance(raw_rows, list):
            raise AssertionError(_("test_contract_concepts debe ser una lista."))
        concept_model = self.getDashboardModel("hr.contract.concepts")
        rule_model = self.getDashboardModel("hr.salary.rule")
        entity_model = self.getDashboardModel("hr.employee.entities")
        period_choices = dict(concept_model._fields["period"].selection or [])
        apply_choices = dict(concept_model._fields["aplicar"].selection or [])
        normalized = []
        for index, raw in enumerate(raw_rows, start=1):
            if not isinstance(raw, dict):
                raise AssertionError(_("El concepto fijo #%s no tiene un formato valido.") % index)
            salary_rule_id = raw.get("salary_rule_id") or raw.get("input_id")
            if not salary_rule_id:
                raise AssertionError(_("El concepto fijo #%s debe indicar salary_rule_id.") % index)
            salary_rule = rule_model.browse(int(salary_rule_id))
            if not salary_rule.exists():
                raise AssertionError(_("El concepto fijo #%s referencia una regla inexistente.") % index)
            if raw.get("amount") in (None, False, ""):
                raise AssertionError(_("El concepto fijo #%s debe indicar amount.") % index)
            amount = float(raw.get("amount"))
            period = str(raw.get("period") or "")
            aplicar = str(raw.get("aplicar") or "")
            if period not in period_choices:
                raise AssertionError(_("El concepto fijo #%s debe indicar period valido.") % index)
            if aplicar not in apply_choices:
                raise AssertionError(_("El concepto fijo #%s debe indicar aplicar valido (15/30/0).") % index)
            date_start = self.parseProcessTestDate(raw.get("date_start"))
            date_end = self.parseProcessTestDate(raw.get("date_end"))
            if period == "limited":
                if not date_start or not date_end:
                    raise AssertionError(
                        _("El concepto fijo #%s limitado debe indicar date_start y date_end.") % index
                    )
                if date_start > date_end:
                    raise AssertionError(
                        _("En el concepto fijo #%s, date_start no puede ser posterior a date_end.") % index
                    )
                if date_end < period_start or date_start > period_end:
                    raise AssertionError(
                        _(
                            "El concepto fijo #%s debe solapar el periodo del escenario (%s - %s)."
                        ) % (index, period_start, period_end)
                    )
            partner = False
            partner_id = raw.get("partner_id")
            if partner_id:
                partner = entity_model.browse(int(partner_id))
                if not partner.exists():
                    raise AssertionError(_("El concepto fijo #%s referencia una entidad inexistente.") % index)
            normalized.append({
                "salary_rule": salary_rule,
                "amount": amount,
                "period": period,
                "aplicar": aplicar,
                "date_start": date_start,
                "date_end": date_end,
                "partner": partner,
            })
        return normalized

    def applyProcessTestContractConcepts(self, version, concepts):
        """Crea conceptos fijos aprobados en hr.contract.concepts para la simulacion."""
        if not concepts:
            return
        concept_model = self.getDashboardModel("hr.contract.concepts")
        vals_list = []
        for concept in concepts:
            values = {
                "version_id": version.id,
                "input_id": concept["salary_rule"].id,
                "amount": concept["amount"],
                "period": concept["period"],
                "aplicar": concept["aplicar"],
                "state": "done",
                "detail": _("Simulacion dashboard"),
                "show_voucher": True,
            }
            if concept["date_start"]:
                values["date_start"] = concept["date_start"]
            if concept["date_end"]:
                values["date_end"] = concept["date_end"]
            if concept["partner"]:
                values["partner_id"] = concept["partner"].id
            vals_list.append(values)
            self.logFunctionalField(
                _("Concepto fijo %s") % (concept["salary_rule"].display_name or concept["salary_rule"].code),
                "%s | cobro %s | %s" % (concept["amount"], concept["aplicar"], concept["period"]),
            )
        self.logFunctionalStep(_("Inyectar conceptos fijos del contrato antes de liquidar."))
        concept_model.create(vals_list)

    def applyProcessRetentionProcedureOverride(self, version, input_values):
        """Sobrescribe temporalmente la pestana Tributaria del contrato si el escenario RTF se diligencio."""
        procedure = input_values.get("retention_procedure")
        fixed_value = input_values.get("fixed_value_retention_procedure")
        raw_deductions = input_values.get("test_deductions_rtf")
        has_procedure = bool(procedure)
        has_fixed = fixed_value not in (None, False, "")
        has_deductions = isinstance(raw_deductions, list) and bool(raw_deductions)
        if not has_procedure and not has_fixed and not has_deductions:
            return

        values = {}
        if has_procedure:
            field = version._fields.get("retention_procedure")
            if not field:
                raise AssertionError(_("El contrato no tiene el campo retention_procedure."))
            selection_values = field.selection
            if callable(selection_values):
                selection_values = selection_values(version)
            valid_keys = {key for key, _label in (selection_values or [])}
            procedure = str(procedure)
            if procedure not in valid_keys:
                raise AssertionError(
                    _("Procedimiento RTF invalido: %s. Valores disponibles: %s")
                    % (procedure, ", ".join(sorted(valid_keys)))
                )
            values["retention_procedure"] = procedure
            if procedure == "fixed":
                if not has_fixed:
                    raise AssertionError(_("Debe indicar Valor fijo retencion cuando el procedimiento es Valor fijo."))
                values["fixed_value_retention_procedure"] = float(fixed_value)
        elif has_fixed:
            values["retention_procedure"] = "fixed"
            values["fixed_value_retention_procedure"] = float(fixed_value)

        if values:
            self.logFunctionalField(
                _("Procedimiento RTF del escenario."),
                values.get("retention_procedure") or procedure or "-",
            )
            if "fixed_value_retention_procedure" in values:
                self.logFunctionalField(
                    _("Valor fijo retencion del escenario."),
                    values["fixed_value_retention_procedure"],
                )
            version.write(values)

        if has_deductions:
            deductions = self.normalizeTestRtfDeductions(input_values)
            self.applyProcessTestRtfDeductions(version, deductions)

    def normalizeTestRtfDeductions(self, input_values):
        """Valida deducciones RTF a inyectar en hr.contract.deductions.rtf."""
        raw_rows = input_values.get("test_deductions_rtf") or []
        if not raw_rows:
            return []
        if not isinstance(raw_rows, list):
            raise AssertionError(_("test_deductions_rtf debe ser una lista."))
        rule_model = self.getDashboardModel("hr.salary.rule")
        normalized = []
        for index, raw in enumerate(raw_rows, start=1):
            if not isinstance(raw, dict):
                raise AssertionError(_("La deduccion RTF #%s no tiene un formato valido.") % index)
            salary_rule_id = raw.get("salary_rule_id") or raw.get("input_id")
            if not salary_rule_id:
                raise AssertionError(_("La deduccion RTF #%s debe indicar salary_rule_id.") % index)
            salary_rule = rule_model.browse(int(salary_rule_id))
            if not salary_rule.exists():
                raise AssertionError(_("La deduccion RTF #%s referencia una regla inexistente.") % index)
            if "type_concept" in salary_rule._fields and salary_rule.type_concept != "tributaria":
                raise AssertionError(
                    _("La deduccion RTF #%s debe usar una regla salarial de tipo tributaria.") % index
                )
            date_start = self.parseProcessTestDate(raw.get("date_start"))
            date_end = self.parseProcessTestDate(raw.get("date_end"))
            if not date_start or not date_end:
                raise AssertionError(
                    _("La deduccion RTF #%s debe indicar date_start y date_end.") % index
                )
            if date_start > date_end:
                raise AssertionError(
                    _("En la deduccion RTF #%s, date_start no puede ser posterior a date_end.") % index
                )
            if raw.get("value_total") in (None, False, ""):
                raise AssertionError(_("La deduccion RTF #%s debe indicar value_total.") % index)
            value_total = float(raw.get("value_total"))
            number_months = int(raw.get("number_months") or 0)
            value_monthly = self.computeRtfDeductionMonthlyValue(
                date_start, date_end, value_total, number_months
            )
            normalized.append({
                "salary_rule": salary_rule,
                "date_start": date_start,
                "date_end": date_end,
                "value_total": value_total,
                "value_monthly": value_monthly,
                "number_months": number_months,
            })
        return normalized

    def computeRtfDeductionMonthlyValue(self, date_start, date_end, value_total, number_months=0):
        """Calcula valor mensualizado con la misma logica de hr.contract.deductions.rtf."""
        n_months_dif = round(((date_end - date_start).total_seconds() / 60 / 60 / 24) / 30, 0)
        if n_months_dif == 0:
            raise AssertionError(
                _("La fecha inicial es mayor que la fecha final, por favor verificar.")
            )
        if number_months > 0:
            return value_total / number_months
        return value_total / 12.0

    def applyProcessTestRtfDeductions(self, version, deductions):
        """Reemplaza temporalmente las deducciones RTF del contrato con las del escenario."""
        if not deductions:
            return
        deduction_model = self.getDashboardModel("hr.contract.deductions.rtf")
        existing = deduction_model.search([("version_id", "=", version.id)])
        if existing:
            existing.unlink()
        vals_list = []
        for deduction in deductions:
            vals_list.append({
                "version_id": version.id,
                "input_id": deduction["salary_rule"].id,
                "date_start": deduction["date_start"],
                "date_end": deduction["date_end"],
                "value_total": deduction["value_total"],
                "value_monthly": deduction["value_monthly"],
                "number_months": deduction["number_months"] or 0,
            })
            self.logFunctionalField(
                _("Deduccion RTF %s") % (
                    deduction["salary_rule"].display_name or deduction["salary_rule"].code
                ),
                "%s | %s - %s" % (
                    deduction["value_total"],
                    deduction["date_start"],
                    deduction["date_end"],
                ),
            )
        self.logFunctionalStep(_("Sobrescribir deducciones RTF del contrato antes de liquidar."))
        deduction_model.create(vals_list)

    def generatePayslipsKeepingPreparedWorkEntries(self, payslip_run, version):
        """Ejecuta generate_payslips sin regenerar las entradas ya preparadas."""
        version_model = self.getDashboardModel("hr.version")
        model_cls = type(version_model)
        if not hasattr(model_cls, "generate_work_entries"):
            payslip_run.generate_payslips([version.id])
            return
        original_generate = model_cls.generate_work_entries

        def keepPreparedWorkEntries(versions, date_start, date_end, *args, **kwargs):
            return True

        model_cls.generate_work_entries = keepPreparedWorkEntries
        try:
            payslip_run.generate_payslips([version.id])
        finally:
            model_cls.generate_work_entries = original_generate

    def buildPayslipRunValuesForProcessTest(self, input_values, version, structure, use_work_entries=False):
        """Arma los valores del lote con los campos que el usuario diligencia al liquidar."""
        run_values = {
            "name": "Lote prueba dashboard",
            "company_id": version.company_id.id,
            "structure_id": structure.id,
            "date_start": input_values.get("date_start") or date.today().replace(day=1),
            "date_end": input_values.get("date_end") or date.today(),
            "z_filter_state_finished": "open",
            "method_schedule_pay": version.method_schedule_pay or "monthly",
        }
        if "use_worked_day_lines" in self.getDashboardModel("hr.payslip.run")._fields:
            # Con novedades se usan hr.work.entry; sin novedades se mantiene el comportamiento actual.
            run_values["use_worked_day_lines"] = bool(use_work_entries)
        return run_values

    def extractPayslipCalculationLines(self, payslip):
        """Devuelve la lista completa de conceptos de la pestana Calculo del salario."""
        lines = []
        for line in payslip.line_ids.sorted(key=lambda item: (item.sequence, item.id)):
            lines.append({
                "code": line.code or "",
                "name": line.name or "",
                "category": line.category_id.display_name if line.category_id else "",
                "quantity": float(line.quantity or 0.0),
                "amount": float(line.amount or 0.0),
                "total": float(line.total or 0.0),
            })
            self.logFunctionalField(
                _("Concepto %s - %s") % (line.code or "-", line.name or "-"),
                line.total,
            )
        return lines

    def extractPayslipWorkedDaysLines(self, payslip):
        """Devuelve las lineas de la pestana Dias trabajados del recibo."""
        lines = []
        for line in payslip.worked_days_line_ids.sorted(key=lambda item: (item.sequence, item.id)):
            work_type = line.work_entry_type_id
            lines.append({
                "code": line.code or (work_type.code if work_type else ""),
                "name": line.name or (work_type.name if work_type else ""),
                "number_of_days": float(line.number_of_days or 0.0),
                "number_of_hours": float(line.number_of_hours or 0.0),
            })
            self.logFunctionalField(
                _("Dia trabajado %s - %s") % (line.code or "-", line.name or "-"),
                line.number_of_days,
            )
        return lines

    def extractPayslipNotAppliedLines(self, payslip):
        """Devuelve las reglas no aplicadas cuando el modelo las expone."""
        if "not_line_ids" not in payslip._fields:
            return []
        lines = []
        for line in payslip.not_line_ids.sorted(key=lambda item: (item.sequence, item.id)):
            lines.append({
                "code": line.code or "",
                "name": line.name or "",
                "category": line.category_id.display_name if line.category_id else "",
                "quantity": float(line.quantity or 0.0),
                "amount": float(line.amount or 0.0),
                "total": float(line.total or 0.0),
            })
        return lines

    def extractPayslipObtainedInfo(self, payslip):
        """Resumen informativo del recibo generado por la simulacion."""
        info = [
            {"label": _("Empleado"), "value": payslip.employee_id.display_name or ""},
            {"label": _("Contrato"), "value": payslip.version_id.display_name or ""},
            {"label": _("Estructura"), "value": payslip.struct_id.display_name or ""},
            {"label": _("Fecha desde"), "value": str(payslip.date_from or "")},
            {"label": _("Fecha hasta"), "value": str(payslip.date_to or "")},
        ]
        wage = 0.0
        if "wage" in payslip._fields:
            wage = float(payslip.wage or 0.0)
        elif payslip.version_id and "wage" in payslip.version_id._fields:
            wage = float(payslip.version_id.wage or 0.0)
        info.append({"label": _("Salario"), "value": wage})
        if "basic_wage" in payslip._fields:
            info.append({"label": _("Basico"), "value": float(payslip.basic_wage or 0.0)})
        if "net_wage" in payslip._fields:
            info.append({"label": _("Neto"), "value": float(payslip.net_wage or 0.0)})
        return info

    def testSimulatePeriodicPayroll(self, input_values=None):
        """Simula la liquidacion periodica con reglas salariales y datos parametricos de BD."""
        input_values = input_values or {}
        self.logFunctionalStep(_("Simular liquidacion de nomina periodica."))
        version = self.resolveVersionForProcessTest(input_values)
        structure = self.resolvePeriodicPayrollStructure()
        period_start, period_end = self.resolveScenarioPeriod(input_values)
        novelties = self.normalizeTestNovelties(input_values, period_start, period_end)
        overtimes = self.normalizeTestOvertimes(input_values, period_start, period_end)
        loans = self.normalizeTestLoans(input_values)
        different_concepts = self.normalizeTestDifferentConcepts(input_values, period_start, period_end)
        contract_concepts = self.normalizeTestContractConcepts(input_values, period_start, period_end)
        run_values = self.buildPayslipRunValuesForProcessTest(
            input_values,
            version,
            structure,
            use_work_entries=bool(novelties),
        )
        run_values["date_start"] = period_start
        run_values["date_end"] = period_end
        self.logFunctionalField(_("Asignar contrato a liquidar."), version.display_name)
        self.logFunctionalField(_("Asignar empleado."), version.employee_id.display_name)
        self.logFunctionalField(_("Asignar estructura salarial."), structure.display_name)
        self.logFunctionalField(_("Asignar fecha inicial del lote."), period_start)
        self.logFunctionalField(_("Asignar fecha final del lote."), period_end)
        self.applyProcessRetentionProcedureOverride(version, input_values)
        if novelties:
            self.applyProcessTestWorkEntries(version, period_start, period_end, novelties)
        self.applyProcessTestOvertimes(version, overtimes)
        self.applyProcessTestLoans(version, period_start, period_end, loans)
        self.applyProcessTestDifferentConcepts(version, different_concepts)
        self.applyProcessTestContractConcepts(version, contract_concepts)
        payslip_run = self.getDashboardModel("hr.payslip.run").create(run_values)
        self.logFunctionalStep(_("Generar nominas del lote con el metodo real generate_payslips."))
        if novelties:
            self.generatePayslipsKeepingPreparedWorkEntries(payslip_run, version)
        else:
            payslip_run.generate_payslips([version.id])
        payslip = payslip_run.slip_ids.filtered(lambda slip: slip.version_id == version)[:1]
        if not payslip:
            raise AssertionError(_("No se genero la nomina del contrato seleccionado."))
        self.logFunctionalStep(_("Obtener dias trabajados del recibo."))
        worked_days_lines = self.extractPayslipWorkedDaysLines(payslip)
        self.logFunctionalStep(_("Obtener conceptos de la pestana Calculo del salario."))
        calculated_lines = self.extractPayslipCalculationLines(payslip)
        if not calculated_lines:
            raise AssertionError(_("La liquidacion no genero conceptos salariales."))
        not_applied_lines = self.extractPayslipNotAppliedLines(payslip)
        obtained_info = self.extractPayslipObtainedInfo(payslip)
        self.logFunctionalStep(_("Finalizar simulacion completa de la liquidacion."))
        if self.hasDashboardProvider():
            self.provider.completeProcessTest(
                calculated_lines=calculated_lines,
                worked_days_lines=worked_days_lines,
                not_applied_lines=not_applied_lines,
                obtained_info=obtained_info,
                message=_("Nómina periódica simulada correctamente."),
            )
        return calculated_lines

    def testSimulatePrima(self, input_values=None):
        """Simula la liquidacion de prima con estructura process=prima y metodos reales."""
        input_values = input_values or {}
        self.logFunctionalStep(_("Simular liquidacion de prima."))
        version = self.resolveVersionForProcessTest(input_values)
        if not version.contract_date_start:
            raise AssertionError(_(
                "El contrato seleccionado no tiene fecha de inicio (contract_date_start); "
                "es requerida para liquidar prima."
            ))
        structure = self.resolvePrimaPayrollStructure()
        period_start, period_end = self.resolveScenarioPeriod(input_values)
        novelties = self.normalizeTestNovelties(input_values, period_start, period_end)
        wage_changes = self.normalizeTestWageChanges(input_values, period_start, period_end)
        run_values = self.buildPayslipRunValuesForProcessTest(
            input_values,
            version,
            structure,
            use_work_entries=bool(novelties),
        )
        run_values["date_start"] = period_start
        run_values["date_end"] = period_end
        self.logFunctionalField(_("Asignar contrato a liquidar."), version.display_name)
        self.logFunctionalField(_("Asignar empleado."), version.employee_id.display_name)
        self.logFunctionalField(_("Asignar estructura salarial."), structure.display_name)
        self.logFunctionalField(_("Asignar fecha inicial del lote."), period_start)
        self.logFunctionalField(_("Asignar fecha final del lote."), period_end)
        self.ensurePrimaSalaryTakeForWageChanges(wage_changes)
        self.sanitizeProcessHistoryAccrualDates(version, "prima")
        if novelties:
            self.applyProcessTestWorkEntries(version, period_start, period_end, novelties)
        self.applyProcessTestWageChanges(version, wage_changes)
        payslip_run = self.getDashboardModel("hr.payslip.run").create(run_values)
        self.logFunctionalStep(_("Generar nominas del lote con el metodo real generate_payslips (prima)."))
        if novelties:
            self.generatePayslipsKeepingPreparedWorkEntries(payslip_run, version)
        else:
            payslip_run.generate_payslips([version.id])
        payslip = payslip_run.slip_ids.filtered(lambda slip: slip.version_id == version)[:1]
        if not payslip:
            raise AssertionError(_("No se genero la nomina de prima del contrato seleccionado."))
        self.logFunctionalStep(_("Obtener dias trabajados del recibo."))
        worked_days_lines = self.extractPayslipWorkedDaysLines(payslip)
        self.logFunctionalStep(_("Obtener conceptos de la pestana Calculo del salario."))
        calculated_lines = self.extractPayslipCalculationLines(payslip)
        not_applied_lines = self.extractPayslipNotAppliedLines(payslip)
        obtained_info = self.extractPayslipObtainedInfo(payslip)
        self.logFunctionalStep(_("Finalizar simulacion completa de la liquidacion de prima."))
        if self.hasDashboardProvider():
            self.provider.completeProcessTest(
                calculated_lines=calculated_lines,
                worked_days_lines=worked_days_lines,
                not_applied_lines=not_applied_lines,
                obtained_info=obtained_info,
                message=_("Liquidación de prima simulada correctamente."),
            )
        return calculated_lines

    def runSimulateCesantiasProcess(self, structure_process, input_values=None):
        """Simula cesantías o intereses de cesantías con el motor real."""
        input_values = input_values or {}
        label = (
            _("intereses de cesantías")
            if structure_process == "intereses_cesantias"
            else _("cesantías")
        )
        self.logFunctionalStep(_("Simular liquidación de %s.") % label)
        version = self.resolveVersionForProcessTest(input_values)
        structure = self.resolveCesantiasPayrollStructure(structure_process)
        period_start, period_end = self.resolveScenarioPeriod(input_values)
        novelties = self.normalizeTestNovelties(input_values, period_start, period_end)
        wage_changes = self.normalizeTestWageChanges(input_values, period_start, period_end)
        advance = self.normalizeTestSeveranceAdvance(input_values)
        run_values = self.buildPayslipRunValuesForProcessTest(
            input_values,
            version,
            structure,
            use_work_entries=bool(novelties),
        )
        run_values["date_start"] = period_start
        run_values["date_end"] = period_end
        self.logFunctionalField(_("Asignar contrato a liquidar."), version.display_name)
        self.logFunctionalField(_("Asignar empleado."), version.employee_id.display_name)
        self.logFunctionalField(_("Asignar estructura salarial."), structure.display_name)
        self.logFunctionalField(_("Asignar fecha inicial del lote."), period_start)
        self.logFunctionalField(_("Asignar fecha final del lote."), period_end)
        self.ensureCesantiasSalaryTakeForWageChanges(wage_changes)
        self.sanitizeProcessHistoryAccrualDates(version, structure_process)
        if novelties:
            self.applyProcessTestWorkEntries(version, period_start, period_end, novelties)
        self.applyProcessTestWageChanges(version, wage_changes)
        payslip_run = self.getDashboardModel("hr.payslip.run").create(run_values)
        self.logFunctionalStep(_(
            "Generar nóminas del lote con el método real generate_payslips (%s)."
        ) % structure_process)
        if novelties:
            self.generatePayslipsKeepingPreparedWorkEntries(payslip_run, version)
        else:
            payslip_run.generate_payslips([version.id])
        payslip = payslip_run.slip_ids.filtered(lambda slip: slip.version_id == version)[:1]
        if not payslip:
            raise AssertionError(_(
                "No se generó la nómina de %s del contrato seleccionado."
            ) % label)
        payslip = self.applyProcessTestSeveranceAdvance(payslip, advance)
        self.logFunctionalStep(_("Obtener días trabajados del recibo."))
        worked_days_lines = self.extractPayslipWorkedDaysLines(payslip)
        self.logFunctionalStep(_("Obtener conceptos de la pestaña Cálculo del salario."))
        calculated_lines = self.extractPayslipCalculationLines(payslip)
        not_applied_lines = self.extractPayslipNotAppliedLines(payslip)
        obtained_info = self.extractPayslipObtainedInfo(payslip)
        self.logFunctionalStep(_("Finalizar simulación completa de la liquidación de %s.") % label)
        if self.hasDashboardProvider():
            self.provider.completeProcessTest(
                calculated_lines=calculated_lines,
                worked_days_lines=worked_days_lines,
                not_applied_lines=not_applied_lines,
                obtained_info=obtained_info,
                message=_(
                    "Liquidación de intereses de cesantías simulada correctamente."
                ) if structure_process == "intereses_cesantias" else _(
                    "Liquidación de cesantías simulada correctamente."
                ),
            )
        return calculated_lines

    def testSimulateCesantias(self, input_values=None):
        """Simula liquidación de cesantías con estructura process=cesantias."""
        return self.runSimulateCesantiasProcess("cesantias", input_values=input_values)

    def testSimulateInteresesCesantias(self, input_values=None):
        """Simula liquidación de intereses con estructura process=intereses_cesantias."""
        return self.runSimulateCesantiasProcess("intereses_cesantias", input_values=input_values)

    def resolveVacacionesPayrollStructure(self):
        structure_model = self.getDashboardModel("hr.payroll.structure")
        structure = structure_model.search([("process", "=", "vacaciones")], limit=1)
        if not structure:
            raise AssertionError(_("No hay estructura salarial de vacaciones disponible en la base de datos."))
        return structure

    def ensureVacacionesStandaloneCalculation(self):
        """Con process=vacaciones, VACDISFRUTADAS solo corre si no se liquidan en nómina.

        El motor lee el parámetro con bool(get_param(...)): bool(\"False\") es True en Python,
        así que hay que eliminar el parámetro (set_param False) y no guardar el string \"False\".
        """
        # sudo: parametro global requerido por el motor de vacaciones
        param = self.env["ir.config_parameter"].sudo()
        current = param.get_param("zue_hr_payroll.pay_vacations_in_payroll")
        if current:
            param.set_param("zue_hr_payroll.pay_vacations_in_payroll", False)
            self.logFunctionalStep(_(
                "Desactivar temporalmente «liquidar vacaciones en nómina» "
                "para calcular VACDISFRUTADAS en process=vacaciones."
            ))

    def resolveVacationLeaveType(self):
        leave_type = self.getDashboardModel("hr.leave.type").search([("is_vacation", "=", True)], limit=1)
        if not leave_type:
            raise AssertionError(_(
                "No hay tipo de ausencia marcado como vacaciones (is_vacation) en la base de datos."
            ))
        return leave_type

    def resolveVacationWorkEntryType(self, leave_type):
        type_model = self.getDashboardModel("hr.work.entry.type")
        if "work_entry_type_id" in leave_type._fields and leave_type.work_entry_type_id:
            return leave_type.work_entry_type_id
        if leave_type.code:
            work_entry_type = type_model.search([("code", "=", leave_type.code)], limit=1)
            if work_entry_type:
                return work_entry_type
        work_entry_type = type_model.search([("code", "=", "VACDISFRUTADAS")], limit=1)
        if work_entry_type:
            return work_entry_type
        raise AssertionError(_(
            "No se encontró tipo de entrada de trabajo para vacaciones disfrutadas "
            "(código del leave type o VACDISFRUTADAS)."
        ))

    def normalizeTestEnjoyedVacations(self, input_values, period_start, period_end):
        """Valida vacaciones disfrutadas (Desde/Hasta) dentro del periodo, sin solapes."""
        raw_rows = input_values.get("test_enjoyed_vacations") or []
        if not raw_rows:
            return []
        if not isinstance(raw_rows, list):
            raise AssertionError(_("test_enjoyed_vacations debe ser una lista."))
        leave_type = self.resolveVacationLeaveType()
        work_entry_type = self.resolveVacationWorkEntryType(leave_type)
        period_days = self.countInclusiveDays(period_start, period_end)
        normalized = []
        total_days = 0
        for index, raw in enumerate(raw_rows, start=1):
            if not isinstance(raw, dict):
                raise AssertionError(_("La vacación disfrutada #%s no tiene un formato válido.") % index)
            date_from = self.parseProcessTestDate(raw.get("date_from"))
            date_to = self.parseProcessTestDate(raw.get("date_to"))
            if not date_from or not date_to:
                raise AssertionError(_("La vacación disfrutada #%s debe indicar Desde y Hasta.") % index)
            if date_from > date_to:
                raise AssertionError(_(
                    "En la vacación disfrutada #%s, Desde no puede ser posterior a Hasta."
                ) % index)
            if date_from < period_start or date_to > period_end:
                raise AssertionError(_(
                    "La vacación disfrutada #%s debe estar dentro del periodo del recibo (%s - %s)."
                ) % (index, period_start, period_end))
            days = self.countInclusiveDays(date_from, date_to)
            total_days += days
            normalized.append({
                "work_entry_type": work_entry_type,
                "leave_type": leave_type,
                "date_from": date_from,
                "date_to": date_to,
                "days": days,
            })
        if total_days > period_days:
            raise AssertionError(_(
                "La suma de días de vacaciones disfrutadas (%s) supera los días del periodo (%s)."
            ) % (total_days, period_days))
        for left_index, left in enumerate(normalized):
            for right_index, right in enumerate(normalized):
                if right_index <= left_index:
                    continue
                if left["date_from"] <= right["date_to"] and right["date_from"] <= left["date_to"]:
                    raise AssertionError(_(
                        "Las vacaciones disfrutadas #%s y #%s se solapan en fechas."
                    ) % (left_index + 1, right_index + 1))
        return normalized

    def normalizeTestPaidVacations(self, input_values, period_start, period_end):
        """Valida líneas de vacaciones remuneradas (días + fecha inicial)."""
        raw_rows = input_values.get("test_paid_vacations") or []
        if not raw_rows:
            return []
        if not isinstance(raw_rows, list):
            raise AssertionError(_("test_paid_vacations debe ser una lista."))
        normalized = []
        for index, raw in enumerate(raw_rows, start=1):
            if not isinstance(raw, dict):
                raise AssertionError(_("La vacación remunerada #%s no tiene un formato válido.") % index)
            days = int(raw.get("paid_vacation_days") or 0)
            if days <= 0:
                raise AssertionError(_("La vacación remunerada #%s debe tener días mayores a 0.") % index)
            start_date = self.parseProcessTestDate(raw.get("start_date_paid_vacation"))
            if not start_date:
                raise AssertionError(_("La vacación remunerada #%s debe indicar Fecha inicial.") % index)
            if start_date < period_start or start_date > period_end:
                raise AssertionError(_(
                    "La fecha inicial de la vacación remunerada #%s debe estar dentro del periodo del recibo."
                ) % index)
            computed = self.computePaidVacationLineDates(start_date, days)
            normalized.append(computed)
        return normalized

    def computePaidVacationLineDates(self, start_date, paid_days):
        """Réplica del onchange de hr.payslip.paid.vacation (fecha final y día 31)."""
        date_to = start_date - timedelta(days=1)
        cant_days = paid_days
        days = 0
        days_31 = 0
        while cant_days > 0:
            date_add = date_to + timedelta(days=1)
            cant_days -= 1
            days += 1
            days_31 += 1 if date_add.day == 31 else 0
            date_to = date_add
        return {
            "paid_vacation_days": days - days_31,
            "start_date_paid_vacation": start_date,
            "end_date_paid_vacation": date_to,
        }

    def applyProcessTestPaidVacations(self, payslip, paid_rows):
        """Crea paid_vacation_ids en el recibo y recalcula con el motor real."""
        if not paid_rows:
            return payslip
        if "paid_vacation_ids" not in payslip._fields:
            raise AssertionError(_("El recibo no expone paid_vacation_ids para vacaciones remuneradas."))
        line_commands = [(5, 0, 0)]
        for row in paid_rows:
            line_commands.append((0, 0, {
                "paid_vacation_days": row["paid_vacation_days"],
                "start_date_paid_vacation": row["start_date_paid_vacation"],
                "end_date_paid_vacation": row["end_date_paid_vacation"],
            }))
            self.logFunctionalField(
                _("Vacación remunerada"),
                "%s días | %s - %s" % (
                    row["paid_vacation_days"],
                    row["start_date_paid_vacation"],
                    row["end_date_paid_vacation"],
                ),
            )
        payslip.write({"paid_vacation_ids": line_commands})
        self.logFunctionalStep(_("Recalcular recibo con vacaciones remuneradas."))
        payslip.compute_sheet()
        return payslip

    def testSimulateVacaciones(self, input_values=None):
        """Simula liquidación de vacaciones con estructura process=vacaciones."""
        input_values = input_values or {}
        self.logFunctionalStep(_("Simular liquidación de vacaciones."))
        version = self.resolveVersionForProcessTest(input_values)
        if not version.contract_date_start:
            raise AssertionError(_(
                "El contrato seleccionado no tiene fecha de inicio (contract_date_start); "
                "es requerida para liquidar vacaciones."
            ))
        structure = self.resolveVacacionesPayrollStructure()
        period_start, period_end = self.resolveScenarioPeriod(input_values)
        enjoyed = self.normalizeTestEnjoyedVacations(input_values, period_start, period_end)
        paid_rows = self.normalizeTestPaidVacations(input_values, period_start, period_end)
        if not enjoyed and not paid_rows:
            raise AssertionError(_(
                "Debe agregar Vacaciones disfrutadas o Vacaciones remuneradas para simular la liquidación."
            ))
        run_values = self.buildPayslipRunValuesForProcessTest(
            input_values,
            version,
            structure,
            use_work_entries=bool(enjoyed),
        )
        run_values["date_start"] = period_start
        run_values["date_end"] = period_end
        self.logFunctionalField(_("Asignar contrato a liquidar."), version.display_name)
        self.logFunctionalField(_("Asignar empleado."), version.employee_id.display_name)
        self.logFunctionalField(_("Asignar estructura salarial."), structure.display_name)
        self.logFunctionalField(_("Asignar fecha inicial del lote."), period_start)
        self.logFunctionalField(_("Asignar fecha final del lote."), period_end)
        self.ensureVacacionesStandaloneCalculation()
        if enjoyed:
            self.applyProcessTestWorkEntries(version, period_start, period_end, enjoyed)
        payslip_run = self.getDashboardModel("hr.payslip.run").create(run_values)
        self.logFunctionalStep(_(
            "Generar nóminas del lote con el método real generate_payslips (vacaciones)."
        ))
        if enjoyed:
            self.generatePayslipsKeepingPreparedWorkEntries(payslip_run, version)
        else:
            payslip_run.generate_payslips([version.id])
        payslip = payslip_run.slip_ids.filtered(lambda slip: slip.version_id == version)[:1]
        if not payslip:
            raise AssertionError(_("No se generó la nómina de vacaciones del contrato seleccionado."))
        if paid_rows:
            payslip = self.applyProcessTestPaidVacations(payslip, paid_rows)
        elif not payslip.line_ids:
            self.logFunctionalStep(_("Recalcular recibo de vacaciones."))
            payslip.compute_sheet()
        self.logFunctionalStep(_("Obtener días trabajados del recibo."))
        worked_days_lines = self.extractPayslipWorkedDaysLines(payslip)
        self.logFunctionalStep(_("Obtener conceptos de la pestaña Cálculo del salario."))
        calculated_lines = self.extractPayslipCalculationLines(payslip)
        not_applied_lines = self.extractPayslipNotAppliedLines(payslip)
        obtained_info = self.extractPayslipObtainedInfo(payslip)
        self.logFunctionalStep(_("Finalizar simulación completa de la liquidación de vacaciones."))
        if self.hasDashboardProvider():
            self.provider.completeProcessTest(
                calculated_lines=calculated_lines,
                worked_days_lines=worked_days_lines,
                not_applied_lines=not_applied_lines,
                obtained_info=obtained_info,
                message=_("Liquidación de vacaciones simulada correctamente."),
            )
        return calculated_lines

    def generateContratoPayslipsDeferredCompute(self, payslip_run, version, use_work_entries=False):
        """Crea el recibo con generate_payslips sin compute_sheet (fechas de contrato aún no escritas)."""
        payslip_model = self.getDashboardModel("hr.payslip")
        model_cls = type(payslip_model)
        original_compute = model_cls.compute_sheet

        def skipComputeSheet(records):
            return True

        model_cls.compute_sheet = skipComputeSheet
        try:
            if use_work_entries:
                self.generatePayslipsKeepingPreparedWorkEntries(payslip_run, version)
            else:
                payslip_run.generate_payslips([version.id])
        finally:
            model_cls.compute_sheet = original_compute

    def testSimulateLiquidacionContrato(self, input_values=None):
        """Simula liquidación de contrato (process=contrato → _get_payslip_lines_contrato)."""
        input_values = input_values or {}
        self.logFunctionalStep(_("Simular liquidación de contrato."))
        version = self.resolveVersionForProcessTest(input_values)
        structure = self.resolveContratoPayrollStructure()
        period_start, period_end = self.resolveScenarioPeriod(input_values)
        run_values = self.buildPayslipRunValuesForProcessTest(
            input_values,
            version,
            structure,
            use_work_entries=False,
        )
        run_values["date_start"] = period_start
        run_values["date_end"] = period_end
        self.logFunctionalField(_("Asignar contrato a liquidar."), version.display_name)
        self.logFunctionalField(_("Asignar empleado."), version.employee_id.display_name)
        self.logFunctionalField(_("Asignar estructura salarial."), structure.display_name)
        self.logFunctionalField(_("Asignar fecha inicial del lote."), period_start)
        self.logFunctionalField(_("Asignar fecha final del lote."), period_end)
        self.sanitizeProcessHistoryAccrualDates(version, "contrato")
        payslip_run = self.getDashboardModel("hr.payslip.run").create(run_values)
        self.logFunctionalStep(_(
            "Generar nóminas del lote con el método real generate_payslips (contrato)."
        ))
        self.generateContratoPayslipsDeferredCompute(
            payslip_run, version, use_work_entries=False,
        )
        payslip = payslip_run.slip_ids.filtered(lambda slip: slip.version_id == version)[:1]
        if not payslip:
            raise AssertionError(_("No se generó la nómina de liquidación del contrato seleccionado."))
        payslip = self.applyContratoPayslipFields(payslip, input_values, version, period_end)
        self.logFunctionalStep(_("Obtener días trabajados del recibo."))
        worked_days_lines = self.extractPayslipWorkedDaysLines(payslip)
        self.logFunctionalStep(_("Obtener conceptos de la pestaña Cálculo del salario."))
        calculated_lines = self.extractPayslipCalculationLines(payslip)
        if not calculated_lines:
            raise AssertionError(_("La liquidación de contrato no generó conceptos salariales."))
        not_applied_lines = self.extractPayslipNotAppliedLines(payslip)
        obtained_info = self.extractPayslipObtainedInfo(payslip)
        if "date_liquidacion" in payslip._fields:
            obtained_info.append({
                "label": _("Fecha liquidación"),
                "value": str(payslip.date_liquidacion or ""),
            })
        self.logFunctionalStep(_("Finalizar simulación completa de la liquidación de contrato."))
        if self.hasDashboardProvider():
            self.provider.completeProcessTest(
                calculated_lines=calculated_lines,
                worked_days_lines=worked_days_lines,
                not_applied_lines=not_applied_lines,
                obtained_info=obtained_info,
                message=_("Liquidación de contrato simulada correctamente."),
            )
        return calculated_lines

    def resolveIndependentPayrollStructure(self):
        structure_model = self.getDashboardModel("hr.payroll.structure")
        structure = structure_model.search([("process", "=", "otro")], limit=1)
        if not structure:
            raise AssertionError(_(
                "No hay estructura salarial de nómina independiente (process=otro) disponible en la base de datos."
            ))
        return structure

    def testSimulateNominaIndependiente(self, input_values=None):
        """Simula nómina independiente (process=otro → _get_payslip_lines_other)."""
        input_values = input_values or {}
        self.logFunctionalStep(_("Simular liquidación de nómina independiente."))
        version = self.resolveVersionForProcessTest(input_values)
        structure = self.resolveIndependentPayrollStructure()
        period_start, period_end = self.resolveScenarioPeriod(input_values)
        independent_novelties = self.normalizeTestIndependentNovelties(
            input_values, period_start, period_end,
        )
        run_values = self.buildPayslipRunValuesForProcessTest(
            input_values,
            version,
            structure,
            use_work_entries=False,
        )
        run_values["date_start"] = period_start
        run_values["date_end"] = period_end
        self.logFunctionalField(_("Asignar contrato a liquidar."), version.display_name)
        self.logFunctionalField(_("Asignar empleado."), version.employee_id.display_name)
        self.logFunctionalField(_("Asignar estructura salarial."), structure.display_name)
        self.logFunctionalField(_("Asignar fecha inicial del lote."), period_start)
        self.logFunctionalField(_("Asignar fecha final del lote."), period_end)
        self.applyProcessTestIndependentNovelties(version, independent_novelties)
        payslip_run = self.getDashboardModel("hr.payslip.run").create(run_values)
        self.logFunctionalStep(_(
            "Generar nóminas del lote con el método real generate_payslips (nómina independiente)."
        ))
        payslip_run.generate_payslips([version.id])
        payslip = payslip_run.slip_ids.filtered(lambda slip: slip.version_id == version)[:1]
        if not payslip:
            raise AssertionError(_(
                "No se generó la nómina independiente del contrato seleccionado."
            ))
        self.logFunctionalStep(_("Obtener días trabajados del recibo."))
        worked_days_lines = self.extractPayslipWorkedDaysLines(payslip)
        self.logFunctionalStep(_("Obtener conceptos de la pestaña Cálculo del salario."))
        calculated_lines = self.extractPayslipCalculationLines(payslip)
        if not calculated_lines:
            raise AssertionError(_(
                "La liquidación de nómina independiente no generó conceptos salariales."
            ))
        not_applied_lines = self.extractPayslipNotAppliedLines(payslip)
        obtained_info = self.extractPayslipObtainedInfo(payslip)
        self.logFunctionalStep(_(
            "Finalizar simulación completa de la liquidación de nómina independiente."
        ))
        if self.hasDashboardProvider():
            self.provider.completeProcessTest(
                calculated_lines=calculated_lines,
                worked_days_lines=worked_days_lines,
                not_applied_lines=not_applied_lines,
                obtained_info=obtained_info,
                message=_("Nómina independiente simulada correctamente."),
            )
        return calculated_lines

    def resolveSocialSecurityPeriod(self, input_values):
        """Resuelve año/mes del escenario y el rango calendario del periodo."""
        try:
            year = int(input_values.get("year") or 0)
        except (TypeError, ValueError):
            year = 0
        month_raw = input_values.get("month")
        try:
            month = int(month_raw or 0)
        except (TypeError, ValueError):
            month = 0
        if self.hasDashboardProvider():
            if year < 2000 or year > 2100:
                raise AssertionError(_("Debe indicar un año válido para seguridad social."))
            if month < 1 or month > 12:
                raise AssertionError(_("Debe indicar un mes válido (1-12) para seguridad social."))
        else:
            today = date.today()
            year = year or today.year
            month = month or today.month
        date_start = date(year, month, 1)
        date_end = (date_start + relativedelta(months=1)) - timedelta(days=1)
        return year, str(month), date_start, date_end

    def ensureValidatedPayslipForSocialSecurity(self, version, date_start, date_end):
        """Exige recibo validated del contrato en el periodo antes de ejecutar SS."""
        payslip_model = self.getDashboardModel("hr.payslip")
        payslips = payslip_model.search([
            ("state", "=", "validated"),
            ("version_id", "=", version.id),
            "|",
            "&",
            ("date_from", ">=", date_start),
            ("date_from", "<=", date_end),
            "&",
            ("date_to", ">=", date_start),
            ("date_to", "<=", date_end),
        ], limit=1)
        if not payslips:
            raise AssertionError(_(
                "No existe nómina periódica validada para este contrato en el periodo seleccionado."
            ))
        self.logFunctionalField(_("Nómina validada del periodo."), payslips.display_name)
        return payslips

    def resolveSocialSecurityHeader(self, year, month, company):
        """Busca o crea la cabecera única del periodo (company+year+month)."""
        header_model = self.getDashboardModel("hr.payroll.social.security")
        header = header_model.search([
            ("company_id", "=", company.id),
            ("year", "=", year),
            ("month", "=", month),
        ], limit=1)
        if header:
            if header.state == "accounting":
                raise AssertionError(_(
                    "La seguridad social del periodo %s-%s ya está contabilizada; "
                    "cancele la contabilización antes de simular."
                ) % (month, year))
            self.logFunctionalStep(_("Reutilizar cabecera de seguridad social del periodo."))
            return header
        self.logFunctionalStep(_("Crear cabecera de seguridad social del periodo (savepoint)."))
        return header_model.create({
            "year": year,
            "month": month,
            "company_id": company.id,
            "observations": _("Simulación dashboard"),
        })

    def formatSocialSecurityEntityName(self, entity):
        return entity.display_name if entity else "-"

    def formatSocialSecurityBoolean(self, value):
        return _("Sí") if value else _("No")

    def formatSocialSecurityDate(self, value):
        return str(value) if value else "-"

    def buildSocialSecurityField(self, label, value, value_type="text"):
        return {
            "label": label,
            "value": value,
            "value_type": value_type,
        }

    def formatSocialSecurityAnalyticValue(self, analytic_distribution):
        if not analytic_distribution:
            return "-"
        return str(analytic_distribution)

    def formatPeriodClosureStateLabel(self, state):
        return {
            "draft": _("Borrador"),
            "done": _("Realizado"),
            "accounting": _("Contabilizado"),
        }.get(state or "", state or "-")

    def formatPeriodClosureMonthLabel(self, month):
        month_labels = {
            "1": _("Enero"),
            "2": _("Febrero"),
            "3": _("Marzo"),
            "4": _("Abril"),
            "5": _("Mayo"),
            "6": _("Junio"),
            "7": _("Julio"),
            "8": _("Agosto"),
            "9": _("Septiembre"),
            "10": _("Octubre"),
            "11": _("Noviembre"),
            "12": _("Diciembre"),
        }
        key = str(month or "")
        return month_labels.get(key, key or "-")

    def buildPeriodClosureHeaderInfo(self, header, version, year, month, line_count):
        """Datos del tab Encabezado (cabecera del proceso real)."""
        header.invalidate_recordset()
        company = header.company_id or version.company_id or self.env.company
        return {
            "year": year,
            "month": str(month),
            "month_label": self.formatPeriodClosureMonthLabel(month),
            "period": "%s-%s" % (month, year),
            "company": company.display_name if company else "-",
            "employee": version.employee_id.display_name or "-",
            "contract": version.display_name or "-",
            "line_count": int(line_count or 0),
            "time_process": header.time_process or "-",
            "state": header.state or "-",
            "state_label": self.formatPeriodClosureStateLabel(header.state),
            "header_name": header.display_name or "-",
        }

    def extractSocialSecuritySegment(self, executing, index):
        """Tramo de ejecución: fila de tabla + secciones del formulario Abrir: Ejecución."""
        leave_label = executing.leave_id.display_name if executing.leave_id else ""
        label = _("Tramo %s") % index
        if leave_label:
            label = "%s | %s" % (label, leave_label)
        employee_name = executing.employee_id.display_name or "-"
        contract_name = executing.version_id.display_name or "-"
        info_days = [
            self.buildSocialSecurityField(
                _("Ejecución seguridad social"),
                executing.executing_social_security_id.display_name or "-",
            ),
            self.buildSocialSecurityField(_("Empleado"), employee_name),
            self.buildSocialSecurityField(
                _("Dependiente UPC"),
                executing.dependent_upc_id.display_name if executing.dependent_upc_id else "-",
            ),
            self.buildSocialSecurityField(
                _("Sucursal"),
                executing.branch_id.display_name if executing.branch_id else "-",
            ),
            self.buildSocialSecurityField(_("Contrato"), contract_name),
            self.buildSocialSecurityField(
                _("Distribución analítica"),
                self.formatSocialSecurityAnalyticValue(executing.analytic_distribution),
            ),
            self.buildSocialSecurityField(_("Sueldo"), float(executing.nSueldo or 0.0), "monetary"),
            self.buildSocialSecurityField(
                _("Horas laboradas"), int(executing.nNumeroHorasLaboradas or 0), "integer"
            ),
            self.buildSocialSecurityField(
                _("Ingreso"), self.formatSocialSecurityBoolean(executing.nIngreso), "boolean"
            ),
            self.buildSocialSecurityField(
                _("Retiro"), self.formatSocialSecurityBoolean(executing.nRetiro), "boolean"
            ),
            self.buildSocialSecurityField(
                _("Exonerado ley 1607"),
                self.formatSocialSecurityBoolean(executing.cExonerado1607),
                "boolean",
            ),
            self.buildSocialSecurityField(
                _("Días liquidados"), int(executing.nDiasLiquidados or 0), "integer"
            ),
            self.buildSocialSecurityField(
                _("Días incapacidad EPS"), int(executing.nDiasIncapacidadEPS or 0), "integer"
            ),
            self.buildSocialSecurityField(_("Días licencia"), int(executing.nDiasLicencia or 0), "integer"),
            self.buildSocialSecurityField(
                _("Días licencia remunerada"), int(executing.nDiasLicenciaRenumerada or 0), "integer"
            ),
            self.buildSocialSecurityField(_("Días maternidad"), int(executing.nDiasMaternidad or 0), "integer"),
            self.buildSocialSecurityField(_("Días vacaciones"), int(executing.nDiasVacaciones or 0), "integer"),
            self.buildSocialSecurityField(
                _("Días incapacidad ARP"), int(executing.nDiasIncapacidadARP or 0), "integer"
            ),
        ]
        health = [
            self.buildSocialSecurityField(
                _("Tercero EPS"), self.formatSocialSecurityEntityName(executing.TerceroEPS)
            ),
            self.buildSocialSecurityField(_("Valor base salud"), float(executing.nValorBaseSalud or 0.0), "monetary"),
            self.buildSocialSecurityField(
                _("Porc. aporte salud empleado"), float(executing.nPorcAporteSaludEmpleado or 0.0), "percent"
            ),
            self.buildSocialSecurityField(
                _("Valor salud empleado"), float(executing.nValorSaludEmpleado or 0.0), "monetary"
            ),
            self.buildSocialSecurityField(
                _("Valor salud nómina"), float(executing.nValorSaludEmpleadoNomina or 0.0), "monetary"
            ),
            self.buildSocialSecurityField(
                _("Porc. aporte salud empresa"), float(executing.nPorcAporteSaludEmpresa or 0.0), "percent"
            ),
            self.buildSocialSecurityField(
                _("Valor salud empresa"), float(executing.nValorSaludEmpresa or 0.0), "monetary"
            ),
            self.buildSocialSecurityField(
                _("Valor salud total"), float(executing.nValorSaludTotal or 0.0), "monetary"
            ),
            self.buildSocialSecurityField(
                _("Diferencia salud"), float(executing.nDiferenciaSalud or 0.0), "monetary"
            ),
            self.buildSocialSecurityField(_("Valor UPC"), float(executing.nValorUPC or 0.0), "monetary"),
        ]
        pension = [
            self.buildSocialSecurityField(
                _("Tercero pensión"), self.formatSocialSecurityEntityName(executing.TerceroPension)
            ),
            self.buildSocialSecurityField(
                _("Valor base pensión"), float(executing.nValorBaseFondoPension or 0.0), "monetary"
            ),
            self.buildSocialSecurityField(
                _("Porc. aporte pensión empleado"), float(executing.nPorcAportePensionEmpleado or 0.0), "percent"
            ),
            self.buildSocialSecurityField(
                _("Valor pensión empleado"), float(executing.nValorPensionEmpleado or 0.0), "monetary"
            ),
            self.buildSocialSecurityField(
                _("Valor pensión nómina"), float(executing.nValorPensionEmpleadoNomina or 0.0), "monetary"
            ),
            self.buildSocialSecurityField(
                _("Porc. aporte pensión empresa"), float(executing.nPorcAportePensionEmpresa or 0.0), "percent"
            ),
            self.buildSocialSecurityField(
                _("Valor pensión empresa"), float(executing.nValorPensionEmpresa or 0.0), "monetary"
            ),
            self.buildSocialSecurityField(
                _("Valor pensión total"), float(executing.nValorPensionTotal or 0.0), "monetary"
            ),
            self.buildSocialSecurityField(
                _("Diferencia pensión"), float(executing.nDiferenciaPension or 0.0), "monetary"
            ),
            self.buildSocialSecurityField(_("Tiene AVP"), self.formatSocialSecurityBoolean(executing.cAVP), "boolean"),
            self.buildSocialSecurityField(
                _("Valor AVP"), float(executing.nAporteVoluntarioPension or 0.0), "monetary"
            ),
            self.buildSocialSecurityField(
                _("Tercero fondo solidaridad"),
                self.formatSocialSecurityEntityName(executing.TerceroFondoSolidaridad),
            ),
            self.buildSocialSecurityField(
                _("Porc. fondo solidaridad"), float(executing.nPorcFondoSolidaridad or 0.0), "percent"
            ),
            self.buildSocialSecurityField(
                _("Valor fondo solidaridad"), float(executing.nValorFondoSolidaridad or 0.0), "monetary"
            ),
            self.buildSocialSecurityField(
                _("Valor fondo subsistencia"), float(executing.nValorFondoSubsistencia or 0.0), "monetary"
            ),
        ]
        arp = [
            self.buildSocialSecurityField(
                _("Tercero ARP"), self.formatSocialSecurityEntityName(executing.TerceroARP)
            ),
            self.buildSocialSecurityField(_("Valor base ARP"), float(executing.nValorBaseARP or 0.0), "monetary"),
            self.buildSocialSecurityField(
                _("Porc. aporte ARP"), float(executing.nPorcAporteARP or 0.0), "percent"
            ),
            self.buildSocialSecurityField(_("Valor ARP"), float(executing.nValorARP or 0.0), "monetary"),
        ]
        parafiscales = [
            self.buildSocialSecurityField(
                _("Tercero caja compensación"), self.formatSocialSecurityEntityName(executing.TerceroCajaCom)
            ),
            self.buildSocialSecurityField(
                _("Valor base caja compensación"), float(executing.nValorBaseCajaCom or 0.0), "monetary"
            ),
            self.buildSocialSecurityField(
                _("Porc. aporte caja compensación"), float(executing.nPorcAporteCajaCom or 0.0), "percent"
            ),
            self.buildSocialSecurityField(
                _("Valor caja compensación"), float(executing.nValorCajaCom or 0.0), "monetary"
            ),
            self.buildSocialSecurityField(
                _("Tercero SENA"), self.formatSocialSecurityEntityName(executing.TerceroSENA)
            ),
            self.buildSocialSecurityField(_("Valor base SENA"), float(executing.nValorBaseSENA or 0.0), "monetary"),
            self.buildSocialSecurityField(
                _("Porc. aporte SENA"), float(executing.nPorcAporteSENA or 0.0), "percent"
            ),
            self.buildSocialSecurityField(_("Valor SENA"), float(executing.nValorSENA or 0.0), "monetary"),
            self.buildSocialSecurityField(
                _("Tercero ICBF"), self.formatSocialSecurityEntityName(executing.TerceroICBF)
            ),
            self.buildSocialSecurityField(_("Valor base ICBF"), float(executing.nValorBaseICBF or 0.0), "monetary"),
            self.buildSocialSecurityField(
                _("Porc. aporte ICBF"), float(executing.nPorcAporteICBF or 0.0), "percent"
            ),
            self.buildSocialSecurityField(_("Valor ICBF"), float(executing.nValorICBF or 0.0), "monetary"),
        ]
        absence_dates = [
            self.buildSocialSecurityField(_("Ausencia"), leave_label or "-"),
            self.buildSocialSecurityField(
                _("Fecha inicio SLN"), self.formatSocialSecurityDate(executing.dFechaInicioSLN), "date"
            ),
            self.buildSocialSecurityField(
                _("Fecha fin SLN"), self.formatSocialSecurityDate(executing.dFechaFinSLN), "date"
            ),
            self.buildSocialSecurityField(
                _("Fecha inicio IGE"), self.formatSocialSecurityDate(executing.dFechaInicioIGE), "date"
            ),
            self.buildSocialSecurityField(
                _("Fecha fin IGE"), self.formatSocialSecurityDate(executing.dFechaFinIGE), "date"
            ),
            self.buildSocialSecurityField(
                _("Fecha inicio LMA"), self.formatSocialSecurityDate(executing.dFechaInicioLMA), "date"
            ),
            self.buildSocialSecurityField(
                _("Fecha fin LMA"), self.formatSocialSecurityDate(executing.dFechaFinLMA), "date"
            ),
            self.buildSocialSecurityField(
                _("Fecha inicio VACLR"), self.formatSocialSecurityDate(executing.dFechaInicioVACLR), "date"
            ),
            self.buildSocialSecurityField(
                _("Fecha fin VACLR"), self.formatSocialSecurityDate(executing.dFechaFinVACLR), "date"
            ),
            self.buildSocialSecurityField(
                _("Fecha inicio VCT"), self.formatSocialSecurityDate(executing.dFechaInicioVCT), "date"
            ),
            self.buildSocialSecurityField(
                _("Fecha fin VCT"), self.formatSocialSecurityDate(executing.dFechaFinVCT), "date"
            ),
            self.buildSocialSecurityField(
                _("Fecha inicio IRL"), self.formatSocialSecurityDate(executing.dFechaInicioIRL), "date"
            ),
            self.buildSocialSecurityField(
                _("Fecha fin IRL"), self.formatSocialSecurityDate(executing.dFechaFinIRL), "date"
            ),
        ]
        for field_row in info_days + health + pension + arp + parafiscales:
            if field_row["value_type"] in ("monetary", "percent", "integer"):
                self.logFunctionalField("%s - %s" % (label, field_row["label"]), field_row["value"])
        return {
            "label": label,
            "employee": employee_name,
            "contract": contract_name,
            "branch": executing.branch_id.display_name if executing.branch_id else "-",
            "days_liquidated": int(executing.nDiasLiquidados or 0),
            "salary": float(executing.nSueldo or 0.0),
            "leave": leave_label or "-",
            "info_days": info_days,
            "health": health,
            "pension": pension,
            "arp": arp,
            "parafiscales": parafiscales,
            "absence_dates": absence_dates,
        }

    def extractSocialSecurityWarnings(self, error_lines):
        """Advertencias de hr.errors.social.security del empleado/periodo."""
        warnings = []
        for error in error_lines:
            description = error.description or _("Advertencia seguridad social")
            warnings.append({
                "employee": error.employee_id.display_name if error.employee_id else "-",
                "branch": error.branch_id.display_name if error.branch_id else "-",
                "description": description,
            })
            self.logFunctionalField(_("Advertencia SS"), description)
        return warnings

    def isTruthyDashboardParam(self, value):
        """Normaliza checkboxes del panel (evita que 'False' string sea truthy)."""
        return value in (True, 1, "1", "true", "True")

    def applySocialSecurityAccounting(self, header):
        """Avanza la cabecera a realizado y ejecuta get_accounting (flujo real Contabilizar)."""
        if header.state == "accounting":
            raise AssertionError(_(
                "La seguridad social del periodo ya está contabilizada; no se puede volver a contabilizar."
            ))
        if header.state != "done":
            # Tras ejecución por empleado la cabecera puede quedar en borrador; Contabilizar exige realizado.
            header.write({"state": "done"})
            self.logFunctionalStep(_("Marcar cabecera de seguridad social como realizada antes de contabilizar."))
        self.logFunctionalStep(_("Contabilizar seguridad social (get_accounting)."))
        header.get_accounting()
        header.invalidate_recordset()
        if header.state != "accounting" or not header.move_id:
            raise AssertionError(_(
                "La contabilización de seguridad social no generó asiento o no avanzó a estado contabilizado."
            ))
        self.logFunctionalField(_("Asiento contable"), header.move_id.display_name or header.move_id.name)
        return header.move_id

    def resolveSocialSecurityAccountingProcessKey(self, line_name):
        """Clasifica una línea del asiento según el texto generado por get_accounting."""
        name = (line_name or "").lower()
        process_matchers = [
            ("ss_empresa_salud", ("aporte empresa salud", "diferencia salud")),
            ("ss_empresa_pension", ("aporte empresa pensión", "aporte empresa pension", "diferencia pensión", "diferencia pension")),
            ("ss_empresa_arp", ("aporte arp",)),
            ("ss_empresa_caja", ("aporte caja de compensación", "aporte caja de compensacion")),
            ("ss_empresa_sena", ("aporte sena",)),
            ("ss_empresa_icbf", ("aporte icbf",)),
        ]
        for process_key, needles in process_matchers:
            if any(needle in name for needle in needles):
                return process_key
        return False

    def extractSocialSecurityAccounting(self, move):
        """Detalle del asiento y líneas agrupadas por los 6 procesos de cierre SS."""
        process_labels = {
            "ss_empresa_salud": _("Seguridad social - Aporte empresa salud"),
            "ss_empresa_pension": _("Seguridad social - Aporte empresa pensión"),
            "ss_empresa_arp": _("Seguridad social - Aporte empresa ARP"),
            "ss_empresa_caja": _("Seguridad social - Aporte empresa caja"),
            "ss_empresa_sena": _("Seguridad social - Aporte empresa SENA"),
            "ss_empresa_icbf": _("Seguridad social - Aporte empresa ICBF"),
        }
        process_order = list(process_labels.keys())
        grouped = {key: [] for key in process_order}
        other_lines = []
        for line in move.line_ids.sorted(key=lambda item: (item.id)):
            row = {
                "name": line.name or "-",
                "account": line.account_id.display_name or line.account_id.code or "-",
                "partner": line.partner_id.display_name if line.partner_id else "-",
                "debit": float(line.debit or 0.0),
                "credit": float(line.credit or 0.0),
            }
            process_key = self.resolveSocialSecurityAccountingProcessKey(line.name)
            if process_key:
                grouped[process_key].append(row)
            else:
                other_lines.append(row)
        processes = []
        for process_key in process_order:
            processes.append({
                "code": process_key,
                "label": process_labels[process_key],
                "lines": grouped[process_key],
            })
        if other_lines:
            processes.append({
                "code": "other",
                "label": _("Otras líneas del asiento"),
                "lines": other_lines,
            })
        return {
            "move_id": move.id,
            "move_name": move.name or move.display_name or "-",
            "move_ref": move.ref or "-",
            "move_state": move.state or "-",
            "move_date": str(move.date) if move.date else "-",
            "processes": processes,
        }

    def extractSocialSecurityResult(
        self,
        executing_lines,
        error_lines,
        version,
        header,
        year,
        month,
        accounting=None,
    ):
        """Payload de resultado con layout propio de Seguridad Social."""
        segments = [
            self.extractSocialSecuritySegment(executing, index)
            for index, executing in enumerate(executing_lines, start=1)
        ]
        return [{
            "layout": "social_security",
            "employee": version.employee_id.display_name or "",
            "contract": version.display_name or "",
            "period": "%s-%s" % (month, year),
            "header": header.display_name or "",
            "header_state": header.state or "",
            "header_info": self.buildPeriodClosureHeaderInfo(
                header, version, year, month, len(segments)
            ),
            "segments": segments,
            "warnings": self.extractSocialSecurityWarnings(error_lines),
            "accounting": accounting or False,
        }]

    def testSimulateSeguridadSocial(self, input_values=None):
        """Simula seguridad social por empleado/contrato vía executing_social_security."""
        input_values = input_values or {}
        self.logFunctionalStep(_("Simular ejecución de seguridad social."))
        if "hr.payroll.social.security" not in self.env:
            raise AssertionError(_(
                "El módulo zue_hr_social_security no está disponible en esta base de datos."
            ))
        version = self.resolveVersionForProcessTest(input_values)
        year, month, date_start, date_end = self.resolveSocialSecurityPeriod(input_values)
        generate_accounting = self.isTruthyDashboardParam(input_values.get("generate_accounting"))
        self.logFunctionalField(_("Asignar contrato a validar."), version.display_name)
        self.logFunctionalField(_("Asignar empleado."), version.employee_id.display_name)
        self.logFunctionalField(_("Asignar año del periodo."), year)
        self.logFunctionalField(_("Asignar mes del periodo."), month)
        self.logFunctionalField(
            _("Generar contabilización"),
            _("Sí") if generate_accounting else _("No"),
        )
        self.ensureValidatedPayslipForSocialSecurity(version, date_start, date_end)
        company = version.company_id or self.env.company
        header = self.resolveSocialSecurityHeader(year, month, company)
        self.logFunctionalStep(_(
            "Ejecutar seguridad social por empleado (executing_social_security)."
        ))
        header.executing_social_security(version.employee_id.id)
        executing_lines = self.getDashboardModel("hr.executing.social.security").search([
            ("executing_social_security_id", "=", header.id),
            ("version_id", "=", version.id),
        ], order="id")
        error_lines = self.getDashboardModel("hr.errors.social.security").search([
            ("executing_social_security_id", "=", header.id),
            ("employee_id", "=", version.employee_id.id),
        ], order="id")
        if not executing_lines and error_lines:
            raise AssertionError(_(
                "La seguridad social no generó líneas para el contrato; advertencias: %s"
            ) % "; ".join(error_lines.mapped("description")))
        if not executing_lines:
            raise AssertionError(_(
                "La seguridad social no generó líneas de ejecución para el contrato seleccionado."
            ))
        accounting_payload = False
        if generate_accounting:
            move = self.applySocialSecurityAccounting(header)
            accounting_payload = self.extractSocialSecurityAccounting(move)
        self.logFunctionalStep(_("Obtener detalle de ejecución de seguridad social."))
        obtained_info = self.extractSocialSecurityResult(
            executing_lines,
            error_lines,
            version,
            header,
            year,
            month,
            accounting=accounting_payload,
        )
        self.logFunctionalStep(_("Finalizar simulación de seguridad social."))
        if self.hasDashboardProvider():
            self.provider.completeProcessTest(
                calculated_lines=[],
                worked_days_lines=[],
                not_applied_lines=[],
                obtained_info=obtained_info,
                message=_("Seguridad social simulada correctamente."),
            )
        return obtained_info

    def resolveProvisionsHeader(self, year, month, company):
        """Busca o crea la cabecera única de provisiones (company+year+month)."""
        header_model = self.getDashboardModel("hr.executing.provisions")
        header = header_model.search([
            ("company_id", "=", company.id),
            ("year", "=", year),
            ("month", "=", month),
        ], limit=1)
        if header:
            if header.state == "accounting":
                raise AssertionError(_(
                    "Las provisiones del periodo %s-%s ya están contabilizadas; "
                    "cancele la contabilización antes de simular."
                ) % (month, year))
            self.logFunctionalStep(_("Reutilizar cabecera de provisiones del periodo."))
            return header
        self.logFunctionalStep(_("Crear cabecera de provisiones del periodo (savepoint)."))
        return header_model.create({
            "year": year,
            "month": month,
            "company_id": company.id,
            "observations": _("Simulación dashboard"),
        })

    def applyProvisionsForEmployee(self, header, version):
        """Ejecuta provisiones solo para el empleado seleccionado (modo por empleado)."""
        try:
            header.executing_provisions(version.employee_id.id)
        except NameError as error:
            # Bug conocido en executing_provisions(employee_id!=0): usa result_query
            # sin definirlo al cerrar estado. El cálculo por savepoint ya corrió.
            if "result_query" not in str(error):
                raise
            self.logFunctionalStep(_(
                "Cálculo por empleado completado; se omite el cierre masivo de estado del motor."
            ))
        return header

    def applyProvisionsAccounting(self, header, date_end):
        """Avanza la cabecera a realizado y ejecuta get_accounting."""
        if header.state == "accounting":
            raise AssertionError(_(
                "Las provisiones del periodo ya están contabilizadas; no se puede volver a contabilizar."
            ))
        values = {}
        if header.state != "done":
            values["state"] = "done"
        if not header.date_end:
            values["date_end"] = date_end
        if values:
            header.write(values)
            self.logFunctionalStep(_(
                "Marcar cabecera de provisiones como realizada antes de contabilizar."
            ))
        self.logFunctionalStep(_("Contabilizar provisiones (get_accounting)."))
        header.get_accounting()
        header.invalidate_recordset()
        if header.state != "accounting" or not header.move_id:
            raise AssertionError(_(
                "La contabilización de provisiones no generó asiento o no avanzó a estado contabilizado."
            ))
        self.logFunctionalField(_("Asiento contable"), header.move_id.display_name or header.move_id.name)
        return header.move_id

    def resolveProvisionsAccountingProcessKey(self, line_name):
        """Clasifica líneas del asiento de provisiones por el texto del proceso."""
        name = (line_name or "").upper()
        process_matchers = [
            ("intcesantias", ("INTCESANTIAS",)),
            ("cesantias", ("CESANTIAS",)),
            ("prima", ("PRIMA",)),
            ("vacaciones", ("VACACIONES", "VACCONTRATO")),
        ]
        for process_key, needles in process_matchers:
            if any(needle in name for needle in needles):
                return process_key
        return False

    def extractProvisionsAccounting(self, move):
        """Detalle del asiento y líneas agrupadas por tipo de provisión."""
        process_labels = {
            "cesantias": _("Cesantías"),
            "intcesantias": _("Intereses de cesantías"),
            "prima": _("Prima"),
            "vacaciones": _("Vacaciones"),
        }
        process_order = list(process_labels.keys())
        grouped = {key: [] for key in process_order}
        other_lines = []
        for line in move.line_ids.sorted(key=lambda item: item.id):
            row = {
                "name": line.name or "-",
                "account": line.account_id.display_name or line.account_id.code or "-",
                "partner": line.partner_id.display_name if line.partner_id else "-",
                "debit": float(line.debit or 0.0),
                "credit": float(line.credit or 0.0),
            }
            process_key = self.resolveProvisionsAccountingProcessKey(line.name)
            if process_key:
                grouped[process_key].append(row)
            else:
                other_lines.append(row)
        processes = []
        for process_key in process_order:
            processes.append({
                "code": process_key,
                "label": process_labels[process_key],
                "lines": grouped[process_key],
            })
        if other_lines:
            processes.append({
                "code": "other",
                "label": _("Otras líneas del asiento"),
                "lines": other_lines,
            })
        return {
            "move_id": move.id,
            "move_name": move.name or move.display_name or "-",
            "move_ref": move.ref or "-",
            "move_state": move.state or "-",
            "move_date": str(move.date) if move.date else "-",
            "processes": processes,
        }

    def extractProvisionsDetailProps(self, detail):
        """Detalle en 2 columnas como el formulario Abrir: Ejecución de provisiones."""
        provision_labels = dict(
            self.getDashboardModel("hr.executing.provisions.details")._fields["provision"].selection or []
        )
        analytic_value = "-"
        if detail.analytic_distribution:
            analytic_value = str(detail.analytic_distribution)
        return {
            "column_left": [
                self.buildSocialSecurityField(
                    _("Ejecución Provisiones"),
                    detail.executing_provisions_id.display_name or "-",
                ),
                self.buildSocialSecurityField(
                    _("Empleado"),
                    detail.employee_id.display_name or "-",
                ),
                self.buildSocialSecurityField(_("Distribución analítica"), analytic_value),
                self.buildSocialSecurityField(_("Base"), float(detail.value_base or 0.0), "monetary"),
                self.buildSocialSecurityField(
                    _("Valor Provisión Mes"), float(detail.value_balance or 0.0), "monetary"
                ),
                self.buildSocialSecurityField(
                    _("Valor liquidado"), float(detail.amount or 0.0), "monetary"
                ),
            ],
            "column_right": [
                self.buildSocialSecurityField(
                    _("Provisión"),
                    provision_labels.get(detail.provision, detail.provision or "-"),
                ),
                self.buildSocialSecurityField(
                    _("Contrato"),
                    detail.version_id.display_name or "-",
                ),
                self.buildSocialSecurityField(_("Salario"), float(detail.value_wage or 0.0), "monetary"),
                self.buildSocialSecurityField(_("Unidades"), float(detail.time or 0.0)),
                self.buildSocialSecurityField(
                    _("Pagos realizados"), float(detail.value_payments or 0.0), "monetary"
                ),
                self.buildSocialSecurityField(
                    _("Valor a Pagar Actual"), float(detail.current_payable_value or 0.0), "monetary"
                ),
            ],
        }

    def extractProvisionsRows(self, detail_lines):
        """Tabla resumen de las 4 provisiones + detalle expandible."""
        provision_order = [
            ("cesantias", _("Cesantías")),
            ("intcesantias", _("Intereses de cesantías")),
            ("prima", _("Prima")),
            ("vacaciones", _("Vacaciones")),
        ]
        by_provision = {}
        for detail in detail_lines:
            by_provision.setdefault(detail.provision, detail)
        rows = []
        for code, label in provision_order:
            detail = by_provision.get(code)
            if not detail:
                rows.append({
                    "code": code,
                    "label": label,
                    "amount": 0.0,
                    "value_payments": 0.0,
                    "current_payable_value": 0.0,
                    "value_balance": 0.0,
                    "missing": True,
                    "detail": False,
                })
                continue
            rows.append({
                "code": code,
                "label": label,
                "amount": float(detail.amount or 0.0),
                "value_payments": float(detail.value_payments or 0.0),
                "current_payable_value": float(detail.current_payable_value or 0.0),
                "value_balance": float(detail.value_balance or 0.0),
                "missing": False,
                "detail": self.extractProvisionsDetailProps(detail),
            })
            self.logFunctionalField("%s - %s" % (label, _("Valor provisión mes")), detail.value_balance)
        return rows

    def extractProvisionsWarnings(self, error_lines):
        warnings = []
        for error in error_lines:
            description = error.description or _("Advertencia provisiones")
            warnings.append({
                "employee": error.employee_id.display_name if error.employee_id else "-",
                "contract": error.version_id.display_name if error.version_id else "-",
                "description": description,
            })
            self.logFunctionalField(_("Advertencia provisiones"), description)
        return warnings

    def extractProvisionsResult(
        self,
        detail_lines,
        error_lines,
        version,
        header,
        year,
        month,
        accounting=None,
    ):
        return [{
            "layout": "provisions",
            "employee": version.employee_id.display_name or "",
            "contract": version.display_name or "",
            "period": "%s-%s" % (month, year),
            "header": header.display_name or "",
            "header_state": header.state or "",
            "header_info": self.buildPeriodClosureHeaderInfo(
                header, version, year, month, len(detail_lines)
            ),
            "rows": self.extractProvisionsRows(detail_lines),
            "warnings": self.extractProvisionsWarnings(error_lines),
            "accounting": accounting or False,
        }]

    def testSimulateProvisiones(self, input_values=None):
        """Simula provisiones por empleado/contrato vía executing_provisions."""
        input_values = input_values or {}
        self.logFunctionalStep(_("Simular ejecución de provisiones."))
        if "hr.executing.provisions" not in self.env:
            raise AssertionError(_(
                "El módulo zue_hr_social_security no está disponible en esta base de datos."
            ))
        version = self.resolveVersionForProcessTest(input_values)
        year, month, date_start, date_end = self.resolveSocialSecurityPeriod(input_values)
        generate_accounting = self.isTruthyDashboardParam(input_values.get("generate_accounting"))
        self.logFunctionalField(_("Asignar contrato a validar."), version.display_name)
        self.logFunctionalField(_("Asignar empleado."), version.employee_id.display_name)
        self.logFunctionalField(_("Asignar año del periodo."), year)
        self.logFunctionalField(_("Asignar mes del periodo."), month)
        self.logFunctionalField(
            _("Generar contabilización"),
            _("Sí") if generate_accounting else _("No"),
        )
        self.ensureValidatedPayslipForSocialSecurity(version, date_start, date_end)
        company = version.company_id or self.env.company
        header = self.resolveProvisionsHeader(year, month, company)
        self.logFunctionalStep(_("Ejecutar provisiones por empleado (executing_provisions)."))
        self.applyProvisionsForEmployee(header, version)
        detail_lines = self.getDashboardModel("hr.executing.provisions.details").search([
            ("executing_provisions_id", "=", header.id),
            ("version_id", "=", version.id),
        ], order="id")
        error_lines = self.getDashboardModel("hr.errors.provisions").search([
            ("executing_provisions_id", "=", header.id),
            ("employee_id", "=", version.employee_id.id),
        ], order="id")
        if not detail_lines and error_lines:
            raise AssertionError(_(
                "Las provisiones no generaron líneas para el contrato; advertencias: %s"
            ) % "; ".join(error_lines.mapped("description")))
        if not detail_lines:
            raise AssertionError(_(
                "Las provisiones no generaron líneas de ejecución para el contrato seleccionado."
            ))
        accounting_payload = False
        if generate_accounting:
            move = self.applyProvisionsAccounting(header, date_end)
            accounting_payload = self.extractProvisionsAccounting(move)
        self.logFunctionalStep(_("Obtener detalle de ejecución de provisiones."))
        obtained_info = self.extractProvisionsResult(
            detail_lines,
            error_lines,
            version,
            header,
            year,
            month,
            accounting=accounting_payload,
        )
        self.logFunctionalStep(_("Finalizar simulación de provisiones."))
        if self.hasDashboardProvider():
            self.provider.completeProcessTest(
                calculated_lines=[],
                worked_days_lines=[],
                not_applied_lines=[],
                obtained_info=obtained_info,
                message=_("Provisiones simuladas correctamente."),
            )
        return obtained_info
