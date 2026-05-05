from odoo import api, models
from odoo.fields import Domain


class AccountReport(models.Model):
    _inherit = 'account.report'

    @api.model
    def _get_options_unreconciled_domain(self, options):
        if options.get('unreconciled'):
            return Domain('reconciled', '=', False)
        return Domain.TRUE
