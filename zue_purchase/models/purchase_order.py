from odoo import models, fields, _, api
from odoo.exceptions import ValidationError, UserError

class purchase_order(models.Model):
    _inherit = 'purchase.order'

    iva_amount = fields.Float('Valor IVA', compute='_compute_amount_iva', store=True)
      
    @api.depends('order_line')
    def _compute_amount_iva(self): 
        iva_amount = 0

        if self.order_line.taxes_id:
            obj_taxes = self.env['account.tax'].search([('name', 'ilike', 'IVA')])

            percent = obj_taxes[0].amount

            for lines in self.order_line:
                for taxes in lines.taxes_id:
                    if taxes.ids[0] in obj_taxes.ids:
                        iva_amount += lines.price_subtotal * percent / 100

        self.iva_amount = iva_amount

    #Validación Cuenta Analitica
    @api.constrains('order_line')
    def _check_order_line_analytic_account(self):  
        for record in self:
            for lines in record.order_line:
                if not lines.account_analytic_id:
                    raise ValidationError(_('El producto "' + lines.product_id.name + '" no tiene cuenta analítica. Por favor verifique!'))
            
            