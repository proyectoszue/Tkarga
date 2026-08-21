# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date, datetime, time
from odoo.exceptions import UserError, ValidationError

class hr_work_entry(models.Model):
    _inherit = 'hr.work.entry'

    @api.model_create_multi
    def create(self, values_list):
        for vals in values_list:
            version_id = vals.get('version_id')
            entry_date = vals.get('date')

            if not version_id or not entry_date:
                continue

            version = self.env['hr.version'].browse(version_id)
            if not version or not version.contract_date_start:
                continue

            entry_date = fields.Date.to_date(entry_date)
            if entry_date < version.contract_date_start:
                vals['state'] = 'conflict'
                vals['active'] = False

        return super().create(values_list)
