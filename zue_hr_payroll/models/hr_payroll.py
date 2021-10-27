# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from .browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips
from odoo.tools import float_compare, float_is_zero

from collections import defaultdict
from datetime import datetime, timedelta, date, time
import pytz

#---------------------------LIQUIDACIÓN DE NÓMINA-------------------------------#

class Account_journal(models.Model):
    _inherit = 'account.journal'

    is_payroll_spreader = fields.Boolean('Es dispersor de nómina')

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    observations = fields.Text('Observaciones')
    definitive_plan = fields.Boolean(string='Plano definitivo generado')

    def action_validate(self):
        self.mapped('slip_ids').filtered(lambda slip: slip.state != 'cancel').action_payslip_done()
        self.action_close()

    def restart_payroll_batch(self):
        self.mapped('slip_ids').action_payslip_cancel()
        self.mapped('slip_ids').unlink()
        return self.write({'state': 'draft','observations':False})
    
    def restart_full_payroll_batch(self):
        for payslip in self.slip_ids.with_progress(msg='Reversando nómina contabilizada',cancellable=False):
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
    
    def _get_available_contracts_domain(self):
        return [('contract_ids.state', '=', 'open'), ('company_id', '=', self.env.company.id)]

    def _check_undefined_slots(self, work_entries, payslip_run):
        """
        Check if a time slot in the contract's calendar is not covered by a work entry
        """
        calendar_is_not_covered = self.env['hr.contract']
        work_entries_by_contract = defaultdict(lambda: self.env['hr.work.entry'])
        for work_entry in work_entries:
            work_entries_by_contract[work_entry.contract_id] |= work_entry

        for contract, work_entries in work_entries_by_contract.items():
            calendar_start = pytz.utc.localize(datetime.combine(max(contract.date_start, payslip_run.date_start), time.min))
            calendar_end = pytz.utc.localize(datetime.combine(min(contract.date_end or date.max, payslip_run.date_end), time.max))
            outside = contract.resource_calendar_id._attendance_intervals_batch(calendar_start, calendar_end)[False] - work_entries._to_intervals()
            if outside:
                calendar_is_not_covered |= contract
                #calendar_is_not_covered.append(contract.id)
                #raise UserError(_("Some part of %s's calendar is not covered by any work entry. Please complete the schedule.") % contract.employee_id.name)

        return calendar_is_not_covered

    def compute_sheet(self):
        self.ensure_one()
        if not self.env.context.get('active_id'):
            from_date = fields.Date.to_date(self.env.context.get('default_date_start'))
            end_date = fields.Date.to_date(self.env.context.get('default_date_end'))
            payslip_run = self.env['hr.payslip.run'].create({
                'name': from_date.strftime('%B %Y'),
                'date_start': from_date,
                'date_end': end_date,
            })
        else:
            payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))

        employees = self.with_context(active_test=False).employee_ids
        if not employees:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))

        payslips = self.env['hr.payslip']
        Payslip = self.env['hr.payslip']

        observations = False
        contracts = employees._get_contracts(payslip_run.date_start, payslip_run.date_end, states=['open']) # , 'close'
        contracts._generate_work_entries(payslip_run.date_start, payslip_run.date_end)
        
        if self.structure_id.use_worked_day_lines:
            work_entries = self.env['hr.work.entry'].search([
                ('date_start', '<=', payslip_run.date_end),
                ('date_stop', '>=', payslip_run.date_start),
                ('employee_id', 'in', employees.ids),
            ])
            calendar_is_not_covered = self._check_undefined_slots(work_entries, payslip_run)

            if calendar_is_not_covered:
                date_start = fields.Datetime.to_datetime(payslip_run.date_start)
                date_stop = datetime.combine(fields.Datetime.to_datetime(payslip_run.date_end), datetime.max.time())        
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
                #raise UserError(_("Some work entries could not be validated."))

            # for calendar in calendar_is_not_covered:
            #     observations = '' if observations == False else observations
            #     msg = ("Alguna parte del calendario de %s no está cubierta por ninguna entrada de trabajo. Por favor complete el horario.") % calendar.employee_id.name
            #     observations = observations + '\n' + msg

        default_values = Payslip.default_get(Payslip.fields_get())
        
        #Se agrega metodo with_progress para mostrar una barra de progreso
        for contract in contracts.with_progress(msg='Paso 1 de 2 - Creando nómina',cancellable=False):
            values = dict(default_values, **{
                'employee_id': contract.employee_id.id,
                'credit_note': payslip_run.credit_note,
                'payslip_run_id': payslip_run.id,
                'date_from': payslip_run.date_start,
                'date_to': payslip_run.date_end,
                'contract_id': contract.id,
                'struct_id': self.structure_id.id or contract.structure_type_id.default_struct_id.id,
            })
            payslip = self.env['hr.payslip'].new(values)
            payslip._onchange_employee()
            values = payslip._convert_to_write(payslip._cache)
            payslips += Payslip.create(values)
        payslips.compute_sheet()
        payslip_run.state = 'verify'
        payslip_run.observations = observations

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
    amount_base = fields.Float('Base')

    @api.depends('quantity', 'amount', 'rate')
    def _compute_total(self):
        for line in self:
            line.total = round(float(line.quantity) * line.amount * line.rate / 100,0)

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
    analytic_account_id = fields.Many2one(related='contract_id.analytic_account_id',string='Cuenta analítica', store=True)
    struct_process = fields.Selection(related='struct_id.process', string='Proceso', store=True)
    definitive_plan = fields.Boolean(string='Plano definitivo generado')
    #Fechas liquidación de contrato
    date_liquidacion = fields.Date('Fecha liquidación de contrato')
    date_prima = fields.Date('Fecha liquidación de prima')
    date_cesantias = fields.Date('Fecha liquidación de cesantías')
    date_vacaciones = fields.Date('Fecha liquidación de vacaciones')    
    
    @api.onchange('worked_days_line_ids', 'input_line_ids')
    def _onchange_worked_days_inputs(self):
        if self.line_ids and self.state in ['draft', 'verify']:
            if self.struct_id.process == 'nomina' or self.struct_id.process == 'otro':
                values = [(5, 0, 0)] + [(0, 0, line_vals) for line_vals in self._get_payslip_lines()]                
            elif self.struct_id.process == 'vacaciones':
                values = [(5, 0, 0)] + [(0, 0, line_vals) for line_vals in self._get_payslip_lines_vacation()]                
            elif self.struct_id.process == 'cesantias_e_intereses':
                values = [(5, 0, 0)] + [(0, 0, line_vals) for line_vals in self._get_payslip_lines_cesantias()]                
            elif self.struct_id.process == 'prima':
                values = [(5, 0, 0)] + [(0, 0, line_vals) for line_vals in self._get_payslip_lines_prima()]
            elif self.struct_id.process == 'contrato':                
                values = [(5, 0, 0)] + [(0, 0, line_vals) for line_vals in self._get_payslip_lines_contrato()]                
            else:
                raise ValidationError(_('La estructura seleccionada se encuentra en desarrollo.'))

            self.update({'line_ids': values})

    def compute_sheet(self):
        #Se agrega metodo with_progress para mostrar una barra de progreso
        for payslip in self.filtered(lambda slip: slip.state not in ['cancel', 'done']).with_progress(msg='Paso 2 de 2 - Calculando nómina',cancellable=False):
            number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
            # delete old payslip lines
            payslip.line_ids.unlink()
            payslip.not_line_ids.unlink()

            #Seleccionar proceso a ejecutar
            lines = []
            if payslip.struct_id.process == 'nomina' or payslip.struct_id.process == 'otro':
                lines = [(0, 0, line) for line in payslip._get_payslip_lines()]
            elif payslip.struct_id.process == 'vacaciones':
                lines = [(0, 0, line) for line in payslip._get_payslip_lines_vacation()]
            elif payslip.struct_id.process == 'cesantias_e_intereses':
                lines = [(0, 0, line) for line in payslip._get_payslip_lines_cesantias()]
            elif payslip.struct_id.process == 'prima':
                lines = [(0, 0, line) for line in payslip._get_payslip_lines_prima()]
            elif payslip.struct_id.process == 'contrato':                
                lines = [(0, 0, line) for line in payslip._get_payslip_lines_contrato()]                
            else:
                raise ValidationError(_('La estructura seleccionada se encuentra en desarrollo.'))

            if lines:
                payslip.write({'line_ids': lines, 'number': number, 'state': 'verify', 'compute_date': fields.Date.today()})
        return True
    
    def restart_payroll(self):
        for payslip in self:
            #Eliminar contabilización y el calculo
            payslip.mapped('move_id').unlink() 
            payslip.line_ids.unlink()
            payslip.not_line_ids.unlink()
            #Eliminar historicos            
            self.env['hr.vacation'].search([('payslip', '=', payslip.id)]).unlink()
            self.env['hr.history.prima'].search([('payslip', '=', payslip.id)]).unlink()
            self.env['hr.history.cesantias'].search([('payslip', '=', payslip.id)]).unlink()
            #Reversar Liquidación            
            payslip.action_payslip_draft()            

    #--------------------------------------------------LIQUIDACIÓN DE LA NÓMINA PERIÓDICA---------------------------------------------------------#

    def _get_payslip_lines(self,inherit_vacation=0,inherit_contrato_dev=0,inherit_contrato_ded=0,localdict=None):
        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
            localdict['categories'].dict[category.code] = localdict['categories'].dict.get(category.code, 0) + amount
            return localdict

        def _sum_salary_rule(localdict, rule, amount):
            localdict['rules_computed'].dict[rule.code] = localdict['rules_computed'].dict.get(rule.code, 0) + amount
            #Sumatoria de valores que son base para los procesos
            if rule.category_id.code != 'BASIC':
                localdict['values_base_prima'] += amount if rule.base_prima else 0
                localdict['values_base_cesantias'] += amount if rule.base_cesantias else 0
                localdict['values_base_int_cesantias'] += amount if rule.base_intereses_cesantias else 0
                localdict['values_base_vacremuneradas'] += amount if rule.base_vacaciones_dinero else 0
                localdict['values_base_vacdisfrutadas'] += amount if rule.base_vacaciones else 0
            
            return localdict

        self.ensure_one()
        result = {}
        result_not = {}
        rules_dict = {}
        worked_days_dict = {line.code: line for line in self.worked_days_line_ids if line.code}
        inputs_dict = {line.code: line for line in self.input_line_ids if line.code}
        
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
        for leave in work_entries:
            if leave.leave_id:
                es_continuidad = 1
                number_of_days = leave.leave_id.number_of_days
                holiday_status_id = leave.leave_id.holiday_status_id.id
                request_date_to = leave.leave_id.request_date_from - timedelta(days=1)
                while es_continuidad == 1:
                    obj_leave = self.env['hr.leave'].search([('employee_id', '=', employee.id),
                                                            ('holiday_status_id','=',holiday_status_id),('request_date_to','=',request_date_to)])       
                    if obj_leave:
                        number_of_days = number_of_days + obj_leave.number_of_days
                        holiday_status_id = obj_leave.holiday_status_id.id
                        request_date_to = obj_leave.request_date_from - timedelta(days=1)
                    else:
                        es_continuidad = 0
                leaves[leave.work_entry_type_id.code] = number_of_days
        
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
                    'values_base_vacremuneradas': 0,
                    'values_base_vacdisfrutadas': 0,
                    'inherit_contrato':inherit_contrato_ded+inherit_contrato_dev, 
                }
            }
        else:
            localdict.update({
                'values_leaves_all' : 0,
                'values_leaves_law' : 0,
                #Sumatoria de valores que son base para los procesos
                'values_base_prima': 0,
                'values_base_cesantias': 0,
                'values_base_int_cesantias': 0,
                'values_base_vacremuneradas': 0,
                'values_base_vacdisfrutadas': 0,
                'inherit_contrato':inherit_contrato_ded+inherit_contrato_dev,})

        #Saber si tiene días de vacaciones
        days_vac = 0
        days_vac += leaves.get('VACDISFRUTADAS') if leaves.get('VACDISFRUTADAS') != None else 0
        #days_vac += leaves.get('VACREMUNERADAS') if leaves.get('VACREMUNERADAS') != None else 0

        worked_days_vac = 0
        worked_days_vac += worked_days_dict.get('VACDISFRUTADAS').number_of_days  if worked_days_dict.get('VACDISFRUTADAS') != None else 0
        #worked_days_vac += worked_days_dict.get('VACREMUNERADAS').number_of_days  if worked_days_dict.get('VACREMUNERADAS') != None else 0

        #Cargar novedades por conceptos diferentes
        obj_novelties = self.env['hr.novelties.different.concepts'].search([('employee_id', '=', employee.id),
                                                            ('date', '>=', self.date_from),('date', '<=', self.date_to)])
        for concepts in obj_novelties:
            if concepts.amount != 0:
                previous_amount = concepts.salary_rule_id.code in localdict and localdict[concepts.salary_rule_id.code] or 0.0
                #set/overwrite the amount computed for this rule in the localdict
                tot_rule = round(concepts.amount * 1.0 * 100 / 100.0,0)

                #LIQUIDACION DE CONTRATO SOLO DEV OR DED DEPENDIENTO SU ORIGEN
                if (inherit_contrato_dev != 0 or inherit_contrato_ded != 0) and self.novelties_payroll_concepts == False and not concepts.salary_rule_id.code in ['TOTALDEV','TOTALDED','NET']:
                   tot_rule = 0
                if inherit_contrato_dev != 0 and concepts.salary_rule_id.dev_or_ded != 'devengo':                            
                    tot_rule = 0
                if inherit_contrato_ded != 0 and concepts.salary_rule_id.dev_or_ded != 'deduccion'and not concepts.salary_rule_id.code in ['TOTALDEV','NET']:                            
                    tot_rule = 0

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

                if tot_rule != 0:
                    result_item = concepts.salary_rule_id.code+'-PCD'+str(concepts.id)
                    result[result_item] = {
                        'sequence': concepts.salary_rule_id.sequence,
                        'code': concepts.salary_rule_id.code,
                        'name': concepts.salary_rule_id.name,
                        'note': concepts.salary_rule_id.note,
                        'salary_rule_id': concepts.salary_rule_id.id,
                        'contract_id': contract.id,
                        'employee_id': employee.id,
                        # 'entity_id': entity_id,
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
                            if rule.dev_or_ded == 'deduccion' and rule.type_concept != 'ley' and (worked_days_entry + leaves_days_all) == 0:
                                amount, qty, rate = 0,1.0,100    

                            #LIQUIDACION DE CONTRATO SOLO DEV OR DED DEPENDIENTO SU ORIGEN
                            if (inherit_contrato_dev != 0 or inherit_contrato_ded != 0) and self.settle_payroll_concepts == False and not rule.code in ['TOTALDEV','TOTALDED','NET']:
                                amount, qty, rate = 0,1.0,100
                            if inherit_contrato_dev != 0 and rule.dev_or_ded != 'devengo':                            
                                amount, qty, rate = 0,1.0,100
                            if inherit_contrato_ded != 0 and rule.dev_or_ded != 'deduccion'and not rule.code in ['TOTALDEV','NET']:                            
                                amount, qty, rate = 0,1.0,100   

                            #VACACIONES SOLAMENTE DEDUCCIONES
                            if inherit_vacation != 0 and rule.dev_or_ded != 'deduccion' and not rule.code in ['TOTALDEV','NET']:                            
                                amount, qty, rate = 0,1.0,100   

                            if days_vac >= 5 and rule.dev_or_ded == 'deduccion' and not rule.code in ['TOTALDED']:
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
                                            vac_months.append(str_vac)
                                            days_fifteen = 0
                                            days_thirty = 0

                                    #Cant de quincenas involucradas en la liquidación de vacaciones
                                    cant_fortnight = 0
                                    for vac_days in vac_months:
                                        cant_fortnight += 1 if vac_days_for_month.get(vac_days).get('days_fifteen') >= 5 else 0 
                                        cant_fortnight += 1 if vac_days_for_month.get(vac_days).get('days_thirty') >= 5 else 0 

                                    if cant_fortnight > 1:
                                        amount = amount * 2 if not rule.modality_value in ['diario','diario_efectivo'] and rule.type_concept != 'ley' else amount                                    
                                else:
                                    if worked_days_vac >= 5:
                                        amount, qty, rate = 0,1.0,100

                            #Continuar con el proceso normal
                            amount = round(amount,0) #Se redondean los decimales de todas las reglas
                            #check if there is already a rule computed with that code
                            previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                            #set/overwrite the amount computed for this rule in the localdict
                            tot_rule = (amount * qty * rate / 100.0) + previous_amount
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
                                if rule.dev_or_ded == 'deduccion':
                                    if rule.type_concept == 'ley':
                                        value_tmp_neto = localdict['categories'].dict.get('DEV_SALARIAL',0) + localdict['categories'].dict.get('DEV_NO_SALARIAL',0) + localdict['categories'].dict.get('DEDUCCIONES',0) 
                                    else:
                                        value_tmp_neto = (localdict['categories'].dict.get('DEV_SALARIAL',0) + localdict['categories'].dict.get('DEV_NO_SALARIAL',0) + localdict['categories'].dict.get('DEDUCCIONES',0)) - localdict['values_leaves_law']
                                else:
                                    value_tmp_neto = 1                            
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
                    if rule.dev_or_ded == 'deduccion' and rule.type_concept != 'ley' and (worked_days_entry + leaves_days_all) == 0:
                        amount, qty, rate = 0,1.0,100 

                    #LIQUIDACION DE CONTRATO SOLO DEV OR DED DEPENDIENTO SU ORIGEN
                    if str(rule.amount_python_compute).find('get_overtime') != -1: #Verficiar si la regla utiliza la tabla hr.overtime por ende es un concepto de novedad del menu horas extras
                        if (inherit_contrato_dev != 0 or inherit_contrato_ded != 0) and self.novelties_payroll_concepts == False and not rule.code in ['TOTALDEV','TOTALDED','NET']:
                            amount, qty, rate = 0,1.0,100
                    else:
                        if (inherit_contrato_dev != 0 or inherit_contrato_ded != 0) and self.settle_payroll_concepts == False and not rule.code in ['TOTALDEV','TOTALDED','NET']:
                            amount, qty, rate = 0,1.0,100
                    if inherit_contrato_dev != 0 and rule.dev_or_ded != 'devengo':                            
                        amount, qty, rate = 0,1.0,100
                    if inherit_contrato_ded != 0 and rule.dev_or_ded != 'deduccion' and not rule.code in ['TOTALDEV','NET']:                            
                        amount, qty, rate = 0,1.0,100   

                    #VACACIONES SOLAMENTE DEDUCCIONES
                    if inherit_vacation != 0 and rule.dev_or_ded != 'deduccion' and not rule.code in ['TOTALDEV','NET']:                            
                        amount, qty, rate = 0,1.0,100  
                    amount = round(amount,0) #Se redondean los decimales de todas las reglas
                    #check if there is already a rule computed with that code
                    previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                    #set/overwrite the amount computed for this rule in the localdict
                    tot_rule = (amount * qty * rate / 100.0) + previous_amount
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
                        if rule.dev_or_ded == 'deduccion':
                            if rule.type_concept == 'ley':
                                value_tmp_neto = localdict['categories'].dict.get('DEV_SALARIAL',0) + localdict['categories'].dict.get('DEV_NO_SALARIAL',0) + localdict['categories'].dict.get('DEDUCCIONES',0) 
                            else:
                                value_tmp_neto = (localdict['categories'].dict.get('DEV_SALARIAL',0) + localdict['categories'].dict.get('DEV_NO_SALARIAL',0) + localdict['categories'].dict.get('DEDUCCIONES',0)) - localdict['values_leaves_law']
                        else:
                            value_tmp_neto = 1
                        if value_tmp_neto >= 0:
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
        obj_rtefte = self.env['hr.employee.rtefte'].search([('employee_id', '=', employee.id),
                                                            ('year', '=', self.date_from.year),('month', '=', self.date_from.month)])
        if obj_rtefte:
            for rtefte in obj_rtefte:
                self.rtefte_id = rtefte.id

        # Agregar reglas no aplicadas
        not_lines = [(0, 0, not_line) for not_line in result_not.values()]
        self.not_line_ids = not_lines

        #Retornar resultado final de la liquidación de nómina
        if inherit_vacation != 0:            
            return result            
        elif inherit_contrato_dev != 0 or inherit_contrato_ded != 0:  
            return localdict,result           
        else:
            return result.values()  
            
    def action_payslip_done(self):
        #res = super(Hr_payslip, self).action_payslip_done()
        if any(slip.state == 'cancel' for slip in self):
            raise ValidationError(_("You can't validate a cancelled payslip."))
        self.write({'state' : 'done'})
        self.mapped('payslip_run_id').action_close()
        
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
                obj_loan_line = self.env['hr.loans.line'].search([('employee_id', '=', payslip_line.employee_id.id),('prestamo_id', '=', payslip_line.loan_id.id),
                                                                    ('date','>=',record.date_from),('date','<=',record.date_to)])
                data = {
                    'paid':True,
                    'payslip_id': record.id
                }
                obj_loan_line.write(data)
                
                obj_loan = self.env['hr.loans'].search([('employee_id', '=', payslip_line.employee_id.id),('id', '=', payslip_line.loan_id.id)])
                if obj_loan.balance_amount <= 0:
                    self.env['hr.contract.concepts'].search([('loan_id', '=', payslip_line.loan_id.id)]).unlink()

            if record.struct_id.process == 'vacaciones':
                history_vacation = []
                for line in sorted(record.line_ids.filtered(lambda filter: filter.initial_accrual_date), key=lambda x: x.initial_accrual_date):                
                    if line.code == 'VACDISFRUTADAS':
                        info_vacation = {
                            'employee_id': record.employee_id.id,
                            'contract_id': record.contract_id.id,
                            'initial_accrual_date': line.initial_accrual_date,
                            'final_accrual_date': line.final_accrual_date,
                            'departure_date': record.date_from,
                            'return_date': record.date_to,
                            'business_units': line.business_units,
                            'value_business_days': line.business_units * line.amount,
                            'holiday_units': line.holiday_units,
                            'holiday_value': line.holiday_units * line.amount,                            
                            'base_value': line.amount_base,
                            'total': (line.business_units * line.amount)+line.holiday_units * line.amount,
                            'payslip': record.id
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

                    history_vacation.append(info_vacation)               

                if history_vacation: 
                    for history in history_vacation:
                        self.env['hr.vacation'].create(history) 

            if record.struct_id.process == 'cesantias_e_intereses':
                his_cesantias = {}         
                his_intcesantias = {}

                for line in record.line_ids:                
                    #Historico cesantias                
                    if line.code == 'CESANTIAS':
                        his_cesantias = {
                            'employee_id': record.employee_id.id,
                            'contract_id': record.contract_id.id,
                            'initial_accrual_date': record.date_from,
                            'final_accrual_date': record.date_to,
                            'settlement_date': record.date_to,                        
                            'time': line.quantity,
                            'base_value':line.amount_base,
                            'severance_value': line.total,                        
                            'payslip': record.id
                        }             

                    if line.code == 'INTCESANTIAS':
                        his_intcesantias = {
                            'severance_interest_value': line.total,
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
                            'units_of_money': line.quantity,
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
                    if line.code == 'CESANTIAS':
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

                    if line.code == 'INTCESANTIAS':
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

    #--------------------------------------------------CONTABILIZACIÓN DE LA NÓMINA---------------------------------------------------------#

    #Items contabilidad
    def _prepare_line_values(self, line, account_id, date, debit, credit, analytic_account_id):
        return {
            'name': line.name,
            'partner_id': line.partner_id.id,
            'account_id': account_id,
            'journal_id': line.slip_id.struct_id.journal_id.id,
            'date': date,
            'debit': debit,
            'credit': credit,
            'analytic_account_id': analytic_account_id,#line.salary_rule_id.analytic_account_id.id or line.slip_id.contract_id.analytic_account_id.id,
        }

    # Verificar existencia de items
    def _get_existing_lines(self, line_ids, line, account_id, debit, credit):
        existing_lines = (
            line_id for line_id in line_ids if
            line_id['name'] == line.name
            and line_id['partner_id'] == line.partner_id.id
            and line_id['account_id'] == account_id
            and line_id['analytic_account_id'] == (line.salary_rule_id.analytic_account_id.id or line.slip_id.contract_id.analytic_account_id.id)
            and ((line_id['debit'] > 0 and credit <= 0) or (line_id['credit'] > 0 and debit <= 0)))
        return next(existing_lines, False)

    #Contabilización de la liquidación de nómina - se sobreescribe el metodo original
    def _action_create_account_move(self):
        #ZUE - Obtener modalidad de contabilización
        settings_batch_account = self.env['ir.config_parameter'].sudo().get_param('zue_hr_payroll.module_hr_payroll_batch_account') or False

        precision = self.env['decimal.precision'].precision_get('Payroll')

        # Add payslip without run
        payslips_to_post = self.filtered(lambda slip: not slip.payslip_run_id)

        # Adding pay slips from a batch and deleting pay slips with a batch that is not ready for validation.
        payslip_runs = (self - payslips_to_post).mapped('payslip_run_id')
        for run in payslip_runs:
            if run._are_payslips_ready():
                payslips_to_post |= run.slip_ids

        # A payslip need to have a done state and not an accounting move.
        payslips_to_post = payslips_to_post.filtered(lambda slip: slip.state == 'done' and not slip.move_id)

        # Check that a journal exists on all the structures
        if any(not payslip.struct_id for payslip in payslips_to_post):
            raise ValidationError(_('One of the contract for these payslips has no structure type.'))
        if any(not structure.journal_id for structure in payslips_to_post.mapped('struct_id')):
            raise ValidationError(_('One of the payroll structures has no account journal defined on it.'))

        slip_mapped_data = {slip.struct_id.journal_id.id: {fields.Date().end_of(slip.date_to, 'month'): self.env['hr.payslip']} for slip in payslips_to_post}
        for slip in payslips_to_post:
            slip_mapped_data[slip.struct_id.journal_id.id][fields.Date().end_of(slip.date_to, 'month')] |= slip

        for journal_id in slip_mapped_data: #For each journal_id.
            for slip_date in slip_mapped_data[journal_id]: # For each month.
                line_ids = []
                debit_sum = 0.0
                credit_sum = 0.0
                date = slip.date_to #slip_date
                move_dict = {
                    'narration': '',
                    'ref': date.strftime('%B %Y'),
                    'journal_id': journal_id,
                    'date': date,
                }
                
                for slip in self.web_progress_iter(slip_mapped_data[journal_id][slip_date],msg="Contabilizar",cancellable=False):
                    if len(slip.line_ids) > 0:
                        if settings_batch_account == '1': #Si en ajustes tiene configurado 'Crear movimiento contable por empleado'
                                                        # Se limpian los datos para crear un nuevo movimiento
                            line_ids = []
                            debit_sum = 0.0
                            credit_sum = 0.0
                            #date = slip_date
                            move_dict = {
                                'narration': '',                            
                                'ref': date.strftime('%B %Y') + ' - Nómina: ' + slip.number + ' - ' + slip.employee_id.name,
                                'journal_id': journal_id,
                                'date': date,
                            }

                        move_dict['narration'] += slip.number or '' + ' - ' + slip.employee_id.name
                        move_dict['narration'] += '\n'
                        print(slip.line_ids.filtered(lambda line: line.category_id))
                        for line in slip.line_ids.filtered(lambda line: line.category_id):
                            amount = -line.total if slip.credit_note else line.total
                            if line.code == 'NET': # Check if the line is the 'Net Salary'.
                                for tmp_line in slip.line_ids.filtered(lambda line: line.category_id):
                                    if tmp_line.salary_rule_id.not_computed_in_net: # Check if the rule must be computed in the 'Net Salary' or not.
                                        if amount > 0:
                                            amount -= abs(tmp_line.total)
                                        elif amount < 0:
                                            amount += abs(tmp_line.total)
                            if float_is_zero(amount, precision_digits=precision):
                                continue

                            debit_account_id = line.salary_rule_id.account_debit.id
                            credit_account_id = line.salary_rule_id.account_credit.id

                            #Lógica de ZUE - Obtener cuenta contable de acuerdo a la parametrización de la regla salarial                        
                            debit_third_id = line.partner_id.id
                            credit_third_id = line.partner_id.id
                            analytic_account_id = line.employee_id.analytic_account_id.id#line.salary_rule_id.analytic_account_id.id or line.slip_id.contract_id.analytic_account_id.id

                            for account_rule in line.salary_rule_id.salary_rule_accounting:
                                #Validar ubicación de trabajo
                                bool_work_location = False
                                if account_rule.work_location.id == slip.employee_id.address_id.id or account_rule.work_location.id == False:
                                    bool_work_location = True
                                #Validar compañia
                                bool_company = False
                                if account_rule.company.id == slip.employee_id.company_id.id or account_rule.company.id == False:
                                    bool_company = True
                                #Validar departamento
                                bool_department = False
                                if account_rule.department.id == slip.employee_id.department_id.id or account_rule.department.id == slip.employee_id.department_id.parent_id.id or account_rule.department.id == False:
                                    bool_department = True
                                
                                if bool_department and bool_company and bool_work_location:
                                    debit_account_id = account_rule.debit_account.id
                                    credit_account_id = account_rule.credit_account.id 

                                    #Tercero debito
                                    if account_rule.third_debit == 'entidad':
                                        debit_third_id = line.entity_id.partner_id
                                        #Recorrer entidades empleado
                                        for entity in slip.employee_id.social_security_entities:
                                            if entity.contrib_id.type_entities == 'eps' and line.code == 'SSOCIAL001': # SALUD 
                                                debit_third_id = entity.partner_id.partner_id
                                            if entity.contrib_id.type_entities == 'pension' and (line.code == 'SSOCIAL002' or line.code == 'SSOCIAL003' or line.code == 'SSOCIAL004'): # Pension
                                                debit_third_id = entity.partner_id.partner_id
                                            if entity.contrib_id.type_entities == 'subsistencia' and line.code == 'SSOCIAL003': # Subsistencia 
                                                debit_third_id = entity.partner_id.partner_id
                                            if entity.contrib_id.type_entities == 'solidaridad' and line.code == 'SSOCIAL004': # Solidaridad 
                                                debit_third_id = entity.partner_id.partner_id
                                        
                                    elif account_rule.third_debit == 'compañia':
                                        debit_third_id = slip.employee_id.company_id.partner_id
                                    elif account_rule.third_debit == 'empleado':
                                        debit_third_id = slip.employee_id.address_home_id

                                    #Tercero credito 
                                    if account_rule.third_credit == 'entidad':
                                        credit_third_id = line.entity_id.partner_id
                                        #Recorrer entidades empleado
                                        for entity in slip.employee_id.social_security_entities:
                                            if entity.contrib_id.type_entities == 'eps' and line.code == 'SSOCIAL001': # SALUD 
                                                credit_third_id = entity.partner_id.partner_id
                                            if entity.contrib_id.type_entities == 'pension' and (line.code == 'SSOCIAL002' or line.code == 'SSOCIAL003' or line.code == 'SSOCIAL004'): # Pension
                                                credit_third_id = entity.partner_id.partner_id
                                            if entity.contrib_id.type_entities == 'subsistencia' and line.code == 'SSOCIAL003': # Subsistencia 
                                                credit_third_id = entity.partner_id.partner_id
                                            if entity.contrib_id.type_entities == 'solidaridad' and line.code == 'SSOCIAL004': # Solidaridad 
                                                credit_third_id = entity.partner_id.partner_id
                                        
                                    elif account_rule.third_credit == 'compañia':
                                        credit_third_id = slip.employee_id.company_id.partner_id
                                    elif account_rule.third_credit == 'empleado':
                                        credit_third_id = slip.employee_id.address_home_id

                                    #Asignación de Tercero final y Cuenta analitica cuando la cuenta contable inicie por 4,5,6 o 7
                                    if debit_account_id:
                                        line.partner_id = debit_third_id
                                        if len(account_rule.debit_account) == 0:
                                            raise ValidationError(_('La regla salarial '+account_rule.salary_rule.name+' no esta bien parametrizada de forma contable, por favor verificar.'))           
                                        analytic_account_id = line.employee_id.analytic_account_id.id if account_rule.debit_account.code[0:1] in ['4','5','6','7'] else analytic_account_id                         
                                    elif credit_third_id:
                                        line.partner_id = credit_third_id
                                        if len(account_rule.credit_account) == 0:
                                            raise ValidationError(_('La regla salarial '+account_rule.salary_rule.name+' no esta bien parametrizada de forma contable, por favor verificar.'))              
                                        analytic_account_id = line.employee_id.analytic_account_id.id if account_rule.credit_account.code[0:1] in ['4','5','6','7']  else analytic_account_id                                                       

                            #Fin Lógica ZUE

                            if debit_account_id: # If the rule has a debit account.
                                debit = abs(amount) if abs(amount) > 0.0 else 0.0
                                credit = 0.0#-amount if amount < 0.0 else 0.0

                                debit_line = False#self._get_existing_lines(line_ids, line, debit_account_id, debit, credit)

                                if not debit_line:
                                    debit_line = self._prepare_line_values(line, debit_account_id, date, debit, credit, analytic_account_id)
                                    line_ids.append(debit_line)
                                else:
                                    debit_line['debit'] += debit
                                    debit_line['credit'] += credit

                            if credit_account_id: # If the rule has a credit account.
                                debit = 0.0#-amount if amount < 0.0 else 0.0
                                credit = abs(amount) if abs(amount) > 0.0 else 0.0
                                credit_line = False #self._get_existing_lines(line_ids, line, credit_account_id, debit, credit)

                                if not credit_line:
                                    credit_line = self._prepare_line_values(line, credit_account_id, date, debit, credit, analytic_account_id)
                                    line_ids.append(credit_line)
                                else:
                                    credit_line['debit'] += debit
                                    credit_line['credit'] += credit

                        for line_id in line_ids: # Get the debit and credit sum.
                            debit_sum += line_id['debit']
                            credit_sum += line_id['credit']

                        # The code below is called if there is an error in the balance between credit and debit sum.
                        if abs(debit_sum-credit_sum) > 10:
                            raise ValidationError(_('Verificar la dinamica contable de las reglas salariales, debido a que existe una diferencia de '+str(abs(debit_sum-credit_sum))+' pesos.'))

                        if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                            acc_id = slip.journal_id.default_credit_account_id.id
                            if not acc_id:
                                raise UserError(_('The Expense Journal "%s" has not properly configured the Credit Account!') % (slip.journal_id.name))
                            existing_adjustment_line = (
                                line_id for line_id in line_ids if line_id['name'] == _('Adjustment Entry')
                            )
                            adjust_credit = next(existing_adjustment_line, False)

                            if not adjust_credit:
                                adjust_credit = {
                                    'name': _('Adjustment Entry'),
                                    'partner_id': slip.employee_id.address_home_id.id,
                                    'account_id': acc_id,
                                    'journal_id': slip.journal_id.id,
                                    'date': date,
                                    'debit': 0.0,
                                    'credit': debit_sum - credit_sum,
                                    'analytic_account_id': slip.employee_id.analytic_account_id.id,
                                }
                                line_ids.append(adjust_credit)
                            else:
                                adjust_credit['credit'] = debit_sum - credit_sum

                        elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                            acc_id = slip.journal_id.default_debit_account_id.id
                            if not acc_id:
                                raise UserError(_('The Expense Journal "%s" has not properly configured the Debit Account!') % (slip.journal_id.name))
                            existing_adjustment_line = (
                                line_id for line_id in line_ids if line_id['name'] == _('Adjustment Entry')
                            )
                            adjust_debit = next(existing_adjustment_line, False)

                            if not adjust_debit:
                                adjust_debit = {
                                    'name': _('Adjustment Entry'),
                                    'partner_id': slip.employee_id.address_home_id.id,
                                    'account_id': acc_id,
                                    'journal_id': slip.journal_id.id,
                                    'date': date,
                                    'debit': credit_sum - debit_sum,
                                    'credit': 0.0,
                                    'analytic_account_id': slip.employee_id.analytic_account_id.id,
                                }
                                line_ids.append(adjust_debit)
                            else:
                                adjust_debit['debit'] = credit_sum - debit_sum

                        if settings_batch_account == '1':
                            # Add accounting lines in the move
                            move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
                            move = self.env['account.move'].create(move_dict)
                            slip.write({'move_id': move.id, 'date': date})

                if settings_batch_account == '0':
                    # Add accounting lines in the move
                    move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
                    move = self.env['account.move'].create(move_dict)
                    for slip in slip_mapped_data[journal_id][slip_date]:
                        slip.write({'move_id': move.id, 'date': date})
        return True
    
          
    