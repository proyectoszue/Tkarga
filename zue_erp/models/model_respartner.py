# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

#---------------------------Modelo RES-PARTNER / TERCEROS-------------------------------#
class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    type_account = fields.Selection([('A', 'Ahorros'), ('C', 'Corriente')], 'Tipo de Cuenta', required=True, default='A')
    is_main = fields.Boolean('Es Principal')
    
class ResPartner(models.Model):
    _inherit = 'res.partner'
    _order = 'name'

    #TRACK VISIBILITY OLD FIELDS
    vat = fields.Char(tracking=True)
    street = fields.Char(tracking=True)
    country_id = fields.Many2one(tracking=True)
    state_id = fields.Many2one(tracking=True)
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

    #INFORMACION BASICA
    same_vat_partner_id = fields.Many2one('res.partner', string='Partner with same Tax ID', compute='_compute_no_same_vat_partner_id', store=False)
    x_type_thirdparty = fields.Many2many('zue.type_thirdparty',string='Tipo de tercero',required=True, tracking=True, ondelete='restrict', domain="['|',('is_company','=',is_company),('is_individual','!=',is_company)]") 
    x_document_type = fields.Selection([
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
                                    ], string='Tipo de documento', tracking=True, default='13')
    x_digit_verification = fields.Integer(string='Digito de verificación', tracking=True,compute='_compute_verification_digit', store=True)
    x_vat_expedition_date = fields.Date('Fecha de expedición documento')
    z_country_issuance_id = fields.Many2one('res.country', string='Pais de expedición documento')
    z_department_issuance_id = fields.Many2one('res.country.state', string='Departamento de expedición documento')
    z_city_issuance_id = fields.Many2one('zue.city', string='Ciudad de expedición documento')
    x_business_name = fields.Char(string='Nombre de negocio', tracking=True)
    x_first_name = fields.Char(string='Primer nombre', tracking=True)
    x_second_name = fields.Char(string='Segundo nombre', tracking=True)
    x_first_lastname = fields.Char(string='Primer apellido', tracking=True)
    x_second_lastname = fields.Char(string='Segundo apellido', tracking=True)
    
    #UBICACIÓN PRINCIPAL
    x_city = fields.Many2one('zue.city', string='Ciudad ZUE', tracking=True, ondelete='restrict')
    x_city_code = fields.Char(related='x_city.code', string='Código ciudad zue')
    x_zip_id = fields.Many2one('zue.zip.code', string='Código postal', tracking=True, ondelete='restrict') #domain="[('code','like',x_city_code)]"
    z_neighborhood = fields.Char(string='Barrio', tracking=True)

    #CLASIFICACION
    x_organization_type = fields.Selection([('1', 'Empresa'),
                                            ('2', 'Universidad'),
                                            ('3', 'Centro de investigación'),
                                            ('4', 'Multilateral'),
                                            ('5', 'Gobierno'),
                                            ('6', 'ONG: Organización no Gubernamental')], string='Tipo de organización', tracking=True)
    x_work_groups = fields.Many2many('zue.work_groups', string='Grupos de trabajo', tracking=True, ondelete='restrict')
    x_sector_id = fields.Many2one('zue.sectors', string='Sector', tracking=True, ondelete='restrict')
    x_ciiu_activity = fields.Many2one('zue.ciiu', string='Códigos CIIU', tracking=True, ondelete='restrict')

    #GRUPO EMPRESARIAL
    x_is_business_group = fields.Boolean(string='¿Es un Grupo Empresarial?', tracking=True)
    x_name_business_group = fields.Char(string='Nombre Grupo Empresarial', tracking=True)

    #VINCULACION 
    x_active_vinculation = fields.Boolean(string='Estado de la vinculación', tracking=True)
    x_date_vinculation = fields.Date(string="Fecha de vinculación", tracking=True)
    x_type_vinculation = fields.Many2many('zue.vinculation_types', string='Tipo de vinculación', tracking=True, ondelete='restrict')
    #Campos Informativos
    x_acceptance_data_policy = fields.Boolean(string='Acepta política de tratamiento de datos', tracking=True)
    x_acceptance_date = fields.Date(string='Fecha de aceptación', tracking=True)
    x_not_contacted_again = fields.Boolean(string='No volver a ser contactado', tracking=True)
    x_date_decoupling = fields.Date(string="Fecha de desvinculación", tracking=True)
    x_reason_desvinculation_text = fields.Text(string='Motivo desvinculación') 
    
    #INFORMACION FINANCIERA
    x_asset_range = fields.Many2one('zue.asset_range', string='Rango de activos', tracking=True, ondelete='restrict')
    x_date_update_asset = fields.Date(string='Fecha de última modificación', compute='_date_update_asset', store=True, tracking=True)
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
    

    #INFORMACIÓN CONTACTO
    x_contact_type = fields.Many2many('zue.contact_types', string='Tipo de contacto', tracking=True, ondelete='restrict')
    x_contact_job_title = fields.Many2one('zue.job_title', string='Cargo', tracking=True, ondelete='restrict')
    x_contact_area = fields.Many2one('zue.areas', string='Área', tracking=True, ondelete='restrict')

    #MANTENIMIENTO
    #is_work_place = fields.Boolean('Is Work Place?')
    @api.depends('street', 'zip', 'x_city', 'country_id')
    def _compute_complete_address(self):
        for record in self:
            record.contact_address_complete = ''
            if record.street:
                record.contact_address_complete += record.street + ', '
            if record.zip:
                record.contact_address_complete += record.zip + ' '
            if record.x_city:
                record.contact_address_complete += record.x_city.name + ', '
            if record.state_id:
                record.contact_address_complete += record.state_id.name + ', '
            if record.country_id:
                record.contact_address_complete += record.country_id.name
            record.contact_address_complete = record.contact_address_complete.strip().strip(',')

    @api.onchange('x_city')
    @api.depends('x_city')
    def _city_update_zue(self):
        for record in self:
            if record.x_city:
                record.city = record.x_city.name

    @api.onchange('x_zip_id')
    @api.depends('x_zip_id')
    def _zip_update_zue(self):
        for record in self:
            if record.x_zip_id:
                record.zip = record.x_zip_id.code

    #Eliminar validaciones del VAT estandar
    @api.constrains('vat', 'country_id')
    def check_vat(self):
        if self.sudo().env.ref('base.module_base_vat').state == 'installed':
            # Si tiene el pais tiene marcado el check x_skip_validation no validar el check_vat
            self = self.filtered(lambda partner: partner.country_id.x_skip_validation == False)
            return super(ResPartner, self).check_vat()
        else:
            return True

    @api.depends('x_asset_range')
    def _date_update_asset(self):
        for record in self:
            record.x_date_update_asset = fields.Date.today()

    @api.depends('vat')
    def _compute_no_same_vat_partner_id(self):
        for partner in self:
            partner.same_vat_partner_id = ""

    @api.depends('vat','x_document_type')
    def _compute_verification_digit(self, return_digit=0):
        # Logica para calcular digito de verificación
        multiplication_factors = [71, 67, 59, 53, 47, 43, 41, 37, 29, 23, 19, 17, 13, 7, 3]
        digit = 0

        for partner in self:
            if (partner.vat and partner.x_document_type == '31' and len(partner.vat) <= len(
                    multiplication_factors)) or return_digit:
                number = 0
                padded_vat = partner.vat

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

    @api.model
    def _run_vat_test(self, vat_number, default_country, partner_is_company=True):
        if default_country.x_skip_validation:
            return True
        else:
            res = super(ResPartner, self)._run_vat_test(vat_number, default_country, partner_is_company)
            return res

    #---------------Search
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if self._context.get('search_by_vat', False):
            if name:
                args = args if args else []
                args.extend(['|', ['name', 'ilike', name], ['vat', 'ilike', name]])
                name = ''
        return super(ResPartner, self).name_search(name=name, args=args, operator=operator, limit=limit)

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

    @api.onchange('vat')
    def _onchange_vatnumber(self):
        for record in self:
            if record.vat:
                lst_character = ['.',',','*','@','-','_','°','!','|','"','#','$','%','&','/','(',')','=','?','¡','¿','{','}','<','>','^','+','[',']','~']
                for character in lst_character:
                    if character in record.vat:
                        raise UserError(_('El campo número de documento no debe contener caracteres especiales.'))                    
                if record.x_document_type == '31' and len(record.vat) > 9:
                    raise UserError(_('El campo número de documento no debe tener mas de 9 dígitos cuando el tipo de documento es NIT.'))   

                obj = self.search([('x_type_thirdparty','in',[1,3]),('vat','=',record.vat)])
                if obj:
                    self.vat = ""
                    raise UserError(_('Ya existe un Cliente con este número de NIT.'))                    
                objArchivado = self.search([('x_type_thirdparty','in',[1,3]),('vat','=',record.vat),('active','=',False)])
                if objArchivado:
                    self.vat = ""
                    raise UserError(_('Ya existe un Cliente con este número de NIT pero se encuentra archivado.')) 
    
    #-----------Validaciones

    @api.depends('x_document_type')
    @api.onchange('x_document_type')
    def assign_identification_type(self):
        if self.x_document_type:
            label = ''
            kay_val_dict = dict(self._fields['x_document_type'].selection)
            for key, val in kay_val_dict.items():
                if key == self.x_document_type:
                    label = val
                    break

            obj_identification = self.env['l10n_latam.identification.type'].search([('name', '=', label)], limit=1)

            if obj_identification:
                self.l10n_latam_identification_type_id = obj_identification.id
            else:
                obj_identification = self.env['l10n_latam.identification.type'].search([('name', '=', 'NIT')], limit=1)
                self.l10n_latam_identification_type_id = obj_identification.id

    #Se elimina el campo vat de los commercial_fields cuando es un contacto hijo para que no herede la identificacion del padre
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
                obj = self.search([('is_company', '=', True),('vat','=',record.vat)])
                if obj:
                    for tercer in obj:
                        cant_vat = cant_vat + 1
                        if tercer.id != record.id:
                            name_tercer = tercer.name
                            user_create = tercer.create_uid.name

                objArchivado = self.search([('is_company', '=', True),('vat','=',record.vat),('active','=',False)])
                if objArchivado:
                    for tercer in objArchivado:
                        cant_vat_archivado = cant_vat_archivado + 1
                        if tercer.id != record.id:
                            name_tercer = tercer.name
                            user_create = tercer.create_uid.name

                obj_ind = self.search([('is_company', '=', False),('vat','=',record.vat)])
                if obj_ind:
                    for tercer in obj_ind:
                        if tercer.parent_id:
                            if tercer.parent_id.vat != record.vat:
                                cant_vat_ind = cant_vat_ind + 1
                                if tercer.id != record.id:
                                    name_tercer = tercer.name
                                    user_create = tercer.create_uid.name

                objArchivado_ind = self.search([('is_company', '=', False),('vat','=',record.vat),('active','=',False)])
                if objArchivado_ind:
                    for tercer in objArchivado_ind:
                        if tercer.parent_id.vat != record.vat:
                            cant_vat_archivado_ind = cant_vat_archivado_ind + 1
                            if tercer.id != record.id:
                                name_tercer = tercer.name
                                user_create = tercer.create_uid.name
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

    @api.constrains('x_type_thirdparty','name','x_document_type','vat','street','state_id','country_id','x_city','phone','mobile','email')
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
        for record in self:
            responsable = 'tercero'
            if len(record.x_type_thirdparty) == 0:
                raise ValidationError(_(f'Debe seleccionar un tipo de tercero para {str(record.name)}, por favor verificar.'))

            if record.parent_id:
                name = ' ' + record.name if record.name else ''
                responsable = 'contacto' + name

            if not record.parent_id:
                if not record.x_document_type:
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
            if not record.x_city:
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

    @api.model
    def create(self, vals):
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
        res = super(ResPartner, self).create(vals)
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