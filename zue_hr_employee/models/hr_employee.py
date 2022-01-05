# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date

class hr_tipo_cotizante(models.Model):
    _name = 'hr.tipo.cotizante'
    _description = 'Tipos de cotizante'
    
    code = fields.Char('Código', required=False, size=10)
    name = fields.Char('Nombre', required=False, size=200)


class hr_subtipo_cotizante(models.Model):
    _name = 'hr.subtipo.cotizante'
    _description = 'Subtipos de cotizante'

    code = fields.Char('Código', required=True, size=10)
    name = fields.Char('Novedad', required=True, size=200)
    not_contribute_pension = fields.Boolean('No aporta pensión')

class hr_indicador_especial_pila(models.Model):
    _name = 'hr.indicador.especial.pila'
    _description = 'Indicadores especiales para PILA'    
    
    name = fields.Char("Nombre")
    code = fields.Char('Codigo')
                
class hr_contract_setting(models.Model):
    _name = 'hr.contract.setting'
    _description = 'Configuracion nomina entidades'

    contrib_id = fields.Many2one('hr.contribution.register', 'Tipo Entidad', help='Concepto de aporte', required=True)
    partner_id = fields.Many2one('hr.employee.entities', 'Entidad', help='Entidad relacionada', domain="[('types_entities','in',[contrib_id])]", required=True)
    date_change = fields.Date(string='Fecha de ingreso')
    # account_debit_id = fields.Many2one('account.account', 'Cuenta deudora')
    # account_credit_id = fields.Many2one('account.account', 'Cuenta acreedora')
    employee_id = fields.Many2one('hr.employee', 'Empleado', required=True, ondelete='cascade')

    _sql_constraints = [('emp_type_entity_uniq', 'unique(employee_id,contrib_id)', 'El empleado ya tiene una entidad de este tipo, por favor verifique.')]

    @api.constrains('employee_id','contrib_id')
    def _check_duplicate_entitites(self):  
        for record in self:
            obj_duplicate = self.env['hr.contract.setting'].search([('id','!=',record.id),('employee_id','=',record.employee_id.id),('contrib_id','=',record.contrib_id.id)])

            if len(obj_duplicate) > 0:   
                raise ValidationError(_('El empleado ya tiene una entidad de este tipo, por favor verifique.'))  
    
    def write(self, vals):
        for record in self:
            vals_history = {
                'contrib_id': record.contrib_id.id,
                'partner_id': record.partner_id.id,
                'date_change': record.date_change,
                'employee_id': record.employee_id.id,
                'date_history': fields.Date.today()
            }
            res = super(hr_contract_setting, self).write(vals)
            self.env['hr.contract.setting.history'].create(vals_history)
            return res

class hr_contract_setting_history(models.Model):
    _name = 'hr.contract.setting.history'
    _description = 'Configuracion nomina entidades historico'

    contrib_id = fields.Many2one('hr.contribution.register', 'Tipo Entidad', help='Concepto de aporte')
    partner_id = fields.Many2one('hr.employee.entities', 'Entidad', help='Entidad relacionada', domain="[('types_entities','in',[contrib_id])]")
    date_change = fields.Date(string='Fecha de ingreso')
    employee_id = fields.Many2one('hr.employee', 'Empleado', required=True, ondelete='cascade')

    date_history = fields.Date(string='Fecha historico')

class hr_employee_dependents(models.Model):
    _name = 'hr.employee.dependents'
    _description = 'Dependientes de los empleados'
    
    employee_id = fields.Many2one('hr.employee', 'Empleado', required=True, ondelete='cascade')
    name = fields.Char('Nombre completo', required=True)
    genero = fields.Selection([('masculino', 'Masculino'),
                               ('femenino', 'Femenino'),
                               ('otro', 'Otro')],'Genero')
    date_birthday = fields.Date('Fecha de nacimiento')
    dependents_type = fields.Selection([('hijo', 'Hijo'),
                               ('padre', 'Padre'),
                               ('madre', 'Madre'),
                               ('conyuge', 'Cónyuge'),
                               ('otro', 'Otro')],'Tipo')

class hr_employee_labor_union(models.Model):
    _name = 'hr.employee.labor.union'
    _description = 'Sindicato de empleados'
    
    employee_id = fields.Many2one('hr.employee', 'Empleado', required=True, ondelete='cascade')
    name_labor_union = fields.Char('Nombre del sindicato', required=True)
    afiliado = fields.Boolean('Afiliado', help='Indica si el empelado esta afiliado a un sindicato')
    fuero = fields.Boolean('Fuero sindical', help='Indica si el empelado cuenta con un fuero sindical')
    cargo_sindicato = fields.Char('Cargo dentro del sindicato')

