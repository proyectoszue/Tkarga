# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class account_journal(models.Model):
    _inherit = 'account.journal'

    type = fields.Selection(track_visibility='onchange')
    company_id = fields.Many2one(track_visibility='onchange')
    code = fields.Char(track_visibility='onchange')
    sequence_number_next = fields.Integer(track_visibility='onchange')
    default_debit_account_id = fields.Many2one(track_visibility='onchange')
    default_credit_account_id = fields.Many2one(track_visibility='onchange')