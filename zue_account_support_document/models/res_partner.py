# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    zue_electronic_invoice_fiscal_regimen = fields.Selection([
        ('48', 'Impuestos sobre la venta del IVA'),
        ('49', 'No responsables del IVA'),
    ], string='Regimen Fiscal')
    obliged_invoice = fields.Boolean(string='Obligado a facturar')
