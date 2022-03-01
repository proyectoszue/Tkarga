# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    payroll_electronic_username_ws = fields.Char(string='Usuario WS')
    payroll_electronic_password_ws = fields.Char(string='Contraseña WS')
    payroll_electronic_company_id_ws = fields.Char(string='Identificador compañia WS')
    payroll_electronic_account_id_ws = fields.Char(string='Identificador cuenta WS')
    payroll_electronic_service_ws = fields.Char(string='Servicio WS', default='PAYROLL')

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_hr_payroll_batch_account = fields.Selection([('0','Crear un solo movimiento contable'),
                                                        ('1','Crear movimiento contable por empleado')],
                                        string='Contabilización por lote')

    pay_vacations_in_payroll = fields.Boolean('¿Liquidar vacaciones en nómina?')
    vacation_days_calculate_absences = fields.Char('Días de vacaciones para calcular ausencias')
    #Nómina electronica
    payroll_electronic_username_ws = fields.Char(related='company_id.payroll_electronic_username_ws',string='Usuario WS', readonly=False)
    payroll_electronic_password_ws = fields.Char(related='company_id.payroll_electronic_password_ws',string='Contraseña WS', readonly=False)
    payroll_electronic_company_id_ws = fields.Char(related='company_id.payroll_electronic_company_id_ws',string='Identificador compañia WS', readonly=False)
    payroll_electronic_account_id_ws = fields.Char(related='company_id.payroll_electronic_account_id_ws',string='Identificador cuenta WS', readonly=False)
    payroll_electronic_service_ws = fields.Char(related='company_id.payroll_electronic_service_ws',string='Servicio WS', default='PAYROLL', readonly=False)

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('zue_hr_payroll.module_hr_payroll_batch_account', self.module_hr_payroll_batch_account)
        set_param('zue_hr_payroll.pay_vacations_in_payroll', self.pay_vacations_in_payroll)
        set_param('zue_hr_payroll.vacation_days_calculate_absences', self.vacation_days_calculate_absences)

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res['module_hr_payroll_batch_account'] = get_param('zue_hr_payroll.module_hr_payroll_batch_account')
        res['pay_vacations_in_payroll'] = get_param('zue_hr_payroll.pay_vacations_in_payroll')
        res['vacation_days_calculate_absences'] = get_param('zue_hr_payroll.vacation_days_calculate_absences')
        return res