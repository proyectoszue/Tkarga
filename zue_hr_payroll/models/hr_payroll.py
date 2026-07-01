# -*- coding: utf-8 -*-
from ast import literal_eval
from odoo import models, api, fields, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
from .browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips
from odoo.tools import float_compare, float_is_zero
from collections import defaultdict
from datetime import datetime, timedelta, date, time
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
from odoo.osv import expression
from odoo.fields import Domain
from odoo.tools.date_utils import get_month
import math
import pytz
import odoo
import threading
import logging

_logger = logging.getLogger(__name__)
#---------------------------LIQUIDACIÓN DE NÓMINA-------------------------------#

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    time_process = fields.Char(string='Tiempo ejecución')
    observations = fields.Text('Observaciones')
    definitive_plan = fields.Boolean(string='Plano definitivo generado')
    z_filter_state_finished = fields.Selection([('open', 'En Proceso'),
                                                ('finished', 'Finalizado por liquidar')],string='Estado',
                                               default='open', required=True)
    method_schedule_pay = fields.Selection([('bi-weekly', 'Quincenal'),
                                            ('monthly', 'Mensual')], 'Frecuencia de Pago')
    structure_process = fields.Selection(related='structure_id.process', string='Proceso estructura')
    prima_run_reverse_id = fields.Many2one(
        'hr.payslip.run',
        string='Lote de prima a ajustar',
        check_company=True,
    )
    state = fields.Selection([
        ('01_ready', 'Borrador'),
        ('02_close', 'Confirmado'),
        ('03_paid', 'Pagado'),
        ('04_cancel', 'Cancelado'),
    ],
        string='Estado', index=True, readonly=True, copy=False,
        default='01_ready', tracking=True,
        compute='_compute_state', store=True)
    schedule_pay = fields.Selection(
        selection=lambda self: self.env['hr.payroll.structure.type']._get_selection_schedule_pay(),
        compute='_compute_schedule_pay', default=False, readonly=False, store=True, precompute=True,
        string='Pay Schedule')

    @api.onchange('structure_id')
    def onchangeStructureIdClearPrimaRunReverse(self):
        if self.structure_id.process != 'prima':
            self.prima_run_reverse_id = False

    @api.depends("slip_ids.state")
    def _compute_state(self):
        for payslip_run in self:
            states = payslip_run.mapped('slip_ids.state')
            if any(state == "draft" for state in states) or not payslip_run.slip_ids:
                payslip_run.state = '01_ready'
            elif any(state == "validated" for state in states):
                payslip_run.state = '02_close'
            elif any(state == "paid" for state in states):
                payslip_run.state = '03_paid'
            elif all(state == "cancel" for state in states):
                payslip_run.state = '04_cancel'
            else:
                payslip_run.state = '01_ready'

    # SE HEREDA METODO COMPLETO DE ODOO
    def action_payroll_hr_version_list_view_payrun(self, date_start=None, date_end=None, structure_id=None, company_id=None, schedule_pay=None, z_filter_state_finished='open', method_schedule_pay=None, prima_run_reverse_id=None):
        action = self.env['ir.actions.act_window']._for_xml_id('hr_payroll.action_payroll_hr_version_list_view_payrun')

        valid_version_ids = self._get_valid_version_ids(
            fields.Date.from_string(date_start),
            fields.Date.from_string(date_end),
            structure_id,
            company_id,
            None,
            schedule_pay,
            z_filter_state_finished,
            method_schedule_pay,
            prima_run_reverse_id,
        )

        payslip_domain = Domain.AND([
           Domain('version_id', 'in', valid_version_ids),
           Domain('date_from', '=', fields.Date.from_string(date_start) if date_start else self.date_start),
           Domain('date_to', '=', fields.Date.from_string(date_end) if date_end else self.date_end),
           Domain('struct_id', '=', structure_id if structure_id else (self.structure_id.id if self.structure_id else False)),
           Domain('state', '!=', 'cancel')#,
           #Domain('version_id.schedule_pay', '=', schedule_pay if schedule_pay else False)
        ])
        existing_version_ids = self.env['hr.payslip'].search(payslip_domain).version_id.ids
        filtered_version_ids = set(valid_version_ids) - set(existing_version_ids)
        action['domain'] = [("id", "in", list(filtered_version_ids))]
        return action

    # SE HEREDA METODO COMPLETO DE ODOO
    def _get_valid_version_ids(self, date_start=None, date_end=None, structure_id=None, company_id=None, employee_ids=None, schedule_pay=None, z_filter_state_finished='open', method_schedule_pay=None, prima_run_reverse_id=None):
        date_start = date_start or self.date_start
        date_end = date_end or self.date_end
        structure = self.env["hr.payroll.structure"].browse(structure_id) if structure_id else self.structure_id
        schedule_pay = schedule_pay or self.schedule_pay
        z_filter_state_finished = z_filter_state_finished or self.z_filter_state_finished
        method_schedule_pay = method_schedule_pay or self.method_schedule_pay
        if prima_run_reverse_id is None:
            prima_run_reverse_id = self.prima_run_reverse_id.id if self.prima_run_reverse_id else False
        company = company_id or self.company_id.id
        if z_filter_state_finished == 'open':
            version_domain = Domain([
                ('company_id', '=', company),
                ('employee_id', '!=', False),
                ('employee_id.active', '=', True),
                ('z_state_finished', '=', False),
                ('contract_date_start', '<=', date_end),
                '|',
                    ('retirement_date', '=', False),
                    ('retirement_date', '>=', date_start),
                ('date_version', '<=', date_end),
                ('structure_type_id', '!=', False),
            ])
        else:
            version_domain = Domain([('company_id', '=', company),('employee_id', '!=', False),('employee_id.active', '=', True),('z_state_finished', '=', True)])

        if method_schedule_pay:
            version_domain &= Domain([('method_schedule_pay', '=', method_schedule_pay)])
        if prima_run_reverse_id and structure.process == 'prima':
            reverse_employee_ids = self.env['hr.payslip'].search([
                ('payslip_run_id', '=', prima_run_reverse_id),
            ]).employee_id.ids
            version_domain &= Domain([('employee_id', 'in', reverse_employee_ids or [0])])
        # if structure: SE COMENTA PARA FUNCIONALIDAD DE ZUE
        #     version_domain &= Domain([('structure_type_id', '=', structure.type_id.id)])
        if employee_ids:
            version_domain &= Domain([('employee_id', 'in', employee_ids)])
        # if schedule_pay: SE COMENTA PARA FUNCIONALIDAD DE ZUE
        #     version_domain &= Domain([('schedule_pay', '=', schedule_pay)])
        all_versions = self.env['hr.version']._read_group(
            domain=version_domain,
            groupby=['employee_id', 'date_version:day'],
            order="date_version:day DESC",
            aggregates=['id:recordset'],
        )
        all_employee_versions = defaultdict(list)
        for employee, _, version in all_versions:
            all_employee_versions[employee] += [*version]
        valid_versions = self.env["hr.version"]
        for employee_versions in all_employee_versions.values():
            employee_valid_versions = self.env["hr.version"]
            for i in range(len(employee_versions)):
                version = employee_versions[i]
                if version.date_version <= date_start or employee_versions[-1] == version:
                    # End case: The first version in contract before the pay run start or the last version of the list
                    employee_valid_versions |= version
                    break
                if employee_valid_versions:
                    # Version already added => new contract?
                    if (employee_valid_versions[-1].contract_date_start > version.contract_date_start
                        and (version.contract_date_start >= version.date_version
                            or version.contract_date_start > employee_versions[i + 1].contract_date_start)):
                        # Take only the first version of the new contract founded
                        employee_valid_versions |= version
                elif version.contract_date_start >= version.date_version or version.contract_date_start > employee_versions[i + 1].contract_date_start:
                    # Take only the first version of the first contract founded
                    employee_valid_versions |= version
            valid_versions |= employee_valid_versions
        return valid_versions.ids

    # SE HEREDA METODO COMPLETO DE ODOO
    def generate_payslips(self, version_ids=None, employee_ids=None):
        self.ensure_one()

        if employee_ids and not version_ids:
            version_ids = self._get_valid_version_ids(employee_ids=employee_ids)

        if not version_ids:
            raise UserError(self.env._("You must select employee(s) version(s) to generate payslip(s)."))

        valid_versions = self.env["hr.version"].browse(version_ids)

        Payslip = self.env['hr.payslip']

        # if self.structure_id: SE COMENTA PARA FUNCIONALIDAD DE ZUE
        #     valid_versions = valid_versions.filtered(lambda c: c.structure_type_id.id == self.structure_id.type_id.id) SE COMENTA PARA FUNCIONALIDAD DE ZUE
        if self.use_worked_day_lines:
            valid_versions.generate_work_entries(self.date_start, self.date_end)

            all_work_entries = dict(self.env['hr.work.entry']._read_group(
                domain=[
                    ('employee_id', 'in', valid_versions.employee_id.ids),
                    ('date', '<=', self.date_end),
                    ('date', '>=', self.date_start),
                ],
                groupby=['version_id'],
                aggregates=['id:recordset'],
            ))

            utc = pytz.utc
            for tz, slips_per_tz in self.slip_ids.grouped(lambda s: s.version_id.tz).items():
                slip_tz = pytz.timezone(tz or utc)
                for slip in slips_per_tz:
                    date_from = slip_tz.localize(datetime.combine(slip.date_from, time.min)).astimezone(utc).replace(tzinfo=None)
                    date_to = slip_tz.localize(datetime.combine(slip.date_to, time.max)).astimezone(utc).replace(tzinfo=None)
                    if version_work_entries := all_work_entries.get(slip.version_id):
                        version_work_entries.filtered_domain([
                            ('date', '<=', date_to),
                            ('date', '>=', date_from),
                        ])
                        version_work_entries._check_undefined_slots(slip.date_from, slip.date_to)

            for work_entries in all_work_entries.values():
                work_entries = work_entries.filtered(lambda we: we.state != 'validated')
                if work_entries._check_if_error():
                    work_entries = work_entries.filtered(lambda we: we.state == 'conflict')
                    conflicts = work_entries._to_intervals()
                    time_intervals_str = "".join(
                        f"\n - {start} -> {end} ({entry.employee_id.name})" for start, end, entry in conflicts._items)
                    raise UserError(self.env._("Some work entries could not be validated. Time intervals to look for:%s", time_intervals_str))

        default_values = Payslip.default_get(Payslip.fields_get())
        payslips_vals = []
        for version in valid_versions[::-1]:
            struct_id = self.structure_id.id or version.structure_type_id.default_struct_id.id
            structure_record = self.env['hr.payroll.structure'].browse(struct_id)
            values = default_values | {
                'name': self.env._('New Payslip'),
                'employee_id': version.employee_id.id,
                'payslip_run_id': self.id,
                'date_from': self.date_start,
                'date_to': self.date_end,
                'version_id': version.id,
                'company_id': self.company_id.id,
                'struct_id': struct_id,
            }
            if structure_record.process == 'prima' and self.prima_run_reverse_id:
                values['prima_run_reverse_id'] = self.prima_run_reverse_id.id
                reverse_slip = self.env['hr.payslip'].search([
                    ('payslip_run_id', '=', self.prima_run_reverse_id.id),
                    ('employee_id', '=', version.employee_id.id),
                ], limit=1)
                if reverse_slip:
                    values['prima_payslip_reverse_id'] = reverse_slip.id
            payslips_vals.append(values)
        self.slip_ids |= Payslip.with_context(tracking_disable=True).create(payslips_vals)
        self.slip_ids._compute_name()
        self.slip_ids.compute_sheet()
        self.state = '01_ready'

        return 1

    def action_open_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'current',
        }

    def assign_status_validated(self):
        for record in self:
            if len(record.slip_ids) > 0:
                record.write({'state': '02_close'})
            else:
                raise ValidationError(_("No existen nóminas asociadas a este lote, no es posible pasar a estado verificar."))

    def action_validate(self):
        settings_batch_account = self.env['ir.config_parameter'].sudo().get_param(
            'zue_hr_payroll.module_hr_payroll_batch_account') or False
        slips_original = self.mapped('slip_ids').filtered(lambda slip: slip.state != 'cancel')
        if settings_batch_account == '1':  # Si en ajustes tiene configurado 'Crear movimiento contable por empleado' ejecutar maximo 200 por envio
            slips = slips_original.filtered(lambda x: len(x.move_id) == 0 or x.move_id == False)[0:200]
        else:
            slips = slips_original
        slips.action_payslip_done()
        if len(slips_original.filtered(lambda x: len(x.move_id) == 0 or x.move_id == False)) == 0:
            self.action_confirm()

    def restart_payroll_batch(self):
        self.mapped('slip_ids').action_payslip_cancel()
        self.mapped('slip_ids').unlink()
        return self.write({'state': '01_ready','observations':False,'time_process':False})

    def restart_payroll_account_batch(self):
        for payslip in self.slip_ids:
            #Eliminar contabilización y el calculo
            payslip.mapped('move_id').unlink()
            #Eliminar historicos
            #self.env['hr.vacation'].search([('payslip', '=', payslip.id)]).unlink()
            self.env['hr.history.prima'].search([('payslip', '=', payslip.id)]).unlink()
            self.env['hr.history.cesantias'].search([('payslip', '=', payslip.id)]).unlink()
            #Reversar Liquidación
            payslip.write({'state': 'draft'})
        return self.write({'state': '01_ready'})

    def restart_full_payroll_batch(self):
        for payslip in self.slip_ids:
            #Eliminar contabilización
            payslip.mapped('move_id').unlink()
            #Eliminar historicos
            #self.env['hr.vacation'].search([('payslip', '=', payslip.id)]).unlink()
            self.env['hr.history.prima'].search([('payslip', '=', payslip.id)]).unlink()
            self.env['hr.history.cesantias'].search([('payslip', '=', payslip.id)]).unlink()
            #Reversar Liquidación
            payslip.write({'state':'draft'})
            payslip.action_payslip_cancel()
            payslip.unlink()

        # self.mapped('slip_ids').action_payslip_cancel()
        # self.mapped('slip_ids').unlink()
        return self.write({'state': '01_ready'})

