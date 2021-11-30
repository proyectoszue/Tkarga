# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError
import time

#Tabla de tipos de empleados
class hr_types_employee(models.Model):
    _name = 'hr.types.employee'
    _description = 'Tipos de empleado'

    code = fields.Char('Código',required=True)
    name = fields.Char('Nombre',required=True)

    _sql_constraints = [('change_code_uniq', 'unique(code)', 'Ya existe un tipo de empleado con este código, por favor verificar')]

#Tabla de tiesgos profesionales
class hr_contract_risk(models.Model):
    _name = 'hr.contract.risk'
    _description = 'Riesgos profesionales'

    code = fields.Char('Codigo', size=10, required=True)
    name = fields.Char('Nombre', size=100, required=True)
    percent = fields.Float('Porcentaje', required=True, help='porcentaje del riesgo profesional')
    date = fields.Date('Fecha vigencia')

    _sql_constraints = [('change_code_uniq', 'unique(code)', 'Ya existe un riesgo con este código, por favor verificar')]         

#Tabla tipos de entidades
class hr_contrib_register(models.Model):
    _name = 'hr.contribution.register'
    _description = 'Tipo de Entidades'
    
    name = fields.Char('Nombre', required=True)
    type_entities = fields.Selection([('none', 'No aplica'),
                             ('eps', 'Entidad promotora de salud'),
                             ('pension', 'Fondo de pensiones'),
                             ('cesantias', 'Fondo de cesantias'),
                             ('caja', 'Caja de compensación'),
                             ('riesgo', 'Aseguradora de riesgos profesionales'),
                             ('sena', 'SENA'),
                             ('icbf', 'ICBF'),
                             ('solidaridad', 'Fondo de solidaridad'),
                             ('subsistencia', 'Fondo de subsistencia')], 'Tipo', required=True)
    note = fields.Text('Description')

    _sql_constraints = [('change_name_uniq', 'unique(name)', 'Ya existe un tipo de entidad con este nombre, por favor verificar')]         

#Tabla de entidades
class hr_employee_entities(models.Model):
    _name = 'hr.employee.entities'
    _description = 'Entidades empleados'

    partner_id = fields.Many2one('res.partner', 'Entidad', help='Entidad relacionada')
    name = fields.Char(related="partner_id.name", readonly=True,string="Nombre")
    business_name = fields.Char(related="partner_id.x_business_name", readonly=True,string="Nombre de negocio")
    types_entities = fields.Many2many('hr.contribution.register',string='Tipo de entidad')
    code_pila_eps = fields.Char('Código PILA')
    code_pila_ccf = fields.Char('Código PILA para CCF')
    code_pila_regimen = fields.Char('Código PILA Regimen de excepción')
    code_pila_exterior = fields.Char('Código PILA Reside en el exterior')
    order = fields.Selection([('territorial', 'Orden Terrritorial'),
                             ('nacional', 'Orden Nacional')], 'Orden de la entidad')

    _sql_constraints = [('change_partner_uniq', 'unique(partner_id)', 'Ya existe una entidad asociada a este tercero, por favor verificar')]         

    def name_get(self):
        result = []
        for record in self:
            if record.partner_id.x_business_name: 
                result.append((record.id, "{}".format(record.partner_id.x_business_name)))
            else: 
                result.append((record.id, "{}".format(record.partner_id.name)))
        return result

#Categorias reglas salariales herencia

class hr_categories_salary_rules(models.Model):
    _inherit = 'hr.salary.rule.category'
    
    group_payroll_voucher = fields.Boolean('Agrupar comprobante de nómina')

