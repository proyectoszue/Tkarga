from odoo import fields, models, api

class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    identification_id = fields.Char(readonly=True)
    address_home_id = fields.Many2one('res.partner',readonly=True)
    personal_mobile = fields.Char(readonly=True)
    birthday = fields.Date(readonly=True)
    type_employee = fields.Many2one('hr.types.employee',readonly=True)
    personal_email = fields.Char(readonly=True)
    gender = fields.Char(string='Genero')
    branch_id = fields.Many2one('zue.res.branch',string='Sucursal')
    mobile_phone = fields.Char(readonly=True)
    work_phone = fields.Char(readonly=True)
    licencia_rh = fields.Char(readonly=True)
    licencia_categoria = fields.Char(readonly=True)
    licencia_vigencia = fields.Date(readonly=True)
    licencia_restricciones = fields.Char(readonly=True)
    country_id = fields.Many2one('res.country',readonly=True)
    place_of_birth = fields.Char(readonly=True)
    country_of_birth = fields.Many2one('res.country',readonly=True)
    emergency_contact = fields.Char(readonly=True)
    emergency_phone = fields.Char(readonly=True)
    emergency_relationship = fields.Char(readonly=True)
    certificate = fields.Char(readonly=True)
    study_field = fields.Char(readonly=True)
    study_school = fields.Char(readonly=True)
    marital = fields.Char(readonly=True)
    contract_id = fields.Many2one('hr.contract.public',string='Contrato')

class HrEmployeeUpdateTmp(models.TransientModel):
    _name = 'hr.employee.update.tmp'
    _description = 'Tabla tmp empleados - Portal autogestion'

    employee_id = fields.Many2one('hr.employee',readonly=True)

    def update_personal_data(self,values_employee,values_partner):
        self.sudo().env['hr.employee'].search([('id', '=', self.employee_id.id)], limit=1).write(values_employee)
        self.sudo().env['res.partner'].search([('id', '=', self.employee_id.address_home_id.id)], limit=1).write(values_partner)