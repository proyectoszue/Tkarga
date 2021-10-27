from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class mntc_routines(models.Model):
    _name = 'mntc.routines'
    _description = 'Rutinas'

    name = fields.Char(string='Name')
    description = fields.Text(string='Description')
    estimated_time = fields.Float(string='Estimated time', compute='calculate_time')
    activity_ids = fields.Many2many('mntc.activity',string='Activity_ids')#,'mntc_routines_x_mntc_activity', 'routine_id', 'activity_id', 
    trigger_type = fields.Selection([('frecuency', "Frecuency"), ('odometer', "Odometer")], string="Trigger type")
    trigger_qty = fields.Float(string='Quantity')
    state = fields.Boolean(string='State', default=True) 

    def calculate_time(self):
        for rotuine in self:
            count = 0.0
            for activity in rotuine.activity_ids:
                if activity.estimated_time:
                    count += activity.estimated_time
            rotuine.estimated_time = count


class mntc_activity(models.Model):
    _name = 'mntc.activity'
    _description = 'Actividades'

    name = fields.Char(string='Name', required=True)
    system_id = fields.Many2one('mntc.vehicle.system', string='System id', required=True)
    estimated_time = fields.Float(string='Estimated time', compute='calculate_stimated_time', store=True)
    description = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence')
    state = fields.Boolean(string='State', default=True)
    inspections_ids = fields.One2many('mntc.inspections', 'activity_id', string='Inspections')
    required_technicians = fields.Integer(string='Required technicians', default=1, required=True) 
    repuesto = fields.One2many('mntc.repuestos', 'actividad', string='Repuestos')
    servicio = fields.One2many('mntc.servicios', 'actividad', string='Servicios')
    disciplina = fields.Many2many('mntc.workforce.type.time',string='Disciplina')
    
    @api.depends('disciplina')
    def calculate_stimated_time(self):
        for activity in self:
            count = 0.0
            for disciplina in activity.disciplina:
                if disciplina.estimated_time:
                    count += disciplina.estimated_time
            activity.estimated_time = count

    # @api.constrains('required_technicians')
    # def _check_required_technicians(self):
    #     for activity in self:
    #         if activity.required_technicians > 5 or activity.required_technicians < 1:
    #             raise ValidationError(_('Enter value between 1-5.'))
    

class mntc_inspections(models.Model):
    _name = 'mntc.inspections'
    _description = 'Inspecciones'

    name = fields.Char(string='Name')
    activity_id = fields.Many2one('mntc.activity', string='Activity')
    sequence = fields.Integer(string='Sequence')
    inspection_type = fields.Selection([('qualitative', 'Qualitative'),('quantitative', 'Quantitative')], string='Type', default='quantitative')
    condition = fields.Selection([('greater_than', '>'),('greater_than_or_equal', '>='),('less_than', '<'),('less_than_or_equal', '<='),('equality', '=='),('inequality', '!='),('between', '<x<') ], string='Condition')
    min_value = fields.Float(string='Min', digits=(16, 5))
    max_value = fields.Float(string='Max', digits=(15, 5))
    uom_id = fields.Many2one('product.uom', string='Uom')
    inspection_values_ids = fields.One2many('mntc.inspections.values', 'inspection_id', string='Inspection values')

class mntc_inspections_values(models.Model):
    _name = 'mntc.inspections.values'
    _description = 'Possible values of qualitative questions.'

    inspection_id = fields.Many2one("mntc.inspections", string="Inspection")
    name = fields.Char(string='Name', required=True)
    ok = fields.Boolean(string='Correct answer?', help="When this field is marked, the answer is considered correct.")

