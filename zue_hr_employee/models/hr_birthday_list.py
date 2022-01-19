from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class hr_birthday_list(models.TransientModel):
    _name = "hr.birthday.list"
    _description = "Listado de cumpleaños"
    
    month = fields.Selection([('0', 'Todos'),
                            ('1', 'Enero'),
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

    def name_get(self):
        result = []
        for record in self:            
            result.append((record.id, "Listado de cumpleaños"))
        return result

    def get_month(self):
        if self.month == '0':
            month = [1,2,3,4,5,6,7,8,9,10,11,12]
        else: 
            month = [int(self.month)]
        return month

    def get_info_birthday(self,month):
        obj_employee = self.env['hr.employee'].search([('birthday','!=',False)]).filtered(lambda x: x.birthday.month == int(month))
        return obj_employee

    def get_name_month(self,month_number):
        #Mes
        month = ''
        month = 'Enero' if month_number == 1 else month
        month = 'Febrero' if month_number == 2 else month
        month = 'Marzo' if month_number == 3 else month
        month = 'Abril' if month_number == 4 else month
        month = 'Mayo' if month_number == 5 else month
        month = 'Junio' if month_number == 6 else month
        month = 'Julio' if month_number == 7 else month
        month = 'Agosto' if month_number == 8 else month
        month = 'Septiembre' if month_number == 9 else month
        month = 'Octubre' if month_number == 10 else month
        month = 'Noviembre' if month_number == 11 else month
        month = 'Diciembre' if month_number == 12 else month

        return month

    def get_date_text(self,date,calculated_week=0,hide_year=0):
        #Mes
        month = self.get_name_month(date.month)
        #Dia de la semana
        week = ''
        week = 'Lunes' if date.weekday() == 0 else week
        week = 'Martes' if date.weekday() == 1 else week
        week = 'Miercoles' if date.weekday() == 2 else week
        week = 'Jueves' if date.weekday() == 3 else week
        week = 'Viernes' if date.weekday() == 4 else week
        week = 'Sábado' if date.weekday() == 5 else week
        week = 'Domingo' if date.weekday() == 6 else week

        if hide_year == 0:
            if calculated_week == 0:
                date_text = date.strftime('%d de '+month+' del %Y')
            else:
                date_text = date.strftime(week+', %d de '+month+' del %Y')
        else:
            if calculated_week == 0:
                date_text = date.strftime('%d de '+month)
            else:
                date_text = date.strftime(week+', %d de '+month)

        return date_text

    def generate_report(self):
        datas = {
             'id': self.id,
             'model': 'hr.birthday.list'             
            }

        return {
            'type': 'ir.actions.report',
            'report_name': 'zue_hr_employee.report_birthday_list',
            'report_type': 'qweb-pdf',
            'datas': datas        
        }      


        
