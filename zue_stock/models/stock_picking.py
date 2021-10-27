# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError 

class stock_picking(models.Model): 
    _inherit = 'stock.picking'
    
    @api.depends('move_ids_without_package.account_move_ids')
    def _compute_account_move_ids(self):
        for record in self:
            obj_account_moves = self.env['account.move']
            for line in record.move_ids_without_package:
                obj_account_moves += line.account_move_ids            
            record.account_move_ids = obj_account_moves

    account_move_ids = fields.Many2many('account.move', compute='_compute_account_move_ids', string='Contabilidad', copy=False)
    