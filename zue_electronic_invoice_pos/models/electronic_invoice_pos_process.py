from odoo import api, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
import logging
import xml.etree.ElementTree as ET

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def _is_pos_electronic_invoice(self):
        return bool(self.pos_order_ids or self.reversed_entry_id.pos_order_ids)

    def _get_fe_xml_prefixes(self):
        if self._is_pos_electronic_invoice():
            return "POSFacElectronica_", "POS_FE_v2_"
        return super()._get_fe_xml_prefixes()

    def _get_fe_web_service_name(self, service_name):
        if self._is_pos_electronic_invoice():
            return {
                "upload_file_fe": "uploadDocumentpos",
                "check_status_fe": "documentStatuspos",
                "download_pdf_fe": "documentpdfpos",
                "get_cufe_fe": "documentcufepos",
            }.get(service_name, service_name)
        return super()._get_fe_web_service_name(service_name)

    def send_xml_FE(self):
        if not self._is_pos_electronic_invoice():
            return super().send_xml_FE()
        invoice_format = self.env.company.zue_electronic_invoice_format or 'xml'
        if invoice_format == 'json':
            base64_file = self.json_file
            file_type = 'JSON'
        else:
            base64_file = self.xml_file
            file_type = 'XML'
        if not base64_file:
            raise UserError(_('No se ha generado el archivo %s a enviar para la facturación electrónica. Por favor verifique!') % file_type)
        base64_file = base64_file.decode("UTF-8")
        user = self.company_id.zue_electronic_invoice_username
        password = self.company_id.zue_electronic_invoice_password
        obj_ws = self.env['zue.request.ws'].search([('name', '=', self._get_fe_web_service_name('upload_file_fe'))])
        if not obj_ws:
            raise ValidationError(_("Error! No ha configurado un web service con el nombre 'upload_file_fe'"))
        obj_result = obj_ws.connection_requests(user, password, base64_file, response_file=True)
        result = self.return_result_FE(obj_result, 'SEND_FE')
        if result:
            return result
        return self.fe_status or ''

    def check_status_FE(self, user='', password=''):
        if not self._is_pos_electronic_invoice():
            return super().check_status_FE(user=user, password=password)
        tmp_transaction_id = self.fe_transaction_id
        if not tmp_transaction_id:
            return 'No se ha realizado el envío de la factura. Por favor verifique!'
        if not user:
            user = self.company_id.zue_electronic_invoice_username
            password = self.company_id.zue_electronic_invoice_password
        obj_ws = self.env['zue.request.ws'].search([('name', '=', self._get_fe_web_service_name('check_status_fe'))])
        if not obj_ws:
            raise ValidationError(_("Error! No ha configurado un web service con el nombre 'check_status_fe'"))
        obj_result = obj_ws.connection_requests(user, password, tmp_transaction_id, response_file=True)
        return self.return_result_FE(obj_result, 'CHECK_FE')

    def download_pdf_file_FE(self, user='', password=''):
        if not self._is_pos_electronic_invoice():
            return super().download_pdf_file_FE(user=user, password=password)
        self.ensure_one()
        self._acquire_ftech_lock('download_pdf')
        if self.env['ir.attachment'].search(self._get_fe_attachment_domain('FE_' + self.name), limit=1):
            return True
        tmp_transaction_id = self.fe_transaction_id
        if not tmp_transaction_id:
            raise UserError(_('No se ha realizado el envío de la factura. Por favor verifique!'))
        if not user:
            user = self.company_id.zue_electronic_invoice_username
            password = self.company_id.zue_electronic_invoice_password
        obj_ws = self.env['zue.request.ws'].search([('name', '=', self._get_fe_web_service_name('download_pdf_fe'))])
        if not obj_ws:
            raise ValidationError(_("Error! No ha configurado un web service con el nombre 'download_pdf_fe'"))
        document, number = self._get_ftech_document_number()
        obj_result = obj_ws.connection_requests(user, password, document, number, response_file=True)
        self.return_result_FE(obj_result, 'GET_PDF')

    def get_cufe_FE(self, user='', password=''):
        if not self._is_pos_electronic_invoice():
            return super().get_cufe_FE(user=user, password=password)
        if self.cufe_cude_ref:
            return True
        tmp_transaction_id = self.fe_transaction_id
        if not tmp_transaction_id:
            raise UserError(_('No se ha realizado el envío de la factura. Por favor verifique!'))
        if not user:
            user = self.company_id.zue_electronic_invoice_username
            password = self.company_id.zue_electronic_invoice_password
        obj_ws = self.env['zue.request.ws'].search([('name', '=', self._get_fe_web_service_name('get_cufe_fe'))])
        if not obj_ws:
            raise ValidationError(_("Error! No ha configurado un web service con el nombre 'get_cufe_fe'"))
        document, number = self._get_ftech_document_number()
        obj_result = obj_ws.connection_requests(user, password, document, number, response_file=True)
        self.return_result_FE(obj_result, 'GET_CUFE')
        return True

    def send_all_process(self):
        if not self._is_pos_electronic_invoice():
            return super().send_all_process()
        self.ensure_one()
        self._acquire_ftech_lock('full_process')
        result = ''
        if self.company_id.zue_electronic_invoice_disable_sending:
            return True
        if self.journal_id.z_disable_dian_sending:
            return True
        invoice_format = self.env.company.zue_electronic_invoice_format or 'xml'
        if self.fe_status == 'draft':
            if invoice_format == 'json':
                if self.json_file_name:
                    self.env['ir.attachment'].search([('res_model', '=', 'account.move'), ('name', '=', self.json_file_name)]).unlink()
                self.get_json()
            else:
                if self.xml_file_name:
                    self.env['ir.attachment'].search(self._get_fe_attachment_domain(self.xml_file_name)).unlink()
            self.get_xml_v2()
            send_result = self.send_xml_FE()
            self.message_post(body=_("Se envió la factura electrónica a la DIAN. Resultado: %s") % (send_result or 'N/A'))
            if isinstance(send_result, str) and 'error' in send_result:
                return True
            if self.fe_transaction_id:
                result = 'accepted'
            if result == 'accepted':
                self.check_status_FE()
                try:
                    self.get_cufe_FE()
                    self.download_pdf_file_FE()
                except Exception as e:
                    _logger.warning("POS FE post-envío CUFE/PDF factura %s: %s", self.name, e)
            elif result != 'fail':
                self.send_xml_FE()
                self.message_post(body=_("Se reenvió la factura electrónica a la DIAN. Resultado: %s") % (send_result or 'N/A'))
                if self.fe_transaction_id:
                    result = 'accepted'
                    self.check_status_FE()
                    try:
                        self.get_cufe_FE()
                        self.download_pdf_file_FE()
                    except Exception as e:
                        _logger.warning("POS FE post-reenvío CUFE/PDF factura %s: %s", self.name, e)
        elif self.fe_status == 'processed':
            result = self.check_status_FE()
            if result == 'accepted':
                try:
                    self.get_cufe_FE()
                    self.download_pdf_file_FE()
                except Exception as e:
                    _logger.warning("POS FE CUFE/PDF factura %s: %s", self.name, e)
        elif self.fe_status in ('other', 'rejected'):
            if invoice_format == 'json':
                if self.json_file_name:
                    self.env['ir.attachment'].search([('res_model', '=', 'account.move'), ('name', '=', self.json_file_name)]).unlink()
                self.get_json()
            else:
                if self.xml_file_name:
                    self.env['ir.attachment'].search(self._get_fe_attachment_domain(self.xml_file_name)).unlink()
            self.get_xml_v2()
            self.send_xml_FE()
            if self.fe_transaction_id:
                result = 'accepted'
            else:
                result = self.check_status_FE()
            if result == 'accepted':
                try:
                    self.get_cufe_FE()
                    self.download_pdf_file_FE()
                except Exception as e:
                    _logger.warning("POS FE CUFE/PDF factura %s: %s", self.name, e)
        elif self.fe_status == 'accepted':
            try:
                if not self.cufe_cude_ref:
                    self.get_cufe_FE()
                self.download_pdf_file_FE()
            except Exception as e:
                _logger.warning("POS FE CUFE/PDF factura %s: %s", self.name, e)
        if self.fe_status == 'accepted' and not self.x_fe_sent:
            self.x_fe_sent = True
            self.fe_sent_date = datetime.now()
            self.fe_msg_result = 'Documento Aceptado!'
        return True

    def _parse_pos_fe_xml(self, obj_result):
        if isinstance(obj_result, bytes):
            obj_result = obj_result.decode('utf-8', errors='replace')
        xml_text = obj_result.strip()
        if '<' in xml_text:
            xml_text = xml_text[xml_text.find('<'):]
        return xml_text, ET.fromstring(xml_text)

    def _extract_pos_transaction_id(self, root, xml_text=''):
        node = root.find('.//{*}transactionID')
        if node is not None and node.text:
            return node.text.strip()
        start_tag = '<transactionID xsi:type="xsd:string">'
        if start_tag in xml_text:
            start = xml_text.find(start_tag) + len(start_tag)
            end = xml_text.find('</transactionID>', start)
            if end > start:
                return xml_text[start:end].strip()
        return ''

    def return_result_FE(self, obj_result, method):
        if not self._is_pos_electronic_invoice():
            return super().return_result_FE(obj_result, method)
        xml_text, root = self._parse_pos_fe_xml(obj_result)
        code_node = root.find('.//{*}code')
        status_code = int(code_node.text) if code_node is not None and code_node.text else 0
        msg_node = root.find('.//{*}message')
        error_msg = msg_node.text if msg_node is not None and msg_node.text else ''
        if status_code >= 400:
            if error_msg and ('transactionID' in error_msg or 'TrasactionID' in error_msg):
                marker = 'transactionID ' if 'transactionID ' in error_msg else 'TrasactionID '
                trasaction_id = error_msg[error_msg.find(marker) + len(marker):].strip()
                self.write({
                    'fe_transaction_id': trasaction_id,
                    'fe_msg_result': error_msg + ".Ya puede descargar el PDF",
                    'fe_status': 'accepted',
                })
                self.message_post(body=_("FE aceptada. Mensaje: %s. Ya puede descargar el PDF.") % error_msg)
            elif method in ('SEND_FE', 'CHECK_FE'):
                self.write({'fe_msg_result': error_msg, 'fe_status': 'rejected'})
                self.message_post(body=_("FE rechazada. Error: %s") % error_msg)
            else:
                self.write({'fe_msg_result': error_msg})
            return error_msg
        if status_code in (200, 201, 202, 203):
            self.write({'fe_msg_result': error_msg})
            if method == 'CHECK_FE':
                status_node = root.find('.//{*}status')
                state = status_node.text if status_node is not None and status_node.text else ''
                if state == 'SIGNED_XML':
                    self.write({'fe_status': 'accepted'})
                    return 'accepted'
                if state == 'PROCESSING':
                    self.write({'fe_status': 'processed'})
                    return 'processed'
                self.write({'fe_status': 'accepted', 'fe_status_info': state or error_msg})
                return 'accepted'
            if method == 'SEND_FE':
                tmp_transaction_id = self._extract_pos_transaction_id(root, xml_text)
                vals = {'fe_msg_result': error_msg or 'El comprobante ha sido recibido correctamente.'}
                if tmp_transaction_id:
                    vals['fe_transaction_id'] = tmp_transaction_id
                    vals['fe_status'] = 'processed'
                self.write(vals)
                return 'fail'
            if method == 'GET_PDF':
                pdf_node = root.find('.//{*}documentBase64')
                pdf_data = pdf_node.text if pdf_node is not None and pdf_node.text else ''
                if pdf_data:
                    self.write({'fe_pdf_name': 'FE_' + self.name})
                    attachment_name = 'FE_' + self.name
                    attachment = self.env['ir.attachment'].search(self._get_fe_attachment_domain(attachment_name), limit=1)
                    if attachment:
                        attachment.write({'datas': pdf_data})
                    else:
                        self.env['ir.attachment'].create({
                            'name': attachment_name,
                            'type': 'binary',
                            'datas': pdf_data,
                            'res_model': 'account.move',
                            'res_id': self.id,
                        })
                    if self.fe_status == 'accepted':
                        self.write({'x_fe_sent': True})
            if method == 'GET_CUFE':
                cufe_node = root.find('.//{*}resourceData')
                cufe = cufe_node.text if cufe_node is not None and cufe_node.text else ''
                if cufe:
                    self.write({'cufe_cude_ref': cufe})
        return True


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def sync_from_ui(self, orders):
        for order in orders or []:
            order["to_invoice"] = True
        res = super().sync_from_ui(orders)
        order_ids = [order["id"] for order in res.get("pos.order", []) if order.get("id")]
        for order in self.browse(order_ids):
            if order.account_move:
                try:
                    order.account_move.send_all_process()
                    _logger.info("Factura %s enviada a FE correctamente.", order.account_move.name)
                except Exception as e:
                    _logger.error(
                        "Error enviando FE para factura %s: %s",
                        order.account_move.name,
                        str(e),
                    )
        return res
