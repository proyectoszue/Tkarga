from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError

from datetime import datetime

#MOVIMIENTO CONTABLE ENCABEZADO

class account_move(models.Model):
    _inherit = 'account.move'

    supplier_invoice_number = fields.Char(string='Nº de factura del proveedor',help="La referencia de esta factura proporcionada por el proveedor.", copy=False)
    supplier_invoice_attachment = fields.Many2one('documents.document',string="Soporte") #fields.Binary(string="Soporte")
    iva_amount = fields.Float('Valor IVA', compute='_compute_amount_iva', store=True)
    l10n_co_edi_type = fields.Selection([('1', 'Factura de venta'),
                                        ('2', 'Factura de exportación'),
                                        ('3', 'Notas electrónicas'),
                                        ('4', 'Factura de contingencia'),
                                        ], string='Tipo de Documento')
    accounting_closing_id = fields.Many2one('annual.accounting.closing', string='Cierre contable anual', ondelete='cascade')

    #supplier_invoice_attachment_name = fields.Char(string="Soporte Filename")
    @api.depends('line_ids','invoice_line_ids')
    def _compute_amount_iva(self):
        iva_amount = 0

        if self.invoice_line_ids.tax_id:
            obj_taxes = self.env['account.tax'].search([('name', 'ilike', 'IVA')])

            percent = obj_taxes[0].amount

            for lines in self.invoice_line_ids:
                for taxes in lines.tax_ids:
                    if taxes.ids[0] in obj_taxes.ids:
                        iva_amount += lines.price_subtotal * percent / 100

        self.iva_amount = iva_amount

    @api.constrains('line_ids','invoice_line_ids')
    def _check_line_ids(self):
        for record in self:
            for lines in record.line_ids:
                if lines.required_partner and not lines.partner_id:
                    raise ValidationError(_(str(lines.ref)+' - La cuenta "' + lines.account_id.name + '" obliga un tercero y este no ha sido digitado. Por favor verifique!'))

                if 'stock_move_id' in self.env['account.move']._fields:
                    if lines.required_analytic_account and not lines.analytic_account_id and not record.stock_move_id.picking_id:
                        raise ValidationError(_(str(lines.ref)+' - La cuenta "' + lines.account_id.name + '" obliga cuenta analítica y esta no ha sido digitada. Por favor verifique!'))
                else:
                    if lines.required_analytic_account and not lines.analytic_account_id:
                        raise ValidationError(_(str(lines.ref)+' - La cuenta "' + lines.account_id.name + '" obliga cuenta analítica y esta no ha sido digitada. Por favor verifique!'))

            for lines in record.invoice_line_ids:
                if lines.required_partner and not lines.partner_id:
                    raise ValidationError(_(str(lines.ref)+' - La cuenta "' + lines.account_id.name + '" obliga un tercero y este no ha sido digitado. Por favor verifique!'))

                if 'stock_move_id' in self.env['account.move']._fields:
                    if lines.required_analytic_account and not lines.analytic_account_id and not record.stock_move_id.picking_id:
                        raise ValidationError(_(str(lines.ref)+' - La cuenta "' + lines.account_id.name + '" obliga cuenta analítica y esta no ha sido digitada. Por favor verifique!'))
                else:
                    if lines.required_analytic_account and not lines.analytic_account_id:
                        raise ValidationError(_(str(lines.ref)+' - La cuenta "' + lines.account_id.name + '" obliga cuenta analítica y esta no ha sido digitada. Por favor verifique!'))

    @api.constrains('supplier_invoice_number')
    def _check_supplier_invoice(self):
        for record in self:
            if record.type == 'in_invoice':
                obj_move = self.env['account.move'].search([('supplier_invoice_number','=',record.supplier_invoice_number),('id','!=',record.id)])
                if len(obj_move) > 0:
                    raise ValidationError('El número de factura digitado ya existe, por favor verificar.')

class zue_confirm_wizard(models.TransientModel):
    _inherit = 'zue.confirm.wizard'

    accounting_closing_id = fields.Many2one('annual.accounting.closing', string='Cierre contable anual', ondelete='cascade')

    def yes(self):
        if self.accounting_closing_id:
            obj_move = self.env['account.move'].search([('accounting_closing_id', '=', self.accounting_closing_id.id)])
            obj_move.unlink()
            self.accounting_closing_id.generate_accounting_closing()
        obj_confirm = super(zue_confirm_wizard, self).yes()
        return obj_confirm

