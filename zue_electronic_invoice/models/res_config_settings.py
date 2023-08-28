from odoo import fields, models, api

# RESPONSABILIDADES RUT
class x_responsibilities_rut(models.Model):
    _name = 'zue.responsibilities_rut'
    _description = 'Responsabilidades RUT'

    code = fields.Char(string='Identificador', required=True)
    description = fields.Char(string='Descripción', required=True)
    valid_for_fe = fields.Boolean(string='Valido para facturación electrónica')

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "{} | {}".format(record.code, record.description)))
        return result

class ResPartner(models.Model):
    _inherit = 'res.partner'
    # INFORMACION TRIBUTARIA
    x_tax_responsibilities = fields.Many2many('zue.responsibilities_rut', string='Responsabilidades Tributarias',
                                              tracking=True, ondelete='restrict')
    #CAMPOS FACTURACIÓN ELECTRONICA
    zue_electronic_invoice_fiscal_regimen = fields.Selection([('48','Impuestos sobre la venta del IVA'),
                                                              ('49','No responsables del IVA')],string='Regimen Fiscal')
    zue_electronic_invoice_responsable_iva = fields.Boolean(string='Responsable de IVA')
    obliged_invoice = fields.Boolean(string='Obligado a facturar')

class ResCompany(models.Model):
    _inherit = 'res.company'

    zue_electronic_invoice_operator = fields.Selection([('FacturaTech', 'FacturaTech')],
                                                       string='Operador', default='FacturaTech')
    zue_electronic_invoice_username = fields.Char(string='Usuario Proveedor Tecnológico')
    zue_electronic_invoice_password = fields.Char(string='Contraseña Proveedor')
    zue_electronic_invoice_company_id = fields.Char(string='Company ID')
    zue_electronic_invoice_account_id = fields.Char(string='Account ID')
    zue_electronic_invoice_environment = fields.Selection([('prod', 'Producción'), ('test', 'Pruebas')],
                                                          string='Ambiente', default='prod')
    zue_electronic_invoice_disable_sending = fields.Boolean(string='Deshabilitar Facturación Electrónica')

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    zue_electronic_invoice_operator = fields.Selection(related='company_id.zue_electronic_invoice_operator', string='Operador',readonly=False)
    zue_electronic_invoice_username = fields.Char(related='company_id.zue_electronic_invoice_username',string='Usuario Proveedor Tecnológico', readonly=False)
    zue_electronic_invoice_password = fields.Char(related='company_id.zue_electronic_invoice_password',string='Contraseña Proveedor', readonly=False)
    zue_electronic_invoice_company_id = fields.Char(related='company_id.zue_electronic_invoice_company_id',string='Company ID', readonly=False)
    zue_electronic_invoice_account_id = fields.Char(related='company_id.zue_electronic_invoice_account_id',string='Account ID', readonly=False)
    zue_electronic_invoice_environment = fields.Selection(related='company_id.zue_electronic_invoice_environment', string='Ambiente',readonly=False)
    zue_electronic_invoice_disable_sending = fields.Boolean(related='company_id.zue_electronic_invoice_disable_sending', string='Deshabilitar Facturación Electrónica',readonly=False)