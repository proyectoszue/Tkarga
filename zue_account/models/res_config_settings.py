from odoo import fields, models, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    z_entity_code_cgn = fields.Char(string='Código de la entidad - CGN')

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    z_entity_code_cgn = fields.Char(related='company_id.z_entity_code_cgn', string='Código de la entidad - CGN', readonly=False)
    z_qty_thread_moves_balance = fields.Integer(string='Cantidad de registros - Hilos balance', default=10000)
    z_qty_thread_balance = fields.Integer(string='Cantidad de bloques - Hilos balance', default=5)

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('zue_account.z_qty_thread_moves_balance', self.z_qty_thread_moves_balance)
        set_param('zue_account.z_qty_thread_balance', self.z_qty_thread_balance)

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res['z_qty_thread_moves_balance'] = get_param('zue_account.z_qty_thread_moves_balance')
        res['z_qty_thread_balance'] = get_param('zue_account.z_qty_thread_balance')
        return res



