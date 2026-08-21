from odoo.exceptions import ValidationError, UserError
from odoo import models, fields, api, _
import base64
from datetime import date
import math, json


class AccountMove(models.Model):
    _inherit = 'account.move'

    z_fe_encab = fields.One2many('zue.fe.encab', 'z_move_id', 'FE Encab')
    z_fe_encab_tax = fields.One2many('zue.fe.encab.tax', 'z_move_id', 'FE Encab Impuesto')
    z_fe_detail = fields.One2many('zue.fe.detail', 'z_move_id', 'FE Detalle')
    z_fe_detail_tax = fields.One2many('zue.fe.detail.tax', 'z_move_id', 'FE Detalle Impuesto')
    z_value_tax_fe = fields.Float(string='Impuesto sin redondeo')

    def get_xml_v2(self):
        self.fill_fe_table()

        xml = None
        if self.pos_order_ids:
            obj_xml = self.env['zue.xml.generator.header'].search([('code', '=', 'POSFacElectronica_' + self.env.company.zue_electronic_invoice_operator + 'v2')])
        else:
            obj_xml = self.env['zue.xml.generator.header'].search([('code', '=', 'FacElectronica_' + self.env.company.zue_electronic_invoice_operator + 'v2')])
        if not obj_xml:
            raise ValidationError(_("Error! No ha configurado un XML con el nombre '{}'".format(('POSFacElectronica_' if self.pos_order_ids else 'FacElectronica_') + self.env.company.zue_electronic_invoice_operator + "v2")))

        xml = obj_xml.xml_generator(self)
        xml = xml.decode("UTF-8").replace("<ITE/>", "").replace("<TII/>", "").replace("<cfc", "<cfc:").replace("</cfc", "</cfc:").replace("<dte", "<dte:").replace("</dte", "</dte:").replace("<cno", "<cno:").replace("</cno", "</cno:").replace("<cex", "<cex:").replace("</cex", "</cex:")

        if self.pos_order_ids:
            filename = f'POS_FE_v2_{date.today().year}_{self.name}_{self.partner_id.name}.xml'
        else:
            filename = f'FE_v2_{date.today().year}_{self.name}_{self.partner_id.name}.xml'

        if self.xml_file_name:
            attachment = self.env['ir.attachment'].search(
                [('res_model', '=', 'account.move'), ('res_id', '=', self.id), ('name', '=', self.xml_file_name)])
            attachment.unlink()

        self.write({
            'xml_file': base64.encodebytes(bytes(xml, 'UTF-8')),
            'xml_file_name': filename,
        })

        data_attach = {'name': filename,
                       'type': 'binary', 'datas': self.xml_file, 'res_name': filename, 'store_fname': filename,
                       'res_model': 'account.move', 'res_id': self.id}

        atts_id = self.env['ir.attachment'].create(data_attach)

        self.message_post(body='XML generado correctamente.', attachment_ids=atts_id.ids)

        return True


    def fill_fe_table(self):
        self.z_fe_encab.unlink()
        self.z_fe_encab_tax.unlink()
        self.z_fe_detail.unlink()
        self.z_fe_detail_tax.unlink()

        # Se llenan tablas para el encabezado
        domain = ['&','&',('move_id', '=', self.id), ('name', '!=', self.name), ('balance', '!=', 0), ('price_subtotal', '!=', self.amount_total*-1)]
        obj_lines = self.env['account.move.line'].search(domain, order='id')

        total, totalret, base = 0, 0, 0
        tax_lines_encab = []
        line_detail = []
        total_base = 0
        tasa_otra_moneda = 0
        invoice_base_lines = obj_lines.filtered(
            lambda line: (
                line.display_type == 'product'
                and (
                    line.account_id.internal_group == 'income'
                    or (line.account_id.internal_group == 'expense' and line.move_id.move_type in ('out_refund', 'in_refund'))
                )
            )
        )
        included_invoice_tax_ids = set(
            invoice_base_lines.mapped('tax_ids').filtered(
                lambda tax: tax.tax_type and not tax.tax_type.not_iclude
            ).ids
        )

        for lines in obj_lines:
            if lines.currency_id != self.company_id.currency_id and not tasa_otra_moneda:
                line_amount_currency = abs(lines.amount_currency) if abs(lines.amount_currency) else abs(lines.price_subtotal)
                tasa_otra_moneda = abs(lines.balance) / line_amount_currency if line_amount_currency and abs(lines.balance) else 1

            line_amount = abs(lines.balance) if lines.currency_id == self.company_id.currency_id else abs(lines.amount_currency or lines.price_subtotal)
            is_rounding_line = lines.display_type == 'rounding'
            is_tax_line = bool(lines.tax_line_id and (lines.tax_base_amount or lines.display_type == 'tax'))

            if is_rounding_line:
                affects_invoice_line = (
                    lines.account_id.internal_group == 'income'
                    or (lines.account_id.internal_group == 'expense' and lines.move_id.move_type in ('out_refund', 'in_refund'))
                )
                affects_included_tax = bool(
                    lines.tax_line_id
                    and lines.tax_line_id.id in included_invoice_tax_ids
                    and lines.tax_line_id.tax_type
                    and not lines.tax_line_id.tax_type.not_iclude
                )

                if (affects_invoice_line or affects_included_tax) and (
                    not lines.tax_line_id
                    or (lines.tax_line_id.tax_type and not lines.tax_line_id.tax_type.retention)
                ):
                    total += line_amount
                continue

            if is_tax_line:
                # obj_tax = self.env['account.tax'].search([('name', '=', lines.name), ('tax_type.not_iclude', '=', False)], limit=1)
                if not lines.tax_line_id.tax_type.not_iclude:
                # if obj_tax:
                    if lines.tax_line_id.tax_type.is_aiu:
                        total += line_amount
                        totalret += line_amount
                        base += line_amount

                        line_detail.append({'z_move_id': lines.move_id.id,
                                            'z_move_line_id': lines.id,
                                            'z_quantity': lines.quantity,
                                            'z_value_base': line_amount})
                    else:
                        totalret += line_amount

                        if not lines.tax_line_id.tax_type.retention:
                            total += line_amount

                        tax_base_amount = abs(lines.tax_base_amount or 0.0)

                        tax_line_encab = {
                            'z_move_id': self.id,
                            'z_code': lines.tax_line_id.tax_type.code,
                            'z_value_tax': line_amount,
                            'z_percent': abs(lines.tax_line_id.amount),
                            'z_value_base': tax_base_amount if lines.currency_id == self.company_id.currency_id else tax_base_amount / (tasa_otra_moneda or 1),
                            'z_retention': lines.tax_line_id.tax_type.retention
                        }
                        tax_lines_encab.append(tax_line_encab)
            else:
                if (lines.display_type == 'product'
                    and (lines.account_id.internal_group == 'income' or (lines.account_id.internal_group == 'expense' and lines.move_id.move_type in ('out_refund', 'in_refund')))):
                    if lines.name:
                        total += line_amount
                        if 'redondeo' not in lines.name:
                            totalret += line_amount
                            base += line_amount
                    if lines.product_id:
                        if lines.tax_ids:
                            total_base += line_amount

                    line_detail.append({'z_move_id': lines.move_id.id,
                                        'z_move_line_id': lines.id,
                                        'z_quantity': lines.quantity,
                                        'z_value_base': line_amount})

        # total_decimals = ""
        # decimals = 0
        #
        # total_decimals = str(total).split('.')
        # if len(total_decimals) > 1:
        #     decimals = int(total_decimals[1])
        #
        #     if decimals <= 50:

        # Se crea un nuevo item para redondear la factura
        # parte_decimal, parte_entera = math.modf(total)
        # redondeo_total = 1 - round(parte_decimal, 2)
        # if redondeo_total < 1:
        #     line_detail.append({'z_move_id': lines.move_id.id,
        #                         'z_move_line_id': None,
        #                         'z_quantity': 1,
        #                         'z_value_base':  redondeo_total
        #                         })
        redondeo_total = 99

        encab = self.env['zue.fe.encab'].create({
            'z_move_id': self.id,
            'z_value_total': total + (redondeo_total if redondeo_total < 1 else 0),
            'z_value_total_with_ret': totalret + (redondeo_total if redondeo_total < 1 else 0),
            'z_value_base': base + (redondeo_total if redondeo_total < 1 else 0),
            'z_currency_id': self.currency_id.id,
            'z_exchange_rate': tasa_otra_moneda
        })

        tax_encab = self.env['zue.fe.encab.tax'].create(tax_lines_encab)
        detail = self.env['zue.fe.detail'].create(line_detail)

        tax_lines_detail = []
        detail_move_lines = detail.mapped('z_move_line_id').filtered(lambda line: line and not line.tax_line_id)
        detail_move_line_ids = set(detail_move_lines.ids)

        def filter_tax_values_to_apply(base_line, tax_data):
            tax = tax_data.get('tax')
            return bool(
                tax
                and tax.tax_type
                and not tax.tax_type.is_aiu
                and not tax.tax_type.not_iclude
            )

        def grouping_key_generator(base_line, tax_data):
            tax = tax_data['tax']
            return {
                'tax_id': tax.id,
                'code': tax.tax_type.code,
                'percent': abs(tax.amount),
                'retention': tax.tax_type.retention,
            }

        tax_details_result = self._prepare_invoice_aggregated_taxes(
            filter_invl_to_apply=lambda line: line.id in detail_move_line_ids,
            filter_tax_values_to_apply=filter_tax_values_to_apply,
            grouping_key_generator=grouping_key_generator,
        )
        tax_details_by_line_id = {
            record.id: values for record, values in tax_details_result.get('tax_details_per_record', {}).items()
        }
        use_invoice_currency = self.currency_id != self.company_id.currency_id

        for item in detail:
            if not item.z_move_line_id or item.z_move_line_id.tax_line_id:
                continue

            line_tax_details = tax_details_by_line_id.get(item.z_move_line_id.id, {}).get('tax_details', {})
            for grouping_key, values in line_tax_details.items():
                value_tax = abs(values['tax_amount_currency']) if use_invoice_currency else abs(values['tax_amount'])
                value_base = abs(values['base_amount_currency']) if use_invoice_currency else abs(values['base_amount'])
                if not value_tax and not value_base:
                    continue

                tax_lines_detail.append({
                    'z_detail_id': item.id,
                    'z_move_id': item.z_move_id.id,
                    'z_move_line_id': item.z_move_line_id.id,
                    'z_code': grouping_key['code'],
                    'z_value_tax': value_tax,
                    'z_percent': grouping_key['percent'],
                    'z_value_base': value_base,
                    'z_retention': grouping_key['retention'],
                })

        detail_tax = self.env['zue.fe.detail.tax'].create(tax_lines_detail)

        return True