#Contabilización reglas salariales
class hr_salary_rule_accounting(models.Model):
    _name ='hr.salary.rule.accounting'
    _description = 'Contabilización reglas salariales'    

    salary_rule = fields.Many2one('hr.salary.rule', string = 'Regla salarial', track_visibility='onchange')
    department = fields.Many2one('hr.department', string = 'Departamento', track_visibility='onchange')
    company = fields.Many2one('res.company', string = 'Compañía', track_visibility='onchange')
    work_location = fields.Many2one('res.partner', string = 'Ubicación de trabajo', track_visibility='onchange')
    third_debit = fields.Selection([('entidad', 'Entidad'),
                                    ('compañia', 'Compañia'),
                                    ('empleado', 'Empleado')], string='Tercero débito', track_visibility='onchange') 
    third_credit = fields.Selection([('entidad', 'Entidad'),
                                    ('compañia', 'Compañia'),
                                    ('empleado', 'Empleado')], string='Tercero crédito', track_visibility='onchange')
    debit_account = fields.Many2one('account.account', string = 'Cuenta débito', company_dependent=True, track_visibility='onchange')
    credit_account = fields.Many2one('account.account', string = 'Cuenta crédito', company_dependent=True, track_visibility='onchange')

#Estructura Salariales - Herencia
class hr_payroll_structure(models.Model):
    _inherit = 'hr.payroll.structure'

    process = fields.Selection([('nomina', 'Nónima'),
                                ('vacaciones', 'Vacaciones'),
                                ('prima', 'Prima'),
                                ('cesantias_e_intereses', 'Cesantías e Intereses'),
                                ('contrato', 'Liq. de Contrato'),
                                ('otro', 'Otro')], string='Proceso')

    @api.onchange('regular_pay')
    def onchange_regular_pay(self):
        for record in self:
            record.process = 'nomina' if record.regular_pay == True else False    

#Tipos entradas de trabajo - Herencia
class hr_work_entry_type(models.Model):
    _name = 'hr.work.entry.type'
    _inherit = ['hr.work.entry.type','mail.thread', 'mail.activity.mixin']

    code = fields.Char(track_visibility='onchange')
    sequence = fields.Integer(track_visibility='onchange')
    round_days = fields.Selection(track_visibility='onchange')
    round_days_type = fields.Selection(track_visibility='onchange')
    is_leave = fields.Boolean(track_visibility='onchange')
    is_unforeseen = fields.Boolean(track_visibility='onchange')

#Reglas Salariales - Herencia
class hr_salary_rule(models.Model):
    _name = 'hr.salary.rule'
    _inherit = ['hr.salary.rule','mail.thread', 'mail.activity.mixin']

    #Trazabilidad
    struct_id = fields.Many2one(track_visibility='onchange')
    active = fields.Boolean(track_visibility='onchange')
    sequence = fields.Integer(track_visibility='onchange')
    condition_select = fields.Selection(track_visibility='onchange')
    amount_select = fields.Selection(track_visibility='onchange')
    amount_python_compute = fields.Text(track_visibility='onchange')
    appears_on_payslip = fields.Boolean(track_visibility='onchange')
    #Campos ZUE
    types_employee = fields.Many2many('hr.types.employee',string='Tipos de Empleado', track_visibility='onchange')
    dev_or_ded = fields.Selection([('devengo', 'Devengo'),
                                     ('deduccion', 'Deducción')],'Naturaleza', track_visibility='onchange')
    type_concept = fields.Selection([('contrato', 'Fijo Contrato'),
                                     ('ley', 'Por Ley'),
                                     ('novedad', 'Novedad Variable'),
                                     ('prestacion', 'Prestación Social'),
                                     ('tributaria', 'Deducción Tributaria')],'Tipo', required=True, default='contrato', track_visibility='onchange')
    aplicar_cobro = fields.Selection([('15','Primera quincena'),
                                        ('30','Segunda quincena'),
                                        ('0','Siempre')],'Aplicar cobro', track_visibility='onchange')
    modality_value = fields.Selection([('fijo', 'Valor fijo'),
                                       ('diario', 'Valor diario'),
                                       ('diario_efectivo', 'Valor diario del día efectivamente laborado')],'Modalidad de valor', track_visibility='onchange')
    deduction_applies_bonus = fields.Boolean('Aplicar deducción en Prima', track_visibility='onchange')
    #Es incapacidad / deducciones
    is_leave = fields.Boolean('Es Ausencia', track_visibility='onchange')
    deduct_deductions = fields.Selection([('all', 'Todas las deducciones'),
                                          ('law', 'Solo las deducciones de ley')],'Tener en cuenta al descontar', default='all', track_visibility='onchange')    #Vacaciones
    #Base de prestaciones
    base_prima = fields.Boolean('Para prima', track_visibility='onchange')
    base_cesantias = fields.Boolean('Para cesantías', track_visibility='onchange')
    base_vacaciones = fields.Boolean('Para vacaciones tomadas', track_visibility='onchange')
    base_vacaciones_dinero = fields.Boolean('Para vacaciones dinero', track_visibility='onchange')
    base_intereses_cesantias = fields.Boolean('Para intereses de cesantías', track_visibility='onchange')
    #Base de Seguridad Social
    base_seguridad_social = fields.Boolean('Para seguridad social', track_visibility='onchange')
    base_parafiscales = fields.Boolean('Para parafiscales', track_visibility='onchange')
    #Contabilización
    salary_rule_accounting = fields.One2many('hr.salary.rule.accounting', 'salary_rule', string="Contabilización", track_visibility='onchange') 

