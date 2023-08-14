# -*- coding: utf-8 -*-
from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
from .browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips
from odoo.tools import float_compare, float_is_zero
from collections import defaultdict
from datetime import datetime, timedelta, date, time
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
import math
import pytz
import odoo
import threading
import logging
import time

_logger = logging.getLogger(__name__)
#---------------------------LIQUIDACIÓN DE NÓMINA-------------------------------#

class HrPayslipRun(models.Model):
    _name = 'hr.payslip.run'
    _inherit = ['hr.payslip.run','mail.thread','mail.activity.mixin']

    time_process = fields.Char(string='Tiempo ejecución')
    observations = fields.Text('Observaciones')
    definitive_plan = fields.Boolean(string='Plano definitivo generado')

    def assign_status_verify(self):
        for record in self:
            if len(record.slip_ids) > 0:
                record.write({'state': 'verify'})
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
            self.action_close()

    def restart_payroll_batch(self):
        self.mapped('slip_ids').action_payslip_cancel()
        self.mapped('slip_ids').unlink()
        return self.write({'state': 'draft','observations':False,'time_process':False})

    def restart_payroll_account_batch(self):
        for payslip in self.slip_ids:
            #Eliminar contabilización y el calculo
            payslip.mapped('move_id').unlink()
            #Eliminar historicos
            self.env['hr.vacation'].search([('payslip', '=', payslip.id)]).unlink()
            self.env['hr.history.prima'].search([('payslip', '=', payslip.id)]).unlink()
            self.env['hr.history.cesantias'].search([('payslip', '=', payslip.id)]).unlink()
            #Reversar Liquidación
            payslip.write({'state': 'verify'})
        return self.write({'state': 'verify'})

    def restart_full_payroll_batch(self):
        for payslip in self.slip_ids:
            #Eliminar contabilización
            payslip.mapped('move_id').unlink() 
            #Eliminar historicos            
            self.env['hr.vacation'].search([('payslip', '=', payslip.id)]).unlink()
            self.env['hr.history.prima'].search([('payslip', '=', payslip.id)]).unlink()
            self.env['hr.history.cesantias'].search([('payslip', '=', payslip.id)]).unlink()
            #Reversar Liquidación
            payslip.write({'state':'verify'})
            payslip.action_payslip_cancel()
            payslip.unlink()
        
        # self.mapped('slip_ids').action_payslip_cancel()
        # self.mapped('slip_ids').unlink()
        return self.write({'state': 'draft'})

