from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class hr_permit_application(models.Model):
    _name = "hr.permit.application"
    _description = 'Solicitud Permisos Portal'
    
    employee_id = fields.Many2one('hr.employee.public', 'Empleado')
    permit_date = fields.Date('Fecha de permiso')
    permit_days = fields.Integer('Numero de dias')
    reason = fields.Selection([('personal','Diligencia Personal'),
                                ('med_general','Cita médico general'),
                                ('med_laboral','Cita médico laboral'),
                                ('other','Otros')
                            ], string = 'Razon del permiso')
    observation = fields.Char('Observacion')
    initial_hour = fields.Datetime('Hora de salida')
    final_hour = fields.Datetime('Hora llegada')
    compensated = fields.Boolean(string='Compensado')

