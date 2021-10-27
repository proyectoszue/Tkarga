# -*- coding: utf-8 -*-
from odoo import models, fields, api

class hr_employee(models.Model):
    _inherit = 'hr.employee'
    
    #Disciplina
    workforce_id = fields.Many2one('mntc.workforce.type', 'Disciplina', track_visibility='onchange')