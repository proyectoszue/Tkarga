from odoo import models, fields, api, _


class account_move(models.Model):
    _inherit = 'account.move'

    x_support_document_sent = fields.Boolean(string='Documento Soporte Enviado', default=False)


# class account_move_line(models.Model):
#     _inherit = 'account.move.line'
#
#     x_sent_support_document = fields.Boolean('Documento Soporte Enviado')