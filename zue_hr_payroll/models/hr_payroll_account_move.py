# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from .browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips
from odoo.tools import float_compare, float_is_zero

from collections import defaultdict
from datetime import datetime, timedelta, date, time
import pytz

class account_move_line(models.Model):
    _inherit = 'account.move.line'

    z_hr_salary_rule_id = fields.Many2one('hr.salary.rule', string='Regla salarial')
    z_hr_struct_id_id = fields.Many2one('hr.payroll.structure', string='Estructura salarial')

class account_move(models.Model):
    _inherit = 'account.move'

    def hr_accounting_public_employees(self):
        for record in self:
            for line in record.line_ids:
                if line.z_hr_salary_rule_id:
                    if line.z_hr_salary_rule_id.z_account_id_cxp:
                        #Obtener regla NETO
                        obj_rule_net = self.env['hr.salary.rule'].search(
                            [('code', '=', 'NET'), ('struct_id', '=', line.z_hr_struct_id_id.id)], limit=1)
                        line_net = record.line_ids.filtered(lambda x: x.z_hr_salary_rule_id == obj_rule_net)
                        #Crear nueva linea con el registro de credito para publicos
                        addref_work_address_account_moves = self.env['ir.config_parameter'].sudo().get_param(
                            'zue_hr_payroll.addref_work_address_account_moves') or False
                        if addref_work_address_account_moves and line.partner_id:
                            if line.partner_id.parent_id:
                                name = f"{line.partner_id.parent_id.vat} {line.partner_id.display_name}|{line.z_hr_salary_rule_id.name}"
                            else:
                                name = f"{line.partner_id.vat} {line.partner_id.display_name}|{line.z_hr_salary_rule_id.name}"
                        else:
                            name = line.z_hr_salary_rule_id.name

                        line_create = {
                            'move_id':record.id,
                            'name': name,
                            'partner_id': line.partner_id.id,
                            'account_id': line.z_hr_salary_rule_id.z_account_id_cxp.id,
                            'journal_id': line.journal_id.id,
                            'date': line.date,
                            'debit': line.credit,
                            'credit': line.debit,
                            'analytic_account_id': line.analytic_account_id.id,
                            'z_hr_salary_rule_id': line.z_hr_salary_rule_id.id,
                        }
                        if line_net.debit == 0 and line_net.credit > 0:
                            if line.debit > 0:
                                if line_net.credit - line.debit >= 0:
                                    line_update_create = {'credit':line_net.credit - line.debit}
                                else:
                                    line_update_create = {'account_id':line.z_hr_salary_rule_id.z_account_id_cxp.id,
                                                          'debit':abs(line_net.credit - line.debit),
                                                          'credit':0}
                            if line.credit > 0:
                                line_update_create = {'credit':line_net.credit + line.credit}
                        else:
                            line_update_create = {'account_id': line.z_hr_salary_rule_id.z_account_id_cxp.id,
                                                  'debit': (line_net.debit + line.debit) if line.debit > 0 else (line_net.debit - line.credit),
                                                  'credit': 0}
                        record.write({'line_ids': [(0, 0, line_create),(1, line_net.id, line_update_create)]})
                        #Link de ayuda: https://www.odoo.com/documentation/15.0/es/developer/reference/backend/orm.html?highlight=many2many#odoo.fields.Command

class Hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    # ---------------------------------------CONTABILIZACIÓN DE LA NÓMINA---------------------------------------------#

    # Items contabilidad
    def _prepare_line_values(self, line, account_id, date, debit, credit, analytic_account_id):
        addref_work_address_account_moves = self.env['ir.config_parameter'].sudo().get_param(
            'zue_hr_payroll.addref_work_address_account_moves') or False
        if addref_work_address_account_moves and line.slip_id.employee_id.address_id:
            if line.slip_id.employee_id.address_id.parent_id:
                name = f"{line.slip_id.employee_id.address_id.parent_id.vat} {line.slip_id.employee_id.address_id.display_name}|{line.name}"
            else:
                name = f"{line.slip_id.employee_id.address_id.vat} {line.slip_id.employee_id.address_id.display_name}|{line.name}"
        else:
            name = line.name

        return {
            'name': name,
            'partner_id': line.partner_id.id,
            'account_id': account_id,
            'journal_id': line.slip_id.struct_id.journal_id.id,
            'date': date,
            'debit': debit,
            'credit': credit,
            'analytic_account_id': analytic_account_id,
            'z_hr_salary_rule_id': line.salary_rule_id.id,
            'z_hr_struct_id_id': line.slip_id.struct_id.id,
            'tax_base_amount': sum([i.result_calculation for i in line.slip_id.rtefte_id.deduction_retention.filtered(lambda x: x.concept_deduction_code == 'TOTAL_ING_BASE_O')]) if line.salary_rule_id.code == 'RETFTE001' or line.salary_rule_id.code == 'RETFTE_PRIMA001' else 0,
            # line.salary_rule_id.analytic_account_id.id or line.slip_id.contract_id.analytic_account_id.id,
        }

    # Verificar existencia de items
    def _get_existing_lines(self, line_ids, line, account_id, debit, credit):
        existing_lines = (
            line_id for line_id in line_ids if
            line_id['name'] == line.name
            and line_id['partner_id'] == line.partner_id.id
            and line_id['account_id'] == account_id
            and line_id['analytic_account_id'] == (
                        line.salary_rule_id.analytic_account_id.id or line.slip_id.contract_id.analytic_account_id.id)
            and ((line_id['debit'] > 0 and credit <= 0) or (line_id['credit'] > 0 and debit <= 0)))
        return next(existing_lines, False)

    # Contabilización de la liquidación de nómina - se sobreescribe el metodo original
    def _action_create_account_move(self):
        # ZUE - Obtener modalidad de contabilización
        settings_batch_account = self.env['ir.config_parameter'].sudo().get_param(
            'zue_hr_payroll.module_hr_payroll_batch_account') or '0'

        precision = self.env['decimal.precision'].precision_get('Payroll')

        # Add payslip without run
        payslips_to_post = self#.filtered(lambda slip: not slip.payslip_run_id)

        # Adding pay slips from a batch and deleting pay slips with a batch that is not ready for validation.
        # payslip_runs = (self - payslips_to_post).mapped('payslip_run_id')
        # for run in payslip_runs:
        #     if run._are_payslips_ready():
        #         payslips_to_post |= run.slip_ids

        # A payslip need to have a done state and not an accounting move.
        payslips_to_post = payslips_to_post.filtered(lambda slip: slip.state == 'done' and not slip.move_id)

        # Check that a journal exists on all the structures
        if any(not payslip.struct_id for payslip in payslips_to_post):
            raise ValidationError(_('One of the contract for these payslips has no structure type.'))
        if any(not structure.journal_id for structure in payslips_to_post.mapped('struct_id')):
            raise ValidationError(_('One of the payroll structures has no account journal defined on it.'))

        slip_mapped_data = {
            slip.struct_id.journal_id.id: {fields.Date().end_of(slip.date_to, 'month'): self.env['hr.payslip']} for slip
            in payslips_to_post}
        for slip in payslips_to_post:
            slip_mapped_data[slip.struct_id.journal_id.id][fields.Date().end_of(slip.date_to, 'month')] |= slip

        for journal_id in slip_mapped_data:  # For each journal_id.
            for slip_date in slip_mapped_data[journal_id]:  # For each month.
                line_ids = []
                debit_sum = 0.0
                credit_sum = 0.0
                if slip.struct_id.process in ['vacaciones']:
                    date = slip.date_from  # slip_date
                else:
                    date = slip.date_to  # slip_date
                move_dict = {
                    'narration': '',
                    'ref': date.strftime('%B %Y'),
                    'journal_id': journal_id,
                    'date': date,
                }

                for slip in slip_mapped_data[journal_id][slip_date]:
                    if len(slip.line_ids) > 0:
                        if settings_batch_account == '1':  # Si en ajustes tiene configurado 'Crear movimiento contable por empleado'
                            # Se limpian los datos para crear un nuevo movimiento
                            line_ids = []
                            debit_sum = 0.0
                            credit_sum = 0.0
                            # date = slip_date
                            move_dict = {
                                'narration': '',
                                'ref': slip.display_name,
                                'journal_id': journal_id,
                                'date': date,
                            }

                        move_dict['narration'] += slip.number or '' + ' - ' + slip.employee_id.name
                        move_dict['narration'] += '\n'
                        print(slip.line_ids.filtered(lambda line: line.category_id))
                        for line in slip.line_ids.filtered(lambda line: line.category_id):
                            amount = -line.total if slip.credit_note else line.total
                            if line.code == 'NET':  # Check if the line is the 'Net Salary'.
                                obj_rule_net = self.env['hr.salary.rule'].search([('code','=','NET'),('struct_id','=',slip.struct_id.id)],limit=1)
                                if len(obj_rule_net) > 0:
                                    line.write({'salary_rule_id':obj_rule_net.id})
                                for tmp_line in slip.line_ids.filtered(lambda line: line.category_id):
                                    if tmp_line.salary_rule_id.not_computed_in_net:  # Check if the rule must be computed in the 'Net Salary' or not.
                                        if amount > 0:
                                            amount -= abs(tmp_line.total)
                                        elif amount < 0:
                                            amount += abs(tmp_line.total)
                            if float_is_zero(amount, precision_digits=precision):
                                continue

                            debit_account_id = line.salary_rule_id.account_debit.id
                            credit_account_id = line.salary_rule_id.account_credit.id

                            # Lógica de ZUE - Obtener cuenta contable de acuerdo a la parametrización de la regla salarial
                            debit_third_id = line.partner_id.id
                            credit_third_id = line.partner_id.id
                            analytic_account_id = line.slip_id.analytic_account_id.id

                            for account_rule in line.salary_rule_id.salary_rule_accounting:
                                # Validar ubicación de trabajo
                                bool_work_location = False
                                if account_rule.work_location.id == slip.employee_id.address_id.id or account_rule.work_location.id == False:
                                    bool_work_location = True
                                # Validar compañia
                                bool_company = False
                                if account_rule.company.id == slip.employee_id.company_id.id or account_rule.company.id == False:
                                    bool_company = True
                                # Validar departamento
                                bool_department = False
                                if account_rule.department.id == slip.employee_id.department_id.id or account_rule.department.id == slip.employee_id.department_id.parent_id.id or account_rule.department.id == slip.employee_id.department_id.parent_id.parent_id.id or account_rule.department.id == False:
                                    bool_department = True

                                if bool_department and bool_company and bool_work_location:
                                    debit_account_id = account_rule.debit_account.id
                                    credit_account_id = account_rule.credit_account.id

                                    # Tercero debito
                                    if account_rule.third_debit == 'entidad':
                                        debit_third_id = line.entity_id.partner_id
                                        # Recorrer entidades empleado
                                        for entity in slip.employee_id.social_security_entities:
                                            if entity.contrib_id.type_entities == 'eps' and line.code == 'SSOCIAL001':  # SALUD
                                                debit_third_id = entity.partner_id.partner_id
                                            if entity.contrib_id.type_entities == 'pension' and (
                                                    line.code == 'SSOCIAL002' or line.code == 'SSOCIAL003' or line.code == 'SSOCIAL004'):  # Pension
                                                debit_third_id = entity.partner_id.partner_id
                                            if entity.contrib_id.type_entities == 'subsistencia' and line.code == 'SSOCIAL003':  # Subsistencia
                                                debit_third_id = entity.partner_id.partner_id
                                            if entity.contrib_id.type_entities == 'solidaridad' and line.code == 'SSOCIAL004':  # Solidaridad
                                                debit_third_id = entity.partner_id.partner_id

                                    elif account_rule.third_debit == 'compañia':
                                        debit_third_id = slip.employee_id.company_id.partner_id
                                    elif account_rule.third_debit == 'empleado':
                                        debit_third_id = slip.employee_id.address_home_id

                                    # Tercero credito
                                    if account_rule.third_credit == 'entidad':
                                        credit_third_id = line.entity_id.partner_id
                                        # Recorrer entidades empleado
                                        for entity in slip.employee_id.social_security_entities:
                                            if entity.contrib_id.type_entities == 'eps' and line.code == 'SSOCIAL001':  # SALUD
                                                credit_third_id = entity.partner_id.partner_id
                                            if entity.contrib_id.type_entities == 'pension' and (
                                                    line.code == 'SSOCIAL002' or line.code == 'SSOCIAL003' or line.code == 'SSOCIAL004'):  # Pension
                                                credit_third_id = entity.partner_id.partner_id
                                            if entity.contrib_id.type_entities == 'subsistencia' and line.code == 'SSOCIAL003':  # Subsistencia
                                                credit_third_id = entity.partner_id.partner_id
                                            if entity.contrib_id.type_entities == 'solidaridad' and line.code == 'SSOCIAL004':  # Solidaridad
                                                credit_third_id = entity.partner_id.partner_id

                                    elif account_rule.third_credit == 'compañia':
                                        credit_third_id = slip.employee_id.company_id.partner_id
                                    elif account_rule.third_credit == 'empleado':
                                        credit_third_id = slip.employee_id.address_home_id

                                    # Asignación de Tercero final y Cuenta analitica cuando la cuenta contable inicie por 4,5,6 o 7
                                    if debit_account_id and amount >= 0:
                                        line.partner_id = debit_third_id
                                        if len(account_rule.debit_account) == 0:
                                            raise ValidationError(
                                                _('La regla salarial ' + account_rule.salary_rule.name + ' no esta bien parametrizada de forma contable, por favor verificar.'))
                                        analytic_account_id = line.slip_id.analytic_account_id.id if account_rule.debit_account.code[
                                                                                                         0:1] in ['4',
                                                                                                                  '5',
                                                                                                                  '6',
                                                                                                                  '7'] else analytic_account_id
                                    elif (credit_third_id and amount < 0) or (credit_account_id and line.code == 'NET'):
                                        line.partner_id = credit_third_id
                                        if len(account_rule.credit_account) == 0:
                                            raise ValidationError(
                                                _('La regla salarial ' + account_rule.salary_rule.name + ' no esta bien parametrizada de forma contable, por favor verificar.'))
                                        analytic_account_id = line.slip_id.analytic_account_id.id if account_rule.credit_account.code[
                                                                                                         0:1] in ['4',
                                                                                                                  '5',
                                                                                                                  '6',
                                                                                                                  '7'] else analytic_account_id

                                        # Fin Lógica ZUE
                            net_account = ''
                            if line.code == 'NET':
                                net_account = 'debit' if amount < 0 else 'credit'

                            if (debit_account_id and amount >= 0 and line.code != 'NET') or (debit_account_id and net_account == 'debit'):  # If the rule has a debit account.
                                debit = abs(amount) if abs(amount) > 0.0 else 0.0
                                credit = 0.0  # -amount if amount < 0.0 else 0.0

                                debit_line = False  # self._get_existing_lines(line_ids, line, debit_account_id, debit, credit)

                                if not debit_line:
                                    debit_line = self._prepare_line_values(line, debit_account_id, date, debit, credit,
                                                                           analytic_account_id)
                                    line_ids.append(debit_line)
                                else:
                                    debit_line['debit'] += debit
                                    debit_line['credit'] += credit

                            if (credit_account_id and amount < 0 and line.code != 'NET') or (credit_account_id and net_account == 'credit'):  # If the rule has a credit account.
                                debit = 0.0  # -amount if amount < 0.0 else 0.0
                                credit = abs(amount) if abs(amount) > 0.0 else 0.0
                                credit_line = False  # self._get_existing_lines(line_ids, line, credit_account_id, debit, credit)

                                if not credit_line:
                                    credit_line = self._prepare_line_values(line, credit_account_id, date, debit,
                                                                            credit, analytic_account_id)
                                    line_ids.append(credit_line)
                                else:
                                    credit_line['debit'] += debit
                                    credit_line['credit'] += credit

                        for line_id in line_ids:  # Get the debit and credit sum.
                            debit_sum += line_id['debit']
                            credit_sum += line_id['credit']

                        # The code below is called if there is an error in the balance between credit and debit sum.
                        if abs(debit_sum - credit_sum) > 10:
                            raise ValidationError(
                                _('Verificar la dinamica contable de las reglas salariales, debido a que existe una diferencia de ' + str(
                                    abs(debit_sum - credit_sum)) + ' pesos - Liquidación '+str(slip.display_name)+'.'))

                        #Descripción ajuste al peso
                        addref_work_address_account_moves = self.env['ir.config_parameter'].sudo().get_param(
                            'zue_hr_payroll.addref_work_address_account_moves') or False
                        if addref_work_address_account_moves and slip.employee_id.address_id:
                            if slip.employee_id.address_id.parent_id:
                                adjustment_entry_name = f"{slip.employee_id.address_id.parent_id.vat} {slip.employee_id.address_id.display_name}|Ajuste al peso"
                            else:
                                adjustment_entry_name = f"{slip.employee_id.address_id.vat} {slip.employee_id.address_id.display_name}|Ajuste al peso"
                        else:
                            adjustment_entry_name = 'Ajuste al peso'

                        if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                            acc_id = slip.journal_id.default_account_id.id
                            if not acc_id:
                                raise UserError(
                                    _('The Expense Journal "%s" has not properly configured the Credit Account!') % (
                                        slip.journal_id.name))
                            existing_adjustment_line = (
                                line_id for line_id in line_ids if line_id['name'] == adjustment_entry_name#_('Adjustment Entry')
                            )
                            adjust_credit = next(existing_adjustment_line, False)

                            if not adjust_credit:
                                adjust_credit = {
                                    'name': adjustment_entry_name,#_('Adjustment Entry'),
                                    'partner_id': slip.employee_id.address_home_id.id,
                                    'account_id': acc_id,
                                    'journal_id': slip.journal_id.id,
                                    'date': date,
                                    'debit': 0.0,
                                    'credit': debit_sum - credit_sum,
                                    'analytic_account_id': slip.analytic_account_id.id,
                                }
                                line_ids.append(adjust_credit)
                            else:
                                adjust_credit['credit'] = debit_sum - credit_sum

                        elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                            acc_id = slip.journal_id.default_account_id.id
                            if not acc_id:
                                raise UserError(
                                    _('The Expense Journal "%s" has not properly configured the Debit Account!') % (
                                        slip.journal_id.name))
                            existing_adjustment_line = (
                                line_id for line_id in line_ids if line_id['name'] == adjustment_entry_name#_('Adjustment Entry')
                            )
                            adjust_debit = next(existing_adjustment_line, False)

                            if not adjust_debit:
                                adjust_debit = {
                                    'name': adjustment_entry_name,#_('Adjustment Entry'),
                                    'partner_id': slip.employee_id.address_home_id.id,
                                    'account_id': acc_id,
                                    'journal_id': slip.journal_id.id,
                                    'date': date,
                                    'debit': credit_sum - debit_sum,
                                    'credit': 0.0,
                                    'analytic_account_id': slip.analytic_account_id.id,
                                }
                                line_ids.append(adjust_debit)
                            else:
                                adjust_debit['debit'] = credit_sum - debit_sum

                        if settings_batch_account == '1':
                            # Add accounting lines in the move
                            move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
                            move = self.env['account.move'].create(move_dict)
                            move.hr_accounting_public_employees()
                            slip.write({'move_id': move.id, 'date': date})

                if settings_batch_account == '0':
                    # Add accounting lines in the move
                    move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
                    move = self.env['account.move'].create(move_dict)
                    for slip in slip_mapped_data[journal_id][slip_date]:
                        slip.write({'move_id': move.id, 'date': date})
        return True


