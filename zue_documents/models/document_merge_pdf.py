# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools import pdf, split_every
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter
import os
import io
import base64

class document_report_merge_pdf(models.TransientModel):
    _name = 'document.report.merge.pdf'
    _description = 'Reporte documentos - Unir PDFs'

    domain_documents = fields.Char(string='Filtro documentos')
    document_ids = fields.One2many('document.report.merge.pdf.documents','report_id',string='Documentos')
    order_fields = fields.Many2many('ir.model.fields', domain="[('model', '=', 'documents.document'),('ttype', 'not in', ['many2many','one2many','text','binary'])]",string='Campos para ordenar')
    save_favorite = fields.Boolean(string='Guardar como favorito')
    name = fields.Char(string='Nombre')
    favorite_id = fields.Many2one('document.report.merge.pdf.favorites',string='Favorito')
    pdf_file = fields.Binary('PDF file')
    pdf_file_name = fields.Char('PDF name')

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "Unir PDFs"))
        return result

    @api.onchange('domain_documents','order_fields')
    def load_documents(self):
        for record in self:
            record.document_ids = False
            domain = []
            domain_documents_obligatory = str([['mimetype', 'like', 'pdf']])
            domain += safe_eval(domain_documents_obligatory)
            if record.domain_documents:
                domain += safe_eval(record.domain_documents)
                lst_order = ['partner_id']
                if len(record.order_fields) > 0:
                    for field in record.order_fields:
                        if field.name not in lst_order:
                            lst_order.append(field.name)
                str_order = ','.join(map(str, lst_order))
                obj_document = self.env['documents.document'].search(domain,order=str_order)
                i = 1
                lst_documents = []
                for document in obj_document:
                    vals = {
                        #'report_id':record.id,
                        'sequence':i,
                        'partner_id':document.partner_id.id if document.partner_id else False,
                        'document_id':document.id,
                    }
                    lst_documents.append((0,0,vals))
                    #self.env['document.report.merge.pdf.documents'].create(vals)
                    i += 1
                record.document_ids = lst_documents

    def generate_pdf(self):
        #Guardar favorito si el check estaba marcado
        if self.save_favorite:
            self.save_favorite_process()
        if not self.domain_documents:
            raise ValidationError(_("Debe seleccionar filtros, por favor verificar."))
        #Variables
        report_personal_data = self.env['ir.actions.report'].search(
            [('report_name', '=', 'zue_documents.report_merge_pdf'),
             ('report_file', '=', 'zue_documents.report_merge_pdf')])
        files_to_merge = []
        filename = 'Documentos_merge.pdf'
        file_merger = PdfFileMerger()
        #Obtener PDFs
        for item in sorted(self.document_ids, key=lambda x: x.sequence):
            document = item.document_id
            if document.mimetype.find('pdf') == -1:
                raise ValidationError(_("Ahí un archivo que que no es formato PDF, por favor verificar."))
            files_to_merge.append((document.partner_id.name if document.partner_id else '',document.name,document.attachment_id.raw))
        #Unir Pdfs
        writer = PdfFileWriter()
        for file in files_to_merge:
            try:
                reader = PdfFileReader(io.BytesIO(file[2]), strict=False, overwriteWarnings=False)
                writer.appendPagesFromReader(reader)
            except Exception as e:
                msg_error = 'Contacto: %s \nDocumento: %s \n Error: %s' % (file[0],file[1], e)
                raise ValidationError(_(msg_error))
        result_stream = io.BytesIO()
        writer.write(result_stream)
        #Guardar pdf
        self.write({
            'pdf_file': base64.encodestring(result_stream.getvalue()),
            'pdf_file_name': filename,
        })
        #Descargar reporte
        action = {
            'name': 'Documentos_merge',
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=document.report.merge.pdf&id=" + str(
                self.id) + "&filename_field=pdf_file_name&field=pdf_file&download=true&filename=" + self.pdf_file_name,
            'target': 'self',
        }
        return action

    def save_favorite_process(self):
        if not self.name:
            raise ValidationError(_("Debe digitar un nombre para guardar como favorito."))
        if not self.domain_documents:
            raise ValidationError(_("Debe seleccionar un filtro para guardar como favorito."))
        vals = {
            'name': self.name,
            'domain_documents':self.domain_documents,
        }
        self.env['document.report.merge.pdf.favorites'].create(vals)

    @api.onchange('favorite_id')
    def load_favorite_process(self):
        if self.favorite_id:
            self.domain_documents = self.favorite_id.domain_documents

class document_report_merge_pdf_documents(models.TransientModel):
    _name = 'document.report.merge.pdf.documents'
    _description = 'Reporte documentos - Unir PDFs - documentos'
    _order = 'sequence'

    report_id = fields.Many2one('document.report.merge.pdf',string='Reporte', required=True)
    sequence = fields.Integer(string='Secuencia', required=True)
    partner_id = fields.Many2one('res.partner', string='Contacto')
    document_id = fields.Many2one('documents.document', string='Documento', required=True)
    folder_id = fields.Many2one(related='document_id.folder_id',string='Espacio de trabajo')
    tag_ids = fields.Many2many(related='document_id.tag_ids',string='Categorías')

class document_report_merge_pdf_favorites(models.Model):
    _name = 'document.report.merge.pdf.favorites'
    _description = 'Reporte documentos - Unir PDFs - favoritos'

    name = fields.Char(string='Nombre')
    domain_documents = fields.Char(string='Filtro documentos')

    _sql_constraints = [('report_merge_pdf_uniq', 'unique(name)',
                         'Ya existe un favorito con este nombre, por favor verificar.')]