from odoo import fields, models, api, tools


class HrContractPublic(models.Model):
    _name = 'hr.contract.public' 
    _description = 'Vista de la tabla de contratos empleados'
    _auto = False
    _log_access = True

    id = fields.Integer(string='id')
    name = fields.Char(string='contrato')
    employee_id = fields.Many2one('hr.employee.public',string='Empleado')
    company_id = fields.Many2one('res.company',string='Compañia')
    state = fields.Char(string='Estado')
    date_start = fields.Date(string='Fecha inicio')
    job_id = fields.Many2one('hr.job',string='Cargo')
    wage = fields.Float(string='Salario')

    @api.model
    def _get_fields(self):
        return ','.join('contract.%s' % name for name, field in self._fields.items() if
                        field.store and field.type not in ['many2many', 'one2many'])

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
                SELECT
                    %s
                FROM hr_contract contract
            )""" % (self._table, self._get_fields()))

    def get_date_text(self,date,calculated_week=0):
        return self.sudo().env['hr.contract'].search([('id','=',self.id)]).get_date_text(date,calculated_week)

    def get_contract_type(self):
        return self.sudo().env['hr.contract'].search([('id','=',self.id)]).get_contract_type()

    def get_amount_text(self, valor):
        return self.sudo().env['hr.contract'].search([('id', '=', self.id)]).get_amount_text(valor)

    def get_amount_text(self, valor):
        return self.sudo().env['hr.contract'].search([('id', '=', self.id)]).get_amount_text(valor)

    def get_average_concept_heyrec(self):
        return self.sudo().env['hr.contract'].search([('id','=',self.id)]).get_average_concept_heyrec()

    def get_signature_certification(self):
        return self.sudo().env['hr.contract'].search([('id','=',self.id)]).get_signature_certification()

    def get_info_book_vacation(self):
        return self.sudo().env['hr.contract'].search([('id','=',self.id)]).get_info_book_vacation()
    
    def get_info_book_cesantias(self):
        return self.sudo().env['hr.contract'].search([('id','=',self.id)]).get_info_book_cesantias()

    def get_accumulated_vacation_days(self):
        return self.sudo().env['hr.contract'].search([('id','=',self.id)]).get_accumulated_vacation_days()

    def get_average_concept_certificate(self,salary_rule_id,last,average,z_value_contract,z_payment_frequency,z_view_in_certificate):
        return self.sudo().env['hr.contract'].search([('id','=',self.id)]).get_average_concept_certificate(salary_rule_id,last,average,z_value_contract,z_payment_frequency,z_view_in_certificate)