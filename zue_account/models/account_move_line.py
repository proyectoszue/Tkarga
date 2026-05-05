from odoo import api, fields, models
from odoo.fields import Domain


class account_move_line(models.Model):
    _inherit = 'account.move.line'

    tax_id = fields.Many2many(related='tax_ids', string="Impuestos")
    type_doc_partner = fields.Char(string='NIT Asociado', store=True)
    supplier_invoice_number = fields.Char(related='move_id.supplier_invoice_number',string='No. de factura del proveedor')
    required_analytic_account = fields.Boolean(related='account_id.required_analytic_account', string="Obliga cuenta analítica")
    required_partner = fields.Boolean(related='account_id.required_partner', string="Obliga tercero")
    accounting_class = fields.Char(string='Clase', store=True, related='account_id.accounting_class')
    account_group_id = fields.Many2one(related='account_id.group_id', string='Grupo Cuenta', store=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Cuenta Analítica',
                                          store=True,check_company=True, copy=True)

    def _zue_extract_company_ids_from_domain(self, domain):
        company_ids = set()

        def _walk(node):
            if isinstance(node, (list, tuple)):
                if len(node) == 3 and node[0] == 'company_id' and node[1] in ('=', 'in', 'child_of'):
                    value = node[2]
                    if isinstance(value, (list, tuple, set)):
                        company_ids.update(v for v in value if isinstance(v, int))
                    elif isinstance(value, int):
                        company_ids.add(value)
                else:
                    for item in node:
                        _walk(item)

        _walk(domain or [])
        return list(company_ids)

    def _zue_get_bank_rec_widget_domain(self, domain):
        if self.env.context.get('list_view_ref') != 'account_accountant.view_account_move_line_list_bank_rec_widget':
            return domain

        company_ids = self._zue_extract_company_ids_from_domain(domain)
        companies = self.env['res.company'].browse(company_ids) if company_ids else self.env.company
        if not companies.filtered('z_bank_auto_reconcile_receivable_payable_only'):
            return domain

        return list(Domain.AND([
            domain or [],
            [('search_account_id.account_type', 'in', ['asset_receivable', 'liability_payable'])],
        ]))

    @api.model
    def web_search_read(self, domain, specification, offset=0, limit=None, order=None, count_limit=None):
        domain = self._zue_get_bank_rec_widget_domain(domain)
        return super().web_search_read(
            domain,
            specification,
            offset=offset,
            limit=limit,
            order=order,
            count_limit=count_limit,
        )

    @api.model
    @api.readonly
    def web_read_group(self, domain, groupby, aggregates=(), limit=None, offset=0, order=None, *, auto_unfold=False,
                       opening_info=None, unfold_read_specification=None, unfold_read_default_limit=80, groupby_read_specification=None):
        domain = self._zue_get_bank_rec_widget_domain(domain)
        return super().web_read_group(domain, groupby, aggregates=aggregates, limit=limit, offset=offset, order=order, auto_unfold=auto_unfold,
                                      opening_info=opening_info, unfold_read_specification=unfold_read_specification, unfold_read_default_limit=unfold_read_default_limit,
                                      groupby_read_specification=groupby_read_specification)
