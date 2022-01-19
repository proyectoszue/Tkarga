# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class account_journal(models.Model):
    _inherit = 'account.journal'

    dian_authorization_number = fields.Char('Resolución Facturación')
    dian_authorization_date = fields.Date('Fecha Resolución')
    dian_authorization_end_date = fields.Date('Fecha Final Resolución')
    dian_min_range_number = fields.Integer('Número Inicial')
    dian_max_range_number = fields.Integer('Número Final')