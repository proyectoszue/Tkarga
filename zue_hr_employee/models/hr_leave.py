from odoo import models, fields, api

#Tipos de Ausencia
class hr_leave_type(models.Model):
    _inherit = 'hr.leave.type'

    is_vacation = fields.Boolean('Tipo de ausencia para vacaciones disfrutadas')
    #Validación
    obligatory_attachment  = fields.Boolean('Obligar adjunto')
    #Configuración de la EPS/ARL
    num_days_no_assume = fields.Integer('Número de días que no asume')
    recognizing_factor_eps_arl = fields.Float('Factor que reconoce la EPS/ARL', digits=(25,5))
    periods_calculations_ibl = fields.Integer('Periodos para cálculo de IBL')
    eps_arl_input_id = fields.Many2one('hr.salary.rule', 'Regla de la incapacidad EPS/ARL')
    #Configuración de la Empresa
    recognizing_factor_company = fields.Float('Factor que reconoce la empresa', digits=(25,5))
    periods_calculations_ibl_company = fields.Integer('Periodos para cálculo de IBL Empresa')
    company_input_id = fields.Many2one('hr.salary.rule', 'Regla de la incapacidad empresa')
    unpaid_absences = fields.Boolean('Ausencia no remunerada')
    type_of_entity_association = fields.Many2one('hr.contribution.register', 'Tipo de entidad asociada')

    _sql_constraints = [('hr_leave_type_code_uniq', 'unique(code)',
                         'Ya existe este código de nómina, por favor verficar.')]
    

    