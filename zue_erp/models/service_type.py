from odoo import fields, models


class ZueServiceType(models.Model):
    _name = 'zue.service.type'
    _description = 'Tipos de servicio'
    _rec_name = 'z_name'

    z_name = fields.Char(string='Nombre')
