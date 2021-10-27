# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
import datetime
_logger = logging.getLogger(__name__)

# CIUDAD
class Cities(models.Model):
    _name = 'zue.city'
    _description = 'Ciudades por departamento'

    state_id = fields.Many2one('res.country.state', string='Departamento', required=True)
    code = fields.Char(string='Código', size=10, required=True)
    name = fields.Char(string='Nombre', required=True)

#--------------------------------Modelos heredados de Odoo------------------------------------#

class ResCountry(models.Model):
    _inherit = 'res.country'
	
    x_code_dian = fields.Char(string='Código del país para la DIAN')

class ResCountryState(models.Model):
    _inherit = 'res.country.state'
	
    x_code_dian = fields.Char(string='Código de provincia/departamento para la DIAN')
