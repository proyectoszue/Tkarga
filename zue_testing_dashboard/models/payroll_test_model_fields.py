# -*- coding: utf-8 -*-
# Payroll: pickers y fechas de proceso (hr.version, cesantías, etc.).

from odoo import _, api, models
from odoo.exceptions import UserError


class ZueTestingDashboardSessionPayrollFields(models.TransientModel):
    """Extensiones de nómina para pickers y fechas de proceso del panel."""

    _inherit = "zue.testing.dashboard.session"

    @api.model
    def getDashboardVersionWage(self, version_id):
        """Devuelve el salario actual del contrato para precargar cambios de salario."""
        if not version_id:
            return False
        version = self.env["hr.version"].sudo().browse(int(version_id))  # sudo: lectura salario en panel
        if not version.exists() or "wage" not in version._fields:
            return False
        return float(version.wage or 0.0)

    @api.model
    def resolveDashboardCesantiasDateFrom(self, version_id, structure_process, date_end=None):
        """Calcula fecha desde de cesantías/intereses según historial o inicio de contrato."""
        from datetime import date, timedelta

        from odoo.fields import Date as OdooDate

        if not version_id:
            return False
        if structure_process not in ("cesantias", "intereses_cesantias"):
            raise UserError(_("Proceso de cesantías inválido: %s") % structure_process)
        version = self.env["hr.version"].sudo().browse(int(version_id))  # sudo: lectura historial para el panel
        if not version.exists():
            raise UserError(_("No se encontró el contrato indicado."))
        date_cesantias = version.contract_date_start
        if not date_cesantias:
            raise UserError(_("El contrato no tiene fecha de inicio para calcular cesantías."))
        history_model = self.env["hr.history.cesantias"].sudo()  # sudo: historial de cesantías del contrato
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
        else:
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
        if date_end:
            parsed_end = OdooDate.to_date(date_end) if not isinstance(date_end, date) else date_end
            if parsed_end and date_cesantias > parsed_end:
                raise UserError(_(
                    "La fecha desde calculada (%s) es posterior a la fecha hasta (%s)."
                ) % (date_cesantias, parsed_end))
        return str(date_cesantias)

    @api.model
    def resolveDashboardContratoAccrualDates(self, version_id):
        """Calcula fechas de causación de liq. contrato (prima/cesantías/vacaciones)."""
        from datetime import date, timedelta

        if not version_id:
            return {
                "date_prima": False,
                "date_cesantias": False,
                "date_vacaciones": False,
            }
        version = self.env["hr.version"].sudo().browse(int(version_id))  # sudo: lectura historial para el panel
        if not version.exists():
            raise UserError(_("No se encontró el contrato indicado."))
        if not version.contract_date_start:
            raise UserError(_(
                "El contrato no tiene fecha de inicio para calcular fechas de causación."
            ))

        date_prima = version.contract_date_start
        for history in sorted(
            self.env["hr.history.prima"].sudo().search([  # sudo: historial prima del contrato
                ("employee_id", "=", version.employee_id.id),
                ("version_id", "=", version.id),
            ]),
            key=lambda item: item.final_accrual_date or date.min,
        ):
            if history.final_accrual_date and history.final_accrual_date > date_prima:
                date_prima = history.final_accrual_date + timedelta(days=1)

        date_vacaciones = version.contract_date_start
        for history in sorted(
            self.env["hr.vacation"].sudo().search([  # sudo: historial vacaciones del contrato
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
            self.env["hr.history.cesantias"].sudo().search([  # sudo: historial cesantías del contrato
                ("employee_id", "=", version.employee_id.id),
                ("version_id", "=", version.id),
            ]),
            key=lambda item: item.final_accrual_date or date.min,
        ):
            if history.final_accrual_date and history.final_accrual_date > date_cesantias:
                date_cesantias = history.final_accrual_date + timedelta(days=1)

        return {
            "date_prima": str(date_prima) if date_prima else False,
            "date_cesantias": str(date_cesantias) if date_cesantias else False,
            "date_vacaciones": str(date_vacaciones) if date_vacaciones else False,
        }

    @api.model
    def searchDashboardVersions(self, search="", limit=40, ids=None):
        """Lista contratos en formato Empleado | Contrato | Tipo | Estado."""
        version_model = self.env["hr.version"].sudo()  # sudo: picker de contratos del panel
        contract_type_labels = dict(version_model._fields["contract_type"].selection or [])
        if ids:
            domain = [("id", "in", list(ids))]
        else:
            domain = []
            search = (search or "").strip()
            if search:
                matching_types = [
                    value
                    for value, label in contract_type_labels.items()
                    if search.lower() in (label or "").lower()
                ]
                domain = [
                    "|", "|",
                    ("employee_id.name", "ilike", search),
                    ("name", "ilike", search),
                    ("sequence", "ilike", search),
                ]
                if matching_types:
                    domain = ["|"] + domain + [("contract_type", "in", matching_types)]
        versions = version_model.search(domain, limit=limit, order="employee_id, sequence, id")
        options = []
        for version in versions:
            employee_name = version.employee_id.display_name or version.employee_id.name or "-"
            contract_name = version.sequence or version.name or str(version.id)
            contract_type = contract_type_labels.get(version.contract_type, version.contract_type or "-")
            status_dot = "🟢" if not version.retirement_date else "🔴"
            options.append({
                "value": version.id,
                "label": "%s | %s%s | %s" % (employee_name, status_dot, contract_name, contract_type),
            })
        return options
