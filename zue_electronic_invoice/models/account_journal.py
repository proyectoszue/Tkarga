# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class account_journal(models.Model):
    _inherit = 'account.journal'

    dian_authorization_number = fields.Char('Resolución Facturación')
    dian_authorization_date = fields.Date('Fecha Resolución')
    dian_authorization_end_date = fields.Date('Fecha Final Resolución')
    dian_min_range_number = fields.Integer('Número Inicial')
    dian_max_range_number = fields.Integer('Número Final')
    z_disable_dian_sending = fields.Boolean(string='Deshabilitar envío DIAN')
    z_is_debit_note = fields.Boolean(string='Nota Débito FE')
    z_is_credit_note = fields.Boolean(string='Nota Crédito FE')
    z_expiration_folios = fields.Integer('Folios de vencimiento FE')
    z_expiration_days = fields.Integer('Días de vencimiento FE')
    z_generate_alert = fields.Boolean(string='Generar Alerta')


class AccountDebitNote(models.TransientModel):
    _inherit = 'account.debit.note'

    def create_debit(self):
        self.ensure_one()
        journal = self.journal_id or (self.move_ids[:1].journal_id if self.move_ids else False)
        if journal and not journal.z_is_debit_note:
            raise ValidationError(_('El diario seleccionado no ha sido marcado como nota débito. Por favor verifique!'))
        return super(AccountDebitNote, self).create_debit()

class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    description_code_credit = fields.Selection([('1', 'Devolución parcial de los bienes y/o no aceptación parcial del servicio'),
                                                 ('2', 'Anulación de factura electrónica'),
                                                 ('3', 'Rebaja o descuento parcial o total'),
                                                 ('4', 'Ajuste de precio'),
                                                 ('6', 'Descuento comercial por pronto pago'),
                                                 ('7', 'Descuento comercial por volumen de ventas'),
                                                 ('8', 'Refacturación'),
                                                 ('5', 'Otros')], string='Concepto nota crédito')
    description_code_debit = fields.Selection([('1', 'Intereses'),
                                               ('2', 'Gastos por cobrar'),
                                               ('3', 'Cambio de valor'),
                                               ('4', 'Otros')], string='Concepto nota débito')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Cuenta analítica')

    def _prepare_default_reversal(self, move):
        values = super(AccountMoveReversal, self)._prepare_default_reversal(move)
        values.update({
            'description_code_credit': self.description_code_credit,
            'description_code_debit': self.description_code_debit,
        })
        return values

    def reverse_moves(self, is_modify=False):
        self.ensure_one()
        if self.description_code_debit and not self.journal_id.z_is_debit_note:
            raise ValidationError(_('El diario seleccionado no ha sido marcado como nota débito. Por favor verifique!'))

        if self.description_code_credit and not self.journal_id.z_is_credit_note:
            raise ValidationError(_('El diario seleccionado no ha sido marcado como nota crédito. Por favor verifique!'))

        return super(AccountMoveReversal, self).reverse_moves(is_modify=is_modify)


class account_move(models.Model):
    _inherit = 'account.move'

    @api.model_create_multi
    def create(self, values_list):
        invoice_res = super(account_move, self).create(values_list)

        for invoice in invoice_res:
            if invoice.move_type in ('out_refund', 'in_refund') and not invoice.journal_id.z_is_credit_note:
                raise ValidationError(_('El diario seleccionado no ha sido marcado como nota crédito. Por favor verifique!'))

        return invoice_res
