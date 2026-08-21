# -*- coding: utf-8 -*-
from odoo import models, tools


class account_journal(models.Model):
    _inherit = 'account.journal'

    def zue_match_reconciliation(self):
        cron_limit_time = tools.config['limit_time_real_cron'] or -1
        limit_time = cron_limit_time if 0 < cron_limit_time < 180 else 180

        statement_lines = self.env['account.bank.statement.line'].search([('journal_id', '=', self.id), ('is_reconciled', '=', False)])

        if statement_lines:
            # Force exact-mode during custom Auto Conciliar runs.
            statement_lines.with_context(zue_force_exact_match_only=True)._cron_try_auto_reconcile_statement_lines(limit_time=limit_time)

        return True
