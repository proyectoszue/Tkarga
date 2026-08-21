# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import pdf
from odoo.tools.safe_eval import safe_eval
import base64


class document_report_merge_pdf(models.TransientModel):
    _name = 'document.report.merge.pdf'
    _description = 'Reporte documentos - Unir PDFs'

    domain_documents = fields.Char(string='Filtro documentos')
    document_ids = fields.One2many('document.report.merge.pdf.documents', 'report_id', string='Documentos')
    order_fields = fields.Many2many(
        'ir.model.fields',
        domain="[('model', '=', 'documents.document'),('ttype', 'not in', ['many2many','one2many','text','binary'])]",
        string='Campos para ordenar',
    )
    save_favorite = fields.Boolean(string='Guardar como favorito')
    name = fields.Char(string='Nombre')
    favorite_id = fields.Many2one('document.report.merge.pdf.favorites', string='Favorito')
    pdf_file = fields.Binary('PDF file')
    pdf_file_name = fields.Char('PDF name')

    def _compute_display_name(self):
        for record in self:
            record.display_name = "Unir PDFs"

    @api.onchange('domain_documents', 'order_fields')
    def load_documents(self):
        for record in self:
            record.document_ids = False
            domain = safe_eval(str([['mimetype', 'like', 'pdf']]))
            if record.domain_documents:
                domain += safe_eval(record.domain_documents)
                lst_order = ['partner_id']
                for field in record.order_fields:
                    if field.name not in lst_order:
                        lst_order.append(field.name)
                obj_document = self.env['documents.document'].search(domain, order=','.join(lst_order))
                lst_documents = []
                for index, document in enumerate(obj_document, start=1):
                    lst_documents.append((0, 0, {
                        'sequence': index,
                        'partner_id': document.partner_id.id if document.partner_id else False,
                        'document_id': document.id,
                    }))
                record.document_ids = lst_documents

    def generate_pdf(self):
        if self.save_favorite:
            self.save_favorite_process()
        if not self.domain_documents:
            raise ValidationError(_("Debe seleccionar filtros, por favor verificar."))

        files_to_merge = []
        for item in sorted(self.document_ids, key=lambda x: x.sequence):
            document = item.document_id
            if 'pdf' not in (document.mimetype or ''):
                raise ValidationError(_("Hay un archivo que no es formato PDF, por favor verificar."))
            if not document.attachment_id or not document.attachment_id.raw:
                raise ValidationError(_("El documento %s no tiene archivo adjunto para fusionar.") % document.name)
            files_to_merge.append(document.attachment_id.raw)

        try:
            merged_pdf = pdf.merge_pdf(files_to_merge)
        except Exception as error:
            raise ValidationError(_("No fue posible fusionar los PDF seleccionados. Error: %s") % error)

        self.write({
            'pdf_file': base64.b64encode(merged_pdf),
            'pdf_file_name': 'Documentos_merge.pdf',
        })
        return {
            'name': 'Documentos_merge',
            'type': 'ir.actions.act_url',
            'url': (
                "web/content/?model=document.report.merge.pdf&id="
                + str(self.id)
                + "&filename_field=pdf_file_name&field=pdf_file&download=true&filename="
                + self.pdf_file_name
            ),
            'target': 'self',
        }

    def save_favorite_process(self):
        if not self.name:
            raise ValidationError(_("Debe digitar un nombre para guardar como favorito."))
        if not self.domain_documents:
            raise ValidationError(_("Debe seleccionar un filtro para guardar como favorito."))
        self.env['document.report.merge.pdf.favorites'].create({
            'name': self.name,
            'domain_documents': self.domain_documents,
        })

    @api.onchange('favorite_id')
    def load_favorite_process(self):
        if self.favorite_id:
            self.domain_documents = self.favorite_id.domain_documents


class document_report_merge_pdf_documents(models.TransientModel):
    _name = 'document.report.merge.pdf.documents'
    _description = 'Reporte documentos - Unir PDFs - documentos'
    _order = 'sequence'

    report_id = fields.Many2one('document.report.merge.pdf', string='Reporte', required=True)
    sequence = fields.Integer(string='Secuencia', required=True)
    partner_id = fields.Many2one('res.partner', string='Contacto')
    document_id = fields.Many2one('documents.document', string='Documento', required=True)
    folder_id = fields.Many2one(related='document_id.folder_id', string='Espacio de trabajo')
    tag_ids = fields.Many2many(related='document_id.tag_ids', string='Categorias')


class document_report_merge_pdf_favorites(models.Model):
    _name = 'document.report.merge.pdf.favorites'
    _description = 'Reporte documentos - Unir PDFs - favoritos'

    name = fields.Char(string='Nombre')
    domain_documents = fields.Char(string='Filtro documentos')

    _report_merge_pdf_uniq = models.Constraint(
        'unique(name)',
        'Ya existe un favorito con este nombre, por favor verificar.',
    )
