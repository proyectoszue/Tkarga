# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import re
from odoo.tools import SQL
from odoo.exceptions import ValidationError

class account_journal(models.Model):
    _inherit = 'account.journal'

    type = fields.Selection(tracking=True)
    company_id = fields.Many2one(tracking=True)
    code = fields.Char(tracking=True)
    z_secure_sequence_id = fields.Many2one('ir.sequence', string='Secuencia de seguridad (ZUE)')
    sequence_number_next = fields.Integer(tracking=True)
    default_account_id = fields.Many2one(tracking=True)
    z_stock_branch_id = fields.Many2one('zue.res.branch', string='Sucursal')

    # metodo original de odoo, herencia para corregir tableros por company_id ambiguo
    def _get_to_check_payment_query(self):
        query = self.env['account.move']._search([
            *self.env['account.move']._check_company_domain(self.env.companies),
            ('journal_id', 'in', self.ids),
            ('checked', '=', False),
            ('state', '=', 'posted'),
        ])
        selects = [
            SQL("account_move.journal_id"),
            SQL("account_move.company_id"),
            SQL("account_move.currency_id AS currency"),
            SQL("account_move.invoice_date_due < %s AS late", fields.Date.context_today(self)),
            SQL("SUM(account_move.amount_residual_signed) AS amount_total_company"),
            SQL("SUM((CASE WHEN account_move.move_type = 'in_invoice' THEN -1 ELSE 1 END) * amount_residual) AS amount_total"),
            SQL("COUNT(*)"),
            SQL("TRUE AS to_pay")
        ]
        return query, selects

class ProductTemplate(models.Model):
    _inherit = "product.template"

    z_income_return_account = fields.Many2one('account.account',string='Cuenta devolución de ingresos') # DEJAR ESTE CAMPO SI NO ES MULTICOMPAÑIA ERRORES JSONB
    # z_income_return_account = fields.Many2one('account.account', string='Cuenta devolución de ingresos', company_dependent=True, copy=False, check_company=True) DEJAR ESTE CAMPO SI ES MULTICOMPAÑIA

    z_account_analytic_id = fields.Many2one('account.analytic.account', string='Cuenta analitica', tracking=True,) # DEJAR ESTE CAMPO SI NO ES MULTICOMPAÑIA ERRORES JSONB
    # z_account_analytic_id = fields.Many2one('account.analytic.account', string='Cuenta analitica', company_dependent=True, tracking=True,)

    @api.constrains('z_account_analytic_id', 'company_id')
    def _check_z_account_analytic_company(self):
        for record in self:
            analytic_account = record.z_account_analytic_id
            if not analytic_account or not analytic_account.company_id or not record.company_id:
                continue

            if analytic_account.company_id != record.company_id:
                raise ValidationError(_(
                    "La cuenta analitica '%(analytic)s' pertenece a la compania '%(analytic_company)s' "
                    "y no coincide con la compania del producto '%(product_company)s'.",
                    analytic=analytic_account.display_name,
                    analytic_company=analytic_account.company_id.display_name,
                    product_company=record.company_id.display_name,
                ))

    def _z_analytic_distribution_model_domain(self, product, company):
        return [
            ('product_id', '=', product.id),
            ('partner_id', '=', False),
            ('partner_category_id', '=', False),
            ('product_categ_id', '=', False),
            ('account_prefix', '=', False),
            ('company_id', '=', company.id),
        ]

    def _z_clear_analytic_distribution_models(self):
        """Elimina reglas creadas por esta automatización cuando no hay cuenta analítica."""
        distribution_model_obj = self.env['account.analytic.distribution.model']
        for record in self:
            for product in record.product_variant_ids:
                target_company = product.company_id or record.company_id or self.env.company
                domain = self._z_analytic_distribution_model_domain(product, target_company)
                distribution_model_obj.search(domain).unlink()

    def _z_sync_analytic_distribution_models(self):
        distribution_model_obj = self.env['account.analytic.distribution.model']
        for record in self:
            analytic_account = record.z_account_analytic_id
            if not analytic_account:
                continue

            for product in record.product_variant_ids:
                target_company = analytic_account.company_id or product.company_id or self.env.company
                domain = self._z_analytic_distribution_model_domain(product, target_company)
                model_vals = {
                    'product_id': product.id,
                    'analytic_distribution': {analytic_account.id: 100.0},
                    'company_id': target_company.id,
                }
                distribution_models = distribution_model_obj.search(domain)
                if distribution_models:
                    distribution_models.write(model_vals)
                else:
                    distribution_model_obj.create(model_vals)

    @api.model_create_multi
    def create(self, values_list):
        res = super(ProductTemplate, self).create(values_list)
        res._z_sync_analytic_distribution_models()
        return res

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if 'z_account_analytic_id' in vals:
            if vals.get('z_account_analytic_id'):
                self._z_sync_analytic_distribution_models()
            else:
                self._z_clear_analytic_distribution_models()
        return res


class ProductCategory(models.Model):
    _inherit = "product.category"

    z_income_return_account = fields.Many2one('account.account', string='Cuenta devolución de ingresos', company_dependent=True, copy=False, check_company=True)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model_create_multi
    def create(self, vals_list):
        products = super().create(vals_list)
        products.mapped('product_tmpl_id').filtered('z_account_analytic_id')._z_sync_analytic_distribution_models()
        return products


class account_move(models.Model):
    _inherit = 'account.move'

    def _z_get_income_return_account(self, line):
        product = line.product_id
        if not product:
            return False
        category_account = product.product_tmpl_id.categ_id.z_income_return_account
        if category_account:
            return category_account
        return product.product_tmpl_id.z_income_return_account

    def _z_apply_income_return_accounts_for_refund(self):
        """En notas crédito, sustituye cuentas de ingreso por la cuenta de devolución configurada.

        Al cambiar ``account_id``, Odoo puede recrear líneas; se aplica un cambio por vuelta,
        se invalida ``line_ids`` y se repite hasta que no quede ninguna corrección pendiente.
        """
        income_types = ('income', 'income_other')
        for move in self:
            if move.move_type not in ('out_refund', 'in_refund'):
                continue
            pending = True
            while pending:
                pending = False
                move.invalidate_recordset(['line_ids'])
                for line in move.line_ids:
                    if not line.product_id or not line.account_id:
                        continue
                    if line.account_id.account_type not in income_types:
                        continue
                    return_acc = move._z_get_income_return_account(line)
                    if return_acc and line.account_id != return_acc:
                        line.write({'account_id': return_acc.id})
                        pending = True
                        break

    z_delay_days = fields.Integer(string='Días retraso factura', compute='_z_delay_days')

    @api.model_create_multi
    def create(self, values_list):
        # standard Odoo version "19"
        invoices = super().create(values_list)
        invoices.filtered(lambda m: m.move_type in ('out_refund', 'in_refund'))._z_apply_income_return_accounts_for_refund()
        return invoices
