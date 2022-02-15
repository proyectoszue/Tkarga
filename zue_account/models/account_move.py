from odoo.exceptions import ValidationError, UserError
from odoo import models, fields, api, _

#MOVIMIENTO CONTABLE ENCABEZADO

class account_move(models.Model):
    _inherit = 'account.move'

    supplier_invoice_number = fields.Char(string='Nº de factura del proveedor',help="La referencia de esta factura proporcionada por el proveedor.", copy=False)
    supplier_invoice_attachment = fields.Many2one('documents.document',string="Soporte") #fields.Binary(string="Soporte")
    iva_amount = fields.Float('Valor IVA', compute='_compute_amount_iva', store=True)
    l10n_co_edi_type = fields.Selection([('1', 'Factura de venta'),
                                        ('2', 'Factura de exportación'),
                                        ('3', 'Notas electrónicas'),
                                        ('4', 'Factura de contingencia'),
                                        ], string='Tipo de Documento')

    #supplier_invoice_attachment_name = fields.Char(string="Soporte Filename")
    @api.depends('line_ids','invoice_line_ids')
    def _compute_amount_iva(self):
        iva_amount = 0

        if self.invoice_line_ids.tax_id:
            obj_taxes = self.env['account.tax'].search([('name', 'ilike', 'IVA')])

            percent = obj_taxes[0].amount

            for lines in self.invoice_line_ids:
                for taxes in lines.tax_ids:
                    if taxes.ids[0] in obj_taxes.ids:
                        iva_amount += lines.price_subtotal * percent / 100

        self.iva_amount = iva_amount

    @api.constrains('line_ids','invoice_line_ids')
    def _check_line_ids(self):
        for record in self:
            for lines in record.line_ids:
                if lines.required_partner and not lines.partner_id:
                    raise ValidationError(_(str(lines.ref)+' - La cuenta "' + lines.account_id.name + '" obliga un tercero y este no ha sido digitado. Por favor verifique!'))

                if lines.required_analytic_account and not lines.analytic_account_id:
                    raise ValidationError(_(str(lines.ref)+' - La cuenta "' + lines.account_id.name + '" obliga cuenta analítica y esta no ha sido digitada. Por favor verifique!'))

            for lines in record.invoice_line_ids:
                if lines.required_partner and not lines.partner_id:
                    raise ValidationError(_(str(lines.ref)+' - La cuenta "' + lines.account_id.name + '" obliga un tercero y este no ha sido digitado. Por favor verifique!'))

                if lines.required_analytic_account and not lines.analytic_account_id:
                    raise ValidationError(_(str(lines.ref)+' - La cuenta "' + lines.account_id.name + '" obliga cuenta analítica y esta no ha sido digitada. Por favor verifique!'))

    @api.constrains('supplier_invoice_number')
    def _check_supplier_invoice(self):
        for record in self:
            if record.type == 'in_invoice':
                obj_move = self.env['account.move'].search([('supplier_invoice_number','=',record.supplier_invoice_number),('id','!=',record.id)])
                if len(obj_move) > 0:
                    raise ValidationError('El número de factura digitado ya existe, por favor verificar.')