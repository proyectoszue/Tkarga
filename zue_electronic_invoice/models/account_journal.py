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
        if not self.journal_id.z_is_debit_note:
            raise ValidationError(_('El diario seleccionado no ha sido marcado como nota débito. Por favor verifique!'))

        res = super(AccountDebitNote, self).create_debit()

class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    description_code_credit = fields.Selection([('1', 'Devolución parcial de los bienes y/o no aceptación parcial del servicio'),
                                                 ('2', 'Anulación de factura electrónica'),
                                                 ('3', 'Rebaja o descuento parcial o total'),
                                                 ('4', 'Ajuste de precio'),
                                                 ('5', 'Otros')], string='Concepto nota crédito')
    description_code_debit = fields.Selection([('1', 'Intereses'),
                                               ('2', 'Gastos por cobrar'),
                                               ('3', 'Cambio de valor'),
                                               ('4', 'Otros')], string='Concepto nota débito')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Cuenta analítica')

    def _prepare_default_reversal(self, move):
        reverse_date = self.date if self.date_mode == 'custom' else move.date
        return {
            'ref': _('Reversal of: %(move_name)s, %(reason)s', move_name=move.name, reason=self.reason)
            if self.reason
            else _('Reversal of: %s', move.name),
            'date': reverse_date,
            'invoice_date': move.is_invoice(include_receipts=True) and (self.date or move.date) or False,
            'journal_id': self.journal_id.id,
            'invoice_payment_term_id': None,
            'invoice_user_id': move.invoice_user_id.id,
            'auto_post': True if reverse_date > fields.Date.context_today(self) else False,
            'description_code_credit': self.description_code_credit,
            'description_code_debit': self.description_code_debit,
        }

    def reverse_moves(self):
        if self.description_code_debit and not self.journal_id.z_is_debit_note:
            raise ValidationError(_('El diario seleccionado no ha sido marcado como nota débito. Por favor verifique!'))

        if self.description_code_credit and not self.journal_id.z_is_credit_note:
            raise ValidationError(_('El diario seleccionado no ha sido marcado como nota crédito. Por favor verifique!'))

        super(AccountMoveReversal, self).reverse_moves()


class account_move(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        invoice = super(account_move, self).create(vals)

        if invoice.move_type in ('out_refund', 'in_refund') and not invoice.journal_id.z_is_credit_note:
            raise ValidationError(_('El diario seleccionado no ha sido marcado como nota crédito. Por favor verifique!'))

        return invoice