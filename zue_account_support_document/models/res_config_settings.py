# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    journal_support_document_co = fields.Many2one('account.journal', string='Diario doc. soporte')
    journal_nc_support_document_co = fields.Many2one('account.journal', string='Diario NC doc. soporte')
    zue_support_document_username = fields.Char(string='Usuario Proveedor Tecnológico Doc Soporte')
    zue_support_document_password = fields.Char(string='Contraseña Proveedor Doc Soporte')

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    #journal_support_document_co = fields.Many2one('account.journal',string='Diario doc. soporte', config_parameter='zue_account_support_document.journal_support_document_co')
    journal_support_document_co = fields.Many2one(related='company_id.journal_support_document_co', string='Diario doc. soporte', readonly=False)
    journal_nc_support_document_co = fields.Many2one(related='company_id.journal_nc_support_document_co', string='Diario NC doc. soporte', readonly=False)
    zue_support_document_username = fields.Char(related='company_id.zue_support_document_username', string='Usuario doc. soporte', readonly=False)
    zue_support_document_password = fields.Char(related='company_id.zue_support_document_password', string='Contraseña doc. soporte', readonly=False)