class annual_accounting_closing(models.Model):
    _name = 'annual.accounting.closing'
    _description = 'Cierre contable anual'

    balance = fields.Float('Saldo', readonly=True)
    closing_year = fields.Integer('Año de cierre', size=4)
    counter_contab = fields.Integer(compute='compute_counter_contab', string='Movimientos')
    company_id = fields.Many2one('res.company', string='Compañía', readonly=True, required=True, default=lambda self: self.env.company)
    journal_id = fields.Many2one('account.journal', string='Diario destino', company_dependent=True)
    counterparty_account = fields.Many2one('account.account',string='Cuenta contrapartida', required=True)

    def compute_counter_contab(self):
        count = self.env['account.move'].search_count([('accounting_closing_id', '=', self.id)])
        self.counter_contab = count

    def call_up_closing_wizard(self):
        yes_no = ''
        no_delete = False

        if self.counter_contab > 0:
            obj_contab = self.env['account.move'].search([('accounting_closing_id', '=', self.id)])
            for rows in obj_contab:
                if rows.state != 'draft':
                    no_delete = True
                    break
            if no_delete:
                return {'messages': [{'record': False, 'type': 'warning',
                                      'message': 'Ya hay documentos publicados. No es posible continuar!', }]}
            else:
                yes_no = "El movimiento contable actual para el cierre será borrado para crear uno nuevo. Desea continuar?"

            return {
                'name': 'Deseas continuar?',
                'type': 'ir.actions.act_window',
                'res_model': 'zue.confirm.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_accounting_closing_id': self.id,
                            'default_yes_no': yes_no}
            }
        else:
            self.generate_accounting_closing()

    def return_action_to_open(self):
        res = {
            'name': 'Movimientos',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'target': 'current',
            'domain': "[('accounting_closing_id','in',[" + str(self._ids[0]) + "])]"
        }
        return res

    def generate_accounting_closing(self):
        year = str(self.closing_year)
        start_date = '01/01/' + year
        end_date = '31/12/' + year
        accounts = '(4%|5%|6%|7%)'

        d_start_date = datetime.strptime(start_date, '%d/%m/%Y')
        d_end_date = datetime.strptime(end_date, '%d/%m/%Y')

        query = '''
                select aml.account_id, aml.partner_id, aml.analytic_account_id, sum(aml.debit-aml.credit) as saldo
                from account_move am 
                inner join account_move_line aml on am.id = aml.move_id 
                inner join account_account aa on aml.account_id = aa.id and code similar to '%s' 
                where am."date" between '%s' and '%s' and am.company_id = %s and am.state = 'posted'
                group by aml.account_id, aml.partner_id, aml.analytic_account_id 
                ''' % (accounts, start_date, end_date, self.company_id.id)

        self.env.cr.execute(query)
        result_query = self.env.cr.fetchall()

        if not result_query:
            raise ValidationError(_("No se encontraron movimientos para el año especificado. Por favor verifique!"))

        line_ids = []
        move_dict = {
            'company_id': self.env.company.id,
            'ref': 'Cierre contable año: ' + year,
            'journal_id': self.journal_id.id,
            'date': d_end_date,
            'accounting_closing_id': self.id
        }

        total = 0
        for result in result_query:
            account_id = result[0]
            partner_id = result[1]
            analytic_account_id = result[2]
            balance = result[3]

            debit = 0
            credit = 0
            total += balance

            if balance > 0:
                credit = abs(balance)
            elif balance < 0:
                debit = abs(balance)
            else:
                continue

            line = {
                'name': 'Cierre contable año: ' + year,
                'partner_id': partner_id,
                'account_id': account_id,
                'journal_id': self.journal_id.id,
                'date': d_end_date,
                'debit': debit,
                'credit': credit,
                'analytic_account_id': analytic_account_id,
            }
            line_ids.append(line)

        debit = 0
        credit = 0
        if total > 0:
            debit = abs(total)
        elif total < 0:
            credit = abs(total)

        line = {
            'name': 'Cierre contable año: ' + year,
            'partner_id': self.company_id.partner_id.id,
            'account_id': self.counterparty_account.id,
            'journal_id': self.journal_id.id,
            'date': d_end_date,
            'debit': debit,
            'credit': credit
        }
        line_ids.append(line)

        move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
        move = self.env['account.move'].create(move_dict)
        self.balance = total

        return True
