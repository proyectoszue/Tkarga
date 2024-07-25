from odoo import fields, models, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    z_has_expired_documents = fields.Boolean(string='Tiene documentos expirados',compute='_compute_has_expired_documents', store=True)
    z_has_to_expired_documents = fields.Boolean(string='Tiene documentos por expirar',compute='_compute_has_expired_documents', store=True)
    z_has_request_documents = fields.Boolean(string='Tiene documentos solicitados',compute='_compute_has_expired_documents', store=True)

    @api.depends('address_home_id')
    def _compute_has_expired_documents(self):
        for record in self:
            lst_documents = []
            qty_expired, qty_to_expire, qty_request = 0, 0, 0
            datetime_today = datetime.now()
            obj_documents = self.env['documents.document'].search([('partner_id', '=', record.address_home_id.id)])
            for document in obj_documents:
                # Verificar documentos expirados
                expired, to_expire = False, False
                if document.expiration_date and document.type != 'empty':
                    equivalent_documents = self.env['documents.document']
                    for tag in document.tag_ids:
                        equivalent_documents += self.env['documents.document'].search(
                            [('partner_id', '=', record.address_home_id.id),
                             ('tag_ids', 'in', tag.id),
                             '|', ('expiration_date', '=', False),
                             ('expiration_date', '>', document.expiration_date)])
                    if document.expiration_date < datetime_today.date() and len(equivalent_documents) == 0:
                        expired = True
                    else:
                        if (document.expiration_date - datetime_today.date()).days <= 14 and len(equivalent_documents) == 0:
                            to_expire = True
                    qty_expired += 1 if expired else 0
                    qty_to_expire += 1 if to_expire else 0
                if document.type == 'empty':
                    qty_request += 1
            record.z_has_expired_documents = True if qty_expired > 0 else False
            record.z_has_to_expired_documents = True if qty_to_expire > 0 else False
            record.z_has_request_documents = True if qty_request > 0 else False

    def get_info_curriculum_vitae_portal(self):
        lst_curriculum = []
        for curriculum in self.resume_line_ids:
            dict_curriculum = {'id':curriculum.id,
                        'name':curriculum.name,
                        'type':curriculum.line_type_id.name if curriculum.line_type_id else 'Otro',
                        'display_type':curriculum.display_type,
                        'description': curriculum.description,
                        'date_start':curriculum.date_start,
                        'date_end':curriculum.date_end}
            lst_curriculum.append(dict_curriculum)
        return lst_curriculum

    def get_info_skills_portal(self):
        lst_skills = []
        for skill in self.employee_skill_ids:
            dict_skill = {'id':skill.id,
                        'type':skill.skill_type_id.name,
                        'skill':skill.skill_id.name,
                        'which_is': skill.which_is if skill.which_is else '',
                        'level': skill.skill_level_id.name,
                        'progress':skill.level_progress}
            lst_skills.append(dict_skill)
        return lst_skills

    def get_info_social_security_portal(self):
        lst_social_security = []
        for ss in self.social_security_entities:
            dict_ss = {'id':ss.id,
                        'contrib':ss.contrib_id.type_entities,
                        'type_entity':ss.contrib_id.name,
                        'entity':ss.partner_id.partner_id.name,
                        'date_change':ss.date_change}
            lst_social_security.append(dict_ss)
        return lst_social_security

    def get_info_dependents_portal(self):
        lst_dependents = []
        for dependent in self.dependents_information:
            dict_dependent = {'id':dependent.id,
                        'type':dependent.dependents_type.capitalize() if dependent.dependents_type else '',
                        'name':dependent.name if dependent.name else '',
                        'genero':dependent.genero.capitalize() if dependent.genero else '',
                        'date_birthday':dependent.date_birthday if dependent.date_birthday else ''}
            lst_dependents.append(dict_dependent)
        return lst_dependents

    def get_info_documents_portal(self,user_id=0,cant_expirados=0):
        lst_documents = []
        qty_expired,qty_to_expire = 0,0
        datetime_today = datetime.now(timezone(self.env.user.tz))
        obj_documents = self.env['documents.document'].search([('partner_id','=',self.address_home_id.id)])
        for document in obj_documents:
            is_visible = False
            if len(document.folder_id.read_group_ids) == 0:
                is_visible = True
            else:
                for permissions in document.folder_id.read_group_ids:
                    if user_id in permissions.users.ids:
                        is_visible = True

            if is_visible == True:
                #Verificar documentos expirados
                expired,to_expire = False,False
                if document.expiration_date:
                    equivalent_documents = self.env['documents.document']
                    for tag in document.tag_ids:
                        equivalent_documents += self.env['documents.document'].search([('partner_id', '=', self.address_home_id.id),
                                                                                        ('tag_ids', 'in', tag.id),
                                                                                         '|', ('expiration_date', '=', False),
                                                                                                ('expiration_date', '>', document.expiration_date)])
                    if document.expiration_date < datetime_today.date() and len(equivalent_documents) == 0:
                        expired = True
                    else:
                        if (document.expiration_date - datetime_today.date()).days <= 14 and len(equivalent_documents) == 0:
                            to_expire = True
                #Verificar si es solicitud de documento
                document_link = ''
                if document.type == 'empty':
                    obj_share = self.env['documents.share'].search([('document_ids','in',document.id)],limit=1)
                    if len(obj_share) == 0:
                        share_vals = {
                            'name': document.name,
                            'type': 'ids',
                            'folder_id': document.folder_id.id,
                            'partner_id': self.address_home_id.id if self.address_home_id else False,
                            'owner_id': user_id,
                            'document_ids': [document.id],
                        }
                        share = self.env['documents.share'].with_user(document.create_uid.id).create(share_vals)
                    else:
                        share = obj_share
                    base_url = False
                    if self.env.user.company_id.website_id:
                        base_url = self.env.user.company_id.website_id.domain
                    if not base_url:
                        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
                    document_link = base_url + '/document/share/' + str(share.id) + '/' + str(share.access_token)
                # Objeto a retornar
                dict_document = {'id': document.id,
                              'name': document.name,
                              'folder': document.folder_id.name,
                              'categories': document.tag_ids,
                              'create_date': document.create_date.date(),
                              'expiration_date': document.expiration_date,
                              'expired': expired,
                              'to_expire': to_expire,
                              'attachment':document.attachment_id.datas,
                              'mimetype':document.mimetype,
                              'document_request': True if document.type == 'empty' else False,
                              'document_link': document_link if document.type == 'empty' else False}
                lst_documents.append(dict_document)
                qty_expired += 1 if expired else 0
                qty_to_expire += 1 if to_expire else 0
        if cant_expirados == 0:
            return lst_documents
        else:
            return {'qty_expired':qty_expired, 'qty_to_expire':qty_to_expire}

    def get_info_absences_portal(self):
        lst_absences = []
        obj_absences = self.env['hr.leave'].search([('employee_id', '=', self.id)])
        for absences in obj_absences:
            dict_state = {'draft': 'Por enviar',
                          'confirm': 'Por aprobar',
                          'refuse': 'Rechazado',
                          'validate1': 'Segunda aprobación',
                          'validate': 'Aprobado'}
            label_state = dict_state.get(absences.state,'')
            dict_absences = {'id': absences.id,
                             'holiday': absences.holiday_status_id.name,
                             'date_from': absences.date_from.date(),
                             'date_to': absences.date_to.date(),
                             'number_days': absences.number_of_days,
                             'name': absences.name,
                             'state': label_state}
            lst_absences.append(dict_absences)
        return lst_absences

