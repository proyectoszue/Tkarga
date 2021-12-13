from odoo import fields, models, api

class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    identification_id = fields.Char(readonly=True)
    address_home_id = fields.Many2one('res.partner',readonly=True)
    personal_mobile = fields.Char(readonly=True)
    birthday = fields.Date(readonly=True)
    type_employee = fields.Many2one('hr.types.employee',readonly=True)
    personal_email = fields.Char(readonly=True)

class HrEmployeeUpdateTmp(models.TransientModel):
    _name = 'hr.employee.update.tmp'
    _description = 'Tabla tmp para actualizar empleados - Portal autogestión'

    employee_id = fields.Many2one('hr.employee',readonly=True)

    def update_personal_data(self,values_employee,values_partner):
        self.sudo().env['hr.employee'].search([('id', '=', self.employee_id.id)], limit=1).write(values_employee)
        self.sudo().env['res.partner'].search([('id', '=', self.employee_id.address_home_id.id)], limit=1).write(values_partner)