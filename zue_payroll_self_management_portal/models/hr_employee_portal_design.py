from odoo import fields, models, api

class zue_hr_employee_portal_design(models.Model):
    _name = 'zue.hr.employee.portal.design'
    _description = 'Diseño del portal'
    _rec_name = 'z_company_design_id'

    z_company_design_id = fields.Many2one('res.company', string='Compañía', required="True")
    z_theme = fields.Selection([('light', 'Claro'),('dark', 'Oscuro')],
                                    string='Tema') #OSCURO/CLARO
    z_background_color = fields.Char(string='Color fondo contenido')
    z_logo = fields.Image(string='Logo')
    z_primary_color = fields.Char(string='Color fuente')
    z_secondary_color = fields.Char(string='Color fondo menú')
    z_font = fields.Selection([('Arial, sans-serif', 'Arial'),
                               ('Helvetica, sans-serif', 'Helvetica'),
                               ('Verdana, sans-serif', 'Verdana'),
                               ('Trebuchet MS, sans-serif', 'Trebuchet MS'),
                               ('Gill Sans, sans-serif', 'Gill Sans'),
                               ('Noto Sans, sans-serif', 'Noto Sans'),
                               ('Avantgarde, TeX Gyre Adventor, URW Gothic L, sans-serif', 'Avantgarde'),
                               ('Optima, sans-serif', 'Optima'),
                               ('Arial Narrow, sans-serif', 'Arial Narrow'),
                               ('Times, Times New Roman, serif', 'Times New Roman'),
                               ('Didot, serif', 'Didot'),
                               ('Georgia, serif', 'Georgia'),
                               ('Palatino, URW Palladio L, serif', 'Palatino'),
                               ('Bookman, URW Bookman L, serif', 'Bookman'),
                               ('New Century Schoolbook, TeX Gyre Schola, serif', 'New Century Schoolbook'),
                               ('American Typewriter, serif', 'American Typewriter'),
                               ('Andale Mono, monospace', 'Andale Mono'),
                               ('Courier New, monospace', 'Courier New'),
                               ('Courier, monospace', 'Courier'),
                               ('FreeMono, monospace', 'FreeMono'),
                               ('OCR A Std, monospace', 'OCR A Std'),
                               ('DejaVu Sans Mono, monospace', 'DejaVu Sans Mono'),
                               ('Comic Sans MS, Comic Sans, cursive', 'Comic Sans MS'),
                               ('Apple Chancery, cursive', 'Apple Chancery'),
                               ('Bradley Hand, cursive', 'Bradley Hand'),
                               ('Brush Script MT, Brush Script Std, cursive', 'Brush Script MT'),
                               ('Snell Roundhand, cursive', 'Snell Roundhand'),
                               ('URW Chancery L, cursive', 'URW Chancery L'),
                               ('Impact, fantasy', 'Impact'),
                               ('Luminari, fantasy', 'Luminari'),
                               ('Chalkduster, fantasy', 'Chalkduster'),
                               ('Jazz LET, fantasy', 'Jazz LET'),
                               ('Blippo, fantasy', 'Blippo'),
                               ('Stencil Std, fantasy', 'Stencil Std'),
                               ('Marker Felt, fantasy', 'Marker Felt'),
                               ('Trattatello, fantasy', 'Trattatello')],
                                string='Fuente')

    _sql_constraints = [
        ('company_unique', 'UNIQUE(z_company_design_id)', 'Ya existe una configuración para el portal de esta compañía')
    ]