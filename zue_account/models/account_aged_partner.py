# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime

from odoo import models, fields, _
from odoo.tools import SQL
from odoo.tools.misc import format_date

from dateutil.relativedelta import relativedelta
from itertools import chain

class AgedPartnerBalanceCustomHandler(models.AbstractModel):
    _inherit = 'account.aged.partner.balance.report.handler'

    def _custom_options_initializer(self, report, options, previous_options):
        super()._custom_options_initializer(report, options, previous_options=previous_options)

        initial_column_labels = [column.get('expression_label') for column in options.get('columns', [])]
        hidden_columns = {'invoice_date'}
        previous_options = previous_options or {}

        # Respetar la selección previa del usuario; si no existe, mostrar por defecto.
        options['show_supplier_invoice_number'] = previous_options.get('show_supplier_invoice_number', True)
        options['show_invoice_user_name'] = previous_options.get('show_invoice_user_name', True)
        options['show_partner_name'] = previous_options.get('show_partner_name', True)
        options['show_partner_user_name'] = previous_options.get('show_partner_user_name', True)

        filtered_columns = [
            column for column in options['columns']
            if column['expression_label'] not in hidden_columns
        ]
        preferred_order = [
            'z_due_date',
            'z_amount_currency',
            'z_currency',
            'z_move_ref',
            'partner_name',
            'supplier_invoice_number',
            'invoice_user_name',
            'partner_user_name',
            'z_account_name',
            'z_expected_date',
            'period0',
            'period1',
            'period2',
            'period3',
            'period4',
            'period5',
            'total',
        ]
        labels_to_columns = {column['expression_label']: column for column in filtered_columns}
        ordered_columns = [labels_to_columns[label] for label in preferred_order if label in labels_to_columns]
        remaining_columns = [column for column in filtered_columns if column['expression_label'] not in preferred_order]
        options['columns'] = ordered_columns + remaining_columns

        # Columnas controladas por los filtros personalizados: si la opción está en False, se retiran del informe.
        toggle_columns = {
            'supplier_invoice_number': options['show_supplier_invoice_number'],
            'invoice_user_name': options['show_invoice_user_name'],
            'partner_name': options['show_partner_name'],
            'partner_user_name': options['show_partner_user_name'],
        }
        options['columns'] = [
            col for col in options['columns']
            if toggle_columns.get(col['expression_label'], True)
        ]

    def _aged_partner_report_custom_engine_common(self, options, internal_type, current_groupby, next_groupby, offset=0, limit=None):
        report = self.env['account.report'].browse(options['report_id'])
        report._check_groupby_fields((next_groupby.split(',') if next_groupby else []) + ([current_groupby] if current_groupby else []))

        def minus_days(date_obj, days):
            return fields.Date.to_string(date_obj - relativedelta(days=days))

        aging_date_field = SQL.identifier('invoice_date') if options['aging_based_on'] == 'base_on_invoice_date' else SQL.identifier('date_maturity')
        date_to = fields.Date.from_string(options['date']['date_to'])
        interval = options['aging_interval']
        periods = [(False, fields.Date.to_string(date_to))]
        # Since we added the first period in the list we have to do one less iteration
        nb_periods = len([column for column in options['columns'] if column['expression_label'].startswith('period')]) - 1
        for i in range(nb_periods):
            start_date = minus_days(date_to, (interval * i) + 1)
            # The last element of the list will have False for the end date
            end_date = minus_days(date_to, interval * (i + 1)) if i < nb_periods - 1 else False
            periods.append((start_date, end_date))

        def build_result_dict(report, query_res_lines):
            rslt = {f'period{i}': 0 for i in range(len(periods))}

            def _normalize_text_value(value):
                if isinstance(value, dict):
                    lang = self.env.lang or 'en_US'
                    return value.get(lang) or value.get('en_US') or next((v for v in value.values() if v), None)
                return value

            def _get_unique_value_from_arrays(lines, key):
                unique_values = []
                for line in lines:
                    for item in (line.get(key) or []):
                        item = _normalize_text_value(item)
                        if item not in (False, None, ''):
                            if all(item != existing for existing in unique_values):
                                unique_values.append(item)
                                if len(unique_values) > 1:
                                    return None
                return unique_values[0] if unique_values else None

            for query_res in query_res_lines:
                for i in range(len(periods)):
                    period_key = f'period{i}'
                    rslt[period_key] += query_res[period_key]

            if current_groupby == 'id':
                query_res = query_res_lines[0] # We're grouping by id, so there is only 1 element in query_res_lines anyway
                currency = self.env['res.currency'].browse(query_res['currency_id'][0]) if len(query_res['currency_id']) == 1 else None
                expected_date = len(query_res['due_date']) == 1 and query_res['due_date'][0]
                rslt.update({
                    'invoice_date': query_res['invoice_date'][0] if len(query_res['invoice_date']) == 1 else None,
                    'move_ref': query_res['move_ref'][0] if len(query_res['move_ref']) == 1 else None,
                    'z_move_ref': query_res['move_ref'][0] if len(query_res['move_ref']) == 1 else None,
                    'supplier_invoice_number': query_res['supplier_invoice_number'][0] if len(query_res['supplier_invoice_number']) == 1 else None,
                    'invoice_user_name': _normalize_text_value(query_res['invoice_user_name'][0]) if len(query_res['invoice_user_name']) == 1 else None,
                    'partner_user_name': _normalize_text_value(query_res['partner_user_name'][0]) if len(query_res['partner_user_name']) == 1 else None,
                    'due_date': query_res['due_date'][0] if len(query_res['due_date']) == 1 else None,
                    'z_due_date': query_res['due_date'][0] if len(query_res['due_date']) == 1 else None,
                    'amount_currency': query_res['amount_currency'],
                    'z_amount_currency': query_res['amount_currency'],
                    'currency_id': query_res['currency_id'][0] if len(query_res['currency_id']) == 1 else None,
                    'currency': currency.display_name if currency else None,
                    'z_currency': currency.display_name if currency else None,
                    'partner_name': _normalize_text_value(query_res['partner_name'][0]) if len(query_res['partner_name']) == 1 else None,
                    'journal_name': _normalize_text_value(query_res['journal_name'][0]) if len(query_res['journal_name']) == 1 else None,
                    'account_name': _normalize_text_value(query_res['account_name'][0]) if len(query_res['account_name']) == 1 else None,
                    'z_account_name': _normalize_text_value(query_res['account_name'][0]) if len(query_res['account_name']) == 1 else None,
                    'expected_date': expected_date or None,
                    'z_expected_date': expected_date or None,
                    'total': None,
                    'has_sublines': query_res['aml_count'] > 0,

                    # Needed by the custom_unfold_all_batch_data_generator, to speed-up unfold_all
                    'partner_id': query_res['partner_id'][0] if query_res['partner_id'] else None,
                })
            else:
                rslt.update({
                    'invoice_date': _get_unique_value_from_arrays(query_res_lines, 'invoice_date'),
                    'move_ref': _get_unique_value_from_arrays(query_res_lines, 'move_ref'),
                    'z_move_ref': _get_unique_value_from_arrays(query_res_lines, 'move_ref'),
                    'supplier_invoice_number': _get_unique_value_from_arrays(query_res_lines, 'supplier_invoice_number'),
                    'invoice_user_name': _get_unique_value_from_arrays(query_res_lines, 'invoice_user_name'),
                    'partner_user_name': _get_unique_value_from_arrays(query_res_lines, 'partner_user_name'),
                    'due_date': _get_unique_value_from_arrays(query_res_lines, 'due_date'),
                    'z_due_date': _get_unique_value_from_arrays(query_res_lines, 'due_date'),
                    'amount_currency': None,
                    'z_amount_currency': None,
                    'currency_id': None,
                    'currency': None,
                    'z_currency': None,
                    'partner_name': _get_unique_value_from_arrays(query_res_lines, 'partner_name'),
                    'journal_name': _get_unique_value_from_arrays(query_res_lines, 'journal_name'),
                    'account_name': _get_unique_value_from_arrays(query_res_lines, 'account_name'),
                    'z_account_name': _get_unique_value_from_arrays(query_res_lines, 'account_name'),
                    'expected_date': None,
                    'z_expected_date': None,
                    'total': sum(rslt[f'period{i}'] for i in range(len(periods))),
                    'has_sublines': True,
                })

            return rslt

        # Build period table
        period_table_format = ('(VALUES %s)' % ','.join("(%s, %s, %s)" for period in periods))
        params = list(chain.from_iterable(
            (period[0] or None, period[1] or None, i)
            for i, period in enumerate(periods)
        ))
        period_table = SQL(period_table_format, *params)

        # Build query
        query = report._get_report_query(options, 'strict_range', domain=[('account_id.account_type', '=', internal_type)])
        account_alias = query.left_join(lhs_alias='account_move_line', lhs_column='account_id', rhs_table='account_account', rhs_column='id', link='account_id')
        # Extraer código del JSON code_store usando alias SQL como identificador real
        account_code = SQL(
            "COALESCE(%s.code_store->>'1', '')",
            SQL.identifier(account_alias),
        )

        always_present_groupby = SQL("period_table.period_index")
        if current_groupby:
            groupby_field_sql = self.env['account.move.line']._field_to_sql("account_move_line", current_groupby, query)
            select_from_groupby = SQL("%s AS grouping_key,", groupby_field_sql)
            groupby_clause = SQL("%s, %s", groupby_field_sql, always_present_groupby)
        else:
            select_from_groupby = SQL()
            groupby_clause = always_present_groupby
        multiplicator = -1 if internal_type == 'liability_payable' else 1
        select_period_query = SQL(',').join(
            SQL("""
                CASE WHEN period_table.period_index = %(period_index)s
                THEN %(multiplicator)s * SUM(%(balance_select)s)
                ELSE 0 END AS %(column_name)s
                """,
                period_index=i,
                multiplicator=multiplicator,
                column_name=SQL.identifier(f"period{i}"),
                balance_select=report._currency_table_apply_rate(SQL(
                    "account_move_line.balance - COALESCE(part_debit.amount, 0) + COALESCE(part_credit.amount, 0)"
                )),
            )
            for i in range(len(periods))
        )

        tail_query = report._get_engine_query_tail(offset, limit)
        query = SQL(
            """
            WITH period_table(date_start, date_stop, period_index) AS (%(period_table)s)

            SELECT
                %(select_from_groupby)s
                %(multiplicator)s * (
                    SUM(account_move_line.amount_currency)
                    - COALESCE(SUM(part_debit.debit_amount_currency), 0)
                    + COALESCE(SUM(part_credit.credit_amount_currency), 0)
                ) AS amount_currency,
                ARRAY_AGG(DISTINCT account_move_line.partner_id) AS partner_id,
                ARRAY_AGG(account_move_line.payment_id) AS payment_id,
                ARRAY_AGG(DISTINCT move.invoice_date) AS invoice_date,
                ARRAY_AGG(DISTINCT move.ref) AS move_ref,
                ARRAY_AGG(DISTINCT COALESCE(account_move_line.%(aging_date_field)s, account_move_line.date)) AS report_date,
                --ARRAY_AGG(DISTINCT account_move_line.expected_pay_date) AS expected_date, --Se elimino en V18 el campo expected_pay_date
                ARRAY_AGG(DISTINCT partner.name) AS partner_name,
                ARRAY_AGG(DISTINCT COALESCE(invoice_user_partner.name,'')) AS invoice_user_name,
                ARRAY_AGG(DISTINCT COALESCE(client_user_partner.name,'')) AS partner_user_name,
                ARRAY_AGG(DISTINCT journal.name) AS journal_name,
                ARRAY_AGG(DISTINCT %(account_code)s) AS account_name,
                ARRAY_AGG(DISTINCT COALESCE(move.supplier_invoice_number,'')) AS supplier_invoice_number,
                ARRAY_AGG(DISTINCT COALESCE(account_move_line.%(aging_date_field)s, account_move_line.date)) AS due_date,
                ARRAY_AGG(DISTINCT account_move_line.currency_id) AS currency_id,
                COUNT(account_move_line.id) AS aml_count,
                ARRAY_AGG(%(account_code)s) AS account_code,
                %(select_period_query)s

            FROM %(table_references)s

            JOIN account_journal journal ON journal.id = account_move_line.journal_id
            JOIN account_account account ON account.id = account_move_line.account_id
            JOIN account_move move ON move.id = account_move_line.move_id
            LEFT JOIN res_users invoice_user ON invoice_user.id = move.invoice_user_id
            LEFT JOIN res_partner invoice_user_partner ON invoice_user_partner.id = invoice_user.partner_id
            LEFT JOIN res_partner partner ON partner.id = account_move_line.partner_id
            LEFT JOIN res_users client_user ON client_user.id = partner.user_id
            LEFT JOIN res_partner client_user_partner ON client_user_partner.id = client_user.partner_id
            %(currency_table_join)s

            LEFT JOIN LATERAL (
                SELECT
                    SUM(part.amount) AS amount,
                    SUM(part.debit_amount_currency) AS debit_amount_currency,
                    part.debit_move_id
                FROM account_partial_reconcile part
                WHERE part.max_date <= %(date_to)s AND part.debit_move_id = account_move_line.id
                GROUP BY part.debit_move_id
            ) part_debit ON TRUE

            LEFT JOIN LATERAL (
                SELECT
                    SUM(part.amount) AS amount,
                    SUM(part.credit_amount_currency) AS credit_amount_currency,
                    part.credit_move_id
                FROM account_partial_reconcile part
                WHERE part.max_date <= %(date_to)s AND part.credit_move_id = account_move_line.id
                GROUP BY part.credit_move_id
            ) part_credit ON TRUE

            JOIN period_table ON
                (
                    period_table.date_start IS NULL
                    OR COALESCE(account_move_line.%(aging_date_field)s, account_move_line.date) <= DATE(period_table.date_start)
                )
                AND
                (
                    period_table.date_stop IS NULL
                    OR COALESCE(account_move_line.%(aging_date_field)s, account_move_line.date) >= DATE(period_table.date_stop)
                )

            WHERE %(search_condition)s

            GROUP BY %(groupby_clause)s

            HAVING
                ROUND(SUM(%(having_debit)s), %(currency_precision)s) != 0
                OR ROUND(SUM(%(having_credit)s), %(currency_precision)s) != 0

            ORDER BY %(groupby_clause)s

            %(tail_query)s
            """,
            account_code=account_code,
            period_table=period_table,
            select_from_groupby=select_from_groupby,
            select_period_query=select_period_query,
            multiplicator=multiplicator,
            aging_date_field=aging_date_field,
            table_references=query.from_clause,
            currency_table_join=report._currency_table_aml_join(options),
            date_to=date_to,
            search_condition=query.where_clause,
            groupby_clause=groupby_clause,
            having_debit=report._currency_table_apply_rate(SQL("CASE WHEN account_move_line.balance > 0  THEN account_move_line.balance else 0 END - COALESCE(part_debit.amount, 0)")),
            having_credit=report._currency_table_apply_rate(SQL("CASE WHEN account_move_line.balance < 0  THEN -account_move_line.balance else 0 END - COALESCE(part_credit.amount, 0)")),
            currency_precision=self.env.company.currency_id.decimal_places,
            tail_query=tail_query,
        )

        self.env.cr.execute(query)
        query_res_lines = self.env.cr.dictfetchall()

        if not current_groupby:
            return build_result_dict(report, query_res_lines)
        else:
            rslt = []

            all_res_per_grouping_key = {}
            for query_res in query_res_lines:
                grouping_key = query_res['grouping_key']
                all_res_per_grouping_key.setdefault(grouping_key, []).append(query_res)

            for grouping_key, query_res_lines in all_res_per_grouping_key.items():
                rslt.append((grouping_key, build_result_dict(report, query_res_lines)))

            return rslt

    def _prepare_partner_values(self):
        return {
            'invoice_date': None,
            'move_ref': None,
            'z_move_ref': None,
            'supplier_invoice_number': None,
            'invoice_user_name': None,
            'partner_user_name': None,
            'due_date': None,
            'z_due_date': None,
            'amount_currency': None,
            'z_amount_currency': None,
            'currency_id': None,
            'currency': None,
            'z_currency': None,
            'partner_name': None,
            'journal_name': None,
            'account_name': None,
            'z_account_name': None,
            'expected_date': None,
            'z_expected_date': None,
            'total': 0,
        }

