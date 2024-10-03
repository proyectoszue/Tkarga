from odoo import fields, models, api

class zue_parameterization_portal_menus(models.Model):
    _name = 'zue.parameterization.portal.menus'
    _description = 'Parametrización portal menus'
    _rec_name = 'z_company_id'

    z_company_id = fields.Many2one('res.company', 'Compañia')
    z_sequence = fields.Integer('Secuencia')
    z_reports = fields.Boolean('Informes')
    z_personal_information = fields.Boolean('Información Laboral')
    z_absences = fields.Boolean('Ausencias')
    z_experience = fields.Boolean('Experiencia')
    z_skills = fields.Boolean('Habilidades')
    z_social_security_and_dependents = fields.Boolean('Seguridad social y Dependientes')
    z_documents = fields.Boolean('Documentos')