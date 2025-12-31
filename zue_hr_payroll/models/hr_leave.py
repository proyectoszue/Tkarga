from odoo import api, fields, models, SUPERUSER_ID, tools, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare
from odoo.osv import expression
from datetime import datetime, timedelta

class HrWorkEntryType(models.Model):    
    _inherit = "hr.work.entry.type"
    
    deduct_deductions = fields.Selection([('all', 'Todas las deducciones'),
                                          ('law', 'Solo las deducciones de ley')],'Tener en cuenta al descontar', default='all')    #Vacaciones
    not_contribution_base = fields.Boolean(string='No es base de aportes',help='Este tipo de ausencia no es base para seguridad social')
    short_name = fields.Char(string='Nombre corto/reportes')

class HolidaysRequest(models.Model):    
    _inherit = "hr.leave"

    def _add_days_360(self, start_date, days_360_to_add):
        """Suma días en convención 30/360 (cada mes tiene 30 días, día 31 se trata como 30)."""
        if not start_date or days_360_to_add <= 0:
            return start_date
        y, m, d = start_date.year, start_date.month, min(start_date.day, 30)
        total = (y * 360) + ((m - 1) * 30) + (d - 1) + days_360_to_add
        new_y, rem = total // 360, total % 360
        new_m, new_d = (rem // 30) + 1, (rem % 30) + 1
        try:
            return datetime(new_y, new_m, new_d).date()
        except ValueError:
            new_d = min(new_d, 28 if new_m == 2 else (30 if new_m in [4, 6, 9, 11] else 31))
            return datetime(new_y, new_m, new_d).date()

    employee_identification = fields.Char('Identificación empleado')
    branch_id = fields.Many2one(related='employee_id.branch_id', string='Sucursal', store=True,tracking=True)
    unpaid_absences = fields.Boolean(related='holiday_status_id.unpaid_absences', string='Ausencia no remunerada',store=True,tracking=True)
    discounting_bonus_days = fields.Boolean(related='holiday_status_id.discounting_bonus_days', string='Descontar días en prima',store=True,tracking=True)
    #Campos para vacaciones
    is_vacation = fields.Boolean(related='holiday_status_id.is_vacation', string='Es vacaciones',store=True,tracking=True)
    business_days = fields.Integer(string='Días habiles',tracking=True)
    holidays = fields.Integer(string='Días festivos',tracking=True)
    days_31_business = fields.Integer(string='Días 31 habiles', help='Este día no se tiene encuenta para el calculo del pago pero si afecta su historico de vacaciones.',tracking=True)
    days_31_holidays = fields.Integer(string='Días 31 festivos', help='Este día no se tiene encuenta para el calculo del pago ni afecta su historico de vacaciones.',tracking=True)
    alert_days_vacation = fields.Boolean(string='Alerta días vacaciones',tracking=True)
    accumulated_vacation_days = fields.Float(string='Días acumulados de vacaciones',tracking=True)
    #Creación de ausencia
    type_of_entity = fields.Many2one('hr.contribution.register', 'Tipo de Entidad',tracking=True)
    entity = fields.Many2one('hr.employee.entities', 'Entidad',tracking=True)
    diagnostic = fields.Many2one('hr.leave.diagnostic', 'Diagnóstico',tracking=True)
    radicado = fields.Char('Recobro radicado #',tracking=True)
    is_recovery = fields.Boolean('Es recobro',tracking=True)
    payroll_value = fields.Float('Valor pagado en nómina',tracking=True)
    eps_value = fields.Float('Valor pagado por la EPS',tracking=True)
    payment_date = fields.Date ('Fecha de pago',tracking=True)
    # Campos fecha real
    z_date_real_from = fields.Date('Fecha real desde',tracking=True)
    z_date_real_to = fields.Date('Fecha real hasta',tracking=True)
    z_real_number_of_days = fields.Integer('Duración real (Días)', compute='_onchange_real_leave_dates')
    z_qty_extension = fields.Integer('Prorrogas',tracking=True,default=0)
    #Prorroga
    z_leave_extension_ids = fields.One2many('zue.hr.leave.extension.wizard', 'z_leave_id', 'Prorroga')
    z_payroll_value_with_extension = fields.Float('Valor pagado en nómina con prorrogas', compute='get_values_with_extension', store=True, tracking=True)
    z_eps_value_with_extension = fields.Float('Valor pagado por la EPS  con prorrogas', compute='get_values_with_extension', store=True, tracking=True)

    @api.onchange('date_from', 'date_to', 'employee_id')
    def _onchange_leave_dates(self):
        if self.holiday_status_id.is_vacation == False:            
            if self.date_from and self.date_to:
                self.number_of_days = self._get_number_of_days(self.date_from, self.date_to, self.employee_id.id)['days']
            else:
                self.number_of_days = 0

    @api.onchange('z_date_real_from', 'z_date_real_to')
    def _onchange_real_leave_dates(self):
        for record in self:
            self.z_real_number_of_days = 0
            if record.z_date_real_to and record.z_date_real_from:
                if record.z_date_real_to < record.z_date_real_from:
                    self.z_real_number_of_days = 0
                    raise ValidationError('La fecha real desde debe ser inferior a la fecha real hasta, por favor verificar')
                # if record.z_date_real_to == False or record.z_date_real_from == False:
                #     self.z_date_real_to = datetime.now().replace(day=1, month=1, year=2000, hour=00, minute=00, second=00)
                #     self.z_date_real_from = datetime.now().replace(day=2, month=1, year=2000, hour=00, minute=00, second=00)
                else:
                    self.z_real_number_of_days = (self.z_date_real_to - self.z_date_real_from).days + 1

    @api.onchange('employee_id','holiday_status_id')
    def _onchange_info_entity(self):
        for record in self:
            if record.employee_id and record.holiday_status_id:
                record.type_of_entity = record.holiday_status_id.type_of_entity_association.id
                for entities in record.employee_id.social_security_entities:
                    if entities.contrib_id.id == record.holiday_status_id.type_of_entity_association.id:                        
                        record.entity = entities.partner_id.id
            else:
                record.type_of_entity = False
                record.entity = False
                record.diagnostic = False

    @api.onchange('number_of_days','request_date_from')
    def onchange_number_of_days_vacations(self):   
        for record in self:
            original_number_of_days = record.number_of_days
            if record.holiday_status_id.is_vacation and record.request_date_from:
                #Obtener si el dia sabado es habil | Guardar dias fines de semana 5=Sabado & 6=Domingo
                lst_days = [5,6] if record.employee_id.sabado == False else [6]
                date_to = record.request_date_from - timedelta(days=1)
                cant_days = record.number_of_days
                holidays = 0
                business_days = 0
                days_31_b = 0
                days_31_h = 0
                while cant_days > 0:
                    date_add = date_to + timedelta(days=1)
                    #Se usa el metodo weekday() que devuelve el día de la semana como un número entero donde el lunes está indexado como 0 y el domingo como 6
                    if not date_add.weekday() in lst_days:
                        #Obtener dias festivos parametrizados
                        obj_holidays = self.env['zue.holidays'].search([('date', '=', date_add)])
                        if obj_holidays:
                            holidays += 1
                            days_31_h += 1 if date_add.day == 31 else 0
                            date_to = date_add
                        else:
                            cant_days = cant_days - 1     
                            business_days += 1
                            days_31_b += 1 if date_add.day == 31 else 0
                            date_to = date_add
                    else:
                        holidays += 1
                        days_31_h += 1 if date_add.day == 31 else 0
                        date_to = date_add                    
                #Guardar calculo en el campo fecha final
                record.business_days = business_days - days_31_b
                record.holidays = holidays - days_31_h
                record.days_31_business = days_31_b
                record.days_31_holidays = days_31_h
                record.request_date_to = date_to
                days_31 = days_31_b+days_31_h
                record.number_of_days = (business_days + holidays) - days_31
                #Verficar alerta
                obj_contract = self.env['hr.contract'].search(
                    [('employee_id', '=', record.employee_id.id), ('state', '=', 'open')])
                if business_days > obj_contract.get_accumulated_vacation_days():
                    record.accumulated_vacation_days = obj_contract.get_accumulated_vacation_days()
                    record.alert_days_vacation =  True
                else:
                    record.accumulated_vacation_days = obj_contract.get_accumulated_vacation_days()
                    record.alert_days_vacation = False

    @api.constrains('business_days', 'holiday_status_id')
    def _check_business_days(self):
        if self.holiday_status_id.is_vacation == True and self.business_days == 0:
            raise ValidationError('No es posible guardar este tipo de ausencia con días hábiles en 0, por favor verificar.')

    @api.constrains('state', 'number_of_days', 'holiday_status_id')
    def _check_holidays(self):
        mapped_days = self.mapped('holiday_status_id').get_employees_days(self.mapped('employee_id').ids)
        for holiday in self:
            if holiday.holiday_type != 'employee' or not holiday.employee_id or holiday.holiday_status_id.requires_allocation == 'no':
                continue
            leave_days = mapped_days[holiday.employee_id.id][holiday.holiday_status_id.id]
            if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
                continue
                # # Se comenta validación original de odoo
                # raise ValidationError(_('The number of remaining time off is not sufficient for this time off type.\n'
                #                         'Please also check the time off waiting for validation.'))

    def action_approve(self):
        for holiday in self:
            # Validacion compañia
            if self.env.company.id != holiday.employee_id.company_id.id:
                raise ValidationError(_('El empleado ' + holiday.employee_id.name + ' esta en la compañía ' + holiday.employee_id.company_id.name + ' por lo cual no se puede aprobar debido a que se encuentra ubicado en la compañía ' + self.env.company.name + ', seleccione la compañía del empleado para aprobar la ausencia.'))
            # Validación adjunto
            if holiday.holiday_status_id.obligatory_attachment:
                attachment = self.env['ir.attachment'].search([('res_model', '=', 'hr.leave'),('res_id','=',holiday.id)])    
                if not attachment:    
                    raise ValidationError(_('Es obligatorio agregar un adjunto para la ausencia '+holiday.display_name+'.'))
        #Ejecución metodo estandar
        obj = super(HolidaysRequest, self).action_approve()
        #Creación registro en el historico de vacaciones cuando es una ausencia no remunerada
        for record in self:
            if record.unpaid_absences:
                days_unpaid_absences = record.number_of_days
                days_vacation_represent = round((days_unpaid_absences * 15) / 360,0)
                if days_vacation_represent > 0:
                    # Obtener contrato y ultimo historico de vacaciones
                    obj_contract = self.env['hr.contract'].search([('employee_id','=',record.employee_id.id),('state','=','open')])
                    date_vacation = obj_contract.date_start
                    obj_vacation = self.env['hr.vacation'].search(
                        [('employee_id', '=', record.employee_id.id), ('contract_id', '=', obj_contract.id)])
                    if obj_vacation:
                        for history in sorted(obj_vacation, key=lambda x: x.final_accrual_date):
                            date_vacation = history.final_accrual_date + timedelta(
                                days=1) if history.final_accrual_date > date_vacation else date_vacation
                    #Fechas de causación
                    initial_accrual_date = date_vacation
                    final_accrual_date = self._add_days_360(date_vacation, int(days_vacation_represent))

                    info_vacation = {
                        'employee_id': record.employee_id.id,
                        'contract_id': obj_contract.id,
                        'initial_accrual_date': initial_accrual_date,
                        'final_accrual_date': final_accrual_date,
                        'departure_date': record.request_date_from,
                        'return_date': record.request_date_to,
                        'business_units': days_vacation_represent,
                        'leave_id': record.id
                    }
                    self.env['hr.vacation'].create(info_vacation)

        return obj

    def action_refuse(self):
        obj = super(HolidaysRequest, self).action_refuse()
        for record in self:
            self.env['hr.vacation'].search([('leave_id','=',record.id)]).unlink()
        return obj

    def action_validate(self):
        # Validación adjunto
        for holiday in self:
            if holiday.holiday_status_id.obligatory_attachment:
                attachment = self.env['ir.attachment'].search([('res_model', '=', 'hr.leave'), ('res_id', '=', holiday.id)])
                if not attachment:
                    raise ValidationError(_('Es obligatorio agregar un adjunto para la ausencia ' + holiday.display_name + '.'))
        # Ejecución metodo estandar
        obj = super(HolidaysRequest, self).action_validate()
        return obj

    @api.model
    def create(self, vals):
        if vals.get('employee_identification'):
            obj_employee = self.env['hr.employee'].search([('company_id','=',self.env.company.id),('identification_id', '=', vals.get('employee_identification'))])
            vals['employee_id'] = obj_employee.id
        if vals.get('employee_id'):
            obj_employee = self.env['hr.employee'].search([('company_id', '=', self.env.company.id), ('id', '=', vals.get('employee_id'))])
            vals['employee_identification'] = obj_employee.identification_id            
        
        res = super(HolidaysRequest, self).create(vals)
        res.validate_number_of_days_child_care_license()
        return res

    def write(self, vals):
        res = super().write(vals)
        self.validate_number_of_days_child_care_license()
        return res

    def validate_number_of_days_child_care_license(self):
        for record in self:
            if not record.holiday_status_id or record.holiday_status_id.code != 'LICENCIA_CUIDADO_NIÑEZ':
                continue
            year_start = datetime(datetime.today().year, 1, 1).date()
            year_end = datetime(datetime.today().year, 12, 31).date()
            # Obtener ausencias aprobadas
            validate_leaves = self.env['hr.leave'].search([
                ('employee_id', '=', record.employee_id.id), ('holiday_status_id', '=', record.holiday_status_id.id), ('state', '=', 'validate'),
                ('request_date_from', '>=', year_start), ('request_date_to', '<=', year_end), ('id', '!=', record.id)
            ])
            accumulated_days = sum(validate_leaves.mapped('number_of_days'))
            updated_total = accumulated_days + record.number_of_days
            if updated_total > 10:
                raise ValidationError(f'El empleado ha tomado {accumulated_days} días de licencia por cuidado de la niñez. Agregar esta solicitud excedería el límite anual de 10 días.')

    def add_extension(self):
        return {
            'context': {'default_z_leave_id': self.id,
                        'default_z_date_end': self.request_date_to if self.request_date_to else False,
                        'default_z_diagnostic_original_id': self.diagnostic.id if self.diagnostic else False,
                        'default_z_diagnostic_id':self.diagnostic.id if self.diagnostic else False},
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'zue.hr.leave.extension.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.depends('z_leave_extension_ids','payroll_value','eps_value')
    def get_values_with_extension(self):
        for record in self:
            if len(record.z_leave_extension_ids) > 0:
                record.z_payroll_value_with_extension = record.payroll_value + sum([i.z_payroll_value for i in record.z_leave_extension_ids])
                record.z_eps_value_with_extension = record.eps_value + sum([i.z_eps_value for i in record.z_leave_extension_ids])
            else:
                record.z_payroll_value_with_extension = record.payroll_value
                record.z_eps_value_with_extension = record.eps_value


class hr_leave_diagnostic(models.Model):
    _name = "hr.leave.diagnostic"
    _description = "Diagnosticos Ausencias"

    name = fields.Char('Nombre', required=True)
    code = fields.Char('Código', required=True)

    _sql_constraints = [('leave_diagnostic_code_uniq', 'unique(code)',
                         'Ya existe un diagnóstico con este código, por favor verificar.')]

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "{} | {}".format(record.code,record.name)))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('code', operator, name)]
        diagnostic_interface = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return diagnostic_interface#self.browse(contract_interface_id).name_get()

