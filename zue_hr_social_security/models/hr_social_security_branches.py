from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError
import time

class hr_social_security_branches(models.Model):
    _name = 'hr.social.security.branches'
    _description = 'Sucursales seguridad social'

    code = fields.Char('Codigo', size=10, required=True)
    name = fields.Char('Nombre', size=40, required=True)    

    _sql_constraints = [('change_code_uniq', 'unique(code)', 'Ya existe una sucursal de seguridad social con este código, por favor verificar')]         

class hr_social_security_work_center(models.Model):
    _name = 'hr.social.security.work.center'
    _description = 'Centro de trabajo seguridad social'

    code = fields.Integer('Codigo', size=9, required=True)
    name = fields.Char('Nombre', size=40, required=True)    
    branch_social_security_id = fields.Many2one('hr.social.security.branches', 'Sucursal seguridad social', required=True)

    _sql_constraints = [('change_code_uniq', 'unique(code)', 'Ya existe un centro de trabajo de seguridad social con este código, por favor verificar')]         