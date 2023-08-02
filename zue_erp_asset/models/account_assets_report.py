from odoo import api, fields, models, _
from odoo.tools import format_date
import copy
import binascii
import struct
import time
import itertools
from itertools import groupby
from collections import defaultdict

MAX_NAME_LENGTH = 50

class assets_report(models.AbstractModel):
    _inherit = 'account.assets.report'

    def get_header(self, options):
        start_date = format_date(self.env, options['date']['date_from'])
        end_date = format_date(self.env, options['date']['date_to'])
        return [
            [
                {'name': ''},
                {'name': _('Datos históricos'), 'colspan': 5},
                {'name': _('Characteristics'), 'colspan': 4},
                {'name': _('Assets'), 'colspan': 4},
                {'name': _('Depreciation'), 'colspan': 4},
                {'name': _('Book Value')},
            ],
            [
                {'name': ''},  # Description
                {'name': _('Costo'), 'class': 'number'}, # Datos Historicos
                {'name': _('Fecha de Compra'), 'class': 'text-center'},
                #{'name': _('Fecha depreciación total'), 'class': 'text-center'},
                {'name': _('Vida útil'), 'class': 'text-center'},
                {'name': _('Periodos depreciados'), 'class': 'text-center'},
                {'name': _('Depreciación acumulada'), 'class': 'number'},
                {'name': _('Acquisition Date'), 'class': 'text-center'},  # Characteristics
                {'name': _('First Depreciation'), 'class': 'text-center'},
                {'name': _('Method'), 'class': 'text-center'},
                {'name': _('Duration / Rate'), 'class': 'number', 'title': _('In percent.<br>For a linear method, the depreciation rate is computed per year.<br>For a declining method, it is the declining factor'), 'data-toggle': 'tooltip'},
                {'name': start_date, 'class': 'number'},  # Assets
                {'name': _('+'), 'class': 'number'},
                {'name': _('-'), 'class': 'number'},
                {'name': end_date, 'class': 'number'},
                {'name': start_date, 'class': 'number'},  # Depreciation
                {'name': _('+'), 'class': 'number'},
                {'name': _('-'), 'class': 'number'},
                {'name': end_date, 'class': 'number'},
                {'name': '', 'class': 'number'},  # Gross
            ],
        ]

    def _get_assets_lines(self, options):
        "Get the data from the database"

        self.env['account.move.line'].check_access_rights('read')
        self.env['account.asset'].check_access_rights('read')

        get_expenses = self.env.context.get('expenses', False)
        asset_type = ''

        if get_expenses:
            asset_type = 'expense'
        else:
            asset_type = 'purchase'

        where_account_move = " AND state != 'cancel'"
        if not options.get('all_entries'):
            where_account_move = " AND state = 'posted'"

        sql = """
                -- remove all the moves that have been reversed from the search
                CREATE TEMPORARY TABLE IF NOT EXISTS temp_account_move () INHERITS (account_move) ON COMMIT DROP;
                INSERT INTO temp_account_move SELECT move.*
                FROM ONLY account_move move
                LEFT JOIN ONLY account_move reversal ON reversal.reversed_entry_id = move.id
                WHERE reversal.id IS NULL AND move.asset_id IS NOT NULL AND move.company_id in %(company_ids)s;

                SELECT asset.id as asset_id,
                       asset.parent_id as parent_id,
                       asset.name as asset_name,
                       asset.x_history_cost,
                       asset.x_date_purchase_his,
                       asset.x_ussefull_life,
                       asset.x_deprecieted_periods,
                       asset.x_accumulated_depreciation,                       
                       asset.original_value as asset_original_value,
                       asset.currency_id as asset_currency_id,
                       COALESCE(asset.first_depreciation_date_import, asset.first_depreciation_date) as asset_date,
                       asset.already_depreciated_amount_import as import_depreciated,
                       asset.disposal_date as asset_disposal_date,
                       asset.acquisition_date as asset_acquisition_date,
                       asset.method as asset_method,
                       (
                           COALESCE(account_move_count.count, 0)
                           + COALESCE(asset.depreciation_number_import, 0)
                           - CASE WHEN asset.prorata THEN 1 ELSE 0 END
                       ) as asset_method_number,
                       asset.method_period as asset_method_period,
                       asset.method_progress_factor as asset_method_progress_factor,
                       asset.state as asset_state,
                       account.code as account_code,
                       account.name as account_name,
                       account.id as account_id,
                       account.company_id as company_id,
                       COALESCE(first_move.asset_depreciated_value, move_before.asset_depreciated_value, 0.0) as depreciated_start,
                       COALESCE(first_move.asset_remaining_value, move_before.asset_remaining_value, 0.0) as remaining_start,
                       COALESCE(last_move.asset_depreciated_value, move_before.asset_depreciated_value, 0.0) as depreciated_end,
                       COALESCE(last_move.asset_remaining_value, move_before.asset_remaining_value, 0.0) as remaining_end,
                       COALESCE(first_move.amount_total, 0.0) as depreciation,
                       COALESCE(first_move.id, move_before.id) as first_move_id,
                       COALESCE(last_move.id, move_before.id) as last_move_id
                FROM account_asset as asset
                LEFT JOIN account_account as account ON asset.account_asset_id = account.id
                LEFT JOIN (
                    SELECT
                        COUNT(*) as count,
                        asset_id
                    FROM temp_account_move
                    WHERE asset_value_change != 't'
                    GROUP BY asset_id
                ) account_move_count ON asset.id = account_move_count.asset_id

                LEFT OUTER JOIN (
                    SELECT DISTINCT ON (asset_id)
                        id,
                        asset_depreciated_value,
                        asset_remaining_value,
                        amount_total,
                        asset_id
                    FROM temp_account_move m
                    WHERE date >= %(date_from)s AND date <= %(date_to)s {where_account_move}
                    ORDER BY asset_id, date, id DESC
                ) first_move ON first_move.asset_id = asset.id

                LEFT OUTER JOIN (
                    SELECT DISTINCT ON (asset_id)
                        id,
                        asset_depreciated_value,
                        asset_remaining_value,
                        amount_total,
                        asset_id
                    FROM temp_account_move m
                    WHERE date >= %(date_from)s AND date <= %(date_to)s {where_account_move}
                    ORDER BY asset_id, date DESC, id DESC
                ) last_move ON last_move.asset_id = asset.id

                LEFT OUTER JOIN (
                    SELECT DISTINCT ON (asset_id)
                        id,
                        asset_depreciated_value,
                        asset_remaining_value,
                        amount_total,
                        asset_id
                    FROM temp_account_move m
                    WHERE date <= %(date_from)s {where_account_move}
                    ORDER BY asset_id, date DESC, id DESC
                ) move_before ON move_before.asset_id = asset.id

                WHERE asset.company_id in %(company_ids)s
                AND asset.acquisition_date <= %(date_to)s
                AND (asset.disposal_date >= %(date_from)s OR asset.disposal_date IS NULL)
                AND asset.state not in ('model', 'draft')
                AND asset.asset_type = %(asset_type)s
                AND asset.active = 't'

                ORDER BY account.code, asset.acquisition_date;
            """.format(where_account_move=where_account_move)

        date_to = options['date']['date_to']
        date_from = options['date']['date_from']
        if options.get('multi_company', False):
            company_ids = tuple(self.env.companies.ids)
        else:
            company_ids = tuple(self.env.company.ids)

        self.flush()
        self.env.cr.execute(sql, {'date_to': date_to, 'date_from': date_from, 'company_ids': company_ids, 'asset_type': asset_type})
        results = self.env.cr.dictfetchall()
        self.env.cr.execute("DROP TABLE temp_account_move")  # Because tests are run in the same transaction, we need to clean here the SQL INHERITS
        return results

    def _get_lines(self, options, line_id=None):
        self = self._with_context_company2code2account()
        options['self'] = self
        lines = []
        total = [0] * 11
        asset_lines = self._get_assets_lines(options)
        curr_cache = {}

        for company_id, company_asset_lines in groupby(asset_lines, key=lambda x: x['company_id']):
            parent_lines = []
            children_lines = defaultdict(list)
            company = self.env['res.company'].browse(company_id)
            company_currency = company.currency_id
            for al in company_asset_lines:
                if al['parent_id']:
                    children_lines[al['parent_id']] += [al]
                else:
                    parent_lines += [al]
            for al in parent_lines:
                if al['asset_method'] == 'linear' and al[
                    'asset_method_number']:  # some assets might have 0 depreciations because they dont lose value
                    total_months = int(al['asset_method_number']) * int(al['asset_method_period'])
                    months = total_months % 12
                    years = total_months // 12
                    asset_depreciation_rate = " ".join(part for part in [
                        years and _("%s y", years),
                        months and _("%s m", months),
                    ] if part)
                elif al['asset_method'] == 'linear':
                    asset_depreciation_rate = '0.00 %'
                else:
                    asset_depreciation_rate = ('{:.2f} %').format(float(al['asset_method_progress_factor']) * 100)

                al_currency = self.env['res.currency'].browse(al['asset_currency_id'])
                al_rate = self._get_rate_cached(al_currency, company_currency, company, al['asset_acquisition_date'],
                                                curr_cache)

                depreciation_opening = company_currency.round(
                    al['depreciated_start'] * al_rate) - company_currency.round(al['depreciation'] * al_rate)
                depreciation_closing = company_currency.round(al['depreciated_end'] * al_rate)
                depreciation_minus = 0.0

                opening = (al['asset_acquisition_date'] or al['asset_date']) < fields.Date.to_date(
                    options['date']['date_from'])
                asset_opening = company_currency.round(al['asset_original_value'] * al_rate) if opening else 0.0
                asset_add = 0.0 if opening else company_currency.round(al['asset_original_value'] * al_rate)
                asset_minus = 0.0

                if al['import_depreciated']:
                    asset_opening += asset_add
                    asset_add = 0
                    depreciation_opening += al['import_depreciated']
                    depreciation_closing += al['import_depreciated']

                for child in children_lines[al['asset_id']]:
                    child_currency = self.env['res.currency'].browse(child['asset_currency_id'])
                    child_rate = self._get_rate_cached(child_currency, company_currency, company,
                                                       child['asset_acquisition_date'], curr_cache)

                    depreciation_opening += company_currency.round(
                        child['depreciated_start'] * child_rate) - company_currency.round(
                        child['depreciation'] * child_rate)
                    depreciation_closing += company_currency.round(child['depreciated_end'] * child_rate)

                    opening = (child['asset_acquisition_date'] or child['asset_date']) < fields.Date.to_date(
                        options['date']['date_from'])
                    asset_opening += company_currency.round(
                        child['asset_original_value'] * child_rate) if opening else 0.0
                    asset_add += 0.0 if opening else company_currency.round(child['asset_original_value'] * child_rate)

                depreciation_add = depreciation_closing - depreciation_opening
                asset_closing = asset_opening + asset_add

                if al['asset_state'] == 'close' and al['asset_disposal_date'] and al[
                    'asset_disposal_date'] <= fields.Date.to_date(options['date']['date_to']):
                    depreciation_minus = depreciation_closing
                    # depreciation_opening and depreciation_add are computed from first_move (assuming it is a depreciation move),
                    # but when previous condition is True and first_move and last_move are the same record, then first_move is not a
                    # depreciation move.
                    # In that case, depreciation_opening and depreciation_add must be corrected.
                    if al['first_move_id'] == al['last_move_id']:
                        depreciation_opening = depreciation_closing
                        depreciation_add = 0
                    depreciation_closing = 0.0
                    asset_minus = asset_closing
                    asset_closing = 0.0

                asset_gross = asset_closing - depreciation_closing

                # Sumatoria Datos Historicos
                x_history_cost_total = al['x_history_cost'] or 0
                x_accumulated_depreciation_total = al['x_accumulated_depreciation'] or 0

                #Variable total
                total = [x + y for x, y in zip(total, [x_history_cost_total,x_accumulated_depreciation_total, asset_opening, asset_add, asset_minus, asset_closing, depreciation_opening, depreciation_add, depreciation_minus, depreciation_closing, asset_gross])]

                asset_line_id = self._build_line_id([
                    (None, 'account.account', al['account_id']),
                    (None, 'account.asset', al['asset_id']),
                ])
                name = str(al['asset_name'])
                line = {
                    'id': asset_line_id,
                    'level': 1,
                    'name': name,
                    'account_code': al['account_code'],
                    'columns': [
                        {'name': self.format_value(x_history_cost_total), 'no_format_name': x_history_cost_total},
                        # Datos Historicos
                        {'name': al['x_date_purchase_his'] and format_date(self.env, al['x_date_purchase_his']) or '','no_format_name': ''},
                        # {'name': al['x_date_depreciation'] and format_date(self.env, al['x_date_depreciation']) or '', 'no_format_name': ''},
                        {'name': al['x_ussefull_life'] or '', 'no_format_name': ''},
                        {'name': al['x_deprecieted_periods'] or 0, 'no_format_name': ''},
                        {'name': self.format_value(x_accumulated_depreciation_total),'no_format_name': x_accumulated_depreciation_total},
                        {'name': al['asset_acquisition_date'] and format_date(self.env, al['asset_acquisition_date']) or '', 'no_format_name': ''},  # Characteristics
                        {'name': al['asset_date'] and format_date(self.env, al['asset_date']) or '', 'no_format_name': ''},
                        {'name': (al['asset_method'] == 'linear' and _('Linear')) or (al['asset_method'] == 'degressive' and _('Declining')) or _('Dec. then Straight'), 'no_format_name': ''},
                        {'name': asset_depreciation_rate, 'no_format_name': ''},
                        {'name': self.format_value(asset_opening + x_accumulated_depreciation_total), 'no_format_name': (asset_opening + x_accumulated_depreciation_total)},  # Assets
                        {'name': self.format_value(asset_add), 'no_format_name': asset_add},
                        {'name': self.format_value(asset_minus), 'no_format_name': asset_minus},
                        {'name': self.format_value(asset_closing + x_accumulated_depreciation_total), 'no_format_name': (asset_closing + x_accumulated_depreciation_total)},
                        {'name': self.format_value(depreciation_opening + x_accumulated_depreciation_total), 'no_format_name': (depreciation_opening + x_accumulated_depreciation_total)},  # Depreciation
                        {'name': self.format_value(depreciation_add), 'no_format_name': depreciation_add},
                        {'name': self.format_value(depreciation_minus), 'no_format_name': depreciation_minus},
                        {'name': self.format_value(depreciation_closing + x_accumulated_depreciation_total), 'no_format_name': (depreciation_closing + x_accumulated_depreciation_total)},
                        {'name': self.format_value(asset_gross), 'no_format_name': asset_gross},  # Gross
                    ],
                    'unfoldable': False,
                    'unfolded': False,
                    'caret_options': 'account.asset.line',
                    'account_id': al['account_id']
                }
                if len(name) >= MAX_NAME_LENGTH:
                    line.update({'title_hover': name})
                lines.append(line)
        lines.append({
            'id': 'total',
            'level': 0,
            'name': _('Total'),
            'columns': [
                {'name': self.format_value(total[0])},  # Datos Historicos
                {'name': ''},
                {'name': ''},
                {'name': ''},
                {'name': self.format_value(total[1])},
                {'name': ''},  # Characteristics
                {'name': ''},
                {'name': ''},
                {'name': ''},
                {'name': self.format_value(total[2])},  # Assets
                {'name': self.format_value(total[3])},
                {'name': self.format_value(total[4])},
                {'name': self.format_value(total[5])},
                {'name': self.format_value(total[6])},  # Depreciation
                {'name': self.format_value(total[7])},
                {'name': self.format_value(total[8])},
                {'name': self.format_value(total[9])},
                {'name': self.format_value(total[10])},  # Gross
            ],
            'unfoldable': False,
            'unfolded': False,
        })
        return lines
