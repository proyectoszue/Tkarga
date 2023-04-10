# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from .browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips
from odoo.tools import float_compare, float_is_zero

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class hr_history_prima(models.Model):
    _name = 'hr.history.prima'
    _description = 'Historico de prima'
    
    employee_id = fields.Many2one('hr.employee', 'Empleado')
    employee_identification = fields.Char('Identificación empleado')
    initial_accrual_date = fields.Date('Fecha inicial de causación')
    final_accrual_date = fields.Date('Fecha final de causación')
    settlement_date = fields.Date('Fecha de liquidación')
    time = fields.Float('Tiempo')
    base_value = fields.Float('Valor base')
    bonus_value = fields.Float('Valor de prima')
    payslip = fields.Many2one('hr.payslip', 'Liquidación')
    contract_id = fields.Many2one('hr.contract', 'Contrato')
    
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "Prima {} del {} al {}".format(record.employee_id.name, str(record.initial_accrual_date),str(record.final_accrual_date))))
        return result

    @api.model
    def create(self, vals):
        if vals.get('employee_identification'):
            obj_employee = self.env['hr.employee'].search([('identification_id', '=', vals.get('employee_identification'))])            
            vals['employee_id'] = obj_employee.id
        if vals.get('employee_id'):
            obj_employee = self.env['hr.employee'].search([('id', '=', vals.get('employee_id'))])            
            vals['employee_identification'] = obj_employee.identification_id            
        
        res = super(hr_history_prima, self).create(vals)
        return res
class Hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    prima_run_reverse_id = fields.Many2one('hr.payslip.run', string='Lote de prima a ajustar')
    prima_payslip_reverse_id = fields.Many2one('hr.payslip', string='Prima a ajustar', domain="[('employee_id', '=', employee_id)]")

    #--------------------------------------------------LIQUIDACIÓN DE PRIMA---------------------------------------------------------#

    def _get_payslip_lines_prima(self,inherit_contrato=0,localdict=None):
        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
            localdict['categories'].dict[category.code] = localdict['categories'].dict.get(category.code, 0) + amount
            return localdict

        def _sum_salary_rule(localdict, rule, amount):
            localdict['rules_computed'].dict[rule.code] = localdict['rules_computed'].dict.get(rule.code, 0) + amount
            return localdict

        #Validar si es ajuste de prima
        if self.prima_run_reverse_id and not self.prima_payslip_reverse_id:
            prima_payslip_reverse_obj = self.env['hr.payslip'].search(
                [('payslip_run_id', '=', self.prima_run_reverse_id.id),
                 ('employee_id', '=', self.employee_id.id)], limit=1)
            if len(prima_payslip_reverse_obj) == 1:
                self.prima_payslip_reverse_id = prima_payslip_reverse_obj.id

        #Validar fecha inicial de causación
        if inherit_contrato==0:
            date_prima = self.contract_id.date_start     
            obj_prima = self.env['hr.history.prima'].search([('employee_id', '=', self.employee_id.id),('contract_id', '=', self.contract_id.id)])
            if obj_prima:
                for history in sorted(obj_prima, key=lambda x: x.final_accrual_date):
                    if history.payslip != self.prima_payslip_reverse_id:
                        date_prima = history.final_accrual_date + timedelta(days=1) if history.final_accrual_date > date_prima else date_prima
            self.date_from = date_prima if self.date_from < date_prima else self.date_from

        self.ensure_one()
        result = {}
        rules_dict = {}
        worked_days_dict = {line.code: line for line in self.worked_days_line_ids if line.code}
        inputs_dict = {line.code: line for line in self.input_line_ids if line.code}
        round_payroll = bool(self.env['ir.config_parameter'].sudo().get_param('zue_hr_payroll.round_payroll')) or False
        prima_salary_take = bool(self.env['ir.config_parameter'].sudo().get_param('zue_hr_payroll.prima_salary_take')) or False
        
        employee = self.employee_id
        contract = self.contract_id

        if contract.modality_salary == 'integral' or contract.contract_type == 'aprendizaje':
            return result.values()

        year = self.date_from.year
        annual_parameters = self.env['hr.annual.parameters'].search([('year', '=', year)])

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
                    'employee': employee,
                    'contract': contract,
                    'annual_parameters': annual_parameters,
                    'inherit_contrato':inherit_contrato,   
                    'values_base_prima': 0,                 
                }
            }
        else:
            localdict.update({
                'inherit_contrato':inherit_contrato,})        
        
        #Ejecutar las reglas salariales y su respectiva lógica
        for rule in sorted(self.struct_id.rule_ids, key=lambda x: x.sequence):
            localdict.update({                
                'result': None,
                'result_qty': 1.0,
                'result_rate': 100})
            if rule._satisfy_condition(localdict):                
                amount, qty, rate = rule._compute_rule(localdict)
                dias_ausencias, amount_base = 0, 0

                if rule.code == 'PRIMA':
                    amount_base = amount
                    dias_trabajados = self.dias360(self.date_from, self.date_to)
                    dias_ausencias =  sum([i.number_of_days for i in self.env['hr.leave'].search([('date_from','>=',self.date_from),('date_to','<=',self.date_to),('state','=','validate'),('employee_id','=',self.employee_id.id),('unpaid_absences','=',True)])])
                    dias_ausencias += sum([i.days for i in self.env['hr.absence.history'].search([('star_date', '>=', self.date_from), ('end_date', '<=', self.date_to),('employee_id', '=', self.employee_id.id), ('leave_type_id.unpaid_absences', '=', True)])])
                    if inherit_contrato != 0:
                        dias_trabajados = self.dias360(self.date_prima, self.date_liquidacion)
                        dias_ausencias =  sum([i.number_of_days for i in self.env['hr.leave'].search([('date_from','>=',self.date_prima),('date_to','<=',self.date_liquidacion),('state','=','validate'),('employee_id','=',self.employee_id.id),('unpaid_absences','=',True)])])
                        dias_ausencias += sum([i.days for i in self.env['hr.absence.history'].search([('star_date', '>=', self.date_prima), ('end_date', '<=', self.date_liquidacion),('employee_id', '=', self.employee_id.id),('leave_type_id.unpaid_absences', '=', True)])])
                    dias_liquidacion = dias_trabajados - dias_ausencias

                    if dias_trabajados != 0:
                        #if dias_trabajados <= 30:
                        #    acumulados_promedio = (amount/dias_trabajados) * dias_trabajados
                        #else:
                        acumulados_promedio = (amount / dias_trabajados) * 30  # dias_liquidacion
                    else:
                        acumulados_promedio = 0
                    wage = contract.wage
                    initial_process_date = self.date_prima if inherit_contrato != 0 else self.date_from
                    end_process_date = self.date_liquidacion if inherit_contrato != 0 else self.date_to
                    obj_wage = self.env['hr.contract.change.wage'].search([('contract_id', '=', contract.id), ('date_start', '>=', initial_process_date), ('date_start', '<=', end_process_date)])
                    obj_wage_history = self.env['hr.contract.change.wage'].search([('contract_id', '=', contract.id)])
                    if prima_salary_take and len(obj_wage) > 0 and len(obj_wage_history) > 1:
                        wage_average = 0
                        while initial_process_date <= end_process_date:
                            if initial_process_date.day != 31:
                                if initial_process_date.month == 2 and  initial_process_date.day == 28 and (initial_process_date + timedelta(days=1)).day != 29:
                                    wage_average += (contract.get_wage_in_date(initial_process_date) / 30)*3
                                elif initial_process_date.month == 2 and initial_process_date.day == 29:
                                    wage_average += (contract.get_wage_in_date(initial_process_date) / 30)*2
                                else:
                                    wage_average += contract.get_wage_in_date(initial_process_date)/30
                            initial_process_date = initial_process_date + timedelta(days=1)
                        if dias_trabajados != 0:
                            wage = contract.wage if wage_average == 0 else (wage_average/dias_trabajados)*30
                        else:
                            wage = 0
                    auxtransporte = annual_parameters.transportation_assistance_monthly
                    auxtransporte_tope = annual_parameters.top_max_transportation_assistance
                    if wage <= auxtransporte_tope:
                        amount_base = round(wage + auxtransporte + acumulados_promedio, 0) if round_payroll == False else wage + auxtransporte + acumulados_promedio
                    else:
                        amount_base = round(wage + acumulados_promedio, 0) if round_payroll == False else wage + acumulados_promedio

                    #amount = round(amount_base * dias_liquidacion / 360, 0)
                    amount = round(amount_base / 360,0) if round_payroll == False else amount_base / 360
                    if self.prima_payslip_reverse_id:
                        value_reverse = self.prima_payslip_reverse_id.line_ids.filtered(lambda line: line.code == 'PRIMA').amount
                        amount = round(amount-value_reverse,0)
                    qty = dias_liquidacion

                #amount = round(amount,0) #Se redondean los decimales de todas las reglas
                #check if there is already a rule computed with that code
                previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                #set/overwrite the amount computed for this rule in the localdict
                tot_rule = (amount * qty * rate / 100.0) + previous_amount
                localdict[rule.code] = tot_rule
                rules_dict[rule.code] = rule
                # sum the amount for its salary category
                localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount) 
                localdict = _sum_salary_rule(localdict, rule, tot_rule)
                # create/overwrite the rule in the temporary results
                if amount != 0:                    
                    result[rule.code] = {
                        'sequence': rule.sequence,
                        'code': rule.code,
                        'name': rule.name,
                        'note': rule.note,
                        'salary_rule_id': rule.id,
                        'contract_id': contract.id,
                        'employee_id': employee.id,
                        'amount_base': amount_base,
                        'amount': amount,
                        'quantity': qty,
                        'rate': rate,
                        'days_unpaid_absences':dias_ausencias,
                        'slip_id': self.id,
                    }

        # Ejecutar reglas salariales de la nómina de pago regular
        if inherit_contrato == 0:
            obj_struct_payroll = self.env['hr.payroll.structure'].search(
                [('regular_pay', '=', True), ('process', '=', 'nomina')])
            struct_original = self.struct_id.id
            self.struct_id = obj_struct_payroll.id
            result_payroll = self._get_payslip_lines(inherit_prima=1, localdict=localdict)
            self.struct_id = struct_original

            result_finally = {**result, **result_payroll}
            # Retornar resultado final de la liquidación de nómina
            return result_finally.values()
        else:
            return localdict, result
