from odoo import fields, models, api


class ReportCertificationReport(models.AbstractModel):
    _inherit = 'l10n_co_reports.certification_report'

    def _get_domain(self, options):
        res = super(ReportCertificationReport, self)._get_domain(options)
        res += [('move_id.accounting_closing_id', '=', False)]
        return res