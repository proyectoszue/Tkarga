from odoo.exceptions import ValidationError, UserError
from odoo import models, fields, api, _
import base64
from datetime import date
import json
import time
import xml.etree.ElementTree as ET

#MOVIMIENTO CONTABLE ENCABEZADO
class account_move(models.Model):
    _inherit = 'account.move'

    description_code_credit = fields.Selection([('1', 'Devolución parcial de los bienes y/o no aceptación parcial del servicio'),
                                                ('2', 'Anulación de factura electrónica'),
                                                ('3', 'Rebaja o descuento parcial o total'),
                                                ('4', 'Ajuste de precio'),
                                                ('5', 'Otros')], string='Concepto nota crédito')
    description_code_debit = fields.Selection([('1', 'Intereses'),
                                               ('2', 'Gastos por cobrar'),
                                               ('3', 'Cambio de valor'),
                                               ('4', 'Otros')], string='Concepto nota débito')
    xml_file = fields.Binary('XML')
    xml_file_name = fields.Char('XML name')
    fe_pdf_file = fields.Binary('PDF')
    fe_pdf_name = fields.Char('PDF name')
    cufe_cude_ref = fields.Char('CUFE/CUDE')
    fe_status = fields.Selection([('draft', 'No procesado'), ('processed', 'Procesando'), ('accepted', 'Aceptado'), ('rejected', 'Rechazado'), ('other', 'Otro')], string='Estado de Factura Electrónica', default='draft')
    fe_status_info = fields.Char('Detalle del estado')
    fe_msg_result = fields.Char('Resultado de envío Factura Electrónica', tracking=True, store=True)
    fe_transaction_id = fields.Char('Id transacción de Factura Electrónica')
    fe_payment_option_id = fields.Many2one('fe.payment.options', string="Método de pago",
                                           default=lambda self: self.env.ref('fe_payment_options_1', raise_if_not_found=False))
    x_fe_sent = fields.Boolean(string='Factura Electrónica Enviada', default=False)
    z_purchase_order = fields.Char('Órden de Compra')
    z_alert_generated = fields.Boolean(string='Alerta generada')

    @api.model
    def create(self, vals):
        vals['xml_file'] = ''
        vals['xml_file_name'] = ''
        vals['fe_pdf_file'] = ''
        vals['fe_pdf_name'] = ''
        vals['cufe_cude_ref'] = ''
        vals['fe_status'] = 'draft'
        vals['fe_status_info'] = ''
        vals['fe_msg_result'] = ''
        vals['fe_transaction_id'] = ''

        amount_total = 1

        if 'tax_totals_json' in vals:
            if vals['tax_totals_json']:
                if 'amount_total' in json.loads(vals['tax_totals_json']):
                    amount_total = json.loads(vals['tax_totals_json'])['amount_total']

        if amount_total == 0:
            raise ValidationError(_('El valor total de la factura no puede ser 0. Por favor verifique!'))

        return super(account_move, self).create(vals)

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

        for record in self.filtered(lambda x: x.state == 'posted' and x.fe_status == 'draft' and not x.x_fe_sent and
                                              x.move_type in ['out_refund', 'out_invoice']):
            if record.state == 'posted':
                if record.move_type in ['out_refund', 'out_invoice']:
                    if record.fe_status != 'rejected':
                        record.send_all_process()


    def action_post(self):
        if not self.z_alert_generated:
             if self.journal_id.z_generate_alert:
                yes_no = ""

                if abs((date.today() - self.journal_id.dian_authorization_end_date).days) <= self.journal_id.z_expiration_days:
                    yes_no += "¡Su resolución de facturación DIAN esta próximo a vencer (Fecha por cumplirse)!. "

                max_sequence = self.env['account.move'].search([('journal_id', '=', self.journal_id.id), ('sequence_number', '!=', 0)],
                                                                   order='sequence_number desc', limit=1).sequence_number

                if (self.journal_id.dian_max_range_number - max_sequence) <= self.journal_id.z_expiration_folios:
                    yes_no += "¡Su resolución de facturación DIAN esta próximo a vencer! (Folio por cumplirse). "

                if yes_no:
                    return {
                        'name': 'Deseas continuar?',
                        'type': 'ir.actions.act_window',
                        'res_model': 'zue.confirm.wizard',
                        'view_mode': 'form',
                        'target': 'new',
                        'context': {'default_account_move_alert_id': self.id,
                                    'default_yes_no': yes_no}
                    }

        return super(account_move, self).action_post()

    def _post(self, soft=False):
        to_return = super(account_move, self)._post(soft=False)

        if self.env.company.zue_electronic_invoice_disable_sending:
            return to_return

        for record in to_return:
            if record.state == 'posted':
                if record.move_type in ['out_refund', 'out_invoice']:
                    if record.fe_status != 'rejected':
                        record.send_all_process()

        return to_return

    def get_invoice_line_ids(self, aiu=0, line_ids=[]):
        to_return = []
        if aiu:
            taxes_aiu = self.env['account.tax'].search([('name', 'ilike', 'AIU')]).filtered(lambda x: x.name.startswith('AIU')).ids
            to_return = self.env['account.move.line'].search(['&', ('id', 'in', line_ids.ids), ('tax_ids.id', 'in', taxes_aiu)])
        else:
            to_return = self.invoice_line_ids.filtered(lambda x: x.price_subtotal > 0 or x.discount == 100)

        return to_return


    def get_xml(self, support_document=False):
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
        xml = xml.decode("UTF-8").replace("<ITE/>", "").replace("<TII/>", "")

        if support_document:
            filename = f'DS_{str(date.today().year)}_{self.name}_{str(self.partner_id.name)}.xml'
        else:
            filename = f'FE_{str(date.today().year)}_{self.name}_{str(self.partner_id.name)}.xml'

        self.write({
            'xml_file': base64.encodestring(bytes(xml, 'UTF-8')),
            'xml_file_name': filename,
        })

        obj_attachment = self.env['ir.attachment'].search([('name', '=', filename)])
        if obj_attachment:
            obj_attachment.write({'datas': self.xml_file})
        else:
            data_attach = {'name': filename,
                           'type': 'binary', 'datas': self.xml_file, 'res_name': filename, 'store_fname': filename,
                           'res_model': 'account.move', 'res_id': self.id}

            atts_id = self.env['ir.attachment'].create(data_attach)

            self.message_post(body='XML generado correctamente.', attachment_ids=atts_id.ids)

        return True

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
                invoice_name = self.ref[:self.ref.find(',')]
            else:
                invoice_name = self.ref[
                               14: 50 if self.ref[14:].find(' ') == -1 else self.ref[14:].find(' ') if self.ref.find(
                                   ',') == -1 else self.ref.find(',')]

            to_execute = f'''obj_factura = o.env["account.move"].sudo().search([("name", "=", "{invoice_name.strip()}")], limit=1).{field_name}'''
            exec(to_execute,ldict)

            result = ldict.get('obj_factura')

            to_return = str(result)
        except Exception as e:
            raise UserError(_('Error %s') % e)

        return to_return

    def send_xml_FE(self):
        base64_file = self.xml_file
        if not base64_file:
            raise UserError(_('No se ha generado el archivo a enviar para la facturación electrónica. Por favor verifique!'))
        else:
            base64_file = base64_file.decode("UTF-8")

        user = self.company_id.zue_electronic_invoice_username
        password = self.company_id.zue_electronic_invoice_password

        obj_ws = self.env['zue.request.ws'].search([('name', '=', 'upload_file_fe')])
        if not obj_ws:
            raise ValidationError(_("Error! No ha configurado un web service con el nombre 'upload_file_fe'"))

        time.sleep(1)
        obj_result = obj_ws.connection_requests(user, password, base64_file)
        time.sleep(1)

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

        obj_ws = self.env['zue.request.ws'].search([('name', '=', 'check_status_fe')])
        if not obj_ws:
            raise ValidationError(_("Error! No ha configurado un web service con el nombre 'check_status_fe'"))

        obj_result = obj_ws.connection_requests(user, password, tmp_transaction_id)

        result = self.return_result_FE(obj_result, 'CHECK_FE')

        return result

    def download_pdf_file_FE(self, user='', password=''):
        if self.env['ir.attachment'].search([('res_model', '=', 'account.move'), ('name', '=', 'FE_' + self.name)]):
            return True

        tmp_transaction_id = self.fe_transaction_id
        if not tmp_transaction_id:
            raise UserError(_('No se ha realizado el envío de la factura. Por favor verifique!'))

        if not user:
            user = self.company_id.zue_electronic_invoice_username
            password = self.company_id.zue_electronic_invoice_password

        obj_ws = self.env['zue.request.ws'].search([('name', '=', 'download_pdf_fe')])
        if not obj_ws:
            raise ValidationError(_("Error! No ha configurado un web service con el nombre 'download_pdf_fe'"))

        document = self.journal_id.code
        number = self.name[len(document):]

        obj_result = obj_ws.connection_requests(user, password, document, number)

        self.return_result_FE(obj_result, 'GET_PDF')

    def get_cufe_FE(self, user='', password=''):
        if self.cufe_cude_ref:
            return True

        tmp_transaction_id = self.fe_transaction_id
        if not tmp_transaction_id:
            raise UserError(_('No se ha realizado el envío de la factura. Por favor verifique!'))

        if not user:
            user = self.company_id.zue_electronic_invoice_username
            password = self.company_id.zue_electronic_invoice_password

        obj_ws = self.env['zue.request.ws'].search([('name', '=', 'get_cufe_fe')])
        if not obj_ws:
            raise ValidationError(_("Error! No ha configurado un web service con el nombre 'get_cufe_fe'"))

        document = self.journal_id.code
        number = self.name[len(document):]

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

        if self.fe_status == 'draft':
            if self.xml_file_name:
                attachment = self.env['ir.attachment'].search([('res_model', '=', 'account.move'), ('name', '=', self.xml_file_name)])
                attachment.unlink()

            self.get_xml()

            send_result = self.send_xml_FE()
            if send_result in ('draft', 'accepted', 'processed', 'rejected', 'other'):
                result = self.check_status_FE()

            if result == 'accepted':
                self.get_cufe_FE()
                self.download_pdf_file_FE()
            else:
                if result != 'fail':
                    self.send_xml_FE()
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
            if self.xml_file_name:
                attachment = self.env['ir.attachment'].search([('res_model', '=', 'account.move'), ('name', '=', self.xml_file_name)])
                attachment.unlink()

            self.get_xml()
            self.send_xml_FE()
            result = self.check_status_FE()
            if result == 'accepted':
                self.get_cufe_FE()
                self.download_pdf_file_FE()
        elif self.fe_status == 'accepted':
            self.download_pdf_file_FE()

        if self.fe_status == 'accepted':
            self.x_fe_sent = True

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

                        result = self.env['ir.attachment'].create({
                            'name': 'FE_' + self.name,
                            'type': 'binary',
                            'datas': error_msg,
                            'res_model': 'account.move',
                            'res_id': self.id
                        })

                        if self.fe_status == 'accepted':
                            self.write({'x_fe_sent': True})

                if method == 'GET_CUFE':
                    cufe_position = obj_result.find('<resourceData xsi:type="xsd:string">') + len('<resourceData xsi:type="xsd:string">')
                    cufe = obj_result[cufe_position:obj_result.find('</resourceData>')]

                    if error_msg:
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


class zue_confirm_wizard(models.TransientModel):
    _inherit = 'zue.confirm.wizard'

    account_move_alert_id = fields.Many2one('account.move', string='Id Movimiento')

    def yes(self):
        if self.account_move_alert_id:
            obj_move = self.env['account.move'].search([('id', '=', self.account_move_alert_id.id)])
            obj_move.z_alert_generated = True
            obj_move._post()
        obj_confirm = super(zue_confirm_wizard, self).yes()
        return obj_confirm