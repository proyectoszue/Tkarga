# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

class mntc_symptoms(models.Model):
    _name = 'mntc.symptoms'
    _description = 'Síntomas'

    code        = fields.Char('Code', size=4, required=True)
    name        = fields.Char(string='Name', required=True)
    system_ids  = fields.Many2many('mntc.vehicle.system',string='Sistemas')
    # active      = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('code', 'UNIQUE (code)', 'You can not have two users with the same name !')
    ]

    @api.depends('code','name')
    def _get_complete_name(self):
        for record in self:
            display_name =''
            if record.name:
                display_name += record.name        
            if record.name:
                display_name += ' ('+record.code+')'
            record.name= display_name

class mntc_vehicle_system(models.Model): 
    _name = 'mntc.vehicle.system'
    _description = 'Sistema de vehículo'

    initials = fields.Char('Initials', size=4,required=True)
    name     = fields.Char('Name',required=True)
    component_ids =  fields.Many2many('mntc.component',string='Componentes')
    
    _sql_constraints = [
        ('initials', 'UNIQUE (initials)', 'You can not have two users with the same name !')
    ]

    @api.onchange('initials')
    @api.depends('name', 'initials')
    def _get_complete_name(self):
        for record in self:
            display_name = ''
            if record.name:
                display_name += record.name
            if record.initials:
                display_name += ' (' + record.initials + ')'
            record.name = display_name        

class mntc_workforce_type_time(models.Model):
    _name = 'mntc.workforce.type.time'
    _description = 'Tiempos de la disciplina'

    workforce_type_id = fields.Many2one('mntc.workforce.type', 'Disciplina')
    estimated_time = fields.Float('Tiempo estimado disciplina')
    
class mntc_workforce_type(models.Model):
    _name = 'mntc.workforce.type'
    _description = 'Disciplinas'

    name = fields.Char(string='Name',store=True)
    code = fields.Char('Code', size=4, required=True)
    description = fields.Text('Description',required=True)
    active      = fields.Boolean('Active', default=True) 
    estimated_time = fields.Float('Tiempo estimado disciplina')
    
    _sql_constraints = [
        ('code', 'UNIQUE (code)', 'You can not have two users with the same name !')
    ]

    @api.onchange('code')
    @api.depends('code', 'description')
    def _get_complete_name(self):
        for record in self:
            display_name = ''
            if record.description:
                display_name += record.description
            if record.code:
                display_name += ' (' + record.code + ')'
            record.name = display_name        


class mntc_workforce_type_rh(models.Model):
    _name = 'mntc.workforce.type.rh' 
    _description = 'Recurso humano de tipo de trabajo' 

    name = fields.Char(string='Nombre',store=True)
    code = fields.Char('Código', size=4, readonly=True)
    description = fields.Text('Descripción', readonly=True)
    active      = fields.Boolean('Activo', default=True)  
    task_id = fields.Many2one('mntc.tasks', string='Tarea')
    start_programmed_date = fields.Datetime('Fecha estimada inicio')
    end_programmed_date = fields.Datetime('Fecha estimada finalización') 
    programmed_time = fields.Float(string='Tiempo estimado')
    workforce_type_id = fields.Many2one('mntc.workforce.type','Disciplina') 

    @api.onchange('workforce_type_id')  
    def workforce_type_change(self):
        self.name = self.workforce_type_id.name
        self.code = self.workforce_type_id.code
        self.description = self.workforce_type_id.description
        self.active = self.workforce_type_id.active
        self.programmed_time = self.workforce_type_id.estimated_time

class mntc_executed_workforce_type_rh(models.Model):
    _name = 'mntc.executed.workforce.type.rh'
    _description = 'Recurso humano ejecutado del tipo de trabajo'

    name = fields.Char(string='Nombre',store=True)
    code = fields.Char('Código', size=4, readonly=True)
    description = fields.Text('Descripción', readonly=True)
    active      = fields.Boolean('Activo', default=True)  
    task_id = fields.Many2one('mntc.tasks', string='Tarea')
    technician_id = fields.Many2one('mntc.technician', string='Técnico', domain=[('employee_id', '!=', False)])
    start_executed_date = fields.Datetime('Fecha inicio ejecución')
    end_executed_date = fields.Datetime('Fecha fin ejecución')
    spent_time = fields.Float(string='Tiempo gastado')
    workforce_type_id = fields.Many2one('mntc.workforce.type','Disciplina')
    res_partner_id = fields.Many2one('res.partner', string='Proveedor')

    @api.onchange('workforce_type_id')  
    def workforce_type_change(self):
        self.name = self.workforce_type_id.name
        self.code = self.workforce_type_id.code
        self.description = self.workforce_type_id.description
        self.active = self.workforce_type_id.active
        self.spent_time = self.workforce_type_id.estimated_time

    @api.onchange('technician_id')  
    def technician_id_change(self):
        if self.technician_id:
            self.workforce_type_id = self.technician_id.workforce_type_id.id
            self.res_partner_id = None

    @api.onchange('res_partner_id')  
    def res_partner_id_change(self):
        if self.res_partner_id:
            self.technician_id = None

class mntc_base_symptoms(models.Model):
    _name = 'mntc.base.symptoms'
    _description = 'Síntomas base'

    name = fields.Char(string='Name')        