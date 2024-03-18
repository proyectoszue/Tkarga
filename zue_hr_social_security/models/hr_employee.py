# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    #Seguridad social - asignación
    branch_social_security_id = fields.Many2one('hr.social.security.branches', 'Sucursal seguridad social', tracking=True)
    work_center_social_security_id = fields.Many2one('hr.social.security.work.center', 'Centro de trabajo seguridad social', tracking=True)
    #Historico de seguridad social
    z_history_social_security_ids = fields.One2many('zue.hr.history.employee.social.security','z_employee_id',string='Historico de información seguridad social')

    def write(self, vals):
        save_history_social_security = False
        vals_history = {}
        if 'tipo_coti_id' in vals.keys() \
                or 'subtipo_coti_id' in vals.keys() \
                or 'branch_social_security_id' in vals.keys() \
                or 'work_center_social_security_id' in vals.keys() \
                or 'extranjero' in vals.keys() \
                or 'residente' in vals.keys() \
                or 'date_of_residence_abroad' in vals.keys() \
                or 'indicador_especial_id' in vals.keys():
            save_history_social_security = True
            for record in self:
                vals_history = {
                    'z_employee_id': record.id,
                    'z_date_change': fields.Date.today(),
                    'z_extranjero': record.extranjero,
                    'z_residente': record.residente,
                    'z_date_of_residence_abroad': record.date_of_residence_abroad,
                    'z_indicador_especial_id': record.indicador_especial_id.id,
                    'z_tipo_coti_id': record.tipo_coti_id.id,
                    'z_subtipo_coti_id': record.subtipo_coti_id.id,
                    'z_branch_social_security_id': record.branch_social_security_id.id,
                    'z_work_center_social_security_id': record.work_center_social_security_id.id,
                }
        res = super(hr_employee, self).write(vals)
        if save_history_social_security:
            self.env['zue.hr.history.employee.social.security'].create(vals_history)
        return res

class zue_hr_history_employee_social_security(models.Model):
    _name = 'zue.hr.history.employee.social.security'
    _description = 'Historico de información seguridad social empleado'

    z_employee_id = fields.Many2one('hr.employee', string='Empleado', required=True)
    z_date_change = fields.Date(string='Fecha cambio', required=True)
    z_extranjero = fields.Boolean('Extranjero', help='Extranjero no obligado a cotizar a pensión')
    z_residente = fields.Boolean('Residente en el Exterior', help='Colombiano residente en el exterior')
    z_date_of_residence_abroad = fields.Date(string='Fecha radicación en el exterior')
    z_indicador_especial_id = fields.Many2one('hr.indicador.especial.pila', 'Indicador tarifa especial pensiones')
    z_tipo_coti_id = fields.Many2one('hr.tipo.cotizante', string='Tipo de cotizante')
    z_subtipo_coti_id = fields.Many2one('hr.subtipo.cotizante', string='Subtipo de cotizante')
    z_branch_social_security_id = fields.Many2one('hr.social.security.branches', 'Sucursal seguridad social')
    z_work_center_social_security_id = fields.Many2one('hr.social.security.work.center','Centro de trabajo seguridad social')