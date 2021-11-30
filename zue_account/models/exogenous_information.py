from odoo import models, fields, api, _

#Código fiscal

class fiscal_accounting_code(models.Model):
    _name = 'fiscal.accounting.code'
    _description = 'Código Fiscal'
    _rec_name = 'code_description'

    company_id = fields.Many2one('res.company', string='Compañía', readonly=True, required=True,
                                 default=lambda self: self.env.company)
    concept_dian = fields.Char(string="Concepto DIAN")
    code_description = fields.Char(string="Descripción del Código")
    fiscal_format = fields.Integer(string="Formato")
    concept = fields.Char(string="Concepto")
    account_type = fields.Selection([('movement', 'Movimiento'),
                              ('balance', 'Balance'), 
                              ], 'Tipo de cuenta')
    account_code = fields.Char(string="Código de cuenta")
    account_ids = fields.Many2many('account.account', string="Cuenta")
    excluded_documents_ids = fields.Many2many('account.journal', string="Documentos Excluidos")
    fiscal_group_id = fields.Many2one('fiscal.accounting.group',string="Grupo Fiscal")

    _sql_constraints = [('fiscal_code_uniq', 'unique(company_id,concept_dian)',
                         'El concepto DIAN digitado ya esta registrado para esta compañía, por favor verificar.')]

#Grupo Fiscal
class fiscal_accounting_group(models.Model):
    _name = 'fiscal.accounting.group'
    _description = 'Grupo Fiscal'
    _rec_name = 'group_description'

    company_id = fields.Many2one('res.company', string='Compañía', readonly=True, required=True,
                                 default=lambda self: self.env.company)
    fiscal_group = fields.Char(string="Grupo Fiscal")
    group_description = fields.Char(string="Descripción del Grupo")
    operator = fields.Selection([('>', 'Mayor que'),
                              ('<', 'Menor que'),
                              ('=', 'Igual que'),
                              ('!=', 'Distinto de'),
                              ('<=','Menor o igual que'),
                              ('>=', 'Mayor o igual que'),
                              ], 'Operador')
    amount = fields.Float(string="Monto")
    tax_type = fields.Selection([('dian', "DIAN Art 631"),
                              ('treasury', "Tesoreria Distrital"), 
                              ], "Tipo de impuesto")
    concept_dian_ids = fields.One2many('fiscal.accounting.code', 'fiscal_group_id', string="Conceptos DIAN")
    excluded_thirdparty_ids = fields.Many2many('account.journal', string="Tercero Excluido")

    _sql_constraints = [('fiscal_group_uniq', 'unique(company_id,fiscal_group)',
                         'El grupo fiscal digitado ya esta registrado para esta compañía, por favor verificar.')]