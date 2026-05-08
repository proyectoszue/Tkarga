# -*- coding: utf-8 -*-

from odoo import models


class AccountFollowupReportHandler(models.AbstractModel):
    _inherit = 'account.followup.report.handler'

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

