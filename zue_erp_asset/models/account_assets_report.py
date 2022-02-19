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
                {'name': _('Datos históricos'), 'colspan': 6},
                {'name': _('Caracteristics'), 'colspan': 4},
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
                {'name': _('Acquisition Date'), 'class': 'text-center'},  # Caracteristics
                {'name': _('First Depreciation'), 'class': 'text-center'},
                {'name': _('Method'), 'class': 'text-center'},
                {'name': _('Rate'), 'class': 'number', 'title': _('In percent.<br>For a linear method, the depreciation rate is computed per year.<br>For a degressive method, it is the degressive factor'), 'data-toggle': 'tooltip'},
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
                       asset.value_residual as asset_value,
                       asset.original_value as asset_original_value,
                       asset.first_depreciation_date as asset_date,
                       asset.disposal_date as asset_disposal_date,
                       asset.acquisition_date as asset_acquisition_date,
                       asset.method as asset_method,
                       (
                           (SELECT COUNT(*) FROM temp_account_move WHERE asset_id = asset.id AND asset_value_change != 't')
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
                       COALESCE(first_move.amount_total, 0.0) as depreciation
                FROM account_asset as asset
                LEFT JOIN account_account as account ON asset.account_asset_id = account.id
                LEFT OUTER JOIN (SELECT MIN(date) as date, asset_id FROM temp_account_move WHERE date >= %(date_from)s AND date <= %(date_to)s {where_account_move} GROUP BY asset_id) min_date_in ON min_date_in.asset_id = asset.id
                LEFT OUTER JOIN (SELECT MAX(date) as date, asset_id FROM temp_account_move WHERE date >= %(date_from)s AND date <= %(date_to)s {where_account_move} GROUP BY asset_id) max_date_in ON max_date_in.asset_id = asset.id
                LEFT OUTER JOIN (SELECT MAX(date) as date, asset_id FROM temp_account_move WHERE date <= %(date_from)s {where_account_move} GROUP BY asset_id) max_date_before ON max_date_before.asset_id = asset.id
                LEFT OUTER JOIN temp_account_move as first_move ON first_move.id = (SELECT m.id FROM temp_account_move m WHERE m.asset_id = asset.id AND m.date = min_date_in.date ORDER BY m.id ASC LIMIT 1)
                LEFT OUTER JOIN temp_account_move as last_move ON last_move.id = (SELECT m.id FROM temp_account_move m WHERE m.asset_id = asset.id AND m.date = max_date_in.date ORDER BY m.id DESC LIMIT 1)
                LEFT OUTER JOIN temp_account_move as move_before ON move_before.id = (SELECT m.id FROM temp_account_move m WHERE m.asset_id = asset.id AND m.date = max_date_before.date ORDER BY m.id DESC LIMIT 1)
                WHERE asset.company_id in %(company_ids)s
                AND asset.acquisition_date <= %(date_to)s
                AND (asset.disposal_date >= %(date_from)s OR asset.disposal_date IS NULL)
                AND asset.state not in ('model', 'draft')
                AND asset.asset_type = 'purchase'
                AND asset.active = 't'

                ORDER BY account.code;
            """.format(where_account_move=where_account_move)

        date_to = options['date']['date_to']
        date_from = options['date']['date_from']
        company_ids = tuple(t['id'] for t in self._get_options_companies(options))

        self.flush()
        self.env.cr.execute(sql, {'date_to': date_to, 'date_from': date_from, 'company_ids': company_ids})
        results = self.env.cr.dictfetchall()
        self.env.cr.execute("DROP TABLE temp_account_move")  # Because tests are run in the same transaction, we need to clean here the SQL INHERITS
        return results

    def _get_lines(self, options, line_id=None):
        options['self'] = self
        lines = []
        total = [0] * 11
        asset_lines = self._get_assets_lines(options)

        for company_asset_lines in groupby(asset_lines, key=lambda x: x['company_id']):
            parent_lines = []
            children_lines = defaultdict(list)
            for al in company_asset_lines[1]:
                if al['parent_id']:
                    children_lines[al['parent_id']] += [al]
                else:
                    parent_lines += [al]
            for al in parent_lines:
                if al['asset_method'] == 'linear' and al['asset_method_number']:  # some assets might have 0 depreciations because they dont lose value
                    asset_depreciation_rate = ('{:.2f} %').format((100.0 / al['asset_method_number']) * (12 / int(al['asset_method_period'])))
                elif al['asset_method'] == 'linear':
                    asset_depreciation_rate = ('{:.2f} %').format(0.0)
                else:
                    asset_depreciation_rate = ('{:.2f} %').format(float(al['asset_method_progress_factor']) * 100)

                depreciation_opening = al['depreciated_start'] - al['depreciation']
                depreciation_closing = al['depreciated_end']
                depreciation_minus = 0.0

                opening = (al['asset_acquisition_date'] or al['asset_date']) < fields.Date.to_date(options['date']['date_from'])
                asset_opening = al['asset_original_value'] if opening else 0.0
                asset_add = 0.0 if opening else al['asset_original_value']
                asset_minus = 0.0

                for child in children_lines[al['asset_id']]:
                    depreciation_opening += child['depreciated_start'] - child['depreciation']
                    depreciation_closing += child['depreciated_end']

                    opening = (child['asset_acquisition_date'] or child['asset_date']) < fields.Date.to_date(options['date']['date_from'])
                    asset_opening += child['asset_original_value'] if opening else 0.0
                    asset_add += 0.0 if opening else child['asset_original_value']

                depreciation_add = depreciation_closing - depreciation_opening
                asset_closing = asset_opening + asset_add

                if al['asset_state'] == 'close' and al['asset_disposal_date'] and al['asset_disposal_date'] < fields.Date.to_date(options['date']['date_to']):
                    depreciation_minus = depreciation_closing
                    depreciation_closing = 0.0
                    depreciation_opening += depreciation_add
                    depreciation_add = 0
                    asset_minus = asset_closing
                    asset_closing = 0.0

                asset_gross = asset_closing - depreciation_closing

                # Sumatoria Datos Historicos
                x_history_cost_total = al['x_history_cost'] or 0
                x_accumulated_depreciation_total = al['x_accumulated_depreciation'] or 0

                #Variable total
                total = [x + y for x, y in zip(total, [x_history_cost_total,x_accumulated_depreciation_total,asset_opening, asset_add, asset_minus, asset_closing, depreciation_opening, depreciation_add, depreciation_minus, depreciation_closing, asset_gross])]

                id = "_".join([self._get_account_group_with_company(al['account_code'], al['company_id'])[0], str(al['asset_id'])])
                name = str(al['asset_name'])
                line = {
                    'id': id,
                    'level': 1,
                    'name': name if len(name) < MAX_NAME_LENGTH else name[:MAX_NAME_LENGTH - 2] + '...',
                    'columns': [
                        {'name': self.format_value(x_history_cost_total),'no_format_name': x_history_cost_total}, # Datos Historicos
                        {'name': al['x_date_purchase_his'] and format_date(self.env, al['x_date_purchase_his']) or '', 'no_format_name': ''},
                        # {'name': al['x_date_depreciation'] and format_date(self.env, al['x_date_depreciation']) or '', 'no_format_name': ''},
                        {'name': al['x_ussefull_life'] or '', 'no_format_name': ''},
                        {'name': al['x_deprecieted_periods'] or 0, 'no_format_name': ''},
                        {'name': self.format_value(x_accumulated_depreciation_total) , 'no_format_name': x_accumulated_depreciation_total},
                        {'name': al['asset_acquisition_date'] and format_date(self.env, al['asset_acquisition_date']) or '', 'no_format_name': ''},  # Caracteristics
                        {'name': al['asset_date'] and format_date(self.env, al['asset_date']) or '', 'no_format_name': ''},
                        {'name': (al['asset_method'] == 'linear' and _('Linear')) or (al['asset_method'] == 'degressive' and _('Degressive')) or _('Accelerated'), 'no_format_name': ''},
                        {'name': asset_depreciation_rate, 'no_format_name': ''},
                        {'name': self.format_value(asset_opening), 'no_format_name': asset_opening},  # Assets
                        {'name': self.format_value(asset_add), 'no_format_name': asset_add},
                        {'name': self.format_value(asset_minus), 'no_format_name': asset_minus},
                        {'name': self.format_value(asset_closing), 'no_format_name': asset_closing},
                        {'name': self.format_value(depreciation_opening), 'no_format_name': depreciation_opening},  # Depreciation
                        {'name': self.format_value(depreciation_add), 'no_format_name': depreciation_add},
                        {'name': self.format_value(depreciation_minus), 'no_format_name': depreciation_minus},
                        {'name': self.format_value(depreciation_closing), 'no_format_name': depreciation_closing},
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
                {'name': ''},  # Caracteristics
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
