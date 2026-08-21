from odoo import fields, models, api, tools
from odoo.exceptions import UserError, ValidationError
from itertools import groupby


class zue_annex_thirdparty_account(models.TransientModel):
    _name = 'zue.annex.thirdparty.account'
    _description = 'Anexo cuenta tercero'

    z_initial_date = fields.Date('Fecha inicial', required= True)
    z_final_date = fields.Date('Fecha final', required= True)
    z_concept_id = fields.Many2one('zue.concept.accounts', string='Concepto', required= True)

    def get_accounts(self):
        initial_date = self.z_initial_date
        final_date = self.z_final_date
        concept = self.z_concept_id
        excluded_thirdparties = concept.z_excluded_thirdparty_ids

        if initial_date and final_date:
            obj_accounts = self.env['account.move.line'].search([('date', '>=', initial_date),('date', '<=', final_date),
                                                                 ('account_id', 'in', concept.z_accounting_details_ids.ids),
                                                                 ('partner_id', 'not in', excluded_thirdparties.ids)])

            if obj_accounts:
                report_data = {}
                for obj in obj_accounts.sorted(lambda line: line.account_id.code):
                    dict_documents = dict(self.env['res.partner']._fields['x_document_type'].selection)
                    document_type = dict_documents.get(obj.partner_id.x_document_type) if obj.partner_id.x_document_type else ''
                    document_num = obj.partner_id.vat
                    thirdparty = obj.partner_id.name
                    account_name = obj.account_id.code + ' | ' + obj.account_id.name
                    account_code = obj.account_id.code
                    credit = obj.credit
                    debit = obj.debit
                    partner_type = 'Persona' if obj.partner_id.company_type == 'person' else 'Compañia'

                    if account_name not in report_data:
                        report_data[account_name] = {'Persona': {}, 'Compañia': {}}

                    if document_num not in report_data[account_name][partner_type]:
                        report_data[account_name][partner_type][document_num] = {}

                    if thirdparty not in report_data[account_name][partner_type][document_num]:
                        report_data[account_name][partner_type][document_num][thirdparty] = {
                            'account_code': account_code,
                            'credit': 0,
                            'debit': 0,
                            'base': 0
                        }

                    report_data[account_name][partner_type][document_num][thirdparty]['credit'] += credit
                    report_data[account_name][partner_type][document_num][thirdparty]['debit'] += debit
                    report_data[account_name][partner_type][document_num][thirdparty]['base'] += obj.tax_base_amount

                report = []
                for account_name, partner_types in sorted(report_data.items()):
                    for partner_type, document_num_data in partner_types.items():
                        account_group = []
                        total_registered_value = 0
                        total_base_value = 0

                        sorted_document_num_data = sorted(document_num_data.items(), key=lambda x: x[0])

                        for document_num, thirdparty_data in sorted_document_num_data:
                            for thirdparty, values in thirdparty_data.items():
                                credit = values['credit']
                                debit = values['debit']
                                base = values['base']
                                registered_value = credit - debit
                                account_code = values['account_code']

                                account_group.append({
                                    'partner_type': partner_type,
                                    'document_type': document_type,
                                    'document_num': document_num,
                                    'thirdparty': thirdparty,
                                    'account_name': account_name,
                                    'registered_value': registered_value,
                                    'base_value': base
                                })

                                total_registered_value += registered_value
                                total_base_value += base

                        report.append({
                            'account_name': account_name,
                            'account_code': account_code,
                            'partner_type': partner_type,
                            'accounts': account_group,
                            'total_registered_value': total_registered_value,
                            'total_base_value': total_base_value
                        })

                return report

    def get_summary_accounts(self):
        #se llama el metodo anterior
        report = self.get_accounts()
        summary = {}
        summary_gran_total = 0
        # Se recorre el método anterior para traer los valores específicos
        for obj in report:
            account_name = obj['account_name']
            total_value = obj['total_registered_value']
            partner_type = obj['partner_type']
            summary_gran_total += total_value

            if account_name not in summary:
                summary[account_name] = {
                    'total_value': 0,
                    'partner_types': {}
                }

            summary[account_name]['total_value'] += total_value

            if partner_type in summary[account_name]['partner_types']:
                summary[account_name]['partner_types'][partner_type] += total_value
            else:
                summary[account_name]['partner_types'][partner_type] = total_value

        summary_report = []
        for account_name, totals in sorted(summary.items()):
            summary_report.append({
                'account_name': account_name,
                'total_value': totals['total_value']
            })

            for partner_type, partner_value in totals['partner_types'].items():
                summary_report.append({
                    'account_name': f"  {partner_type}",
                    'total_value': partner_value
                })
        summary_report.append({
            'account_name': 'Resumen gran total',
            'total_value': summary_gran_total
        })

        return summary_report

    def generate_pdf(self):
        datas = {
            'id': self.id,
            'model': 'zue.annex.thirdparty.account'
        }

        return {
            'type': 'ir.actions.report',
            'report_name': 'zue_erp_reports_accounting.annex_thirdparty_account_id',
            'report_type': 'qweb-pdf',
            'datas': datas
        }