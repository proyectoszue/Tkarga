from odoo import models, fields, api

class mntc_documents_types(models.Model):
    _name = 'mntc.documents.types'
    _description = 'Tipos de documentos'

    name = fields.Char('Name')
    format_code = fields.Char('Format code', size=35)
    version_code = fields.Char('Version code', size=15)