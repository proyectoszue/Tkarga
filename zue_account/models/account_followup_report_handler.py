# -*- coding: utf-8 -*-

import unicodedata
from uuid import uuid4

from odoo import models


class AccountFollowupReportHandler(models.AbstractModel):
    _inherit = 'account.followup.report.handler'

    def _get_followup_section(self, line_name):
        normalized = unicodedata.normalize('NFKD', (line_name or '').strip().lower())
        normalized = ''.join(character for character in normalized if not unicodedata.combining(character))

        due_labels = ('a vencer', 'por vencer', 'no vencid', 'not due', 'no adeudado')
        overdue_labels = ('vencid', 'overdue', 'retraso')

        if normalized == 'due' or any(label in normalized for label in due_labels):
            return 'due'
        if any(label in normalized for label in overdue_labels):
            return 'overdue'
        if normalized == 'adeudado':
            return 'due'
        return None

    def _custom_options_initializer(self, report, options, previous_options=None):
        super()._custom_options_initializer(report, options, previous_options=previous_options)

        followup_report = self.env.ref('account_reports.followup_report', raise_if_not_found=False)
        if not followup_report or report.id != followup_report.id:
            return

        column_labels = {
            'invoice_date': 'Fecha factura',
            'date_maturity': 'Fecha vencimiento',
            'amount': 'Valor factura origen',
            'balance': 'Saldo adeudado',
        }

        for column in options.get('columns', []):
            column['name'] = column_labels.get(column.get('expression_label'), column['name'])

        options['columns'] = [
            column for column in options.get('columns', [])
            if column.get('expression_label') != 'amount_currency'
        ]

    def _get_partner_aml_report_lines(self, report, options, partner_line_id, aml_results, progress, offset=0, level_shift=0):
        section_labels = {
            'overdue': ('Facturas vencidas', 'Total facturas vencidas'),
            'due': ('Facturas a vencer', 'Total facturas a vencer'),
        }

        super_result = super()._get_partner_aml_report_lines(
            report, options, partner_line_id, aml_results, progress,
            offset=offset, level_shift=level_shift,
        )
        lines, *rest = super_result

        columns = [column.get('expression_label') for column in options.get('columns', [])]
        amount_idx = columns.index('amount') if 'amount' in columns else None
        balance_idx = columns.index('balance') if 'balance' in columns else None

        def num(line_dict, column_idx):
            if column_idx is None:
                return 0.0
            cells = line_dict.get('columns') or []
            if len(cells) <= column_idx:
                return 0.0
            cell = cells[column_idx]
            raw = cell.get('no_format', 0.0) if isinstance(cell, dict) else cell
            return float(raw or 0.0)

        def build_subtotal(section, parent_id, detail_lines):
            total_amount = sum(num(line, amount_idx) for line in detail_lines)
            total_balance = sum(num(line, balance_idx) for line in detail_lines)
            _, subtotal_title = section_labels[section]

            return {
                'id': report._get_generic_line_id(None, None, markup='sub_%s' % uuid4().hex, parent_line_id=parent_id),
                'name': subtotal_title,
                'level': 4 + level_shift,
                'parent_id': parent_id,
                'columns': [
                    report._build_column_dict(
                        total_amount if i == amount_idx else total_balance if i == balance_idx else False,
                        column_def,
                        options=options,
                    )
                    for i, column_def in enumerate(options.get('columns', []))
                ],
                'unfolded': True,
            }

        out = []
        active_section = None
        section_id = None
        section_lines = []

        for line in lines:
            section = self._get_followup_section(line.get('name'))
            if section:
                if active_section and section_lines:
                    out.append(build_subtotal(active_section, section_id, section_lines))

                active_section = section
                section_id = line.get('id')
                section_lines = []
                out.append({**line, 'name': section_labels[section][0]})
                continue

            if active_section and line.get('parent_id') == section_id and line.get('columns'):
                section_lines.append(line)
                out.append(line)
                continue

            if active_section and section_lines:
                out.append(build_subtotal(active_section, section_id, section_lines))
            active_section = None
            section_id = None
            section_lines = []
            out.append(line)

        if active_section and section_lines:
            out.append(build_subtotal(active_section, section_id, section_lines))

        if isinstance(super_result, tuple):
            return (out, *rest)
        return [out, *rest]

    def _dynamic_lines_generator(self, report, options, all_column_groups_expression_totals, warnings=None):
        lines = super()._dynamic_lines_generator(report, options, all_column_groups_expression_totals, warnings=warnings)

        followup_report = self.env.ref('account_reports.followup_report', raise_if_not_found=False)
        if not followup_report or report.id != followup_report.id:
            return lines

        balance_col_indexes = [i for i, c in enumerate(options.get('columns', [])) if c.get('expression_label') == 'balance']
        if not balance_col_indexes:
            return lines

        self.env['account.move.line'].flush_model()
        residual_total_by_group = {}
        column_groups = options.get('column_groups') or {}
        if not column_groups:
            domain = report._get_options_domain(options, 'strict_range')
            amls = self.env['account.move.line'].search(domain)
            total_residual = sum(amls.mapped('amount_residual'))
            for col_idx in balance_col_indexes:
                gk = options['columns'][col_idx].get('column_group_key')
                residual_total_by_group.setdefault(gk, total_residual)
        else:
            for group_key in column_groups:
                group_options = report._get_column_group_options(options, group_key)
                domain = report._get_options_domain(group_options, 'strict_range')
                amls = self.env['account.move.line'].search(domain)
                residual_total_by_group[group_key] = sum(amls.mapped('amount_residual'))

        for _idx, (_seq, line_dict) in enumerate(lines):
            line_id = line_dict.get('id')
            if not line_id:
                continue

            if report._parse_line_id(line_id)[-1][0] == 'total':
                for col_idx in balance_col_indexes:
                    col_def = options['columns'][col_idx]
                    gk = col_def.get('column_group_key')
                    line_dict['columns'][col_idx] = report._build_column_dict(
                        residual_total_by_group.get(gk, 0.0),
                        col_def,
                        options=options,
                    )

        return lines

    def _get_report_line_move_line(self, options, aml_query_result, partner_line_id, init_bal_by_col_group, level_shift=0):
        line = super()._get_report_line_move_line(options, aml_query_result, partner_line_id, init_bal_by_col_group, level_shift=level_shift)

        report = self.env['account.report'].browse(options['report_id'])
        followup_report = self.env.ref('account_reports.followup_report', raise_if_not_found=False)
        if not followup_report or report.id != followup_report.id:
            return line

        aml = self.env['account.move.line'].browse(aml_query_result['id'])
        for i, col_def in enumerate(options['columns']):
            if col_def.get('expression_label') != 'balance':
                continue
            line['columns'][i] = report._build_column_dict(aml.amount_residual, col_def, options=options)
            break

        return line

