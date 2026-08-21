from odoo import fields, models, api, tools
from odoo.exceptions import UserError, ValidationError

class zue_concept_accounts(models.Model):
    _name = 'zue.concept.accounts'
    _description = 'Agrupar cuentas por concepto'
    _rec_name = 'z_concept'

    z_concept = fields.Char('Concepto', required= True)
    z_company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)
    z_accounting_details_ids = fields.Many2many('account.account', string='Cuenta')
    z_excluded_thirdparty_ids = fields.Many2many('res.partner', string='Tercero Excluidos')
    z_type_account = fields.Selection([('1','Impuesto'),
                                       ('2','PYG')], 'Tipo de cuenta')

