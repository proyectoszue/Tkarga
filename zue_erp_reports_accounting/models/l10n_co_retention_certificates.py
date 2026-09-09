# -*- coding: utf-8 -*-
from odoo import models


class L10nCoIcaReportHandler(models.AbstractModel):
    _inherit = 'l10n_co.ica.report.handler'

    def _get_domain(self, report, options, line_dict_id=None):
        domain = super()._get_domain(report, options, line_dict_id=line_dict_id)
        domain = [
            term for term in domain
            if term != ('tax_line_id.type_tax_use', '=', 'purchase')
            and not (
                isinstance(term, (list, tuple))
                and len(term) == 3
                and term[0] == 'tax_line_id.l10n_co_edi_type.code'
            )
        ]
        domain += [
            '|',
            '&',
            ('tax_line_id.type_tax_use', '=', 'purchase'),
            '|', '|',
            ('tax_line_id.tax_type.code', '=', '07'),
            ('account_id.tax_type.code', '=', '07'),
            ('account_id.code', '=like', '2368%'),
            '&',
            ('tax_line_id', '=', False),
            '|',
            ('account_id.tax_type.code', '=', '07'),
            ('account_id.code', '=like', '2368%'),
        ]
        return domain


class L10nCoFuenteReportHandler(models.AbstractModel):
    _inherit = 'l10n_co.fuente.report.handler'

    def _get_domain(self, report, options, line_dict_id=None):
        domain = super()._get_domain(report, options, line_dict_id=line_dict_id)
        domain = [
            term for term in domain
            if term != ('tax_line_id.type_tax_use', '=', 'purchase')
            and not (
                isinstance(term, (list, tuple))
                and len(term) == 3
                and term[0] == 'tax_line_id.l10n_co_edi_type.code'
            )
        ]
        domain += [
            '|',
            '&',
            ('tax_line_id.type_tax_use', '=', 'purchase'),
            '|', '|',
            ('tax_line_id.tax_type.code', '=', '06'),
            ('account_id.tax_type.code', '=', '06'),
            '&',
            ('account_id.code', '=like', '2365%'),
            ('account_id.code', '!=', '236505'),
            '&',
            ('tax_line_id', '=', False),
            '|',
            ('account_id.tax_type.code', '=', '06'),
            '&',
            ('account_id.code', '=like', '2365%'),
            ('account_id.code', '!=', '236505'),
        ]
        return domain


class L10nCoIvaReportHandler(models.AbstractModel):
    _inherit = 'l10n_co.iva.report.handler'

    def _get_domain(self, report, options, line_dict_id=None):
        domain = super()._get_domain(report, options, line_dict_id=line_dict_id)
        domain = [
            term for term in domain
            if term != ('tax_line_id.type_tax_use', '=', 'purchase')
            and not (
                isinstance(term, (list, tuple))
                and len(term) == 3
                and term[0] == 'tax_line_id.l10n_co_edi_type.code'
            )
        ]
        domain += [
            '|',
            '&',
            ('tax_line_id.type_tax_use', '=', 'purchase'),
            '|', '|',
            ('tax_line_id.tax_type.code', '=', '05'),
            ('account_id.tax_type.code', '=', '05'),
            ('account_id.code', '=like', '2367%'),
            '&',
            ('tax_line_id', '=', False),
            '|',
            ('account_id.tax_type.code', '=', '05'),
            ('account_id.code', '=like', '2367%'),
        ]
        return domain
