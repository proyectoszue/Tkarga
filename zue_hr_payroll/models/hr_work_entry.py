# -*- coding: utf-8 -*-
from odoo.tools import config
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, datetime, time
import pytz

class hr_work_entry_refresh(models.TransientModel):
    _name = 'hr.work.entry.refresh'
    _description = 'Actualizar entradas de trabajo'

    date_start = fields.Date('Fecha Inicial', required=True)
    date_stop = fields.Date('Fecha Final', required=True)
    contract_ids = fields.Many2many('hr.contract', string='Contratos', required=True, domain=[('state', '=', 'open')])
    # employee_id = fields.Many2one('hr.employee', 'Empleado', required=True)
    # contract_id = fields.Many2one('hr.contract', 'Contrato', required=True)

    def refresh_work_entry(self):
        for record in self:
            date_start = fields.Datetime.to_datetime(record.date_start)
            date_stop = datetime.combine(fields.Datetime.to_datetime(record.date_stop), datetime.max.time())

            self.env['hr.work.entry'].search([('date_start', '>=', date_start),
                                                ('date_stop', '<=', date_stop),
                                                ('contract_id', 'in', record.contract_ids.ids)]).unlink()
            
            vals_list = record.contract_ids._get_work_entries_values(date_start, date_stop)
            self.env['hr.work.entry'].create(vals_list)



    
    
