# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date, datetime, time

class hr_work_entry(models.Model):
    _inherit = 'hr.work.entry'

    @api.model
    def create(self, vals):
        obj_contract = self.env['hr.contract'].search([('id', '=', vals.get('contract_id'))])
        date_start = datetime.strptime(str(vals.get('date_start')), '%Y-%m-%d %H:%M:%S').date()
        if date_start < obj_contract.date_start:
            vals['state'] = 'conflict'
            vals['active'] = False

        res = super(hr_work_entry, self).create(vals)
        return res

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

            for contract in record.contract_ids:
                date_start_contract = datetime.combine(contract.date_start, datetime.min.time())
                date_start_calculated = date_start_contract if date_start < date_start_contract else date_start
                date_stop_calculated = date_start_contract if date_stop < date_start_contract else date_stop
                self.env['hr.work.entry'].search([('date_start', '<=', date_stop_calculated),
                                                    ('date_stop', '>=', date_start_calculated),
                                                    ('contract_id', '=', contract.id)]).unlink()

                vals_list = contract._get_work_entries_values(date_start_calculated, date_stop_calculated)
                self.env['hr.work.entry'].create(vals_list)



    
    
