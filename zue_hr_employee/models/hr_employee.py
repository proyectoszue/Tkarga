# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date
import json

class hr_tipo_cotizante(models.Model):
    _name = 'hr.tipo.cotizante'
    _description = 'Tipos de cotizante'
    _order = 'code,name'
    
    code = fields.Char('Código', required=True)
    name = fields.Char('Nombre', required=True)

    #Tabla de cotizante 51
    #Documentación - http://aportesenlinea.custhelp.com/app/answers/detail/a_id/464/~/condiciones-cotizante-51
    def get_value_cotizante_51(self,year,number_of_days):
        value_return = 0
        number_of_days = round(number_of_days)
        if self.code == '51':
            annual_parameters = self.env['hr.annual.parameters'].search([('year', '=', year)])
            if number_of_days >= 1 and number_of_days <= 7:
                value_return = (annual_parameters.smmlv_monthly / 4) * 1
            elif number_of_days >= 8 and number_of_days <= 14:
                value_return = (annual_parameters.smmlv_monthly / 4) * 2
            elif number_of_days >= 15 and number_of_days <= 21:
                value_return = (annual_parameters.smmlv_monthly / 4) * 3
            elif number_of_days >= 22 and number_of_days <= 30:
                value_return = annual_parameters.smmlv_monthly
        return value_return

class hr_subtipo_cotizante(models.Model):
    _name = 'hr.subtipo.cotizante'
    _description = 'Subtipos de cotizante'
    _order = 'code,name'

    code = fields.Char('Código', required=True)
    name = fields.Char('Novedad', required=True)
    not_contribute_pension = fields.Boolean('No aporta pensión')

