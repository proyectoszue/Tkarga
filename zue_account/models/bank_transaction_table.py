from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class zue_bank_transaction_table(models.Model):
    _name = 'zue.bank.transaction.table'
    _description = 'Tabla de transacciones multicash'

    z_transaction_code = fields.Char(string='Código de transacción')
    z_account_nature = fields.Selection([('c', 'Crédito'),
                                       ('d', 'Débito')], string='Naturaleza')
    z_transaction_name = fields.Char(string='Nombre de la transaccion')
    z_bank_id = fields.Many2one('res.bank', string='Banco')

