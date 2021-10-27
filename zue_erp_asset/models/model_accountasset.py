# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.base.models.res_bank import sanitize_account_number


import logging
_logger = logging.getLogger(__name__)
#---------------------------Modelo account.asset-------------------------------#

class AccountAsset(models.Model):
    _inherit = 'account.asset'
    
    move_ids = fields.Many2one(related='original_move_line_ids.move_id', string='Movimiento Original', readonly=True, copy=False)
    x_partner = fields.Many2one('res.partner', string='Asociado', track_visibility='onchange')
    x_accumulated_depreciation = fields.Float(string='Depreciación acumulada')
    x_asset_plate = fields.Char(string='Placa del activo')
    x_date_depreciation = fields.Date(string='Fecha depreciación total')
    x_deprecieted_periods = fields.Integer(string='Periodos depreciados')
    x_date_purchase_his = fields.Date(string='Fecha de Compra (Histórica)')
    x_history_cost = fields.Float(string='Costo histórico')
    x_serial = fields.Char(string='Serial')
    x_ussefull_life = fields.Integer(string='Vida útil')
        