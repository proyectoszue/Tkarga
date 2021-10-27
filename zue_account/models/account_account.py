
from odoo import models, fields, api, _

#PLAN CONTABLE - PUC

class account_account(models.Model):
    _name = 'account.account'
    _inherit = ['account.account','mail.thread', 'mail.activity.mixin']

    required_analytic_account = fields.Boolean('Obliga cuenta analítica', track_visibility='onchange')
    required_partner = fields.Boolean('Obliga tercero', track_visibility='onchange')
    accounting_class = fields.Char('Clase', track_visibility='onchange')
    code = fields.Char(track_visibility='onchange')
    user_type_id = fields.Many2one(track_visibility='onchange')
    tax_ids = fields.Many2many(track_visibility='onchange')
    group_id = fields.Many2one(track_visibility='onchange')
    company_id = fields.Many2one(track_visibility='onchange')
    account_distribution = fields.Boolean(track_visibility='onchange')