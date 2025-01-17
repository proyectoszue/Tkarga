from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone
from lxml import etree

import random
import base64
import io
import uuid
import time

class hr_electronic_payroll_detail(models.Model):
    _inherit = 'hr.electronic.payroll.detail'

    def get_consolidated_provisions(self, provision):
        if self.electronic_payroll_id.month == '12':
            obj_consolidated = self.env['hr.consolidated.provisions.detail'].search(
                [('z_consolidated_provision_id.z_year', '=', self.electronic_payroll_id.year),
                 ('z_consolidated_provision_id.z_provision', '=', provision),
                 ('z_consolidated_provision_id.state', '=', 'approved'),
                 ('z_employee_id.id', '=', self.employee_id.id)])
            if len(obj_consolidated) > 0:
                return sum([i.z_total for i in obj_consolidated])
            else:
                return 0
        else:
            return 0

class hr_electronic_adjust_payroll_detail(models.Model):
    _inherit = 'hr.electronic.adjust.payroll.detail'

    def get_consolidated_provisions(self, provision):
        if self.electronic_adjust_payroll_id.electronic_payroll_id.month == '12':
            obj_consolidated = self.env['hr.consolidated.provisions.detail'].search(
                [('z_consolidated_provision_id.z_year', '=', self.electronic_adjust_payroll_id.electronic_payroll_id.year),
                 ('z_consolidated_provision_id.z_provision', '=', provision),
                 ('z_consolidated_provision_id.state', '=', 'approved'),
                 ('z_employee_id.id', '=', self.employee_id.id)])
            if len(obj_consolidated) > 0:
                return sum([i.z_total for i in obj_consolidated])
            else:
                return 0
        else:
            return 0