# from odoo.exceptions import ValidationError, UserError
# from odoo import models, fields, api, _
# import base64
# from datetime import date
# import math
#
#
# class AccountMove(models.Model):
#     _inherit = 'account.move'
#
#     z_fe_encab = fields.One2many('zue.fe.encab', 'z_move_id', 'FE Encab')
#     z_fe_encab_tax = fields.One2many('zue.fe.encab.tax', 'z_move_id', 'FE Encab Impuesto')
#     z_fe_detail = fields.One2many('zue.fe.detail', 'z_move_id', 'FE Detalle')
#     z_fe_detail_tax = fields.One2many('zue.fe.detail.tax', 'z_move_id', 'FE Detalle Impuesto')
#
#     def get_xml_v2(self):
#         self.fill_fe_table()
#
#         xml = None
#         obj_xml = self.env['zue.xml.generator.header'].search([('code', '=', 'FacElectronica_' + self.env.company.zue_electronic_invoice_operator + 'v2')])
#         if len(obj_xml) == 0:
#             raise ValidationError(_("Error! No ha configurado un XML con el nombre 'FacElectronica_" + self.env.company.zue_electronic_invoice_operator + "v2'"))
#
#         xml = obj_xml.xml_generator(self)
#         xml = xml.decode("UTF-8").replace("<ITE/>", "").replace("<TII/>", "")
#
#         filename = f'FE_v2_{str(date.today().year)}_{self.name}_{str(self.partner_id.name)}.xml'
#
#         if self.xml_file_name:
#             attachment = self.env['ir.attachment'].search(
#                 [('res_model', '=', 'account.move'), ('name', '=', self.xml_file_name)])
#             attachment.unlink()
#
#         self.write({
#             'xml_file': base64.encodebytes(bytes(xml, 'UTF-8')),
#             'xml_file_name': filename,
#         })
#
#         data_attach = {'name': filename,
#                        'type': 'binary', 'datas': self.xml_file, 'res_name': filename, 'store_fname': filename,
#                        'res_model': 'account.move', 'res_id': self.id}
#
#         atts_id = self.env['ir.attachment'].create(data_attach)
#
#         self.message_post(body='XML generado correctamente.', attachment_ids=atts_id.ids)
#
#         return True
#
#
#     def fill_fe_table(self):
#         self.z_fe_encab.unlink()
#         self.z_fe_encab_tax.unlink()
#         self.z_fe_detail.unlink()
#         self.z_fe_detail_tax.unlink()
#
#         # Se llenan tablas para el encabezado
#         domain = ['&','&',('move_id', '=', self.id), ('name', '!=', self.name), ('balance', '!=', 0), ('price_subtotal', '!=', self.amount_total*-1)]
#         obj_lines = self.env['account.move.line'].search(domain, order='id')
#
#         total, totalret, base = 0, 0, 0
#         tax_lines_encab = []
#         line_detail = []
#         total_base = 0
#
#         for lines in obj_lines:
#             if lines.tax_base_amount:
#                 # obj_tax = self.env['account.tax'].search([('name', '=', lines.name), ('tax_type.not_iclude', '=', False)], limit=1)
#                 if not lines.tax_line_id.tax_type.not_iclude:
#                 # if obj_tax:
#                     if lines.tax_line_id.tax_type.is_aiu:
#                         total += abs(lines.balance)
#                         totalret += abs(lines.balance)
#                         base += abs(lines.balance)
#
#                         line_detail.append({'z_move_id': lines.move_id.id,
#                                             'z_move_line_id': lines.id,
#                                             'z_quantity': lines.quantity,
#                                             'z_value_base': abs(lines.balance)})
#                     else:
#                         totalret += abs(lines.balance)
#
#                         if not lines.tax_line_id.tax_type.retention:
#                             total += abs(lines.balance)
#
#                         tax_line_encab = {
#                             'z_move_id': self.id,
#                             'z_code': lines.tax_line_id.tax_type.code,
#                             'z_value_tax': abs(lines.balance),
#                             'z_percent': abs(lines.tax_line_id.amount),
#                             'z_value_base': abs(lines.tax_base_amount),
#                             'z_retention': lines.tax_line_id.tax_type.retention
#                         }
#                         tax_lines_encab.append(tax_line_encab)
#             else:
#                 if lines.name:
#                     if 'redondeo' not in lines.name:
#                         total += abs(lines.balance)
#                         totalret += abs(lines.balance)
#                         base += abs(lines.balance)
#
#                         if lines.product_id:
#                             total_base += lines.price_subtotal
#
#                         line_detail.append({'z_move_id': lines.move_id.id,
#                                             'z_move_line_id': lines.id,
#                                             'z_quantity': lines.quantity,
#                                             'z_value_base': abs(lines.balance)})
#                 else:
#                     line_detail.append({'z_move_id': lines.move_id.id,
#                                         'z_move_line_id': lines.id,
#                                         'z_quantity': lines.quantity,
#                                         'z_value_base': abs(lines.balance)})
#
#         # total_decimals = ""
#         # decimals = 0
#         #
#         # total_decimals = str(total).split('.')
#         # if len(total_decimals) > 1:
#         #     decimals = int(total_decimals[1])
#         #
#         #     if decimals <= 50:
#
#         # Se crea un nuevo item para redondear la factura
#         parte_decimal, parte_entera = math.modf(total)
#         redondeo_total = round(1 - round(parte_decimal, 2), 2)
#         if 0 < round(redondeo_total, 2) < 1:
#             line_detail.append({'z_move_id': lines.move_id.id,
#                                 'z_move_line_id': None,
#                                 'z_quantity': 1,
#                                 'z_value_base':  redondeo_total
#                                 })
#
#         encab = self.env['zue.fe.encab'].create({
#             'z_move_id': self.id,
#             'z_value_total': total + redondeo_total if redondeo_total < 1 else total,
#             'z_value_total_with_ret': totalret + redondeo_total if redondeo_total < 1 else totalret,
#             'z_value_base': base + redondeo_total if redondeo_total < 1 else base,
#             'z_currency_id': self.currency_id.id
#         })
#
#         tax_encab = self.env['zue.fe.encab.tax'].create(tax_lines_encab)
#         detail = self.env['zue.fe.detail'].create(line_detail)
#
#         list_dup = []
#         query = f'''
#                 select count(id) as count, price_subtotal, price_total
#                 from account_move_line A
#                 where move_id = %s
#                 group by move_name, "date", "ref", parent_state, journal_id, company_id, company_currency_id, account_id, account_root_id,
#                          "sequence", quantity, price_unit, discount, debit, credit, balance, amount_currency, price_subtotal, price_total,
#                          date_maturity, currency_id, partner_id, product_id, payment_id, tax_line_id, tax_base_amount, analytic_account_id
#                 having count(A.id) > 1
#                 ''' % self.id
#
#         self.env.cr.execute(query)
#         list_dup = self.env.cr.dictfetchall()
#
#         tax_lines_detail = []
#         for item in detail:
#             obj_move_lines = self.env['account.move.line'].search([('move_id', '=', item.z_move_id.id), ('tax_line_id', '!=', False), ('tax_base_amount', '=', item.z_value_base),
#                                                                    ('tax_line_id.tax_type.is_aiu', '=', False), ('tax_line_id.tax_type.not_iclude', '=', False)], order='amount_currency desc')
#
#             if not obj_move_lines:
#                 if list_dup:
#                     for row in list_dup:
#                         if item.z_value_base == row['price_subtotal']:
#                             obj_move_lines = self.env['account.move.line'].search(
#                                                 [('move_id', '=', item.z_move_id.id), ('tax_line_id', '!=', False),
#                                                  ('tax_base_amount', '=', item.z_value_base * row['count']),
#                                                  ('tax_line_id.tax_type.is_aiu', '=', False),
#                                                  ('tax_line_id.tax_type.not_iclude', '=', False)])
#
#                             for lines in sorted(obj_move_lines, key=lambda x: x.tax_line_id.tax_type.code):
#                                 tax_lines_detail.append({'z_detail_id': item.id,
#                                                          'z_move_id': item.z_move_id.id,
#                                                          'z_move_line_id': item.z_move_line_id.id,
#                                                          'z_code': lines.tax_line_id.tax_type.code,
#                                                          'z_value_tax': abs(lines.balance) / row['count'],
#                                                          'z_percent': abs(lines.tax_line_id.amount),
#                                                          'z_value_base': abs(lines.tax_base_amount) / row['count'],
#                                                          'z_retention': lines.tax_line_id.tax_type.retention
#                                                          })
#                 else:
#                     if total_base:
#                         obj_move_lines = self.env['account.move.line'].search([('move_id', '=', item.z_move_id.id), ('tax_line_id', '!=', False),('tax_base_amount', '=', total_base),
#                                                                                ('tax_line_id.tax_type.is_aiu', '=', False), ('tax_line_id.tax_type.not_iclude', '=', False)], order='amount_currency desc')
#
#                         for lines in sorted(obj_move_lines, key=lambda x: x.tax_line_id.tax_type.code):
#                             tax_lines_detail.append({'z_detail_id': item.id,
#                                                      'z_move_id': item.z_move_id.id,
#                                                      'z_move_line_id': item.z_move_line_id.id,
#                                                      'z_code': lines.tax_line_id.tax_type.code,
#                                                      'z_value_tax': abs(item.z_move_line_id.price_subtotal) * abs(lines.tax_line_id.amount) / 100,
#                                                      'z_percent': abs(lines.tax_line_id.amount),
#                                                      'z_value_base': abs(item.z_move_line_id.price_subtotal),
#                                                      'z_retention': lines.tax_line_id.tax_type.retention
#                                                      })
#
#             else:
#                 for lines in sorted(obj_move_lines, key=lambda x: x.tax_line_id.tax_type.code):
#                     tax_lines_detail.append({'z_detail_id': item.id,
#                                             'z_move_id': item.z_move_id.id,
#                                             'z_move_line_id': item.z_move_line_id.id,
#                                             'z_code': lines.tax_line_id.tax_type.code,
#                                             'z_value_tax': abs(lines.balance),
#                                             'z_percent': abs(lines.tax_line_id.amount),
#                                             'z_value_base': abs(lines.tax_base_amount),
#                                             'z_retention': lines.tax_line_id.tax_type.retention
#                                             })
#
#         detail_tax = self.env['zue.fe.detail.tax'].create(tax_lines_detail)
#
#         return True
#
#
# class zue_fe_encab(models.TransientModel):
#     _name = 'zue.fe.encab'
#     _description = 'Encabezado de facturación electrónica ZUE'
#
#     z_move_id = fields.Many2one('account.move', string='Movimiento contable')
#     z_value_total = fields.Float(string='Valor Total')
#     z_value_total_with_ret = fields.Float(string='Valor Total')
#     z_value_base = fields.Float(string='Valor Base')
#     z_currency_id = fields.Many2one('res.currency', string='Moneda')
#
# class zue_fe_encab_tax(models.TransientModel):
#     _name = 'zue.fe.encab.tax'
#     _description = 'Impuestos del encabezado de facturación electrónica ZUE'
#     _order = "z_code asc"
#
#     z_move_id = fields.Many2one('account.move', string='Movimiento contable')
#     z_code = fields.Char(string='Codigo')
#     z_value_tax = fields.Float(string='Valor Impuesto')
#     z_percent = fields.Float(string='Porcentaje')
#     z_value_base = fields.Float(string='Valor Base')
#     z_retention = fields.Boolean(string='Retención')
#
#
# class zue_fe_detail(models.TransientModel):
#     _name = 'zue.fe.detail'
#     _description = 'Detalle de facturación electrónica ZUE'
#
#     z_move_id = fields.Many2one('account.move', string='Movimiento contable')
#     z_move_line_id = fields.Many2one('account.move.line', string='Detalle movimiento contable')
#     z_quantity = fields.Float(string='Cantidad')
#     z_value_base = fields.Float(string='Valor Base')
#     z_tax_detail_ids = fields.One2many('zue.fe.detail.tax', 'z_detail_id', 'Impuestos Detalle')
#
#
# class zue_fe_detail_tax(models.TransientModel):
#     _name = 'zue.fe.detail.tax'
#     _description = 'Impuestos del detalle de facturación electrónica ZUE'
#     _order = "z_code asc"
#
#     z_detail_id = fields.Many2one('zue.fe.detail', string='Movimiento contable')
#     z_move_id = fields.Many2one('account.move', string='Movimiento contable')
#     z_move_line_id = fields.Many2one('account.move.line', string='Detalle movimiento contable')
#     z_code = fields.Char(string='Codigo')
#     z_value_tax = fields.Float(string='Valor Impuesto')
#     z_percent = fields.Float(string='Porcentaje')
#     z_value_base = fields.Float(string='Valor Base')
#     z_retention = fields.Boolean(string='Retención')