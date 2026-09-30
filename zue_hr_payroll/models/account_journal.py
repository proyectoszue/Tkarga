from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import re

class Account_journal(models.Model):
    _inherit = 'account.journal'

    is_payroll_spreader = fields.Boolean('Es dispersor de nómina')
    plane_type = fields.Selection([('bancolombiasap', 'Bancolombia SAP'),
                                    ('bancolombiapab', 'Bancolombia PAB'),
                                    ('davivienda1', 'Davivienda 1'),
                                    ('occired', 'Occired'),
                                    ('avvillas1', 'AV VILLAS 1'),
                                    ('bancobogota', 'Banco Bogotá'),
                                    ('popular', 'Banco Popular'),
                                    ('bbva', 'Banco BBVA'),
                                    ], string='Tipo de Plano')

    def getNextElectronicDocumentNumber(self):
        # Consecutivo DIAN para NE / NE ajuste. El valor guardado en NE sigue siendo Prefijo+Consecutivo.
        self.ensure_one()
        if not self.code:
            raise ValidationError(_('El diario "%(journal)s" no tiene código/prefijo. Configure el código del diario.', journal=self.display_name))
        sequence_dian = self.z_secure_sequence_id
        if not sequence_dian:
            raise ValidationError(_('El diario "%(journal)s" no tiene Secuencia de seguridad (ZUE). Configure la secuencia en el diario.', journal=self.display_name))
        consecutive = sequence_dian._next()
        numbers = re.findall(r'\d+', str(consecutive))
        if not numbers:
            raise ValidationError(_('La secuencia "%(sequence)s" no generó un consecutivo numérico.', sequence=sequence_dian.display_name))
        item = int(numbers[-1])
        return self.code, item, '%s%s' % (self.code, item)