class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'	

    @api.model
    def _get_default_structure(self):
        return self.env['hr.payroll.structure'].search([('process','=','nomina')],limit=1)

    structure_id = fields.Many2one('hr.payroll.structure', string='Salary Structure', default=_get_default_structure)
    struct_process = fields.Selection(related='structure_id.process', string='Proceso', store=True)
    method_schedule_pay  = fields.Selection([('bi-weekly', 'Quincenal'),
                                          ('monthly', 'Mensual'),
                                          ('other', 'Ambos')], 'Frecuencia de Pago', default='other')
    analytic_account_ids = fields.Many2many('account.analytic.account', string='Cuentas analíticas')
    z_branch_ids = fields.Many2many('zue.res.branch', string='Sucursales')
    state_contract = fields.Selection([('open','En Proceso'),('finished','Finalizado Por Liquidar')], string='Estado Contrato', default='open')
    settle_payroll_concepts = fields.Boolean('Liquida conceptos de nómina', default=True)
    novelties_payroll_concepts = fields.Boolean('Liquida conceptos de novedades', default=True)
    prima_run_reverse_id = fields.Many2one('hr.payslip.run', string='Lote de prima a ajustar')

    def _get_available_contracts_domain(self):
        domain = [('contract_id.state', '=', self.state_contract or 'open'), ('company_id', '=', self.env.company.id)]
        if self.method_schedule_pay and self.method_schedule_pay != 'other':
            domain.append(('contract_id.method_schedule_pay','=',self.method_schedule_pay))
        if len(self.analytic_account_ids) > 0:
            domain.append(('contract_id.analytic_account_id', 'in', self.analytic_account_ids.ids))
        if len(self.z_branch_ids) > 0:
            domain.append(('branch_id', 'in', self.z_branch_ids.ids))
        if self.prima_run_reverse_id:
            employee_ids = self.env['hr.payslip'].search([('payslip_run_id', '=', self.prima_run_reverse_id.id)]).employee_id.ids
            domain.append(('id','in',employee_ids))
        return domain

    @api.depends('structure_id','department_id','method_schedule_pay','analytic_account_ids','z_branch_ids','state_contract','prima_run_reverse_id')
    def _compute_employee_ids(self):
        for wizard in self:
            domain = wizard._get_available_contracts_domain()
            if wizard.department_id:
                domain.append(('department_id', 'child_of', self.department_id.id))
            wizard.employee_ids = self.env['hr.employee'].search(domain)

    def _check_undefined_slots(self, work_entries, payslip_run):
        """
        Check if a time slot in the contract's calendar is not covered by a work entry
        """
        calendar_is_not_covered = self.env['hr.contract']
        work_entries_by_contract = defaultdict(lambda: self.env['hr.work.entry'])
        for work_entry in work_entries:
            work_entries_by_contract[work_entry.contract_id] |= work_entry

        for contract, work_entries in work_entries_by_contract.items():
            calendar_start = pytz.utc.localize(datetime.combine(max(contract.date_start, payslip_run.date_start), datetime.min.time()))
            calendar_end = pytz.utc.localize(datetime.combine(min(contract.date_end or date.max, payslip_run.date_end), datetime.max.time()))
            outside = contract.resource_calendar_id._attendance_intervals_batch(calendar_start, calendar_end)[False] - work_entries._to_intervals()
            if outside:
                calendar_is_not_covered |= contract
                #calendar_is_not_covered.append(contract.id)
                #raise UserError(_("Some part of %s's calendar is not covered by any work entry. Please complete the schedule.") % contract.employee_id.name)

        return calendar_is_not_covered

    def compute_sheet_thread(self,item,obj_structure_id,obj_payslip_run,obj_contracts):
        time.sleep(3)
        with api.Environment.manage():
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            aditional_info = ''

            _logger.info(f'(START) HILO/REGISTRO {str(item)} - Ejecución liquidación de nómina con {len(obj_contracts.ids)} contratos.')

            payslips = self.env['hr.payslip'].with_env(self.env(cr=new_cr))
            Payslip = self.env['hr.payslip'].with_env(self.env(cr=new_cr))
            default_values = Payslip.default_get(Payslip.fields_get())

            contracts = self.env['hr.contract'].search([('id', 'in', obj_contracts.ids)]).with_env(self.env(cr=new_cr))
            structure_id = self.env['hr.payroll.structure'].search([('id', 'in', obj_structure_id.ids)]).with_env(self.env(cr=new_cr))
            payslip_run = self.env['hr.payslip.run'].search([('id', 'in', obj_payslip_run.ids)]).with_env(self.env(cr=new_cr))

            try:
                for contract in contracts:
                    if structure_id.name:
                        aditional_info = 'Contrato: ' + contract.name + '. Estructura: ' + structure_id.name
                    else:
                        aditional_info = 'Contrato: ' + contract.name + '. Estructura: ' + contract.structure_type_id.default_struct_id.name

                    log_msg = 'Empleado actual: ' + str(contract.employee_id.id) + ': ' + \
                              contract.employee_id.name + '. ' + aditional_info

                    values = dict(default_values, **{
                        'employee_id': contract.employee_id.id,
                        'credit_note': payslip_run.credit_note,
                        'payslip_run_id': payslip_run.id,
                        'date_from': payslip_run.date_start,
                        'date_to': payslip_run.date_end,
                        'contract_id': contract.id,
                        'struct_id': structure_id.id or contract.structure_type_id.default_struct_id.id,
                        'prima_run_reverse_id': self.prima_run_reverse_id,
                    })
                    if structure_id.process == 'prima' and self.prima_run_reverse_id:
                        prima_payslip_reverse_obj = self.env['hr.payslip'].search([('payslip_run_id','=',self.prima_run_reverse_id.id),
                                                       ('employee_id','=',contract.employee_id.id)],limit=1).with_env(self.env(cr=new_cr))
                        if len(prima_payslip_reverse_obj) == 1:
                            values = dict(values, **{
                                'prima_payslip_reverse_id': prima_payslip_reverse_obj.id,
                            })
                    if structure_id.process == 'contrato':
                        values = dict(values, **{
                            'settle_payroll_concepts': self.settle_payroll_concepts,
                            'novelties_payroll_concepts': self.novelties_payroll_concepts,
                        })

                    payslip = self.env['hr.payslip'].new(values).with_env(self.env(cr=new_cr))
                    payslip._onchange_employee()
                    if structure_id.process == 'contrato':
                        payslip.load_dates_liq_contrato()
                    values = payslip._convert_to_write(payslip._cache)
                    payslips += Payslip.create(values)
                payslips.compute_sheet()
                _logger.info(f'(END) HILO/REGISTRO {str(item)} - Ejecución liquidación de nómina con {len(obj_contracts.ids)} contratos.')
            except Exception as e:
                msg = 'ERROR: ' + str(e.args[0])
                if payslip_run.observations:
                    if log_msg not in payslip_run.observations:
                        payslip_run.write({'observations': log_msg + '\n' + msg + '\n' + payslip_run.observations})
                else:
                    payslip_run.write({'observations':log_msg + '\n' + msg})
                _logger.info(f'(END/ERROR) HILO/REGISTRO {str(item)} - Ejecución liquidación de nómina con {len(obj_contracts.ids)} contratos.')
            new_cr.commit()

    def compute_sheet(self):
        self.ensure_one()
        if not self.env.context.get('active_id'):
            #from_date = fields.Date.to_date(self.env.context.get('default_date_start'))
            #end_date = fields.Date.to_date(self.env.context.get('default_date_end'))
            #payslip_run = self.env['hr.payslip.run'].create({
            #    'name': from_date.strftime('%B %Y'),
            #    'date_start': from_date,
            #    'date_end': end_date,
            #})
            _logger.info(f'PROCESAMIENTOS DE NÓMINAS / LOTES - ERROR - SE INTENTO CREAR UN LOTE DE FORMA AUTOMATICA.')
            return {'type': 'ir.actions.act_window_close'}
        else:
            payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))

        obj_payslip_exists = self.env['hr.payslip'].search([('payslip_run_id','in',payslip_run.ids)])
        if len(obj_payslip_exists) > 0:
            _logger.info(f'PROCESAMIENTOS DE NÓMINAS / LOTES - ERROR - SE INTENTO DUPLICAR LOS REGISTROS.')
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'hr.payslip.run',
                'views': [[False, 'form']],
                'res_id': payslip_run.id,
            }

        employees = self.with_context(active_test=False).employee_ids
        if not employees:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))

        if self.structure_id.use_worked_day_lines:
            work_entries_conflict = self.env['hr.work.entry'].search([
                ('date_start', '<=', payslip_run.date_end),
                ('date_stop', '>=', payslip_run.date_start),
                ('employee_id', 'in', employees.ids),
                ('state', '=', 'conflict'),
            ])

            if len(work_entries_conflict) > 0:
                raise ValidationError(_("Existen entradas de trabajo con conflicto, por favor verificar."))

            work_entries = self.env['hr.work.entry'].search([
                ('date_start', '<=', payslip_run.date_end),
                ('date_stop', '>=', payslip_run.date_start),
                ('employee_id', 'in', employees.ids),
            ])
            calendar_is_not_covered = self._check_undefined_slots(work_entries, payslip_run)

            if calendar_is_not_covered:
                date_start = fields.Datetime.to_datetime(payslip_run.date_start)
                date_stop = datetime.combine(fields.Datetime.to_datetime(payslip_run.date_end),datetime.max.time())
                self.env['hr.work.entry'].search([('date_start', '>=', date_start),
                                             ('date_stop', '<=', date_stop),
                                             ('contract_id', 'in', calendar_is_not_covered.ids)]).unlink()

                vals_list = calendar_is_not_covered._get_work_entries_values(date_start, date_stop)
                self.env['hr.work.entry'].create(vals_list)

                work_entries = self.env['hr.work.entry'].search([
                    ('date_start', '<=', payslip_run.date_end),
                    ('date_stop', '>=', payslip_run.date_start),
                    ('employee_id', 'in', employees.ids),
                ])

            validated = work_entries.action_validate()
            if not validated:
                observations = 'Algunas entradas de trabajo no se pudieron validar.'
                payslip_run.observations = observations
                # raise UserError(_("Some work entries could not be validated."))

        if self.structure_id.process == 'contrato':
            contracts = employees._get_contracts(payslip_run.date_start, payslip_run.date_end,
                                                 states=['open', 'finished'])
        else:
            contracts = employees._get_contracts(payslip_run.date_start, payslip_run.date_end,
                                                 states=['open'])  # , 'close'
        contracts._generate_work_entries(payslip_run.date_start, payslip_run.date_end)

        if len(contracts) == 0:
            raise UserError(_("No se encontraron contratos activos para procesar, por favor verificar."))
        
        #--------------------------MANEJO POR HILOS PARA LA LIQUIDACIÓN EN LOTE--------------------------------

        # Se dividen los contratos en 3 lotes para ser ejecutados en 2 hilos
        div = math.ceil(len(contracts) / 3)
        contracts_array_def, i, j = [], 0, div
        while i <= len(contracts):
            contracts_array_def.append(contracts[i:j])
            i = j
            j += div

        # ----------------------------Recorrer empleados por multihilos
        threads = []
        date_start_process = datetime.now()
        item = 1
        for i_contracts in contracts_array_def:
            if len(i_contracts) > 0:
                t = threading.Thread(target=self.compute_sheet_thread, args=(item,self.structure_id,payslip_run,i_contracts,))
                threads.append(t)
                t.start()
            item += 1

        for thread in threads:
            try:
                thread.join()
            except Exception as e:
                msg = 'ERROR: ' + str(e.args[0])
                if payslip_run.observations:
                    payslip_run.write({'observations': payslip_run.observations + '\n' + msg})
                else:
                    payslip_run.write({'observations': msg})

        date_finally_process = datetime.now()
        time_process = date_finally_process - date_start_process
        time_process = time_process.seconds / 60
        str_time_process = "El proceso se demoro {:.2f} minutos.".format(time_process)

        #Finalización del proceso
        payslip_run.time_process = str_time_process
        payslip_run.state = 'verify'

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip.run',
            'views': [[False, 'form']],
            'res_id': payslip_run.id,
        }

    def clean_employees(self):   
        self.employee_ids = [(5,0,0)]
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.payslip.employees',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

