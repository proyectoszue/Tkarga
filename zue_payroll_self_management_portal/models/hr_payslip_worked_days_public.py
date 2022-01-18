from odoo import fields, models, api, tools


class HrPayslipWorkedDaysPublic(models.Model):
    _name = 'hr.payslip.worked.days.public' 
    _description = 'Vista dias trabajados del empleado'
    _auto = False
    _log_access = True

    id = fields.Integer(string='id')
    payslip_id = fields.Many2one('hr.payslip',string='Nomina')
    sequence = fields.Char(string='secuencia')
    work_entry_type_id = fields.Many2one('hr.work.entry.type',string='Concepto')
    number_of_days = fields.Float(string='Dias')

    @api.model
    def _get_fields(self):
        return ','.join('payslip_worked_days.%s' % name for name, field in self._fields.items() if
                        field.store and field.type not in ['many2many', 'one2many'])

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
                SELECT
                    %s
                FROM hr_payslip_worked_days payslip_worked_days
            )""" % (self._table, self._get_fields()))