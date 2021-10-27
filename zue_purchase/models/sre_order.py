from odoo import models, fields, _, api
import datetime
from odoo.exceptions import ValidationError, UserError


class sre_order(models.Model):
    _name = 'sre.order'
    _inherit = ['mail.thread']
    _description = 'Solicitud de recursos economicos'

    name = fields.Char('Nombre')
    date = fields.Date('Fecha solicitud', default=datetime.datetime.utcnow(), required=True)
    branch_id = fields.Many2one('zue.res.branch', 'Sucursal', required=True)
    consignar = fields.Selection([('caja_menor','Caja Menor'),('cuenta_ahorros','Cuenta Ahorros'),('cuenta_corriente','Cuenta corriente'),('otros','Otros')],'Consignar', default='caja_menor', required=True)
    partner_id = fields.Many2one('res.partner', 'Solicitante')
    term_paid_id = fields.Many2one('account.payment.term','Plazo de pago')
    type_paid_id = fields.Many2one('payment.type','Tipo de pago')
    amount_untaxed = fields.Float('Sub total', default=0.0)
    amount_tax = fields.Float('Impuestos', default=0.0)
    amount_total = fields.Float('Total', default=0.0)
    sre_order_line_id = fields.One2many('sre.order.line', 'sre_id', string='Sre lineas')
    state = fields.Selection([('solicitado','Solicitado'),('revisado','Revisado'),('aprobado','Aprobado'),('pagado','Pagado'),('anulado','Anulado'),('legalizacion_borrador','Legalizacion en borrador'),('legalizacion_proceso','En proceso legalizacion'),('legalizado','Legalizado')], 'Estado', default='solicitado', track_visibility='onchange')
    comments = fields.Text('Observaciones')
    move_id = fields.One2many('account.move', 'sre_order_id','Asiento solicitud')
    nota_rechazo = fields.Text('Causa de rechazo')
    # counter_legalization = fields.Integer(compute='compute_counter_legalization', string='Legalización', store=True)
    counter_moves = fields.Integer(string='Movimientos')
    company_id = fields.Many2one('res.company', 'Compañia', required=True, default=lambda self: self.env.company.id)


    @api.model
    def create(self, vals):
        if vals.get('sre_order_line_id'):
            if vals.get('name','/')=='/':
                vals['name'] = self.env['ir.sequence'].next_by_code('sre.order') or '/'
         
            order =  super(sre_order, self).create(vals)
            
            return order
        else:
            raise UserError(_('No hay detalles en la solicitud'))

    @api.onchange('sre_order_line_id')
    def on_change_sre_order_line_id(self):
        self.calculate_totals()

    @api.depends('sre_order_line_id','amount_untaxed','amount_tax','amount_total')
    def calculate_totals(self):
        taxes_t = 0
        subtotal = 0
        total = 0
        for line in self.sre_order_line_id:
            line_price = line.amount
            line_qty = line.qty

            if line.taxes_id and line_price and line_qty:
                taxes = line.taxes_id.compute_all(price_unit=line_price,
                                            quantity=line_qty,
                                            partner=line.sre_id.partner_id)
                subtotal +=  round(taxes['total_excluded'])
                total += round(taxes['total_included'])

                for tax in taxes['taxes']:
                    taxes_t += tax['amount']

            else:
                subtotal += (line_price * line_qty)
                total += (line_price * line_qty)

        self.amount_untaxed = subtotal
        self.amount_tax = taxes_t
        self.amount_total = total

    # def compute_counter_legalization(self):
    #     for record in self:
    #         count = self.env['account.move'].search_count([('sre_order_id', '=', record.id)])
    #         if not count:
    #             record.counter_legalization = 0
    #         else:
    #             record.counter_legalization = count

    # def return_action_to_open_moves(self):
    #     res = {
    #         'name': 'Movimiento',
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'tree,form',
    #         'res_model': 'account.move',
    #         'domain': "[('ref','=','" + self.name + "'),('type', '=', 'entry')]",
    #         'context': "{'default_type': 'entry'}"
    #     }
    #     return res

    # def return_action_to_open(self):
    #     res = {
    #         'name': 'Legalización',
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'tree,form',
    #         'res_model': 'account.move',
    #         'domain': "[('name','in',[" + str(self._ids[0]) + "]),('type', '=', 'in_invoice'), ('is_rcm', '=', True)]",
    #         'context': "{'default_type': 'in_invoice', 'default_is_rcm': True}"
    #     }
    #     return res

    def wkf_sre_anular(self):
        if self.state == 'aprobado':
            obj_account_move = self.env['account.move'].search([('ref', '=', self.name)])

            if obj_account_move:
                for record in obj_account_move:
                    if record.state == 'posted':
                        record.button_draft()
                        record.button_cancel()
                    else:
                        record.button_cancel()
            
            self.write({'state' : 'anulado'})
            return True

        elif self.state in ['solicitado', 'revisado']:
            self.write({'state' : 'anulado'})
            return True
        else:
            raise ValidationError(_("El estado del movimiento a cambiado actualice la pagina el nuevo estado es %s!" % self.state))

    def wkf_sre_revisado(self):
        if self.state == 'solicitado':
            self.write({'state' : 'revisado'})
        else:
            raise ValidationError(_("Error!. El estado del movimiento a cambiado actualice la pagina el nuevo estado es %s!" % self.state))

    def wkf_sre_confirmado(self):
        if self.state == 'revisado':
            move_line_vals = []
            descripcion = ''
            valor = 0

            for record in self.sre_order_line_id:
                descripcion = record.name
                break
            
            # Cuentas tercero
            cta_debito = self.partner_id.property_account_payable_id.id

            if not cta_debito:
                raise ValidationError(_("Error!. El tercero '%s' no tiene una cuenta a pagar asociada. Por favor verifique!" % self.partner_id.name))

            cta_credito = self.partner_id.x_property_account_advance_id.id

            if not cta_credito:
                raise ValidationError(_("Error!. El tercero '%s' no tiene una cuenta de anticipo asociada. Por favor verifique!" % self.partner_id.name))

            valor = self.amount_untaxed

            # Débitos
            line = (0, 0, {'account_id': cta_debito, 
                            'name': descripcion,
                            'debit': valor,
                            'credit': 0,
                            'partner_id': self.partner_id.id,
                            })
            move_line_vals.append(line)

            if self.consignar == 'caja_menor':
                obj_account = self.env['account.account'].search(['&',('code', '=', '531595'), ('company_id', '=', self.company_id.id)], limit=1)

                if not obj_account:
                    raise ValidationError(_("Error!. No se ha parametrizado la cuenta del 4x1000. Por favor verifique!"))

                # Débitos 4 x 1000
                line = (0, 0, {'account_id': obj_account.id, 
                                'name': descripcion,
                                'debit': valor*(4/1000),
                                'credit': 0,
                                'partner_id': self.partner_id.id,
                                })
                move_line_vals.append(line)

            # Créditos
            if self.consignar == 'caja_menor':
                valor = valor + (valor*(4/1000))

            line = (0, 0, {'account_id': cta_credito, 
                            'name': descripcion,
                            'debit': 0,
                            'credit': valor,
                            'partner_id': self.partner_id.id,
                            })
            move_line_vals.append(line)
            
            obj_journal = self.env['account.journal'].search(['&',('name', '=', 'Anticipos'), ('company_id', '=', self.company_id.id)], limit=1)
            
            if not obj_journal:
                raise ValidationError(_("Error!. No se encontró el diario 'Anticipos'. Por favor verifique!"))

            # Movimiento contable
            move_vals = {
                "ref": self.name,
                "type": 'entry',
                "date": datetime.date.today(),
                "partner_id": self.partner_id.id,
                "journal_id": obj_journal.id,
                "company_id": self.company_id.id,
                "line_ids": move_line_vals,
                "sre_order_id": self.id,
            }
            obj_account_move = self.env['account.move'].create(move_vals)
            obj_account_move.action_post()

            self.write({'state' : 'aprobado',
                        'counter_moves' : 1})
        else:
            raise ValidationError(_("Error!. El estado del movimiento a cambiado actualice la pagina el nuevo estado es %s!" % self.state))


