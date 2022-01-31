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
    contract_id = fields.Many2one('hr.contract.public',string='Contrato')
    company_id = fields.Many2one('res.company',string='Compañia')
    observation  = fields.Char(string='Observacion')
    # worked_days_line_ids = fields.One2many('hr.payslip.worked_days', 'payslip_id',
    #     string='Payslip Worked Days', copy=True, readonly=True)


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

    #Dias laborados
    def worked_days_line_ids(self):
        obj_worked_days_line_ids = self.sudo().env['hr.payslip.worked.days.public'].search([('payslip_id', '=', self.id)])
        return obj_worked_days_line_ids

    #Detalle nomina
    def line_ids(self):
        obj_line_ids = self.sudo().env['hr.payslip.line.public'].search([('slip_id','=',self.id)])            
        return obj_line_ids
        
        