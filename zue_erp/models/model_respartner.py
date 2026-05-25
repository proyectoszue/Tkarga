# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

#---------------------------Modelo RES-PARTNER / TERCEROS-------------------------------#

class l10n_latam_identification_type(models.Model):
    _inherit = 'l10n_latam.identification.type'

    z_code_dian = fields.Char(string='Colombian Code DIAN')

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    type_account = fields.Selection([('A', 'Ahorros'), ('C', 'Corriente')], 'Tipo de Cuenta', required=True, default='A')
    is_main = fields.Boolean('Es Principal')

class x_areas(models.Model):
    _name = 'zue.areas'
    _description = 'Áreas'
    _order = 'code,name'

    code = fields.Char(string='Código', required=True)
    name = fields.Char(string='Nombre', required=True)

class x_job_title(models.Model):
    _name = 'zue.job_title'
    _description = 'Cargos'
    _order = 'area_id,code,name'

    area_id = fields.Many2one('zue.areas', string='Área')
    code = fields.Char(string='Código', required=True)
    name = fields.Char(string='Nombre', required=True)


class x_contact_types(models.Model):
    _name = 'zue.contact_types'
    _description = 'Tipos de contacto'

    code = fields.Char(string='Código', required=True)
    name = fields.Char(string='Nombre', required=True)

