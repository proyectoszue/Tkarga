from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError


class zue_confirm_wizard(models.TransientModel):
    _name = 'zue.confirm.wizard'
    _description = 'Confirmación de procesos zue'

    yes_no = fields.Char(default='Desea continuar?')

    def yes(self):
        return True