class Hr_payslip_line(models.Model):
    _inherit = 'hr.payslip.line'

    entity_id = fields.Many2one('hr.employee.entities', string="Entidad")
    loan_id = fields.Many2one('hr.loans', 'Prestamo')
    days_unpaid_absences = fields.Integer(string='Días de ausencias no pagadas')
    amount_base = fields.Float('Base')
    is_history_reverse = fields.Boolean(string='Es historico para reversar')
    note = fields.Char(string='Note')
    #Campos informe detalle
    category_id = fields.Many2one(related='salary_rule_id.category_id', readonly=True, store=True)
    branch_employee_id = fields.Many2one(related='employee_id.branch_id', string='Sucursal', store=True)
    state_slip = fields.Selection(related='slip_id.state', string='Estado Nómina', store=True)
    struct_slip_id = fields.Many2one(related='slip_id.struct_id', string='Estructura', store=True)
    contract_type = fields.Many2one(related='version_id.contract_type_id', string='Tipo de contrato', store=True)
    date_end = fields.Date(related='version_id.date_end', string='Fecha de finalización de contrato', store=True)
    type_of_jurisdiction = fields.Many2one(related='version_id.type_of_jurisdiction', string='Tipo de Fuero', store=True)

    @api.depends('quantity', 'amount', 'rate')
    def _compute_total(self):
        #round_payroll = bool(self.env['ir.config_parameter'].sudo().get_param('zue_hr_payroll.round_payroll')) or False
        for line in self:
            if str(line.salary_rule_id.amount_python_compute).find('get_overtime') != -1:  # Verficiar si la regla utiliza la tabla hr.overtime por ende es un concepto de novedad del menu horas extras
                amount = round(line.amount, 2)
                line.amount = amount
            else:
                amount = line.amount
            amount_total_original = float(line.quantity) * amount * line.rate / 100
            part_decimal, part_value = math.modf(amount_total_original)
            amount_total = float(line.quantity) * amount * line.rate / 100 #if round_payroll == False else float(line.quantity) * line.amount * line.rate / 100
            if part_decimal >= 0.49 and math.modf(amount_total)[1] == part_value:
                line.total = part_value+1
            else:
                line.total = round(amount_total,0)

    def count_category_ids(self):
        count_category_ids = self.env['hr.payslip.line'].search_count([('slip_id', '=', self.slip_id.id), ('category_id', '=', self.category_id.id)])
        return count_category_ids

class Hr_payslip_not_line(models.Model):
    _name = 'hr.payslip.not.line'
    _description = 'Reglas no aplicadas'

    name = fields.Char(string='Nombre',required=True, translate=True)
    note = fields.Text(string='Descripción')
    sequence = fields.Integer(string='Secuencia',required=True, index=True, default=5,
                              help='Use to arrange calculation sequence')
    code = fields.Char(string='Código',required=True)
    slip_id = fields.Many2one('hr.payslip', string='Nómina', required=True, ondelete='cascade')
    salary_rule_id = fields.Many2one('hr.salary.rule', string='Regla', required=True)
    category_id = fields.Many2one(related='salary_rule_id.category_id', string='Categoría', store=True)
    version_id = fields.Many2one('hr.version', string='Contrato', required=True, index=True)
    employee_id = fields.Many2one('hr.employee', string='Empleado', required=True)
    entity_id = fields.Many2one('hr.employee.entities', string="Entidad")
    loan_id = fields.Many2one('hr.loans', 'Prestamo')
    rate = fields.Float(string='Porcentaje (%)', digits='Payroll Rate', default=100.0)
    amount = fields.Float(string='Importe',digits='Payroll')
    quantity = fields.Float(string='Cantidad',digits='Payroll', default=1.0)
    total = fields.Float(compute='_compute_total', string='Total', digits='Payroll', store=True)

    @api.depends('quantity', 'amount', 'rate')
    def _compute_total(self):
        for line in self:
            line.total = float(line.quantity) * line.amount * line.rate / 100

    @api.model_create_multi
    def create(self, values_list):
        for values in values_list:
            if 'employee_id' not in values or 'version_id' not in values:
                payslip = self.env['hr.payslip'].browse(values.get('slip_id'))
                values['employee_id'] = values.get('employee_id') or payslip.employee_id.id
                values['version_id'] = values.get('version_id') or payslip.version_id and payslip.version_id.id
                if not values['version_id']:
                    raise UserError(_('You must set a version to create a payslip line.'))
        return super(Hr_payslip_not_line, self).create(values_list)

