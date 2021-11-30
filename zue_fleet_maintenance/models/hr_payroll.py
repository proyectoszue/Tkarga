# -*- coding: utf-8 -*-
from odoo import models, fields, api

class hr_employee(models.Model):
    _inherit = 'hr.employee'
    
    #Disciplina
    workforce_id = fields.Many2one('mntc.workforce.type', 'Disciplina', track_visibility='onchange')

    @api.model
    def create(self, vals):
        res = super(hr_employee, self).create(vals)
        if vals.get('workforce_id'):
            obj_mntc_technician = self.env['mntc.technician'].search([('employee_id', '=', res.id)])
            if not obj_mntc_technician:
                self.env['mntc.technician'].create({
                    'employee_supplier':'emp_sup_1',
                    'employee_id':res.id,
                    'workforce_type_id':vals.get('workforce_id'),
                })
        return res

    def write(self, vals):
        res = super(hr_employee, self).write(vals)
        if vals.get('workforce_id'):
            obj_mntc_technician = self.env['mntc.technician'].search([('employee_id', '=', self.id)])
            if not obj_mntc_technician:
                self.env['mntc.technician'].create({
                    'employee_supplier': 'emp_sup_1',
                    'employee_id': self.id,
                    'workforce_type_id': vals.get('workforce_id'),
                })
            else:
                obj_mntc_technician.write({'workforce_type_id':vals.get('workforce_id')})
        return res