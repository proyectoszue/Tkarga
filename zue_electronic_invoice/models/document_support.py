from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
import pandas as pd
import base64
from datetime import date, datetime
import uuid
from pytz import timezone
import hashlib

class sending_support_document(models.Model):
    _inherit = 'sending.support.document'

    def get_xmls(self):
        for row in self.executing_document_support_ids.filtered(lambda x: x.state in ('xml', 'draft')):
            row.get_xml()

        self.state = 'xml'

    def get_xmls_rejected(self):
        for row in self.executing_document_support_ids.filtered(lambda x: x.status != 'ACCEPTED'):
            row.get_xml()

    def upload_ds(self):
        count = 0
        for row in self.executing_document_support_ids.filtered(lambda x: x.state == 'xml'):
            row.consume_web_service_send_xml()
            count += 1

        if count > 0:
            self.state = 'ws'

    def upload_ds_rejected(self):
        for row in self.executing_document_support_ids.filtered(lambda x: x.state == 'xml' and x.status != 'ACCEPTED'):
            row.consume_web_service_send_xml()


    def check_document_status_ds(self):
        qty_failed = 0
        qty_done = 0

        for row in self.executing_document_support_ids:
            row.consume_web_service_status_document()
            if row.status == 'ACCEPTED':
                qty_done += 1
            else:
                qty_failed += 1

        self.qty_failed = qty_failed
        self.qty_done = qty_done

    def download_pdf_ds(self):
        for row in self.executing_document_support_ids.filtered(lambda x: x.state == 'ws'):
            row.consume_web_service_download_files()

        self.state = 'finished'