# class AccountReport(models.Model):
#     _inherit = "account.report"
#
#     filter_accounts = fields.Boolean(
#         string="Cuentas",
#         compute=lambda x: x._compute_report_option_filter('filter_accounts'), store=True,
#         depends=['root_report_id'],
#     )
#
#     ####################################################
#     # OPTIONS: accounts
#     ####################################################
#
#     def _get_filter_accounts(self):
#         account_type = self.env.context.get('model',None)
#         if account_type != 'account.aged.payable' and account_type != 'account.aged.receivable':
#             return self.env['account.account'].with_context(active_test=False).search([
#                 ('company_id', 'in', self.env.user.company_ids.ids or [self.env.company.id])
#             ], order="company_id, code, name")
#         else:
#             return self.env['account.account'].with_context(active_test=False).search([
#                 ('company_id', 'in', self.env.user.company_ids.ids or [self.env.company.id]),
#                 ('internal_type','=',account_type.split('.')[2])
#             ], order="company_id, code, name")
#
#     def _init_filter_accounts(self, options, previous_options=None):
#         if self.filter_accounts is None:
#             return
#
#         previous_company = False
#         if previous_options and previous_options.get('accounts'):
#             account_map = dict((opt['id'], opt['selected']) for opt in previous_options['accounts'] if opt['id'] != 'divider' and 'selected' in opt)
#         else:
#             account_map = {}
#         options['accounts'] = []
#
#         group_header_displayed = False
#         default_group_ids = []
#
#         for j in self._get_filter_accounts():
#             if j.company_id != previous_company:
#                 options['accounts'].append({'id': 'divider', 'name': j.company_id.name})
#                 previous_company = j.company_id
#             options['accounts'].append({
#                 'id': j.id,
#                 'name': j.name,
#                 'code': j.code,
#                 'selected': account_map.get(j.id, j.id in default_group_ids),
#             })
#
#     def _get_options_accounts(self, options):
#         return [
#             account for account in options.get('accounts', []) if
#             not account['id'] in ('divider', 'group') and account['selected']
#         ]
#
#     def _get_options_accounts_domain(self, options):
#         # retorna para filtrar la entidad account_account
#         selected_accounts = self._get_options_accounts(options)
#         return selected_accounts and [('account_id', 'in', [j['id'] for j in selected_accounts])] or []
#
#     def _get_options_domain(self, options, date_scope):
#         domain = super(AccountReport, self)._get_options_domain(options, date_scope)
#         domain += self._get_options_accounts_domain(options)
#         return domain

