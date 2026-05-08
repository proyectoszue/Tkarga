# -*- coding: utf-8 -*-

from odoo import models


class AccountReconcileModel(models.Model):
    _inherit = 'account.reconcile.model'

    def _apply_reconcile_models(self, statement_lines):
        if self.env.context.get('zue_force_exact_match_only'):
            lines_with_exact_match_only = statement_lines
        else:
            lines_with_exact_match_only = statement_lines.filtered(lambda line: line.company_id.z_bank_auto_reconcile_exact_match_only)
        standard_lines = statement_lines - lines_with_exact_match_only

        if standard_lines:
            return super()._apply_reconcile_models(standard_lines)

        return
