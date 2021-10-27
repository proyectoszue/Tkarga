# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from .browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips
from odoo.tools import float_compare, float_is_zero

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class hr_history_cesantias(models.Model):
    _name = 'hr.history.cesantias'
    _description = 'Historico de cesantias'
    
    employee_id = fields.Many2one('hr.employee', 'Empleado')
    employee_identification = fields.Char('Identificación empleado')
    initial_accrual_date = fields.Date('Fecha inicial de causación')
    final_accrual_date = fields.Date('Fecha final de causación')
    settlement_date = fields.Date('Fecha de liquidación')
    time = fields.Float('Tiempo')
    severance_value = fields.Float('Valor de cesantías')
    severance_interest_value = fields.Float('Valor intereses de cesantías')
    payslip = fields.Many2one('hr.payslip', 'Liquidación')
    contract_id = fields.Many2one('hr.contract', 'Contrato')
    base_value = fields.Float('Valor base')
    
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "Cesantias {} del {} al {}".format(record.employee_id.name, str(record.initial_accrual_date),str(record.final_accrual_date))))
        return result

    @api.model
    def create(self, vals):
        if vals.get('employee_identification'):
            obj_employee = self.env['hr.employee'].search([('identification_id', '=', vals.get('employee_identification'))])            
            vals['employee_id'] = obj_employee.id
        if vals.get('employee_id'):
            obj_employee = self.env['hr.employee'].search([('id', '=', vals.get('employee_id'))])            
            vals['employee_identification'] = obj_employee.identification_id            
        
        res = super(hr_history_cesantias, self).create(vals)
        return res

class Hr_payslip(models.Model):
    _inherit = 'hr.payslip'    
    
    #--------------------------------------------------LIQUIDACIÓN DE CESANTIAS---------------------------------------------------------#

    def _get_payslip_lines_cesantias(self,inherit_contrato=0,localdict=None):
        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
            localdict['categories'].dict[category.code] = localdict['categories'].dict.get(category.code, 0) + amount
            return localdict

        def _sum_salary_rule(localdict, rule, amount):
            localdict['rules_computed'].dict[rule.code] = localdict['rules_computed'].dict.get(rule.code, 0) + amount
            return localdict

        #Validar fecha inicial de causación
        if inherit_contrato==0:
            date_cesantias = self.contract_id.date_start     
            obj_cesantias = self.env['hr.history.cesantias'].search([('employee_id', '=', self.employee_id.id),('contract_id', '=', self.contract_id.id)])
            if obj_cesantias:
                for history in sorted(obj_cesantias, key=lambda x: x.final_accrual_date):
                    date_cesantias = history.final_accrual_date + timedelta(days=1) if history.final_accrual_date > date_cesantias else date_cesantias             
            self.date_from = date_cesantias if self.date_from < date_cesantias else self.date_from
        
        self.ensure_one()
        result = {}
        rules_dict = {}
        worked_days_dict = {line.code: line for line in self.worked_days_line_ids if line.code}
        inputs_dict = {line.code: line for line in self.input_line_ids if line.code}
        
        employee = self.employee_id
        contract = self.contract_id
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
                    'values_base_cesantias': 0,
                    'values_base_int_cesantias': 0,                    
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
                
                #Cuando es cesantias o intereses de cesantias, la regla retorna la base y el calculo se realiza a continuación
                amount_base = amount
                dias_trabajados = self.dias360(self.date_from, self.date_to)
                dias_ausencias =  sum([i.number_of_days for i in self.env['hr.leave'].search([('date_from','>=',self.date_from),('date_to','<=',self.date_to),('state','=','validate'),('employee_id','=',self.employee_id.id),('unpaid_absences','=',True)])])
                if inherit_contrato != 0:                    
                    dias_trabajados = self.dias360(self.date_cesantias, self.date_liquidacion)
                    dias_ausencias =  sum([i.number_of_days for i in self.env['hr.leave'].search([('date_from','>=',self.date_cesantias),('date_to','<=',self.date_liquidacion),('state','=','validate'),('employee_id','=',self.employee_id.id),('unpaid_absences','=',True)])])
                dias_liquidacion = dias_trabajados - dias_ausencias

                if rule.code == 'CESANTIAS':   
                    acumulados_promedio = (amount/dias_liquidacion) * 30
                    wage = contract.wage
                    auxtransporte = annual_parameters.transportation_assistance_monthly
                    auxtransporte_tope = annual_parameters.top_max_transportation_assistance
                    if wage <= auxtransporte_tope:
                        amount_base = round(wage + auxtransporte + acumulados_promedio, 0)
                    else:
                        amount_base = round(wage + acumulados_promedio, 0)              

                    #amount = round(amount_base * dias_liquidacion / 360, 0)
                    amount = round(amount_base / 360, 0)
                    qty = dias_liquidacion

                if rule.code == 'INTCESANTIAS':
                    #amount = round(amount * dias_liquidacion * 0.12 / 360, 0)
                    amount = round(amount / 360, 0)
                    qty = dias_liquidacion
                    rate = 12

                amount = round(amount,0) #Se redondean los decimales de todas las reglas
                #check if there is already a rule computed with that code
                previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                #set/overwrite the amount computed for this rule in the localdict
                tot_rule = round(amount * qty * rate / 100.0,0) + previous_amount
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
                        'slip_id': self.id,
                    }
        
        if inherit_contrato == 0:
            return result.values()  
        else:
            return localdict,result           