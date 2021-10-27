from odoo import models, fields, api
from datetime import datetime, timedelta

class mntc_causes(models.Model):
    _name = 'mntc.causes'
    _description = 'Causas de falla'

    name = fields.Char(compute="_get_complete_name", string='Name',store=True)
    code = fields.Char('Code', size=4, required=True)
    description = fields.Text('Description',required=True)
    _sql_constraints = [
        ('code', 'UNIQUE (code)', 'You can not have two users with the same name !')
    ]

    @api.onchange('code')
    @api.depends('code', 'description')
    def _get_complete_name(self):
        for record in self:
            display_name = ''
            if record.description:
                display_name += record.description
            if record.code:
                display_name += ' (' + record.code + ')'
            record.name = display_name
