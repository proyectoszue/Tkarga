from odoo import fields, models, api

class documents_document(models.Model):
    _inherit = 'documents.document'

    expiration_date = fields.Date('Fecha de expiración')