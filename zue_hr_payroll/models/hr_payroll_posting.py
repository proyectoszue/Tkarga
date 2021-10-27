# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import base64
import datetime
#---------------------------Modelo para contabilizar el pago de nómina-------------------------------#

class hr_payroll_posting_distribution(models.Model):
    _name = 'hr.payroll.posting.distribution'
    _description = 'Pago contabilización de nomina - distribución'

    payroll_posting = fields.Many2one('hr.payroll.posting',string='Contabilización', required=True)
    partner_id = fields.Many2one('res.company',string='Ubicación laboral', required=True)
    account_id = fields.Many2one('account.account',string='Cuenta', required=True)

class hr_payroll_posting(models.Model):
    _name = 'hr.payroll.posting'
    _description = 'Pago contabilización de nomina'
    _rec_name = 'description'

    payment_type = fields.Selection([('225', 'Pago de Nómina')], string='Tipo de pago', required=True, default='225', readonly=True)
    journal_id = fields.Many2one('account.journal', string='Diario', domain=[('is_payroll_spreader', '=', True)], required=True)        
    company_id = fields.Many2one('res.company',string='Compañia', required=True, default=lambda self: self.env.company)
    vat_payer = fields.Char(string='NIT Pagador', readonly=True, related='company_id.partner_id.vat')
    payslip_id = fields.Many2one('hr.payslip.run',string='Lote de nómina', domain=[('definitive_plan', '=', False),('state', '=', 'close')])
    description = fields.Char(string='Descripción', required=True) 
    state = fields.Selection([('draft', 'Borrador'),('done', 'Hecho')], string='Estado', default='draft')
    move_id = fields.Many2one('account.move',string='Movimiento Contable', readonly=True)
    source_information = fields.Selection([('lote', 'Por lote'),
                                          ('liquidacion', 'Por liquidaciones')],'Origen información', default='lote') 
    liquidations_ids= fields.Many2many('hr.payslip', string='Liquidaciones', domain=[('definitive_plan', '=', False),('payslip_run_id', '=', False)])    
    payroll_posting_distribution_ids = fields.One2many('hr.payroll.posting.distribution', 'payroll_posting',string='Distribución')

    #_sql_constraints = [('change_payslip_id_uniq', 'unique(payslip_id,liquidations_ids)', 'Ya existe un pago de contabilización para este lote/liquidación, por favor verificar')]
    #Realizar validacion

    def payroll_posting(self):
        #Inicializar variables
        debit_account_id = False
        credit_account_id = False
        line_ids = []
        debit_sum = 0.0
        move_dict = {
                    'company_id': self.company_id.id,
                    'ref': self.description,
                    'journal_id': self.journal_id.id,
                    'date': fields.Date.today(),
                }
        if self.source_information == 'lote':
            obj_payrolls = self.env['hr.payslip'].search([('payslip_run_id', '=', self.payslip_id.id)])            
        elif self.source_information == 'liquidacion':
            obj_payrolls = self.env['hr.payslip'].search([('id', 'in', self.liquidations_ids.ids)])
        else:
            raise ValidationError(_('No se ha configurado origen de información.'))
        #------------------PASO 1 | Obtener cuentas contables del proceso----------------------------------
        #Debito - se obtiene de la regla Neto  
        struct_id = 0
        for p in obj_payrolls:
            if p.struct_id.process == 'contrato':
                struct_id = self.env['hr.payroll.structure'].search([('process','=','nomina')], limit = 1).id
            else:        
                struct_id = p.struct_id.id 

        obj_rule_neto = self.env['hr.salary.rule'].search([('code', '=', 'NET'),('struct_id','=',struct_id)]) 
        for contab in obj_rule_neto.salary_rule_accounting:
            if contab.company.id == self.company_id.id:
                debit_account_id = contab.debit_account.id if contab.debit_account else contab.credit_account.id            
        #Credito - se obtiene del diario seleccionado
        credit_account_id = self.journal_id.default_credit_account_id.id if self.journal_id.default_credit_account_id else self.journal_id.default_debit_account_id.id
        #Validar cuentas
        if not debit_account_id:
            raise ValidationError(_('No se ha configurado la cuenta contable para la regla salarial Neto.'))
        if not credit_account_id:
            raise ValidationError(_('No se ha configurado la cuenta contable para el diario seleccionado.'))
        #------------------PASO 2 | Obtener las lineas del debito (Valor Neto x Empleado)----------------------------------
        dict_distribution = {}
        for payslip in obj_payrolls:
            value = payslip.line_ids.filtered(lambda line: line.code == 'NET').total
            value = value if value > 0 else 0
            if not payslip.employee_id.address_home_id.id:
                raise ValidationError(_('El empleado '+payslip.employee_id.name+' no tiene un tercero asociado, por favor verificar.'))
            line_debit = {
                'name': self.description + ' | ' + payslip.employee_id.name,
                'partner_id': payslip.employee_id.address_home_id.id,
                'account_id': debit_account_id,
                'journal_id': self.journal_id.id,
                'date': fields.Date.today(),
                'debit': value,
                'credit': 0,
                #'analytic_account_id': analytic_account_id,
            }
            
            dict_distribution[payslip.employee_id.address_id.id] = dict_distribution.get(payslip.employee_id.address_id.id, 0)+value

            debit_sum = debit_sum + value
            line_ids.append(line_debit)
        #------------------PASO 3 | Obtener las linea del credito----------------------------------
        if len(self.payroll_posting_distribution_ids) > 0:
            for distribution in self.payroll_posting_distribution_ids:
                line_credit = {
                        'name': self.description,
                        'partner_id': distribution.partner_id.partner_id.id,
                        'account_id': distribution.account_id.id,
                        'journal_id': self.journal_id.id,
                        'date': fields.Date.today(),
                        'debit': 0,
                        'credit': dict_distribution.get(distribution.partner_id.partner_id.id, 0),
                        #'analytic_account_id': analytic_account_id,
                    }            
                line_ids.append(line_credit)
        else:            
            line_credit = {
                    'name': self.description,
                    'partner_id': self.company_id.partner_id.id,
                    'account_id': credit_account_id,
                    'journal_id': self.journal_id.id,
                    'date': fields.Date.today(),
                    'debit': 0,
                    'credit': debit_sum,
                    #'analytic_account_id': analytic_account_id,
                }            
            line_ids.append(line_credit)

        move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
        move = self.env['account.move'].create(move_dict)        
        self.write({'move_id': move.id,'state':'done'})

        if self.source_information == 'lote':
            self.payslip_id.write({'definitive_plan':True})
        elif self.source_information == 'liquidacion':
            for liq in self.liquidations_ids:
                liq.write({'definitive_plan':True})            
    
    def payroll_rever_posting(self):
        self.env['account.move'].search([('id', '=', self.move_id.id)]).unlink()
        self.write({'state':'draft'})
        if self.source_information == 'lote':
            self.payslip_id.write({'definitive_plan':False})
        elif self.source_information == 'liquidacion':
            for liq in self.liquidations_ids:
                liq.write({'definitive_plan':False})            

    @api.constrains('payslip_id','liquidations_ids')
    def _check_uniq_payslip_id(self):  
        for record in self:
            obj_lote = False
            obj_liq = False
            if record.source_information == 'lote':
                obj_lote = self.env['hr.payroll.posting'].search([('payslip_id','=',record.payslip_id.id),('id','!=',record.id)]) 
            if record.source_information == 'liquidacion':
                obj_liq = self.env['hr.payroll.posting'].search([('liquidations_ids','in',record.liquidations_ids.ids),('id','!=',record.id)]) 

            if obj_lote or obj_liq:
                raise ValidationError(_('Ya existe un pago de contabilización para este lote/liquidación, por favor verificar'))  

    def unlink(self):
        if any(self.filtered(lambda posting: posting.state not in ('draft'))):
            raise ValidationError(_('No se puede eliminar una contabilización del pago en estado hecho!'))
        return super(hr_payroll_posting, self).unlink()