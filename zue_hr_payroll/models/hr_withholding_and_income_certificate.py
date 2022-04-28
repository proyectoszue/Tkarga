from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
#---------------------------Certificado ingreso y retenciones-------------------------------#

class hr_withholding_and_income_certificate(models.TransientModel):
    _name = 'hr.withholding.and.income.certificate'
    _description = 'Certificado ingreso y retenciones'

    employee_id = fields.Many2many('hr.employee', string="Empleado",)
    year = fields.Integer('Año', required=True)

    def generate_certificate(self):
        datas = {
             'id': self.id,
             'model': 'hr.withholding.and.income.certificate'
            }

        return {
            'type': 'ir.actions.report',
            'report_name': 'zue_hr_payroll.hr_report_income_and_withholdings',
            'report_type': 'qweb-pdf',
            'datas': datas
        }