class sre_order_line(models.Model):
    _name = 'sre.order.line'
    _description = 'Linea de la solicitud de recursos economicos'

    sre_id = fields.Many2one('sre.order', string='sre', ondelete="cascade")
    name = fields.Char('Descripcion', required=True)
    qty = fields.Float('Cantidad', required=True)
    account_analytic_id = fields.Many2one('account.analytic.account', 'Cuenta analitica', required=True)
    amount = fields.Float('Valor unitario', required=True)
    taxes_id = fields.Many2many('account.tax', string='Impuestos')
    amount_total = fields.Float(compute='_amount_line', string='Subtotal', store=True)

    @api.depends('qty','amount','taxes_id')
    def _amount_line(self):
        res = {}
        taxes_t = 0
        for line in self:
            line_price = line.amount
            line_qty = line.qty

            if line.taxes_id and line_price and line_qty:
                taxes = line.taxes_id.compute_all(price_unit=line_price,
                                            quantity=line_qty,
                                            partner=line.sre_id.partner_id)
                line.amount_total = round(taxes['total_included'])
            else:
                line.amount_total = line_price * line_qty

    
    # @api.onchange('name')
    # def set_consignar(self, consignar, context=None):
    #     return {'value':{'consignar':consignar}}

    # @api.depends('qty','amount')
    # def set_total(self):
    #     if amount and qty:
    #         return {'value':{'amount_total': amount * qty, 'amount_untax': amount * qty}}
    #     else:
    #         return {'value':{'amount_total': 0, 'amount_untax': 0}}


class payment_type(models.Model):
    _name = 'payment.type'
    _description = 'Tipo de pago'

    name= fields.Char('Nombre', size=64, required=True, help='Nombre del tipo de pago')
    code= fields.Char('Código', size=64, required=False, help='Especifica el código del tipo de pago')
    active= fields.Boolean('Active', default=True)
    note= fields.Text('Descripción', help='Descripción del tipo de pago')
   