class hr_parameterization_of_contributors(models.Model):
    _name = 'hr.parameterization.of.contributors'
    _description = 'Parametrizacion Cotizantes'

    type_of_contributor = fields.Many2one('hr.tipo.cotizante', string='Tipo de cotizante')
    contributor_subtype = fields.Many2one('hr.subtipo.cotizante', string='Subtipos de cotizante')
    liquidated_eps_employee = fields.Boolean('Liquida EPS Empleado')
    liquidate_employee_pension = fields.Boolean('Liquida Pensión Empleado')
    liquidated_aux_transport = fields.Boolean('Liquida Auxilio de Transporte')
    liquidates_solidarity_fund = fields.Boolean('Liquida Fondo de Solidaridad')
    liquidates_eps_company = fields.Boolean('Liquida EPS Empresa')
    liquidated_company_pension = fields.Boolean('Liquida Pensión Empresa')
    liquidated_arl = fields.Boolean('Liquida ARL')
    liquidated_sena = fields.Boolean('Liquida SENA')
    liquidated_icbf = fields.Boolean('Liquida ICBF')
    liquidated_compensation_fund = fields.Boolean('Liquida Caja de Compensación')
    liquidated_provisions = fields.Boolean('Liquida Provisiones')

    _parameterization_type_of_contributor_uniq = models.Constraint('unique(type_of_contributor,contributor_subtype)', 'Ya existe esta parametrizacion de tipo de cotizante y subtipo de cotizante, por favor verficar.')

    @api.depends('type_of_contributor', 'contributor_subtype')
    def _compute_display_name(self):
        for record in self:
            record.display_name = "Parametrización {} | {}".format(record.type_of_contributor.name, record.contributor_subtype.name)

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
    is_transfer = fields.Boolean(string='Es un Traslado', default=False)
    # account_debit_id = fields.Many2one('account.account', 'Cuenta deudora')
    # account_credit_id = fields.Many2one('account.account', 'Cuenta acreedora')
    employee_id = fields.Many2one('hr.employee', 'Empleado', required=True, ondelete='cascade')

    _emp_type_entity_uniq = models.Constraint('unique(employee_id,contrib_id)', 'El empleado ya tiene una entidad de este tipo, por favor verifique.')

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
                'is_transfer': vals.get('is_transfer',False),
                'date_history': vals.get('date_change',fields.Date.today())
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
    is_transfer = fields.Boolean(string='Es un Traslado')
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
    dependents_type = fields.Selection([('hijo', 'Hijo(a)'),
                                        ('padre', 'Padre'),
                                        ('madre', 'Madre'),
                                        ('conyuge', 'Cónyuge'),
                                        ('hermano', 'Hermano(a)'),
                                        ('sobrino', 'Sobrino(a)'),
                                        ('nieto', 'Nieto(a)'),
                                        ('hermano', 'Hermano(a)'),
                                        ('tio', 'Tío(a)'),
                                        ('abuelo', 'Abuelo(a)'),
                                        ('tio_abuelo', 'Tío(a) abuelo(a)'),
                                        ('bisabuelo', 'Bisabuelo(a)'),
                                        ('bisnieto', 'Bisnieto(a)'),
                                        ('suegro', 'Suegro(a)'),
                                        ('yerno', 'Yerno(a)'),
                                        ('nuera', 'Nuera'),
                                        ('cuñado', 'Cuñado(a)'),
                                        ('otro', 'Otro')], 'Tipo')
    z_document_type = fields.Selection([
        ('11', 'Registro civil de nacimiento'),
        ('12', 'Tarjeta de identidad'),
        ('13', 'Cédula de ciudadanía'),
        ('21', 'Tarjeta de extranjería'),
        ('22', 'Cedula de extranjería'),
        ('31', 'NIT'),
        ('41', 'Pasaporte'),
        ('42', 'Tipo de documento extranjero'),
        ('43', 'Sin identificación del exterior o para uso definido por la DIAN'),
        ('44', 'Documento de identificación extranjero persona jurídica'),
        ('PE', 'Permiso especial de permanencia'),
        ('PT', 'Permiso por Protección Temporal')
    ], string='Tipo de documento',default='13')
    z_vat = fields.Char(string='Número de documento')
    z_phone = fields.Integer(string='Teléfono')
    z_address = fields.Char(string='Dirección')
    z_report_income_and_withholdings = fields.Boolean(string='Reportar en Certificado ingresos y retenciones')
    z_upc_payment = fields.Boolean(string='Paga UPC')
    z_upc_geographic_area = fields.Selection([
        ('ZN', 'Zona normal'),
        ('ZE', 'Zona especial'),
        ('CD', 'Ciudades'),
        ('IS', 'Islas')
    ], string='Zona geográfica')

    @api.onchange('z_upc_payment')
    def onchange_z_upc_payment(self):
        for record in self:
            if not record.z_upc_payment:
                record.z_upc_geographic_area = False


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

    def unlink(self):
        obj_document = self.document
        obj = super(hr_employee_documents, self).unlink()
        obj_document.unlink()
        return obj

