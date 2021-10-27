from odoo import fields, models

class ProductTemplate(models.Model):
    _inherit = "product.template"

    # Encabezado 
    sale_ok = fields.Boolean(track_visibility='onchange')
    purchase_ok = fields.Boolean(track_visibility='onchange')
    # Informacion general
    categ_id = fields.Many2one(track_visibility='onchange')
    default_code = fields.Char(track_visibility='onchange')
    barcode = fields.Char(track_visibility='onchange')
    codigo_fabrica = fields.Char(track_visibility='onchange')
    uom_id = fields.Many2one(track_visibility='onchange')
    company_id = fields.Many2one(track_visibility='onchange')
    taxes_id = fields.Many2many(track_visibility='onchange')
    list_price = fields.Float(track_visibility='onchange')
    standard_price = fields.Float(track_visibility='onchange')
    uom_po_id = fields.Many2one(track_visibility='onchange')
    #unspsc_code_id = fields.Many2one(track_visibility='onchange', string='Código UNSPSC')
    # Inventario
    route_ids = fields.Many2many(track_visibility='onchange')
    property_stock_production = fields.Many2one(track_visibility='onchange')
    property_stock_inventory = fields.Many2one(track_visibility='onchange')
    # Contabilidad
    property_account_income_id = fields.Many2one(track_visibility='onchange')
    property_account_expense_id = fields.Many2one(track_visibility='onchange')
    property_account_creditor_price_difference = fields.Many2one(track_visibility='onchange')
    # Ventas
    #invoice_policy = fields.Selection(track_visibility='onchange')
    #expense_policy = fields.Selection(track_visibility='onchange')