class zue_fe_encab(models.TransientModel):
    _name = 'zue.fe.encab'
    _description = 'Encabezado de facturación electrónica ZUE'

    z_move_id = fields.Many2one('account.move', string='Movimiento contable')
    z_value_total = fields.Float(string='Valor Total')
    z_value_total_with_ret = fields.Float(string='Valor Total con Ret')
    z_value_base = fields.Float(string='Valor Base')
    z_currency_id = fields.Many2one('res.currency', string='Moneda')
    z_exchange_rate = fields.Float(string='Tasa de cambio')


class zue_fe_encab_tax(models.TransientModel):
    _name = 'zue.fe.encab.tax'
    _description = 'Impuestos del encabezado de facturación electrónica ZUE'
    _order = "z_code asc"

    z_move_id = fields.Many2one('account.move', string='Movimiento contable')
    z_code = fields.Char(string='Codigo')
    z_value_tax = fields.Float(string='Valor Impuesto')
    z_percent = fields.Float(string='Porcentaje')
    z_value_base = fields.Float(string='Valor Base')
    z_retention = fields.Boolean(string='Retención')


class zue_fe_detail(models.TransientModel):
    _name = 'zue.fe.detail'
    _description = 'Detalle de facturación electrónica ZUE'

    z_move_id = fields.Many2one('account.move', string='Movimiento contable')
    z_move_line_id = fields.Many2one('account.move.line', string='Detalle movimiento contable')
    z_quantity = fields.Float(string='Cantidad')
    z_value_base = fields.Float(string='Valor Base')
    z_tax_detail_ids = fields.One2many('zue.fe.detail.tax', 'z_detail_id', 'Impuestos Detalle')


class zue_fe_detail_tax(models.TransientModel):
    _name = 'zue.fe.detail.tax'
    _description = 'Impuestos del detalle de facturación electrónica ZUE'
    _order = "z_code asc"

    z_detail_id = fields.Many2one('zue.fe.detail', string='Movimiento contable FE')
    z_move_id = fields.Many2one('account.move', string='Movimiento contable')
    z_move_line_id = fields.Many2one('account.move.line', string='Detalle movimiento contable')
    z_code = fields.Char(string='Codigo')
    z_value_tax = fields.Float(string='Valor Impuesto')
    z_percent = fields.Float(string='Porcentaje')
    z_value_base = fields.Float(string='Valor Base')
    z_retention = fields.Boolean(string='Retención')
