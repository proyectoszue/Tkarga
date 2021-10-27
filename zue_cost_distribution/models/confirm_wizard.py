from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError


class zue_confirm_wizard(models.TransientModel):
    _inherit = 'zue.confirm.wizard'

    distribution_rule_id = fields.Many2one('distribution.rules.execution', string='Regla de distribución de costos')

    def yes(self):
        if self.distribution_rule_id:
            obj_move = self.env['account.move'].search([('distribution_execution_id', '=', self.distribution_rule_id.id)])
            obj_move.unlink()
            self.distribution_rule_id.generate_account_move()
        obj_confirm = super(zue_confirm_wizard, self).yes()
        return obj_confirm


