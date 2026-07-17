from odoo import api, fields, models, _

class zue_parameterization_portal_menus(models.Model):
    _name = 'zue.parameterization.portal.menus'
    _description = 'Parametrización portal menus'
    _rec_name = 'z_company_id'

    z_company_id = fields.Many2one('res.company', 'Compañia')
    z_sequence = fields.Integer('Secuencia')
    z_reports = fields.Boolean('Informes', default=True)
    z_hide_laboral_certificate = fields.Boolean('Certificado Laboral', default=False)
    z_hide_payroll_vouchers = fields.Boolean('Comprobante de nómina', default=False)
    z_hide_vacation_book = fields.Boolean('Libro de vacaciones', default=False)
    z_hide_cesantias_book = fields.Boolean('Libro de cesantías', default=False)
    z_personal_information = fields.Boolean('Información Laboral',default=True)
    z_absences = fields.Boolean('Ausencias',default=True)
    z_experience = fields.Boolean('Experiencia',default=True)
    z_skills = fields.Boolean('Habilidades',default=True)
    z_social_security_and_dependents = fields.Boolean('Seguridad social y Dependientes',default=True)
    z_documents = fields.Boolean('Documentos',default=True)