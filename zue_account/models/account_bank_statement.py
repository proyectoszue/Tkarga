# -*- coding: utf-8 -*-
import logging
import re

from odoo import SUPERUSER_ID, fields, models
from odoo.fields import Domain
from odoo.tools import SQL


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    z_bank_auto_reconcile_receivable_payable_only = fields.Boolean(related='company_id.z_bank_auto_reconcile_receivable_payable_only', readonly=True)

    def _zue_is_exact_amount_match(self, currency, left_amount, right_amount):
        return bool(currency) and currency.compare_amounts(left_amount, right_amount) == 0

    def _zue_is_exact_invoice_match_candidate(self, st_line, aml):
        discount_date_matches = aml.discount_date and st_line.date <= aml.discount_date

        if (aml.company_currency_id == st_line.currency_id and (self._zue_is_exact_amount_match(st_line.currency_id, aml.amount_residual, st_line.amount)
                or (discount_date_matches and self._zue_is_exact_amount_match(st_line.currency_id, aml.discount_balance, st_line.amount)))):
            return True

        if (aml.currency_id == st_line.currency_id and (self._zue_is_exact_amount_match(st_line.currency_id, aml.amount_residual_currency, st_line.amount)
                or (discount_date_matches and self._zue_is_exact_amount_match(st_line.currency_id, aml.discount_amount_currency, st_line.amount)))):
            return True

        if (st_line.foreign_currency_id and aml.currency_id == st_line.foreign_currency_id and (self._zue_is_exact_amount_match(st_line.foreign_currency_id, aml.amount_residual_currency, st_line.amount_currency)
                or (discount_date_matches and self._zue_is_exact_amount_match(st_line.foreign_currency_id, aml.discount_amount_currency, st_line.amount_currency)))):
            return True

        return False

    def _invoice_matching_post_process(self, st_line, amls):
        exact_match_only = (st_line.company_id.z_bank_auto_reconcile_exact_match_only or self.env.context.get('zue_force_exact_match_only'))
        if not exact_match_only:
            return super()._invoice_matching_post_process(st_line, amls)

        candidate_amls = self.env['account.move.line']
        for aml in amls:
            if self._zue_is_exact_invoice_match_candidate(st_line, aml):
                candidate_amls += aml

        if len(candidate_amls) == 1:
            return candidate_amls

        if prior_amls := candidate_amls.filtered(lambda aml: aml.invoice_date and aml.invoice_date <= st_line.date):
            return max(prior_amls, key=lambda aml: aml.invoice_date)
        return None

    def _zue_get_receivable_payable_auto_reconcile_account_ids(self):
        """ ZUE Helper para filtrar las cuentas que quiero en la autoconciliación """
        accounts = self.env['account.account'].search([('reconcile', '=', True), ('account_type', 'in', ('asset_receivable', 'liability_payable'))])
        accounts -= self.env['account.journal'].search([('type', 'in', ['bank', 'cash', 'credit'])]).suspense_account_id

        return accounts.ids

    def _try_auto_reconcile_statement_lines(self, company_id=None):
        restricted_lines = self.filtered(lambda line: line.company_id.z_bank_auto_reconcile_receivable_payable_only)
        standard_lines = self - restricted_lines

        if standard_lines:
            super(AccountBankStatementLine, standard_lines)._try_auto_reconcile_statement_lines(company_id=company_id)

        if restricted_lines:
            restricted_lines._zue_try_auto_reconcile_statement_lines_receivable_payable(company_id=company_id)

    def _zue_try_auto_reconcile_statement_lines_receivable_payable(self, company_id=None):
        """ ZUE Override Odoo 19 para autoconciliar únicamente cuentas por cobrar y pagar """
        st_move_ids = self.mapped('move_id').ids
        self.lock_for_update()

        domain = []
        if company_id is not None:
            domain = Domain(self.env['account.reconcile.model']._check_company_domain(company_id))
        reco_models = self.env['account.reconcile.model'].search(domain)

        self.env['account.reconcile.model'].flush_model()
        self.flush_recordset(['journal_id', 'transaction_details', 'payment_ref', 'company_id'])
        self.env.cr.execute(SQL("""
            WITH matching_journal_ids AS (
                    SELECT account_reconcile_model_id,
                           ARRAY_AGG(account_journal_id) AS ids
                      FROM account_journal_account_reconcile_model_rel
                  GROUP BY account_reconcile_model_id
                 )

          SELECT st_line.id AS st_line_id, reco_model.mapped_partner_id
            FROM account_bank_statement_line st_line
       LEFT JOIN LATERAL (
                   SELECT reco_model.id,
                          reco_model.mapped_partner_id
                     FROM account_reconcile_model reco_model
                LEFT JOIN matching_journal_ids ON reco_model.id = matching_journal_ids.account_reconcile_model_id
                    WHERE (matching_journal_ids.ids IS NULL OR st_line.journal_id = ANY(matching_journal_ids.ids))
                      AND reco_model.mapped_partner_id IS NOT NULL
                      AND (
                              (
                                  reco_model.match_label = 'contains'
                                  AND (
                                      st_line.payment_ref IS NOT NULL AND st_line.payment_ref ILIKE '%%' || reco_model.match_label_param || '%%'
                                      OR st_line.transaction_details IS NOT NULL AND st_line.transaction_details::TEXT ILIKE '%%' || reco_model.match_label_param || '%%'
                                   )
                              ) OR (
                                  reco_model.match_label = 'not_contains'
                                  AND NOT (
                                      st_line.payment_ref IS NOT NULL AND st_line.payment_ref ILIKE '%%' || reco_model.match_label_param || '%%'
                                      OR st_line.transaction_details IS NOT NULL AND st_line.transaction_details::TEXT ILIKE '%%' || reco_model.match_label_param || '%%'
                                  )
                              ) OR (
                                  reco_model.match_label = 'match_regex'
                                  AND (
                                      st_line.payment_ref IS NOT NULL AND st_line.payment_ref ~* reco_model.match_label_param
                                      OR st_line.transaction_details IS NOT NULL AND st_line.transaction_details::TEXT ~* reco_model.match_label_param
                                  )
                              )
                          )
                      AND reco_model.id = ANY(%s)
                      AND reco_model.company_id = st_line.company_id
                 ORDER BY reco_model.sequence ASC, reco_model.id ASC
                    LIMIT 1
                 ) AS reco_model ON TRUE
           WHERE st_line.id IN %s
             AND st_line.partner_id IS NULL
             AND reco_model.mapped_partner_id IS NOT NULL
            """, reco_models.ids, tuple(self.ids)))

        for st_line_id, mapped_partner_id in self.env.cr.fetchall():
            st_line = self.browse(st_line_id).with_prefetch(self._prefetch_ids)  # guarantees batch prefetching if needed
            st_line.partner_id = mapped_partner_id

        # global flushing of tables that should not be updated between the different SQL queries
        self.env['account.account'].flush_model(['account_type', 'active'])
        self.env['account.move'].flush_model(['date', 'amount_total'])
        self.env['account.move.line'].flush_model([
            'ref', 'move_id', 'move_name', 'account_id', 'partner_id', 'company_id',
            'reconciled', 'company_currency_id', 'amount_residual',
            'currency_id', 'amount_residual_currency',
            'discount_date', 'discount_balance', 'discount_amount_currency',
        ])
        self.flush_recordset([
            'move_id', 'partner_id', 'company_id', 'currency_id',
            'amount', 'foreign_currency_id', 'amount_currency', 'payment_ref'
        ])
        self.env['account.payment'].flush_model(['move_id', 'journal_id', 'memo'])

        # Limit the automatic match to receivable/payable accounts only.
        account_ids = self._zue_get_receivable_payable_auto_reconcile_account_ids()

        # First, try to match invoices and payments using the end to end ID.
        processed_st_line_ids = set()
        st_lines_with_end_to_end_uuid_ids = 'end_to_end_uuid' in self._fields and self.filtered('end_to_end_uuid').ids
        if st_lines_with_end_to_end_uuid_ids and account_ids:
            self.env.cr.execute(SQL("""
                 -- Query to get either payment amls either invoice/bill amls related to payments which have
                 -- the same end to end uuid of bank statement lines.
                    SELECT st_line.id AS st_line_id,
                           ARRAY_AGG(aml.id ORDER BY aml.id ASC) AS aml_ids
                      FROM account_bank_statement_line st_line
                      JOIN account_payment payment ON st_line.end_to_end_uuid = payment.end_to_end_uuid
                      JOIN account_move_line aml ON (
                              payment.move_id = aml.move_id
                           OR aml.move_id IN (
                              SELECT move_payment_rel.invoice_id
                                FROM account_move__account_payment move_payment_rel
                               WHERE move_payment_rel.payment_id = payment.id
                           )
                      )
                 LEFT JOIN res_company aml_company ON aml_company.id = aml.company_id
                 LEFT JOIN res_company payment_company ON payment_company.id = payment.company_id
                     WHERE aml.move_id NOT IN %(st_move_ids)s
                       AND (
                              aml_company.parent_path LIKE CONCAT(payment_company.id, '/%%')
                           OR payment_company.parent_path LIKE CONCAT(aml_company.id, '/%%')
                       )
                       AND aml.reconciled = false
                       AND aml.account_id IN %(account_ids)s
                       AND ((st_line.amount > 0 AND aml.balance > 0) OR (st_line.amount < 0 AND aml.balance < 0))
                       AND aml.parent_state in ('draft', 'posted')
                       AND st_line.id IN %(st_line_ids)s
                  GROUP BY st_line.id
            """, st_move_ids=tuple(st_move_ids), account_ids=tuple(account_ids), st_line_ids=tuple(st_lines_with_end_to_end_uuid_ids)))

            for st_line_id, aml_ids in self.env.cr.fetchall():
                st_line = self.browse(st_line_id).with_prefetch(self._prefetch_ids)
                st_line.with_company(st_line.company_id).with_user(SUPERUSER_ID).set_line_bank_statement_line(aml_ids)
                processed_st_line_ids.add(st_line_id)

        remaining_st_line_ids = list(set(self.ids) - processed_st_line_ids)

        if not remaining_st_line_ids:
            self.write({'cron_last_check': self.env.cr.now()})
            return

        # Intentionally skip the standalone/outstanding payment matching branch:
        # those technical payment accounts are outside the receivable/payable scope.
        if not account_ids:
            self.write({'cron_last_check': fields.Datetime.now()})
            return

        query = SQL("""
                SELECT st_line.id,
                       ARRAY_AGG(word_aml.id) aml_ids,
                       SUM(word_aml.amount_residual),
                       word_aml.word matching_word
                  FROM account_bank_statement_line st_line
          JOIN LATERAL (
                        SELECT aml.id, word, aml.ref, aml.amount_residual
                          FROM account_move_line aml
                     LEFT JOIN account_move move ON (move.id = aml.move_id AND move.payment_reference != move.name),
                       LATERAL regexp_split_to_table(
                                  COALESCE(aml.ref, '') || ' - ' ||
                                  COALESCE(aml.move_name, '') || ' - ' ||
                                  COALESCE(move.payment_reference, ''), ' - '
                               ) AS word
                         WHERE (st_line.partner_id IS NULL OR st_line.partner_id = aml.partner_id)
                           AND aml.move_id NOT IN %s
                           AND aml.reconciled = false
                           AND aml.account_id IN %s
                           AND aml.company_id = st_line.company_id
                           AND aml.currency_id = COALESCE(st_line.foreign_currency_id, st_line.currency_id)
                           AND ((st_line.amount > 0 AND aml.balance > 0) OR (st_line.amount < 0 AND aml.balance < 0))
                           AND (aml.parent_state IN ('draft', 'posted'))
                           AND st_line.id IN %s
                           AND (
                                length(word) > 5 AND st_line.payment_ref ILIKE '%%' || word || '%%'
                               )
                       ) word_aml ON TRUE
              GROUP BY st_line.id, matching_word
                HAVING COUNT(*) = 1
        """, tuple(st_move_ids), tuple(account_ids), tuple(remaining_st_line_ids))
        self.env.cr.execute(query)

        st_lines_refs = {}
        to_process = {}

        def is_properly_surrounded(text, substring):
            """
            Definition of what a valid matching word can be: any string, containing whitespaces or not, surrounded by
            start/end of line, whitespace, or punctuation in ['.', ';', ',', '?', '!'].
            """
            sub_escaped = re.escape(substring)
            pattern = rf"(^|[\s\.;,?!]){sub_escaped}($|[\s\.;,?!])"
            return re.search(pattern, text) is not None

        for st_line_id, aml_id, aml_amount_residual, matching_word in self.env.cr.fetchall():
            st_line = self.browse(st_line_id).with_prefetch(self._prefetch_ids)
            if not is_properly_surrounded(st_line.payment_ref, matching_word):
                continue
            to_process[st_line_id, matching_word] = [(aml_id, aml_amount_residual)]
            for word in st_lines_refs.get(st_line_id, []):
                if word in matching_word or matching_word in word:
                    del to_process[st_line_id, matching_word]
                    del to_process[st_line_id, word]
            if st_line_id not in st_lines_refs:
                st_lines_refs[st_line_id] = []
            st_lines_refs[st_line_id].append(matching_word)

        ref_amls_sum = {}
        for key, to_process_list in to_process.items():
            st_line_id, matching_word = key
            st_line = self.browse(st_line_id).with_prefetch(self._prefetch_ids)
            for aml_id, aml_amount_residual in to_process_list:
                if st_line_id in ref_amls_sum:
                    if ref_amls_sum[st_line_id] <= 0:
                        continue
                    ref_amls_sum[st_line_id] -= aml_amount_residual
                else:
                    ref_amls_sum[st_line_id] = st_line.amount - aml_amount_residual
                st_line.with_user(SUPERUSER_ID).set_line_bank_statement_line(aml_id)
                if st_line.currency_id.is_zero(st_line.amount_residual):
                    processed_st_line_ids.add(st_line.id)
        remaining_st_line_ids = set(remaining_st_line_ids) - processed_st_line_ids

        if not remaining_st_line_ids:
            self.write({'cron_last_check': self.env.cr.now()})
            return

        query = SQL("""
                SELECT st_line.id AS st_line_id,
                       ARRAY_AGG(aml.id ORDER BY aml.id ASC) AS all_aml_ids,
                       SUM(aml.amount_residual) AS total_residual
                  FROM account_bank_statement_line st_line
                  JOIN account_move_line aml ON (st_line.partner_id = aml.partner_id AND aml.company_id = st_line.company_id)
                  JOIN account_move move ON aml.move_id = move.id
                 WHERE st_line.partner_id IS NOT NULL
                   AND aml.move_id NOT IN %s
                   AND aml.reconciled = false
                   AND aml.account_id IN %s
                   AND ((st_line.amount > 0 AND aml.balance > 0) OR (st_line.amount < 0 AND aml.balance < 0))
                   AND (aml.parent_state IN ('draft', 'posted'))
                   AND st_line.id IN %s

              GROUP BY st_line.id
        """, tuple(st_move_ids), tuple(account_ids), tuple(remaining_st_line_ids))
        self.env.cr.execute(query)

        for st_line_id, all_aml_ids, total_residual in self.env.cr.fetchall():
            st_line = self.browse(st_line_id).with_prefetch(self._prefetch_ids)
            if st_line.currency_id.compare_amounts(total_residual, st_line.amount) == 0:
                st_line.with_user(SUPERUSER_ID).set_line_bank_statement_line(all_aml_ids)
            elif all_aml_ids:
                amls = self.env['account.move.line'].browse(all_aml_ids)
                candidate_amls = self._invoice_matching_post_process(st_line, amls)
                if candidate_amls:
                    st_line.with_user(SUPERUSER_ID).set_line_bank_statement_line(candidate_amls.ids)

            if st_line.currency_id.is_zero(st_line.amount_residual):
                processed_st_line_ids.add(st_line.id)

        remaining_st_line_ids -= processed_st_line_ids

        if not remaining_st_line_ids:
            self.write({'cron_last_check': self.env.cr.now()})
            return

        remaining_st_lines = self.browse(list(remaining_st_line_ids)).with_prefetch(self._prefetch_ids)
        reco_models._apply_reconcile_models(remaining_st_lines)

        self.write({'cron_last_check': self.env.cr.now()})