class ResPartner(models.Model):
    _inherit = 'res.partner'
    _order = 'name'

    #TRACK VISIBILITY OLD FIELDS
    vat = fields.Char(tracking=True)
    street = fields.Char(tracking=True)
    country_id = fields.Many2one(tracking=True)
    state_id = fields.Many2one(tracking=True)
    city_id = fields.Many2one(tracking=True, string="Ciudad")
    zip = fields.Char(tracking=True)
    phone = fields.Char(tracking=True)
    mobile = fields.Char(tracking=True)
    email = fields.Char(tracking=True)
    website = fields.Char(tracking=True)
    lang = fields.Selection(tracking=True)
    category_id = fields.Many2many(tracking=True)
    user_id = fields.Many2one(tracking=True)    
    comment = fields.Text(tracking=True)
    name = fields.Char(tracking=True)
    city = fields.Char(string='Descripción ciudad')

    x_contact_area = fields.Many2one('zue.areas', string='Área', tracking=True, ondelete='restrict')
    x_contact_job_title = fields.Many2one('zue.job_title', string='Cargo', tracking=True, ondelete='restrict')
    x_contact_type = fields.Many2many('zue.contact_types', string='Tipo de contacto', tracking=True, ondelete='restrict')
    x_city_code = fields.Char(related='city_id.z_code_dian', string='Código ciudad DIAN TMP (No usar)')

    #INFORMACION BASICA
    same_vat_partner_id = fields.Many2one('res.partner', string='Partner with same Tax ID', compute='_compute_no_same_vat_partner_id', store=False)
    x_type_thirdparty = fields.Many2many('zue.type_thirdparty',string='Tipo de tercero',required=True, tracking=True, ondelete='restrict')
    x_digit_verification = fields.Integer(string='Digito de verificación', tracking=True,compute='_compute_verification_digit', store=True)
    x_vat_expedition_date = fields.Date('Fecha de expedición documento')
    z_country_issuance_id = fields.Many2one('res.country', string='Pais de expedición documento')
    z_department_issuance_id = fields.Many2one('res.country.state', string='Departamento de expedición documento')
    z_city_issuance_id = fields.Many2one('zue.city', string='Ciudad de expedición documento TMP V15') # TMP MIENTRAS MIGRACION a v19 DESPUES SE DEBE ELIMINAR
    z_city_issuance_id_new = fields.Many2one('res.city', string='Ciudad de expedición documento')
    x_business_name = fields.Char(string='Nombre de negocio', tracking=True)
    x_first_name = fields.Char(string='Primer nombre', tracking=True)
    x_second_name = fields.Char(string='Segundo nombre', tracking=True)
    x_first_lastname = fields.Char(string='Primer apellido', tracking=True)
    x_second_lastname = fields.Char(string='Segundo apellido', tracking=True)
    
    #UBICACIÓN PRINCIPAL
    x_city = fields.Many2one('zue.city', string='Ciudad ZUE TMP V15', tracking=True, ondelete='restrict') # TMP MIENTRAS MIGRACION a v19 DESPUES SE DEBE ELIMINAR
    z_city_code = fields.Char(related='city_id.z_code_dian', string='Código ciudad DIAN')
    x_zip_id = fields.Many2one('zue.zip.code', string='Código postal', tracking=True, ondelete='restrict') #domain="[('code','like',x_city_code)]"
    z_neighborhood = fields.Char(string='Barrio', tracking=True)

    #CLASIFICACION
    x_organization_type = fields.Selection([('1', 'Empresa'),
                                            ('2', 'Universidad'),
                                            ('3', 'Centro de investigación'),
                                            ('4', 'Multilateral'),
                                            ('5', 'Gobierno'),
                                            ('6', 'ONG: Organización no Gubernamental')], string='Tipo de organización', tracking=True)
    x_ciiu_activity = fields.Many2one('zue.ciiu', string='Códigos CIIU', tracking=True, ondelete='restrict')

    #GRUPO EMPRESARIAL
    x_is_business_group = fields.Boolean(string='¿Es un Grupo Empresarial?', tracking=True)
    x_name_business_group = fields.Char(string='Nombre Grupo Empresarial', tracking=True)
    #Campos Informativos
    x_acceptance_data_policy = fields.Boolean(string='Acepta política de tratamiento de datos', tracking=True)
    x_acceptance_date = fields.Date(string='Fecha de aceptación', tracking=True)
    x_not_contacted_again = fields.Boolean(string='No volver a ser contactado', tracking=True)
    x_date_decoupling = fields.Date(string="Fecha de desvinculación", tracking=True)
    x_reason_desvinculation_text = fields.Text(string='Motivo desvinculación') 
    
    #INFORMACION FINANCIERA
    x_company_size = fields.Selection([
                                        ('1', 'Mipyme'),
                                        ('2', 'Pyme'),
                                        ('3', 'Mediana'),
                                        ('4', 'Grande')
                                    ], string='Tamaño empresa', tracking=True)

    #INFORMACION COMERCIAL
    x_account_origin = fields.Selection([
                                        ('1', 'Campañas'),
                                        ('2', 'Eventos'),
                                        ('3', 'Referenciado'),
                                        ('4', 'Telemercadeo'),
                                        ('5', 'Web'),
                                        ('6', 'Otro')
                                    ], string='Origen de la cuenta', tracking=True)
    
    @api.onchange('x_zip_id')
    @api.depends('x_zip_id')
    def _zip_update_zue(self):
        for record in self:
            if record.x_zip_id:
                record.zip = record.x_zip_id.code

    #Eliminar validaciones del VAT estandar
    @api.constrains('vat', 'country_id')
    def _check_vat(self, validation="error"):
        if self.sudo().env.ref('base.module_base_vat').state == 'installed':
            # Si tiene el pais tiene marcado el check z_skip_validation no validar el check_vat
            self = self.filtered(lambda partner: partner.country_id.z_skip_validation == False)
            return super(ResPartner, self)._check_vat()
        else:
            return True

    @api.depends('vat')
    def _compute_no_same_vat_partner_id(self):
        for partner in self:
            partner.same_vat_partner_id = ""

    @api.depends('vat','l10n_latam_identification_type_id','country_id')
    def _compute_verification_digit(self, return_digit=0):
        # Logica para calcular digito de verificación
        multiplication_factors = [71, 67, 59, 53, 47, 43, 41, 37, 29, 23, 19, 17, 13, 7, 3]
        digit = 0

        for partner in self:
            identification_type = partner.l10n_latam_identification_type_id
            has_co_document_code = (
                    identification_type
                    and 'l10n_co_document_code' in identification_type._fields
            )
            if has_co_document_code:
                if (partner.vat and partner.l10n_latam_identification_type_id.l10n_co_document_code == 'rut' and len(partner.vat) <= len(
                        multiplication_factors)) or return_digit:
                    number = 0
                    padded_vat = partner.vat.split('-')[0]

                    while len(padded_vat) < len(multiplication_factors):
                        padded_vat = '0' + padded_vat

                    # if there is a single non-integer in vat the verification code should be False
                    try:
                        for index, vat_number in enumerate(padded_vat):
                            number += int(vat_number) * multiplication_factors[index]

                        number %= 11

                        if number < 2:
                            digit = number
                        else:
                            digit = 11 - number

                        if not return_digit:
                            partner.x_digit_verification = digit
                        else:
                            return digit

                    except ValueError:
                        partner.x_digit_verification = False
                else:
                    partner.x_digit_verification = False
            else:
                partner.x_digit_verification = False

    @api.model
    def _run_vat_test(self, vat_number, default_country, partner_is_company=True):
        if default_country.z_skip_validation:
            return True
        else:
            res = super(ResPartner, self)._run_vat_test(vat_number, default_country, partner_is_company)
            return res

    #Onchange
    # @api.onchange('x_type_thirdparty')
    # def _onchange_type_thirdparty(self):
    #     for record in self:
    #         if record.x_type_thirdparty:
    #             for i in record.x_type_thirdparty:
    #                 print(i.id)
    #                 if i.id == 2 and record.company_type == 'company':
    #                     raise UserError(_('Una compañia no puede estar catalogada como contacto, por favor verificar.')) 
        
    @api.onchange('email')
    def _onchange_email(self):
        for record in self:
            if record.email:
                if not '@' in str(record.email):
                    self.email = False
                    raise UserError(_('El correo digitado no es valido, por favor verificar.'))

    @api.onchange('vat', 'country_id', 'company_id', 'l10n_latam_identification_type_id')
    def _onchange_vatnumber(self):
        for record in self:
            if record.vat:
                lst_character = ['.',',','*','@','-','_','°','!','|','"','#','$','%','&','/','(',')','=','?','¡','¿','{','}','<','>','^','+','[',']','~']
                for character in lst_character:
                    if character in record.vat:
                        raise UserError(_('El campo número de documento no debe contener caracteres especiales.'))

                identification_type = record.l10n_latam_identification_type_id
                has_co_document_code = (
                        identification_type
                        and 'l10n_co_document_code' in identification_type._fields
                )
                if has_co_document_code and record.l10n_latam_identification_type_id.l10n_co_document_code == 'rut' and len(record.vat) > 9:
                    raise UserError(_('El campo número de documento no debe tener mas de 9 dígitos cuando el tipo de documento es NIT.'))   

                company_id = record.company_id.id or self.env.company.id
                domain = [
                    ('x_type_thirdparty', 'in', [1, 3]),
                    ('vat', '=', record.vat),
                    '|', ('company_id', '=', False),
                    ('company_id', '=', company_id),
                    ('id', '!=', record.id),
                ]

                obj = self.search(domain, limit=1)
                if obj:
                    record.vat = ""
                    raise UserError(_('Ya existe un Cliente con este número de NIT.'))                    
                objArchivado = self.with_context(active_test=False).search(domain + [('active', '=', False)], limit=1)
                if objArchivado:
                    record.vat = ""
                    raise UserError(_('Ya existe un Cliente con este número de NIT pero se encuentra archivado.')) 
    
    #-----------Validaciones

    @api.model
    def _commercial_fields(self):
        res = super(ResPartner, self)._commercial_fields()
        if self.parent_id:
            res.remove('vat')
        return res

    @api.constrains('vat')
    def _check_vatnumber(self):
        for record in self:
            cant_vat = 0
            cant_vat_archivado = 0
            cant_vat_ind = 0
            cant_vat_archivado_ind = 0
            name_tercer =  ''
            user_create = ''
            if record.vat:
                company_id = record.company_id.id or self.env.company.id
                company_domain = ['|', ('company_id', '=', False), ('company_id', '=', company_id)]
                obj = self.search([('is_company', '=', True), ('vat', '=', record.vat)] + company_domain)
                if obj:
                    for tercer in obj:
                        cant_vat = cant_vat + 1
                        if tercer.id != record.id:
                            name_tercer = tercer.name or ''
                            user_create = tercer.create_uid.name or ''

                objArchivado = self.search([('is_company', '=', True), ('vat', '=', record.vat), ('active', '=', False)] + company_domain)
                if objArchivado:
                    for tercer in objArchivado:
                        cant_vat_archivado = cant_vat_archivado + 1
                        if tercer.id != record.id:
                            name_tercer = tercer.name or ''
                            user_create = tercer.create_uid.name or ''

                obj_ind = self.search([('is_company', '=', False), ('vat', '=', record.vat)] + company_domain)
                if obj_ind:
                    for tercer in obj_ind:
                        if tercer.parent_id.vat != record.vat:
                            cant_vat_ind = cant_vat_ind + 1
                            if tercer.id != record.id:
                                name_tercer = tercer.name or ''
                                user_create = tercer.create_uid.name or ''

                objArchivado_ind = self.search([('is_company', '=', False), ('vat', '=', record.vat), ('active', '=', False)] + company_domain)
                if objArchivado_ind:
                    for tercer in objArchivado_ind:
                        if tercer.parent_id.vat != record.vat:
                            cant_vat_archivado_ind = cant_vat_archivado_ind + 1
                            if tercer.id != record.id:
                                name_tercer = tercer.name or ''
                                user_create = tercer.create_uid.name or ''
            if cant_vat > 1:
                raise ValidationError(_('Ya existe un Cliente ('+name_tercer+') con este número de NIT creado por '+user_create+'.'))                
            if cant_vat_archivado > 1:
                raise ValidationError(_('Ya existe un Cliente ('+name_tercer+') con este número de NIT pero se encuentra archivado, fue creado por '+user_create+'.'))                
            if cant_vat_ind > 1:
                raise ValidationError(_('Ya existe un Tercero ('+name_tercer+') con este número de ID creado por '+user_create+'.'))                
            if cant_vat_archivado_ind > 1:
                raise ValidationError(_('Ya existe un Tercero ('+name_tercer+') con este número de ID pero se encuentra archivado, fue creado por '+user_create+'.'))

    @api.constrains('bank_ids')
    def _check_bank_ids(self):
        for record in self:
            if len(record.bank_ids) > 0:
                count_main = 0
                for bank in record.bank_ids:
                    count_main += 1 if bank.is_main else 0
                if count_main > 1:
                    raise ValidationError(_('No puede tener más de una cuenta principal, por favor verificar.'))

    @api.constrains('x_type_thirdparty','name','vat','street','state_id','country_id','phone','mobile','email')
    def _check_fields_required(self):
        # Verificar que el usuario este logueado
        public_user = self.env.user._is_public()
        # Verificar si es usuario de simulación para website
        website_simulation_partner = False
        try:
            for record in self:
                if record.website_url.find('simulation') != -1:
                    website_simulation_partner = True
        except:
            website_simulation_partner = False
        #Validaciones correspondientes
        if self.env.user.name != 'OdooBot' and self.env.user.login != '__system__' and public_user == False and website_simulation_partner == False: # Se omite esta validación con datos DEMO ESTANDAR DE ODOO
            for record in self:
                if len(record.x_type_thirdparty) > 0:
                    # Si es Cliente, Proveedor o Funcionario mantener las validaciones.
                    ids_type_thirdparty_validate = self.env['zue.type_thirdparty'].search([('types', 'in', ['1', '3', '4'])]).ids
                    validate = False
                    for type_process in record.x_type_thirdparty.ids:
                        validate = True if type_process in ids_type_thirdparty_validate else validate
                    if validate:
                        record.validate_check_fields_required()

    def validate_check_fields_required(self):
        if self.env.context.get('from_multicash'):
            return True

        for record in self:
            responsable = 'tercero'
            if len(record.x_type_thirdparty) == 0:
                raise ValidationError(_(f'Debe seleccionar un tipo de tercero para {str(record.name)}, por favor verificar.'))

            if record.parent_id:
                name = ' ' + record.name if record.name else ''
                responsable = 'contacto' + name

            if not record.parent_id:
                if not record.l10n_latam_identification_type_id:
                    raise ValidationError(_('Debe seleccionar el tipo de documento del ' + responsable + ', por favor verificar.'))
                if not record.vat:
                    raise ValidationError(_('Debe digitar el número de documento del ' + responsable + ', por favor verificar.'))
                if not record.phone and not record.mobile:
                    raise ValidationError(_('Debe digitar el telefono o móvil del ' + responsable + ', por favor verificar.'))

            if not record.name:
                raise ValidationError(_('Debe digitar el nombre del ' + responsable + ', por favor verificar.'))
            if not record.street:
                raise ValidationError(_('Debe digitar la dirección del ' + responsable + ', por favor verificar.'))
            if not record.state_id:
                raise ValidationError(_('Debe digitar el departamento del ' + responsable + ', por favor verificar.'))
            if not record.city_id:
                raise ValidationError(_('Debe digitar la ciudad del ' + responsable + ', por favor verificar.'))
            if not record.country_id:
                raise ValidationError(_('Debe digitar el país del ' + responsable + ', por favor verificar.'))
            if not record.email:
                raise ValidationError(_('Debe digitar el correo electrónico del ' + responsable + ', por favor verificar.'))
        return True

    def validate_fields_mandatory_type_thirdparty(self):
        for record in self:
            ldict = {'record': record}
            for type_thirdparty in record.x_type_thirdparty:
                for field in type_thirdparty.fields_mandatory:
                    exec('return_value = record.'+field.name, ldict)
                    return_value = ldict.get('return_value',False)
                    if not return_value:
                        raise ValidationError(_('El campo ' + field.field_description + ' es obligatorio para el tipo de tercero '+ type_thirdparty.name +', por favor verificar.'))
        return True

    @api.depends('city_id')
    @api.onchange('city_id')
    def _onchange_city_id(self):
        for record in self:
            record.city = record.city_id.name

    @api.onchange('x_first_name','x_second_name','x_first_lastname','x_second_lastname')
    def _onchange_info_names(self):
        for record in self:
            if record.company_type == 'person':
                fn = record.x_first_name if record.x_first_name else ''
                sn = record.x_second_name if record.x_second_name else ''
                fl = record.x_first_lastname if record.x_first_lastname else ''
                sl = record.x_second_lastname if record.x_second_lastname else ''

                name_partner = ''
                name_partner = name_partner+fn if fn != '' else name_partner
                name_partner = name_partner+" "+sn if sn != '' and name_partner != '' else name_partner+sn            
                name_partner = name_partner+" "+fl if fl != '' and name_partner != '' else name_partner+fl            
                name_partner = name_partner+" "+sl if sl != '' and name_partner != '' else name_partner+sl

                record.name = name_partner.upper()
                record.x_first_name = record.x_first_name.upper() if record.x_first_name else False
                record.x_second_name = record.x_second_name.upper() if record.x_second_name else False
                record.x_first_lastname = record.x_first_lastname.upper() if record.x_first_lastname else False
                record.x_second_lastname = record.x_second_lastname.upper() if record.x_second_lastname else False

    @api.onchange('name')
    def _onchange_info_name_upper(self):
        for record in self:            
            record.name = record.name.upper() if record.name else False

    @api.model_create_multi
    def create(self, values_list):
        for vals in values_list:
            if vals.get('name',False):
                vals['name'] = vals.get('name',False).upper()
            if vals.get('x_first_name',False):
                vals['x_first_name'] = vals.get('x_first_name',False).upper()
            if vals.get('x_second_name', False):
                vals['x_second_name'] = vals.get('x_second_name', False).upper()
            if vals.get('x_first_lastname', False):
                vals['x_first_lastname'] = vals.get('x_first_lastname', False).upper()
            if vals.get('x_second_lastname', False):
                vals['x_second_lastname'] = vals.get('x_second_lastname', False).upper()
            if vals.get('x_type_thirdparty',False) == False:
                ids_type_thirdparty_contact = self.env['zue.type_thirdparty'].search([('types', 'in', ['2'])]).ids
                vals['x_type_thirdparty'] = ids_type_thirdparty_contact

        self = self.with_context(no_vat_validation=True)
        res = super(ResPartner, self).create(values_list)
        res.validate_fields_mandatory_type_thirdparty()
        return res

    def write(self, vals):
        if vals.get('name', False):
            vals['name'] = vals.get('name', False).upper()
        if vals.get('x_first_name', False):
            vals['x_first_name'] = vals.get('x_first_name', False).upper()
        if vals.get('x_second_name', False):
            vals['x_second_name'] = vals.get('x_second_name', False).upper()
        if vals.get('x_first_lastname', False):
            vals['x_first_lastname'] = vals.get('x_first_lastname', False).upper()
        if vals.get('x_second_lastname', False):
            vals['x_second_lastname'] = vals.get('x_second_lastname', False).upper()
        self = self.with_context(no_vat_validation=True)
        res = super(ResPartner, self).write(vals)
        for record in self:
            record.validate_fields_mandatory_type_thirdparty()
        return res