class hr_employee_documents(models.Model):
    _name = 'hr.employee.documents'
    _description = 'Documentos del empleado'

    employee_id = fields.Many2one('hr.employee','Empleado', required=True, ondelete='cascade')
    name = fields.Char('Descripción', required=True)
    expiration_date = fields.Date('Fecha de vencimiento')
    document = fields.Many2one('documents.document',string='Documento',required=True)

class hr_cost_distribution_employee(models.Model):
    _name = 'hr.cost.distribution.employee'
    _description = 'Distribucion de costos empleados'

    employee_id = fields.Many2one('hr.employee', string='Empleado', required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Cuenta analítica', required=True)
    porcentage = fields.Float(string='Porcentaje', required=True)

    _sql_constraints = [('change_distribution_analytic_uniq', 'unique(employee_id,analytic_account_id)',
                         'Ya existe una cuenta analítica asignada, por favor verificar')]

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def _get_default_type_thirdparty(self):
        id_type = self.env['zue.type_thirdparty'].search([('types', '=', '4')], limit=1).id
        if id_type:
            return id_type
        else:
            return False
    #Trazabilidad
    work_email = fields.Char(track_visibility='onchange')
    company_id = fields.Many2one(track_visibility='onchange')
    department_id = fields.Many2one(track_visibility='onchange')
    job_id = fields.Many2one(track_visibility='onchange')
    parent_id = fields.Many2one(track_visibility='onchange')
    address_id = fields.Many2one(track_visibility='onchange')
    #Asignación
    branch_id = fields.Many2one('zue.res.branch', 'Sucursal', track_visibility='onchange')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Cuenta analítica', track_visibility='onchange')
    front_back = fields.Selection([('front','Front office'),('back','Back office')],'Area laboral', track_visibility='onchange')
    confianza_manejo = fields.Boolean('Confianza y manejo', track_visibility='onchange')
    type_thirdparty = fields.Many2one('zue.type_thirdparty',string='Tipo de tercero', domain=[('types', '=', '4')], default=_get_default_type_thirdparty)
    #Evaluación de desempeño
    ed_qualification = fields.Float(string='Calificación', track_visibility='onchange')
    ed_observation = fields.Text(string='Observaciones', track_visibility='onchange')
    #General
    partner_encab_id = fields.Many2one('res.partner', 'Tercero', help='Tercero equivalente a el empleado')
    type_employee = fields.Many2one('hr.types.employee',string='Tipo de Empleado', track_visibility='onchange')
    sabado = fields.Boolean('Sábado día hábil', help='Indica si el día sábado se incluye como día hábil', track_visibility='onchange')
    certificate = fields.Selection(selection_add=[('primary','Primaria'),
                                    ('academic_bachelor','Bachiller'),
                                    ('apprentice','Aprendiz'),
                                    ('technical','Técnico'),
                                    ('technologist','Tecnólogo'),
                                    ('academic','Universitario'),
                                    ('specialist','Especialista'),
                                    ('magister','Maestría')],
                                    string='Nivel de certificado', track_visibility='onchange')
    social_security_entities  = fields.One2many('hr.contract.setting', 'employee_id', string = 'Entidades', track_visibility='onchange')
    dependents_information = fields.One2many('hr.employee.dependents', 'employee_id', string = 'Dependientes', track_visibility='onchange')
    labor_union_information = fields.One2many('hr.employee.labor.union', 'employee_id', string = 'Sindicato', track_visibility='onchange')
    personal_email = fields.Char(string='Correo-e personal')
    personal_mobile = fields.Char(string='Móvil')
    type_job = fields.Selection([('clave', 'Cargo Clave'),
                                    ('critico', 'Cargo Crítico'),
                                    ('cc', 'Cargo CC')], 'Tipo de cargo', track_visibility='onchange')
    emergency_relationship = fields.Char(string='Parentesco contacto')
    documents_ids = fields.One2many('hr.employee.documents', 'employee_id', 'Documentos')
    distribution_cost_information = fields.One2many('hr.cost.distribution.employee', 'employee_id', string='Distribución de costos empleado')
    #PILA
    extranjero = fields.Boolean('Extranjero', help='Extranjero no obligado a cotizar a pensión', track_visibility='onchange')
    residente = fields.Boolean('Residente en el Exterior', help='Colombiano residente en el exterior', track_visibility='onchange')
    date_of_residence_abroad = fields.Date(string='Fecha radicación en el exterior')
    tipo_coti_id = fields.Many2one('hr.tipo.cotizante', string='Tipo de cotizante', track_visibility='onchange')
    subtipo_coti_id = fields.Many2one('hr.subtipo.cotizante', string='Subtipo de cotizante')
    type_identification = fields.Selection([('CC', 'Cédula de ciudadanía'),
                                            ('CE', 'Cédula de extranjería'),
                                            ('TI', 'Tarjeta de identidad'),
                                            ('RC', 'Registro civil'),
                                            ('PA', 'Pasaporte')], 'Tipo de identificación', track_visibility='onchange')
    indicador_especial_id = fields.Many2one('hr.indicador.especial.pila','Indicador tarifa especial pensiones', track_visibility='onchange')
    cost_assumed_by  = fields.Selection([('partner', 'Cliente'),
                                        ('company', 'Compañía')], 'Costo asumido por', track_visibility='onchange')
    #Licencia de conducción
    licencia_rh = fields.Selection([('op','O+'),('ap','A+'),('bp','B+'),('abp','AB+'),('on','O-'),('an','A-'),('bn','B-'),('abn','AB-')],'Tipo de sangre', track_visibility='onchange')
    licencia_categoria = fields.Selection([('a1','A1'),('a2','A2'),('b1','B1'),('b2','B2'),('b3','B3'),('c1','C1'),('c2','C2'),('c3','C3')],'Categoria', track_visibility='onchange')
    licencia_vigencia = fields.Date('Vigencia', track_visibility='onchange')
    licencia_restricciones = fields.Char('Restricciones', size=255, track_visibility='onchange')
    operacion_retirar = fields.Boolean('Retirar de la operacion', track_visibility='onchange')
    operacion_reemplazo = fields.Many2one('hr.employee','Reemplazo', track_visibility='onchange')
    #Estado civil
    type_identification_spouse = fields.Selection([('CC', 'Cédula de ciudadanía'),
                                            ('CE', 'Cédula de extranjería'),
                                            ('TI', 'Tarjeta de identidad'),
                                            ('RC', 'Registro civil'),
                                            ('PA', 'Pasaporte')], 'Tipo de identificación cónyuge', track_visibility='onchange')
    num_identification_spouse = fields.Char('Número de identificación cónyuge', track_visibility='onchange')

    _sql_constraints = [('emp_identification_uniq', 'unique(company_id,identification_id)', 'La cédula debe ser unica. La cédula ingresada ya existe en esta compañía')]

    @api.onchange('partner_encab_id')
    def _onchange_partner_encab(self):
        for record in self:
            for partner in record.partner_encab_id:
                self.address_home_id = partner.id                

    @api.onchange('address_home_id')
    def _onchange_tercero_asociado(self):
        for record in self:
            for partner in record.address_home_id:
                if record.address_home_id.id != record.partner_encab_id.id:
                    self.partner_encab_id = partner.id  
                self.name = partner.name
                self.country_id = partner.country_id
                self.identification_id = partner.vat
                self.private_email = partner.email
                self.work_email = partner.email
                self.phone = partner.phone
                self.personal_mobile = partner.mobile

    @api.constrains('distribution_cost_information')
    def _check_porcentage_distribution_cost(self):
        for record in self:
            if len(record.distribution_cost_information) > 0:
                porc_total = 0
                for distribution in record.distribution_cost_information:
                    porc_total += distribution.porcentage
                if porc_total != 100:
                    raise UserError(_('Los porcentajes de la distribución de costos no suman un 100%, por favor verificar.'))

    @api.constrains('identification_id')
    def _check_identification(self):  
        for record in self:
            if record.identification_id != record.address_home_id.vat:
                raise UserError(_('El número de identificación debe ser igual al tercero seleccionado.'))
            if record.identification_id != record.partner_encab_id.vat:
                raise UserError(_('El número de identificación debe ser igual al tercero seleccionado.'))

    @api.constrains('social_security_entities')
    def _check_social_security_entities(self):
        for record in self:
            if len(record.social_security_entities) == 0:
                raise ValidationError(_('El empelado no tiene entidades asignadas, por favor verificar.'))

    @api.model
    def create(self, vals):
        if vals.get('address_home_id') and not vals.get('partner_encab_id'):
            vals['partner_encab_id'] = vals.get('address_home_id')
        if not vals.get('address_home_id') and vals.get('partner_encab_id'):
            vals['address_home_id'] = vals.get('partner_encab_id')         
        
        res = super(hr_employee, self).create(vals)
        return res

    def get_info_contract(self):
        for record in self:
            obj_contract = self.env['hr.contract'].search([('employee_id','=',record.id),('state','=','open')],limit=1)
            if len(obj_contract) == 0:
                obj_contract += self.env['hr.contract'].search([('employee_id', '=', record.id), ('state', '=', 'close')],limit=1)
            return obj_contract

    def get_age_for_date(self,date):
        today = date.today()
        return today.year - date.year - ((today.month, today.day) < (date.month, date.day))


            
                
                    
