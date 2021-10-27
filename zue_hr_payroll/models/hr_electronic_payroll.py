from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone

import base64
import io

class hr_electronic_payroll_detail(models.Model):
    _name = 'hr.electronic.payroll.detail'
    _description = 'Nómina electrónica detalle'

    electronic_payroll_id = fields.Many2one('hr.electronic.payroll',string='Nómina electrónica', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee',string='Empleado')
    contract_id = fields.Many2one('hr.contract', string='Contrato')
    item = fields.Integer(string='Item')
    sequence = fields.Char(string='Prefijo+Consecutivo')
    cune_dian = fields.Char(string='CUNE')
    return_file_dian = fields.Binary(string='Archivo DIAN')
    payslip_ids = fields.Many2many('hr.payslip',string='Nóminas')
    # XML
    xml_file = fields.Binary('XML')
    xml_file_name = fields.Char('XML name', size=64)

    def download_xml(self):
        action = {
            'name': 'XMLNominaElectronicaCarvajal',
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=hr.electronic.payroll.detail&id=" + str(
                self.id) + "&filename_field=xml_file_name&field=xml_file&download=true&filename=" + self.xml_file_name,
            'target': 'self',
        }
        return action

    def get_xml(self):
        obj_xml = self.env['zue.xml.generator.header'].search([('code','=','NomElectronica_Carvajal')])
        xml = obj_xml.xml_generator(self)

        filename = obj_xml.name+'.xml'
        self.write({
            'xml_file': base64.encodestring(xml),
            'xml_file_name': filename,
        })

        return True

    def get_type_contract(self):
        type = self.contract_id.contract_type
        if type == 'fijo':
            type = '1' # Contrato de Trabajo a Término Fijo
        elif type == 'indefinido':
            type = '2' # Contrato de Trabajo a Término Indefinido
        elif type == 'obra' or type == 'temporal':
            type = '3' # Contrato por Obra o Labor
        elif type == 'aprendizaje':
            type = '4' # Aprendizaje
        else:
            type = '0'
        # type = 5 | Practicante
        return type

    def get_date_now(self):
        return str(datetime.now(timezone(self.env.user.tz)).date())

    def get_time_now(self):
        time = datetime.now(timezone(self.env.user.tz)).strftime("%H:%M:%S")
        return time+'-05:00' # https://24timezones.com/es/difference/gmt/bogota

    def get_dates_process(self,end=0): #Si se envia el parametro end en 1 retornara la fecha final del periodo sino retornara fecha inicial.
        try:
            date_start = '01/' + str(self.electronic_payroll_id.month) + '/' + str(self.electronic_payroll_id.year)
            date_start = datetime.strptime(date_start, '%d/%m/%Y')

            date_end = date_start + relativedelta(months=1)
            date_end = date_end - timedelta(days=1)

            date_start = date_start.date()
            date_end = date_end.date()

            if end == 1:
                return str(date_end)
            else:
                return str(date_start)
        except:
            raise UserError(_('El año digitado es invalido, por favor verificar.'))

    def get_time_working(self):
        date_start = self.contract_id.date_start
        date_end = datetime.strptime(self.get_dates_process(end=1), '%Y-%m-%d').date() if not self.contract_id.retirement_date else self.contract_id.retirement_date
        dias = self.dias360(date_start,date_end)
        return dias

    def get_bank_information(self,r_bank=0,r_type=0,r_account=0):
        for bank in self.employee_id.address_home_id.bank_ids:
            if bank.is_main:
                if r_bank != 0:
                    return bank.bank_id.name
                if r_type != 0:
                    return bank.type_account
                if r_account != 0:
                    return bank.acc_number

    def get_dates_payment_payrolls(self):
        dates = []
        for payslip in self.payslip_ids:
            dates.append(str(payslip.date_to))
        return dates

    def get_days_lines(self,lst_codes):
        days = 0
        for payslip in self.payslip_ids:
            for entries in payslip.worked_days_line_ids:
                days += entries.number_of_days if entries.work_entry_type_id.code in lst_codes else 0
        return int(days)

    def get_value_salary_rules(self,lst_codes):
        value = 0
        for payslip in self.payslip_ids:
            for line in payslip.line_ids:
                value += abs(line.total) if line.salary_rule_id.code in lst_codes else 0
        return value

    def get_quantity_salary_rules(self,lst_codes):
        quantity = 0
        for payslip in self.payslip_ids:
            for line in payslip.line_ids:
                quantity += abs(line.quantity) if line.salary_rule_id.code in lst_codes else 0
        return quantity

    def get_annual_parameters(self):
        obj = self.env['hr.annual.parameters'].search([('year', '=', self.electronic_payroll_id.year)])
        return obj

    def get_type_overtime(self,equivalence_number_ne):
        obj = self.env['hr.type.overtime'].search([('equivalence_number_ne', '=', equivalence_number_ne)], limit=1)
        return obj

    def get_porc_fsp(self):
        porc = 0
        annual_parameters = self.env['hr.annual.parameters'].search([('year', '=', self.electronic_payroll_id.year)])
        value_base = 0
        for payslip in self.payslip_ids:
            for line in payslip.line_ids:
                value_base += abs(line.total) if line.salary_rule_id.category_id.code == 'DEV_SALARIAL' else 0

        if (value_base / annual_parameters.smmlv_monthly) > 4 and (
                value_base / annual_parameters.smmlv_monthly) < 16:
            porc = 1
        if (value_base / annual_parameters.smmlv_monthly) >= 16 and (
                value_base / annual_parameters.smmlv_monthly) <= 17:
            porc = 1.2
        if (value_base / annual_parameters.smmlv_monthly) > 17 and (
                value_base / annual_parameters.smmlv_monthly) <= 18:
            porc = 1.4
        if (value_base / annual_parameters.smmlv_monthly) > 18 and (
                value_base / annual_parameters.smmlv_monthly) <= 19:
            porc = 1.6
        if (value_base / annual_parameters.smmlv_monthly) > 19 and (
                value_base / annual_parameters.smmlv_monthly) <= 20:
            porc = 1.8
        if (value_base / annual_parameters.smmlv_monthly) > 20:
            porc = 2

        return porc

