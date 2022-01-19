from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    zue_electronic_invoice_username = fields.Char(string='Usuario Proveedor Tecnológico')
    zue_electronic_invoice_password = fields.Char(string='Contraseña Proveedor')
    zue_electronic_invoice_company_id = fields.Char(string='Company ID')
    zue_electronic_invoice_account_id = fields.Char(string='Account ID')
    zue_electronic_invoice_environment = fields.Selection([('prod','Producción'),('test','Pruebas')],string='Ambiente', default='prod')

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('zue_electronic_invoice.zue_electronic_invoice_username', self.zue_electronic_invoice_username)
        set_param('zue_electronic_invoice.zue_electronic_invoice_password', self.zue_electronic_invoice_password)
        set_param('zue_electronic_invoice.zue_electronic_invoice_company_id', self.zue_electronic_invoice_company_id)
        set_param('zue_electronic_invoice.zue_electronic_invoice_account_id', self.zue_electronic_invoice_account_id)
        set_param('zue_electronic_invoice.zue_electronic_invoice_environment', self.zue_electronic_invoice_environment)

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res['zue_electronic_invoice_username'] = get_param('zue_electronic_invoice.zue_electronic_invoice_username')
        res['zue_electronic_invoice_password'] = get_param('zue_electronic_invoice.zue_electronic_invoice_password')
        res['zue_electronic_invoice_company_id'] = get_param('zue_electronic_invoice.zue_electronic_invoice_company_id')
        res['zue_electronic_invoice_account_id'] = get_param('zue_electronic_invoice.zue_electronic_invoice_account_id')
        res['zue_electronic_invoice_environment'] = get_param('zue_electronic_invoice.zue_electronic_invoice_environment')
        return res



