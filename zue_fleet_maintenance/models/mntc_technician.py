from odoo import models, fields, api, _ 
from datetime import datetime, timedelta


class mntc_technician(models.Model):
    _name = 'mntc.technician'
    _description = 'Tecnicos'

    name                = fields.Char('Name')
    employee_id         = fields.Many2one('hr.employee','Employee')
    supplier_id         = fields.Many2one('res.partner', 'Supplier')
    workforce_type_id   = fields.Many2one('mntc.workforce.type', 'Workforce type',required=True)
    garage_id = fields.Many2many('mntc.garage',string='Garage',required=True)
    employee_supplier = fields.Selection([('emp_sup_1', 'Employee'), ('emp_sup_2', 'Supplier')], 'employee/supplier', default='emp_sup_1',required=True)

    _sql_constraints = [
        ('employee_id', 'UNIQUE (employee_id)', 'You can not have two employee with the same name !'),
        ('supplier_id', 'UNIQUE (supplier_id)', 'You can not have two supplier with the same name !')
    ]

    @api.onchange('employee_id')
    def mntc_employee_id_onchange(self):
        if self.employee_id:
            self.name = self.employee_id.name
            self.supplier_id =False


    @api.onchange('supplier_id')
    def mntc_supplier_id_onchange(self):
        if self.supplier_id:
            self.name = self.supplier_id.name
            self.employee_id = False

    def name_get(self):
        result = []
        for record in self:
            name = record.name
            if not name:
                name = record.employee_id.name if record.employee_id else record.supplier_id.name
            result.append((record.id, "{}".format(name)))
        return result


class mntc_garage(models.Model):
    _name = 'mntc.garage'
    _description = 'Talleres del vehiculo'

    display_name= fields.Char(compute="_get_complete_name", string='Display Name',store=True)
    name        = fields.Char('Name',required=True)
    code        = fields.Char('code' , size=4,required=True)
    branch_id    = fields.Many2one('zue.res.branch', 'Sucursal',required=True)
    location = fields.One2many('mntc.location','garage_id' , string = 'Location')
    stock_location_id = fields.Many2one('stock.location', string='Stock location', company_dependent=True, domain="[('usage','=','internal')]")
    time_value = fields.Float('Time value', required=True)
    _sql_constraints = [
        ('code', 'UNIQUE (code)', 'You can not have two users with the same name !')
    ]

    @api.onchange('code')
    @api.depends('code', 'name')
    def _get_complete_name(self):
        display_name = ''
        if self.name:
            display_name += self.name
        if self.code:
            display_name += ' (' + self.code + ')'
        self.display_name = display_name

    @api.model
    def create(self, vals):
        if 'code' in vals:
            self.create_sequence(vals, 'SO')
            self.create_sequence(vals, 'EM')
            self.create_sequence(vals, 'OT')
        return super(mntc_garage, self).create(vals)


    def write(self, vals):
        if 'code'in vals:
            self.create_sequence(vals, 'SO')
            self.create_sequence(vals, 'EM')
            self.create_sequence(vals, 'OT')
        return super(mntc_garage, self).write(vals)

    # @api.model
    # def create_sequence_tipe(self, vals,tipe_sequence):
    #     prefix = vals['code']
    #     seq = {
    #                     'name':tipe_sequence+"-" + prefix,
    #                     'code': "mntc_"+tipe_sequence+"-" + prefix,
    #                 }
    #     if 'company_id' in vals:
    #                     seq['company_id'] = vals['company_id']
    #     return self.env['ir.sequence.type'].create(seq)

    @api.model
    def create_sequence(self, vals,tipe_sequence):
        prefix = vals['code'].upper()
        code = "mntc_" + tipe_sequence + "-" + prefix
        # found_sequence = self.env['ir.sequence.type'].search([('code', '=', "mntc_"+tipe_sequence+"-" + prefix)])

        # if found_sequence:
        #     seq = {
        #         'name': tipe_sequence + vals['name'],
        #         'prefix': tipe_sequence + "-" + prefix + "%(y)s%(month)s-",
        #         'code': found_sequence.code,
        #     }
        #     return found_sequence.write(seq)
        # else:

        # id_sequence_type = self.create_sequence_tipe(vals, tipe_sequence)
        seq = {
            'name': tipe_sequence + vals['name'],
            'implementation': 'no_gap',
            'prefix': tipe_sequence + "-" + prefix + "%(y)s%(month)s-",
            'padding': 3,
            'code': code,
            'number_increment': 1
        }
        if 'company_id' in vals:
            seq['company_id'] = vals['company_id']

        return self.env['ir.sequence'].create(seq)

class mntc_location(models.Model):
    _name = 'mntc.location'
    _description = 'MNTC Locaciones'

    name            = fields.Char('Name',required=True)
    location_code   = fields.Char('code' , size=4,required=True)
    location_type   = fields.Selection([('location_1', 'Taller'), ('location_2', 'Otro Taller'),('location_3', 'En camino')],'Location', default='location_3',required=True)
    garage_id       = fields.Many2one('mntc.garage', 'Garage')
    _sql_constraints = [
        ('location_code', 'UNIQUE (location_code)', 'You can not have two users with the same name !')
    ]
