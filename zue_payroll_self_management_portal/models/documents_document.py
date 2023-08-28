from odoo import fields, models, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone

class documents_document(models.Model):
    _inherit = 'documents.document'

    z_expired_document = fields.Boolean(string='Documento expirado', compute='_compute_expired_documents', store=True)
    z_to_expired_document = fields.Boolean(string='Documento por expirar', compute='_compute_expired_documents', store=True)

    @api.depends('partner_id')
    def _compute_expired_documents(self):
        for document in self:
            # Verificar documentos expirados
            datetime_today = datetime.now()
            if document.expiration_date and document.type != 'empty':
                equivalent_documents = self.env['documents.document']
                for tag in document.tag_ids:
                    equivalent_documents += self.env['documents.document'].search(
                        [('partner_id', '=', document.partner_id.id),
                         ('tag_ids', 'in', tag.id),
                         '|', ('expiration_date', '=', False),
                         ('expiration_date', '>', document.expiration_date)])
                if document.expiration_date < datetime_today.date() and len(equivalent_documents) == 0:
                    document.z_expired_document = True
                    document.z_to_expired_document = False
                else:
                    if (document.expiration_date - datetime_today.date()).days <= 14 and len(equivalent_documents) == 0:
                        document.z_expired_document = False
                        document.z_to_expired_document = True
                    else:
                        document.z_expired_document = False
                        document.z_to_expired_document = False
            else:
                document.z_expired_document = False
                document.z_to_expired_document = False
