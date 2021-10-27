# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import decimal

class account_account(models.Model):
    _inherit = 'account.account'

    account_distribution = fields.Boolean(string='Cuenta de distribución')

class account_move(models.Model):
    _inherit = 'account.move'

    distribution_execution_id = fields.Many2one('distribution.rules.execution', string='Regla de distribución ejecutada', ondelete='cascade')

class hr_distribution_rules(models.Model):
    _name = 'hr.distribution.rules'
    _description = 'Reglas de distribución'
    
    #company_id = fields.Many2one('res.company', string = 'Compañía', required=True, default=lambda self: self.env.company.id)
    name= fields.Char(string= 'Nombre', required=True)
    origin_analytical_account_id = fields.Many2one('account.analytic.account', 'Cuenta analítica', required=True)
    originating_account_id = fields.Many2many('account.account',string='Cuentas contables')
    distribution_account_id = fields.Many2one('account.account', 'Cuenta de distribución', domain=[('account_distribution', '=', True)])
    model_id =  fields.Many2one('hr.distribution.model', 'Modelo de distribición')
    model_type = fields.Selection(related='model_id.model_type',string='Tipo de modelo', store=True, readonly=True)
    base = fields.Selection(related='model_id.base',string='Con base en', store=True, readonly=True)
    distribution_rules_details = fields.One2many('hr.distribution.rules.details', 'distribution_rules_id', string='Info Estático')
    operational_filter_type = fields.Selection([('1', 'Vehículo'),
                                ('2', 'Sucursal'),
                                ('3', 'Servicio'),
                                ('4', 'Contrato'),
                                ], string='Filtro posible')    
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehículo')
    branch_id = fields.Many2one('zue.res.branch', 'Sucursal')
    service_id = fields.Many2one('mntc.services.type', 'Servicio')
    contract_id = fields.Many2one('cntr.contract.encab', 'Contrato')
    analytical_target_account_structure = fields.Selection([('1', 'Ingresos'),
                            ('2', 'Operaciones'),
                            ('3', 'Mantenimiento'),
                            ('4', 'Taller'),
                            ('5', 'Almacén'),
                            ('6', 'Activos'),
                            ('7', 'Backoffice')        
                            ], string='Estructura cuenta analitica destino')
    initial_year = fields.Integer('Año inicial', required=True)
    initial_month = fields.Selection([('1', 'Enero'),
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
                            ], string='Mes inicial', required=True)
    final_year= fields.Integer('Año final', required=True)
    final_month = fields.Selection([('1', 'Enero'),
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
                            ], string='Mes final', required=True)
    initial_date = fields.Date('Fecha Inicial', compute='_get_initial_date', store=True)
    final_date = fields.Date('Fecha Final', compute='_get_final_date', store=True)
    distribution_rules_execution_id = fields.Many2one('distribution.rules.execution', 'Ejecución')

    @api.depends('initial_month', 'initial_year')
    def _get_initial_date(self):
        for record in self:
            start_date = datetime.strptime(('1/' + str(record.initial_month) + '/' + str(record.initial_year)), '%d/%m/%Y')

            record.initial_date = start_date.date()

    @api.depends('final_month', 'final_year')
    def _get_final_date(self):
        for record in self:
            end_date = datetime.strptime(('1/' + str(record.final_month) + '/' + str(record.final_year)), '%d/%m/%Y')
            end_date = end_date + relativedelta(months=1)
            end_date = end_date - timedelta(days=1)

            record.final_date = end_date.date()


    @api.constrains('distribution_rules_details')
    def _check_distribution_rules_details(self):  
        for record in self:
            if record.model_type == 'S' and record.base == '1':
                porc_total = 0
                for item in record.distribution_rules_details:
                    porc_total += item.percentage

                if porc_total != 100:
                    raise UserError(_('Los porcentajes no completan un 100%, por favor verficar.'))  

