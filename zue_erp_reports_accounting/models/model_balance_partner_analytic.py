# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class balance_partner_analytic_filter(models.TransientModel):
    _name = "balance.partner.analytic.filter"
    _description = "Filter - Balance Partner"
    
    #date_filter = fields.Date(string='Fecha', required=True)
    x_type_filter = fields.Selection([
                                        ('1', 'Periodo'),
                                        ('2', 'Rango de periodos'),
                                        ('3', 'Anual')        
                                    ], string='Tipo', required=True, default='1')    
    #x_clase_filter = fields.Char(string='Clase', default='')
    x_ano_filter = fields.Integer(string='Año', required=True)
    x_month_filter = fields.Selection([
                                        ('1', 'Enero'),
                                        ('2', 'Febrero'),
                                        ('3', 'Marzo'),
                                        ('4', 'Abril'),
                                        ('5', 'Mayo'),
                                        ('6', 'Junio'),
                                        ('7', 'Julio'),
                                        ('8', 'Agosto'),
                                        ('9', 'Septiembre'),
                                        ('10', 'Octubre'),
                                        ('11', 'Noviembre'),
                                        ('12', 'Diciembre')        
                                    ], string='Mes', required=True)
    x_ano_filter_two = fields.Integer(string='Año 2')
    x_month_filter_two = fields.Selection([
                                        ('1', 'Enero'),
                                        ('2', 'Febrero'),
                                        ('3', 'Marzo'),
                                        ('4', 'Abril'),
                                        ('5', 'Mayo'),
                                        ('6', 'Junio'),
                                        ('7', 'Julio'),
                                        ('8', 'Agosto'),
                                        ('9', 'Septiembre'),
                                        ('10', 'Octubre'),
                                        ('11', 'Noviembre'),
                                        ('12', 'Diciembre')        
                                    ], string='Mes 2')
    company_id = fields.Many2one('res.company', string='Compañia')

    @api.depends('x_type_filter', 'x_ano_filter', 'x_month_filter', 'x_ano_filter_two', 'x_month_filter_two')
    def _compute_display_name(self):
        for record in self:
            if record.x_type_filter == '1':
                ttype = 'Periodo'
            elif record.x_type_filter == '2':
                ttype = 'Rango de periodos'
            else:
                ttype = 'Anual'
            
            if record.x_type_filter == '2':
                record.display_name = "{} - Inicial: {}-{} | Final: {}-{} ".format(ttype,record.x_ano_filter,record.x_month_filter,record.x_ano_filter_two,record.x_month_filter_two)
            else:
                record.display_name = "{} - Año: {} | Mes: {}".format(ttype,record.x_ano_filter,record.x_month_filter)

    
    def open_pivot_view(self):
        
        if not self.company_id:
            company_id = 0
        else:
            company_id = self.company_id.id

        #if not self.x_clase_filter:
        #    x_clase_filter = ''
       # else:
        #    x_clase_filter = self.x_clase_filter
        
        ctx = self.env.context.copy()
        ctx.update({'x_type':self.x_type_filter,'x_ano':self.x_ano_filter,'x_month':self.x_month_filter,'x_ano_two':self.x_ano_filter_two,'x_month_two':self.x_month_filter_two,'company_id':company_id})
        self.env['balance.analytic.partner.report'].with_context(ctx).init()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Pivot Balance',
            'res_model': 'balance.analytic.partner.report',
            'domain': [],
            'view_mode': 'pivot',
            'context': ctx
        }
    
class balance_analytic_partner_report(models.Model):
    _name = "balance.analytic.partner.report"
    _description = "Report - Balance Partner"
    _order = 'account_level_one,account_level_two,account_level_three,account_level_four,account_level_five'

    # Compañia
    company_id = fields.Many2one('res.company', string='Compañia', readonly=True)
    # Cuenta y sus niveles
    account_level_one = fields.Char(string='Cuenta Nivel 1', readonly=True)
    account_level_two = fields.Char(string='Cuenta Nivel 2', readonly=True)
    account_level_three = fields.Char(string='Cuenta Nivel 3', readonly=True) 
    account_level_four = fields.Char(string='Cuenta Nivel 4', readonly=True)
    account_level_five = fields.Char(string='Cuenta Nivel 5', readonly=True)
    account_cuenta_financiera = fields.Char(string='Cuenta Financiera', readonly=True)
    clase_cuenta = fields.Char(string='Clase Cuenta', readonly=True)
    # Cliente
    partner = fields.Char(string='Cliente', readonly=True)
    # Valores
    initial_balance = fields.Float(string='Saldo Anterior', default=0.0)
    debit = fields.Float(string='Débito', default=0.0)
    credit = fields.Float(string='Crédito', default=0.0)
    new_balance = fields.Float(string='Nuevo Saldo', default=0.0)
    
    
