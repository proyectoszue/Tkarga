from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


#class res_partner(models.Model):
    #_inherit = 'res.partner'

    #payroll_dispersion_account = fields.Many2one('account.journal', string='Cuenta bancaria dispersora nómina', domain="[('is_payroll_spreader', '=', True)]")

class res_partner_bank(models.Model):
    _inherit = 'res.partner.bank'

    type_account = fields.Selection(selection_add=[('DP', 'Daviplata'),('N', 'Nequi')], ondelete={"DP": "set default","N": "set default"})
    # company_id = fields.Many2one('res.company', string="Compañía", default=lambda self: self.env.company)
    company_id = fields.Many2one('res.company', 'Compañía', related=False, store=True, readonly=False)
    payroll_dispersion_account = fields.Many2one('account.journal', string='Cuenta bancaria dispersora nómina', domain="[('is_payroll_spreader', '=', True)]")
