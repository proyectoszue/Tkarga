from odoo import api, models
from odoo.fields import Domain


class AccountReport(models.Model):
    _inherit = 'account.report'

    @api.model
    def _get_options_unreconciled_domain(self, options):
        if options.get('unreconciled'):
            return Domain('reconciled', '=', False)
        return Domain.TRUE


class AccountReportExpression(models.Model):
    _inherit = 'account.report.expression'

    @api.model
    def _zue_bind_existing_aged_partner_xmlids(self):
        """
        Link our XML IDs to existing aged partner expressions when they already
        exist in DB (base data or previous migrations), avoiding duplicate-key
        errors on (report_line_id, label) during module load.
        """
        xmlid_specs = (
            ('account_reports.aged_receivable_line', 'supplier_invoice_number', 'aged_receivable_line_supplier_invoice_number'),
            ('account_reports.aged_receivable_line', 'z_due_date', 'aged_receivable_line_due_date'),
            ('account_reports.aged_receivable_line', 'z_amount_currency', 'aged_receivable_line_amount_currency'),
            ('account_reports.aged_receivable_line', 'z_currency', 'aged_receivable_line_currency'),
            ('account_reports.aged_receivable_line', 'z_move_ref', 'aged_receivable_line_move_ref'),
            ('account_reports.aged_receivable_line', 'invoice_user_name', 'aged_receivable_line_invoice_user_name'),
            ('account_reports.aged_receivable_line', 'z_account_name', 'aged_receivable_line_account_name'),
            ('account_reports.aged_receivable_line', 'z_expected_date', 'aged_receivable_line_expected_date'),
            ('account_reports.aged_receivable_line', 'partner_name', 'aged_receivable_line_z_partner_name'),
            ('account_reports.aged_receivable_line', 'partner_user_name', 'aged_receivable_line_z_user_name'),
            ('account_reports.aged_payable_line', 'supplier_invoice_number', 'aged_payable_line_supplier_invoice_number'),
            ('account_reports.aged_payable_line', 'z_due_date', 'aged_payable_line_due_date'),
            ('account_reports.aged_payable_line', 'z_amount_currency', 'aged_payable_line_amount_currency'),
            ('account_reports.aged_payable_line', 'z_currency', 'aged_payable_line_currency'),
            ('account_reports.aged_payable_line', 'z_move_ref', 'aged_payable_line_move_ref'),
            ('account_reports.aged_payable_line', 'invoice_user_name', 'aged_payable_line_invoice_user_name'),
            ('account_reports.aged_payable_line', 'z_account_name', 'aged_payable_line_account_name'),
            ('account_reports.aged_payable_line', 'z_expected_date', 'aged_payable_line_expected_date'),
            ('account_reports.aged_payable_line', 'partner_name', 'aged_payable_line_z_partner_name'),
            ('account_reports.aged_payable_line', 'partner_user_name', 'aged_payable_line_z_user_name'),
        )
        ir_model_data = self.env['ir.model.data'].sudo()

        for line_xmlid, label, name in xmlid_specs:
            module = 'zue_account'
            if ir_model_data.search([('module', '=', module), ('name', '=', name)], limit=1):
                continue

            report_line = self.env.ref(line_xmlid, raise_if_not_found=False)
            if not report_line:
                continue

            expression = self.search(
                [('report_line_id', '=', report_line.id), ('label', '=', label)],
                limit=1,
            )
            if not expression:
                continue

            ir_model_data.create({
                'module': module,
                'name': name,
                'model': 'account.report.expression',
                'res_id': expression.id,
                'noupdate': False,
            })
