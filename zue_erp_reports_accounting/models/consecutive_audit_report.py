from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class zue_consecutive_audit_report(models.Model):
    _name = 'zue.consecutive.audit.report'
    _description = 'Informe de auditoria de consecutivos'

    z_journal_ids = fields.Many2many('account.journal', string='Diarios')
    z_initial_date = fields.Date(string='Fecha inicial', required=True)
    z_end_date = fields.Date(string='Fecha final', required=True)

    def generate_report(self):
        datas = {
            'id': self.id,
            'model': 'zue.consecutive.audit.report'
        }

        return {
            'type': 'ir.actions.report',
            'report_name': 'zue_erp_reports_accounting.zue_consecutive_audit_report_document',
            'report_type': 'qweb-html',
            'datas': datas
        }

    def generate_info(self):
        for record in self:
            lst_info_journal = []
            #Obtener diarios
            obj_journal = self.env['account.journal']
            if len(record.z_journal_ids) > 0:
                obj_journal = record.z_journal_ids
            else:
                obj_journal = self.env['account.journal'].search([])
            #Verificar facturas por diario
            for journal in obj_journal:
                domain = [('state', '=', 'posted'), ('date', '>=', record.z_initial_date),
                          ('date', '<=', record.z_end_date)]
                domain.append(('journal_id','=',journal.id))
                obj_account_move = self.env['account.move'].search(domain)
                if len(obj_account_move) > 0:
                    sequence_numbers = [i.sequence_number for i in obj_account_move]
                    min_sequence_number = min(sequence_numbers)
                    max_sequence_number = max(sequence_numbers)
                    missing_sequence_number = []
                    for sequence in range(min_sequence_number,max_sequence_number+1):
                        if sequence not in sequence_numbers:
                            missing_sequence_number.append(sequence)
                    lst_info_journal.append({'journal_id':journal.id,
                                            'journal_name':journal.name,
                                            'min_sequence_number':min_sequence_number,
                                            'max_sequence_number':max_sequence_number,
                                            'missing_sequence_number':missing_sequence_number})
            if len(lst_info_journal) > 0:
                return lst_info_journal
            else:
                raise ValidationError('No se encontro información con los filtros seleccionados, por favor verificar.')
