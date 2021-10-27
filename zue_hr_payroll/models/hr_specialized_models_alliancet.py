from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class hr_assistance_vacation_alliancet(models.Model):
    _name = 'hr.assistance.vacation.alliancet'
    _description = 'Auxilio de vacaciones AlianzaT'

    antiquity = fields.Integer('Antigüedad (Años)', required=True)
    vacation_relief = fields.Float('Auxilio vacaciones pacto (Días)')
    convention_vacation = fields.Float('Auxilio vacaciones convención (Días)')