# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
import datetime
_logger = logging.getLogger(__name__)

# Dias festivos
class ZueHolidays(models.Model):
    _name = 'zue.holidays'
    _description = 'Días festivos'

    name = fields.Char('Descripción', required=True)
    date = fields.Date('Fecha', required=True)

    _date_uniq = models.Constraint('unique(date)', 'Ya existe un día festivo en esta fecha, por favor verificar.')

#Codigo postal
class ZueZipCode(models.Model):
    _name = 'zue.zip.code'
    _rec_name = 'code'
    _description = 'Código postal'

    code = fields.Char('Código', required=True)

    _zip_postal_uniq = models.Constraint('unique(code)', 'Ya existe ese código postal, por favor verificar.')

# CIIU
class Ciiu(models.Model):
    _name = 'zue.ciiu'
    _parent_store = True
    _parent_name  = 'parent_id'
    _description = 'CIIU - Actividades economicas'

    code = fields.Char('Codigo', required=True)
    name = fields.Char('Name', required=True)
    porcent_ica = fields.Float(string='Porcentaje ICA')
    parent_id = fields.Many2one('zue.ciiu','Parent Tag', ondelete='cascade')
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many('zue.ciiu', 'parent_id', 'Child Tags')

    @api.depends('name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = "{}".format(record.name)

# TIPOS DE TERCERO
class x_type_thirdparty(models.Model):
    _name = 'zue.type_thirdparty'
    _description = 'Tipos de tercero'

    code = fields.Char(string='Código', required=True)
    name = fields.Char(string='Nombre', required=True)
    is_company = fields.Boolean('¿Es un tipo de tercero compañia?')
    is_individual = fields.Boolean('¿Es un tipo de tercero individual?')
    types = fields.Selection([('1', 'Cliente / Cuenta'),
                              ('2', 'Contacto'),
                              ('3', 'Proveedor'),
                              ('4', 'Funcionario / Contratista'),
                              ('5', 'Candidato')], string='Tipo', required=True)
    fields_mandatory = fields.Many2many('ir.model.fields', domain="[('model', '=', 'res.partner'),('ttype', 'not in', ['many2many','one2many'])]", string='Campos obligatorios')

    _type_thirdparty_uniq = models.Constraint('unique(types)', 'Ya existe un tipo de tercero de este tipo, por favor verificar.')

    @api.depends('name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = "{}".format(record.name)
