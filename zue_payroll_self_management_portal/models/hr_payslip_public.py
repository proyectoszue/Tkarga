from odoo import fields, models, api, tools


class HrPayslipPublic(models.Model):
    _name = 'hr.payslip.public' 
    _description = 'Vista de la tabla de liquidaciones'
    _auto = False
    _log_access = True

    id = fields.Integer(string='id')
    employee_id = fields.Many2one('hr.employee.public',string='Empleado')
    struct_id = fields.Many2one('hr.payroll.structure',string='Tipo Liquidacion')
    state = fields.Char(string='Estado')
    date_from = fields.Date(string='Fecha inicio')
    date_to = fields.Date(string='Fecha fin')


    @api.model
    def _get_fields(self):
        return ','.join('payslip.%s' % name for name, field in self._fields.items() if
                        field.store and field.type not in ['many2many', 'one2many'])

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
                SELECT
                    %s
                FROM hr_payslip payslip
            )""" % (self._table, self._get_fields()))