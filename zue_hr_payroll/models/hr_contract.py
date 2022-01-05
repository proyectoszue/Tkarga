
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError
import time

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class hr_contract(models.Model):
    _inherit = 'hr.contract'
    
    #Libro de vacaciones
    def get_info_book_vacation(self):
        return self.env['hr.vacation'].search([('contract_id','=',self.id)])

    def get_accumulated_vacation_days(self):
        date_start = self.date_start
        date_end = datetime.now().date()
        employee_id = self.employee_id.id
        #Días de servicio
        days_service = self.dias360(date_start, date_end)
        #Ausencias no remuneradas
        days_unpaid_absences = sum([i.number_of_days for i in self.env['hr.leave'].search(
            [('date_from', '>=', date_start), ('date_to', '<=', date_end),
             ('state', '=', 'validate'), ('employee_id', '=', employee_id),
             ('unpaid_absences', '=', True)])])
        days_unpaid_absences += sum([i.days for i in self.env['hr.absence.history'].search(
            [('star_date', '>=', date_start), ('end_date', '<=', date_end),
             ('employee_id', '=', employee_id), ('leave_type_id.unpaid_absences', '=', True)])])
        #Días a disfrutar
        days_vacations_total = ((days_service - days_unpaid_absences) * 15) / 360
        #Días ya pagados
        days_paid = sum([i.business_units+i.units_of_money for i in self.env['hr.vacation'].search([('contract_id', '=', self.id)])])
        #Dias faltantes por disfrutar
        days_vacations = round(days_vacations_total - days_paid,2)
        return days_vacations

    #Libro de cesantias
    def get_info_book_cesantias(self):
        return self.env['hr.history.cesantias'].search([('contract_id','=',self.id)])