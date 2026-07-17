from odoo import fields, models, api


class hr_payslip_reports_template(models.Model):
    _name = 'hr.payslip.reports.template'
    _description = 'Configuración plantillas reportes de liquidación'

    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)
    type_report = fields.Selection([('nomina', 'Nómina'),
                                     ('vacaciones', 'Vacaciones'),
                                     ('prima', 'Prima'),
                                     ('cesantias', 'Cesantías'),
                                     ('intereses_cesantias', 'Intereses de cesantías'),
                                     ('contrato', 'Liq. de Contrato')], 'Tipo de Comprobante',required=True, default='nomina')
    hide_vacation_dates = fields.Boolean('Ocultar fechas de vacaciones')
    #Encabezado y pie de pagina
    type_header_footer = fields.Selection([('default', 'Por defecto'),
                                           ('custom', 'Personalizado')], 'Tipo de encabezado y pie de pagina',
                                          required=True, default='default')
    header_custom = fields.Html('Encabezado')
    footer_custom = fields.Html('Pie de pagina')
    #Contenido
    show_observation = fields.Boolean('Mostrar observaciones')
    caption = fields.Text(string='Leyenda')
    notes = fields.Text(string='Notas')
    signature_prepared = fields.Boolean('Elaboró')
    z_signature_done = fields.Boolean('Estado Hecho', help="Generar reporte con empleado, sucursal y cargo de quien dejó la liquidación en estado hecho")
    #txt_signature_prepared = fields.Many2one('hr.employee', string='Empleado Elaboró')
    #z_branch_prepared = fields.Many2one(related='txt_signature_prepared.branch_id', string='Sucursal Elaboró', store=True)
    z_txt_signature_prepared_contact = fields.Char(string='Contacto Elaboró')
    z_txt_post_prepared = fields.Char(string='Cargo Elaboró')
    signature_reviewed = fields.Boolean('Revisó')
    txt_signature_reviewed = fields.Char(string='Contacto Revisó')
    signature_approved = fields.Boolean('Aprobó')
    txt_signature_approved = fields.Char(string='Contacto Aprobó')
    signature_employee = fields.Boolean('Empleado')
    txt_signature_employee = fields.Char(string='Contacto Empleado', help='Utilizar $_name_employee para que tome el nombre del empleado')

    _company_payslip_reports_template = models.Constraint('UNIQUE (company_id,type_report)', 'Ya existe una configuración de plantilla de este tipo para esta compañía, por favor verificar')

    @api.depends('type_report','company_id')
    def _compute_display_name(self):
        for record in self:
            record.display_name = "Plantilla Reporte {} de {}".format(record.type_report.upper(),record.company_id.name)


class ResUsers(models.Model):
    _inherit = 'res.users'

    branch_id = fields.Many2one('zue.res.branch', string="Sucursal")
