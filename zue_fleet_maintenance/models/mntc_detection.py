from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

class mntc_detection_methods(models.Model):
    _name = 'mntc.detection.methods'
    _description = 'Metodos de detección'

    name        = fields.Char(compute="_get_complete_name", string='Name',store=True)
    code = fields.Char('Code', size=4, required=True)
    description = fields.Char('Description',required=True)

    _sql_constraints = [
        ('code', 'UNIQUE (code)', 'You can not have two users with the same name !')
    ]

    @api.depends('code', 'description')
    def _get_complete_name(self):
        for record in self:
            display_name = ''
            if record.description:
                display_name += record.description
            if record.code:
                display_name += ' (' + record.code + ')'
            record.name = display_name