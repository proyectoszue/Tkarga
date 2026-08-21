from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountReconcileModel(models.Model):
    _inherit = 'account.reconcile.model'

    def _get_invoice_matching_amls_result(self, st_line, partner, candidate_vals):
        def _create_result_dict(amls_values_list, status):
            if 'rejected' in status:
                return

            result = {'amls': self.env['account.move.line']}
            for aml_values in amls_values_list:
                result['amls'] |= aml_values['aml']

            if 'allow_write_off' in status and self.line_ids:
                result['status'] = 'write_off'

            if 'allow_auto_reconcile' in status and candidate_vals['allow_auto_reconcile'] and self.auto_reconcile:
                result['auto_reconcile'] = True

            return result

        st_line_currency = st_line.foreign_currency_id or st_line.currency_id
        st_line_amount = st_line._prepare_move_line_default_vals()[1]['amount_currency']
        sign = 1 if st_line_amount > 0.0 else -1

        amls = candidate_vals['amls']
        amls_values_list = []
        amls_with_epd_values_list = []
        same_currency_mode = amls.currency_id == st_line_currency
        for aml in amls:
            aml_values = {
                'aml': aml,
                'amount_residual': aml.amount_residual,
                'amount_residual_currency': aml.amount_residual_currency,
            }

            amls_values_list.append(aml_values)

            # Manage the early payment discount.
            if aml.move_id.invoice_payment_term_id:
                last_discount_date = aml.move_id.invoice_payment_term_id._get_last_discount_date(aml.move_id.date)
            else:
                last_discount_date = False
            if same_currency_mode \
                    and aml.move_id.move_type in ('out_invoice', 'out_receipt', 'in_invoice', 'in_receipt') \
                    and not aml.matched_debit_ids \
                    and not aml.matched_credit_ids \
                    and last_discount_date \
                    and st_line.date <= last_discount_date:

                rate = abs(aml.amount_currency) / abs(aml.balance) if aml.balance else 1.0
                amls_with_epd_values_list.append({
                    **aml_values,
                    'amount_residual': st_line.company_currency_id.round(aml.discount_amount_currency / rate),
                    'amount_residual_currency': aml.discount_amount_currency,
                })
            else:
                amls_with_epd_values_list.append(aml_values)

        def match_batch_amls(amls_values_list):
            if not same_currency_mode:
                return None, []

            kepts_amls_values_list = []
            sum_amount_residual_currency = 0.0
            for aml_values in amls_values_list:

                if st_line_currency.compare_amounts(st_line_amount, -aml_values['amount_residual_currency']) == 0:
                    # Special case: the amounts are the same, submit the line directly.
                    return 'perfect', [aml_values]

                if st_line_currency.compare_amounts(sign * (st_line_amount + sum_amount_residual_currency), 0.0) > 0:
                    # Here, we still have room for other candidates ; so we add the current one to the list we keep.
                    # Then, we continue iterating, even if there is no room anymore, just in case one of the following candidates
                    # is an exact match, which would then be preferred on the current candidates.
                    kepts_amls_values_list.append(aml_values)
                    sum_amount_residual_currency += aml_values['amount_residual_currency']

            if st_line_currency.is_zero(sign * (st_line_amount + sum_amount_residual_currency)):
                return 'perfect', kepts_amls_values_list
            elif kepts_amls_values_list:
                return 'partial', kepts_amls_values_list
            else:
                return None, []

        # Try to match a batch with the early payment feature. Only a perfect match is allowed.
        match_type, kepts_amls_values_list = match_batch_amls(amls_with_epd_values_list)
        if match_type != 'perfect':
            kepts_amls_values_list = []

        # Try to match the amls having the same currency as the statement line.
        if not kepts_amls_values_list:
            _match_type, kepts_amls_values_list = match_batch_amls(amls_values_list)

        # Try to match the whole candidates.
        if not kepts_amls_values_list:
            kepts_amls_values_list = amls_values_list

        # Try to match the amls having the same currency as the statement line.
        if kepts_amls_values_list:
            status = self._check_rule_propositions(st_line, kepts_amls_values_list)

            # ===== INICIO Lógica ZUE - Perfect Match =====
            # Fuerza auto-reconciliación cuando:
            # - Hay un único AML,
            # - La regla tiene 'allow_auto_reconcile' (como en v15),
            # - El partner debe coincidir (self.match_partner),
            # - El monto del extracto es exactamente el negativo del residual en moneda.
            do_reconcile = False
            if self.match_partner and len(kepts_amls_values_list) == 1:
                aml_val = kepts_amls_values_list[0]
                if st_line_currency.compare_amounts(st_line_amount, -aml_val['amount_residual_currency']) == 0:
                    do_reconcile = True

            if do_reconcile and 'allow_auto_reconcile' in status and candidate_vals.get('allow_auto_reconcile') and self.auto_reconcile:
                forced_result = {'amls': self.env['account.move.line']}
                for v in kepts_amls_values_list:
                    forced_result['amls'] |= v['aml']
                forced_result['auto_reconcile'] = True
                if 'allow_write_off' in status and self.line_ids:
                    forced_result['status'] = 'write_off'

                return forced_result
            # ===== FIN Lógica ZUE - Perfect Match =====

            result = _create_result_dict(kepts_amls_values_list, status)
            if result:
                return result