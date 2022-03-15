from odoo import fields, models, api


class hr_payslip_reports_template(models.Model):
    _name = 'hr.payslip.reports.template'
    _description = 'Configuración plantillas reportes de liquidación'

    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)
    type_report = fields.Selection([('nomina', 'Nónima'),
                                     ('vacaciones', 'Vacaciones'),
                                     ('prima', 'Prima'),
                                     ('cesantias', 'Cesantías'),
                                     ('intereses_cesantias', 'Intereses de cesantías'),
                                     ('contrato', 'Liq. de Contrato')], 'Reporte de liquidación',required=True, default='nomina')
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
    #partner_signature_prepared = fields.Many2one('res.partner',string='Contacto Elaboró')
    signature_reviewed = fields.Boolean('Revisó')
    #partner_signature_reviewed = fields.Many2one('res.partner',string='Contacto Revisó')
    signature_approved = fields.Boolean('Aprobó')
    #partner_signature_approved = fields.Many2one('res.partner',string='Contacto Aprobó')

    _sql_constraints = [
        ('company_payslip_reports_template', 'UNIQUE (company_id,type_report)', 'Ya existe una configuración de plantilla de este tipo para esta compañía, por favor verificar')
    ]

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "Plantilla Reporte {} de {}".format(record.type_report.upper(),record.company_id.name)))
        return result