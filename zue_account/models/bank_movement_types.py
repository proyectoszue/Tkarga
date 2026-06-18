from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class zue_bank_movement_types(models.Model):
    _name = 'zue.bank.movement.types'
    _description = 'Tabla de movimientos multicash'

    z_movement_types = fields.Char(string='Tipo de movimiento')
    z_movement_name = fields.Char(string='Nombre del movimiento')
    z_bank_id = fields.Many2one('res.bank', string='Banco')