class zue_hr_leave_extension_wizard(models.Model):
    _name = 'zue.hr.leave.extension.wizard'
    _description = 'Agregar prorroga en ausencias'

    z_leave_id = fields.Many2one('hr.leave',string='Ausencia',required=True)
    z_obligatory_attachment = fields.Boolean(related='z_leave_id.holiday_status_id.obligatory_attachment', string='Obliga adjunto')
    z_date_end = fields.Date(string='Fecha final original', required=True)
    z_new_date_end = fields.Date(string='Nueva fecha final',required=True)
    z_diagnostic_original_id = fields.Many2one('hr.leave.diagnostic', 'Diagnóstico Original')
    z_diagnostic_id = fields.Many2one('hr.leave.diagnostic', 'Nuevo Diagnóstico')
    z_attachment = fields.Binary(string='Adjunto')
    z_attachment_filename = fields.Char(string='Adjunto filename')
    z_radicado = fields.Char('Recobro radicado #')
    z_payroll_value = fields.Float('Valor pagado en nómina')
    z_eps_value = fields.Float('Valor pagado por la EPS')
    z_payment_date = fields.Date('Fecha de pago')

    @api.constrains("z_new_date_end", "z_leave_id", "z_attachment")
    def validate_authorized_extension(self):
        # Validar que la nueva fecha final sea mayor a la fecha final anterior
        if self.z_new_date_end <= self.z_leave_id.request_date_to:
            raise ValidationError(_('La nueva fecha de la ausencia debe ser mayor a la última fecha final.'))
        for exists_extension in self.z_leave_id.z_leave_extension_ids:
            if self.z_new_date_end <= exists_extension.z_new_date_end and self.id != exists_extension.id:
                raise ValidationError(_('La nueva fecha de la ausencia debe ser mayor a la última fecha final.'))
        # Validar si requiere adjunto
        if self.z_leave_id.holiday_status_id.obligatory_attachment and not self.z_attachment:
            raise ValidationError(_('Es obligatorio agregar un adjunto para la prórroga de la ausencia ' + self.z_leave_id.display_name + '.'))

    def authorized_extension(self):
        #Convertir ausencia en borrador para realizar la modificación
        self.z_leave_id.action_refuse()
        self.z_leave_id.action_draft()
        #Modificar ausencia original
        self.z_leave_id.write({'request_date_to':self.z_new_date_end,
                               'z_qty_extension':self.z_leave_id.z_qty_extension+1,
                               'diagnostic':self.z_diagnostic_id.id})
        #Agregar adjunto
        if self.z_attachment:
            data_attach = {'name': self.z_attachment_filename,
                           'type': 'binary', 'datas': self.z_attachment, 'res_name': self.z_attachment_filename, 'store_fname': self.z_attachment_filename,
                           'res_model': 'hr.leave', 'res_id': self.z_leave_id.id}
            atts_id = self.env['ir.attachment'].create(data_attach)
        #Confirmar y aprobar
        self.z_leave_id.action_confirm()
        if self.z_leave_id.state != 'validate':
            self.z_leave_id.action_approve()
        return True