class Hr_payslip_line(models.Model):
    _inherit = 'hr.payslip.line'

    entity_id = fields.Many2one('hr.employee.entities', string="Entidad")
    loan_id = fields.Many2one('hr.loans', 'Prestamo', readonly=True)
    days_unpaid_absences = fields.Integer(string='Días de ausencias no pagadas',readonly=True)
    amount_base = fields.Float('Base')
    is_history_reverse = fields.Boolean(string='Es historico para reversar')
    #Campos informe detalle
    branch_employee_id = fields.Many2one(related='employee_id.branch_id', string='Sucursal', store=True)
    state_slip = fields.Selection(related='slip_id.state', string='Estado Nómina', store=True)
    analytic_account_slip_id = fields.Many2one(related='slip_id.analytic_account_id', string='Cuenta Analitica', store=True)
    struct_slip_id = fields.Many2one(related='slip_id.struct_id', string='Estructura', store=True)

    @api.depends('quantity', 'amount', 'rate')
    def _compute_total(self):
        #round_payroll = bool(self.env['ir.config_parameter'].sudo().get_param('zue_hr_payroll.round_payroll')) or False
        for line in self:
            amount_total_original = float(line.quantity) * line.amount * line.rate / 100
            part_decimal, part_value = math.modf(amount_total_original)
            amount_total = float(line.quantity) * line.amount * line.rate / 100 #if round_payroll == False else float(line.quantity) * line.amount * line.rate / 100
            if part_decimal >= 0.5 and math.modf(amount_total)[1] == part_value:
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
    category_id = fields.Many2one(related='salary_rule_id.category_id', string='Categoría',readonly=True, store=True)
    contract_id = fields.Many2one('hr.contract', string='Contrato', required=True, index=True)
    employee_id = fields.Many2one('hr.employee', string='Empleado', required=True)
    entity_id = fields.Many2one('hr.employee.entities', string="Entidad")
    loan_id = fields.Many2one('hr.loans', 'Prestamo', readonly=True)   
    rate = fields.Float(string='Porcentaje (%)', digits='Payroll Rate', default=100.0)
    amount = fields.Float(string='Importe',digits='Payroll')
    quantity = fields.Float(string='Cantidad',digits='Payroll', default=1.0)
    total = fields.Float(compute='_compute_total', string='Total', digits='Payroll', store=True) 

    @api.depends('quantity', 'amount', 'rate')
    def _compute_total(self):
        for line in self:
            line.total = float(line.quantity) * line.amount * line.rate / 100

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if 'employee_id' not in values or 'contract_id' not in values:
                payslip = self.env['hr.payslip'].browse(values.get('slip_id'))
                values['employee_id'] = values.get('employee_id') or payslip.employee_id.id
                values['contract_id'] = values.get('contract_id') or payslip.contract_id and payslip.contract_id.id
                if not values['contract_id']:
                    raise UserError(_('You must set a contract to create a payslip line.'))
        return super(Hr_payslip_not_line, self).create(vals_list)

class Hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    rtefte_id = fields.Many2one('hr.employee.rtefte', 'RteFte', readonly=True)
    not_line_ids = fields.One2many('hr.payslip.not.line', 'slip_id', string='Reglas no aplicadas', readonly=True)
    observation = fields.Text(string='Observación')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Cuenta analítica')
    struct_process = fields.Selection(related='struct_id.process', string='Proceso', store=True)
    employee_branch_id = fields.Many2one(related='employee_id.branch_id', string='Sucursal empleado', store=True)
    definitive_plan = fields.Boolean(string='Plano definitivo generado')
    #Fechas liquidación de contrato
    date_liquidacion = fields.Date('Fecha liquidación de contrato')
    date_prima = fields.Date('Fecha liquidación de prima')
    date_cesantias = fields.Date('Fecha liquidación de cesantías')
    date_vacaciones = fields.Date('Fecha liquidación de vacaciones')

    def name_get(self):
        result = []
        for record in self:
            if record.payslip_run_id:
                result.append((record.id, "{} - {}".format(record.payslip_run_id.name,record.employee_id.name)))
            else:
                result.append((record.id, "{} - {} - {}".format(record.struct_id.name,record.employee_id.name,str(record.date_from))))
        return result

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
        if self.line_ids and self.state in ['draft', 'verify']:
            if self.struct_id.process == 'nomina':
                values = [(5, 0, 0)] + [(0, 0, line_vals) for line_vals in self._get_payslip_lines()]                
            elif self.struct_id.process == 'vacaciones':
                values = [(5, 0, 0)] + [(0, 0, line_vals) for line_vals in self._get_payslip_lines_vacation()]                
            elif self.struct_id.process == 'cesantias' or self.struct_id.process == 'intereses_cesantias':
                values = [(5, 0, 0)] + [(0, 0, line_vals) for line_vals in self._get_payslip_lines_cesantias()]                
            elif self.struct_id.process == 'prima':
                values = [(5, 0, 0)] + [(0, 0, line_vals) for line_vals in self._get_payslip_lines_prima()]
            elif self.struct_id.process == 'contrato':                
                values = [(5, 0, 0)] + [(0, 0, line_vals) for line_vals in self._get_payslip_lines_contrato()]
            elif self.struct_id.process == 'otro':
                values = [(5, 0, 0)] + [(0, 0, line_vals) for line_vals in self._get_payslip_lines_other()]
            else:
                raise ValidationError(_('La estructura seleccionada se encuentra en desarrollo.'))

            self.update({'line_ids': values})

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to

        self.company_id = employee.company_id
        if not self.contract_id or self.employee_id != self.contract_id.employee_id:  # Add a default contract if not already defined
            contracts = employee._get_contracts(date_from, date_to)

            if not contracts or not contracts[0].structure_type_id.default_struct_id:
                self.contract_id = False
                self.struct_id = False
                return
            self.contract_id = contracts[0]
            self.struct_id = contracts[0].structure_type_id.default_struct_id

        payslip_name = self.struct_id.payslip_name or _('Recibo de Salario')

        mes = self.date_from.month
        month_name = self.env['hr.birthday.list'].get_name_month(mes)

        date_name = month_name + ' ' + str(self.date_from.year)
        #date_name = format_date(self.env, self.date_from, date_format="MMMM y")

        self.name = '%s - %s - %s' % (payslip_name, self.employee_id.name or '', date_name)
        self.analytic_account_id = self.contract_id.analytic_account_id

        if date_to > date_utils.end_of(fields.Date.today(), 'month'):
            self.warning_message = _(
                "This payslip can be erroneous! Work entries may not be generated for the period from %s to %s." %
                (date_utils.add(date_utils.end_of(fields.Date.today(), 'month'), days=1), date_to))
        else:
            self.warning_message = False

        self.worked_days_line_ids = self._get_new_worked_days_lines()

    def compute_sheet(self):
        for payslip in self.filtered(lambda slip: slip.state not in ['cancel', 'done']):
            number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
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
                payslip.write({'line_ids': lines, 'number': number, 'state': 'verify',
                               'analytic_account_id': payslip.contract_id.analytic_account_id.id,
                               'compute_date': fields.Date.today()})
        return True
    
    def restart_payroll(self):
        for payslip in self:
            #Eliminar contabilización y el calculo
            payslip.mapped('move_id').unlink()
            # Modificar cuotas de prestamos pagadas
            obj_payslip_line = self.env['hr.payslip.line'].search(
                [('slip_id', '=', payslip.id), ('loan_id', '!=', False)])
            for payslip_line in obj_payslip_line:
                obj_loan_line = self.env['hr.loans.line'].search(
                    [('employee_id', '=', payslip_line.employee_id.id), ('prestamo_id', '=', payslip_line.loan_id.id),
                     ('payslip_id', '>=', payslip.id)])
                if payslip.struct_id.process == 'contrato' and payslip_line.loan_id.final_settlement_contract == True:
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
            self.env['hr.vacation'].search([('payslip', '=', payslip.id)]).unlink()
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
                    #Ultimo día de febrero
                    work_hours = self.contract_id._get_work_hours(self.date_to, self.date_to)
                    work_hours_ordered = sorted(work_hours.items(), key=lambda x: x[1])
                    biggest_work = work_hours_ordered[-1][0] if work_hours_ordered else 0
                    #Primer día de marzo
                    march_date_from = self.date_to + timedelta(days=1)
                    march_date_to = self.date_to + timedelta(days=1)
                    march_work_hours = self.contract_id._get_work_hours(march_date_from, march_date_to)
                    march_work_hours_ordered = sorted(march_work_hours.items(), key=lambda x: x[1])
                    march_biggest_work = march_work_hours_ordered[-1][0] if march_work_hours_ordered else 0
                    #Proceso a realizar
                    #if march_biggest_work == 0 or biggest_work != march_biggest_work: #Si la ausencia no continua hasta marzo se agregan 2 días trabajados para completar los 30 días en febrero
                    # 25/02/2023 | Se realiza que siempre cree 2 días laborados para completar  los 30 dias ignorando si la ausencia continua en marzo
                    # Por ende se comenta la funcionalidad anterior.
                    work_entry_type = self.env['hr.work.entry.type'].search([('code','=','WORK100')])
                    attendance_line = {
                        'sequence': work_entry_type.sequence,
                        'work_entry_type_id': work_entry_type.id,
                        'number_of_days': days_summary,
                        'number_of_hours': hours_summary,
                        'amount': 0,
                    }
                    worked_days_lines |= worked_days_lines.new(attendance_line)
                    # else: #Si la ausencia continua hasta marzo se agregan 2 días de la ausencia para completar los 30 días en febrero
                    #     work_entry_type = self.env['hr.work.entry.type'].search([('id', '=', biggest_work)])
                    #     for february_days in worked_days_lines:
                    #         if february_days.work_entry_type_id.code == work_entry_type.code:
                    #             february_days.number_of_days = february_days.number_of_days + days_summary  # Se agregan 2 días
                    #             february_days.number_of_hours = february_days.number_of_hours + hours_summary  # Se agregan 16 horas
            #return worked_days_lines
            res = []
            for w in worked_days_lines:
                res.append({
                    'sequence': w.sequence,
                    'work_entry_type_id': w.work_entry_type_id.id,
                    'number_of_days': w.number_of_days,
                    'number_of_hours': w.number_of_hours,
                })

            return [(5, 0, 0)] + [(0, 0, vals) for vals in res]
        else:
            return [(5, False, False)]

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
        contract = self.contract_id
        year = self.date_from.year
        annual_parameters = self.env['hr.annual.parameters'].search([('year', '=', year)])

        #Se eliminan registros actuales para el periodo ejecutado de Retención en la fuente
        self.env['hr.employee.deduction.retention'].search([('employee_id', '=', employee.id),('year', '=', self.date_from.year),('month', '=', self.date_from.month)]).unlink()
        self.env['hr.employee.rtefte'].search([('employee_id', '=', employee.id),('year', '=', self.date_from.year),('month', '=', self.date_from.month)]).unlink()

        #Se obtienen las entradas de trabajo
        date_from = datetime.combine(self.date_from, datetime.min.time())
        date_to = datetime.combine(self.date_to, datetime.max.time())
        #Primero, encontró una entrada de trabajo que no excedió el intervalo.
        work_entries = self.env['hr.work.entry'].search(
            [
                ('state', 'in', ['validated', 'draft']),
                ('date_start', '>=', date_from),
                ('date_stop', '<=', date_to),
                ('contract_id', '=', contract.id),
                ('leave_id','!=',False)
            ]
        )
        #En segundo lugar, encontró entradas de trabajo que exceden el intervalo y calculan la duración correcta. 
        work_entries += self.env['hr.work.entry'].search(
            [
                '&', '&',
                ('state', 'in', ['validated', 'draft']),
                ('contract_id', '=', contract.id),
                '|', '|', '&', '&',
                ('date_start', '>=', date_from),
                ('date_start', '<', date_to),
                ('date_stop', '>', date_to),
                '&', '&',
                ('date_start', '<', date_from),
                ('date_stop', '<=', date_to),
                ('date_stop', '>', date_from),
                '&',
                ('date_start', '<', date_from),
                ('date_stop', '>', date_to),
            ]
        )
        #Validar incapacidades de mas de 180 dias
        leaves = {}
        lst_leave_ids = []
        for leave in work_entries:
            if leave.leave_id:
                if leave.leave_id.id not in lst_leave_ids:
                    lst_leave_ids.append(leave.leave_id.id)
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
                        leaves[leave.work_entry_type_id.code] += number_of_days
                    else:
                        leaves[leave.work_entry_type_id.code+'_TOTAL'] = number_of_days_total
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
                                leaves[leave.work_entry_type_id.code + '_PARTNER'] += days_partner
                            else:
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
                    'contract': contract,
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
                        'contract_id': contract.id,
                        'employee_id': employee.id,
                        'entity_id': concepts.partner_id.id if concepts.partner_id else False,
                        # 'loan_id': loan_id,
                        'amount': tot_rule, #Se redondean los decimales de todas las reglas
                        'quantity': 1.0,
                        'rate': 100,
                        'slip_id': self.id,
                    }
                    
        #Ejecutar las reglas salariales y su respectiva lógica
        for rule in sorted(self.struct_id.rule_ids, key=lambda x: x.sequence):
            localdict.update({
                'id_contract_concepts': 0,
                'result': None,
                'result_qty': 1.0,
                'result_rate': 100})
            if rule._satisfy_condition(localdict):
                entity_id,loan_id = 0,0
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
                #Valida que si la regla esta en la pestaña de Devengo & Deducciones del contrato
                obj_concept = self.env['hr.contract.concepts'].search([('contract_id', '=', contract.id),('input_id','=',rule.id)])
                
                if obj_concept:
                    #Obtener Info devengos y deducciónes - Contrato empleados
                    for concept in obj_concept:
                        date_start_concept = concept.date_start if concept.date_start else datetime.strptime('01/01/1900', '%d/%m/%Y').date()
                        date_end_concept = concept.date_end if concept.date_end else datetime.strptime('31/12/2080', '%d/%m/%Y').date()
                        if concept.state == 'done' and date_start_concept <= date_to.date() and date_end_concept >= date_from.date():
                            localdict.update({'id_contract_concepts': concept.id})
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
                                if part_decimal >= 0.5 and tot_rule == part_value:
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
                                    if concept.loan_id.final_settlement_contract == True:
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
                                        if part_decimal >= 0.5 and tot_rule == part_value:
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
                                                'contract_id': contract.id,
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
                                    'contract_id': contract.id,
                                    'employee_id': employee.id,
                                    'entity_id': entity_id,
                                    'loan_id': loan_id,
                                    'amount': amount, 
                                    'quantity': qty,
                                    'rate': rate,
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
                                    'contract_id': contract.id,
                                    'employee_id': employee.id,
                                    'entity_id': entity_id,
                                    'loan_id': loan_id,
                                    'amount': amount, 
                                    'quantity': qty,
                                    'rate': rate,
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
                        if part_decimal >= 0.5 and math.modf(tot_rule)[1] == part_value:
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
                                'contract_id': contract.id,
                                'employee_id': employee.id,
                                'entity_id': entity_id,
                                'loan_id': loan_id,
                                'amount': amount, #Se redondean los decimales de todas las reglas
                                'quantity': qty,
                                'rate': rate,
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
                                'contract_id': contract.id,
                                'employee_id': employee.id,
                                'entity_id': entity_id,
                                'loan_id': loan_id,
                                'amount': amount, #Se redondean los decimales de todas las reglas
                                'quantity': qty,
                                'rate': rate,
                                'slip_id': self.id,
                            }
        
        #Cargar detalle retención en la fuente si tuvo
        obj_rtefte = self.env['hr.employee.rtefte'].search([('employee_id', '=', employee.id),('type_tax', '=', self.env['hr.type.tax.retention'].search([('code', '=', contract.retention_procedure)],limit=1).id),
                                                            ('year', '=', self.date_from.year),('month', '=', self.date_from.month)])
        if obj_rtefte:
            for rtefte in obj_rtefte:
                self.rtefte_id = rtefte.id

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
            
    def action_payslip_done(self):
        #res = super(Hr_payslip, self).action_payslip_done()
        if any(slip.state == 'cancel' for slip in self):
            raise ValidationError(_("You can't validate a cancelled payslip."))
        self.write({'state' : 'done'})
        self.mapped('payslip_run_id').action_close()
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
                    'datas': base64.encodestring(pdf_content),
                    'res_model': payslip._name,
                    'res_id': payslip.id
                })
        '''

        #Contabilización
        self._action_create_account_move()
        #Actualizar en la tabla de prestamos la cuota pagada
        for record in self:
            obj_payslip_line = self.env['hr.payslip.line'].search([('slip_id', '=', record.id),('loan_id', '!=', False)])
            for payslip_line in obj_payslip_line:
                if record.struct_id.process == 'contrato' and payslip_line.loan_id.final_settlement_contract == True:
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
                            'contract_id': record.contract_id.id,
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
                            'contract_id': record.contract_id.id,
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
                                                                                      ('contract_id','=',record.contract_id.id),
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
                            'contract_id': record.contract_id.id,
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
                            'contract_id': record.contract_id.id,
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
                            'contract_id': record.contract_id.id,
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
                            'contract_id': record.contract_id.id,
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
                            'contract_id': record.contract_id.id,
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
                            'contract_id': record.contract_id.id,
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

                obj_contrato = self.env['hr.contract'].search([('id','=',record.contract_id.id)])
                values_update = {'retirement_date':record.date_liquidacion,
                                'state':'close'}
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
                        payments.payslip.write({'observation':payments.payslip.observation+ '\n El valor se trasladó a la liquidación '+self.number+' de '+self.struct_id.name })
                    else:
                        payments.payslip.write({'observation': 'El valor se trasladó a la liquidación ' + self.number + ' de ' + self.struct_id.name})
