from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone
#---------------------------Certificado ingreso y retenciones-------------------------------#

class hr_withholding_and_income_certificate(models.TransientModel):
    _name = 'hr.withholding.and.income.certificate'
    _description = 'Certificado ingreso y retenciones'

    employee_ids = fields.Many2many('hr.employee', string="Empleado",)
    year = fields.Integer('Año', required=True)
    struct_report_income_and_withholdings = fields.Html('Estructura Certificado ingresos y retenciones')

    def generate_certificate(self):
        struct_report_income_and_withholdings = ''
        if len(self.employee_ids) == 0:
            raise UserError(_('No se seleccionaron empleados.'))

        obj_annual_parameters = self.env['hr.annual.parameters'].search([('year', '=', self.year)], limit=1)
        for employee in self.employee_ids:
            if len(obj_annual_parameters) > 0:
                struct_report_income_and_withholdings = obj_annual_parameters.report_income_and_withholdings
                lst_items = []
                #Obtener nóminas
                year_process = self.year - 1
                # Obtener fechas del periodo seleccionado
                try:
                    date_start = '01/01/' + str(year_process)
                    date_start = datetime.strptime(date_start, '%d/%m/%Y')
                    date_start = date_start.date()
                    date_end = '31/12/' + str(year_process)
                    date_end = datetime.strptime(date_end, '%d/%m/%Y')
                    date_end = date_end.date()
                except:
                    raise UserError(_('El año digitado es invalido, por favor verificar.'))

                obj_payslip = self.env['hr.payslip'].search(
                    [('state', '=', 'done'), ('employee_id', '=', employee.id),
                     ('date_from', '>=', date_start), ('date_from', '<=', date_end)])
                obj_payslip += self.env['hr.payslip'].search(
                    [('state', '=', 'done'), ('employee_id', '=', employee.id),
                     ('id', 'not in', obj_payslip.ids),
                     ('struct_id.process', 'in', ['cesantias', 'intereses_cesantias', 'prima']),
                     ('date_to', '>=', date_start), ('date_to', '<=', date_end)])

                obj_payslip_accumulated = self.env['hr.accumulated.payroll'].search([('employee_id', '=', employee.id),
                                                                                     ('date', '>=', date_start),
                                                                                     ('date', '<=', date_end)])

                for conf in sorted(obj_annual_parameters.conf_certificate_income_ids, key=lambda x: x.sequence):
                        ldict = {'employee':employee}
                        value = None
                        #Tipo de Calculo ---------------------- INFORMACIÓN
                        if conf.calculation == 'info':
                            if conf.type_partner == 'employee':
                                if conf.information_fields_id.model_id.model == 'hr.employee':
                                    code_python = 'value = employee.' + str(conf.information_fields_id.name)
                                    exec(code_python, ldict)
                                    value = ldict.get('value')
                                elif conf.information_fields_id.model_id.model == 'hr.contract':
                                    raise UserError(_('No se puede traer información del empleado de un campo de la tabla contratos, EN DESARROLLO.'))
                                elif conf.information_fields_id.model_id.model == 'res.partner':
                                    code_python = 'value = employee.address_home_id.'+str(conf.information_fields_id.name)
                                    exec(code_python, ldict)
                                    value = ldict.get('value')
                            if conf.type_partner == 'company':
                                if conf.information_fields_id.model_id.model == 'hr.employee':
                                    raise UserError(_('No se puede traer información de la compañía de un campo de la tabla empleados, por favor verificar.'))
                                elif conf.information_fields_id.model_id.model == 'hr.contract':
                                    raise UserError(_('No se puede traer información de la compañía de un campo de la tabla contratos, por favor verificar.'))
                                elif conf.information_fields_id.model_id.model == 'res.partner':
                                    code_python = 'value = employee.company_id.partner_id.'+str(conf.information_fields_id.name)
                                    exec(code_python, ldict)
                                    value = ldict.get('value')
                        # Tipo de Calculo ---------------------- SUMATORIA REGLAS
                        elif conf.calculation == 'sum_rule':
                            amount = 0
                            #Nóminas
                            for payslip in obj_payslip:
                                amount += abs(sum([i.total for i in payslip.line_ids.filtered(lambda line: line.salary_rule_id.id in conf.salary_rule_id.ids)]))
                            #Acumulados
                            amount += abs(sum([i.amount for i in obj_payslip_accumulated.filtered(lambda line: line.salary_rule_id.id in conf.salary_rule_id.ids)]))
                            value = amount
                        # Tipo de Calculo ---------------------- SUMATORIA SECUENCIAS ANTERIORES
                        elif conf.calculation == 'sum_sequence':
                            if conf.sequence_list_sum:
                                amount = 0
                                sequence_list_sum = conf.sequence_list_sum.split(',')
                                for item in lst_items:
                                    amount += float(item[1]) if str(item[0]) in sequence_list_sum else 0
                                value = amount
                        # Tipo de Calculo ---------------------- FECHA EXPEDICIÓN
                        elif conf.calculation == 'date_issue':
                            value = str(datetime.now(timezone(self.env.user.tz)).strftime("%Y-%m-%d"))
                        # Tipo de Calculo ---------------------- FECHA CERTIFICACIÓN INICIAL
                        elif conf.calculation == 'start_date_year':
                            value = str(year_process)+'-01-01'
                        # Tipo de Calculo ---------------------- FECHA CERTIFICACIÓN FINAL
                        elif conf.calculation == 'end_date_year':
                            value = str(year_process)+'-12-31'
                        #----------------------------------------------------------------------------------------------
                        #                                       GUARDAR RESULTADO
                        # ----------------------------------------------------------------------------------------------
                        lst_items.append((conf.sequence, value))
                        if value != None:
                            struct_report_income_and_withholdings = struct_report_income_and_withholdings.replace('$_val'+str(conf.sequence)+'_$',("{:,.2f}".format(value) if type(value) is float else str(value)))
                        else:
                            struct_report_income_and_withholdings = struct_report_income_and_withholdings.replace('$_val' + str(conf.sequence)+'_$', '')
        #Limpiar vals no calculados
        for sequence_val in range(1,101):
            struct_report_income_and_withholdings = struct_report_income_and_withholdings.replace('$_val' + str(sequence_val) + '_$', '')
            for sequence_val_internal in range(1,10):
                struct_report_income_and_withholdings = struct_report_income_and_withholdings.replace('$_val' + str(sequence_val) + '.' + str(sequence_val_internal) + '_$', '')
        #Retonar PDF
        self.struct_report_income_and_withholdings = struct_report_income_and_withholdings
        datas = {
             'id': self.id,
             'model': 'hr.withholding.and.income.certificate'
            }
        return {
            'type': 'ir.actions.report',
            'report_name': 'zue_hr_payroll.hr_report_income_and_withholdings',
            'report_type': 'qweb-pdf',
            'datas': datas
        }