class distribution_rules_execution_history(models.Model):
    _name = 'distribution.rules.execution.history'
    _description = 'Historial de ejecución de las reglas de distribución'
    _order = "create_date desc"

    initial_date = fields.Date('Fecha Inicio')
    final_date = fields.Date('Fecha Fin')
    applied_rules = fields.Many2many('hr.distribution.rules', string='Reglas aplicadas')
    user_id = fields.Many2one('res.users', string='Usuario')
    execution_rule_id = fields.Many2one('distribution.rules.execution', string='Usuario ejecución', ondelete='cascade')


class distribution_rules_execution(models.Model):
    _name = 'distribution.rules.execution'
    _description = 'Ejecución de las reglas de distribución'

    name= fields.Char(string= 'Nombre', required=True)
    initial_year = fields.Integer('Año inicial', required=True)
    initial_month = fields.Selection([('1', 'Enero'),
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
                            ], string='Mes inicial', required=True)
    final_year= fields.Integer('Año final', required=True)
    final_month = fields.Selection([('1', 'Enero'),
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
                            ], string='Mes final', required=True)
    initial_date = fields.Date('Fecha Inicial', compute='_get_initial_date', store=True)
    final_date = fields.Date('Fecha Final', compute='_get_final_date', store=True)
    distribution_rule_id = fields.One2many('hr.distribution.rules','distribution_rules_execution_id',
                                           string='Reglas de distribución',
                                           domain="['|','&',('initial_date', '>=', initial_date)," +
                                                  "('initial_date', '<=', final_date)," +
                                                  "'&'," +
                                                  "('final_date', '>=', initial_date)," +
                                                  "('final_date', '<=', final_date)]")
    history_id = fields.One2many('distribution.rules.execution.history','execution_rule_id', string='Histórico de ejecución')
    counter_contab = fields.Integer(compute='compute_counter_contab', string='Movimientos')

    @api.depends('initial_month', 'initial_year')
    def _get_initial_date(self):
        for record in self:
            start_date = datetime.strptime(('1/' + str(record.initial_month) + '/' + str(record.initial_year)),
                                           '%d/%m/%Y')

            record.initial_date = start_date.date()

    @api.depends('final_month', 'final_year')
    def _get_final_date(self):
        for record in self:
            end_date = datetime.strptime(('1/' + str(record.final_month) + '/' + str(record.final_year)), '%d/%m/%Y')
            end_date = end_date + relativedelta(months=1)
            end_date = end_date - timedelta(days=1)

            record.final_date = end_date.date()

    def return_action_to_open(self):
        res = {
            'name': 'Movimientos',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'target': 'current',
            'domain': "[('distribution_execution_id','in',[" + str(self._ids[0]) + "])]"
        }
        return res

    def compute_counter_contab(self):
        count = self.env['account.move'].search_count([('distribution_execution_id', '=', self.id)])
        self.counter_contab = count

    def call_up_wizard(self):
        yes_no = ''
        no_delete = False

        if self.counter_contab > 0:
            obj_contab = self.env['account.move'].search([('distribution_execution_id', '=', self.id)])
            for rows in obj_contab:
                if rows.state != 'draft':
                    no_delete = True
                    break
            if no_delete:
                return {'messages': [{'record': False, 'type': 'warning', 'message': 'Ya hay documentos publicados. No es posible continuar!', }]}
            else:
                yes_no = "El movimiento contable actual para esta ejecución será borrado para crear uno nuevo. Desea continuar?"

            return {
                'name': 'Deseas continuar?',
                'type': 'ir.actions.act_window',
                'res_model': 'zue.confirm.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_distribution_rule_id': self.id,
                            'default_yes_no': yes_no}
            }
        else:
            self.generate_account_move()

    def generate_account_move(self):
        for record in self:
            start_date = datetime.strptime(('1/' + str(record.initial_month) + '/' + str(record.initial_year)), '%d/%m/%Y')
            end_date = datetime.strptime(('1/' + str(record.final_month) + '/' + str(record.final_year)), '%d/%m/%Y')
            end_date = end_date + relativedelta(months=1)
            end_date = end_date - timedelta(days=1)

            start_date_d = start_date.date()
            end_date_d = end_date.date()

            # obj_history = self.env['distribution.rules.execution.history'].search([('execution_rule_id','=',record.id)])
            # if obj_history:
            #     for obj in obj_history:
            #         if start_date_d > obj.initial_date and start_date_d < obj.final_date:
            #             raise ValidationError(_("Ya se realizo una ejecución para el periodo seleccionado. Por favor verifique!"))
            #
            #         if end_date_d > obj.initial_date and end_date_d < obj.final_date:
            #             raise ValidationError(_("Ya se realizo una ejecución para el periodo seleccionado. Por favor verifique!"))
            #
            #         if start_date_d == obj.initial_date and end_date_d == obj.final_date:
            #             raise ValidationError(_("Ya se realizo una ejecución para el periodo seleccionado. Por favor verifique!"))

            if not record.distribution_rule_id:
                obj_rule = self.env['hr.distribution.rules'].search([('id','!=',False)])
            else:
                obj_rule = record.distribution_rule_id

            obj_account = None
            for rule in obj_rule:
                start_date = datetime.strptime(('1/' + str(rule.initial_month) + '/' + str(rule.initial_year)),'%d/%m/%Y')
                end_date = datetime.strptime(('1/' + str(rule.final_month) + '/' + str(rule.final_year)), '%d/%m/%Y')
                end_date = end_date + relativedelta(months=1)
                end_date = end_date - timedelta(days=1)

                # estático
                if rule.model_id.model_type == 'S':
                    debit = 0
                    credit = 0
                    balance = 0
                    tmp_credit = 0
                    tmp_debit = 0

                    obj_move = self.env['account.move.line'].search([('analytic_account_id', '=', rule.origin_analytical_account_id.id),
                                                                    ('account_id', 'in', rule.originating_account_id.ids),
                                                                    ('parent_state', '=', 'posted'),
                                                                    ('date', '>=', start_date),
                                                                    ('date', '<=', end_date)])
                    obj_contract = self.env['cntr.contract.encab'].search([('account_analytic_id', '=', rule.origin_analytical_account_id.id)])

                    if not obj_move:
                        raise ValidationError(_("No se encontraron movimientos para las cuentas contables seleccionadas en la regla '" + rule.name + "'. Por favor verifique!"))
                    if not obj_contract:
                        partner_id = self.env.company.id
                    else:
                        partner_id = obj_contract.customer_id.id
                        #raise ValidationError(_("No hay un contrato con la cuenta analítica seleccionada en el origen contable. Por favor verifique!"))

                    for move in obj_move:
                        debit += move.debit
                        credit += move.credit
                        balance += move.balance

                    obj_journal = self.env['account.journal'].search([('name', '=', 'Distribucion proyectos')], limit=1)
                    if not obj_journal:
                        raise ValidationError(_("No existe un diario para la Distribución de proyectos. Por favor verifique!"))

                    line_ids = []
                    move_dict = {
                                'company_id': self.env.company.id,
                                'ref': 'DISTRIBUCIÓN DE COSTOS: ' + rule.name,
                                'journal_id': obj_journal.id,
                                'date': date.today(),
                                'distribution_execution_id': record.id
                            }

                    if balance < 0:
                        credit = abs(balance)
                        debit = 0
                    elif balance > 0:
                        credit = 0
                        debit = abs(balance)

                    # proporcion
                    if rule.model_id.base == '1':
                        if debit > 0:
                            tmp_credit = debit
                        elif credit > 0:
                            tmp_debit = credit

                        line_debit = {
                                'name': 'DISTRIBUCIÓN DE COSTOS: ' + rule.name,
                                'partner_id': partner_id,
                                'account_id': rule.distribution_account_id.id,
                                'journal_id': obj_journal.id,
                                'date': date.today(),
                                'debit': tmp_debit,
                                'credit': tmp_credit,
                                'analytic_account_id': rule.origin_analytical_account_id.id,
                            }
                        line_ids.append(line_debit)


                        for rows in rule.distribution_rules_details:
                            debit_value = 0
                            credit_value = 0
                            if rows.percentage > 0:
                                debit_value = debit * rows.percentage / 100
                                credit_value = credit * rows.percentage / 100
                            else:
                                raise ValidationError(_("No se ha configurado un porcentaje para esta regla. Por favor verifique!"))

                            if debit > 0:
                                line_debit = {
                                        'name': 'DISTRIBUCIÓN DE COSTOS: ' + rule.name + ' - ' + str(rows.percentage) + '%',
                                        'partner_id': partner_id,
                                        'account_id': rule.distribution_account_id.id,
                                        'journal_id': obj_journal.id,
                                        'date': date.today(),
                                        'debit': debit_value,
                                        'credit': 0,
                                        'analytic_account_id': rows.analytical_account_destination_id.id,
                                    }
                                line_ids.append(line_debit)

                            if credit > 0:
                                line_credit = {
                                        'name': 'DISTRIBUCIÓN DE COSTOS: ' + rule.name + ' - ' + str(rows.percentage) + '%',
                                        'partner_id': partner_id,
                                        'account_id': rule.distribution_account_id.id,
                                        'journal_id': obj_journal.id,
                                        'date': date.today(),
                                        'debit': 0,
                                        'credit': credit_value,
                                        'analytic_account_id': rows.analytical_account_destination_id.id,
                                    }
                                line_ids.append(line_credit)

                    # valores
                    elif rule.model_id.base == '2':
                        tmp_value = abs(debit - credit)
                        total_value = 0

                        if debit > 0:
                            tmp_credit = debit
                        elif credit > 0:
                            tmp_debit = credit

                        line_debit = {
                                'name': 'DISTRIBUCIÓN DE COSTOS: ' + rule.name,
                                'partner_id': partner_id,
                                'account_id': rule.distribution_account_id.id,
                                'journal_id': obj_journal.id,
                                'date': date.today(),
                                'debit': tmp_debit,
                                'credit': tmp_credit,
                                'analytic_account_id': rule.origin_analytical_account_id.id,
                            }
                        line_ids.append(line_debit)


                        for rows in rule.distribution_rules_details:
                            debit_value = 0
                            credit_value = 0
                            if rows.value > 0:
                                if debit > 0:
                                    tmp_value = tmp_value - rows.value

                                    if tmp_value <= 0:
                                        debit_value = abs(tmp_value + rows.value)
                                    elif tmp_value > 0:
                                        debit_value = rows.value

                                    total_value += debit_value

                                    if total_value > debit:
                                        raise ValidationError(_("Se han configurado de forma incorrecta los valores. Por favor verifique!"))

                                elif credit > 0:
                                    tmp_value = credit - rows.value

                                    if tmp_value <= 0:
                                        credit_value = credit
                                    elif tmp_value > 0:
                                        credit_value = rows.value

                                    total_value += credit_value

                                    if total_value > credit:
                                        raise ValidationError(_("Se han configurado de forma incorrecta los valores. Por favor verifique!"))
                            else:
                                raise ValidationError(_("No se ha configurado un valor para esta regla. Por favor verifique!"))

                            if debit > 0:
                                line_debit = {
                                        'name': 'DISTRIBUCIÓN DE COSTOS: ' + rule.name + ' - ' + str(rows.value),
                                        'partner_id': partner_id,
                                        'account_id': rule.distribution_account_id.id,
                                        'journal_id': obj_journal.id,
                                        'date': date.today(),
                                        'debit': debit_value,
                                        'credit': credit_value,
                                        'analytic_account_id': rows.analytical_account_destination_id.id,
                                    }
                                line_ids.append(line_debit)

                            if credit > 0:
                                line_credit = {
                                        'name': 'DISTRIBUCIÓN DE COSTOS: ' + rule.name + ' - ' + str(rows.value),
                                        'partner_id': partner_id,
                                        'account_id': rule.distribution_account_id.id,
                                        'journal_id': obj_journal.id,
                                        'date': date.today(),
                                        'debit': debit_value,
                                        'credit': credit_value,
                                        'analytic_account_id': rows.analytical_account_destination_id.id,
                                    }
                                line_ids.append(line_credit)

                    move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
                    move = self.env['account.move'].create(move_dict)

                    ##viajes
                    #     elif rule.model_id.base == '3':
                    #     # Km
                    #     elif rule.model_id.base == '4':

                # driver
                elif rule.model_id.model_type == 'D':
                    # # proporcion
                    # if rule.model_id.base == '1':

                    # # valores
                    # elif rule.model_id.base == '2':
                    self.env['distribution.rule.drivers'].search([('id', '!=', False)]).unlink()

                    if rule.model_id.base == '3' or rule.model_id.base == '4':
                        count_km, count_trip, tmp_vehicle_id, total_km, total_trip, tmp_contract_id = 0, 0, 0, 0, 0, 0
                        tmp_vehicle = ''
                        new_rows = []
                        domain = []

                        filter_type = rule.operational_filter_type
                        obj_journal = self.env['account.journal'].search([('name', '=', 'Distribucion proyectos')],
                                                                         limit=1)
                        if not obj_journal:
                            raise ValidationError(
                                _("No existe un diario para la Distribución de proyectos. Por favor verifique!"))

                        # domain = [('contract_encab_id', '=', 2)]

                        if filter_type:
                            # Vehículo
                            if filter_type == '1':
                                if rule.vehicle_id:
                                    domain = domain + [('vehicle_id', '=', rule.vehicle_id.placa_nro)]
                            # Sucursal
                            elif filter_type == '2':
                                if rule.branch_id:
                                    domain = domain + [('branch_id', 'ilike', rule.branch_id.name)]
                            # Servicio
                            elif filter_type == '3':
                                if rule.service_id:
                                    domain = domain + [('service_id', 'ilike', rule.service_id.name)]
                            # Contrato
                            elif filter_type == '4':
                                if rule.contract_id:
                                    domain = domain + [('contract_encab_id', '=', rule.contract_id.id)]

                        obj_contract = self.env['cntr.contract.service.detail'].search(domain, order='contract_encab_id, vehicle_id desc')

                        for data in obj_contract:
                            if data.vehicle_id == tmp_vehicle:
                                if tmp_contract_id:
                                    if tmp_contract_id != data.contract_encab_id.id:
                                        driver_vals = {
                                            'vehicle_id': tmp_vehicle_id,
                                            'trip_quantity': count_trip,
                                            'km_quantity': count_km,
                                            'process_id': record.id,
                                            'contract_id': tmp_contract_id
                                        }
                                        new_rows.append(driver_vals)
                                        count_km = data.real_distance
                                        count_trip = 1
                                    else:
                                        count_km += data.real_distance
                                        count_trip += 1
                                else:
                                    count_km += data.real_distance
                                    count_trip += 1
                            else:
                                if tmp_vehicle_id:
                                    driver_vals = {
                                        'vehicle_id': tmp_vehicle_id,
                                        'trip_quantity': count_trip,
                                        'km_quantity': count_km,
                                        'process_id': record.id,
                                        'contract_id': tmp_contract_id
                                    }
                                    new_rows.append(driver_vals)
                                    total_km += count_km
                                    total_trip += count_trip

                                vehicle = self.env['fleet.vehicle'].search([('placa_nro', '=', data.vehicle_id)], limit=1)
                                tmp_vehicle = vehicle.placa_nro
                                tmp_vehicle_id = vehicle.id
                                count_km = data.real_distance
                                count_trip = 1
                            tmp_contract_id = data.contract_encab_id.id

                        if tmp_vehicle_id:
                            driver_vals = {
                                'vehicle_id': tmp_vehicle_id,
                                'trip_quantity': count_trip,
                                'km_quantity': count_km,
                                'process_id': record.id,
                                'contract_id': tmp_contract_id
                            }
                            new_rows.append(driver_vals)
                            total_km += count_km
                            total_trip += count_trip

                        obj_created = self.env['distribution.rule.drivers'].create(new_rows)
                        # distribution_rule_drivers
                        credit, debit, tmp_credit, tmp_debit, balance = 0, 0, 0, 0, 0

                        domain = [('analytic_account_id', 'in', rule.origin_analytical_account_id.ids),
                                 ('account_id', 'in', rule.originating_account_id.ids),
                                 ('parent_state', '=', 'posted'),
                                 ('date', '>=', start_date),
                                 ('date', '<=', end_date)]

                        obj_move = self.env['account.move.line'].search(domain)

                        if not obj_move:
                            continue
                            #raise ValidationError(_("No se encontraron movimientos para las cuentas contables seleccionadas en la regla '" + rule.name + "'. Por favor verifique!"))

                        for move in obj_move:
                            debit += decimal.Decimal(move.debit)
                            credit += decimal.Decimal(move.credit)
                            balance += decimal.Decimal(move.balance)

                        debit = round(debit, 0)
                        credit = round(credit, 0)
                        balance = round(balance, 0)


                        line_ids = []
                        move_dict = {
                            'company_id': self.env.company.id,
                            'ref': 'DISTRIBUCIÓN DE COSTOS: ' + rule.name,
                            'journal_id': obj_journal.id,
                            'date': date.today(),
                            'distribution_execution_id': record.id
                        }

                        if balance < 0:
                            credit = abs(balance)
                            debit = 0
                        elif balance > 0:
                            credit = 0
                            debit = abs(balance)

                        if debit > 0:
                            tmp_credit = debit
                        elif credit > 0:
                            tmp_debit = credit

                        vehicles_to_process = []
                        for obj in obj_created:
                            if not (obj.vehicle_id.id in vehicles_to_process):
                                vehicles_to_process.append(obj.vehicle_id.id)

                        partner_id = self.env.company.id

                        for item in vehicles_to_process:
                            vehicle = self.env['fleet.vehicle'].search([('id', '=', item)])

                            line_debit = {
                                'name': 'DISTRIBUCIÓN DE COSTOS: ' + rule.name,
                                'partner_id': None,
                                'account_id': rule.distribution_account_id.id,
                                'journal_id': obj_journal.id,
                                'date': date.today(),
                                'debit': tmp_debit,
                                'credit': tmp_credit,
                                'analytic_account_id': vehicle.account_analytic_id.id,
                            }
                            line_ids.append(line_debit)

                            prueba = obj_created.search([('vehicle_id', '=', item)])

                            total_trip, total_km = 0, 0

                            for rows in prueba:
                                total_trip += rows.trip_quantity
                                total_km += rows.km_quantity

                            for rows in prueba:
                                debit_value, credit_value, percentage = 0, 0, 0

                                # viajes
                                if rule.model_id.base == '3':
                                    percentage = decimal.Decimal(rows.trip_quantity * 100 / total_trip)
                                # Km
                                elif rule.model_id.base == '4':
                                    percentage = decimal.Decimal(rows.km_quantity * 100 / total_km)

                                if percentage > 0:
                                    debit_value = round(debit * percentage / 100, 2)
                                    credit_value = round(credit * percentage / 100, 2)
                                else:
                                    raise ValidationError(
                                        _("No se ha configurado un porcentaje para esta regla. Por favor verifique!"))

                                name_analytical_account = rows.contract_id.account_analytic_id.name
                                if not name_analytical_account:
                                    raise ValidationError(_("No hay una cuenta analitica configurada para el contrato. Por favor verifique!"))

                                name_analytical_account = name_analytical_account.rpartition('.')[0]

                                if rule.analytical_target_account_structure == '1':
                                    name_analytical_account += '.Ingresos'
                                elif rule.analytical_target_account_structure == '2':
                                    name_analytical_account += '.Operaciones'
                                elif rule.analytical_target_account_structure == '3':
                                    name_analytical_account += '.Mantenimiento'
                                elif rule.analytical_target_account_structure == '4':
                                    name_analytical_account += '.Taller'
                                elif rule.analytical_target_account_structure == '5':
                                    name_analytical_account += '.Almacén'
                                elif rule.analytical_target_account_structure == '6':
                                    name_analytical_account += '.Activos'
                                elif rule.analytical_target_account_structure == '7':
                                    name_analytical_account += '.BackOffice'

                                analytical_account_id = self.env['account.analytic.account'].search([('name', '=', name_analytical_account)]).id
                                if not analytical_account_id:
                                    raise ValidationError(_("No se encontró la estructura de la cuenta analítica configurada. Por favor verifique!"))

                                if debit > 0:
                                    line_debit = {
                                        'name': 'DISTRIBUCIÓN DE COSTOS: ' + rule.name + ' - ' + str(round(percentage, 2)) + '%',
                                        'partner_id': partner_id,
                                        'account_id': rule.distribution_account_id.id,
                                        'journal_id': obj_journal.id,
                                        'date': date.today(),
                                        'debit': debit_value,
                                        'credit': 0,
                                        'analytic_account_id': analytical_account_id,
                                    }
                                    line_ids.append(line_debit)

                                if credit > 0:
                                    line_credit = {
                                        'name': 'DISTRIBUCIÓN DE COSTOS: ' + rule.name + ' - ' + str(round(percentage, 2)) + '%',
                                        'partner_id': partner_id,
                                        'account_id': rule.distribution_account_id.id,
                                        'journal_id': obj_journal.id,
                                        'date': date.today(),
                                        'debit': 0,
                                        'credit': credit_value,
                                        'analytic_account_id': analytical_account_id,
                                    }
                                    line_ids.append(line_credit)

                        total_debit, total_credit = 0, 0
                        for line in line_ids:
                            total_debit += line['debit']
                            total_credit += line['credit']
                        total_total = round(total_debit - total_credit, 2)

                        if total_total != 0 and not obj_account:
                            # Ajuste al peso
                            obj_account = self.env['account.account'].search([('code', '=', '53959501')])

                        if total_total > 0:
                            line_credit = {
                                'name': 'DISTRIBUCIÓN DE COSTOS: Ajuste al peso',
                                'partner_id': partner_id,
                                'account_id': obj_account.id,
                                'journal_id': obj_journal.id,
                                'date': date.today(),
                                'debit': 0,
                                'credit': abs(total_total),
                                'analytic_account_id': None,
                            }
                            line_ids.append(line_credit)
                        elif total_total < 0:
                            line_debit = {
                                'name': 'DISTRIBUCIÓN DE COSTOS: Ajuste al peso',
                                'partner_id': partner_id,
                                'account_id': obj_account.id,
                                'journal_id': obj_journal.id,
                                'date': date.today(),
                                'debit': abs(total_total),
                                'credit': 0,
                                'analytic_account_id': None,
                            }
                            line_ids.append(line_debit)

                        move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
                        move = self.env['account.move'].create(move_dict)
            result = []

            history_vals = {
                    'initial_date': start_date,
                    'final_date': end_date,
                    'applied_rules': record.distribution_rule_id.ids,
                    'user_id': self.env.user.id,
                    'execution_rule_id': record.id,
                }
            result.append((0,0,history_vals))
            record.history_id = result


class distribution_rule_drivers(models.TransientModel):
    _name = 'distribution.rule.drivers'
    _description = 'Reglas de distribución por drivers'

    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehículo')
    trip_quantity = fields.Integer('Cantidad de viajes')
    km_quantity = fields.Integer('Km recorridos')
    process_id = fields.Integer('Id del proceso')
    contract_id = fields.Many2one('cntr.contract.encab', 'Contrato')