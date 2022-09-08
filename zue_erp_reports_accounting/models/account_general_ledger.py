from odoo import models, fields, api, _


class account_general_ledger(models.AbstractModel):
    _inherit = "account.general.ledger"

    @api.model
    def _get_report_name(self):
        return "Libro de Inventario y Balance"