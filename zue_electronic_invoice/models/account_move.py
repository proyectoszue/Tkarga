from odoo.exceptions import ValidationError, UserError
from odoo import models, fields, api, _
import base64
from datetime import date

#MOVIMIENTO CONTABLE ENCABEZADO

class account_move(models.Model):
    _inherit = 'account.move'

    xml_file = fields.Binary('XML')
    xml_file_name = fields.Char('XML name', size=64)
    fe_pdf_file = fields.Binary('PDF')
    fe_pdf_name = fields.Char('PDF name', size=64)
    cufe_cude_ref = fields.Char('CUFE/CUDE')
    fe_sent_name = fields.Char('Nombre de Factura Electrónica')
    fe_status = fields.Char('Estado de Factura Electrónica')
    fe_msg_result = fields.Char('Resultado de envío Factura Electrónica', track_visibility='onchange')
    fe_transaction_id = fields.Char('Id transacción de Factura Electrónica')

    # def action_post(self):
    #     obj_action_post = super(account_move, self).action_post()
    #
    #     if self.get_xml():
    #         if self.send_xml_FE():
    #             if self.check_status_FE() == 'SIGNED_XML':
    #                 self.get_cufe_FE()
    #
    #     return obj_action_post

    def get_xml(self):
        obj_xml = self.env['zue.xml.generator.header'].search([('code','=','FacElectronica_FacturaTech')])
        xml = obj_xml.xml_generator(self)

        filename = f'FE_{str(date.today().year)}_{self.name}_{str(self.partner_id.name)}.xml'

        filename_no_ext = f'FE_{str(date.today().year)}_{self.name}_{str(self.partner_id.name)}'
        self.write({
            'xml_file': base64.encodestring(xml),
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

        # action = {
        #     'name': 'XMLFacturacionElectronicaFacturaTech',
        #     'type': 'ir.actions.act_url',
        #     'url': "web/content/?model=account.move&id=" + str(
        #         self.id) + "&filename_field=xml_file_name&field=xml_file&download=true&filename=" + self.xml_file_name,
        #     'target': 'self',
        # }

        return True

    def get_Fiscal_Value_TCR_TAC(self, partner_id):
        obj_partner = self.env['res.partner'].search([('id', '=', partner_id)])
        fiscal_value = ''

        for obj in obj_partner.x_tax_responsibilities.filtered(lambda x: x.valid_for_fe == True):
            if fiscal_value != '':
                fiscal_value += ','

            fiscal_value += str(obj.code)

        return fiscal_value

    def get_impuestos_TIM(self):
        impuestos = []
        line_tax = {}
        for invoice in self.invoice_line_ids:
            for tax in invoice.tax_ids:
                if tax.amount < 0:
                    continue

                if line_tax.get(str(tax.amount), 0) == 0:
                    line_tax.update({
                        str(tax.amount): tax.amount * invoice.price_subtotal / 100,
                    })
                else:
                    line_tax[str(tax.amount)] = line_tax.get(str(tax.amount), 0) + (tax.amount * invoice.price_subtotal / 100)

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
            to_return = 'R99'

        if to_return == '':
            to_return = 'R99'

        return to_return

    def get_info_ref_Factura(self, field_name):
        to_return = ''
        obj_factura = None
        ldict = {'o':self}

        try:
            invoice_name = self.ref[14: 50 if self.ref[14:].find(' ') == -1 else self.ref[14:].find(' ') if self.ref.find(',') == -1 else self.ref.find(',')]

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
            base64_file = str(base64_file)[2:-1]

        user = self.env['ir.config_parameter'].sudo().get_param('zue_account.zue_electronic_invoice_username')
        password = self.env['ir.config_parameter'].sudo().get_param('zue_account.zue_electronic_invoice_password')

        obj_ws = self.env['zue.request.ws'].search([('name', '=', 'upload_file_fe')])
        if not obj_ws:
            raise ValidationError(_("Error! No ha configurado un web service con el nombre 'upload_file_fe'"))

        obj_result = obj_ws.connection_requests(user, password, base64_file)

        self.return_result_FE(obj_result, 'SEND_FE')

        if self.fe_status:
            return self.fe_status
        else:
            return ''

    def check_status_FE(self, user='', password=''):
        tmp_transaction_id = self.fe_transaction_id
        if not tmp_transaction_id:
            raise UserError(_('No se ha realizado el envío de la factura. Por favor verifique!'))

        if not user:
            user = self.env['ir.config_parameter'].sudo().get_param('zue_account.zue_electronic_invoice_username')
            password = self.env['ir.config_parameter'].sudo().get_param('zue_account.zue_electronic_invoice_password')

        obj_ws = self.env['zue.request.ws'].search([('name', '=', 'check_status_fe')])
        if not obj_ws:
            raise ValidationError(_("Error! No ha configurado un web service con el nombre 'check_status_fe'"))

        obj_result = obj_ws.connection_requests(user, password, tmp_transaction_id)

        result = self.return_result_FE(obj_result, 'CHECK_FE')

        return result

    def download_pdf_file_FE(self, user='', password=''):
        tmp_transaction_id = self.fe_transaction_id
        if not tmp_transaction_id:
            raise UserError(_('No se ha realizado el envío de la factura. Por favor verifique!'))

        if not user:
            user = self.env['ir.config_parameter'].sudo().get_param('zue_account.zue_electronic_invoice_username')
            password = self.env['ir.config_parameter'].sudo().get_param('zue_account.zue_electronic_invoice_password')

        obj_ws = self.env['zue.request.ws'].search([('name', '=', 'download_pdf_fe')])
        if not obj_ws:
            raise ValidationError(_("Error! No ha configurado un web service con el nombre 'download_pdf_fe'"))

        document = self.journal_id.code
        number = self.name[len(document):]

        obj_result = obj_ws.connection_requests(user, password, document, number)

        self.return_result_FE(obj_result, 'GET_PDF')

        if self.fe_pdf_file:
            action = {
                'name': 'XMLFacturacionElectronicaFacturaTech',
                'type': 'ir.actions.act_url',
                'url': "web/content/?model=account.move&id=" + str(self.id) + "&filename_field=fe_pdf_name&field=fe_pdf_file&download=true&filename=" + self.fe_pdf_name,
                'target': 'self',
            }

            return action

    def get_cufe_FE(self, user='', password=''):
        tmp_transaction_id = self.fe_transaction_id
        if not tmp_transaction_id:
            raise UserError(_('No se ha realizado el envío de la factura. Por favor verifique!'))

        if not user:
            user = self.env['ir.config_parameter'].sudo().get_param('zue_account.zue_electronic_invoice_username')
            password = self.env['ir.config_parameter'].sudo().get_param('zue_account.zue_electronic_invoice_password')

        obj_ws = self.env['zue.request.ws'].search([('name', '=', 'get_cufe_fe')])
        if not obj_ws:
            raise ValidationError(_("Error! No ha configurado un web service con el nombre 'get_cufe_fe'"))

        document = self.journal_id.code
        number = self.name[len(document):]

        obj_result = obj_ws.connection_requests(user, password, document, number)

        self.return_result_FE(obj_result, 'GET_CUFE')

        return True

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

                self.write({'fe_msg_result': error_msg})

            if status_code in (200, 201, 202, 203):
                error_position = obj_result.find('<success xsi:type="xsd:string">') + len('<success xsi:type="xsd:string">')
                error_msg = obj_result[error_position:obj_result.find('</success>')]

                self.write({'fe_msg_result': error_msg})

                if method == 'CHECK_FE':
                    state_position = obj_result.find('<status xsi:type="xsd:string">') + len('<status xsi:type="xsd:string">')
                    state = obj_result[state_position:obj_result.find('</status>')]

                    self.write({'fe_status': state})

                if method == 'SEND_FE':
                    transaction_position = obj_result.find('<transaccionID xsi:type="xsd:string">') + len('<transaccionID xsi:type="xsd:string">')
                    tmp_transaction_id = obj_result[transaction_position:obj_result.find('</transaccionID>')]

                    self.write({'fe_transaction_id': tmp_transaction_id})

                if method == 'GET_PDF':
                    error_position = obj_result.find('<resourceData xsi:type="xsd:string">') + len('<resourceData xsi:type="xsd:string">')
                    error_msg = obj_result[error_position:obj_result.find('</resourceData>')]

                    if error_msg:
                        self.write({'fe_pdf_file': error_msg,
                                    'fe_pdf_name': 'FE_' + self.name})

                if method == 'GET_CUFE':
                    cufe_position = obj_result.find('<resourceData xsi:type="xsd:string">') + len('<resourceData xsi:type="xsd:string">')
                    cufe = obj_result[cufe_position:obj_result.find('</resourceData>')]

                    if error_msg:
                        self.write({'cufe_cude_ref': cufe})

        return True
