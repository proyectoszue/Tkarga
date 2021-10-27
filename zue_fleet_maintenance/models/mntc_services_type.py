from odoo import fields,models
from datetime import datetime, timedelta

class mntc_services_type(models.Model):
    _name = 'mntc.services.type'
    _description = 'Tipos de servicio'

    name = fields.Char('Name',required=True)
    code = fields.Char('Code' , size=4,required=True)
    margin = fields.Integer('Margin',required=True, size=4)
    # account_analytic_x_service_type_ids = fields.One2many('mntc.account.analytic.x.service.type', 'service_type_id', string='account analytic x service type')

    _sql_constraints = [
        ('code', 'UNIQUE (code)', 'You can not have two users with the same name !')
    ]

class mntc_account_analytic_x_service_type(models.Model):
    _name = 'mntc.account.analytic.x.service.type'
    _description = 'Cuenta analítica por tipo de servicio'

    service_type_id = fields.Many2one('mntc.services.type', string='Service type')
    reference_account_analytic = fields.Char(string='Reference account analytic')
    in_the_charge_of = fields.Many2one('res.partner', string='Asignado a') # ,domain="[('is_work_place', '=', True)]"

class mntc_location_dest(models.Model):
    _name = 'mntc.location.dest'
    _description = 'Sucursal destino'

    spare_part_company_id = fields.Many2one('res.partner', string='Spare part company') #,domain="[('is_work_place', '=', True)]"
    inventory_company_id = fields.Many2one('res.partner', string='Inventory company') #,domain="[('is_work_place', '=', True)]"
    location_dest_name = fields.Char(string='Location dest name')