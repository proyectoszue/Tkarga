# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class account_journal(models.Model):
    _inherit = 'account.journal'

    type = fields.Selection(track_visibility='onchange')
    company_id = fields.Many2one(track_visibility='onchange')
    code = fields.Char(track_visibility='onchange')
    sequence_number_next = fields.Integer(track_visibility='onchange')
    default_debit_account_id = fields.Many2one(track_visibility='onchange')
    default_credit_account_id = fields.Many2one(track_visibility='onchange')
    dian_authorization_number = fields.Char('Resolución Facturación')
    dian_authorization_date = fields.Date('Fecha Resolución')
    dian_authorization_end_date = fields.Date('Fecha Final Resolución')
    dian_min_range_number = fields.Integer('Número Inicial')
    dian_max_range_number = fields.Integer('Número Final')