class hr_electronic_payroll(models.Model):
    _name = 'hr.electronic.payroll'
    _description = 'Nómina electrónica'

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
    observations = fields.Text('Observaciones')
    state = fields.Selection([
            ('draft', 'Borrador'),
            ('done', 'Realizado'),
            ('accounting', 'Contabilizado'),
        ], string='Estado', default='draft')
    #Proceso
    prefix = fields.Char(string='Prefijo', required=True)
    executing_electronic_payroll_ids = fields.One2many('hr.electronic.payroll.detail', 'electronic_payroll_id', string='Ejecución', ondelete='cascade' )
    time_process = fields.Char(string='Tiempo ejecución')
    
    company_id = fields.Many2one('res.company', string='Compañía', readonly=True, required=True,
        default=lambda self: self.env.company)

    _sql_constraints = [('electronic_payroll_period_uniq', 'unique(company_id,year,month)', 'El periodo seleccionado ya esta registrado para esta compañía, por favor verificar.')]

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "Nómina Electrónica | Periodo {}-{}".format(record.month,str(record.year))))
        return result

    def executing_electronic_payroll(self):
        # Eliminar ejecución
        self.env['hr.electronic.payroll.detail'].search([('electronic_payroll_id', '=', self.id)]).unlink()

        # Obtener fechas del periodo seleccionado
        date_start = '01/' + str(self.month) + '/' + str(self.year)
        try:
            date_start = datetime.strptime(date_start, '%d/%m/%Y')

            date_end = date_start + relativedelta(months=1)
            date_end = date_end - timedelta(days=1)

            date_start = date_start.date()
            date_end = date_end.date()
        except:
            raise UserError(_('El año digitado es invalido, por favor verificar.'))

        # Obtener empleados que tuvieron liquidaciones en el mes
        query = '''
            select distinct b.id 
            from hr_payslip a 
            inner join hr_employee b on a.employee_id = b.id 
            where a.state = 'done' and a.date_from >= '%s' and a.date_to <= '%s' and a.company_id = %s            
        ''' % (date_start, date_end, self.company_id.id)

        self.env.cr.execute(query)
        result_query = self.env.cr.fetchall()

        employee_ids = []
        for result in result_query:
            employee_ids.append(result)
        obj_employee = self.env['hr.employee'].search([('id', 'in', employee_ids)])

        item = 0
        for employee in obj_employee:
            item += 1
            # Obtener contrato activo
            obj_contract = self.env['hr.contract'].search([('state', '=', 'open'), ('employee_id', '=', employee.id)])
            if not obj_contract:
                obj_contract = self.env['hr.contract'].search([('state', '=', 'close'), ('employee_id', '=', employee.id), ('retirement_date', '>=', date_start)],limit=1)
                # Obtener nóminas en ese rango de fechas
            obj_payslip = self.env['hr.payslip'].search([('state', '=', 'done'), ('employee_id', '=', employee.id), ('contract_id', '=', obj_contract.id),('date_from', '>=', date_start), ('date_to', '<=', date_end)])

            value_detail = {
                'electronic_payroll_id':self.id,
                'employee_id':employee.id,
                'contract_id':obj_contract.id,
                'item':item,
                'sequence': self.prefix+''+str(item),
                'payslip_ids':[(6, 0, obj_payslip.ids)]
            }

            self.env['hr.electronic.payroll.detail'].create(value_detail)

        for detail in self.executing_electronic_payroll_ids:
            detail.get_xml()