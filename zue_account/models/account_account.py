import re
from odoo import models, fields, api, _
from odoo.tools.float_utils import float_round as round
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_round
import math
import logging

#PLAN CONTABLE - PUC

class AccountGroup(models.Model):
    _inherit = "account.group"

    z_code_cgn = fields.Char(string='Codigo CGN')

class account_account(models.Model):
    _inherit = 'account.account'
    #_inherit = ['account.account','mail.thread', 'mail.activity.mixin'] // EN V18 YA LO HEREDA ODOO

    required_partner = fields.Boolean('Obliga tercero', tracking=True)
    accounting_class = fields.Char('Clase', tracking=True)
    exclude_balance_test = fields.Boolean('Permitir filtro de excluir en balance de prueba', tracking=True)
    z_not_disaggregate_partner_balance_test = fields.Boolean('No desagregar por tercero en balance de prueba', tracking=True)
    z_code_cgn = fields.Char(string='Codigo CGN')
    z_account_value = fields.Selection([
        ('1', 'Corriente'),
        ('2', 'No corriente')], string="Valor de cuenta")
    
    def _get_code_from_store(self):
        """Extrae el código de cuenta del campo code_store (JSON)
        El formato esperado es: {"1": "112000"}
        Retorna el valor de la clave '1' o el primer valor disponible
        """
        self.ensure_one()
        if not self.code_store:
            return ''
        import json
        try:
            # Si es string, parsearlo como JSON
            if isinstance(self.code_store, str):
                code_dict = json.loads(self.code_store)
            # Si ya es dict, usarlo directamente
            elif isinstance(self.code_store, dict):
                code_dict = self.code_store
            else:
                return ''
            
            # Extraer el valor de la clave '1' (preferido) o la primera clave disponible
            if '1' in code_dict:
                return str(code_dict['1']) if code_dict['1'] else ''
            elif code_dict:
                first_key = list(code_dict.keys())[0]
                return str(code_dict[first_key]) if code_dict[first_key] else ''
            return ''
        except (json.JSONDecodeError, AttributeError, TypeError, KeyError):
            return ''

# class ReportCertificationReport(models.AbstractModel): # IDENTIFICAR SI ESTO ES NECESARIO EN V18
#     _inherit = 'report.l10n_co_reports.report_certification'
#
#     def _get_lines(self, options, line_id=None):
#         lines = []
#         domain = []
#
#         domain += self._get_domain(options)
#
#         if line_id:
#             partner_id = re.search('partner_(.+)', line_id).group(1)
#             if partner_id:
#                 domain += [('partner_id.id', '=', partner_id)]
#
#         amls = self.env['account.move.line'].search(domain, order='partner_id, date, id')
#         previous_partner_id = self.env['res.partner']
#         lines_per_group = {}
#
#         for aml in amls:
#             if previous_partner_id != aml.partner_id:
#                 partner_lines = self._generate_lines_for_partner(previous_partner_id, lines_per_group, options)
#                 if partner_lines:
#                     lines += partner_lines
#                     lines_per_group = {}
#                 previous_partner_id = aml.partner_id
#
#             self._handle_aml(aml, lines_per_group)
#
#         lines += self._generate_lines_for_partner(previous_partner_id, lines_per_group, options)
#
#         return lines

class account_tax(models.Model):
    _inherit = 'account.tax'

    is_base_affected_only_taxes = fields.Boolean(string="Base afectada unicamente por los impuestos anteriores (Zue)")
    base_affected_only_taxes_id = fields.Many2one('account.tax', string="Base afectada unicamente por el impuesto")
    has_minimum_base = fields.Boolean(string="¿Tiene base mínima?")
    minimum_base = fields.Float(string="Base mínima")
    fiscal_position_ids = fields.Many2many(comodel_name='account.fiscal.position', relation='account_fiscal_position_account_tax_rel', column1='account_tax_id', column2='account_fiscal_position_id', tracking=True)

    """ ZUE
    Se añade la lógica al método estandar de v19 "_add_tax_details_in_base_line": 
    Para cambiar la base de cálculo de ciertos impuestos para que no se calculen sobre el subtotal del producto, sino sobre 
    otros impuestos (o sobre la suma de impuestos ya calculados) en base al campo personalizado "is_base_affected_only_taxes".
    """
    def _add_tax_details_in_base_line(self, base_line, company, rounding_method=None):
        super()._add_tax_details_in_base_line(base_line, company, rounding_method=rounding_method)
        self.zue_patch_only_taxes_base(base_line, company, rounding_method=rounding_method)

    def zue_patch_only_taxes_base(self, base_line, company, rounding_method=None):
        td = base_line.get("tax_details")
        if not td:
            return
        taxes_data = td.get("taxes_data") or []
        if not taxes_data:
            return

        # salir si no hay impuestos con el check is_base_affected_only_taxes marcado
        if not any(getattr(t["tax"], "is_base_affected_only_taxes", False) or getattr(t["tax"], "base_affected_only_taxes_id", False) for t in taxes_data):
            return

        currency = base_line["currency_id"]
        prec = currency.rounding
        method = rounding_method or company.tax_calculation_rounding_method
        if method == "round_globally":
            prec *= 1e-5

        sum_tax_amount = 0.0
        tax_amount_by_id = {}

        for tax_data in taxes_data:
            tax = tax_data["tax"]

            old_amount = tax_data.get("raw_tax_amount_currency", tax_data.get("tax_amount_currency", 0.0)) or 0.0
            old_base_amount = tax_data.get("raw_base_amount_currency", 0.0) or 0.0

            new_base = None
            if getattr(tax, "is_base_affected_only_taxes", False):
                new_base = sum_tax_amount
            elif getattr(tax, "base_affected_only_taxes_id", False):
                new_base = tax_amount_by_id.get(tax.base_affected_only_taxes_id.id, 0.0)

            if new_base is not None:
                if tax.amount_type == "percent":
                    new_amount = float_round(new_base * (tax.amount / 100.0), precision_rounding=prec)
                elif tax.amount_type == "fixed":
                    qty = abs(base_line.get("quantity", 0.0))
                    new_amount = float_round(qty * tax.amount, precision_rounding=prec)
                else:
                    # si no es percent/fixed (ej: python/division), no lo fuerzo aquí
                    new_amount = old_amount

                # mantener el signo de base original de Odoo para evitar inconsistencias
                base_sign = -1.0 if old_base_amount < 0 else 1.0
                tax_data["raw_base_amount_currency"] = base_sign * abs(float_round(new_base, precision_rounding=prec))
                tax_data["raw_tax_amount_currency"] = new_amount
                tax_data["tax_amount_currency"] = new_amount

                # ajustar total incluido por delta (mínimo)
                td["raw_total_included_currency"] += new_amount - old_amount
                current_tax_amount = new_amount
            else:
                current_tax_amount = old_amount

            # acumuladores ZUE
            sum_tax_amount += current_tax_amount
            tax_amount_by_id[tax.id] = current_tax_amount
