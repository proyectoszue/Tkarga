from odoo import models, fields, _
from odoo.exceptions import UserError


class account_tax_type(models.Model):
    _name = 'account.tax.type'
    _description = 'Tipo de Impuestos'

    code = fields.Char('Código')
    name = fields.Char('Descripción')
    retention = fields.Boolean('Retención')
    not_iclude = fields.Boolean('No incluir en FE')


class account_tax(models.Model):
    _inherit = 'account.tax'

    tax_type = fields.Many2one('account.tax.type', 'Tipo de Impuestos')


class AccountTaxRepartitionLine(models.Model):
    _inherit = 'account.tax.repartition.line'

    def _get_accounts_by_tax_type(self, tax_type, company):
        """Busca cuentas del plan contable asociadas al Tipo de Impuesto (retención)."""
        accounts = self.env['account.account'].search([('tax_type', '=', tax_type.id)])
        if company:
            accounts = accounts.filtered(lambda a: not a.company_ids or company in a.company_ids)
        return accounts

    def _get_aml_target_tax_account(self, force_caba_exigibility=False):
        account = super()._get_aml_target_tax_account(force_caba_exigibility=force_caba_exigibility)
        tax = self.tax_id
        if not tax or not tax.tax_type or not tax.tax_type.retention:
            return account

        if account:
            return account

        company = tax.company_id or self.company_id or self.env.company
        accounts = self._get_accounts_by_tax_type(tax.tax_type, company)
        if len(accounts) == 1:
            return accounts

        if not accounts:
            raise UserError(_(
                "El impuesto '%(tax)s' no tiene cuenta en su distribución y no existe "
                "ninguna cuenta contable con Tipo de Impuesto '%(tax_type)s'.\n"
                "Configure la cuenta en el impuesto (Distribución) o asocie el Tipo de Impuesto "
                "en Contabilidad / Configuración / Plan de Cuentas."
            ) % {
                'tax': tax.display_name,
                'tax_type': tax.tax_type.display_name,
            })

        raise UserError(_(
            "El impuesto '%(tax)s' no tiene cuenta configurada en su distribución "
            "y existen varias cuentas con Tipo de Impuesto '%(tax_type)s'.\n"
            "Configure la cuenta específica en el impuesto "
            "(Contabilidad → Impuestos → pestaña Distribución de factura/reembolso).\n"
            "Cuentas encontradas: %(accounts)s"
        ) % {
            'tax': tax.display_name,
            'tax_type': tax.tax_type.display_name,
            'accounts': ', '.join(accounts.mapped(lambda a: a.display_name)),
        })