class hr_cost_distribution_employee(models.Model):
    _name = 'hr.cost.distribution.employee'
    _description = 'Distribucion de costos empleados'

    employee_id = fields.Many2one('hr.employee', string='Empleado', required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Cuenta analítica', required=True)
    porcentage = fields.Float(string='Porcentaje', required=True)

    _change_distribution_analytic_uniq = models.Constraint('unique(employee_id,analytic_account_id)', 'Ya existe una cuenta analítica asignada, por favor verificar')

class hr_employee_sanctions(models.Model):
    _name = 'hr.employee.sanctions'
    _description = 'Sanciones'

    employee_id = fields.Many2one('hr.employee', string='Empleado')
    company_id = fields.Many2one(related='employee_id.company_id', string='Compañía', store=True)
    work_contact_id = fields.Many2one(related='employee_id.partner_encab_id', string='Tercero asociado', store=True)
    document_id = fields.Many2one('documents.document', string='Documento')
    absence_id = fields.Many2one('hr.leave', string='Ausencia')
    registration_date = fields.Date(string='Fecha de registro')
    type_fault_id = fields.Many2one('hr.types.faults', string='Tipo de falta')
    name = fields.Char(string='Observación')
    stage = fields.Selection([('1', 'Comunicación'),
                              ('2', 'Descargos'),
                              ('3', 'Pronunciamiento'),
                              ('4', 'Sanción'),
                              ('5', 'Cancelar'),
                              ], string='Estado')


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
    work_email = fields.Char(tracking=True)
    company_id = fields.Many2one(tracking=True)
    parent_id = fields.Many2one(tracking=True)
    resource_calendar_id = fields.Many2one('resource.calendar', tracking=True)
    #Asignación
    branch_id = fields.Many2one('zue.res.branch', 'Sucursal', tracking=True)
    front_back = fields.Selection([('front','Front office'),('back','Back office')],'Area laboral', tracking=True)
    confianza_manejo = fields.Boolean('Confianza y manejo', tracking=True)
    type_thirdparty = fields.Many2one('zue.type_thirdparty',string='Tipo de tercero', domain=[('types', '=', '4')], default=_get_default_type_thirdparty)
    info_project = fields.Char(string='Proyecto', tracking=True)
    #Evaluación de desempeño
    ed_qualification = fields.Float(string='Calificación', tracking=True)
    ed_observation = fields.Text(string='Observaciones', tracking=True)
    #General
    partner_encab_id = fields.Many2one('res.partner', 'Tercero', help='Tercero equivalente a el empleado', tracking=True)
    type_employee = fields.Many2one('hr.types.employee',string='Tipo de Empleado', tracking=True)
    sabado = fields.Boolean('Sábado día hábil', help='Indica si el día sábado se incluye como día hábil', tracking=True)
    certificate = fields.Selection(selection=[('primary', 'Primaria'),
                                    ('academic_bachelor', 'Bachiller'),
                                    ('technical', 'Técnico'),
                                    ('technologist', 'Tecnólogo'),
                                    ('academic', 'Profesional Universitario'),
                                    ('specialist', 'Especialista'),
                                    ('magister', 'Magister'),
                                    ('doctor', 'Doctor'),
                                    ('graduate', 'Licenciado'),
                                    ('bachelor', 'Graduado'),
                                    ('master', 'Maestro'),
                                    ('other', 'Otro')],
                                    string='Nivel de certificado', default='primary',tracking=True)
    social_security_entities  = fields.One2many('hr.contract.setting', 'employee_id', string = 'Entidades', tracking=True, copy=True)
    dependents_information = fields.One2many('hr.employee.dependents', 'employee_id', string = 'Dependientes', tracking=True, copy=True)
    labor_union_information = fields.One2many('hr.employee.labor.union', 'employee_id', string = 'Sindicato', tracking=True, copy=True)
    personal_email = fields.Char(string='Correo-e personal', tracking=True)
    personal_mobile = fields.Char(string='Móvil', tracking=True)
    type_job = fields.Selection([('clave', 'Cargo Clave'),
                                    ('critico', 'Cargo Crítico'),
                                    ('cc', 'Cargo CC')], 'Tipo de cargo', tracking=True)
    emergency_relationship = fields.Char(string='Parentesco contacto', tracking=True)
    documents_ids = fields.One2many('hr.employee.documents', 'employee_id', 'Documentos', copy=True)
    distribution_cost_information = fields.One2many('hr.cost.distribution.employee', 'employee_id', string='Distribución de costos empleado', copy=True)
    #PILA
    extranjero = fields.Boolean('Extranjero', help='Extranjero no obligado a cotizar a pensión', tracking=True)
    residente = fields.Boolean('Residente en el Exterior', help='Colombiano residente en el exterior', tracking=True)
    date_of_residence_abroad = fields.Date(string='Fecha radicación en el exterior', tracking=True)
    tipo_coti_id = fields.Many2one('hr.tipo.cotizante', string='Tipo de cotizante', tracking=True)
    subtipo_coti_id = fields.Many2one('hr.subtipo.cotizante', string='Subtipo de cotizante', tracking=True)
    type_identification = fields.Selection([('CC', 'Cédula de ciudadanía'),
                                            ('CE', 'Cédula de extranjería'),
                                            ('TI', 'Tarjeta de identidad'),
                                            ('RC', 'Registro civil'),
                                            ('PA', 'Pasaporte')], 'Tipo de identificación', tracking=True)
    indicador_especial_id = fields.Many2one('hr.indicador.especial.pila','Indicador tarifa especial pensiones', tracking=True)
    cost_assumed_by  = fields.Selection([('partner', 'Cliente'),
                                        ('company', 'Compañía')], 'Costo asumido por', tracking=True)
    #Licencia de conducción
    licencia_rh = fields.Selection([('op','O+'),('ap','A+'),('bp','B+'),('abp','AB+'),('on','O-'),('an','A-'),('bn','B-'),('abn','AB-')],'Tipo de sangre', tracking=True)
    licencia_categoria = fields.Selection([('a1','A1'),('a2','A2'),('b1','B1'),('b2','B2'),('b3','B3'),('c1','C1'),('c2','C2'),('c3','C3')],'Categoria', tracking=True)
    licencia_vigencia = fields.Date('Vigencia', tracking=True)
    licencia_restricciones = fields.Char('Restricciones', tracking=True)
    operacion_retirar = fields.Boolean('Retirar de la operacion', tracking=True)
    operacion_reemplazo = fields.Many2one('hr.employee','Reemplazo', tracking=True)
    #Estado civil
    type_identification_spouse = fields.Selection([('CC', 'Cédula de ciudadanía'),
                                            ('CE', 'Cédula de extranjería'),
                                            ('TI', 'Tarjeta de identidad'),
                                            ('RC', 'Registro civil'),
                                            ('PA', 'Pasaporte')], 'Tipo de identificación cónyuge', tracking=True)
    num_identification_spouse = fields.Char('Número de identificación cónyuge', tracking=True)
    spouse_phone= fields.Char('Teléfono del cónyuge', tracking=True)
    #Sanciones
    employee_sanctions_ids = fields.One2many('hr.employee.sanctions', 'employee_id', string='Sanciones', copy=True)
    #Edad
    z_employee_age = fields.Integer(string='Edad', compute='_get_employee_age', store=True)
    # Campos Caracterizacion
    z_stratum = fields.Selection([('1', '1'),
                                  ('2', '2'),
                                  ('3', '3'),
                                  ('4', '4'),
                                  ('5', '5'),
                                  ('6', '6')], string='Estrato', tracking=True)
    z_sexual_orientation = fields.Selection([('heterosexual', 'Heterosexual'),
                                             ('bisexual', 'Bisexual'),
                                             ('homosexual', 'Homosexual'),
                                             ('pansexual', 'Pansexual'),
                                             ('asexual', 'Asexual'),
                                             ('other', 'Otro')], string='Orientación Sexual', tracking=True)
    z_sexual_orientation_other = fields.Char(string="¿Cual?", tracking=True)
    z_ethnic_group = fields.Selection([('none', 'Ninguno'),
                                       ('indigenous', 'Indígena'),
                                       ('afrocolombian', 'Afrocolombiano'),
                                       ('gypsy', 'Gitano'),
                                       ('raizal', 'Raizal')], string='Grupo étnico', tracking=True)
    z_housing_area = fields.Selection([('rural', 'Rural'),
                                       ('urban', 'Urbana')], string='Zona de Vivienda', tracking=True)
    z_health_risk_factors = fields.Char(string="Factores de riesgo en salud", tracking=True)
    z_religion = fields.Char(string="Religión", tracking=True)
    z_victim_armed_conflict = fields.Selection([('yes', 'Si'),
                                                ('not', 'No')], string='Victima del conflicto armado', tracking=True)
    z_academic_data= fields.Char(string="Datos académicos", tracking=True)
    #z_city_birth_id = fields.Many2one('res.city',string="Ciudad de nacimiento",domain="[('state_id', '=', z_department_birth_id)]", tracking=True)
    z_department_birth_id = fields.Many2one('res.country.state',string="Departamento de nacimiento", domain="[('country_id', '=', country_id)]", tracking=True)
    z_military_passbook = fields.Boolean('Libreta militar', tracking=True)

    _emp_identification_uniq = models.Constraint('unique(company_id,identification_id)', 'La cédula debe ser unica. La cédula ingresada ya existe en esta compañía')

    @api.onchange('partner_encab_id')
    def _onchange_tercero_asociado(self):
        partner = self.partner_encab_id
        if not partner:
            return {}
        country_id = partner.country_id.id if partner.country_id else False
        vals = {
            'name': partner.name,
            'country_id': country_id,
            'private_country_id': country_id,
            'identification_id': partner.vat or False,
            'private_email': partner.email,
            'work_email': partner.email,
            'mobile_phone': partner.phone,
            'personal_mobile': partner.mobile,
            'private_street': partner.street,
            'private_city': partner.city,
            'private_state_id': partner.state_id.id if partner.state_id else False,
            'private_zip': partner.x_zip_id.code if partner.x_zip_id else False,
        }
        if self.work_contact_id.id != partner.id:
            vals['work_contact_id'] = partner.id
        return {'value': vals}

    @api.depends('birthday')
    def _get_employee_age(self):
        for record in self:
            if record.birthday:
                record.z_employee_age = (date.today() - record.birthday).days // 365

    @api.constrains('distribution_cost_information')
    def _check_porcentage_distribution_cost(self):
        for record in self:
            if len(record.distribution_cost_information) > 0:
                porc_total = 0
                for distribution in record.distribution_cost_information:
                    porc_total += distribution.porcentage
                if porc_total != 100:
                    raise UserError(_('Los porcentajes de la distribución de costos no suman un 100%, por favor verificar.'))
    @api.constrains('dependents_information')
    def _check_dependents(self):
        for record in self:
            if len(record.dependents_information.filtered(lambda a: a.z_report_income_and_withholdings == True)) > 4:
                raise UserError(_('No puede reportar más de 4 dependientes en el certificado de ingresos y retenciones, por favor verificar.'))

    @api.constrains('identification_id')
    def _check_identification(self):
        for record in self:
            if record.identification_id != record.work_contact_id.vat:
                raise UserError(_('El número de identificación debe ser igual al tercero seleccionado.'))
            if record.identification_id != record.partner_encab_id.vat:
                raise UserError(_('El número de identificación debe ser igual al tercero seleccionado.'))

    @api.constrains('tipo_coti_id','social_security_entities','subtipo_coti_id')
    def _check_social_security_entities(self):
        for record in self:
            if record.tipo_coti_id or record.subtipo_coti_id:
                #Obtener parametrización de cotizantes
                obj_parameterization_contributors = self.env['hr.parameterization.of.contributors'].search(
                    [('type_of_contributor', '=', record.tipo_coti_id.id),
                     ('contributor_subtype', '=', record.subtipo_coti_id.id)],limit=1)
                if len(obj_parameterization_contributors) == 0:
                    raise ValidationError(_('No existe parametrización para este tipo de cotizante / subtipo de cotizante, por favor verificar.'))
                #Obtener las entidades seleccionadas del empleado
                qty_eps, qty_pension, qty_riesgo, qty_caja = 0, 0, 0, 0
                for entity in record.social_security_entities:
                    if entity.contrib_id.type_entities == 'eps':  # SALUD
                        qty_eps += 1
                    if entity.contrib_id.type_entities == 'pension':  # PENSION
                        qty_pension += 1
                    if entity.contrib_id.type_entities == 'riesgo':  # ARP
                        qty_riesgo += 1
                    if entity.contrib_id.type_entities == 'caja':  # CAJA DE COMPENSACIÓN
                        qty_caja += 1

                #Validar EPS
                if obj_parameterization_contributors.liquidates_eps_company or obj_parameterization_contributors.liquidated_eps_employee:
                    if qty_eps == 0:
                        raise ValidationError(_('El empleado no tiene entidad EPS asignada, por favor verificar.'))
                    if qty_eps > 1:
                        raise ValidationError(_('El empleado tiene más de una entidad EPS asignada, por favor verificar.'))

                # Validar PENSIÓN
                if obj_parameterization_contributors.liquidated_company_pension or obj_parameterization_contributors.liquidate_employee_pension or obj_parameterization_contributors.liquidates_solidarity_fund:
                    if qty_pension == 0:
                        raise ValidationError(_('El empleado no tiene entidad Pensión asignada, por favor verificar.'))
                    if qty_pension > 1:
                        raise ValidationError(_('El empleado tiene más de una entidad Pensión asignada, por favor verificar.'))

                # Validar ARL/ARP - Se comenta debido a que se maneja por compañia
                #if obj_parameterization_contributors.liquidated_arl:
                #    if qty_riesgo == 0:
                #        raise ValidationError(_('El empleado no tiene entidad ARL asignada, por favor verificar.'))
                #    if qty_riesgo > 1:
                #        raise ValidationError(_('El empleado tiene más de una entidad ARL asignada, por favor verificar.'))

                # Validar CAJA DE COMPENSACIÓN
                if obj_parameterization_contributors.liquidated_compensation_fund:
                    if qty_caja == 0:
                        raise ValidationError(_('El empleado no tiene entidad Caja de compensación asignada, por favor verificar.'))
                    if qty_caja > 1:
                        raise ValidationError(_('El empleado tiene más de una entidad Caja de compensación asignada, por favor verificar.'))

    @api.model_create_multi
    def create(self, values_list):
        for vals in values_list:
            if vals.get('work_contact_id') and not vals.get('partner_encab_id'):
                vals['partner_encab_id'] = vals.get('work_contact_id')
            if not vals.get('work_contact_id') and vals.get('partner_encab_id'):
                vals['work_contact_id'] = vals.get('partner_encab_id')
            if not vals.get('name'):
                partner_id = vals.get('partner_encab_id') or vals.get('work_contact_id')
                if partner_id:
                    vals['name'] = self.env['res.partner'].browse(partner_id).name
                elif vals.get('user_id'):
                    vals['name'] = self.env['res.users'].browse(vals['user_id']).name
            if not vals.get('name'):
                vals['name'] = _('Empleado')

            pid_tercero = vals.get('partner_encab_id') or vals.get('work_contact_id')
            if pid_tercero:
                vals['identification_id'] = self.env['res.partner'].browse(pid_tercero).vat or False

        res = super(hr_employee, self).create(values_list)
        for record in res:
            #Asignar tipo de tercero funcionario
            obj_type_thirdparty = self.env['zue.type_thirdparty'].search([('types', '=', '4')], limit=1)
            if len(obj_type_thirdparty) == 1:
                ids_type_thirdparty = record.partner_encab_id.x_type_thirdparty.ids
                id_type_thirdparty_employee = obj_type_thirdparty.id
                if id_type_thirdparty_employee not in ids_type_thirdparty:
                    ids_type_thirdparty.append(id_type_thirdparty_employee)
                    record.partner_encab_id.write({'x_type_thirdparty': ids_type_thirdparty})
        return res

    def write(self, vals):
        pid = vals.get('partner_encab_id')
        if pid:
            vals['identification_id'] = self.env['res.partner'].browse(pid).vat or False
        return super(hr_employee, self).write(vals)

    def get_info_version(self):
        for record in self:
            obj_version = self.env['hr.version'].search([('employee_id','=',record.id),('retirement_date','=',False)],limit=1)
            if len(obj_version) == 0:
                obj_version += self.env['hr.version'].search([('employee_id', '=', record.id), ('retirement_date', '!=', False)],limit=1)
            return obj_version

    def get_retirement_date_version(self):
        self.ensure_one()
        active_version = self.env['hr.version'].search([('employee_id', '=', self.id), ('retirement_date', '=', False)], order='contract_date_start desc', limit=1)
        if active_version:
            return active_version
        return self.env['hr.version'].search([('employee_id', '=', self.id), ('retirement_date', '!=', False)], order='retirement_date desc', limit=1)

    def get_age_for_date(self, o_date):
        if o_date:
            today = date.today()
            return today.year - o_date.year - ((today.month, today.day) < (o_date.month, o_date.day))
        else:
            return 0

    # Metodos reportes
    def get_report_print_badge_template(self):
        obj = self.env['report.print.badge.template'].search([('company_id','=',self.company_id.id)])
        if len(obj) == 0:
            raise ValidationError(_('No tiene configurada plantilla de identificación. Por favor verifique!'))
        return obj

    def get_name_rh(self):
        rh = dict(self._fields['licencia_rh'].selection).get(self.licencia_rh,'')
        return rh

    def get_name_type_document(self):
        type_document = self.partner_encab_id.l10n_latam_identification_type_id.name or ''
        return type_document

    def _sync_user(self, user, employee_has_image=False):
        vals = dict(
            work_email=user.email,
            user_id=user.id,
        )
        if not employee_has_image:
            vals['image_1920'] = user.image_1920 if user.image_1920 else self.image_1920
        if user.tz:
            vals['tz'] = user.tz
        return vals

    def generate_labor_certificate(self):
        self.ensure_one()
        return self.version_id.generate_labor_certificate()

    def generate_report_severance(self):
        self.ensure_one()
        return self.version_id.generate_report_severance()

    def print_book_vacaciones(self):
        self.ensure_one()
        return self.version_id.print_book_vacaciones()

    def print_book_cesantias(self):
        self.ensure_one()
        return self.version_id.print_book_cesantias()


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def write(self, vals):
        res = super().write(vals)
        if 'vat' not in vals:
            return res
        obj_employee = self.env['hr.employee']
        for partner in self:
            linked = obj_employee.search([
                '|',
                ('partner_encab_id', '=', partner.id),
                ('work_contact_id', '=', partner.id),
            ])
            if linked:
                linked.write({'identification_id': partner.vat or False})
        return res

class report_print_badge_template(models.Model):
    _name = 'report.print.badge.template'
    _description = 'Imprimir Identificación'

    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)
    with_extra_space = fields.Boolean('Con espacio extra')
    img_header_file = fields.Binary('Plantilla del identificación')
    img_header_filename = fields.Char('Plantilla del identificación filename')
    imgback_header_file = fields.Binary('Plantilla del identificación respaldo')
    imgback_header_filename = fields.Char('Plantilla del identificación filename respaldo')
    orientation = fields.Selection([('horizontal', 'Horizontal'),
                                    ('vertical', 'Vertical')], string='Orientación', default="horizontal")
    z_area_source = fields.Selection([('department', 'Departamento'), ('branch', 'Sucursal')], string='Área', default='department', required=True, help='Define si el carnet muestra el departamento o la sucursal del empleado.')
    z_layout_json = fields.Text(string='Layout carnet', default='{}')

    _company_report_print_badge_template = models.Constraint('unique(company_id)','Ya existe una configuración de plantilla de identificación para esta compañía, por favor verificar')

    @api.onchange('orientation')
    def onchangeOrientation(self):
        self.z_layout_json = json.dumps(self.getDefaultLayout())

    def getDefaultLayout(self):
        """Posiciones por defecto (cm) según orientación."""
        self.ensure_one()
        text = {
            'font_size': 5.5,
            'color': '#000000',
        }
        if self.orientation == 'vertical':
            return {
                'photo': {'top': 3.07, 'left': 0.49, 'width': 1.82, 'height': 2.74},
                'name': {'top': 3.45, 'left': 2.45, 'width': 2.75, 'height': 0.70, **text},
                'job': {'top': 4.50, 'left': 2.45, 'width': 2.75, 'height': 0.55, **text},
                'vat': {'top': 5.45, 'left': 2.85, 'width': 2.35, 'height': 0.35, **text},
                'rh': {'top': 6.15, 'left': 1.60, 'width': 1.20, 'height': 0.28, **text},
                'date': {'top': 6.75, 'left': 2.60, 'width': 2.00, 'height': 0.28, **text},
                'area': {'top': 7.90, 'left': 0.40, 'width': 4.70, 'height': 0.40, **text},
            }
        return {
            'photo': {'top': 2.40, 'left': 0.55, 'width': 2.90, 'height': 2.90},
            'name': {'top': 2.50, 'left': 3.80, 'width': 6.40, 'height': 0.80, **text},
            'job': {'top': 3.40, 'left': 3.80, 'width': 6.40, 'height': 0.55, **text},
            'vat': {'top': 4.00, 'left': 3.80, 'width': 6.40, 'height': 0.40, **text},
            'rh': {'top': 4.55, 'left': 3.80, 'width': 2.50, 'height': 0.35, **text},
            'date': {'top': 4.55, 'left': 6.50, 'width': 3.50, 'height': 0.35, **text},
            'area': {'top': 5.20, 'left': 3.80, 'width': 6.40, 'height': 0.40, **text},
        }

    def getLayout(self):
        """Layout guardado fusionado con defaults."""
        self.ensure_one()
        defaults = self.getDefaultLayout()
        try:
            saved = json.loads(self.z_layout_json or '{}') or {}
        except (TypeError, ValueError, json.JSONDecodeError):
            saved = {}
        layout = {}
        for key, default_box in defaults.items():
            box = dict(default_box)
            if isinstance(saved.get(key), dict):
                for attr in ('top', 'left', 'width', 'height', 'font_size'):
                    if attr in saved[key]:
                        try:
                            box[attr] = float(saved[key][attr])
                        except (TypeError, ValueError):
                            pass
                if saved[key].get('color'):
                    box['color'] = str(saved[key]['color'])
            layout[key] = box
        return layout

    def getFitFontSize(self, text, width_cm, height_cm, max_pt=7.0, min_pt=3.5, allow_wrap=True):
        """Reduce la fuente hasta que el texto quepa en el recuadro."""
        text = ' '.join((text or '').split()).upper()
        if not text:
            return max_pt
        width_pt = max(width_cm, 0.2) * 28.35
        height_pt = max(height_cm, 0.2) * 28.35
        size = max_pt
        while size >= min_pt:
            avg = size * 0.55  # ancho aproximado de mayúscula bold
            # 1) Intentar una sola línea
            if len(text) * avg <= width_pt and size * 1.05 <= height_pt:
                return round(size, 1)
            size -= 0.25
        if not allow_wrap:
            return min_pt
        # 2) Permitir varias líneas
        size = max_pt
        while size >= min_pt:
            avg = size * 0.55
            words = text.split()
            lines = 1
            line_w = 0.0
            fits = True
            for word in words:
                word_w = len(word) * avg
                gap = avg if line_w else 0.0
                if line_w + gap + word_w <= width_pt:
                    line_w += gap + word_w
                else:
                    lines += 1
                    line_w = word_w
                    if word_w > width_pt:
                        fits = False
                        break
            if fits and lines * size * 1.08 <= height_pt:
                return round(size, 1)
            size -= 0.25
        return min_pt

    def getElementStyle(self, element, text=''):
        """CSS absoluto para un elemento del carnet (reporte)."""
        self.ensure_one()
        box = self.getLayout().get(element) or self.getDefaultLayout()[element]
        style = (
            f"position:absolute;z-index:1;"
            f"top:{box['top']}cm;left:{box['left']}cm;"
            f"width:{box['width']}cm;height:{box['height']}cm;"
            f"overflow:hidden;letter-spacing:normal;word-spacing:normal;"
        )
        if element == 'photo':
            style += 'border-radius:0.18cm;'
            return style

        max_pt = float(box.get('font_size') or 5.5)
        color = box.get('color') or '#000000'
        font_size = self.getFitFontSize(
            text,
            box['width'],
            box['height'],
            max_pt=max_pt,
            min_pt=min(3.2, max_pt),
            allow_wrap=element in ('name', 'job'),
        )
        if element in ('name', 'job'):
            style += (
                f'font-size:{font_size}pt;font-weight:bold;line-height:1.05;'
                f'white-space:normal;word-break:break-word;color:{color};'
            )
        elif element == 'area':
            style += (
                f'font-size:{font_size}pt;font-weight:bold;text-align:center;'
                f'white-space:nowrap;color:{color};'
            )
        else:
            style += (
                f'font-size:{font_size}pt;font-weight:bold;line-height:1.1;'
                f'white-space:nowrap;color:{color};'
            )
        return style

    def actionResetLayout(self):
        """Restablece posiciones a los valores por defecto de la orientación."""
        for record in self:
            record.z_layout_json = json.dumps(record.getDefaultLayout())
        return True

