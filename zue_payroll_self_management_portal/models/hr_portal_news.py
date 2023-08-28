from odoo import fields, models, api

class hr_portal_news(models.Model):
    _name = 'hr.portal.news'
    _description = 'Comunicados del portal'

    company_id = fields.Many2one('res.company', 'Compañia')
    date_end = fields.Date('Fecha límite')
    name = fields.Char('Nombre')
    sequence = fields.Integer('Secuencia')
    news_html = fields.Html('Comunicado')