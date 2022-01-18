from odoo import fields, models, api, tools


class HrPayslipWorkedDaysPublic(models.Model):
    _name = 'hr.payslip.line.public' 
    _description = 'Vista detalle nomina'
    _auto = False
    _log_access = True

    id = fields.Integer(string='id')
    name = fields.Char(string='Concepto')
    note = fields.Char(string='Nota')
    code = fields.Char(string='Codigo')
    slip_id = fields.Many2one('hr.payslip',string='Nomina')
    contract_id = fields.Many2one('hr.contract.public',string='Contrato')
    employee_id = fields.Many2one('hr.employee.public',string='Empleado')
    category_id = fields.Many2one('hr.salary.rule.category',string='Categoria')
    amount = fields.Float(string='Valor')
    quantity = fields.Float(string='Cantidad')
    total = fields.Float(string='Valor Total')
    entity_id = fields.Many2one('hr.employee.entities',string='Entidad')
    salary_rule_id = fields.Many2one('hr.salary.rule',string='Regla Salarial')

    @api.model
    def _get_fields(self):
        return ','.join('payslip_line.%s' % name for name, field in self._fields.items() if
                        field.store and field.type not in ['many2many', 'one2many'])

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
                SELECT
                    %s
                FROM hr_payslip_line payslip_line
            )""" % (self._table, self._get_fields()))