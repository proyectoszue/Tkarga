from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class hr_permit_application(models.Model):
    _name = "hr.permit.application"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Solicitud Permisos Portal'
    
    employee_id = fields.Many2one('hr.employee.public', 'Empleado', track_visibility='onchange')
    department_id = fields.Many2one(related='employee_id.department_id', string='Departamento')
    branch_id = fields.Many2one(related='employee_id.branch_id', string='Sucursal')
    permit_date = fields.Date('Fecha de solicitud', track_visibility='onchange')
    reason = fields.Selection([('personal', 'Diligencia Personal'),
                               ('med_general', 'Cita médico general'),
                               ('med_laboral', 'Cita médico laboral'),
                               ('other', 'Otros')
                               ], string='Tipo de solicitud', track_visibility='onchange')
    text_other = fields.Char(string='¿Cual?', track_visibility='onchange')
    leave_requested_more_day = fields.Boolean(string='Permiso solicitado superior a un dia', track_visibility='onchange')
    permit_days = fields.Integer('Dias solicitados', track_visibility='onchange')
    initial_hour = fields.Float('Hora de salida', track_visibility='onchange')
    final_hour = fields.Float('Hora llegada', track_visibility='onchange')
    observation = fields.Char('Observacion', track_visibility='onchange')
    compensated = fields.Boolean(string='Compensado')
    state = fields.Selection([('confirm', 'Para Aprobar'),
                                ('validate', 'Aprobado'),
                                ('refuse', 'Rechazado'),
                                ], string='Estado', default='confirm', required=True, track_visibility='onchange')

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "{} | {} - {}".format(record.employee_id.name, record.reason, record.permit_date)))
        return result

    def action_validate(self):
        for record in self:
            record.write({'state':'validate'})

    def action_refuse(self):
        for record in self:
            record.write({'state':'refuse'})