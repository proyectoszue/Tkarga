
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

    #Libro de cesantias
    def get_info_book_cesantias(self):
        return self.env['hr.history.cesantias'].search([('contract_id','=',self.id)])