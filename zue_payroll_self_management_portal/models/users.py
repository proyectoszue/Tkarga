from odoo import models, fields, api

class res_users(models.Model):
    _inherit = 'res.users'

    portal_role = fields.Selection([('admin', 'Administrador'),('coordinator', 'Coordinador'),('user', 'Usuario')], string='Rol del portal')
