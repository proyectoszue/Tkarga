from odoo import fields, models, api

# RESPONSABILIDADES RUT
class x_responsibilities_rut(models.Model):
    _name = 'zue.responsibilities_rut'
    _description = 'Responsabilidades RUT'

    code = fields.Char(string='Identificador', required=True)
    description = fields.Char(string='Descripción', required=True)
    valid_for_fe = fields.Boolean(string='Valido para facturación electrónica')

    @api.depends('code', 'description')
    def _compute_display_name(self):
        for record in self:
            record.display_name = "{} | {}".format(record.code or "", record.description or "")
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
    z_entrego_rut = fields.Boolean(string='Entregó RUT', default=False, tracking=True)

    def get_ds_dian_id_type_code(self):
        self.ensure_one()
        if self.z_entrego_rut:
            return '31'
        return str(self.l10n_latam_identification_type_id.z_code_dian or '')

    def get_ds_digit_verification(self):
        self.ensure_one()
        if self.z_entrego_rut:
            return self._get_ds_verification_digit_from_vat()
        if self.x_digit_verification is not False and self.x_digit_verification is not None:
            return self.x_digit_verification
        return ''

    def _get_ds_verification_digit_from_vat(self):
        self.ensure_one()
        if not self.vat:
            return ''
        multiplication_factors = [71, 67, 59, 53, 47, 43, 41, 37, 29, 23, 19, 17, 13, 7, 3]
        padded_vat = str(self.vat).split('-')[0]
        if len(padded_vat) > len(multiplication_factors):
            return ''
        while len(padded_vat) < len(multiplication_factors):
            padded_vat = '0' + padded_vat
        try:
            number = sum(int(vat_number) * multiplication_factors[index]
                         for index, vat_number in enumerate(padded_vat))
            number %= 11
            return number if number < 2 else 11 - number
        except ValueError:
            return ''

class ResCompany(models.Model):
    _inherit = 'res.company'

    zue_electronic_invoice_operator = fields.Selection([('FacturaTech', 'FacturaTech'),
                                                        ('Infile', 'Infile')],
                                                       string='Operador', default='FacturaTech')
    zue_electronic_invoice_format = fields.Selection([('xml', 'XML'),
                                                      ('json', 'JSON')],
                                                     string='Formato de Documento', default='xml',
                                                     help='Seleccione el formato que utiliza el operador tecnológico')
    zue_electronic_invoice_username = fields.Char(string='Usuario Proveedor Tecnológico')
    zue_electronic_invoice_password = fields.Char(string='Contraseña Proveedor')
    zue_electronic_invoice_company_id = fields.Char(string='ID de compañía del proveedor')
    zue_electronic_invoice_account_id = fields.Char(string='ID de cuenta del proveedor')
    zue_electronic_invoice_environment = fields.Selection([('prod', 'Producción'), ('test', 'Pruebas')],
                                                          string='Ambiente', default='prod')
    zue_electronic_invoice_disable_sending = fields.Boolean(string='Deshabilitar Facturación Electrónica')

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    zue_electronic_invoice_operator = fields.Selection(related='company_id.zue_electronic_invoice_operator', string='Operador',readonly=False)
    zue_electronic_invoice_format = fields.Selection(related='company_id.zue_electronic_invoice_format', string='Formato de Documento', readonly=False)
    zue_electronic_invoice_username = fields.Char(related='company_id.zue_electronic_invoice_username',string='Usuario Proveedor Tecnológico', readonly=False)
    zue_electronic_invoice_password = fields.Char(related='company_id.zue_electronic_invoice_password',string='Contraseña Proveedor', readonly=False)
    zue_electronic_invoice_company_id = fields.Char(related='company_id.zue_electronic_invoice_company_id',string='ID de compañía del proveedor', readonly=False)
    zue_electronic_invoice_account_id = fields.Char(related='company_id.zue_electronic_invoice_account_id',string='ID de cuenta del proveedor', readonly=False)
    zue_electronic_invoice_environment = fields.Selection(related='company_id.zue_electronic_invoice_environment', string='Ambiente',readonly=False)
    zue_electronic_invoice_disable_sending = fields.Boolean(related='company_id.zue_electronic_invoice_disable_sending', string='Deshabilitar Facturación Electrónica',readonly=False)
