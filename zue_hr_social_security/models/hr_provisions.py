# -*- coding: utf-8 -*-

from logging import exception
from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import math
import odoo

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
    analytic_account_id = fields.Many2one('account.analytic.account', string='Cuenta analítica')
    value_wage = fields.Float('Salario')
    value_base = fields.Float('Base')
    time = fields.Float('Unidades')
    value_balance = fields.Float('Valor Provisión Mes')
    value_payments = fields.Float('Pagos realizados')
    amount = fields.Float('Valor liquidado')
    current_payable_value = fields.Float('Valor a Pagar Actual')

class hr_executing_provisions(models.Model):
    _name = 'hr.executing.provisions'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Ejecución Provisiones empleados'

    year = fields.Integer('Año', required=True, tracking=True)
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
                            ], string='Mes', required=True, tracking=True)
    date_end = fields.Date('Fecha', tracking=True)
    #employee_ids = fields.Many2many('hr.employee', string='Empleados', ondelete='restrict', required=True)
    details_ids = fields.One2many('hr.executing.provisions.details', 'executing_provisions_id',string='Ejecución', tracking=True)
    time_process_float = fields.Float(string='Tiempo ejecución float', tracking=True)
    time_process = fields.Char(string='Tiempo ejecución', tracking=True)
    observations = fields.Text('Observaciones', tracking=True)
    employees_per_batch = fields.Integer(string='# de Empleados por lote a ejecutar', default=100, required=True)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('done', 'Realizado'),
        ('accounting', 'Contabilizado'),
    ], string='Estado', default='draft', tracking=True)
    move_id = fields.Many2one('account.move',string='Contabilidad', tracking=True)

    company_id = fields.Many2one('res.company', string='Compañía', readonly=True, required=True,
        default=lambda self: self.env.company, tracking=True)
    errors_provisions_ids = fields.One2many('hr.errors.provisions', 'executing_provisions_id', string='Errores')

    _sql_constraints = [('provisions_period_uniq', 'unique(company_id,year,month)', 'El periodo seleccionado ya esta registrado para esta compañía, por favor verificar.')]

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "Periodo {}-{}".format(record.month,str(record.year))))
        return result

    def executing_provisions_savepoint(self,date_start,date_end,struct_vacaciones,struct_prima,struct_cesantias,struct_intcesantias,contracts):
        with self.env.cr.savepoint():
            for obj_contract in contracts:
                contract = self.env['hr.contract'].search([('id', '=', obj_contract.id)])
                try:
                    result_cesantias = {}
                    result_intcesantias = {}
                    result_prima = {}
                    result_vac = {}
                    retirement_date = contract.retirement_date
                    date_end_without_31 = date_end - timedelta(days=1) if date_end.day == 31 else date_end

                    #Obtener fecha cesantias
                    date_cesantias = contract.date_start
                    if retirement_date == False:
                        obj_cesantias = self.env['hr.history.cesantias'].search([('employee_id', '=', contract.employee_id.id),('contract_id', '=', contract.id),('initial_accrual_date', '<', date_end),('initial_accrual_date', '<', date_end_without_31),('final_accrual_date','<',date_end),('final_accrual_date','<',date_end_without_31)])
                    else:
                        if retirement_date >= date_end:
                            obj_cesantias = self.env['hr.history.cesantias'].search([('employee_id', '=', contract.employee_id.id), ('contract_id', '=', contract.id),('initial_accrual_date', '<', date_end),('initial_accrual_date', '<', date_end_without_31),('final_accrual_date', '<', date_end),('final_accrual_date', '<', date_end_without_31)])
                        else:
                            obj_cesantias = self.env['hr.history.cesantias'].search([('employee_id', '=', contract.employee_id.id), ('contract_id', '=', contract.id),('initial_accrual_date', '<', retirement_date),('final_accrual_date', '<', retirement_date)])
                    if obj_cesantias:
                        for history in sorted(obj_cesantias, key=lambda x: x.final_accrual_date):
                            date_cesantias = history.final_accrual_date + timedelta(days=1) if history.final_accrual_date > date_cesantias else date_cesantias

                    #Obtener fecha prima
                    date_prima = contract.date_start
                    if retirement_date == False:
                        obj_prima = self.env['hr.history.prima'].search([('employee_id', '=', contract.employee_id.id),('contract_id', '=', contract.id),('initial_accrual_date', '<', date_end),('initial_accrual_date', '<', date_end_without_31),('final_accrual_date','<',date_end),('final_accrual_date','<',date_end_without_31)])
                    else:
                        if retirement_date >= date_end:
                            obj_prima = self.env['hr.history.prima'].search([('employee_id', '=', contract.employee_id.id), ('contract_id', '=', contract.id),('initial_accrual_date', '<', date_end),('initial_accrual_date', '<', date_end_without_31),('final_accrual_date', '<', date_end),('final_accrual_date', '<', date_end_without_31)])
                        else:
                            obj_prima = self.env['hr.history.prima'].search([('employee_id', '=', contract.employee_id.id), ('contract_id', '=', contract.id),('initial_accrual_date', '<', retirement_date),('final_accrual_date', '<', retirement_date)])
                    if obj_prima:
                        for history in sorted(obj_prima, key=lambda x: x.final_accrual_date):
                            date_prima = history.final_accrual_date + timedelta(days=1) if history.final_accrual_date > date_prima else date_prima

                    #Obtener fecha vacaciones
                    date_vacation = contract.date_start
                    if retirement_date == False:
                        obj_vacation = self.env['hr.vacation'].search([('employee_id', '=', contract.employee_id.id), ('contract_id', '=', contract.id), ('departure_date', '<=', date_end)])
                    else:
                        if retirement_date >= date_end:
                            obj_vacation = self.env['hr.vacation'].search([('employee_id', '=', contract.employee_id.id), ('contract_id', '=', contract.id),('departure_date', '<=', date_end)])
                        else:
                            obj_vacation = self.env['hr.vacation'].search([('employee_id', '=', contract.employee_id.id), ('contract_id', '=', contract.id),('departure_date', '<=', retirement_date)])
                    if obj_vacation:
                        for history in sorted(obj_vacation, key=lambda x: x.final_accrual_date):
                            if history.leave_id:
                                if history.leave_id.holiday_status_id.unpaid_absences == False:
                                    date_vacation = history.final_accrual_date + timedelta(days=1) if history.final_accrual_date > date_vacation else date_vacation
                            else:
                                date_vacation = history.final_accrual_date + timedelta(days=1) if history.final_accrual_date > date_vacation else date_vacation

                    if retirement_date == False:
                        date_to_process = date_end_without_31
                    else:
                        date_to_process = date_end_without_31 if retirement_date >= date_end_without_31 else retirement_date

                        date_cesantias = date_cesantias if retirement_date >= date_cesantias else retirement_date
                        date_prima = date_prima if retirement_date >= date_prima else retirement_date
                        date_vacation = date_vacation if retirement_date >= date_vacation else retirement_date

                    #Simular liquidación de contrato
                    obj_liq_contract_exists = self.env['hr.payslip'].search(
                        [('state', '=', 'done'), ('contract_id', '=', contract.id), ('struct_id.process', '=', 'contrato'),
                         ('date_liquidacion', '>=', date_start), ('date_liquidacion', '<=', date_end)], limit=1)
                    obj_liq_prima_cesantias_exists = self.env['hr.payslip'].search(
                        [('state', '=', 'done'), ('contract_id', '=', contract.id),
                         ('struct_id', 'in', [struct_prima.id,struct_cesantias.id,struct_intcesantias.id]),
                         ('date_to', '>=', date_start), ('date_to', '<=', date_end)], limit=1)
                    if len(obj_liq_contract_exists) == 1 and len(obj_liq_prima_cesantias_exists) == 0:
                        result_finally = {}
                        for liq in obj_liq_contract_exists.line_ids:
                            liq_dict = {liq.copy_data()[0]['code']:liq.copy_data()[0]}
                            result_finally = {**result_finally, **liq_dict}
                    else:
                        Payslip = self.env['hr.payslip']
                        default_values = Payslip.default_get(Payslip.fields_get())
                        values = dict(default_values, **{
                                'employee_id': contract.employee_id.id,
                                'date_cesantias':date_cesantias,
                                'date_prima': date_prima,
                                'date_vacaciones':date_vacation,
                                'date_from': date_start,
                                'date_to': date_to_process,
                                'date_liquidacion':date_to_process,
                                'contract_id': contract.id,
                                'struct_id': struct_cesantias.id
                            })
                        payslip = self.env['hr.payslip'].new(values)
                        payslip._onchange_employee()
                        values = payslip._convert_to_write(payslip._cache)
                        obj_provision = Payslip.create(values)

                        # Obtener parametrización de cotizantes
                        # Obtener tipo y subtipo de cotizante de acuerdo a la fecha
                        datetime_start = datetime.combine(date_start, datetime.min.time())
                        obj_tipo_coti = contract.employee_id.tipo_coti_id
                        obj_subtipo_coti = contract.employee_id.subtipo_coti_id
                        obj_history_social_security = self.env['zue.hr.history.employee.social.security'].search([('z_employee_id.id', '=', contract.employee_id.id)])
                        if len(obj_history_social_security) > 0:
                            for history_ss in sorted(obj_history_social_security, key=lambda x: x.z_date_change):
                                if contract.state != 'open' and contract.id != contract.employee_id.contract_id.id:
                                    if contract.date_start >= history_ss.z_date_change and contract.employee_id.contract_id.date_start <= history_ss.z_date_change and date_start >= history_ss.z_date_change and date_end <= history_ss.z_date_change:
                                        obj_tipo_coti = history_ss.z_tipo_coti_id
                                        obj_subtipo_coti = history_ss.z_subtipo_coti_id
                                        break
                                else:
                                    if datetime_start.date() < history_ss.z_date_change:
                                        obj_tipo_coti = history_ss.z_tipo_coti_id
                                        obj_subtipo_coti = history_ss.z_subtipo_coti_id
                                        break

                        obj_tipo_coti = contract.employee_id.tipo_coti_id if len(obj_tipo_coti) == 0 else obj_tipo_coti
                        obj_subtipo_coti = contract.employee_id.subtipo_coti_id if len(obj_subtipo_coti) == 0 else obj_subtipo_coti
                        obj_parameterization_contributors = self.env['hr.parameterization.of.contributors'].search(
                            [('type_of_contributor', '=', obj_tipo_coti.id),
                             ('contributor_subtype', '=', obj_subtipo_coti.id)], limit=1)

                        if len(obj_parameterization_contributors) > 0 and obj_parameterization_contributors.liquidated_provisions:
                            if contract.modality_salary != 'integral':
                                #Cesantias
                                obj_provision.write({'struct_id': struct_cesantias.id})
                                localdict,result_cesantias = obj_provision._get_payslip_lines_cesantias(inherit_contrato=1)
                                # Intereses de Cesantias
                                obj_provision.write({'struct_id': struct_intcesantias.id})
                                localdict, result_intcesantias = obj_provision._get_payslip_lines_cesantias(inherit_contrato=1)
                                #Prima
                                obj_provision.write({'struct_id': struct_prima.id})
                                localdict,result_prima = obj_provision._get_payslip_lines_prima(inherit_contrato=1)
                            #Vacaciones
                            obj_provision.write({'struct_id': struct_vacaciones.id})
                            localdict,result_vac = obj_provision._get_payslip_lines_vacation(inherit_contrato=1)


                        obj_provision.action_payslip_cancel()
                        obj_provision.unlink()

                        #Guardar resultado
                        result_finally = {**result_cesantias,**result_intcesantias,**result_prima,**result_vac}

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
                            date_month_ant = date_start - timedelta(days=1)

                            obj_provisions = self.env['hr.executing.provisions.details']

                            executing_provisions = self.env['hr.executing.provisions.details'].search(
                                [('executing_provisions_id.state', 'in', ['done', 'accounting']),
                                 ('executing_provisions_id', '!=', self.id),
                                 ('executing_provisions_id.date_end', '=', date_month_ant),
                                 ('provision', '=', provision), ('contract_id', '=', contract.id)])
                            value_balance = sum([i.current_payable_value for i in obj_provisions.browse(executing_provisions.ids)])
                            amount_ant = sum([i.amount for i in obj_provisions.browse(executing_provisions.ids)])
                            #Obtener pagos realizados en el mes
                            code_filter = [provision.upper()] if provision != 'vacaciones' else ['VACCONTRATO','VACDISFRUTADAS','VACREMUNERADAS']

                            obj_payslip = self.env['hr.payslip.line']
                            lines_payslip = self.env['hr.payslip.line'].search(
                                [('slip_id.state', '=', 'done'), ('slip_id.date_from', '>=', date_start),
                                 ('slip_id.date_from', '<=', date_end), ('code', 'in', code_filter),
                                 ('slip_id.contract_id', '=', contract.id),('is_history_reverse','=',False)])
                            lines_payslip += self.env['hr.payslip.line'].search(
                                [('slip_id.state', '=', 'done'), ('slip_id.date_to', '>=', date_start),
                                 ('slip_id.date_to', '<=', date_end), ('code', 'in', code_filter),
                                 ('slip_id.contract_id', '=', contract.id),('is_history_reverse','=',False),
                                 ('id','not in',lines_payslip.ids),
                                 ('slip_id.struct_id.process','in',['cesantias','intereses_cesantias','prima'])])
                            if len(lines_payslip) > 0:
                                value_payments = sum([i.total for i in obj_payslip.browse(lines_payslip.ids)])
                            else:
                                value_payments = 0

                            #Calcular valor a pagar actual
                            amount = round((line['amount'] * line['quantity'] * line['rate'])/100,0)

                            # ------------------------
                            # 19/01/2022 - Luis Buitrón | Carolina Rincón : Se comenta buscar los pagos historicos
                            #  debido a que solamente debe tener en cuenta los pagos realizados en el mes
                            # ------------------------
                            #obj_provisions = self.env['hr.executing.provisions.details']
                            #executing_provisions = self.env['hr.executing.provisions.details'].search(
                            #    [('executing_provisions_id.state', 'in', ['done', 'accounting']),
                            #     ('executing_provisions_id', '!=', self.id),('value_payments','>',0),
                            #     ('provision', '=', provision), ('contract_id', '=', contract.id)])

                            #if len(executing_provisions) > 0:
                            #    payable_value = sum([i.value_payments for i in obj_provisions.browse(executing_provisions.ids)])
                            #    current_payable_value = amount - (payable_value+value_payments)
                            #else:
                            if value_payments > 0 and provision == 'vacaciones':
                                current_payable_value = value_balance - value_payments
                            else:
                                current_payable_value = amount - value_payments
                                current_payable_value = current_payable_value if current_payable_value > 0 else 0

                            #Valor provision Mes
                            if value_payments > 0 and current_payable_value < 0 and provision == 'vacaciones':
                                value_provision = abs(current_payable_value)
                                current_payable_value = 0
                            elif value_payments > 0 and current_payable_value >=0 and provision == 'vacaciones' and not retirement_date:
                                value_provision = amount - current_payable_value
                                current_payable_value = amount
                            elif (retirement_date or (
                                    value_payments == 0 and current_payable_value >= 0)) and provision == 'vacaciones':
                                value_provision = amount - value_balance  # amount_ant
                            else:
                                value_provision = amount - value_balance

                            if line['quantity'] <= 0 and provision == 'vacaciones':
                                line['quantity'] = 0
                                value_provision, current_payable_value, amount = 0, 0, 0

                            #Obtener ultima liquidacion del mes para traer la cuenta analitica utilizada
                            obj_last_payslip = self.env['hr.payslip']
                            last_lines_payslip = self.env['hr.payslip'].search(
                                [('state', '=', 'done'), ('date_from', '>=', date_start),
                                 ('date_from', '<=', date_end),('contract_id', '=', contract.id)])
                            last_lines_payslip += self.env['hr.payslip'].search(
                                [('state', '=', 'done'), ('date_to', '>=', date_start),
                                 ('date_to', '<=', date_end),('contract_id', '=', contract.id), ('id', 'not in', last_lines_payslip.ids),
                                 ('struct_id.process', 'in', ['cesantias', 'intereses_cesantias', 'prima'])])
                            analytic_account_id = contract.analytic_account_id
                            for last_payslip in sorted(last_lines_payslip,key=lambda x: x.date_to):
                                analytic_account_id = last_payslip.analytic_account_id

                            #Guardar valores
                            values_details = {
                                'executing_provisions_id':self.id,
                                'provision': provision,
                                'employee_id': contract.employee_id.id,
                                'contract_id': contract.id,
                                'analytic_account_id': analytic_account_id.id,
                                'value_wage': contract.wage,
                                'value_base': line['amount_base'],
                                'time': line['quantity'],
                                'value_balance': value_provision,
                                'value_payments': value_payments,
                                'current_payable_value': current_payable_value,
                                'amount': amount
                            }
                            self.env['hr.executing.provisions.details'].create(values_details)

                except Exception as e:
                    msg = 'ERROR: '+str(e.args[0])+' en el contrato '+contract.name+'.'
                    result = {
                        'executing_provisions_id': self.id,
                        'employee_id': contract.employee_id.id,
                        'branch_id': False,
                        'description': str(e.args[0])
                    }
                    self.env['hr.errors.provisions'].create(result)
                    if self.observations:
                        self.observations = self.observations + '\n' + msg
                    else:
                        self.observations = msg

    def executing_provisions(self):
        #Eliminar ejecución
        #self.env['hr.executing.provisions.details'].search([('executing_provisions_id','=',self.id)]).unlink()
        self.env['hr.errors.provisions'].search([('executing_provisions_id', '=', self.id)]).unlink()
        #self.env['hr.executing.provisions'].search([('executing_provisions_id', '=', self.id)]).unlink()
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
        struct_cesantias = self.env['hr.payroll.structure'].search([('process', '=', 'cesantias')])
        struct_intcesantias = self.env['hr.payroll.structure'].search([('process', '=', 'intereses_cesantias')])
        struct_prima = self.env['hr.payroll.structure'].search([('process', '=', 'prima')])
        struct_vacaciones = self.env['hr.payroll.structure'].search([('process', '=', 'vacaciones')])

        #Obtener contratos activos o desactivados en el mes de ejecución
        #obj_contracts = self.env['hr.contract'].search(
        #    [('state', '=', 'open'), ('date_start', '<=', date_end), ('company_id', '=', self.env.company.id),
        #     ('subcontract_type','!=','obra_integral')])
        #obj_contracts += self.env['hr.contract'].search(
        #    [('state', '=', 'close'), ('retirement_date', '>=', date_start), ('retirement_date', '<=', date_end),
        #     ('company_id', '=', self.env.company.id),('subcontract_type','!=','obra_integral')])
        #obj_contracts += self.env['hr.contract'].search(
        #    [('state', '=', 'finished'), ('date_end', '>=', date_start), ('date_end', '<=', date_end),
        #     ('company_id', '=', self.env.company.id), ('subcontract_type', '!=', 'obra_integral')])

        # Obtener contratos que tuvieron liquidaciones en el mes
        str_contracts = '(0)'
        if len(self.details_ids) > 0:
            str_contracts = str(self.details_ids.contract_id.ids).replace('[', '(').replace(']', ')')

        query = '''
            select distinct b.id 
            from hr_payslip a
            inner join hr_contract b on a.contract_id = b.id and (b.subcontract_type not in ('obra_integral') or b.subcontract_type is null) and b.id not in %s
            where a.state = 'done' and a.company_id = %s and ((a.date_from >= '%s' and a.date_from <= '%s') or (a.date_to >= '%s' and a.date_to <= '%s'))
            Limit %s
        ''' % (str_contracts,self.env.company.id,date_start,date_end,date_start,date_end,self.employees_per_batch)

        self.env.cr.execute(query)
        result_query = self.env.cr.fetchall()

        contract_ids = []
        for result in result_query:
            contract_ids.append(result)
        obj_contracts = self.env['hr.contract'].search([('id', 'in', contract_ids)])

        #Guardo los contratos en lotes de a 20
        limit_employees_per_batch = int(math.ceil(self.employees_per_batch/5)) if self.employees_per_batch > 100 else self.employees_per_batch
        contracts_array, i, j = [], 0 , limit_employees_per_batch
        while i <= len(obj_contracts):
            contracts_array.append(obj_contracts[i:j])
            i = j
            j += limit_employees_per_batch

        #----------------------------Recorrer contratos por savepoints
        date_start_process = datetime.now()
        date_finally_process = datetime.now()
        i = 1

        for contract in contracts_array:
            self.executing_provisions_savepoint(date_start,date_end,struct_vacaciones,struct_prima,struct_cesantias,struct_intcesantias,contract)

        date_finally_process = datetime.now()
        time_process = date_finally_process - date_start_process
        time_process = time_process.seconds / 60
        time_process += self.time_process_float
        self.time_process_float = time_process
        self.time_process = "El proceso se demoro {:.2f} minutos.".format(time_process)

        query = '''
                    select distinct b.id 
                    from hr_payslip a
                    inner join hr_contract b on a.contract_id = b.id and (b.subcontract_type not in ('obra_integral') or b.subcontract_type is null)
                    inner join hr_employee c on a.employee_id = c.id
                    inner join hr_parameterization_of_contributors d on c.tipo_coti_id = d.type_of_contributor and c.subtipo_coti_id = d.contributor_subtype and d.liquidated_provisions = true
                    where a.state = 'done' and a.company_id = %s and ((a.date_from >= '%s' and a.date_from <= '%s') or (a.date_to >= '%s' and a.date_to <= '%s'))
                ''' % (self.env.company.id, date_start, date_end, date_start, date_end)
        self.env.cr.execute(query)
        result_query = self.env.cr.fetchall()

        if len(self.details_ids.contract_id.ids) >= len(result_query):
            self.date_end = date_end
            self.state = 'done'
        else:
            self.env['hr.errors.provisions'].search([('executing_provisions_id', '=', self.id), ('description', '=', 'EMPLEADO FALTANTE POR EJECUTAR')]).unlink()
            ids_execute = set(self.details_ids.mapped('contract_id').ids)
            ids_x_execute = set(int(tupla[0]) for tupla in result_query)
            ids_diff = list(ids_x_execute - ids_execute)
            missing_contracts = self.env['hr.contract'].browse(ids_diff)
            for diff in missing_contracts:
                result = {
                    'executing_provisions_id': self.id,
                    'employee_id': diff.employee_id.id if diff.employee_id else False,
                    'contract_id': diff.id,
                    'description': 'EMPLEADO FALTANTE POR EJECUTAR'
                }
                self.env['hr.errors.provisions'].create(result)

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
            analytic_account_id = slip.analytic_account_id

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
                    if account_rule.department.id == slip.employee_id.department_id.id or account_rule.department.id == slip.employee_id.department_id.parent_id.id or account_rule.department.id == slip.employee_id.department_id.parent_id.parent_id.id or account_rule.department.id == False:
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

                    # Descripción final
                    addref_work_address_account_moves = self.env['ir.config_parameter'].sudo().get_param(
                        'zue_hr_payroll.addref_work_address_account_moves') or False
                    if addref_work_address_account_moves and slip.employee_id.address_id:
                        if slip.employee_id.address_id.parent_id:
                            description = f"{slip.employee_id.address_id.parent_id.vat} {slip.employee_id.address_id.display_name}|{slip.provision.upper()}"
                        else:
                            description = f"{slip.employee_id.address_id.vat} {slip.employee_id.address_id.display_name}|{slip.provision.upper()}"
                    else:
                        description = slip.provision.upper()

                    #Valor
                    amount = slip.value_balance if slip.value_balance != 0 else slip.amount

                    if debit_account_id:
                        debit = abs(amount) if amount >= 0.0 else 0.0
                        credit = abs(amount) if amount < 0.0 else 0.0
                        debit_line = {
                            'name': description,
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
                            'name': description,
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
        self.env['hr.errors.provisions'].search([('executing_provisions_id', '=', self.id)]).unlink()
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

class hr_errors_provisions(models.Model):
    _name = 'hr.errors.provisions'
    _description = 'Ejecución de provisiones errores'

    executing_provisions_id =  fields.Many2one('hr.executing.provisions', 'Ejecución de provisiones', required=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', 'Empleado',required=True, ondelete='cascade',)
    contract_id =  fields.Many2one('hr.contract', 'Contrato')
    description = fields.Text('Observación')