#Tabla de parametros anuales
class hr_annual_parameters(models.Model):
    _name = 'hr.annual.parameters'
    _description = 'Parámetros anuales'

    year = fields.Integer('Año', required=True)
    #Básicos Salario Minimo
    smmlv_monthly = fields.Float('Valor mensual SMMLV', required=True)
    smmlv_daily = fields.Float('Valor diario SMMLV', compute='_values_smmlv', store=True)
    top_four_fsp_smmlv = fields.Float('Tope 4 salarios FSP', compute='_values_smmlv', store=True)
    top_twenty_five_smmlv = fields.Float('Tope 25 salarios', compute='_values_smmlv', store=True)
    top_ten_smmlv = fields.Float('Tope 10 salarios', compute='_values_smmlv', store=True)
    #Básicos Auxilio de transporte
    transportation_assistance_monthly = fields.Float('Valor mensual Auxilio Transporte', required=True)
    transportation_assistance_daily = fields.Float('Valor diario Auxilio Transporte', compute='_value_transportation_assistance_daily', store=True)
    top_max_transportation_assistance = fields.Float('Tope maxímo para pago', compute='_values_smmlv', store=True)
    #Básicos Salario Integral
    min_integral_salary  = fields.Float('Salario mínimo integral', compute='_values_smmlv', store=True)
    porc_integral_salary  = fields.Integer('Porcentaje salarial', required=True)
    value_factor_integral_salary = fields.Float('Valor salarial', compute='_values_integral_salary', store=True)
    value_factor_integral_performance  = fields.Float('Valor prestacional', compute='_values_integral_salary', store=True)    
    #Básicos Horas Laborales
    hours_daily = fields.Integer('Horas diarias', required=True)
    hours_weekly = fields.Integer('Horas semanales', compute='_values_hours', store=True)
    hours_fortnightly = fields.Integer('Horas quincenales', compute='_values_hours', store=True)
    hours_monthly = fields.Integer('Horas mensuales', compute='_values_hours', store=True)
    #Seguridad Social
    weight_contribution_calculations = fields.Boolean('Cálculos de aportes al peso')
    #Salud
    value_porc_health_company = fields.Float('Porcentaje empresa salud', required=True)
    value_porc_health_employee = fields.Float('Porcentaje empleado salud', required=True)
    value_porc_health_total = fields.Float('Porcentaje total salud', compute='_value_porc_health_total', store=True)
    value_porc_health_employee_foreign = fields.Float('Porcentaje aporte extranjero', required=True)
    #Pension
    value_porc_pension_company = fields.Float('Porcentaje empresa pensión', required=True)
    value_porc_pension_employee = fields.Float('Porcentaje empleado pensión', required=True)
    value_porc_pension_total = fields.Float('Porcentaje total pensión', compute='_value_porc_pension_total', store=True)
    #Aportes parafiscales
    value_porc_compensation_box_company  = fields.Float('Caja de compensación', required=True)
    value_porc_sena_company = fields.Float('SENA', required=True)
    value_porc_icbf_company = fields.Float('ICBF', required=True)
    #Provisiones prestaciones
    value_porc_provision_bonus = fields.Float('Prima', required=True)
    value_porc_provision_cesantias = fields.Float('Cesantías', required=True)
    value_porc_provision_intcesantias = fields.Float('Intereses Cesantías', required=True)
    value_porc_provision_vacation = fields.Float('Vacaciones', required=True)
    #Tope Ley 1395
    value_porc_statute_1395 =  fields.Integer('Porcentaje (%)', required=True)
    #Tributario
    #Retención en la fuente
    value_uvt = fields.Float('Valor UVT', required=True)
    value_top_source_retention = fields.Float('Tope para el calculo de retención en la fuente', required=True)
    #Incrementos
    value_porc_increment_smlv = fields.Float('Incremento SMLV', required=True)
    value_porc_ipc = fields.Float('Porcentaje IPC', required=True)

    #Metodos
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "{}".format(str(record.year))))
        return result

    @api.depends('smmlv_monthly')
    def _values_smmlv(self):
        self.smmlv_daily = self.smmlv_monthly / 30
        self.top_four_fsp_smmlv = 4 * self.smmlv_monthly
        self.top_twenty_five_smmlv = 25 * self.smmlv_monthly
        self.top_ten_smmlv = 10 * self.smmlv_monthly
        self.top_max_transportation_assistance = 2 * self.smmlv_monthly
        self.min_integral_salary = 13 * self.smmlv_monthly
    
    @api.depends('transportation_assistance_monthly')
    def _value_transportation_assistance_daily(self):
        self.transportation_assistance_daily = self.transportation_assistance_monthly / 30
    
    @api.depends('porc_integral_salary')
    def _values_integral_salary(self):
        porc_integral_salary_rest = 100 - self.porc_integral_salary
        value_factor_integral_salary = round(self.min_integral_salary / ((porc_integral_salary_rest/100)+1),0)
        value_factor_integral_performance = round(self.min_integral_salary - value_factor_integral_salary,0)
        self.value_factor_integral_salary = value_factor_integral_salary
        self.value_factor_integral_performance = value_factor_integral_performance

    @api.depends('hours_daily')
    def _values_hours(self):
        self.hours_weekly = 7 * self.hours_daily
        self.hours_fortnightly = 15 * self.hours_daily
        self.hours_monthly = 30 * self.hours_daily

    @api.depends('value_porc_health_company', 'value_porc_health_employee')
    def _value_porc_health_total(self):
        self.value_porc_health_total = self.value_porc_health_company + self.value_porc_health_employee
    
    @api.depends('value_porc_pension_company', 'value_porc_pension_employee')
    def _value_porc_pension_total(self):
        self.value_porc_pension_total = self.value_porc_pension_company + self.value_porc_pension_employee

    #Validaciones
    @api.onchange('porc_integral_salary')
    def _onchange_porc_integral_salary(self):
        for record in self:
            if record.porc_integral_salary > 100:
                raise UserError(_('El porcentaje salarial integral no puede ser mayor a 100. Por favor verificar.'))   
    
    #Funcionalidades

    #Obtener salario integral, el parametro get_value | 0 = Valor Salarial & 1 = Valor Prestacional
    def get_values_integral_salary(self,integral_salary,get_value):
        porc_integral_salary_rest = 100 - self.porc_integral_salary
        value_factor_integral_salary = round(integral_salary / ((porc_integral_salary_rest/100)+1),0)
        value_factor_integral_performance = round(integral_salary - value_factor_integral_salary,0)
        value_factor_integral_salary = value_factor_integral_salary
        value_factor_integral_performance = value_factor_integral_performance
        return value_factor_integral_salary if get_value == 0 else value_factor_integral_performance

    _sql_constraints = [('change_year_uniq', 'unique(year)', 'Ya existe una parametrización para el año digitado, por favor verificar')]         
    