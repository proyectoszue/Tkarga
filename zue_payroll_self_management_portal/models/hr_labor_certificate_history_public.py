from odoo import fields, models, api, tools


class hr_labor_certificate_history_public(models.Model):
    _name = 'hr.labor.certificate.history.public'
    _description = 'Vista de la tabla de historico de certificados laborales generados '
    _auto = False
    _log_access = True

    contract_id = fields.Many2one('hr.contract.public', 'Contrato')
    sequence = fields.Char(string="Secuencia")
    date_generation = fields.Date('Fecha generación')
    info_to = fields.Char(string='Dirigido a')
    z_functions_with = fields.Boolean(string="Con funciones")
    # pdf = fields.Binary(string='Certificado')
    pdf_name = fields.Char(string='Filename Certificado')


    @api.model
    def _get_fields(self):
        return ','.join('labor_certificate_his.%s' % name for name, field in self._fields.items() if
                        field.store and field.type not in ['many2many', 'one2many'])

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (
                SELECT
                    %s
                FROM hr_labor_certificate_history labor_certificate_his
            )""" % (self._table, self._get_fields()))
    
    def get_hr_labor_certificate_template(self):
        return self.sudo().env['hr.labor.certificate.history'].search([('id', '=', self.id)]).get_hr_labor_certificate_template()