class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    identification_id = fields.Char(readonly=True)
    address_home_id = fields.Many2one('res.partner',readonly=True)
    personal_mobile = fields.Char(readonly=True)
    birthday = fields.Date(readonly=True)
    type_employee = fields.Many2one('hr.types.employee',readonly=True)
    personal_email = fields.Char(readonly=True)
    gender = fields.Char(string='Genero')
    branch_id = fields.Many2one('zue.res.branch',string='Sucursal')
    mobile_phone = fields.Char(readonly=True)
    work_phone = fields.Char(readonly=True)
    licencia_rh = fields.Char(readonly=True)
    licencia_categoria = fields.Char(readonly=True)
    licencia_vigencia = fields.Date(readonly=True)
    licencia_restricciones = fields.Char(readonly=True)
    country_id = fields.Many2one('res.country',readonly=True)
    place_of_birth = fields.Char(readonly=True)
    country_of_birth = fields.Many2one('res.country',readonly=True)
    emergency_contact = fields.Char(readonly=True)
    emergency_phone = fields.Char(readonly=True)
    emergency_relationship = fields.Char(readonly=True)
    certificate = fields.Char(readonly=True)
    front_back = fields.Char(readonly=True)
    confianza_manejo = fields.Boolean(readonly=True)
    type_thirdparty = fields.Many2one('zue.type_thirdparty',readonly=True)
    info_project = fields.Char(readonly=True)
    ed_qualification = fields.Float(readonly=True)
    ed_observation = fields.Text(readonly=True)
    study_field = fields.Char(readonly=True)
    study_school = fields.Char(readonly=True)
    marital = fields.Char(readonly=True)
    contract_id = fields.Many2one('hr.contract.public',string='Contrato')
    #Campos Zue
    partner_encab_id = fields.Many2one('res.partner',readonly=True)
    type_employee = fields.Many2one('hr.types.employee',readonly=True)
    sabado = fields.Boolean(readonly=True)
    certificate = fields.Char(readonly=True)
    personal_email = fields.Char(readonly=True)
    personal_mobile = fields.Char(readonly=True)
    type_job = fields.Char(readonly=True)
    emergency_relationship = fields.Char(readonly=True)
    extranjero = fields.Boolean(readonly=True)
    residente = fields.Boolean(readonly=True)
    date_of_residence_abroad = fields.Date(readonly=True)
    tipo_coti_id = fields.Many2one('hr.tipo.cotizante',readonly=True)
    subtipo_coti_id = fields.Many2one('hr.subtipo.cotizante',readonly=True)
    type_identification = fields.Char(readonly=True)
    indicador_especial_id = fields.Many2one('hr.indicador.especial.pila',readonly=True)
    cost_assumed_by = fields.Char(readonly=True)
    licencia_rh = fields.Char(readonly=True)
    licencia_categoria = fields.Char(readonly=True)
    licencia_vigencia = fields.Date(readonly=True)
    licencia_restricciones = fields.Char(readonly=True)
    operacion_retirar = fields.Boolean(readonly=True)
    operacion_reemplazo = fields.Many2one('hr.employee',readonly=True)
    type_identification_spouse = fields.Char(readonly=True)
    num_identification_spouse = fields.Char(readonly=True)
    spouse_phone = fields.Char(readonly=True)
    z_employee_age = fields.Integer(readonly=True)
    z_stratum = fields.Char(readonly=True)
    z_sexual_orientation = fields.Char(readonly=True)
    z_sexual_orientation_other = fields.Char(readonly=True)
    z_ethnic_group = fields.Char(readonly=True)
    z_housing_area = fields.Char(readonly=True)
    z_health_risk_factors = fields.Char(readonly=True)
    z_religion = fields.Char(readonly=True)
    z_victim_armed_conflict = fields.Char(readonly=True)
    z_academic_data = fields.Char(readonly=True)
    z_city_birth_id = fields.Many2one('zue.city',readonly=True)
    z_department_birth_id = fields.Many2one('res.country.state',readonly=True)
    z_military_passbook = fields.Boolean(readonly=True)
    branch_social_security_id = fields.Many2one('hr.social.security.branches',readonly=True)
    work_center_social_security_id = fields.Many2one('hr.social.security.work.center',readonly=True)
    z_has_expired_documents = fields.Boolean(readonly=True)
    z_has_to_expired_documents = fields.Boolean(readonly=True)
    z_has_request_documents = fields.Boolean(readonly=True)


    def get_info_curriculum_vitae_portal(self):
        return self.sudo().env['hr.employee'].search([('id','=',self.id)]).get_info_curriculum_vitae_portal()

    def get_info_skills_portal(self):
        return self.sudo().env['hr.employee'].search([('id','=',self.id)]).get_info_skills_portal()

    def get_info_social_security_portal(self):
        return self.sudo().env['hr.employee'].search([('id','=',self.id)]).get_info_social_security_portal()

    def get_info_dependents_portal(self):
        return self.sudo().env['hr.employee'].search([('id','=',self.id)]).get_info_dependents_portal()

    def get_info_documents_portal(self,user_id=0,cant_expirados=0):
        return self.sudo().env['hr.employee'].search([('id','=',self.id)]).get_info_documents_portal(user_id,cant_expirados)

    def get_info_absences_portal(self):
        return self.sudo().env['hr.employee'].search([('id','=',self.id)]).get_info_absences_portal()

    def get_info_planning_get_url(self,planning):
        try:
            res = self.sudo().env['hr.employee'].search([('id','=',self.id)])._planning_get_url(planning)
            return res
        except:
            return ''

class HrEmployeeUpdateTmp(models.TransientModel):
    _name = 'hr.employee.update.tmp'
    _description = 'Tabla tmp empleados - Portal autogestion'

    employee_id = fields.Many2one('hr.employee',readonly=True)

    def update_personal_data(self,values_employee,values_partner):
        self.sudo().env['hr.employee'].search([('id', '=', self.employee_id.id)], limit=1).write(values_employee)
        self.sudo().env['res.partner'].search([('id', '=', self.employee_id.address_home_id.id)], limit=1).write(values_partner)