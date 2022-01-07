# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError 
from odoo.tools.float_utils import float_compare

class stock_move(models.Model): 
    _inherit = 'stock.move'
    
    analytic_account_id = fields.Many2one('account.analytic.account', 'Cuenta analítica')

    @api.constrains('analytic_account_id')
    def _check_analytic_account_id(self):  
        for record in self:
            if record.picking_id and not record.analytic_account_id:           
                raise ValidationError(_('El producto "' + record.product_id.name + '" no tiene cuenta analítica. Por favor verifique!'))           
    
class stock_immediate_transfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'
    
    def process(self):
        r = super(stock_immediate_transfer, self).process()

        for stock_pick in self.pick_ids:
            for stock_move in stock_pick.move_ids_without_package:
                obj_account_move = self.env['account.move'].search([('stock_move_id', '=', stock_move.id)])
                obj_account_move_line = self.env['account.move.line'].search([('move_id', 'in', obj_account_move.ids)])

                obj_account_move_line.write({'analytic_account_id': stock_move.analytic_account_id.id})

            if stock_pick.workorder_id.work_task_ids:
                stock_pick.workorder_id.work_task_ids.compute_tasks_cost()
        
        return r

class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    #Se reemplaza metodo original _prepare_picking agregando la cuenta analitica
    def _prepare_stock_moves(self, picking):
        """ Prepare the stock moves data for one order line. This function returns a list of
        dictionary ready to be used in stock.move's create()
        """
        self.ensure_one()
        res = []
        if self.product_id.type not in ['product', 'consu']:
            return res
        qty = 0.0
        price_unit = self._get_stock_move_price_unit()
        outgoing_moves, incoming_moves = self._get_outgoing_incoming_moves()
        for move in outgoing_moves:
            qty -= move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom, rounding_method='HALF-UP')
        for move in incoming_moves:
            qty += move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom, rounding_method='HALF-UP')
        description_picking = self.product_id.with_context(lang=self.order_id.dest_address_id.lang or self.env.user.lang)._get_description(self.order_id.picking_type_id)
        template = {
            # truncate to 2000 to avoid triggering index limit error
            # TODO: remove index in master?
            'name': (self.name or '')[:2000],
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'date': self.order_id.date_order,
            'date_expected': self.date_planned,
            'location_id': self.order_id.partner_id.property_stock_supplier.id,
            'location_dest_id': self.order_id._get_destination_location(),
            'picking_id': picking.id,
            'partner_id': self.order_id.dest_address_id.id,
            'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'purchase_line_id': self.id,
            'company_id': self.order_id.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': self.order_id.picking_type_id.id,
            'group_id': self.order_id.group_id.id,
            'origin': self.order_id.name,
            'propagate_date': self.propagate_date,
            'propagate_date_minimum_delta': self.propagate_date_minimum_delta,
            'description_picking': description_picking,
            'propagate_cancel': self.propagate_cancel,
            'route_ids': self.order_id.picking_type_id.warehouse_id and [(6, 0, [x.id for x in self.order_id.picking_type_id.warehouse_id.route_ids])] or [],
            'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
            #Se agrega CUENTA ANALITICA
            'analytic_account_id':self.account_analytic_id.id,
        }
        diff_quantity = self.product_qty - qty
        if float_compare(diff_quantity, 0.0,  precision_rounding=self.product_uom.rounding) > 0:
            po_line_uom = self.product_uom
            quant_uom = self.product_id.uom_id
            product_uom_qty, product_uom = po_line_uom._adjust_uom_quantities(diff_quantity, quant_uom)
            template['product_uom_qty'] = product_uom_qty
            template['product_uom'] = product_uom.id
            res.append(template)
        return res

class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    def _process(self, cancel_backorder=False):
        for confirmation in self:
            if cancel_backorder:
                for pick_id in confirmation.pick_ids:
                    moves_to_log = {}
                    for move in pick_id.move_lines:
                        if float_compare(move.product_uom_qty,
                                         move.quantity_done,
                                         precision_rounding=move.product_uom.rounding) > 0:
                            moves_to_log[move] = (move.quantity_done, move.product_uom_qty)
                    pick_id._log_less_quantities_than_expected(moves_to_log)
            confirmation.pick_ids.with_context(cancel_backorder=cancel_backorder).action_done()

            for stock_pick in confirmation.pick_ids:
                for stock_move in stock_pick.move_ids_without_package:
                    obj_account_move = self.env['account.move'].search([('stock_move_id', '=', stock_move.id)])
                    obj_account_move_line = self.env['account.move.line'].search([('move_id', 'in', obj_account_move.ids)])

                    obj_account_move_line.write({'analytic_account_id': stock_move.analytic_account_id.id})

                if stock_pick.workorder_id.work_task_ids:
                    stock_pick.workorder_id.work_task_ids.compute_tasks_cost()

    def process(self):
        self._process()

    def process_cancel_backorder(self):
        self._process(cancel_backorder=True)
