from odoo.exceptions import ValidationError, UserError
from odoo import models, fields, api, _
import base64
from datetime import date
import json
import time
import xml.etree.ElementTree as ET
from datetime import timedelta
import os
import zipfile
import re
import zlib
from io import BytesIO
from datetime import datetime, timedelta

#MOVIMIENTO CONTABLE ENCABEZADO
class account_move(models.Model):
    _inherit = 'account.move'

    description_code_credit = fields.Selection([('1', 'Devolución parcial de los bienes y/o no aceptación parcial del servicio'),
                                                ('2', 'Anulación de factura electrónica'),
                                                ('3', 'Rebaja o descuento parcial o total'),
                                                ('4', 'Ajuste de precio'),
                                                ('6', 'Descuento comercial por pronto pago'),
                                                ('7', 'Descuento comercial por volumen de ventas'),
                                                ('8', 'Refacturación'),
                                                ('5', 'Otros')], string='Concepto nota crédito')
    description_code_debit = fields.Selection([('1', 'Intereses'),
                                               ('2', 'Gastos por cobrar'),
                                               ('3', 'Cambio de valor'),
                                               ('4', 'Otros')], string='Concepto nota débito')
    xml_file = fields.Binary('XML')
    xml_file_name = fields.Char('XML name')
    json_file = fields.Binary('JSON')
    json_file_name = fields.Char('JSON name')
    fe_pdf_file = fields.Binary('PDF')
    fe_pdf_name = fields.Char('PDF name')
    cufe_cude_ref = fields.Char('CUFE/CUDE')
    fe_status = fields.Selection([('draft', 'No procesado'), ('processed', 'Procesando'), ('accepted', 'Aceptado'), ('rejected', 'Rechazado'), ('other', 'Otro')], string='Estado de Factura Electrónica', default='draft')
    fe_status_info = fields.Char('Detalle del estado')
    fe_msg_result = fields.Char('Resultado de envío Factura Electrónica', tracking=True, store=True)
    fe_transaction_id = fields.Char('Id transacción de Factura Electrónica')
    fe_payment_option_id = fields.Many2one('fe.payment.options', string="Método de pago",
                                           default=lambda self: self.env.ref('fe_payment_options_1', raise_if_not_found=False))
    fe_sent_date = fields.Datetime('Fecha de Emisión')
    x_fe_sent = fields.Boolean(string='Factura Electrónica Enviada', default=False)
    z_purchase_order = fields.Char('Órden de Compra')
    z_alert_generated = fields.Boolean(string='Alerta generada')
    z_dian_alert_type = fields.Selection([("none", "No alert"),
                                          ("date", "Date alert"),
                                          ("folios", "Folios alert"),
                                          ("both", "Date and folios alert")], compute="_compute_z_dian_alert_type")

    def _get_fe_attachment_domain(self, filename):
        self.ensure_one()
        return [
            ('res_model', '=', 'account.move'),
            ('res_id', '=', self.id),
            ('name', '=', filename),
        ]

    def _get_ftech_document_number(self):
        self.ensure_one()
        document = (self.journal_id.code or '').strip()
        if not document:
            raise ValidationError(_('No se encontró el prefijo del diario para consultar el documento en FacturaTech.'))

        move_name = (self.name or '').strip()
        number = move_name
        if move_name.startswith(document):
            number = move_name[len(document):].strip()

        number = number.lstrip('/- _')
        match = re.search(r'(\d+)$', number or move_name)
        if match:
            number = match.group(1)
        elif self.sequence_number:
            number = str(self.sequence_number)

        if not number:
            raise ValidationError(_('No fue posible determinar el folio para consultar el documento en FacturaTech.'))

        return document, number

    def _acquire_ftech_lock(self, scope):
        self.ensure_one()
        lock_seed = f'zue_ftech:{scope}:{self.company_id.id}:{self.journal_id.id}:{self.journal_id.code or ""}'
        lock_key = zlib.crc32(lock_seed.encode('utf-8'))
        if lock_key > 2147483647:
            lock_key -= 4294967296
        self.env.cr.execute("SELECT pg_advisory_lock(%s)", (lock_key,))
        return lock_key

    def _release_ftech_lock(self, lock_key):
        self.env.cr.execute("SELECT pg_advisory_unlock(%s)", (lock_key,))

    @api.model_create_multi
    def create(self, values_list):
        for vals in values_list:
            vals['xml_file'] = ''
            vals['xml_file_name'] = ''
            vals['json_file'] = ''
            vals['json_file_name'] = ''
            vals['fe_pdf_file'] = ''
            vals['fe_pdf_name'] = ''
            vals['cufe_cude_ref'] = ''
            vals['fe_status'] = 'draft'
            vals['fe_status_info'] = ''
            vals['fe_msg_result'] = ''
            vals['fe_transaction_id'] = ''
            vals['x_fe_sent'] = ''

            amount_total = 1

            if 'tax_totals_json' in vals:
                if vals['tax_totals_json']:
                    if 'amount_total' in json.loads(vals['tax_totals_json']):
                        amount_total = json.loads(vals['tax_totals_json'])['amount_total']

            if 'line_ids' in vals:
                if len(vals['line_ids']) <= 0:
                    if amount_total == 0:
                        raise ValidationError(_('El valor total de la factura no puede ser 0. Por favor verifique!'))

        return super(account_move, self).create(values_list)

    @api.depends("z_alert_generated", "journal_id", "journal_id.z_generate_alert", "journal_id.dian_authorization_end_date", "journal_id.z_expiration_days", "journal_id.dian_max_range_number", "journal_id.z_expiration_folios")
    def _compute_z_dian_alert_type(self):
        for move in self:
            if move.fe_status != 'draft':
                move.z_dian_alert_type = "none"
            else:
                alert_date = False
                alert_folios = False

                if not move.z_alert_generated and move.journal_id.z_generate_alert:
                    end_date = move.journal_id.dian_authorization_end_date
                    if end_date and abs((fields.Date.today() - end_date).days) <= move.journal_id.z_expiration_days:
                        alert_date = True

                    max_sequence = self.env["account.move"].search([("journal_id", "=", move.journal_id.id), ("sequence_number", "!=", 0)], order="sequence_number desc", limit=1).sequence_number or 0

                    if (move.journal_id.dian_max_range_number - max_sequence) <= move.journal_id.z_expiration_folios:
                        alert_folios = True

                if alert_date and alert_folios:
                    move.z_dian_alert_type = "both"
                elif alert_date:
                    move.z_dian_alert_type = "date"
                elif alert_folios:
                    move.z_dian_alert_type = "folios"
                else:
                    move.z_dian_alert_type = "none"

    # Se comenta debido a que cuando falla alguna factura, se hace rollback del POST pero no se puede hacer rollback del envío a FE
    # def _post(self, soft=True):
    #     to_return = super(account_move, self)._post(soft)
    #
    #     for record in self:
    #         if record.state == 'posted':
    #             if record.move_type in ['out_refund', 'in_refund', 'out_invoice']:
    #                 record.send_all_process()
    #
    #     return to_return

    def masive_send_fe(self):
        if self.env.company.zue_electronic_invoice_disable_sending:
            return True

        for record in self.filtered(lambda x: x.state == 'posted' and x.fe_status == 'draft' and x.x_fe_sent == False and
                                              x.move_type in ['out_refund', 'out_invoice']):
            if record.state == 'posted':
                if record.move_type in ['out_refund', 'out_invoice']:
                    if record.fe_status != 'rejected':
                        record.send_all_process()

    def download_massive_pdf_file_fe(self):
        zip_buffer = BytesIO()
        filename = 'Facturas_PDFs_FE_masiva.zip'
        self.env['ir.attachment'].search([('res_model', '=', False), ('name', '=', filename)]).unlink()
        for record in self:
            obj_attachment = self.env['ir.attachment'].search(record._get_fe_attachment_domain('FE_' + record.name), limit=1)
            if len(obj_attachment) == 0:
                record.download_pdf_file_FE()
                obj_attachment = self.env['ir.attachment'].search(record._get_fe_attachment_domain('FE_' + record.name), limit=1)

            # Crea un archivo zip en memoria
            if len(obj_attachment) == 1:
                with zipfile.ZipFile(zip_buffer, 'a') as zip_file:
                    # Lee el contenido del adjunto
                    attachment_content = base64.b64decode(obj_attachment.datas)
                    # Agrega el archivo al zip
                    zip_file.writestr(obj_attachment.name+'.pdf', attachment_content)
        # Vuelve al principio del buffer
        zip_buffer.seek(0)
        # Devuelve el contenido del buffer
        zip_content = zip_buffer.read()

        # Crea un nuevo registro de archivo adjunto para el zip
        zip_attachment_vals = {
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(zip_content),
            'store_fname': filename,
        }

        zip_attachment = self.env['ir.attachment'].create(zip_attachment_vals)

        # Devuelve una acción para abrir el archivo zip
        return {
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=ir.attachment&id=" + str(zip_attachment.id) + "&filename_field=name&field=datas&download=true&name="+filename,
            'target': 'self'
        }

    # def action_post(self):
    #     if not self.z_alert_generated:
    #          if self.journal_id.z_generate_alert:
    #             yes_no = ""
    #
    #             if abs((date.today() - self.journal_id.dian_authorization_end_date).days) <= self.journal_id.z_expiration_days:
    #                 yes_no += "¡Su resolución de facturación DIAN esta próximo a vencer (Fecha por cumplirse)!. "
    #
    #             max_sequence = self.env['account.move'].search([('journal_id', '=', self.journal_id.id), ('sequence_number', '!=', 0)],
    #                                                                order='sequence_number desc', limit=1).sequence_number
    #
    #             if (self.journal_id.dian_max_range_number - max_sequence) <= self.journal_id.z_expiration_folios:
    #                 yes_no += "¡Su resolución de facturación DIAN esta próximo a vencer! (Folio por cumplirse). "
    #
    #             if yes_no:
    #                 return {
    #                     'name': 'Deseas continuar?',
    #                     'type': 'ir.actions.act_window',
    #                     'res_model': 'zue.confirm.wizard',
    #                     'view_mode': 'form',
    #                     'target': 'new',
    #                     'context': {'default_account_move_alert_id': self.id,
    #                                 'default_yes_no': yes_no}
    #                 }
    #
    #     return super(account_move, self).action_post()

    # def _post(self, soft=False):
    #     to_return = super(account_move, self)._post(soft=False)
    #
    #     if self.env.company.zue_electronic_invoice_disable_sending:
    #         return to_return
    #
    #     for record in to_return:
    #         if record.state == 'posted':
    #             if record.move_type in ['out_refund', 'out_invoice']:
    #                 if record.fe_status != 'rejected':
    #                     record.send_all_process()
    #
    #     return to_return

    def get_invoice_line_ids(self, aiu=0, line_ids=[]):
        to_return = []
        if aiu:
            taxes_aiu = self.env['account.tax'].search([('name', 'ilike', 'AIU')]).filtered(lambda x: x.name.startswith('AIU')).ids
            to_return = self.env['account.move.line'].search(['&', ('id', 'in', line_ids.ids), ('tax_ids.id', 'in', taxes_aiu)])
        else:
            to_return = self.invoice_line_ids.filtered(lambda x: x.price_subtotal > 0 or x.discount == 100)

        return to_return


    def get_xml(self, support_document=False, return_xml=False):
        xml = None

        if support_document:
            obj_xml = self.env['zue.xml.generator.header'].search([('code','=','DocSopElectronico_Carvajal')])
        else:
            obj_xml = self.env['zue.xml.generator.header'].search([('code', '=', 'FacElectronica_' + self.env.company.zue_electronic_invoice_operator)])
            if not obj_xml:
                obj_xml = self.env['zue.xml.generator.header'].search([('code', '=', 'FacElectronica_' + self.env.company.zue_electronic_invoice_operator + 'v2')])
            if len(obj_xml) == 0:
                raise ValidationError(
                    _("Error! No ha configurado un XML con el nombre 'FacElectronica_" + self.env.company.zue_electronic_invoice_operator + "'"))

        self.fill_fe_table()
        xml = obj_xml.xml_generator(self)
        xml = xml.decode("UTF-8").replace("<ITE/>", "").replace("<TII/>", "").replace("<cfc", "<cfc:").replace("</cfc", "</cfc:").replace("<dte", "<dte:").replace("</dte", "</dte:").replace("<cno", "<cno:").replace("</cno", "</cno:").replace("<cex", "<cex:").replace("</cex", "</cex:")

        if support_document:
            filename = f'DS_{str(date.today().year)}_{self.name}_{str(self.partner_id.name)}.xml'
        else:
            filename = f'FE_{str(date.today().year)}_{self.name}_{str(self.partner_id.name)}.xml'

        self.write({
            'xml_file': base64.encodebytes(bytes(xml, 'UTF-8')),
            'xml_file_name': filename,
        })

        obj_attachment = self.env['ir.attachment'].search(self._get_fe_attachment_domain(filename), limit=1)
        if obj_attachment:
            obj_attachment.write({'datas': self.xml_file})
        else:
            data_attach = {'name': filename,
                           'type': 'binary', 'datas': self.xml_file, 'res_name': filename, 'store_fname': filename,
                           'res_model': 'account.move', 'res_id': self.id}

            atts_id = self.env['ir.attachment'].create(data_attach)

            self.message_post(body='XML generado correctamente.', attachment_ids=atts_id.ids)

        if return_xml:
            return xml
        else:
            return True

    def get_json(self, support_document=False, return_json=False):
        """Genera el archivo JSON para facturación electrónica"""
        json_data = None

        # Buscar generador JSON similar al XML
        if support_document:
            obj_json = self.env['zue.json.generator.header'].search([('code', '=', 'DocSopElectronico_JSON')], limit=1)
        else:
            obj_json = self.env['zue.json.generator.header'].search([('code', '=', 'FacElectronica_' + self.env.company.zue_electronic_invoice_operator + '_JSON')], limit=1)
            if not obj_json:
                obj_json = self.env['zue.json.generator.header'].search([('code', '=', 'FacElectronica_' + self.env.company.zue_electronic_invoice_operator + 'v2_JSON')], limit=1)

        self.fill_fe_table()

        if obj_json:
            # Si existe un generador JSON configurado, usarlo
            json_data = obj_json.json_generator(self)
            if isinstance(json_data, bytes):
                json_data = json_data.decode("UTF-8")
        else:
            # Generar JSON básico con la estructura de la factura
            json_data = self._generate_basic_json()

        if support_document:
            filename = f'DS_{str(date.today().year)}_{self.name}_{str(self.partner_id.name)}.json'
        else:
            filename = f'FE_{str(date.today().year)}_{self.name}_{str(self.partner_id.name)}.json'

        self.write({
            'json_file': base64.encodebytes(bytes(json_data, 'UTF-8')),
            'json_file_name': filename,
        })

        obj_attachment = self.env['ir.attachment'].search([('name', '=', filename)])
        if obj_attachment:
            obj_attachment.unlink()

        data_attach = {'name': filename,
                       'type': 'binary', 'datas': self.json_file, 'res_name': filename, 'store_fname': filename,
                       'res_model': 'account.move', 'res_id': self.id}

        atts_id = self.env['ir.attachment'].create(data_attach)

        self.message_post(body='JSON generado correctamente.', attachment_ids=atts_id.ids)

        if return_json:
            return json_data
        else:
            return True

    def _generate_basic_json(self):
        """Genera un JSON básico con la estructura de la factura electrónica"""
        import json as json_lib
        
        # Estructura básica del JSON para factura electrónica
        json_structure = {
            'invoice': {
                'number': self.name or '',
                'date': self.invoice_date.strftime('%Y-%m-%d') if self.invoice_date else '',
                'partner': {
                    'vat': self.partner_id.vat or '',
                    'name': self.partner_id.name or '',
                },
                'company': {
                    'vat': self.company_id.partner_id.vat or '',
                    'name': self.company_id.name or '',
                },
                'amount_total': self.amount_total,
                'amount_untaxed': self.amount_untaxed,
                'amount_tax': self.amount_tax,
                'currency': self.currency_id.name if self.currency_id else 'COP',
                'lines': []
            }
        }

        # Agregar líneas de la factura
        for line in self.invoice_line_ids:
            line_data = {
                'product': line.product_id.name if line.product_id else line.name,
                'quantity': line.quantity,
                'price_unit': line.price_unit,
                'discount': line.discount,
                'price_subtotal': line.price_subtotal,
                'taxes': []
            }
            
            # Agregar impuestos de la línea
            for tax in line.tax_ids:
                line_data['taxes'].append({
                    'name': tax.name,
                    'amount': tax.amount,
                })
            
            json_structure['invoice']['lines'].append(line_data)

        # Agregar impuestos del encabezado si existen
        if self.z_fe_encab_tax:
            json_structure['invoice']['header_taxes'] = []
            for tax in self.z_fe_encab_tax:
                json_structure['invoice']['header_taxes'].append({
                    'code': tax.z_code,
                    'percent': tax.z_percent,
                    'value': tax.z_value_tax,
                    'base': tax.z_value_base,
                    'retention': tax.z_retention,
                })

        return json_lib.dumps(json_structure, indent=2, ensure_ascii=False)

    def get_Fiscal_Value_TCR_TAC(self, partner_id):
        obj_partner = self.env['res.partner'].search([('id', '=', partner_id)])
        fiscal_value = ''

        for obj in obj_partner.x_tax_responsibilities.filtered(lambda x: x.valid_for_fe == True):
            if fiscal_value != '':
                fiscal_value += ','

            fiscal_value += str(obj.code)

        return fiscal_value

    def get_impuestos_TIM(self, line_ids=None):
        impuestos = []
        line_tax = {}
        if line_ids:
            for invoice in line_ids:
                for tax in invoice.tax_ids:
                    # if tax.amount < 0:
                    #    continue

                    if line_tax.get(str(tax.amount), 0) == 0:
                        line_tax.update({
                            str(tax.amount): abs(tax.amount * invoice.price_subtotal / 100),
                        })
                    else:
                        line_tax[str(tax.amount)] = abs(
                            line_tax.get(str(tax.amount), 0) + (tax.amount * invoice.price_subtotal / 100))

            for key, value in line_tax.items():
                temp = [key, value]
                impuestos.append(temp)
        else:
            for invoice in self.invoice_line_ids:
                for tax in invoice.tax_ids:
                    if "AIU" in tax.name:
                        continue

                    if line_tax.get(str(tax.amount), 0) == 0:
                        line_tax.update({
                            str(tax.amount): abs(tax.amount * invoice.price_subtotal / 100),
                        })
                    else:
                        line_tax[str(tax.amount)] = abs(line_tax.get(str(tax.amount), 0) + (tax.amount * invoice.price_subtotal / 100))

            for key, value in line_tax.items():
                temp = [key, value]
                impuestos.append(temp)

        return impuestos

    def get_tax_type(self, percent, get_code):
        return_value = ''
        tmp_percent = float(percent)
        obj_tax = self.env['account.tax'].search([('amount', '=', tmp_percent), ('tax_type', '!=', None), ('company_id', 'in', self.env.user.company_ids.ids)], limit=1)

        if get_code:
            return_value = obj_tax.tax_type.code
        else:
            return_value = obj_tax.tax_type.retention

        return return_value

    def get_TDC_1(self, invoice_line_ids, line_ids):
        return_value = ''
        no_cop_total = 0
        cop_total = 0

        for invoice in invoice_line_ids:
            no_cop_total += invoice.price_subtotal

        for line in line_ids:
            cop_total += line.credit

        return_value = cop_total / no_cop_total

        return return_value

    def get_TAC_TCR(self, tag):
        to_return = ''

        if tag == 'TAC':
            for obj in self.company_id.partner_id.x_tax_responsibilities.filtered(lambda x: x.valid_for_fe == True):
                if to_return:
                    to_return = to_return + ',' + obj.code
                else:
                    to_return = obj.code
        elif tag == 'TCR':
            for obj in self.partner_id.x_tax_responsibilities.filtered(lambda x: x.valid_for_fe == True):
                if to_return:
                    to_return = to_return + ',' + obj.code
                else:
                    to_return = obj.code
        else:
            to_return = 'R-99-PN'

        if to_return == '':
            to_return = 'R-99-PN'

        return to_return

    def get_info_ref_Factura(self, field_name):
        to_return = ''
        obj_factura = None
        ldict = {'o':self}

        try:
            if self.journal_id.z_is_debit_note:
                if self.ref:
                    invoice_name = self.ref[:self.ref.find(',')]
                else:
                    return 'Referencia No encontrada'
            else:
                if self.ref:
                    invoice_name = self.ref[
                                   14: 50 if self.ref[14:].find(' ') == -1 else self.ref[14:].find(' ') if self.ref.find(
                                   ',') == -1 else self.ref.find(',')]
                else:
                    return 'Referencia No encontrada'

            to_execute = f'''obj_factura = o.env["account.move"].sudo().search([("name", "=", "{invoice_name.strip()}")], limit=1).{field_name}'''
            exec(to_execute,ldict)

            result = ldict.get('obj_factura')

            to_return = str(result)
        except Exception as e:
            raise UserError(_('Error %s') % e)

        return to_return

    def get_pricelist_id(self):
        to_return = ''
        obj_factura = None
        ldict = {'o': self}
        val = 'DESCUENTO POR PRONTO PAGO: '

        try:
            query = """
                SELECT so.pricelist_id, am.name
                FROM sale_order so
                JOIN sale_order_line sol ON sol.order_id = so.id
                JOIN sale_order_line_invoice_rel soli_rel ON soli_rel.order_line_id = sol.id
                JOIN account_move_line aml ON aml.id = soli_rel.invoice_line_id
                JOIN account_move am ON am.id = aml.move_id AND am.id = %s
                ORDER BY am.id DESC
                LIMIT 1
            """
            self.env.cr.execute(query, (self.id,))
            res = self.env.cr.fetchone()

            pricelist_id = res[0] if res and res[0] else None
            if not pricelist_id and 'z_sale_pricelist_id' in self._fields:
                pl = self.z_sale_pricelist_id
                pricelist_id = pl.id if pl else None

            if not pricelist_id:
                return ''

            obj_payment_condition = self.env['zue.prompt.payment.discount.condition'].search([('z_product_pricelist', '=', pricelist_id)], order='z_invoice_days asc')

            if obj_payment_condition:
                for condition in obj_payment_condition:
                    fecha = str(self.invoice_date + timedelta(days=condition.z_invoice_days))
                    valor = (self.amount_total - (self.amount_untaxed * condition.z_discount_percent / 100))
                    ahorro = (self.amount_untaxed * condition.z_discount_percent / 100)

                    formatted_valor = '{:,.2f}'.format(valor)
                    formatted_valor = formatted_valor.replace('.', '*').replace(',', '.').replace('*', ',')

                    formatted_ahorro = '{:,.2f}'.format(ahorro)
                    formatted_ahorro = formatted_ahorro.replace('.', '*').replace(',', '.').replace('*', ',')

                    val += 'Si paga antes de: ' + fecha + ', Pague: $' + formatted_valor + ', Ahorre: $' + formatted_ahorro + '  /  '
            else:
                val = ''

            to_return = val
        except Exception as e:
            raise UserError(_('Error %s') % e)

        return to_return

    def get_pickings_fe(self):
        for record in self:
            obj_sale = self.env['sale.order'].search([('invoice_ids','in',[record.id])],limit=1)
            obj_picking = self.env['stock.picking'].search([('origin','=',obj_sale.name),('name','ilike','PICK')])
            return obj_picking

    def get_order_fe(self):
        for record in self:
            obj_sale = self.env['sale.order'].search([('invoice_ids','in',[record.id])],limit=1)
            return obj_sale

    def send_xml_FE(self):
        """Envía el archivo XML o JSON según la configuración"""
        # Determinar formato según configuración
        invoice_format = self.env.company.zue_electronic_invoice_format or 'xml'
        
        if invoice_format == 'json':
            base64_file = self.json_file
            file_type = 'JSON'
        else:
            base64_file = self.xml_file
            file_type = 'XML'
        
        if not base64_file:
            raise UserError(_('No se ha generado el archivo %s a enviar para la facturación electrónica. Por favor verifique!') % file_type)
        else:
            base64_file = base64_file.decode("UTF-8")

        user = self.company_id.zue_electronic_invoice_username
        password = self.company_id.zue_electronic_invoice_password

        if self.pos_order_ids:
            obj_ws = self.env['zue.request.ws'].search([('name', '=', 'uploadDocumentpos')])
        else:
            obj_ws = self.env['zue.request.ws'].search([('name', '=', 'upload_file_fe')])

        if not obj_ws:
            raise ValidationError(_("Error! No ha configurado un web service con el nombre 'upload_file_fe'"))

        # time.sleep(1)
        obj_result = obj_ws.connection_requests(user, password, base64_file)
        # time.sleep(1)

        result = self.return_result_FE(obj_result, 'SEND_FE')

        if result:
            return result
        else:
            if self.fe_status:
                return self.fe_status
            else:
                return ''

    def check_status_FE(self, user='', password=''):
        tmp_transaction_id = self.fe_transaction_id
        if not tmp_transaction_id:
            # raise UserError(_('No se ha realizado el envío de la factura. Por favor verifique!'))
            return 'No se ha realizado el envío de la factura. Por favor verifique!'

        if not user:
            user = self.company_id.zue_electronic_invoice_username
            password = self.company_id.zue_electronic_invoice_password

        if self.pos_order_ids:
            obj_ws = self.env['zue.request.ws'].search([('name', '=', 'documentStatuspos')])
        else:
            obj_ws = self.env['zue.request.ws'].search([('name', '=', 'check_status_fe')])
        if not obj_ws:
            raise ValidationError(_("Error! No ha configurado un web service con el nombre 'check_status_fe'"))

        obj_result = obj_ws.connection_requests(user, password, tmp_transaction_id)

        result = self.return_result_FE(obj_result, 'CHECK_FE')

        return result

    def download_pdf_file_FE(self, user='', password=''):
        self.ensure_one()
        lock_key = self._acquire_ftech_lock('download_pdf')
        try:
            if self.env['ir.attachment'].search(self._get_fe_attachment_domain('FE_' + self.name), limit=1):
                return True

            tmp_transaction_id = self.fe_transaction_id
            if not tmp_transaction_id:
                raise UserError(_('No se ha realizado el envío de la factura. Por favor verifique!'))

            if not user:
                user = self.company_id.zue_electronic_invoice_username
                password = self.company_id.zue_electronic_invoice_password

            if self.pos_order_ids:
                obj_ws = self.env['zue.request.ws'].search([('name', '=', 'documentpdfpos')])
            else:
                obj_ws = self.env['zue.request.ws'].search([('name', '=', 'download_pdf_fe')])
            if not obj_ws:
                raise ValidationError(_("Error! No ha configurado un web service con el nombre 'download_pdf_fe'"))

            document, number = self._get_ftech_document_number()

            obj_result = obj_ws.connection_requests(user, password, document, number)

            self.return_result_FE(obj_result, 'GET_PDF')
        finally:
            self._release_ftech_lock(lock_key)

    def get_cufe_FE(self, user='', password=''):
        if self.cufe_cude_ref:
            return True

        tmp_transaction_id = self.fe_transaction_id
        if not tmp_transaction_id:
            raise UserError(_('No se ha realizado el envío de la factura. Por favor verifique!'))

        if not user:
            user = self.company_id.zue_electronic_invoice_username
            password = self.company_id.zue_electronic_invoice_password

        if self.pos_order_ids:
            obj_ws = self.env['zue.request.ws'].search([('name', '=', 'documentcufepos')])
        else:
            obj_ws = self.env['zue.request.ws'].search([('name', '=', 'get_cufe_fe')])
        if not obj_ws:
            raise ValidationError(_("Error! No ha configurado un web service con el nombre 'get_cufe_fe'"))

        document, number = self._get_ftech_document_number()

        obj_result = obj_ws.connection_requests(user, password, document, number)

        self.return_result_FE(obj_result, 'GET_CUFE')

        return True

    def send_all_process(self):
        self.ensure_one()
        result = ''
        send_result = ''

        if self.env.company.zue_electronic_invoice_disable_sending:
            return True

        if self.journal_id.z_disable_dian_sending:
            return True

        # Determinar formato según configuración
        invoice_format = self.env.company.zue_electronic_invoice_format or 'xml'

        if self.fe_status == 'draft':
            # Eliminar archivo anterior según formato
            if invoice_format == 'json':
                if self.json_file_name:
                    attachment = self.env['ir.attachment'].search([('res_model', '=', 'account.move'), ('name', '=', self.json_file_name)])
                    attachment.unlink()
                self.get_json()
            else:
                if self.xml_file_name:
                    attachment = self.env['ir.attachment'].search(self._get_fe_attachment_domain(self.xml_file_name))
                    attachment.unlink()
            self.get_xml_v2()

            send_result = self.send_xml_FE()
            self.message_post(body=_("Se envió la factura electrónica a la DIAN. Resultado: %s") % (send_result or 'N/A'))
            if send_result in ('draft', 'accepted', 'processed', 'rejected', 'other'):
                result = self.check_status_FE()

            if result == 'accepted':
                self.get_cufe_FE()
                self.download_pdf_file_FE()
            else:
                if result != 'fail':
                    self.send_xml_FE()
                    self.message_post(body=_("Se reenvió la factura electrónica a la DIAN. Resultado: %s") % (send_result or 'N/A'))
                    result = self.check_status_FE()
                    if result == 'accepted':
                        self.get_cufe_FE()
                        self.download_pdf_file_FE()
        elif self.fe_status == 'processed':
            result = self.check_status_FE()
            if result == 'accepted':
                self.get_cufe_FE()
                self.download_pdf_file_FE()
        elif self.fe_status == 'other' or self.fe_status == 'rejected':
            # Eliminar archivo anterior según formato
            if invoice_format == 'json':
                if self.json_file_name:
                    attachment = self.env['ir.attachment'].search([('res_model', '=', 'account.move'), ('name', '=', self.json_file_name)])
                    attachment.unlink()
                self.get_json()
            else:
                if self.xml_file_name:
                    attachment = self.env['ir.attachment'].search(self._get_fe_attachment_domain(self.xml_file_name))
                    attachment.unlink()
            self.get_xml_v2()
            self.send_xml_FE()
            result = self.check_status_FE()
            if result == 'accepted':
                self.get_cufe_FE()
                self.download_pdf_file_FE()
        elif self.fe_status == 'accepted':
            self.download_pdf_file_FE()

        if self.fe_status == 'accepted' and not self.x_fe_sent:
            self.x_fe_sent = True
            # current_datetime_utc = datetime.now(pytz.utc)
            # current_datetime_utc = current_datetime_utc.replace(second=0, microsecond=0)
            #
            # timezone_str = '-05:00' #Colombia
            # timezone_hours = int(timezone_str[:-3])
            # timezone_minutes = int(timezone_str[-2:])
            #
            # timezone_delta = timedelta(hours=timezone_hours, minutes=timezone_minutes)
            # hours_utc = current_datetime_utc + timezone_delta
            # formatted_datetime = hours_utc.strftime('%Y-%m-%d %H:%M:%S')
            # act_datetime = datetime.strptime(formatted_datetime, '%Y-%m-%d %H:%M:%S')

            self.fe_sent_date = datetime.now()
            self.fe_msg_result = 'Documento Aceptado!'

    def return_result_FE(self, obj_result, method):
        code_position = -1
        error_msg, tmp_transaction_id, resource, state, cufe = '', '', '', '', ''
        status_code, error_position, transaction_position, resource_position, state_position, cufe_position = 0, 0, 0, 0, 0, 0

        code_position = obj_result.find('</code>') - 3

        if code_position > -1:
            status_code = int(obj_result[code_position:code_position + 3])

            if status_code >= 400:
                error_position = obj_result.find('<error xsi:type="xsd:string">') + len('<error xsi:type="xsd:string">')
                error_msg = obj_result[error_position:obj_result.find('</error>')]

                if method in ('SEND_FE','CHECK_FE'):
                    self.write({'fe_status': 'rejected',
                                'fe_msg_result': error_msg})
                elif method == 'GET_PDF':
                    self.write({'fe_msg_result': "Error al obtener el PDF: " + error_msg})

                return error_msg

            if status_code in (200, 201, 202, 203):
                error_position = obj_result.find('<success xsi:type="xsd:string">') + len('<success xsi:type="xsd:string">')
                error_msg = obj_result[error_position:obj_result.find('</success>')]

                self.write({'fe_msg_result': error_msg})

                if method == 'CHECK_FE':
                    state_position = obj_result.find('<status xsi:type="xsd:string">') + len('<status xsi:type="xsd:string">')
                    state = obj_result[state_position:obj_result.find('</status>')]

                    if state == 'SIGNED_XML':
                        self.write({'fe_status': 'accepted'})
                        return 'accepted'
                    elif state == 'PROCESSING':
                        self.write({'fe_status': 'processed'})
                        return 'processed'
                    else:
                        self.write({'fe_status': 'other',
                                    'fe_status_info': state})
                        return 'other'

                if method == 'SEND_FE':
                    transaction_position = obj_result.find('<transaccionID xsi:type="xsd:string">') + len('<transaccionID xsi:type="xsd:string">')
                    tmp_transaction_id = obj_result[transaction_position:obj_result.find('</transaccionID>')]

                    self.write({'fe_transaction_id': tmp_transaction_id})
                    return 'fail'

                if method == 'GET_PDF':
                    error_position = obj_result.find('<resourceData xsi:type="xsd:string">') + len('<resourceData xsi:type="xsd:string">')
                    error_msg = obj_result[error_position:obj_result.find('</resourceData>')]

                    if error_msg:
                        self.write({#'fe_pdf_file': error_msg,
                                    'fe_pdf_name': 'FE_' + self.name})

                        attachment_name = 'FE_' + self.name
                        attachment_vals = {
                            'name': attachment_name,
                            'type': 'binary',
                            'datas': error_msg,
                            'res_model': 'account.move',
                            'res_id': self.id
                        }
                        attachment = self.env['ir.attachment'].search(
                            self._get_fe_attachment_domain(attachment_name), limit=1
                        )
                        if attachment:
                            attachment.write({'datas': error_msg})
                        else:
                            self.env['ir.attachment'].create(attachment_vals)

                        if self.fe_status == 'accepted':
                            self.write({'x_fe_sent': True})

                if method == 'GET_CUFE':
                    cufe_position = obj_result.find('<resourceData xsi:type="xsd:string">') + len('<resourceData xsi:type="xsd:string">')
                    cufe = obj_result[cufe_position:obj_result.find('</resourceData>')]

                    if cufe:
                        self.write({'cufe_cude_ref': cufe})

        return True


class fe_payment_options(models.Model):
    _name = 'fe.payment.options'
    _description = 'Métodos de pago para la facturación electrónica'

    code = fields.Char(string="Código")
    name = fields.Char(string="Nombre")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_email_fe = fields.Char('Email facturación electrónica')


# class zue_confirm_wizard(models.TransientModel):
#     _inherit = 'zue.confirm.wizard'
#
#     account_move_alert_id = fields.Many2one('account.move', string='Id Movimiento')
