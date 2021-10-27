from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError

class confirm_wizard(models.TransientModel):
    _name = 'confirm.wizard'
    _description = 'Confirmación de procesos'

    yes_no = fields.Char(default='Desea continuar?')
    workorder_id = fields.Many2one('mntc.workorder', string='Órden de trabajo')

    def yes(self):
        if self.workorder_id:
            self.workorder_id.mntc_workorder_end()

        return True


    