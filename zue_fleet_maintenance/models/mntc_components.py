from odoo import api,fields,models

class mntc_component(models.Model):
    _name = 'mntc.component'
    _description = 'Componentes'

    code = fields.Char('Code', size=4, required=True)
    name = fields.Text('Description',required=True)
    _sql_constraints = [
        ('code', 'UNIQUE (code)', 'You can not have two users with the same name !')
    ]
    
    @api.onchange('code')
    @api.depends('code', 'name')
    def _get_complete_name(self):
        for record in self:
            display_name = ''
            if record.name:
                display_name += record.name
            if record.code:
                display_name += ' (' + record.code + ')'
            record.name = display_name


class mntc_action_taken(models.Model):
    _name = 'mntc.action.taken'
    _description = 'Acciones tomadas'
    

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