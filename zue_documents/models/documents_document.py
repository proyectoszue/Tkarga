from odoo import fields, models, api

class documents_document(models.Model):
    _inherit = 'documents.document'

    expiration_date = fields.Date('Fecha de expiración')
    handler = fields.Char(string='handler')
    # Campos generando error en plantilla mal migrada por Odoo
    activity_note = fields.Html(string="Message")
    full_url = fields.Char(string="URL")
    date_deadline = fields.Date('Expected Closing')