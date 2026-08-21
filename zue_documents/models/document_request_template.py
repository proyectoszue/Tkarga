from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import fields, models
from odoo.exceptions import ValidationError
from odoo.tools.misc import clean_context

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
    folder_id = fields.Many2one('documents.document', string="Espacio de trabajo",required=True)
    tags_ids  = fields.Many2many('documents.tag',string="Categoria")

class documents_request_template_wizard(models.TransientModel):
    _name = "documents.request.template_wizard"
    _description = "Plantilla de solicitud wizard"

    template_id = fields.Many2one('document.request.template', string="Plantilla")
    owner_id = fields.Many2one('res.users', required=True, string="Solicitud de")
    partner_id = fields.Many2one('res.partner', string="Contacto")

    activity_type_id = fields.Many2one('mail.activity.type',
                                        string="Tipo de actividad",
                                        default=lambda self: self.env.ref('mail.mail_activity_data_upload_document',
                                        raise_if_not_found=False),
                                        required=True,
                                        domain="[('category', '=', 'upload_file')]")
    res_model = fields.Char('Modelo del recurso')
    res_id = fields.Integer('ID del recurso')

    activity_note = fields.Html(string="Nota")
    activity_date_deadline_range = fields.Integer(string='Fecha de vencimiento (duracion)', default=30)
    activity_date_deadline_range_type = fields.Selection(
        [('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months')],
        string='Fecha de vencimiento (tiempo)',
        default='days',
    )

    def request_document(self):
        self.ensure_one()
        if not self.template_id.detail_ids:
            raise ValidationError("La plantilla seleccionada no tiene documentos a solicitar, por favor verificar.")
        if not self.owner_id.partner_id:
            raise ValidationError("El usuario seleccionado no tiene un contacto asociado, por favor verificar.")

        documents_by_folder = {}
        requestee_partner = self.owner_id.partner_id
        for detail in self.template_id.detail_ids:
            request_vals = {
                'name': detail.name,
                'folder_id': detail.folder_id.id if detail.folder_id else False,
                'tag_ids': [(6, 0, detail.tags_ids.ids)] if detail.tags_ids else [],
                'requestee_id': requestee_partner.id,
                'partner_id': self.partner_id.id if self.partner_id else False,
                'activity_type_id': self.activity_type_id.id,
                'res_model': self.res_model,
                'res_id': self.res_id,
                'activity_note': self.activity_note,
                'activity_date_deadline_range': self.activity_date_deadline_range,
                'activity_date_deadline_range_type': self.activity_date_deadline_range_type,
            }
            request_wizard = self.env['documents.request_wizard'].create(request_vals)
            requested_document = request_wizard.request_document(not_share=1 if self.partner_id else 0)
            folder_id = detail.folder_id.id if detail.folder_id else False
            documents_by_folder.setdefault(folder_id, []).append(requested_document.id)

        if self.partner_id:
            for document_ids in documents_by_folder.values():
                share_action = self.env['documents.sharing'].action_open(document_ids)
                share = self.env['documents.sharing'].browse(share_action['res_id'])
                share.write({
                    'invite_partner_ids': [(6, 0, [self.partner_id.id])],
                    'invite_role': 'edit',
                    'invite_notify': True,
                    'invite_notify_message': self.activity_note or False,
                })
                share.action_invite_members()

        return {'type': 'ir.actions.act_window_close'}


class RequestWizard(models.TransientModel):
    _inherit = "documents.request_wizard"

    def request_document(self, not_share=0):
        self.ensure_one()
        document = self.env['documents.document'].create({
            'name': self.name,
            'folder_id': self.folder_id.id,
            'tag_ids': [(6, 0, self.tag_ids.ids if self.tag_ids else [])],
            'partner_id': self.partner_id.id if self.partner_id else False,
            'requestee_partner_id': self.requestee_id.id,
            'res_model': self.res_model,
            'res_id': self.res_id,
        })

        activity_vals = {
            'user_id': self.requestee_id.user_ids[0].id if self.requestee_id.user_ids else self.env.user.id,
            'note': self.activity_note,
            'activity_type_id': self.activity_type_id.id if self.activity_type_id else False,
            'summary': self.name,
        }
        if self.activity_date_deadline_range > 0:
            activity_vals['date_deadline'] = fields.Date.context_today(self) + relativedelta(
                **{self.activity_date_deadline_range_type: self.activity_date_deadline_range}
            )

        request_by_mail = self.requestee_id and self.create_uid not in self.requestee_id.user_ids
        activity = document.with_context(mail_activity_quick_update=request_by_mail).activity_schedule(**activity_vals)
        document.request_activity_id = activity

        if self.requestee_id.user_ids:
            document.action_update_access_rights('none', partners={
                self.env.user.partner_id.id: ('edit', False),
                self.requestee_id.id: ('edit', datetime.combine(activity.date_deadline, datetime.max.time())),
            })
        else:
            document.access_via_link = 'edit'
            document.action_update_access_rights('none', partners={
                self.env.user.partner_id.id: ('edit', False),
            })

        if not not_share:
            request_template = self.env.ref('documents.mail_template_document_request', raise_if_not_found=False)
            if request_template:
                document.with_context(clean_context(self.env.context)).message_mail_with_source(request_template)

        return document
