from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date

class zue_suppliers_category(models.Model):
    _name = 'zue.suppliers.category'
    _description = 'Categoría proveedores'
    _rec_name = 'z_category'

    z_category = fields.Char(string='Categoría')
    z_description = fields.Char(string='Descripción')