class Hr_payslip(models.Model):
    _name = 'hr.payslip'
    _inherit = ['hr.payslip', "analytic.mixin"]

    # Permitir modificar datos del empleado cuando ya tiene nóminas asociadas
    @api.depends('version_id', 'version_id.last_modified_date', 'done_date')
    def _compute_is_wrong_version(self):
        for payslip in self:
            if not payslip.done_date or not payslip.version_id or not payslip.version_id.last_modified_date:
                payslip.has_wrong_data = False
            else:
                payslip.has_wrong_data = payslip.version_id.last_modified_date > payslip.done_date

    # Se quitan los metodos compute de los campos estandar de Odoo porque nosotros no lo hacemos de forma calculada
    date_from = fields.Date(
        string='From', readonly=False, required=True, tracking=True,
        compute=False, store=True, precompute=False)
    date_to = fields.Date(
        string='To', readonly=False, required=True, tracking=True,
        compute=False, store=True, precompute=False)

    rtefte_id = fields.Many2one('hr.employee.rtefte', 'RteFte')
    not_line_ids = fields.One2many('hr.payslip.not.line', 'slip_id', string='Reglas no aplicadas')
    observation = fields.Text(string='Observación')
    analytic_distribution = fields.Json(groups="hr.group_hr_user", tracking=False, string='Distribución analítica')
    analytic_precision = fields.Integer(groups="hr.group_hr_user", tracking=False)
    distribution_analytic_account_ids = fields.Many2many(groups="hr.group_hr_user", tracking=False)
    struct_process = fields.Selection(related='struct_id.process', string='Proceso', store=True)
    employee_branch_id = fields.Many2one(related='employee_id.branch_id', string='Sucursal empleado', store=True)
    definitive_plan = fields.Boolean(string='Plano definitivo generado')
    version_id = fields.Many2one('hr.version', required=True, index=True)
    z_version_domain_ids = fields.Many2many('hr.version', string='Contratos disponibles', compute='_compute_z_version_domain_ids', compute_sudo=False, store=False)
    #Fechas liquidación de contrato
    date_liquidacion = fields.Date('Fecha liquidación de contrato')
    date_prima = fields.Date('Fecha liquidación de prima')
    date_cesantias = fields.Date('Fecha liquidación de cesantías')
    date_vacaciones = fields.Date('Fecha liquidación de vacaciones')

    # Eliminar históricos de vacaciones cuando la liquidación pase a Borrador o Cancelado y al reversar contabilización del lote
    def write(self, vals):
        vacation_history = self.env['hr.payslip']
        if 'state' in vals and vals['state'] in ('draft', 'cancel'):
            vacation_history = self.filtered(lambda p: p.state not in ('draft', 'cancel'))
        res = super().write(vals)
        if vacation_history:
            self.env['hr.vacation'].search([('payslip', 'in', vacation_history.ids)]).unlink()
        return res

    # Campo computado para traer solo contratos activos
    @api.depends('company_id', 'employee_id')
    def _compute_z_version_domain_ids(self):
        for payslip in self:
            if payslip.company_id and payslip.employee_id:
                payslip.z_version_domain_ids = self.env['hr.version'].search([
                    ('company_id', '=', payslip.company_id.id),
                    ('employee_id', '=', payslip.employee_id.id),
                    ('employee_id.active', '=', True),
                    ('retirement_date', '=', False),
                ])
            else:
                payslip.z_version_domain_ids = self.env['hr.version']

    # Asigna version_id solo a contratos activos al cambiar empleado o compañía
    @api.onchange('employee_id', 'company_id')
    def _onchange_employee_version_id(self):
        if self.employee_id and self.company_id:
            active_versions = self.env['hr.version'].search([
                ('company_id', '=', self.company_id.id),
                ('employee_id', '=', self.employee_id.id),
                ('employee_id.active', '=', True),
                ('retirement_date', '=', False),
            ])
            if self.version_id and (self.version_id.contract_date_end or self.version_id not in active_versions):
                self.version_id = active_versions[:1] if active_versions else self.env['hr.version']
            elif not self.version_id and active_versions:
                self.version_id = active_versions[0]
        else:
            self.version_id = self.env['hr.version']

    #Anular metodo de ODOO
    @api.depends('date_from','date_to')
    def _compute_date_to(self):
        for payslip in self:
            payslip.date_to = payslip.date_to

    @api.depends('payslip_run_id', 'employee_id', 'date_from')
    def _compute_display_name(self):
        for record in self:
            if record.payslip_run_id:
                record.display_name = "{} - {}".format(record.payslip_run_id.name,record.employee_id.name)
            else:
                record.display_name = "{} - {} - {}".format(record.struct_id.name,record.employee_id.name,str(record.date_from))

    def get_hr_payslip_reports_template(self):
        type_report = self.struct_process if self.struct_process != 'otro' else 'nomina'
        obj = self.env['hr.payslip.reports.template'].search([('company_id','=',self.employee_id.company_id.id),('type_report','=',type_report)])
        if len(obj) == 0:
            raise ValidationError(_('No tiene configurada plantilla de liquidacion. Por favor verifique!'))
        return obj

    def get_pay_vacations_in_payroll(self):
        return bool(
            self.env['ir.config_parameter'].sudo().get_param('zue_hr_payroll.pay_vacations_in_payroll')) or False

    @api.onchange('worked_days_line_ids', 'input_line_ids')
    def _onchange_worked_days_inputs(self):
        if self.line_ids and self.state in ['draft', 'validated']:
            if self.struct_id.process == 'nomina':
                values = [(5, 0, 0)] + [(0, 0, line_vals) for line_vals in self._get_payslip_lines()]
            elif self.struct_id.process == 'vacaciones':
                values = [(5, 0, 0)] + [(0, 0, line_vals) for line_vals in self._get_payslip_lines_vacation()]
            elif self.struct_id.process == 'cesantias' or self.struct_id.process == 'intereses_cesantias':
                values = [(5, 0, 0)] + [(0, 0, line_vals) for line_vals in self._get_payslip_lines_cesantias()]
            elif self.struct_id.process == 'prima':
                values = [(5, 0, 0)] + [(0, 0, line_vals) for line_vals in self._get_payslip_lines_prima()]
            elif self.struct_id.process == 'contrato':
                contrato_lines = self._get_payslip_lines_contrato()
                values = [(5, 0, 0)] + [(0, 0, line_vals) for line_vals in contrato_lines]
                self.update({
                    'line_ids': values,
                    'z_vacation_contract_line_skip': self.z_vacation_contract_line_skip,
                })
                return
            elif self.struct_id.process == 'otro':
                values = [(5, 0, 0)] + [(0, 0, line_vals) for line_vals in self._get_payslip_lines_other()]
            else:
                raise ValidationError(_('La estructura seleccionada se encuentra en desarrollo.'))

            self.update({'line_ids': values})

    def compute_sheet(self):
        for payslip in self.filtered(lambda slip: slip.state not in ['cancel', 'validated']):
            payslip.z_vacation_contract_line_skip = False
            name = payslip.name
            # delete old payslip lines
            payslip.line_ids.unlink()
            payslip.not_line_ids.unlink()

            #Seleccionar proceso a ejecutar
            lines = []
            if payslip.struct_id.process == 'nomina':
                lines = [(0, 0, line) for line in payslip._get_payslip_lines()]
            elif payslip.struct_id.process == 'vacaciones':
                lines = [(0, 0, line) for line in payslip._get_payslip_lines_vacation()]
            elif payslip.struct_id.process == 'cesantias' or payslip.struct_id.process == 'intereses_cesantias':
                lines = [(0, 0, line) for line in payslip._get_payslip_lines_cesantias()]
            elif payslip.struct_id.process == 'prima':
                lines = [(0, 0, line) for line in payslip._get_payslip_lines_prima()]
            elif payslip.struct_id.process == 'contrato':
                lines = [(0, 0, line) for line in payslip._get_payslip_lines_contrato()]
            elif payslip.struct_id.process == 'otro':
                lines = [(0, 0, line) for line in payslip._get_payslip_lines_other()]
            else:
                raise ValidationError(_('La estructura seleccionada se encuentra en desarrollo.'))

            if lines:
                write_vals = {
                    'line_ids': lines,
                    'name': name,
                    'state': 'draft',
                    'analytic_distribution': payslip.version_id.analytic_distribution,
                    'compute_date': fields.Date.today(),
                }
                if payslip.struct_id.process == 'contrato':
                    write_vals['z_vacation_contract_line_skip'] = payslip.z_vacation_contract_line_skip
                payslip.write(write_vals)
        return True

    def restart_payroll(self):
        for payslip in self:
            #Eliminar contabilización y el calculo
            if payslip.mapped('move_id').state == 'posted':
                raise ValidationError(f'No puedes reversar un movimiento contable de nómina publicado.')
            payslip.mapped('move_id').unlink()
            # Modificar cuotas de prestamos pagadas
            obj_payslip_line = self.env['hr.payslip.line'].search(
                [('slip_id', '=', payslip.id), ('loan_id', '!=', False)])
            for payslip_line in obj_payslip_line:
                obj_loan_line = self.env['hr.loans.line'].search(
                    [('employee_id', '=', payslip_line.employee_id.id), ('prestamo_id', '=', payslip_line.loan_id.id),
                     ('payslip_id', '>=', payslip.id)])
                if payslip.struct_id.process == 'contrato' and payslip_line.loan_id.final_settlement_version == True:
                    obj_loan_line.unlink()
                else:
                    obj_loan_line.write({
                        'paid': False,
                        'payslip_id': False
                    })
                obj_loan = self.env['hr.loans'].search(
                    [('employee_id', '=', payslip_line.employee_id.id), ('id', '=', payslip_line.loan_id.id)])
                if obj_loan.balance_amount > 0:
                    self.env['hr.contract.concepts'].search([('loan_id', '=', payslip_line.loan_id.id)]).write(
                        {'state': 'done'})
            payslip.line_ids.unlink()
            payslip.not_line_ids.unlink()
            #Eliminar historicos
            #self.env['hr.vacation'].search([('payslip', '=', payslip.id)]).unlink()
            self.env['hr.history.prima'].search([('payslip', '=', payslip.id)]).unlink()
            self.env['hr.history.cesantias'].search([('payslip', '=', payslip.id)]).unlink()
            #Reversar Liquidación            
            payslip.action_payslip_draft()            

    #--------------------------------------------------LIQUIDACIÓN DE LA NÓMINA PERIÓDICA---------------------------------------------------------#

    def _get_new_worked_days_lines(self):
        if self.struct_id.use_worked_day_lines:
            # computation of the salary worked days
            worked_days_line_values = self._get_worked_day_lines()
            worked_days_lines = self.worked_days_line_ids.browse([])
            for r in worked_days_line_values:
                r['payslip_id'] = self.id
                worked_days_lines |= worked_days_lines.new(r)
            # Validar que al ser el mes de febrero modifique los días trabajados para que sean igual a un mes de 30 días
            if self.date_to.month == 2 and self.date_to.day in (28,29):
                february_worked_days = worked_days_lines.filtered(lambda l: l.work_entry_type_id.code == 'WORK100')
                days_summary = 2 if self.date_to.day == 28 else 1
                hours_summary = 16 if self.date_to.day == 28 else 8
                if len(february_worked_days) > 0:
                    for february_days in worked_days_lines:
                        if february_days.work_entry_type_id.code == 'WORK100':
                            february_days.number_of_days = february_days.number_of_days + days_summary # Se agregan 2 días
                            february_days.number_of_hours = february_days.number_of_hours + hours_summary # Se agregan 16 horas
                else:
                    # Ultimo día de febrero
                    # work_hours = self.version_id._get_work_hours(self.date_to, self.date_to)
                    work_hours = self.version_id._get_work_hours(self.date_to,self.date_to)
                    work_hours_ordered = sorted(work_hours.items(), key=lambda x: x[1])
                    biggest_work = work_hours_ordered[-1][0] if work_hours_ordered else 0
                    # Primer día de marzo
                    march_date_from = self.date_to + timedelta(days=1)
                    march_date_to = self.date_to + timedelta(days=1)
                    # Calcular horas laboradas
                    march_work_hours = self.version_id._get_work_hours(march_date_from, march_date_to)
                    march_work_hours_ordered = sorted(march_work_hours.items(), key=lambda x: x[1])
                    march_biggest_work = march_work_hours_ordered[-1][0] if march_work_hours_ordered else 0
                    # Proceso a realizar
                    if march_biggest_work == 0 or biggest_work != march_biggest_work:  # Si la ausencia no continua hasta marzo se agregan 2 días trabajados para completar los 30 días en febrero
                        work_entry_type = self.env['hr.work.entry.type'].search([('code', '=', 'WORK100')])
                        attendance_line = {
                            'sequence': work_entry_type.sequence,
                            'work_entry_type_id': work_entry_type.id,
                            'number_of_days': days_summary,
                            'number_of_hours': hours_summary,
                            'amount': 0,
                        }
                        worked_days_lines |= worked_days_lines.new(attendance_line)
                    else:  # Si la ausencia continua hasta marzo se agregan 2 días de la ausencia para completar los 30 días en febrero
                        work_entry_type = self.env['hr.work.entry.type'].search([('id', '=', biggest_work)])
                        for february_days in worked_days_lines:
                            if february_days.work_entry_type_id.code == work_entry_type.code:
                                february_days.number_of_days = february_days.number_of_days + days_summary  # Se agregan 2 días
                                february_days.number_of_hours = february_days.number_of_hours + hours_summary  # Se agregan 16 horas
            #return worked_days_lines
            res = []
            for w in worked_days_lines:
                res.append({
                    'sequence': w.sequence,
                    'work_entry_type_id': w.work_entry_type_id.id,
                    'number_of_days': w.number_of_days,
                    'number_of_hours': w.number_of_hours,
                })
            if self.struct_id.process == 'contrato' and self.date_from == self.date_to and self.z_no_days_worked:
                return [(5, False, False)]
            else:
                return [(5, 0, 0)] + [(0, 0, vals) for vals in res]
        else:
            return [(5, False, False)]

    # Se reemplaza metodo de Odoo ya que interfiere con la localizacion Colombiana
    @api.depends('date_from', 'date_to', 'struct_id')
    def _compute_warning_message(self):
        for slip in self.filtered(lambda p: p.date_to):
            slip.warning_message = False

    def _get_payslip_lines(self,inherit_vacation=0,inherit_prima=0,inherit_contrato_dev=0,inherit_contrato_ded_bases=0,inherit_contrato_ded=0,localdict=None):
        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
            localdict['categories'].dict[category.code] = localdict['categories'].dict.get(category.code, 0) + amount
            return localdict

        def _sum_salary_rule(localdict, rule, amount):
            localdict['rules_computed'].dict[rule.code] = localdict['rules_computed'].dict.get(rule.code, 0) + amount
            #Sumatoria de valores que son base para los procesos
            if rule.category_id.code != 'BASIC' and amount != 0:
                localdict['values_base_prima'] += amount if rule.base_prima else 0
                localdict['values_base_cesantias'] += amount if rule.base_cesantias else 0
                localdict['values_base_int_cesantias'] += amount if rule.base_intereses_cesantias else 0
                localdict['values_base_compensation'] += amount if rule.z_base_compensation else 0
                localdict['values_base_vacremuneradas'] += amount if rule.base_vacaciones_dinero else 0
                localdict['values_base_vacdisfrutadas'] += amount if rule.base_vacaciones else 0
            
            return localdict

        self.ensure_one()
        result = {}
        result_not = {}
        rules_dict = {}
        if inherit_contrato_ded_bases + inherit_contrato_ded + inherit_contrato_dev == 1 and (self.date_from == self.date_to and self.z_no_days_worked):
            worked_days_dict = {}
        else:
            worked_days_dict = {line.code: line for line in self.worked_days_line_ids if line.code}
        inputs_dict = {line.code: line for line in self.input_line_ids if line.code}
        pay_vacations_in_payroll = bool(self.env['ir.config_parameter'].sudo().get_param(
            'zue_hr_payroll.pay_vacations_in_payroll')) or False
        vacation_days_calculate_absences = int(self.env['ir.config_parameter'].sudo().get_param(
            'zue_hr_payroll.vacation_days_calculate_absences')) or 5
        round_payroll = bool(self.env['ir.config_parameter'].sudo().get_param('zue_hr_payroll.round_payroll')) or False
        
        worked_days_entry = 0
        leaves_days_law = 0
        leaves_days_all = 0
        for days in self.worked_days_line_ids:
            worked_days_entry = worked_days_entry + (days.number_of_days if days.work_entry_type_id.is_leave == False else 0)
            leaves_days_law = leaves_days_law + (days.number_of_days if days.work_entry_type_id.is_leave and days.work_entry_type_id.deduct_deductions == 'law' else 0)
            leaves_days_all = leaves_days_all + (days.number_of_days if days.work_entry_type_id.is_leave and days.work_entry_type_id.deduct_deductions == 'all' else 0)

        employee = self.employee_id
        version = self.version_id
        year = self.date_from.year
        annual_parameters = self.env['hr.annual.parameters'].search([('year', '=', year)])

        #Se eliminan registros actuales para el periodo ejecutado de Retención en la fuente
        # Se comenta con base a la historia Validar bases de retención cuando la liquidación esta registrada
        self.env['hr.employee.deduction.retention'].search([('employee_id', '=', employee.id),('year', '=', self.date_from.year),('month', '=', self.date_from.month)]).unlink()
        self.env['hr.employee.rtefte'].search([('employee_id', '=', employee.id),('year', '=', self.date_from.year),('month', '=', self.date_from.month)]).unlink()

        #Se obtienen las entradas de trabajo
        date_from = datetime.combine(self.date_from, datetime.min.time())
        date_to = datetime.combine(self.date_to, datetime.max.time())
        work_entries = self.env['hr.work.entry'].search([
            ('state', 'in', ['validated', 'draft']),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('version_id', '=', version.id),
            ('leave_id', '!=', False)
        ])
        #Validar incapacidades de mas de 180 dias
        leaves = {}
        leave_entity_by_work_code = {}
        lst_leave_ids = []
        for leave in work_entries:
            if leave.leave_id:
                if leave.leave_id.id not in lst_leave_ids:
                    lst_leave_ids.append(leave.leave_id.id)
                    if leave.leave_id.entity and leave.work_entry_type_id.code:
                        wcode = leave.work_entry_type_id.code
                        if wcode not in leave_entity_by_work_code:
                            leave_entity_by_work_code[wcode] = leave.leave_id.entity.id
                    es_continuidad = 1
                    number_of_days_total = leave.leave_id.number_of_days
                    holiday_status_id = leave.leave_id.holiday_status_id.id
                    request_date_to = leave.leave_id.request_date_from - timedelta(days=1)
                    #Fecha Ausencia pertenecientes a la liquidación
                    start_leave = True if leave.leave_id.request_date_from >= self.date_from else False
                    end_leave = True if leave.leave_id.request_date_to <= self.date_to else False
                    initial_date = leave.leave_id.request_date_from if leave.leave_id.request_date_from >= self.date_from else self.date_from
                    end_date = leave.leave_id.request_date_to if leave.leave_id.request_date_to <= self.date_to else self.date_to
                    number_of_days = (end_date-initial_date).days + 1
                    if self.version_id.method_schedule_pay == 'bi-weekly' and self.date_from.month == 2 and self.date_to.month == 2 and self.date_from.day == 16 and self.date_to.day in (28, 29):
                        period_days = (self.date_to - self.date_from).days + 1
                        number_of_days = (number_of_days * 15.0) / period_days if period_days > 0 else number_of_days
                    '''
                    while es_continuidad == 1:
                        obj_leave = self.env['hr.leave'].search([('employee_id', '=', employee.id),('state','=','validate'),
                                                                ('holiday_status_id','=',holiday_status_id),('request_date_to','=',request_date_to)])
                        if obj_leave:
                            number_of_days = number_of_days + obj_leave.number_of_days
                            holiday_status_id = obj_leave.holiday_status_id.id
                            request_date_to = obj_leave.request_date_from - timedelta(days=1)
                        else:
                            es_continuidad = 0
                    '''
                    if leaves.get(leave.work_entry_type_id.code,False):
                        leaves[leave.work_entry_type_id.code+'_TOTAL'] += number_of_days_total
                        leaves[leave.work_entry_type_id.code + '_PLUS90'] += number_of_days_total if number_of_days_total > 90 else 0
                        leaves[leave.work_entry_type_id.code + '_MINUS90'] += number_of_days_total if number_of_days_total <= 90 else 0
                        leaves[leave.work_entry_type_id.code] += number_of_days
                    else:
                        leaves[leave.work_entry_type_id.code+'_TOTAL'] = number_of_days_total
                        leaves[leave.work_entry_type_id.code + '_PLUS90'] = number_of_days_total if number_of_days_total > 90 else 0
                        leaves[leave.work_entry_type_id.code + '_MINUS90'] = number_of_days_total if number_of_days_total <= 90 else 0
                        leaves[leave.work_entry_type_id.code] = number_of_days
                    #Guardar dias que asume la compañia
                    obj_leave_type = self.env['hr.leave.type'].search([('code', '=', leave.work_entry_type_id.code)],limit=1)
                    if len(obj_leave_type) > 0:
                        if obj_leave_type.num_days_no_assume > 0:
                            if start_leave or (start_leave and end_leave):
                                days_company = obj_leave_type.num_days_no_assume if number_of_days >= obj_leave_type.num_days_no_assume else number_of_days
                                days_partner = number_of_days - obj_leave_type.num_days_no_assume if number_of_days >= obj_leave_type.num_days_no_assume else 0
                            if end_leave and not start_leave:
                                num_days_no_assume = (((initial_date - leave.leave_id.request_date_from).days + 1)-obj_leave_type.num_days_no_assume)
                                if num_days_no_assume > 0:
                                    days_company = 0
                                    days_partner = number_of_days
                                else:
                                    num_days_no_assume = 1 if abs(num_days_no_assume)==0 else num_days_no_assume
                                    num_days_no_assume = obj_leave_type.num_days_no_assume if abs(num_days_no_assume)>=obj_leave_type.num_days_no_assume else num_days_no_assume
                                    days_company = abs(num_days_no_assume)
                                    days_partner = number_of_days - abs(num_days_no_assume) if number_of_days >= abs(num_days_no_assume) else 0
                            if not start_leave and not end_leave:
                                days_company = 0
                                days_partner = number_of_days
                            if leaves.get(leave.work_entry_type_id.code+'_COMPANY', False):
                                leaves[leave.work_entry_type_id.code+'_COMPANY'] += days_company
                            else:
                                leaves[leave.work_entry_type_id.code + '_COMPANY'] = days_company
                            if leaves.get(leave.work_entry_type_id.code + '_PARTNER', False):
                                leaves[leave.work_entry_type_id.code + '_PARTNER_PLUS90'] += days_partner if number_of_days_total > 90 else 0
                                leaves[leave.work_entry_type_id.code + '_PARTNER_MINUS90'] += days_partner if number_of_days_total <= 90 else 0
                                leaves[leave.work_entry_type_id.code + '_PARTNER'] += days_partner
                            else:
                                leaves[leave.work_entry_type_id.code + '_PARTNER_PLUS90'] = days_partner if number_of_days_total > 90 else 0
                                leaves[leave.work_entry_type_id.code + '_PARTNER_MINUS90'] = days_partner if number_of_days_total <= 90 else 0
                                leaves[leave.work_entry_type_id.code + '_PARTNER'] = days_partner
        
        if localdict == None:
            localdict = {
                **self._get_base_local_dict(),
                **{
                    'categories': BrowsableObject(employee.id, {}, self.env),
                    'rules_computed': BrowsableObject(employee.id, {}, self.env),
                    'rules': BrowsableObject(employee.id, rules_dict, self.env),
                    'payslip': Payslips(employee.id, self, self.env),
                    'worked_days': WorkedDays(employee.id, worked_days_dict, self.env),
                    'inputs': InputLine(employee.id, inputs_dict, self.env),
                    'leaves':  BrowsableObject(employee.id, leaves, self.env),
                    'employee': employee,
                    'version': version,
                    'annual_parameters': annual_parameters,
                    'values_leaves_all' : 0,
                    'values_leaves_law' : 0,
                    #Sumatoria de valores que son base para los procesos
                    'values_base_prima': 0,
                    'values_base_cesantias': 0,
                    'values_base_int_cesantias': 0,
                    'values_base_compensation': 0,
                    'values_base_vacremuneradas': 0,
                    'values_base_vacdisfrutadas': 0,
                    'inherit_contrato':inherit_contrato_ded_bases+inherit_contrato_ded+inherit_contrato_dev,
                    'inherit_prima':inherit_prima,
                }
            }
        else:
            localdict.update({
                'worked_days': WorkedDays(employee.id, worked_days_dict, self.env),
                'inputs': InputLine(employee.id, inputs_dict, self.env),
                'values_leaves_all' : localdict.get('values_leaves_all',0),
                'values_leaves_law' : localdict.get('values_leaves_law',0),
                #Sumatoria de valores que son base para los procesos
                'values_base_prima': localdict.get('values_base_prima',0),
                'values_base_cesantias': localdict.get('values_base_cesantias',0),
                'values_base_int_cesantias': localdict.get('values_base_int_cesantias',0),
                'values_base_compensation': localdict.get('values_base_compensation',0),
                'values_base_vacremuneradas': localdict.get('values_base_vacremuneradas',0),
                'values_base_vacdisfrutadas': localdict.get('values_base_vacdisfrutadas',0),
                'inherit_contrato':inherit_contrato_ded_bases+inherit_contrato_ded+inherit_contrato_dev,
                'inherit_prima':inherit_prima,})
            if localdict.get('leaves',False) == False:
                localdict.update({'leaves': BrowsableObject(employee.id, leaves, self.env), })

        #Saber si tiene días de vacaciones
        days_vac = 0
        days_vac += leaves.get('VACDISFRUTADAS') if leaves.get('VACDISFRUTADAS') != None else 0
        #days_vac += leaves.get('VACREMUNERADAS') if leaves.get('VACREMUNERADAS') != None else 0

        worked_days_vac = 0
        worked_days_vac += worked_days_dict.get('VACDISFRUTADAS').number_of_days  if worked_days_dict.get('VACDISFRUTADAS') != None else 0
        #worked_days_vac += worked_days_dict.get('VACREMUNERADAS').number_of_days  if worked_days_dict.get('VACREMUNERADAS') != None else 0

        #Ejecutar vacaciones dentro de la nómina - 16/02/2022
        if pay_vacations_in_payroll == True and inherit_vacation == 0 and inherit_contrato_ded_bases+inherit_contrato_ded+inherit_contrato_dev == 0 and inherit_prima == 0:
            struct_original = self.struct_id.id
            #Vacaciones
            obj_struct_vacation = self.env['hr.payroll.structure'].search([('process', '=', 'vacaciones')])
            self.struct_id = obj_struct_vacation.id
            localdict, result_vac = self._get_payslip_lines_vacation(inherit_contrato=0, localdict=localdict, inherit_nomina=1)
            #Continuar con la nómina
            self.struct_id = struct_original
            worked_days_dict = {line.code: line for line in self.worked_days_line_ids if line.code}
            inputs_dict = {line.code: line for line in self.input_line_ids if line.code}
            localdict.update({'worked_days': WorkedDays(employee.id, worked_days_dict, self.env),
                              'inputs': InputLine(employee.id, inputs_dict, self.env),
                              'leaves': BrowsableObject(employee.id, leaves, self.env)})
        else:
            result_vac = {}

        #Cargar novedades por conceptos diferentes
        obj_novelties = self.env['hr.novelties.different.concepts'].search([('employee_id', '=', employee.id),
                                                            ('date', '>=', self.date_from),('date', '<=', self.date_to)])
        for concepts in obj_novelties:
            if concepts.amount != 0 and inherit_prima == 0 and inherit_vacation == 0:
                previous_amount = concepts.salary_rule_id.code in localdict and localdict[concepts.salary_rule_id.code] or 0.0
                #set/overwrite the amount computed for this rule in the localdict
                tot_rule = round(concepts.amount * 1.0 * 100 / 100.0,0) if round_payroll == False else concepts.amount * 1.0 * 100 / 100.0

                #LIQUIDACION DE CONTRATO SOLO DEV OR DED DEPENDIENTO SU ORIGEN
                if (inherit_contrato_dev != 0 or inherit_contrato_ded != 0 or inherit_contrato_ded_bases != 0) and self.novelties_payroll_concepts == False and not concepts.salary_rule_id.code in ['TOTALDEV','TOTALDED','NET']:
                   tot_rule = 0
                if inherit_contrato_dev != 0 and concepts.salary_rule_id.dev_or_ded != 'devengo':                            
                    tot_rule = 0
                if inherit_contrato_ded+inherit_contrato_ded_bases != 0 and concepts.salary_rule_id.dev_or_ded != 'deduccion' and not concepts.salary_rule_id.code in ['TOTALDEV','NET']:
                    tot_rule = 0
                if inherit_contrato_ded != 0 and concepts.salary_rule_id.dev_or_ded == 'deduccion' and not concepts.salary_rule_id.code in ['TOTALDEV','NET'] \
                        and (concepts.salary_rule_id.base_prima or concepts.salary_rule_id.base_cesantias or concepts.salary_rule_id.base_vacaciones_dinero or concepts.salary_rule_id.base_intereses_cesantias):
                    tot_rule = 0
                if inherit_contrato_ded_bases != 0 and concepts.salary_rule_id.dev_or_ded == 'deduccion' and not concepts.salary_rule_id.code in ['TOTALDEV','NET'] \
                        and not(concepts.salary_rule_id.base_prima or concepts.salary_rule_id.base_cesantias or concepts.salary_rule_id.base_vacaciones_dinero or concepts.salary_rule_id.base_intereses_cesantias):
                    tot_rule = 0

                if tot_rule != 0:
                    localdict[concepts.salary_rule_id.code+'-PCD'] = tot_rule
                    rules_dict[concepts.salary_rule_id.code+'-PCD'] = concepts.salary_rule_id
                    # sum the amount for its salary category
                    localdict = _sum_salary_rule_category(localdict, concepts.salary_rule_id.category_id, tot_rule - previous_amount)
                    localdict = _sum_salary_rule(localdict, concepts.salary_rule_id, tot_rule)
                    #Guardar valores de ausencias dependiendo parametrización
                    if concepts.salary_rule_id.is_leave:
                        amount_leave = tot_rule if concepts.salary_rule_id.deduct_deductions == 'all' else 0
                        localdict['values_leaves_all'] = localdict['values_leaves_all'] + amount_leave
                        amount_leave_law = tot_rule if concepts.salary_rule_id.deduct_deductions == 'law' else 0
                        localdict['values_leaves_law'] = localdict['values_leaves_law'] + amount_leave_law

                    result_item = concepts.salary_rule_id.code+'-PCD'+str(concepts.id)
                    result[result_item] = {
                        'sequence': concepts.salary_rule_id.sequence,
                        'code': concepts.salary_rule_id.code,
                        'name': concepts.salary_rule_id.name,
                        'note': concepts.salary_rule_id.note,
                        'salary_rule_id': concepts.salary_rule_id.id,
                        'version_id': version.id,
                        'employee_id': employee.id,
                        'entity_id': concepts.partner_id.id if concepts.partner_id else False,
                        # 'loan_id': loan_id,
                        'amount': tot_rule, #Se redondean los decimales de todas las reglas
                        'quantity': 1.0,
                        'rate': 100,
                        'total': self._get_payslip_line_total(tot_rule, 1, 100, concepts.salary_rule_id),
                        'slip_id': self.id,
                    }

        #Ejecutar las reglas salariales y su respectiva lógica
        for rule in sorted(self.struct_id.rule_ids, key=lambda x: x.sequence):
            localdict.update({
                'id_version_concepts': 0,
                'result': None,
                'result_qty': 1.0,
                'result_rate': 100})
            if rule._satisfy_condition(localdict):
                entity_id,loan_id = False,False
                #Obtener entidades de seguridad social
                if rule.category_id.code == 'SSOCIAL':
                    for entity in employee.social_security_entities:
                        if entity.contrib_id.type_entities == 'eps' and rule.code == 'SSOCIAL001': # SALUD
                            entity_id = entity.partner_id.id
                        if entity.contrib_id.type_entities == 'pension' and (rule.code == 'SSOCIAL002' or rule.code == 'SSOCIAL003' or rule.code == 'SSOCIAL004'): # Pension
                            entity_id = entity.partner_id.id
                        if entity.contrib_id.type_entities == 'subsistencia' and rule.code == 'SSOCIAL003': # Subsistencia
                            entity_id = entity.partner_id.id
                        if entity.contrib_id.type_entities == 'solidaridad' and rule.code == 'SSOCIAL004': # Solidaridad
                            entity_id = entity.partner_id.id
                if not entity_id and leave_entity_by_work_code:
                    leave_types = self.env['hr.leave.type'].search([
                        '|',
                        ('eps_arl_input_id', '=', rule.id),
                        ('company_input_id', '=', rule.id),
                    ])
                    for leave in leave_types:
                        entity = leave_entity_by_work_code.get(leave.code)
                        if entity:
                            entity_id = entity
                            break
                #Valida que si la regla esta en la pestaña de Devengo & Deducciones del contrato
                obj_concept = self.env['hr.contract.concepts'].search([('version_id', '=', version.id),('input_id','=',rule.id), ('state','=','done')])

                if obj_concept:
                    #Obtener Info devengos y deducciónes - Contrato empleados
                    for concept in obj_concept:
                        date_start_concept = concept.date_start if concept.date_start else datetime.strptime('01/01/1900', '%d/%m/%Y').date()
                        date_end_concept = concept.date_end if concept.date_end else datetime.strptime('31/12/2080', '%d/%m/%Y').date()
                        if concept.state == 'done' and date_start_concept <= date_to.date() and date_end_concept >= date_from.date():
                            localdict.update({'id_version_concepts': concept.id})
                            if concept.partner_id:
                                entity_id = concept.partner_id.id
                            loan_id = concept.loan_id.id
                            amount, qty, rate = rule._compute_rule(localdict)
                            #Validar si no tiene dias trabajados, si no tiene revisar las ausencias y sus caracteristicas para calcular la deducción
                            if rule.dev_or_ded == 'deduccion' and rule.type_concept != 'ley' and (worked_days_entry + leaves_days_all) == 0 and inherit_prima == 0:
                                amount, qty, rate = 0,1.0,100

                            #LIQUIDACION DE CONTRATO SOLO DEV OR DED DEPENDIENTO SU ORIGEN
                            # PRIMA SOLAMENTE DEDUCCIONES QUE ESTEN CONFIGURADAS
                            # VACACIONES SOLAMENTE DEDUCCIONES
                            if ((inherit_contrato_dev != 0 or inherit_contrato_ded != 0 or inherit_contrato_ded_bases != 0) and self.settle_payroll_concepts == False and not rule.code in ['TOTALDEV','TOTALDED','NET'])\
                                    or (inherit_contrato_dev != 0 and rule.dev_or_ded != 'devengo') \
                                    or (inherit_contrato_ded+inherit_contrato_ded_bases != 0 and rule.dev_or_ded != 'deduccion' and not rule.code in ['TOTALDEV','NET']) \
                                    or (inherit_contrato_ded != 0 and rule.dev_or_ded == 'deduccion' and not rule.code in ['TOTALDEV','NET'] and (rule.base_prima or rule.base_cesantias or rule.base_vacaciones_dinero or rule.base_intereses_cesantias)) \
                                    or (inherit_contrato_ded_bases != 0 and rule.dev_or_ded == 'deduccion' and not rule.code in ['TOTALDEV','NET'] and not(rule.base_prima or rule.base_cesantias or rule.base_vacaciones_dinero or rule.base_intereses_cesantias)) \
                                    or (inherit_prima != 0 and rule.dev_or_ded != 'deduccion' and not rule.code in ['TOTALDEV','NET']) \
                                    or (inherit_prima != 0 and rule.dev_or_ded == 'deduccion' and rule.deduction_applies_bonus == False) \
                                    or (inherit_vacation != 0 and rule.dev_or_ded != 'deduccion' and not rule.code in ['TOTALDEV','NET']):
                                amount, qty, rate = 0,1.0,100

                            if days_vac > vacation_days_calculate_absences and rule.dev_or_ded == 'deduccion' and not rule.code in ['TOTALDED']:
                                if inherit_vacation != 0:
                                    month_from = self.date_from.month
                                    year_from = self.date_from.year
                                    initial_date = self.date_from
                                    end_date = self.date_to
                                    vac_months = []
                                    str_vac = str(month_from)+'_'+str(year_from)
                                    vac_months.append(str_vac)
                                    vac_days_for_month = {}
                                    days_fifteen = 0
                                    days_thirty = 0
                                    while initial_date <= end_date:
                                        if initial_date.day <= 15:
                                            days_fifteen += 1
                                        else:
                                            days_thirty += 1

                                        initial_date = initial_date + timedelta(days=1)
                                        str_vac = str(month_from)+'_'+str(year_from)
                                        vac_days_for_month[str_vac] = {'days_fifteen':days_fifteen,'days_thirty':days_thirty}

                                        if initial_date.month != month_from:
                                            month_from = initial_date.month
                                            year_from = initial_date.year
                                            str_vac = str(month_from) + '_' + str(year_from)
                                            vac_months.append(str_vac)
                                            days_fifteen = 0
                                            days_thirty = 0

                                    #Cant de quincenas involucradas en la liquidación de vacaciones que afecten mas de vacation_days_calculate_absences
                                    cant_fortnight = 0
                                    for vac_days in vac_months:
                                        if vac_days_for_month.get(vac_days) != None:
                                            cant_fortnight += 1 if vac_days_for_month.get(vac_days).get('days_fifteen') > vacation_days_calculate_absences else 0
                                            cant_fortnight += 1 if vac_days_for_month.get(vac_days).get('days_thirty') > vacation_days_calculate_absences else 0

                                    if cant_fortnight > 1:
                                        amount = amount * cant_fortnight if not rule.modality_value in ['diario','diario_efectivo'] and rule.type_concept != 'ley' else amount

                                    if cant_fortnight == 0:
                                        amount, qty, rate = 0, 1.0, 100
                                else:
                                    if worked_days_vac > vacation_days_calculate_absences:
                                        amount, qty, rate = 0,1.0,100
                            else:
                                if inherit_vacation != 0:
                                    amount, qty, rate = 0, 1.0, 100

                            #Continuar con el proceso normal
                            amount = round(amount,0) if round_payroll == False else amount #Se redondean los decimales de todas las reglas
                            if amount != 0:
                                #check if there is already a rule computed with that code
                                previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                                #set/overwrite the amount computed for this rule in the localdict
                                tot_rule_original = (amount * qty * rate / 100.0)
                                part_decimal, part_value = math.modf(tot_rule_original)
                                tot_rule = round(amount * qty * rate / 100.0,0)
                                if part_decimal >= 0.49 and tot_rule == part_value:
                                    tot_rule = (part_value + 1)+previous_amount
                                else:
                                    tot_rule = tot_rule+previous_amount
                            else:
                                tot_rule, previous_amount = 0, 0
                            localdict[rule.code] = tot_rule
                            rules_dict[rule.code] = rule
                            # sum the amount for its salary category
                            localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
                            localdict = _sum_salary_rule(localdict, rule, tot_rule)
                            #Guardar valores de ausencias dependiendo parametrización
                            if rule.is_leave:
                                amount_leave = (float(qty) * amount * rate / 100) if rule.deduct_deductions == 'all' else 0
                                localdict['values_leaves_all'] = localdict['values_leaves_all'] + amount_leave
                                amount_leave_law = (float(qty) * amount * rate / 100) if rule.deduct_deductions == 'law' else 0
                                localdict['values_leaves_law'] = localdict['values_leaves_law'] + amount_leave_law

                            # create/overwrite the rule in the temporary results
                            if amount != 0:
                                result_item = rule.code+'-'+str(concept.id) if concept.id else rule.code
                                if rule.dev_or_ded == 'deduccion' and inherit_prima == 0:
                                    if rule.type_concept == 'ley':
                                        value_tmp_neto = localdict['categories'].dict.get('DEV_SALARIAL',0) + localdict['categories'].dict.get('DEV_NO_SALARIAL',0) + localdict['categories'].dict.get('PRESTACIONES_SOCIALES',0) + localdict['categories'].dict.get('DEDUCCIONES',0)
                                    else:
                                        value_tmp_neto = (localdict['categories'].dict.get('DEV_SALARIAL',0) + localdict['categories'].dict.get('DEV_NO_SALARIAL',0) + localdict['categories'].dict.get('PRESTACIONES_SOCIALES',0) + localdict['categories'].dict.get('DEDUCCIONES',0)) - localdict['values_leaves_law']
                                else:
                                    value_tmp_neto = 1

                                if (inherit_contrato_dev != 0 or inherit_contrato_ded != 0 or inherit_contrato_ded_bases != 0) and self.settle_payroll_concepts == True and loan_id:
                                    if concept.loan_id.final_settlement_version == True:
                                        loan_pending_amount = 0
                                        for line_loan in concept.loan_id.prestamo_lines:
                                            if not line_loan.paid:
                                                loan_pending_amount += line_loan.amount
                                        dif_loan_pending_amount = 0 if value_tmp_neto+abs(amount) >= loan_pending_amount else loan_pending_amount-(value_tmp_neto+abs(amount))
                                        loan_pending_amount = loan_pending_amount if value_tmp_neto+abs(amount) >= loan_pending_amount else value_tmp_neto+abs(amount)
                                        previous_amount = (rule.code in localdict and localdict[rule.code] or 0.0) - amount
                                        previous_amount_act = amount
                                        amount, qty, rate = abs(loan_pending_amount) * -1, 1.0, 100
                                        tot_rule_original = (amount * qty * rate / 100.0)
                                        part_decimal, part_value = math.modf(tot_rule_original)
                                        tot_rule = round(amount * qty * rate / 100.0, 0)
                                        if part_decimal >= 0.49 and tot_rule == part_value:
                                            tot_rule = (part_value + 1) + previous_amount
                                        else:
                                            tot_rule = tot_rule + previous_amount
                                        localdict[rule.code] = tot_rule
                                        localdict = _sum_salary_rule_category(localdict, rule.category_id,tot_rule - previous_amount_act)
                                        localdict = _sum_salary_rule(localdict, rule, tot_rule)
                                        if dif_loan_pending_amount > 0:
                                            result_not[result_item] = {
                                                'sequence': rule.sequence,
                                                'code': rule.code,
                                                'name': rule.name,
                                                'note': rule.note,
                                                'salary_rule_id': rule.id,
                                                'version_id': version.id,
                                                'employee_id': employee.id,
                                                'entity_id': entity_id,
                                                'loan_id': loan_id,
                                                'amount': dif_loan_pending_amount,
                                                'quantity': qty,
                                                'rate': rate,
                                                'slip_id': self.id,
                                            }

                                if value_tmp_neto >= 0:
                                    result[result_item] = {
                                    'sequence': rule.sequence,
                                    'code': rule.code,
                                    'name': rule.name,
                                    'note': rule.note,
                                    'salary_rule_id': rule.id,
                                    'version_id': version.id,
                                    'employee_id': employee.id,
                                    'entity_id': entity_id,
                                    'loan_id': loan_id,
                                    'amount': amount,
                                    'quantity': qty,
                                    'rate': rate,
                                    'total': self._get_payslip_line_total(amount, qty, rate, rule),
                                    'slip_id': self.id,
                                    }
                                else:
                                    localdict = _sum_salary_rule_category(localdict, rule.category_id, (tot_rule - previous_amount)*-1)
                                    localdict = _sum_salary_rule(localdict, rule, (tot_rule*-1))
                                    result_not[result_item] = {
                                    'sequence': rule.sequence,
                                    'code': rule.code,
                                    'name': rule.name,
                                    'note': rule.note,
                                    'salary_rule_id': rule.id,
                                    'version_id': version.id,
                                    'employee_id': employee.id,
                                    'entity_id': entity_id,
                                    'loan_id': loan_id,
                                    'amount': amount,
                                    'quantity': qty,
                                    'rate': rate,
                                    'total': self._get_payslip_line_total(amount, qty, rate, rule),
                                    'slip_id': self.id,
                                    }
                else:
                    amount, qty, rate = rule._compute_rule(localdict)
                    #Validar si no tiene dias trabajados, si no tiene revisar las ausencias y sus caracteristicas para calcular la deducción
                    if rule.dev_or_ded == 'deduccion' and rule.type_concept != 'ley' and (worked_days_entry + leaves_days_all) == 0 and inherit_prima==0:
                        amount, qty, rate = 0,1.0,100

                    #LIQUIDACION DE CONTRATO SOLO DEV OR DED DEPENDIENTO SU ORIGEN
                    if str(rule.amount_python_compute).find('get_overtime') != -1: #Verficiar si la regla utiliza la tabla hr.overtime por ende es un concepto de novedad del menu horas extras
                        if (inherit_contrato_dev != 0 or inherit_contrato_ded != 0 or inherit_contrato_ded_bases != 0) and self.novelties_payroll_concepts == False and not rule.code in ['TOTALDEV','TOTALDED','NET']:
                            amount, qty, rate = 0,1.0,100
                        else:
                            amount = round(amount, 2)
                    else:
                        if (inherit_contrato_dev != 0 or inherit_contrato_ded != 0 or inherit_contrato_ded_bases != 0) and self.settle_payroll_concepts == False and rule.type_concept != 'ley' and not rule.code in ['TOTALDEV','TOTALDED','NET']:
                            amount, qty, rate = 0,1.0,100

                    # PRIMA SOLAMENTE DEDUCCIONES QUE ESTEN CONFIGURADAS
                    # VACACIONES SOLAMENTE DEDUCCIONES
                    if (inherit_contrato_dev != 0 and rule.dev_or_ded != 'devengo') \
                            or (inherit_contrato_ded+inherit_contrato_ded_bases != 0 and rule.dev_or_ded != 'deduccion' and not rule.code in ['TOTALDEV','NET']) \
                            or (inherit_contrato_ded != 0 and rule.dev_or_ded == 'deduccion' and not rule.code in ['TOTALDEV','NET'] and (rule.base_prima or rule.base_cesantias or rule.base_vacaciones_dinero or rule.base_intereses_cesantias)) \
                            or (inherit_contrato_ded_bases != 0 and rule.dev_or_ded == 'deduccion' and not rule.code in ['TOTALDEV', 'NET'] and not(rule.base_prima or rule.base_cesantias or rule.base_vacaciones_dinero or rule.base_intereses_cesantias)) \
                            or (inherit_prima != 0 and rule.dev_or_ded != 'deduccion' and not rule.code in ['TOTALDEV','NET']) \
                            or (inherit_prima != 0 and rule.dev_or_ded == 'deduccion' and rule.deduction_applies_bonus == False) \
                            or (inherit_vacation != 0 and rule.dev_or_ded != 'deduccion' and not rule.code in ['TOTALDEV','NET']):
                        amount, qty, rate = 0,1.0,100

                    amount = round(amount,0) if round_payroll == False else amount #Se redondean los decimales de todas las reglas
                    if amount != 0:
                        #check if there is already a rule computed with that code
                        previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                        #set/overwrite the amount computed for this rule in the localdict
                        tot_rule_original = (amount * qty * rate / 100.0)
                        part_decimal, part_value = math.modf(tot_rule_original)
                        tot_rule = amount * qty * rate / 100.0
                        if part_decimal >= 0.49 and math.modf(tot_rule)[1] == part_value:
                            tot_rule = (part_value + 1) + previous_amount
                        else:
                            tot_rule = tot_rule + previous_amount
                        tot_rule = round(tot_rule, 0)
                    else:
                        tot_rule,previous_amount = 0, 0
                    localdict[rule.code] = tot_rule
                    rules_dict[rule.code] = rule
                    # sum the amount for its salary category
                    localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
                    localdict = _sum_salary_rule(localdict, rule, tot_rule)
                    #Guardar valores de ausencias dependiendo parametrización
                    if rule.is_leave:
                        amount_leave = (float(qty) * amount * rate / 100) if rule.deduct_deductions == 'all' else 0
                        localdict['values_leaves_all'] = localdict['values_leaves_all'] + amount_leave
                        amount_leave_law = (float(qty) * amount * rate / 100) if rule.deduct_deductions == 'law' else 0
                        localdict['values_leaves_law'] = localdict['values_leaves_law'] + amount_leave_law

                    # create/overwrite the rule in the temporary results
                    if amount != 0 or rule.code == 'NET':
                        if rule.dev_or_ded == 'deduccion' and inherit_prima == 0:
                            if rule.type_concept == 'ley':
                                value_tmp_neto = localdict['categories'].dict.get('DEV_SALARIAL',0) + localdict['categories'].dict.get('DEV_NO_SALARIAL',0) + localdict['categories'].dict.get('PRESTACIONES_SOCIALES',0) + localdict['categories'].dict.get('DEDUCCIONES',0)
                            else:
                                value_tmp_neto = (localdict['categories'].dict.get('DEV_SALARIAL',0) + localdict['categories'].dict.get('DEV_NO_SALARIAL',0) + localdict['categories'].dict.get('PRESTACIONES_SOCIALES',0) + localdict['categories'].dict.get('DEDUCCIONES',0)) - localdict['values_leaves_law']
                        else:
                            value_tmp_neto = 1
                        if value_tmp_neto >= 0 or rule.code == 'NET' or rule.type_concept == 'ley':
                            result[rule.code] = {
                                'sequence': rule.sequence,
                                'code': rule.code,
                                'name': rule.name,
                                'note': rule.note,
                                'salary_rule_id': rule.id,
                                'version_id': version.id,
                                'employee_id': employee.id,
                                'entity_id': entity_id,
                                'loan_id': loan_id,
                                'amount': amount, #Se redondean los decimales de todas las reglas
                                'quantity': qty,
                                'rate': rate,
                                'total': self._get_payslip_line_total(amount, qty, rate, rule),
                                'slip_id': self.id,
                            }
                        else:
                            localdict = _sum_salary_rule_category(localdict, rule.category_id, (tot_rule - previous_amount)*-1)
                            localdict = _sum_salary_rule(localdict, rule, (tot_rule)*-1)
                            result_not[rule.code] = {
                                'sequence': rule.sequence,
                                'code': rule.code,
                                'name': rule.name,
                                'note': rule.note,
                                'salary_rule_id': rule.id,
                                'version_id': version.id,
                                'employee_id': employee.id,
                                'entity_id': entity_id,
                                'loan_id': loan_id,
                                'amount': amount, #Se redondean los decimales de todas las reglas
                                'quantity': qty,
                                'rate': rate,
                                'total': self._get_payslip_line_total(amount, qty, rate, rule),
                                'slip_id': self.id,
                            }

        #Cargar detalle retención en la fuente si tuvo
        obj_rtefte = self.env['hr.employee.rtefte'].search([('employee_id', '=', employee.id),('type_tax', '=', self.env['hr.type.tax.retention'].search([('code', '=', version.retention_procedure)],limit=1).id),
                                                            ('year', '=', self.date_from.year),('month', '=', self.date_from.month)])
        if obj_rtefte:
            for rtefte in obj_rtefte:
                self.rtefte_id = rtefte.id
            # Crear histórico de rtefte la liquidación actual
            self._create_rtefte_history(employee)

        # Agregar reglas no aplicadas
        not_lines = [(0, 0, not_line) for not_line in result_not.values()]
        self.not_line_ids = not_lines
        #Reglas que dan como valor final 0 deben ser eliminadas
        lst_rules_delete = []
        for key in localdict['rules_computed'].dict:
            if localdict['rules_computed'].dict[key] == 0:
                for key_result in result:
                    if key == result[key_result]['code']:
                        lst_rules_delete.append(key_result)
        for rule in lst_rules_delete:
            result.pop(rule)
        #Retornar resultado final de la liquidación de nómina
        if inherit_vacation != 0 or inherit_prima != 0:
            return result
        elif inherit_contrato_dev != 0 or inherit_contrato_ded != 0 or inherit_contrato_ded_bases != 0:
            return localdict,result
        else:
            result_finally = {**result, **result_vac}
            return result_finally.values()

    def action_payslip_cancel(self):
        posted_moves = self.mapped('move_id').filtered(lambda m: m.state == 'posted')
        if posted_moves:
            raise ValidationError(_('No puedes cancelar un movimiento contable de nómina publicado.'))
        return super(Hr_payslip, self).action_payslip_cancel()

    def action_payslip_done(self):
        #res = super(Hr_payslip, self).action_payslip_done()
        if any(slip.state == 'cancel' for slip in self):
            raise ValidationError(_("You can't validate a cancelled payslip."))
        self.write({'state' : 'validated'})
        self.mapped('payslip_run_id').action_confirm()
        pay_vacations_in_payroll = bool(self.env['ir.config_parameter'].sudo().get_param(
            'zue_hr_payroll.pay_vacations_in_payroll')) or False

        ''' Se comenta la generación del PDF al momento del cierre de nómina
        if self.env.context.get('payslip_generate_pdf'):
            for payslip in self:
                if not payslip.struct_id or not payslip.struct_id.report_id:
                    report = self.env.ref('hr_payroll.action_report_payslip', False)
                else:
                    report = payslip.struct_id.report_id
                pdf_content, content_type = report.render_qweb_pdf(payslip.id)
                if payslip.struct_id.report_id.print_report_name:
                    pdf_name = safe_eval(payslip.struct_id.report_id.print_report_name, {'object': payslip})
                else:
                    pdf_name = _("Payslip")
                self.env['ir.attachment'].create({
                    'name': pdf_name,
                    'type': 'binary',
                    'datas': base64.encodebytes(pdf_content),
                    'res_model': payslip._name,
                    'res_id': payslip.id
                })
        '''

        #Contabilización
        self._action_create_account_move()
        for record in self:
            if record.move_id:
                if record.move_id.date > fields.Date.today():
                    record.move_id.write({'auto_post': 'at_date'})
        #Actualizar en la tabla de prestamos la cuota pagada
        for record in self:
            obj_payslip_line = self.env['hr.payslip.line'].search([('slip_id', '=', record.id),('loan_id', '!=', False)])
            for payslip_line in obj_payslip_line:
                if record.struct_id.process == 'contrato' and payslip_line.loan_id.final_settlement_version == True:
                    data = {
                        'prestamo_id':payslip_line.loan_id.id,
                        'employee_id':payslip_line.employee_id.id,
                        'date': record.date_liquidacion,
                        'amount':abs(payslip_line.total),
                        'paid': True,
                        'payslip_id': record.id
                    }
                    self.env['hr.loans.line'].create(data)
                else:
                    obj_loan_line = self.env['hr.loans.line'].search([('employee_id', '=', payslip_line.employee_id.id),
                                                                      ('prestamo_id', '=', payslip_line.loan_id.id),
                                                                      ('date', '>=', record.date_from),
                                                                      ('date', '<=', record.date_to)])
                    data = {
                        'paid':True,
                        'payslip_id': record.id
                    }
                    obj_loan_line.write(data)

                obj_loan = self.env['hr.loans'].search([('employee_id', '=', payslip_line.employee_id.id),('id', '=', payslip_line.loan_id.id)])
                if obj_loan.balance_amount <= 0:
                    self.env['hr.contract.concepts'].search([('loan_id', '=', payslip_line.loan_id.id)]).write({'state':'cancel'})

            if record.struct_id.process == 'vacaciones' or (pay_vacations_in_payroll == True and record.struct_id.process != 'contrato'):
                history_vacation = []
                for line in sorted(record.line_ids.filtered(lambda filter: filter.initial_accrual_date), key=lambda x: x.initial_accrual_date):
                    if line.code == 'VACDISFRUTADAS':
                        info_vacation = {
                            'employee_id': record.employee_id.id,
                            'version_id': record.version_id.id,
                            'initial_accrual_date': line.initial_accrual_date,
                            'final_accrual_date': line.final_accrual_date,
                            'departure_date': record.date_from if not line.vacation_departure_date else line.vacation_departure_date,
                            'return_date': record.date_to if not line.vacation_return_date else line.vacation_return_date,
                            'business_units': line.business_units + line.business_31_units,
                            'value_business_days': line.business_units * line.amount,
                            'holiday_units': line.holiday_units + line.holiday_31_units,
                            'holiday_value': line.holiday_units * line.amount,
                            'base_value': line.amount_base,
                            'total': (line.business_units * line.amount)+(line.holiday_units * line.amount),
                            'payslip': record.id,
                            'leave_id': False if not line.vacation_leave_id else line.vacation_leave_id.id
                        }
                    if line.code == 'VACREMUNERADAS':
                        info_vacation = {
                            'employee_id': record.employee_id.id,
                            'version_id': record.version_id.id,
                            'initial_accrual_date': line.initial_accrual_date,
                            'final_accrual_date': line.final_accrual_date,
                            'departure_date': record.date_from,
                            'return_date': record.date_to,
                            'units_of_money': line.quantity,
                            'money_value': line.total,
                            'base_value_money': line.amount_base,
                            'total': line.total,
                            'payslip': record.id
                        }

                    if pay_vacations_in_payroll == True:
                        #Si el historico ya existe no vuelva a crearlo
                        obj_history_vacation_exists = self.env['hr.vacation'].search([('employee_id','=',record.employee_id.id),
                                                                                      ('version_id','=',record.version_id.id),
                                                                                      ('initial_accrual_date','=',line.initial_accrual_date),
                                                                                      ('final_accrual_date','=',line.final_accrual_date),
                                                                                      ('leave_id','=',line.vacation_leave_id.id)])
                        if len(obj_history_vacation_exists) == 0:
                            history_vacation.append(info_vacation)
                    else:
                        history_vacation.append(info_vacation)

                if history_vacation:
                    for history in history_vacation:
                        self.env['hr.vacation'].create(history)

            if record.struct_id.process == 'cesantias' or record.struct_id.process == 'intereses_cesantias':
                his_cesantias = {}
                his_intcesantias = {}

                for line in record.line_ids:
                    #Historico cesantias
                    if line.code == 'CESANTIAS' and line.is_history_reverse == False:
                        his_cesantias = {
                            'employee_id': record.employee_id.id,
                            'version_id': record.version_id.id,
                            'type_history': 'cesantias',
                            'initial_accrual_date': record.date_from,
                            'final_accrual_date': record.date_to,
                            'settlement_date': record.date_to,
                            'time': line.quantity,
                            'base_value':line.amount_base,
                            'severance_value': line.total,
                            'payslip': record.id
                        }

                    if line.code == 'INTCESANTIAS' and line.is_history_reverse == False:
                        his_intcesantias = {
                            'employee_id': record.employee_id.id,
                            'version_id': record.version_id.id,
                            'type_history': 'intcesantias',
                            'initial_accrual_date': record.date_from,
                            'final_accrual_date': record.date_to,
                            'settlement_date': record.date_to,
                            'time': line.quantity,
                            'base_value': line.amount_base,
                            'severance_interest_value': line.total,
                            'payslip': record.id
                        }

                info_cesantias = {**his_cesantias,**his_intcesantias}
                if info_cesantias:
                    self.env['hr.history.cesantias'].create(info_cesantias)

            if record.struct_id.process == 'prima':
                for line in record.line_ids:
                    if line.code == 'PRIMA':
                        his_prima = {
                            'employee_id': record.employee_id.id,
                            'version_id': record.version_id.id,
                            'initial_accrual_date': record.date_from,
                            'final_accrual_date': record.date_to,
                            'settlement_date': record.date_to,
                            'time': line.quantity,
                            'base_value':line.amount_base,
                            'bonus_value': line.total,
                            'payslip': record.id
                        }
                        self.env['hr.history.prima'].create(his_prima)

            if record.struct_id.process == 'contrato':
                his_cesantias = {}
                his_intcesantias = {}

                for line in record.line_ids:
                    #Historico vacaciones
                    if line.code == 'VACCONTRATO':
                        info_vacation = {
                            'employee_id': record.employee_id.id,
                            'version_id': record.version_id.id,
                            'initial_accrual_date': line.initial_accrual_date,
                            'final_accrual_date': line.final_accrual_date,
                            'departure_date': record.date_liquidacion,
                            'return_date': record.date_liquidacion,
                            'units_of_money': round((line.quantity*15)/360),
                            'money_value': line.total,
                            'base_value_money': line.amount_base,
                            'total': line.total,
                            'payslip': record.id
                        }
                        self.env['hr.vacation'].create(info_vacation)

                    #Historico prima
                    if line.code == 'PRIMA':
                        his_prima = {
                            'employee_id': record.employee_id.id,
                            'version_id': record.version_id.id,
                            'initial_accrual_date': record.date_prima,
                            'final_accrual_date': record.date_liquidacion,
                            'settlement_date': record.date_liquidacion,
                            'time': line.quantity,
                            'base_value':line.amount_base,
                            'bonus_value': line.total,
                            'payslip': record.id
                        }
                        self.env['hr.history.prima'].create(his_prima)

                    #Historico cesantias
                    if line.code == 'CESANTIAS' and line.is_history_reverse == False:
                        his_cesantias = {
                            'employee_id': record.employee_id.id,
                            'version_id': record.version_id.id,
                            'initial_accrual_date': record.date_cesantias,
                            'final_accrual_date': record.date_liquidacion,
                            'settlement_date': record.date_liquidacion,
                            'time': line.quantity,
                            'base_value':line.amount_base,
                            'severance_value': line.total,
                            'payslip': record.id
                        }

                    if line.code == 'INTCESANTIAS' and line.is_history_reverse == False:
                        his_intcesantias = {
                            'severance_interest_value': line.total,
                        }

                info_cesantias = {**his_cesantias,**his_intcesantias}
                if info_cesantias:
                    self.env['hr.history.cesantias'].create(info_cesantias)

                obj_contrato = self.env['hr.version'].search([('id','=',record.version_id.id)])
                values_update = {'retirement_date':record.date_liquidacion}
                obj_contrato.write(values_update)
        #return res

            #Validar Historico de cesantias/int.cesantias a tener encuenta
            #Una vez confirmado va a la liquidacion asociado y deja en 0 el valor de CESANTIAS y INT CESANTIAS
            #Para evitar la duplicidad de los valores ya que fueron heredados a esta liquidación
            for payments in self.severance_payments_reverse:
                if payments.payslip:
                    value_cesantias = 0
                    value_intcesantias = 0
                    for line in payments.payslip.line_ids:
                        if line.code == 'CESANTIAS':
                            value_cesantias = line.total
                            line.write({'amount':0})
                        if line.code == 'INTCESANTIAS':
                            value_intcesantias = line.total
                            line.write({'amount':0})
                        if line.code == 'NET':
                            amount = line.total - (value_cesantias+value_intcesantias)
                            line.write({'amount':amount})

                    if payments.payslip.observation:
                        payments.payslip.write({'observation':payments.payslip.observation+ '\n El valor se trasladó a la liquidación '+self.name+' de '+self.struct_id.name })
                    else:
                        payments.payslip.write({'observation': 'El valor se trasladó a la liquidación ' + self.name + ' de ' + self.struct_id.name})

