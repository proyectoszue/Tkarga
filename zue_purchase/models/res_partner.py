# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class res_partner(models.Model):
    _inherit = 'res.partner'

    #TRACK VISIBILITY PESTAÑA VENTA Y COMPRA
    property_account_position_id = fields.Many2one(track_visibility='onchange')
