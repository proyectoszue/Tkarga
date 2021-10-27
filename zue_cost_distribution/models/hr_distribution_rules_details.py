# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class hr_distribution_rules_details(models.Model):
    _name = 'hr.distribution.rules.details'
    _description = 'Reglas de distribución (detalles)'

    distribution_rules_id = fields.Many2one('hr.distribution.rules', 'Reglas de distribución')   
    analytical_account_destination_id = fields.Many2one('account.analytic.account', 'Cuenta analítica destino')
    percentage = fields.Float(string='Porcentaje')
    value = fields.Float(string='Valor')