class HrPayrollEditPayslipLinesWizard(models.TransientModel):
    _inherit = 'hr.payroll.edit.payslip.lines.wizard'

    def recompute_following_lines(self, line_id):
        self.ensure_one()
        wizard_line = self.env['hr.payroll.edit.payslip.line'].browse(line_id)
        reload_wizard = {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payroll.edit.payslip.lines.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
        return reload_wizard

        # SE COMENTA EL ESTÁNDAR DE NÓMINA ZUE EN ODOO
        # if not wizard_line.salary_rule_id:

        # localdict = self.payslip_id._get_localdict()
        # result_rules_dict = localdict['result_rules']
        # remove_lines = False
        # lines_to_remove = []
        # blacklisted_rule_ids = []
        # for line in sorted(self.line_ids, key=lambda x: x.sequence):
        #     if remove_lines and line.code in self.payslip_id.line_ids.mapped('code'):
        #         lines_to_remove.append((2, line.id, 0))
        #     else:
        #         if line == wizard_line:
        #             line._compute_total()
        #             remove_lines = True
        #         blacklisted_rule_ids.append(line.salary_rule_id.id)
        #         localdict[line.code] = line.total
        #         result_rules_dict[line.code] = {'total': line.total, 'amount': line.amount, 'quantity': line.quantity, 'rate': line.rate, 'ytd': line.ytd}
        #         localdict = line.salary_rule_id.category_id._sum_salary_rule_category(localdict, line.total)
        #
        # payslip = self.payslip_id.with_context(force_payslip_localdict=localdict, prevent_payslip_computation_line_ids=blacklisted_rule_ids)
        #
        # lines_to_payslip = []
        # for line in payslip._get_payslip_lines():
        #     del line['note']
        #     del line['entity_id']
        #     del line['loan_id']
        #     lines_to_payslip.append(line)
        # self.line_ids = lines_to_remove + [(0, 0, line) for line in lines_to_payslip]
        # return reload_wizard
