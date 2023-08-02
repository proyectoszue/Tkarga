from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

class document_request_template(models.Model):
    _name = 'document.request.template'
    _description = "Plantilla de solicitud documentos"

    name = fields.Char('Nombre de la plantilla',required=True)
    detail_ids = fields.One2many('document.request.template.detail','document_request_template_id',string="Plantilla solicitud de documentos")


class document_request_template_detail(models.Model):
    _name = 'document.request.template.detail'
    _description = "Plantilla de solicitud detalle"

    document_request_template_id = fields.Many2one('document.request.template',string="Plantilla solicitud de documentos",required=True)
    name = fields.Char('Nombre del documento',required=True)
    folder_id = fields.Many2one('documents.folder', string="Espacio de trabajo",required=True)
    tags_ids  = fields.Many2many('documents.tag',string="Categoria")

class documents_request_template_wizard(models.TransientModel):
    _name = "documents.request.template_wizard"
    _description = "Plantilla de solicitud wizard"

    template_id = fields.Many2one('document.request.template', string="Plantilla")
    owner_id = fields.Many2one('res.users', required=True, string="Solicitud de")
    partner_id = fields.Many2one('res.partner', string="Contacto")

    activity_type_id = fields.Many2one('mail.activity.type',
                                       string="Tipo de actividad",
                                       default=lambda self: self.env.ref('documents.mail_documents_activity_data_md',
                                                                         raise_if_not_found=False),
                                       required=True,
                                       domain="[('category', '=', 'upload_file')]")
    res_model = fields.Char('Modelo del recurso')
    res_id = fields.Integer('ID del recurso')

    activity_note = fields.Html(string="Nota")
    activity_date_deadline_range = fields.Integer(string='Fecha de vencimiento (duración)', default=30)
    activity_date_deadline_range_type = fields.Selection([
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
    ], string='Fecha de vencimiento (tiempo)', default='days')


    def request_document(self):
        if len(self.template_id.detail_ids) == 0:
            raise ValidationError(("La plantilla seleccionada no tiene documentos a solicitar, por favor verificar."))

        document_ids = []
        folder_ids = []

        for document in self.template_id.detail_ids:
            request_document = {
                'name':document.name,
                'folder_id':document.folder_id.id if document.folder_id else False,
                'tag_ids':document.tags_ids.ids if len(document.tags_ids) > 0 else [],
                'owner_id': self.owner_id.id,
                'partner_id': self.partner_id.id,
                'activity_type_id': self.activity_type_id.id,
                'res_model': self.res_model,
                'res_id': self.res_id,
                'activity_note': self.activity_note,
                'activity_date_deadline_range': self.activity_date_deadline_range,
                'activity_date_deadline_range_type': self.activity_date_deadline_range_type,
            }
            obj_requestdocument = self.env['documents.request_wizard'].create(request_document)
            document_r = obj_requestdocument.request_document(not_share=1)
            folder_ids.append(document.folder_id.id if document.folder_id else False)
            document_ids.append({'document_id': document_r.id, 'folder_id': document.folder_id.id if document.folder_id else False})

        if len(document_ids) > 0 and len(folder_ids) > 0:
            folder_ids = list(set(folder_ids))
            cant_folders = len(folder_ids)
            cont = 1
            for folder in folder_ids:
                document_ids_email = []
                for id in document_ids:
                    if id.get('folder_id', 0) == folder:
                        document_ids_email.append(id.get('document_id', False))

                name_share = self.template_id.name if cant_folders == 1 else self.template_id.name + ' Parte #' + str(
                    cont)
                share_vals = {
                    'name': name_share,
                    'type': 'ids',
                    'folder_id': folder,
                    'partner_id': self.partner_id.id,
                    'owner_id': self.owner_id.id,
                    'document_ids': document_ids_email,
                    # 'activity_note': self.activity_note,
                }
                share = self.env['documents.share'].create(share_vals)
                # Enviar correo
                share.send_share_by_mail('documents.mail_template_document_request')

                cont += 1

        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'reload',
        # }


class RequestWizard(models.TransientModel):
    _inherit = "documents.request_wizard"

    def request_document(self,not_share=0):
        self.ensure_one()
        document = self.env['documents.document'].create({
            'name': self.name,
            'type': 'empty',
            'folder_id': self.folder_id.id,
            'tag_ids': [(6, 0, self.tag_ids.ids if self.tag_ids else [])],
            'owner_id': self.env.user.id,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'res_model': self.res_model,
            'res_id': self.res_id,
        })

        # Setting the document owner is done as sudo as the user may lose access to that record
        # depending on the workspace's (folder) settings.
        # Subsequent actions on the document will also have to be done as sudo.
        if document.owner_id != self.owner_id:
            document = document.sudo()
            document.owner_id = self.owner_id

        activity_vals = {
            'user_id': self.owner_id.id if self.owner_id else self.env.user.id,
            'note': self.activity_note,
            'activity_type_id': self.activity_type_id.id if self.activity_type_id else False,
            'summary': self.name
        }

        deadline = None
        if self.activity_date_deadline_range > 0:
            activity_vals['date_deadline'] = deadline = fields.Date.context_today(self) + relativedelta(
                **{self.activity_date_deadline_range_type: self.activity_date_deadline_range})

        request_by_mail = self.owner_id and self.owner_id.id != self.create_uid.id
        if request_by_mail and not_share == 0:
            share_vals = {
                'name': self.name,
                'type': 'ids',
                'folder_id': self.folder_id.id,
                'partner_id': self.partner_id.id if self.partner_id else False,
                'owner_id': self.owner_id.id,
                'document_ids': [(4, document.id)],
                'activity_note': self.activity_note,
            }
            if deadline:
                share_vals['date_deadline'] = deadline
            share = self.env['documents.share'].create(share_vals)
            share.send_share_by_mail('documents.mail_template_document_request')

        activity = document.with_context(mail_activity_quick_update=request_by_mail).activity_schedule(**activity_vals)
        document.request_activity_id = activity
        return document