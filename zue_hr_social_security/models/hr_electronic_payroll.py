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

class hr_electronic_payroll(models.Model):
    _inherit = 'hr.electronic.payroll'

    def executing_electronic_payroll(self):
        super(hr_electronic_payroll, self).executing_electronic_payroll()
        for record in self:
            if record.month == '12':
                for detail in record.executing_electronic_payroll_ids:
                    obj_consolidated_provisions_detail = self.env['hr.consolidated.provisions.detail'].search(
                                                            [('z_consolidated_provision_id.z_year', '=', record.year),
                                                             ('z_consolidated_provision_id.state', '=', 'approved'),
                                                             ('z_employee_id.id', '=', detail.employee_id.id)])
                    detail.write({'z_consolidated_provisions_detail_ids': [(6, 0, obj_consolidated_provisions_detail.ids)]})

class hr_electronic_payroll_detail(models.Model):
    _inherit = 'hr.electronic.payroll.detail'

    z_consolidated_provisions_detail_ids = fields.Many2many('hr.consolidated.provisions.detail',
                                                            'hr_consolidated_hr_electronic_detail_rel',
                                                            string='Consolidado de Provisiones',
                                                            domain="[('z_employee_id','=',employee_id)]")

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

class hr_electronic_adjust_payroll(models.Model):
    _inherit = 'hr.electronic.adjust.payroll'

    def executing_electronic_payroll(self):
        super(hr_electronic_adjust_payroll, self).executing_electronic_payroll()
        for record in self:
            if record.electronic_payroll_id.month == '12':
                for detail in record.executing_electronic_adjust_payroll_ids:
                    obj_consolidated_provisions_detail = self.env['hr.consolidated.provisions.detail'].search(
                                                            [('z_consolidated_provision_id.z_year', '=', record.electronic_payroll_id.year),
                                                             ('z_consolidated_provision_id.state', '=', 'approved'),
                                                             ('z_employee_id.id', '=', detail.employee_id.id)])
                    detail.write({'z_consolidated_provisions_detail_ids': [(6, 0, obj_consolidated_provisions_detail.ids)]})

class hr_electronic_adjust_payroll_detail(models.Model):
    _inherit = 'hr.electronic.adjust.payroll.detail'

    z_consolidated_provisions_detail_ids = fields.Many2many('hr.consolidated.provisions.detail',
                                                            'hr_consolidated_hr_electronic_adjust_detail_rel',
                                                            string='Consolidado de Provisiones',
                                                            domain="[('z_employee_id','=',employee_id)]")

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