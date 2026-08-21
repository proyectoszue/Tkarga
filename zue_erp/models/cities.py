# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

# TMP MIENTRAS MIGRACION a v19 DESPUES SE DEBE ELIMINAR
class Cities(models.Model):
    _name = 'zue.city'
    _description = 'Ciudades por departamento'

    state_id = fields.Many2one('res.country.state', string='Departamento', required=True)
    code = fields.Char(string='Código', required=True)
    name = fields.Char(string='Nombre', required=True)

# --------------------------------Modelos heredados de Odoo------------------------------------#

class ResCountry(models.Model):
    _inherit = 'res.country'

    z_code_dian = fields.Char(string='Código del país para la DIAN')
    x_code_dian = fields.Char(string='Código DIAN país')
    z_skip_validation = fields.Boolean(string='Omitir validación VAT')

class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    z_code_dian = fields.Char(string='Código de provincia/departamento para la DIAN')

class ResCity(models.Model):
    _inherit = 'res.city'

    z_code_dian = fields.Char(string='Código para la DIAN')

    @api.model_create_multi
    def create(self, vals_list):
        max_id = None
        seq_last_value = None
        # Capture information about current max(id) and sequence status
        self.env.cr.execute("SELECT COALESCE(MAX(id), 0) FROM res_city")
        max_id = self.env.cr.fetchone()[0]
        try:
            self.env.cr.execute("SELECT last_value, is_called FROM res_city_id_seq")
            seq_row = self.env.cr.fetchone()
            if seq_row:
                seq_last_value = seq_row[0]
        except Exception:
            # Sequence name may differ; ignore if query fails
            pass
        # If sequence is behind the current max(id), realign it to avoid duplicate key errors
        if max_id is not None and seq_last_value is not None and seq_last_value <= max_id:
            try:
                self.env.cr.execute(
                    "SELECT setval('res_city_id_seq', %s, true)", (max_id + 1,)
                )
            except Exception:
                # If alignment fails, let the original error surface
                pass
        return super(ResCity, self).create(vals_list)
