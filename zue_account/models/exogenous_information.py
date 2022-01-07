from odoo import models, fields, api, _

#Código fiscal
class fiscal_accounting_code_details(models.Model):
    _name = 'fiscal.accounting.code.details'
    _description = 'Código Fiscal - Cuentas'

    fiscal_accounting_id = fields.Many2one('fiscal.accounting.code',string='Código fiscal', required=True)
    account_id = fields.Many2one('account.account',string='Cuenta', required=True)
    move_type = fields.Selection([('debit', 'Débito'),
                                     ('credit', 'Crédito'),
                                     ('net', 'Neto')], string='Tipo de movimiento', required=True)

    _sql_constraints = [('fiscal_account_id_uniq', 'unique(fiscal_accounting_id,account_id)',
                         'Ya existe la cuenta en este código fiscal, por favor verficar.')]

class fiscal_accounting_code(models.Model):
    _name = 'fiscal.accounting.code'
    _description = 'Código Fiscal'
    _rec_name = 'code_description'

    company_id = fields.Many2one('res.company', string='Compañía', readonly=True, required=True,
                                 default=lambda self: self.env.company)
    concept_dian = fields.Char(string="Código Fiscal", required=True)
    code_description = fields.Char(string="Descripción del Código", required=True)
    format_id = fields.Many2one('format.encab', string='Formato')
    #concept = fields.Char(string="Concepto")
    account_type = fields.Selection([('movement', 'Movimiento'),
                              ('balance', 'Balance'),
                              ], 'Tipo de cuenta')
    #account_code = fields.Char(string="Código de cuenta")
    accounting_details_ids = fields.One2many('fiscal.accounting.code.details','fiscal_accounting_id',string='Cuentas')
    #excluded_documents_ids = fields.Many2many('account.journal', string="Documentos Excluidos")
    #fiscal_group_id = fields.Many2one('fiscal.accounting.group',string="Grupo Fiscal")

    _sql_constraints = [('fiscal_code_uniq', 'unique(company_id,concept_dian)',
                         'El concepto DIAN digitado ya esta registrado para esta compañía, por favor verificar.')]

#Grupo Fiscal
class fiscal_accounting_group(models.Model):
    _name = 'fiscal.accounting.group'
    _description = 'Grupo Fiscal'
    _rec_name = 'group_description'

    company_id = fields.Many2one('res.company', string='Compañía', readonly=True, required=True,
                                 default=lambda self: self.env.company)
    fiscal_group = fields.Char(string="Grupo Fiscal", required=True)
    group_description = fields.Char(string="Descripción del Grupo", required=True)
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
    concept_dian_ids = fields.Many2many('fiscal.accounting.code', string="Códigos Fiscales")
    excluded_thirdparty_ids = fields.Many2many('res.partner', string="Tercero Excluido")

    _sql_constraints = [('fiscal_group_uniq', 'unique(company_id,fiscal_group)',
                         'El grupo fiscal digitado ya esta registrado para esta compañía, por favor verificar.')]


class format_encab(models.Model):
    _name = 'format.encab'
    _description = 'Formato de Código Fiscal Encabezado'

    format_id = fields.Char(string="Código Formato", required=True)
    description = fields.Char(string="Descripción del formato", required=True)
    details_ids = fields.One2many('format.detail','format_id',string = 'Campos Disponibles', ondelete='cascade')
    company_id = fields.Many2one('res.company', string='Compañía', readonly=True, required=True,default=lambda self: self.env.company)
    format_associated_id = fields.Many2one('format.encab', string='Formato Asociado')
    fields_associated_code_fiscal_ids = fields.Many2many('fiscal.accounting.code', string='Conceptos Asociados')

    _sql_constraints = [('format_encab_uniq', 'unique(format_id,company_id)',
                         'El formato fiscal digitado ya esta registrado para esta compañía, por favor verificar.')]

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "{}/{}".format(record.format_id,record.description)))
        return result

    @api.onchange('format_associated_id')
    def get_code_fiscal(self):
        for record in self:
            record.fields_associated_code_fiscal_ids = self.env['fiscal.accounting.code'].search(
                [('format_id', '=', self.format_associated_id.id), ('format_id', '!=', False)]).ids

class format_detail(models.Model):
    _name = 'format.detail'
    _description = 'Formato de Código Fiscal Detalle'

    format_id = fields.Many2one('format.encab',string='Código Formato', required=True, ondelete='cascade')
    sequence = fields.Integer(string="Secuencia", required=True)
    available_fields = fields.Selection([('fiscal_accounting_id', 'Concepto Fiscal'),
                              ('concept_dian',  'Concepto DIAN'),
                              ('format',  'Formato Archivo'),
                              ('x_document_type', 'Tipo Documento Tercero'),
                              ('vat', 'Número Documento Tercero'),
                              ('x_first_name', 'Primer Nombre'),
                              ('x_second_name', 'Segundo Nombre'),
                              ('x_first_lastname', 'Primer Apellido'),
                              ('x_second_lastname', 'Segundo Apellido'),
                              ('commercial_company_name', 'Razón Social'),
                              ('x_digit_verification', 'Dígito de Verificación'),
                              ('street', 'Dirección'),
                              ('state_id', 'Código Departamento'),
                              ('x_city', 'Código Ciudad'),
                              ('amount', 'Valor Pesos'),
                              ('operador', 'Operador'),
                              ('tax', 'Base Impuestos'),
                              ('x_code_dian', 'Código País DIAN'),
                              ('phone', 'Teléfono Tercero'),
                              ('unit_rate', 'Tarifa Aplicada'),
                              ('email', 'Email'),
                              ('higher_value_iva', 'Mayor Valor Iva'),
                              ], 'Campos Seleccionados', required=True)