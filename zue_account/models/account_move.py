from odoo.exceptions import ValidationError, UserError
from odoo import models, fields, api, _
import base64
from datetime import date

#MOVIMIENTO CONTABLE ENCABEZADO

class account_move(models.Model):
    _inherit = 'account.move'

    supplier_invoice_number = fields.Char(string='Nº de factura del proveedor',help="La referencia de esta factura proporcionada por el proveedor.")
    supplier_invoice_attachment = fields.Many2one('documents.document',string="Soporte") #fields.Binary(string="Soporte")
    iva_amount = fields.Float('Valor IVA', compute='_compute_amount_iva', store=True)
    l10n_co_edi_type = fields.Selection([('1', 'Factura de venta'),
                                        ('2', 'Factura de exportación'),
                                        ('3', 'Notas electrónicas'),
                                        ('4', 'Factura de contingencia'),
                                        ], string='Tipo de Documento')
    # XML
    xml_file = fields.Binary('XML')
    xml_file_name = fields.Char('XML name', size=64)
    cufe_cude_ref = fields.Char('CUFE/CUDE')
    fe_sent_name = fields.Char('Nombre de Factura Electrónica')
    fe_status = fields.Char('Estado de Factura Electrónica')

    #supplier_invoice_attachment_name = fields.Char(string="Soporte Filename")
    @api.depends('line_ids','invoice_line_ids')
    def _compute_amount_iva(self):
        iva_amount = 0

        if self.invoice_line_ids.tax_id:
            obj_taxes = self.env['account.tax'].search([('name', 'ilike', 'IVA')])

            percent = obj_taxes[0].amount

            for lines in self.invoice_line_ids:
                for taxes in lines.tax_ids:
                    if taxes.ids[0] in obj_taxes.ids:
                        iva_amount += lines.price_subtotal * percent / 100

        self.iva_amount = iva_amount

    @api.constrains('line_ids','invoice_line_ids')
    def _check_line_ids(self):
        for record in self:
            for lines in record.line_ids:
                if lines.required_partner and not lines.partner_id:
                    raise ValidationError(_(str(lines.ref)+' - La cuenta "' + lines.account_id.name + '" obliga un tercero y este no ha sido digitado. Por favor verifique!'))

                if lines.required_analytic_account and not lines.analytic_account_id and not record.stock_move_id.picking_id:
                    raise ValidationError(_(str(lines.ref)+' - La cuenta "' + lines.account_id.name + '" obliga cuenta analítica y esta no ha sido digitada. Por favor verifique!'))

            for lines in record.invoice_line_ids:
                if lines.required_partner and not lines.partner_id:
                    raise ValidationError(_(str(lines.ref)+' - La cuenta "' + lines.account_id.name + '" obliga un tercero y este no ha sido digitado. Por favor verifique!'))

                if lines.required_analytic_account and not lines.analytic_account_id and not record.stock_move_id.picking_id:
                    raise ValidationError(_(str(lines.ref)+' - La cuenta "' + lines.account_id.name + '" obliga cuenta analítica y esta no ha sido digitada. Por favor verifique!'))

    def get_xml(self):
        obj_xml = self.env['zue.xml.generator.header'].search([('code','=','FacElectronica_FacturaTech')])
        xml = obj_xml.xml_generator(self)

        filename = f'FE_{str(date.today().year)}_{self.name}_{str(self.partner_id.name)}.xml'
        self.write({
            'xml_file': base64.encodestring(xml),
            'xml_file_name': filename,
        })

        action = {
            'name': 'XMLFacturacionElectronicaFacturaTech',
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=account.move&id=" + str(
                self.id) + "&filename_field=xml_file_name&field=xml_file&download=true&filename=" + self.xml_file_name,
            'target': 'self',
        }

        return action

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

        code_position = -1
        status_code = 0
        error_msg = ''
        error_position = 0

        code_position = obj_result.find('</code>') - 3

        if code_position > -1:
            status_code = int(obj_result[code_position:code_position + 3])

            if status_code != 200:
                error_position = obj_result.find('<error xsi:type="xsd:string">') + len('<error xsi:type="xsd:string">')
                error_msg = obj_result[error_position:obj_result.find('</error>')]

                raise ValidationError(_("Error al realizar el envío! %s") % error_msg)

        return True
