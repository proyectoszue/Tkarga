# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class hr_distribution_model(models.Model):
    _name = 'hr.distribution.model'
    _description = 'Modelo de distribición'

    model_type = fields.Selection([('S', 'Estático'),
                                ('D', 'Driver')        
                                ], string='Tipo de modelo', required=True)
    base = fields.Selection([('1', 'Proporción'),
                                ('2', 'Valores'),
                                ('3', 'Viajes'),
                                ('4', 'KM'),
                                ], string='Con base en', required=True)
    
    _sql_constraints = [('change_type_base_uniq', 'unique(model_type,base)', 'Ya existe este modelo de distribución, por favor verficar.')]
    
    def name_get(self):
        result = []
        for record in self:
            model_type = dict(self._fields['model_type'].selection).get(record.model_type)
            base = dict(self._fields['base'].selection).get(record.base)
            result.append((record.id, "{} con base en {}".format(model_type,base.lower())))
        return result
    
    @api.constrains('model_type','base')
    def _check_model(self):  
        for record in self:
            if record.model_type == 'D' and record.base in ['1','2']:
                raise UserError(_('El tipo de modelo Driver no puede tener la base seleccionada'))  
            if record.model_type == 'S' and record.base in ['3','4']:
                raise UserError(_('El tipo de modelo Estático no puede tener la base seleccionada'))  