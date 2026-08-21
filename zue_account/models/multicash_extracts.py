from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import base64

class zue_bank_multicash_extracts(models.TransientModel):
    _name = 'zue.bank.multicash.extracts'
    _description = 'Extractos multicash'

    z_company_id = fields.Many2one('res.company', string='Compañía', required=True, default=lambda self: self.env.company)

    z_extract_origin = fields.Binary(string='Archivo')

    def convert_extract(self):
        for record in self:
            # Validar que el archivo esté presente
            if not record.z_extract_origin:
                raise ValidationError(_('Debe seleccionar un archivo para procesar. Por favor verifique.'))
            
            try:
                information_lines = []
                file_txt = base64.b64decode(record.z_extract_origin)
                file_txt = file_txt.decode("utf-8")
                lines_txt = file_txt.split("\n")
            except Exception as e:
                raise ValidationError(_('El archivo seleccionado no es válido o está corrupto. Por favor verifique el archivo e intente nuevamente.'))
            obj_journal = self.env['account.journal']
            obj_account_bank = self.env['res.partner.bank']
            date_process = False

            for line in lines_txt:
                if len(line) > 0:
                    items_line = line.split(';')
                    date_process = datetime.strptime(items_line[3],'%d.%m.%y').date()
                    account_number = str(items_line[1])
                    obj_account_bank = self.env['res.partner.bank'].search([('acc_number','like',account_number)],limit=1)
                    obj_journal = self.env['account.journal'].search([('bank_account_id','=',obj_account_bank.id)],limit=1)
                    obj_partner = self.env['res.partner'].search([('x_type_thirdparty','not in',[2]),('x_type_thirdparty','!=',False),'|',('vat', '=', str(items_line[16])),('vat', '=', str(items_line[16])[:-1]),('vat', '!=', '')],limit=1)
                    if len(obj_partner) == 0:
                        id_partner = False
                    elif obj_partner.id == obj_account_bank.z_partner_id.id:
                        id_partner = False
                    else:
                        id_partner = obj_partner.id
                    # if len(obj_account_bank) == 0:
                    #     raise ValidationError(f'No se encontro el número de cuenta {account_number}, por favor verificar')
                    if len(obj_journal) == 0:
                        raise ValidationError(f'No se encontro diario para el banco {obj_account_bank.bank_id.name}, por favor verificar')

                    payment_ref = ''
                    payment_type_plano = str(items_line[6])
                    obj_movement_types = self.env['zue.bank.movement.types'].search([('z_movement_types','=',payment_type_plano[0:4])],limit=1)
                    if len(obj_movement_types) == 1:
                        payment_ref = obj_movement_types.z_movement_name

                    transaction_number = str(items_line[16])
                    obj_transaction_table = self.env['zue.bank.transaction.table'].search([('z_transaction_code', '=', payment_type_plano[4:])], limit=1)
                    if len(obj_transaction_table) == 1:
                        payment_ref = payment_ref +' '+ obj_transaction_table.z_transaction_name +' '+transaction_number

                    if id_partner:
                        information = (0,0,{
                            'date': date_process,
                            'payment_ref': payment_ref,
                            'partner_id': id_partner,
                            'amount': items_line[10],
                            'journal_id': obj_journal.id,
                            # 'account_number': account_number,
                        })
                    else:
                        information = (0, 0, {
                            'date': date_process,
                            'payment_ref': payment_ref,
                            'amount': items_line[10],
                            'journal_id': obj_journal.id,
                            # 'account_number': account_number,
                        })
                    information_lines.append(information)

            if len(information_lines) == 0:
                raise ValidationError('No se encontro información en el archivo seleccionado.')

            dict_bank = {
                'name': f'MOVIMIENTOS {obj_account_bank.bank_id.name} Fecha: {date_process}',
                'journal_id': obj_journal.id,
                'date': date_process,
                'company_id': record.z_company_id.id,
                'line_ids': information_lines,
            }
            obj_bank_statement = self.env['account.bank.statement'].with_context(from_multicash=True).create(dict_bank)
            obj_bank_statement_line = self.env['account.bank.statement.line'].action_save_close
            # obj_bank_statement.action_bank_reconcile_bank_statements()
            return True

class res_partner_bank(models.Model):
    _inherit = 'res.partner.bank'

    z_partner_id = fields.Many2one('res.partner', 'Asociado')

    _unique_number = models.Constraint('unique(sanitized_acc_number, partner_id, company_id)',
        'The combination Account Number/Partner must be unique.')
