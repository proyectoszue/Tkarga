# -*- coding: utf-8 -*-
from odoo import models


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def get_paperformat(self):
        # CxC/CxP: hoja ancha real (sin rotar). landscape=True de account_reports
        # intercambia width/height y deja solo 297mm de ancho util.
        if self.env.context.get('zue_aged_partner_wide_pdf'):
            return self.env['report.paperformat'].new({
                'name': 'Aged Partner Wide PDF',
                'format': 'custom',
                'page_width': 550,
                'page_height': 297,
                'orientation': 'Portrait',
                'margin_top': 8,
                'margin_bottom': 8,
                'margin_left': 3,
                'margin_right': 3,
                'header_line': False,
                'header_spacing': 0,
                'dpi': 96,
                'disable_shrinking': False,
            })
        return super().get_paperformat()

    def _run_wkhtmltopdf(self, bodies, report_ref=False, header=None, footer=None, landscape=False, specific_paperformat_args=None, set_viewport_size=False):
        if self.env.context.get('zue_aged_partner_wide_pdf'):
            landscape = False
        return super()._run_wkhtmltopdf(
            bodies,
            report_ref=report_ref,
            header=header,
            footer=footer,
            landscape=landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size,
        )
