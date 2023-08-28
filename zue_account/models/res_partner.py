# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    #TRACK VISIBILITY PESTAÑA CONTABILIDAD
    property_account_receivable_id = fields.Many2one(tracking=True)
    property_account_payable_id = fields.Many2one(tracking=True)
    bank_ids = fields.One2many(tracking=True)
    #Operaciones Recíprocas
    z_partner_with_reciprocal_operations = fields.Boolean(string='Maneja operación recíproca')
    z_code_partner_reciprocal_operations = fields.Char(string='Código del tercero')
    # CAMPOS FACTURACIÓN ELECTRONICA
    zue_electronic_invoice_fiscal_regimen = fields.Selection([('48', 'Impuestos sobre la venta del IVA'),
                                                              ('49', 'No responsables del IVA')],
                                                             string='Regimen Fiscal')
    zue_electronic_invoice_responsable_iva = fields.Boolean(string='Responsable de IVA')

class res_company(models.Model):
    _inherit = 'res.company'

    note_id = fields.One2many('res.company.note', 'company_id', 'Notas')

class res_company_note(models.Model):
    _name = 'res.company.note'
    _description = 'Notas por compañia para Facturación electrónica'

    note = fields.Char('Notas')
    company_id = fields.Many2one('res.company', 'Compañia',default=lambda self: self.env.company)
