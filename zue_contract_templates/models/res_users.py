# -*- coding: utf-8 -*-
from odoo import models, fields, api


class res_users(models.Model):
    _inherit = 'res.users'

    # Firma autorizada para certificado laboral
    z_signing_contracts = fields.Boolean('Firma autorizada para contratos')