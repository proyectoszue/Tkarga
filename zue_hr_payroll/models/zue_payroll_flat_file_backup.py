# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import base64
import datetime
#---------------------------Modelo para generar Archivo plano de pago de nómina-------------------------------#

class zue_payroll_flat_file_backup(models.Model):
    _name = 'zue.payroll.flat.file.backup'
    _description = 'Archivo plano de pago de nómina BACKUP'

    generation_date = fields.Date(string="Fecha en la cual se genero", required=True, readonly=True)
    journal_id = fields.Many2one('account.journal', string='Diario', required=True, readonly=True)    
    payment_type = fields.Selection([('225', 'Pago de Nómina')], string='Tipo de pago', required=True, readonly=True)
    company_id = fields.Many2one('res.company',string='Compañia', required=True, readonly=True)
    payslip_id = fields.Many2one('hr.payslip.run',string='Lote de nómina', readonly=True)
    liquidations_ids = fields.Many2many('hr.payslip', string='Liquidaciones', readonly=True)
    transmission_date = fields.Datetime(string="Fecha transmisión de lote", required=True, readonly=True)
    application_date = fields.Date(string="Fecha aplicación transacciones", required=True, readonly=True)
    description = fields.Char(string='Descripción', required=True, readonly=True)
    txt_file = fields.Binary('TXT file', readonly=True)
    txt_file_name = fields.Char('TXT name', readonly=True)