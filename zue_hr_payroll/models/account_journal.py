from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class Account_journal(models.Model):
    _inherit = 'account.journal'

    is_payroll_spreader = fields.Boolean('Es dispersor de nómina')
