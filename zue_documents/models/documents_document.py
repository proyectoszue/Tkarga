from odoo import fields, models, api

class documents_document(models.Model):
    _inherit = 'documents.document'

    expiration_date = fields.Date('Fecha de expiración')
    handler = fields.Char(string='handler')
    # Campos generando error en plantilla mal migrada por Odoo
    activity_note = fields.Html(string="Message")
    full_url = fields.Char(string="URL")
    date_deadline = fields.Date('Expected Closing')

    def get_formview_action(self, access_uid=None):
        # Enlace Many2one: misma carpeta del archivo + solo documentos del partner (empleado)
        self.ensure_one()
        # Sin partner no hay filtro de empleado; se deja el comportamiento estándar
        if not self.partner_id:
            return super().get_formview_action(access_uid=access_uid)
        action = self.env['ir.actions.actions']._for_xml_id('documents.document_action')
        return action | {
            'domain': [('partner_id', '=', self.partner_id.id)],
            'context': {
                'default_partner_id': self.partner_id.id,
                # Abre la misma carpeta del documento seleccionado
                'searchpanel_default_user_folder_id': str(self.folder_id.id) if self.folder_id else False,
            },
            'target': 'new',
        }
