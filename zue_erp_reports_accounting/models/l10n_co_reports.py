from odoo import api, fields, models
import pandas as pd
import json
import zipfile
import base64
from io import BytesIO


class RetentionReportWizard(models.TransientModel):
    _inherit = 'l10n_co_reports.retention_report.wizard'

    z_save_documents = fields.Boolean(string="Guardar en documentos")

    def generate_report(self):
        lst_lines = self.env.context.get('options').get('unfolded_lines')
        lst_lines_original = lst_lines.copy()
        lst_parents = []
        for lines in lst_lines_original:
            if lines:
                tmp_partner_id = int(str(lines.split('~')[2]).split('|')[0])
                obj_partner = self.env['res.partner'].search([('id','=',tmp_partner_id)],limit=1)
                if (lines,obj_partner.name,obj_partner.id) not in lst_parents:
                    lst_parents.append((lines,obj_partner.name,obj_partner.id))

        if self.env.context.get('options'):
            if self.env.context.get('options').get("available_variants"):
                rpt_name = self.env.context.get('options').get("available_variants")[0].get("name")
            else:
                rpt_name = 'Not_name_found'
        else:
            rpt_name = 'Not_name_found'

        if len(lst_parents) > 1:
            zip_buffer = BytesIO()
            filename = f'Certificados_ret_{rpt_name.replace(" ","_")}.zip'
            self.env['ir.attachment'].search([('res_model', '=', False), ('name', '=', filename)]).sudo().unlink()

            for parent in lst_parents:
            #     while len(list(set([x for x in lst_lines]) - set([parent[2],False]))) > 0:
            #         for lines in lst_lines:
            #             if tmp_partner_id and tmp_partner_id != parent[2]:
            #                 lst_lines.remove(lines)

                data = {
                    'wizard_values': self.read()[0],
                    'lines': lst_lines,
                    'report_name': rpt_name,
                }

                report = self.env.ref('l10n_co_reports.action_report_certification', False)
                pdf_content = report._render_qweb_pdf(report.id, data=data)

                with zipfile.ZipFile(zip_buffer, 'a') as zip_file:
                    # Agrega el archivo al zip
                    zip_file.writestr('CERTIFICACIÓN_RTE{}_{}.pdf'.format(rpt_name, parent[1]), pdf_content[0])

                #report = self.env.ref('l10n_co_reports.action_report_certification').report_action([], data=data)
                lst_lines = lst_lines_original.copy()

                #guardar en documentos
                if self.z_save_documents:
                    #crear en adjuntos
                    obj_attachment_cert = self.env['ir.attachment']
                    name = 'CERTIFICACIÓN_RTE{}_{}.pdf'.format(rpt_name.upper(), parent[1])
                    obj_attachment_cert = obj_attachment_cert.sudo().create({
                        'name': name,
                        'store_fname': name,
                        'res_name': name,
                        'type': 'binary',
                        'res_model': 'res.partner',
                        'res_id': parent[2] ,
                        'datas': base64.b64encode(pdf_content[0]),
                    })
                    # Asociar adjunto a documento de Odoo
                    doc_vals = {
                        'name': name,
                        'owner_id': self.env.user.id,
                        'partner_id': parent[2],
                        'folder_id': self.env.user.company_id.z_folder_retention_certificates_id.id,
                        #'tag_ids': self.env.user.company_id.z_validated_certificate.ids,
                        'type': 'binary',
                        'attachment_id': obj_attachment_cert.id
                    }
                    self.env['documents.document'].sudo().create(doc_vals)

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
                    'url': "web/content/?model=ir.attachment&id=" + str(
                        zip_attachment.id) + "&filename_field=name&field=datas&download=true&name=" + filename,
                    'target': 'self'
                }
        else:
            data = {
                'wizard_values': self.read()[0],
                'lines': lst_lines_original,
                'report_name': self.env.context.get('report_name'),
            }

            if self.z_save_documents:
                for parent in lst_parents:
                    report = self.env.ref('l10n_co_reports.action_report_certification', False)
                    pdf_content = report._render_qweb_pdf(report.id, data=data)
                    # crear en adjuntos
                    obj_attachment_cert = self.env['ir.attachment']
                    name = 'CERTIFICACIÓN_RTE{}_{}.pdf'.format(rpt_name.upper(), parent[1])
                    obj_attachment_cert = obj_attachment_cert.sudo().create({
                        'name': name,
                        'store_fname': name,
                        'res_name': name,
                        'type': 'binary',
                        'res_model': 'res.partner',
                        'res_id': parent[2],
                        'datas': base64.b64encode(pdf_content[0]),
                    })
                    # Asociar adjunto a documento de Odoo
                    doc_vals = {
                        'name': name,
                        'owner_id': self.env.user.id,
                        'partner_id': parent[2],
                        'folder_id': self.env.user.company_id.z_folder_retention_certificates_id.id,
                        # 'tag_ids': self.env.user.company_id.z_validated_certificate.ids,
                        'type': 'binary',
                        'attachment_id': obj_attachment_cert.id
                    }
                    self.env['documents.document'].sudo().create(doc_vals)

            return self.env.ref('l10n_co_reports.action_report_certification').report_action([], data=data)