class sending_support_document_datail(models.Model):
    _inherit = 'sending.support.document.detail'

    def download_xml(self):
        action = {
            'name': 'XML Documento Soporte',
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=sending.support.document.detail&id=" + str(
                self.id) + "&filename_field=xml_file_name&field=xml_file&download=true&filename=" + self.xml_file_name,
            'target': 'self',
        }
        return action

    def download_pdf(self):
        action = {
            'name': 'PDF Documento Soporte',
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=sending.support.document.detail&id=" + str(
                self.id) + "&filename_field=pdf_name&field=pdf_file&download=true&filename=" + self.pdf_name,
            'target': 'self',
        }
        return action

    def get_xml(self):
        obj_xml = self.env['zue.xml.generator.header'].search([('code','=','DocSopElectronico_Ftech')])
        xml = obj_xml.xml_generator(self)
        xml = xml.decode('utf-8')
        xml = bytes(xml, 'utf-8')

        self.xml_file = None
        self.xml_file_name = ''

        filename = f'DS_{str(date.today().year)}_{str(self.document_support_id.id)}_{str(self.id)}.xml'
        self.xml_file = base64.encodestring(xml)
        self.xml_file_name = filename
        self.state = 'xml'

        # obj_attachment = self.env['ir.attachment'].search([('name', '=', filename)])
        # if obj_attachment:
        #     obj_attachment.write({'datas': self.xml_file})
        # else:
        #     data_attach = {'name': filename,
        #                    'type': 'binary', 'datas': self.xml_file, 'res_name': filename, 'store_fname': filename,
        #                    'res_model': 'account.move', 'res_id': self.id}
        #
        #     atts_id = self.env['ir.attachment'].create(data_attach)
        #
        #     self.message_post(body='XML generado correctamente.', attachment_ids=atts_id.ids)

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
        return impuestos

    def get_tax_type(self, percent, get_code):
        return_value = ''
        tmp_percent = float(percent)
        obj_tax = self.env['account.tax'].search([('amount', '=', tmp_percent), ('tax_type.code', '!=', None), ('company_id', 'in', self.env.user.company_ids.ids)], limit=1)

        if get_code:
            return_value = obj_tax.tax_type.code
        else:
            return_value = obj_tax.tax_type.retention

        return return_value

    def get_TAC_TCR(self, tag):
        to_return = ''

        if tag == 'TAC':
            for obj in self.move_id.company_id.partner_id.x_tax_responsibilities.filtered(lambda x: x.valid_for_fe == True):
                if to_return:
                    to_return = to_return + ',' + obj.code
                else:
                    to_return = obj.code
        elif tag == 'TCR':
            for obj in self.move_id.partner_id.x_tax_responsibilities.filtered(lambda x: x.valid_for_fe == True):
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
            invoice_name = self.move_id.ref[14: 50 if self.move_id.ref[14:].find(' ') == -1 else self.move_id.ref[14:].find(' ') if self.move_id.ref.find(',') == -1 else self.move_id.ref.find(',')]

            to_execute = f'''obj_factura = o.env["account.move"].sudo().search([("name", "=", "{invoice_name.strip()}")], limit=1).{field_name}'''
            exec(to_execute,ldict)

            result = ldict.get('obj_factura')

            to_return = str(result)
        except Exception as e:
            raise UserError(_('Error %s') % e)

        return to_return

    def return_result_FE(self, obj_result, method):
        code_position = -1
        error_msg, tmp_transaction_id, resource, state, cufe = '', '', '', '', ''
        status_code, error_position, transaction_position, resource_position, state_position, cufe_position = 0, 0, 0, 0, 0, 0

        code_position = obj_result.find('</code>') - 3

        if code_position > -1:
            status_code = int(obj_result[code_position:code_position + 3])

            if status_code >= 400:
                if '</error>' in obj_result:
                    error_position = obj_result.find('<error xsi:type="xsd:string">') + len('<error xsi:type="xsd:string">')
                    error_msg = obj_result[error_position:obj_result.find('</error>')]
                elif '</message>' in obj_result:
                    error_position = obj_result.find('<message xsi:type="xsd:string">') + len('<message xsi:type="xsd:string">')
                    error_msg = obj_result[error_position:obj_result.find('</message>')]
                else:
                    error_msg = 'No fue posible identificar el error. Contacte con el administrador!'

                if method == 'CHECK_FE':
                    self.status = 'REJECTED'
                elif method == 'SEND_FE':
                    if '<message xsi:type="xsd:string">El comprobante  ya ha sido firmado previamente. TrasactionID ' in obj_result:
                        tmp_transaction_id = obj_result[obj_result.find(
                            '<message xsi:type="xsd:string">El comprobante  ya ha sido firmado previamente. TrasactionID ') + len(
                            '<message xsi:type="xsd:string">El comprobante  ya ha sido firmado previamente. TrasactionID '):obj_result.find(
                            '</message>')]

                    if tmp_transaction_id == '':
                        self.status = 'ERROR AL ENVIAR XML'
                    else:
                        if 'Ya existe un comprobante con ese mismo tipo' not in obj_result:
                            self.status = 'XML ENVIADO'
                            self.transaction_id = tmp_transaction_id
                        error_msg = 'El comprobante  ya ha sido firmado previamente.'
                elif method == 'GET_PDF':
                    if '<messageError xsi:type="xsd:string">' in obj_result:
                        error_position = obj_result.find('<messageError xsi:type="xsd:string">') + len('<messageError xsi:type="xsd:string">')
                        error_msg = obj_result[error_position:obj_result.find('</messageError>')]

                    if not error_msg:
                        error_msg = 'Se presentó un error al descargar el PDF'

                    self.result_status = error_msg
                if method != 'GET_PDF':
                    self.result_upload_xml = error_msg
                    self.result_status = error_msg
                return error_msg

            if status_code in (200, 201, 202, 203):
                error_position = obj_result.find('<message xsi:type="xsd:string">') + len('<message xsi:type="xsd:string">')
                error_msg = obj_result[error_position:obj_result.find('</message>')]

                self.result_upload_xml = error_msg
                self.result_status = error_msg

                if method == 'CHECK_FE':
                    if '<message xsi:type="xsd:string">' in obj_result:
                        state_position = obj_result.find('<message xsi:type="xsd:string">') + len('<message xsi:type="xsd:string">')
                        state = obj_result[state_position:obj_result.find('</message>')]

                        if 'ha sido autorizado' in state:
                            self.status = 'ACCEPTED'
                            self.result_status = state
                            return 'ACCEPTED'
                    elif '<messageError xsi:type="xsd:string">' in obj_result:
                        state_position = obj_result.find('<messageError xsi:type="xsd:string">') + len('<messageError xsi:type="xsd:string">')
                        state = obj_result[state_position:obj_result.find('</messageError>')]

                        self.status = 'REJECTED'
                        self.result_status = state
                        return 'REJECTED'
                    else:
                        self.status = 'PROCESSED'
                        return 'PROCESSED'

                if method == 'SEND_FE':
                    to_search = ''
                    error_to_search = ''

                    if '<transaccionID xsi:type="xsd:string">' in obj_result:
                        to_search = '<transaccionID xsi:type="xsd:string">'
                    else:
                        if '<transactionID xsi:type="xsd:string">' in obj_result:
                            to_search = '<transactionID xsi:type="xsd:string">'

                    if '<error xsi:type="xsd:string">El comprobante  ya ha sido firmado previamente. transactionID ' in obj_result:
                        error_to_search = '<error xsi:type="xsd:string">El comprobante  ya ha sido firmado previamente. transactionID '
                    else:
                        if '<error xsi:type="xsd:string">El comprobante  ya ha sido firmado previamente. transaccionID ' in obj_result:
                            error_to_search = '<error xsi:type="xsd:string">El comprobante  ya ha sido firmado previamente. transaccionID '


                    if to_search in obj_result:
                        transaction_position = obj_result.find(to_search) + len(to_search)
                        tmp_transaction_id = obj_result[transaction_position:obj_result.find('</transactionID>')]

                        if tmp_transaction_id == '':
                            if error_to_search in obj_result:
                                tmp_transaction_id = obj_result[obj_result.find(
                                    error_to_search) + len(
                                    error_to_search):obj_result.find('</error>')]
                            if tmp_transaction_id == '':
                                self.status = 'ERROR AL ENVIAR XML'
                            else:
                                self.status = 'XML ENVIADO'
                                self.transaction_id = tmp_transaction_id
                        else:
                            self.status = 'XML ENVIADO'
                            self.transaction_id = tmp_transaction_id

                if method == 'GET_PDF':
                    if '<documentBase64 xsi:type="xsd:string">' in obj_result:
                        error_position = obj_result.find('<documentBase64 xsi:type="xsd:string">') + len('<documentBase64 xsi:type="xsd:string">')
                        error_msg = obj_result[error_position:obj_result.find('</documentBase64>')]

                        filename = 'DS_' + str(self.partner_id.vat) + '_' + str(self.document_support_id.id) + '.pdf'

                        if error_msg:
                            self.pdf_name = filename
                            self.pdf_file = error_msg

                            result = self.env['ir.attachment'].create({
                                'name': filename,
                                'type': 'binary',
                                'datas': error_msg,
                                'res_model': 'sending.support.document.detail',
                                'res_id': self.id
                            })

                if method == 'GET_CUFE':
                    cufe_position = obj_result.find('<resourceData xsi:type="xsd:string">') + len('<resourceData xsi:type="xsd:string">')
                    cufe = obj_result[cufe_position:obj_result.find('</resourceData>')]

                    if error_msg:
                        self.cuds = cufe

        return True


    def send_xml_FE(self):
        base64_file = self.xml_file
        if not base64_file:
            raise UserError(_('No se ha generado el archivo a enviar para la facturación electrónica. Por favor verifique!'))
        else:
            base64_file = str(base64_file)[2:-1]

        user = self.move_id.company_id.zue_support_document_username
        password = self.move_id.company_id.zue_support_document_password

        obj_ws = self.env['zue.request.ws'].search([('name', '=', 'upload_file_fe')])
        if not obj_ws:
            raise ValidationError(_("Error! No ha configurado un web service con el nombre 'upload_file_fe'"))

        obj_result = obj_ws.connection_requests(user, password, base64_file)

        result = self.return_result_FE(obj_result, 'SEND_FE')

        if result:
            return result
        else:
            if self.status:
                return self.status
            else:
                return ''

    def consume_web_service_send_xml(self):
        try:
            username = self.move_id.company_id.zue_support_document_username
            password = self.move_id.company_id.zue_support_document_password
            # if username and password:
            #     password = hashlib.sha256(password.encode()).hexdigest()
            # else:
            #     raise ValidationError(_("No se ha definido un usuario y/o contraseña para el uso del servicio de envío de documentos de Carvajal"))

            filename = self.xml_file_name
            filedata = str(self.xml_file).split("'")[1]

            #Ejecutar ws
            obj_ws = self.env['zue.request.ws'].search([('name', '=', 'ftech_ds_upload_xml')])
            if not obj_ws:
                raise ValidationError(_("Error! No ha configurado un web service con el nombre 'ftech_ds_upload_xml'"))

            obj_result = obj_ws.connection_requests(username, password, filedata)

            result = self.return_result_FE(obj_result, 'SEND_FE')

            # if result:
            #     return result
            # else:
            #     if self.fe_status:
            #         return self.fe_status
            #     else:
            #         return ''

            # self.result_upload_xml = result

            self.state = 'ws'

            self.move_id.write({'x_support_document_sent': True})

        except Exception as e:
            self.status = 'ERROR AL ENVIAR XML'
            self.result_status = 'Error: %s' % (str(e))


    def consume_web_service_status_document(self):
        if self.result_status != 'ENVIADO':
            username = self.move_id.company_id.zue_support_document_username
            password = self.move_id.company_id.zue_support_document_password

            tmp_transaction_id = self.transaction_id
            if not tmp_transaction_id:
                # raise UserError(_('No se ha realizado el envío de la factura. Por favor verifique!'))
                return 'No se ha realizado el envío de la factura. Por favor verifique!'

            if not username:
                username = self.move_id.company_id.zue_support_document_username
                password = self.move_id.company_id.zue_support_document_password

            obj_ws = self.env['zue.request.ws'].search([('name', '=', 'ftech_ds_status_document')])
            if not obj_ws:
                raise ValidationError(_("Error! No ha configurado un web service con el nombre 'ftech_ds_status_document'"))

            obj_result = obj_ws.connection_requests(username, password, tmp_transaction_id)

            result = self.return_result_FE(obj_result, 'CHECK_FE')

            return True

    def consume_web_service_download_files(self):
        tmp_transaction_id = self.transaction_id
        username = self.move_id.company_id.zue_support_document_username
        password = self.move_id.company_id.zue_support_document_password

        if not tmp_transaction_id:
            raise UserError(_('No se ha realizado el envío de la factura. Por favor verifique!'))

        if not username:
            username = self.move_id.company_id.zue_support_document_username
            password = self.move_id.company_id.zue_support_document_password

        obj_ws = self.env['zue.request.ws'].search([('name', '=', 'ftech_ds_download_file_document')])
        if not obj_ws:
            raise ValidationError(_("Error! No ha configurado un web service con el nombre 'ftech_ds_download_file_document'"))

        document = self.document_support_id.journal_resolution_id.code
        number = self.consecutive_doc_support[len(document):]

        obj_result = obj_ws.connection_requests(username, password, document, number)

        result = self.return_result_FE(obj_result, 'GET_PDF')
        if result != '':
            return True

        action = {
            'name':'Documento Soporte',
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=sending.support.document.detail&id=" + str(
                self.id) + "&filename_field=pdf_name&field=pdf_file&download=true&filename=" + self.pdf_name,
            'target': 'self',
        }

        return action

    def consume_web_service_get_cuds(self):
        try:
            username = self.move_id.company_id.zue_support_document_username
            password = self.move_id.company_id.zue_support_document_password
            tmp_transaction_id = self.fe_transaction_id

            if not tmp_transaction_id:
                raise UserError(_('No se ha realizado el envío de la factura. Por favor verifique!'))

            if not username:
                username = self.move_id.company_id.zue_support_document_username
                password = self.move_id.company_id.zue_support_document_password

            obj_ws = self.env['zue.request.ws'].search([('name', '=', 'ftech_ds_get_cuds')])
            if not obj_ws:
                raise ValidationError(_("Error! No ha configurado un web service con el nombre 'ftech_ds_get_cuds'"))

            document = self.document_support_id.journal_resolution_id.code
            number = self.consecutive_doc_support[len(document):]

            obj_result = obj_ws.connection_requests(username, password, document, number)

            self.return_result_FE(obj_result, 'GET_CUFE')

        except Exception as e:
            print('DS %s Error: %s' % (self.id, str(e)))

    def update_data_move(self):
        # Se obtienen los movimientos publicados en el rango de fechas que tienen un diario con documento soporte
        obj_moves = self.move_id
        obj_moves_lines = self.line_move_ids

        # Insertar movimientos
        if len(obj_moves_lines) == 0:
            raise ValidationError(_('No se encontro información de acuerdo a los filtros ingresados.'))

        lst_moves = []
        for move in obj_moves_lines:
            dict_move = {
                'partner_id': move.partner_id.id,
                'move_id': move.move_id.id,
                'concept': move.name,
                'first_concept': '/',
                'amount': move.debit - move.credit
            }
            lst_moves.append(dict_move)
        # Se guarda la data en pandas
        moves_df = pd.DataFrame(lst_moves)
        # Se agrupa por tercero, asiento contable y diario
        group_moves_df = moves_df.groupby(by=['partner_id', 'move_id', 'first_concept'], group_keys=False,as_index=False).sum()
        # Se obtiene el primer concepto de cada detalle y los apuntes contables
        count_sequence = 0
        for i, j in group_moves_df.iterrows():
            concepts = moves_df.loc[(moves_df['move_id'] == group_moves_df.loc[i, 'move_id']) & (
                        moves_df['partner_id'] == group_moves_df.loc[i, 'partner_id']), 'concept']
            group_moves_df.loc[i, 'first_concept'] = concepts.values[0]
            count_sequence += 1
        # Salvar proceso
        lst_moves_finally = group_moves_df.to_dict(orient='records')
        for dict_move in lst_moves_finally:
            # Se guarda en la tabla detalle del proceso
            self.write(dict_move)
