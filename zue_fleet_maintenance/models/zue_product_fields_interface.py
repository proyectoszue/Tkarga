from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    familia = fields.Many2one(related='product_id.family_id')
    marca = fields.Many2one(related='product_id.brand_id')
    linea = fields.Many2one(related='product_id.vehiculo_linea_id')
    sistema = fields.Many2one(related='product_id.system_id')

class stock_move(models.Model):
    _inherit = 'stock.move'

    familia = fields.Many2one(related='product_id.family_id')
    marca = fields.Many2one(related='product_id.brand_id')
    linea = fields.Many2one(related='product_id.vehiculo_linea_id')
    sistema = fields.Many2one(related='product_id.system_id')

class stock_move_line(models.Model):
    _inherit = 'stock.move.line'

    familia = fields.Many2one(related='product_id.family_id')
    marca = fields.Many2one(related='product_id.brand_id')
    linea = fields.Many2one(related='product_id.vehiculo_linea_id')
    sistema = fields.Many2one(related='product_id.system_id')
