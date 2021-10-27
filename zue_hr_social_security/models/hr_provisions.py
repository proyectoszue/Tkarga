# -*- coding: utf-8 -*-

from logging import exception
from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


import odoo
import threading

class hr_executing_provisions_details(models.Model):
    _name = 'hr.executing.provisions.details'
    _description = 'Ejecución Provisiones empleados detalle'


    executing_provisions_id = fields.Many2one('hr.executing.provisions',string='Ejecución Provisiones')
    provision = fields.Selection([('cesantias', 'Cesantías'),
                                    ('intcesantias', 'Intereses de cesantías'),
                                    ('prima', 'Prima'),
                                    ('vacaciones', 'Vacaciones')], string='Provisión', required=True)
    employee_id = fields.Many2one('hr.employee', 'Empleado', required=True)
    contract_id = fields.Many2one('hr.contract', 'Contrato', required=True)
    analytic_account_id = fields.Many2one(related='contract_id.analytic_account_id',string='Cuenta analítica', store=True)
    value_wage = fields.Float('Salario')
    value_base = fields.Float('Base')
    time = fields.Float('Unidades')
    value_balance = fields.Float('Saldo')
    value_payments = fields.Float('Pagos realizados')
    amount = fields.Float('Valor liquidado')

class hr_executing_provisions(models.Model):
    _name = 'hr.executing.provisions'
    _description = 'Ejecución Provisiones empleados'

    year = fields.Integer('Año', required=True)
    month = fields.Selection([('1', 'Enero'),
                            ('2', 'Febrero'),
                            ('3', 'Marzo'),
                            ('4', 'Abril'),
                            ('5', 'Mayo'),
                            ('6', 'Junio'),
                            ('7', 'Julio'),
                            ('8', 'Agosto'),
                            ('9', 'Septiembre'),
                            ('10', 'Octubre'),
                            ('11', 'Noviembre'),
                            ('12', 'Diciembre')        
                            ], string='Mes', required=True)
    date_end = fields.Date('Fecha')
    #employee_ids = fields.Many2many('hr.employee', string='Empleados', ondelete='restrict', required=True)
    details_ids = fields.One2many('hr.executing.provisions.details', 'executing_provisions_id',string='Ejecución')
    time_process = fields.Char(string='Tiempo ejecución')
    observations = fields.Text('Observaciones')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('done', 'Realizado'),
        ('accounting', 'Contabilizado'),
    ], string='Estado', default='draft')
    move_id = fields.Many2one('account.move',string='Contabilidad')

    company_id = fields.Many2one('res.company', string='Compañía', readonly=True, required=True,
        default=lambda self: self.env.company)

    _sql_constraints = [('provisions_period_uniq', 'unique(company_id,year,month)', 'El periodo seleccionado ya esta registrado para esta compañía, por favor verificar.')]

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "Periodo {}-{}".format(record.month,str(record.year))))
        return result
  
    def executing_provisions_thread(self,date_start,date_end,struct_vacaciones,struct_prima,struct_cesantias,contracts):
        with odoo.api.Environment.manage():
            registry = odoo.registry(self._cr.dbname)
            with registry.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                
                for obj_contract in contracts:
                    contract = env['hr.contract'].search([('id', '=', obj_contract.id)])
                    try:
                        result_cesantias = {}
                        result_prima = {}
                        result_vac = {}

                        #Obtener fecha cesantias
                        date_cesantias = contract.date_start     
                        obj_cesantias = env['hr.history.cesantias'].search([('employee_id', '=', contract.employee_id.id),('contract_id', '=', contract.id)])
                        if obj_cesantias:
                            for history in sorted(obj_cesantias, key=lambda x: x.final_accrual_date):
                                date_cesantias = history.final_accrual_date + timedelta(days=1) if history.final_accrual_date > date_cesantias else date_cesantias             

                        #Obtener fecha prima
                        date_prima = contract.date_start     
                        obj_prima = env['hr.history.prima'].search([('employee_id', '=', contract.employee_id.id),('contract_id', '=', contract.id)])
                        if obj_prima:
                            for history in sorted(obj_prima, key=lambda x: x.final_accrual_date):
                                date_prima = history.final_accrual_date + timedelta(days=1) if history.final_accrual_date > date_prima else date_prima                                   

                        #Obtener fecha vacaciones
                        date_vacation = contract.date_start     
                        obj_vacation = env['hr.vacation'].search([('employee_id', '=', contract.employee_id.id),('contract_id', '=', contract.id)])
                        if obj_vacation:
                            for history in sorted(obj_vacation, key=lambda x: x.final_accrual_date):
                                date_vacation = history.final_accrual_date + timedelta(days=1) if history.final_accrual_date > date_vacation else date_vacation             

                        #Simular liquidación de cesantias
                        Payslip = env['hr.payslip']
                        default_values = Payslip.default_get(Payslip.fields_get())
                        values = dict(default_values, **{
                                'employee_id': contract.employee_id.id,
                                'date_cesantias':date_cesantias,
                                'date_prima': date_prima,
                                'date_vacaciones':date_vacation,
                                'date_from': date_start,
                                'date_to': date_end,
                                'date_liquidacion':date_end,
                                'contract_id': contract.id,
                                'struct_id': struct_cesantias.id
                            })
                        payslip = env['hr.payslip'].new(values)
                        payslip._onchange_employee()
                        values = payslip._convert_to_write(payslip._cache)
                        obj_provision = Payslip.create(values)
                        
                        if contract.contract_type != 'aprendizaje':
                            if contract.modality_salary != 'integral':
                                #Cesantias
                                obj_provision.write({'struct_id': struct_cesantias.id})
                                localdict,result_cesantias = obj_provision._get_payslip_lines_cesantias(inherit_contrato=1)
                                #Prima
                                obj_provision.write({'struct_id': struct_prima.id})
                                localdict,result_prima = obj_provision._get_payslip_lines_prima(inherit_contrato=1)
                            #Vacaciones
                            obj_provision.write({'struct_id': struct_vacaciones.id})
                            localdict,result_vac = obj_provision._get_payslip_lines_vacation(inherit_contrato=1)


                        obj_provision.action_payslip_cancel()
                        obj_provision.unlink()
                        
                        #Guardar resultado
                        result_finally = {**result_cesantias,**result_prima,**result_vac}   
                        
                        #Restar las provisiones anteriores
                        for line in result_finally.values():
                            if line['code'] in ['CESANTIAS','INTCESANTIAS','PRIMA','VACCONTRATO']:
                                if line['code'] == 'CESANTIAS':
                                    provision = 'cesantias'
                                if line['code'] == 'INTCESANTIAS':
                                    provision = 'intcesantias'
                                if line['code'] == 'PRIMA':
                                    provision = 'prima'
                                if line['code'] == 'VACCONTRATO':
                                    provision = 'vacaciones'

                                #Obtener provisiones anteriores que afectan el valor
                                obj_provisions = env['hr.executing.provisions.details']
                                executing_provisions = env['hr.executing.provisions.details'].search([('executing_provisions_id.state','in',['done','accounting']),('executing_provisions_id','!=',self.id),('executing_provisions_id.date_end','<',date_end),('provision','=',provision),('contract_id','=',contract.id)])
                                value_balance = sum([i.amount for i in obj_provisions.browse(executing_provisions.ids)])
                                
                                #Guardar valores
                                values_details = {
                                    'executing_provisions_id':self.id,
                                    'provision': provision,
                                    'employee_id': contract.employee_id.id,
                                    'contract_id': contract.id,
                                    'value_wage': contract.wage,
                                    'value_base': line['amount_base'],
                                    'time': line['quantity'],
                                    'value_balance': round((line['amount'] * line['quantity'] * line['rate'])/100,0) - value_balance,
                                    'value_payments': 0,
                                    'amount': round((line['amount'] * line['quantity'] * line['rate'])/100,0)
                                } 
                                env['hr.executing.provisions.details'].create(values_details)
                    
                    except Exception as e:
                        msg = 'ERROR: '+str(e.args[0])+' en el contrato '+contract.name+'.'
                        if self.observations:
                            self.observations = self.observations + '\n' + msg
                        else:
                            self.observations = msg

    def executing_provisions(self):
        #Eliminar ejecución
        self.env['hr.executing.provisions.details'].search([('executing_provisions_id','=',self.id)]).unlink()

        #Obtener fechas del periodo seleccionado
        date_start = '01/'+str(self.month)+'/'+str(self.year)
        try:
            date_start = datetime.strptime(date_start, '%d/%m/%Y')       

            date_end = date_start + relativedelta(months=1)
            date_end = date_end - timedelta(days=1)
            
            date_start = date_start.date()
            date_end = date_end.date()
        except:
            raise UserError(_('El año digitado es invalido, por favor verificar.'))  


        #Obtener estructuras
        struct_cesantias = self.env['hr.payroll.structure'].search([('process', '=', 'cesantias_e_intereses')])
        struct_prima = self.env['hr.payroll.structure'].search([('process', '=', 'prima')])
        struct_vacaciones = self.env['hr.payroll.structure'].search([('process', '=', 'vacaciones')])

        #Obtener contratos activos
        obj_contracts = self.env['hr.contract'].search([('state', '=', 'open'), ('date_start','<=', date_start), ('company_id', '=', self.env.company.id)])
        
        #Guardo los contratos en lotes de a 20
        contracts_array, i, j = [], 0 , 20            
        while i <= len(obj_contracts):                
            contracts_array.append(obj_contracts[i:j])
            i = j
            j += 20   

        #Los lotes anteriores, los separo en los de 5, para ejecutar un maximo de 5 hilos
        contracts_array_def, i, j = [], 0 , 5            
        while i <= len(contracts_array):                
            contracts_array_def.append(contracts_array[i:j])
            i = j
            j += 5  

        #----------------------------Recorrer contratos por multihilos
        date_start_process = datetime.now()
        date_finally_process = datetime.now()
        i = 1
        for contracts in contracts_array_def:
            array_thread = []
            for contract in contracts:
                t = threading.Thread(target=self.executing_provisions_thread, args=(date_start,date_end,struct_vacaciones,struct_prima,struct_cesantias,contract,))                
                t.start()
                array_thread.append(t)
                i += 1   

            for hilo in array_thread:
                while hilo.is_alive():
                    date_finally_process = datetime.now()  


        time_process = date_finally_process - date_start_process
        time_process = time_process.seconds / 60

        self.time_process = 'El proceso se demoro '+str(time_process)+' minutos.'
        self.date_end = date_end
        self.state = 'done'

    def get_accounting(self):
        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        date = self.date_end
        move_dict = {
            'narration': '',
            'ref': f"Provisión - {date.strftime('%B %Y')}",
            'journal_id': False,
            'date': date,
        }

        for slip in self.details_ids:
            # Lógica de ZUE - Obtener cuenta contable de acuerdo a la parametrización contable
            debit_third_id = slip.employee_id.address_home_id
            credit_third_id = slip.employee_id.address_home_id
            analytic_account_id = slip.employee_id.analytic_account_id

            obj_closing = self.env['hr.closing.configuration.header'].search([('process','=',slip.provision)])

            for closing in obj_closing:
                move_dict['journal_id'] = closing.journal_id.id
                for account_rule in closing.detail_ids:
                    debit_account_id = False
                    credit_account_id = False
                    # Validar ubicación de trabajo
                    bool_work_location = False
                    if account_rule.work_location.id == slip.employee_id.address_id.id or account_rule.work_location.id == False:
                        bool_work_location = True
                    # Validar compañia
                    bool_company = False
                    if account_rule.company.id == slip.employee_id.company_id.id or account_rule.company.id == False:
                        bool_company = True
                    # Validar departamento
                    bool_department = False
                    if account_rule.department.id == slip.employee_id.department_id.id or account_rule.department.id == slip.employee_id.department_id.parent_id.id or account_rule.department.id == False:
                        bool_department = True

                    if bool_department and bool_company and bool_work_location:
                        debit_account_id = account_rule.debit_account
                        credit_account_id = account_rule.credit_account

                    # Tercero debito
                    if account_rule.third_debit == 'entidad':
                        pass
                        #debit_third_id = line.entity_id.partner_id
                    elif account_rule.third_debit == 'compañia':
                        debit_third_id = slip.employee_id.company_id.partner_id
                    elif account_rule.third_debit == 'empleado':
                        debit_third_id = slip.employee_id.address_home_id

                    # Tercero credito
                    if account_rule.third_credit == 'entidad':
                        pass
                        #credit_third_id = line.entity_id.partner_id
                    elif account_rule.third_credit == 'compañia':
                        credit_third_id = slip.employee_id.company_id.partner_id
                    elif account_rule.third_credit == 'empleado':
                        credit_third_id = slip.employee_id.address_home_id

                    #Valor
                    amount = slip.value_balance if slip.value_balance != 0 else slip.amount

                    if debit_account_id:
                        debit = abs(amount) if amount >= 0.0 else 0.0
                        credit = abs(amount) if amount < 0.0 else 0.0
                        debit_line = {
                            'name': slip.provision.upper(),
                            'partner_id': debit_third_id.id,# if debit > 0 else credit_third_id.id,
                            'account_id': debit_account_id.id,# if debit > 0 else credit_account_id.id,
                            'journal_id': closing.journal_id.id,
                            'date': date,
                            'debit': debit,
                            'credit': credit,
                            'analytic_account_id': analytic_account_id.id,
                        }
                        line_ids.append(debit_line)

                    if credit_account_id:
                        debit = abs(amount) if amount < 0.0 else 0.0
                        credit = abs(amount) if amount >= 0.0 else 0.0

                        credit_line = {
                            'name': slip.provision.upper(),
                            'partner_id': credit_third_id.id,
                            'account_id': credit_account_id.id,
                            'journal_id': closing.journal_id.id,
                            'date': date,
                            'debit': debit,
                            'credit': credit,
                            'analytic_account_id': analytic_account_id.id,
                        }
                        line_ids.append(credit_line)

        move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
        move = self.env['account.move'].create(move_dict)
        self.write({'move_id': move.id, 'state': 'accounting'})

    def cancel_process(self):
        #Eliminar ejecución
        self.env['hr.executing.provisions.details'].search([('executing_provisions_id', '=', self.id)]).unlink()
        return self.write({'state':'draft','time_process':''})

    def restart_accounting(self):
        if self.move_id:
            if self.move_id.state != 'draft':
                raise ValidationError(_('No se puede reversar el movimiento contable debido a que su estado es diferente de borrador.'))
            self.move_id.unlink()
        return self.write({'state': 'done'})

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise ValidationError(_('No se puede eliminar la provisión debido a que su estado es diferente de borrador.'))
        return super(hr_executing_provisions, self).unlink()

