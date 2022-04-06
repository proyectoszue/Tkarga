from odoo import api, fields, models, SUPERUSER_ID, tools, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare
from odoo.osv import expression
from datetime import datetime, timedelta

class HrWorkEntryType(models.Model):    
    _inherit = "hr.work.entry.type"
    
    deduct_deductions = fields.Selection([('all', 'Todas las deducciones'),
                                          ('law', 'Solo las deducciones de ley')],'Tener en cuenta al descontar', default='all')    #Vacaciones

class HolidaysRequest(models.Model):    
    _inherit = "hr.leave"

    employee_identification = fields.Char('Identificación empleado')
    branch_id = fields.Many2one(related='employee_id.branch_id', string='Sucursal', store=True)
    unpaid_absences = fields.Boolean(related='holiday_status_id.unpaid_absences', string='Ausencia no remunerada',store=True)
    #Campos para vacaciones
    is_vacation = fields.Boolean(related='holiday_status_id.is_vacation', string='Es vacaciones',store=True)
    business_days = fields.Integer(string='Días habiles')
    holidays = fields.Integer(string='Días festivos')
    days_31_business = fields.Integer(string='Días 31 habiles', help='Este día no se tiene encuenta para el calculo del pago pero si afecta su historico de vacaciones.')
    days_31_holidays = fields.Integer(string='Días 31 festivos', help='Este día no se tiene encuenta para el calculo del pago ni afecta su historico de vacaciones.')
    alert_days_vacation = fields.Boolean(string='Alerta días vacaciones')
    accumulated_vacation_days = fields.Float(string='Días acumulados de vacaciones')
    #Creación de ausencia
    type_of_entity = fields.Many2one('hr.contribution.register', 'Tipo de Entidad')
    entity = fields.Many2one('hr.employee.entities', 'Entidad')
    diagnostic = fields.Many2one('hr.leave.diagnostic', 'Diagnóstico')

    @api.onchange('date_from', 'date_to', 'employee_id')
    def _onchange_leave_dates(self):
        if self.holiday_status_id.is_vacation == False:            
            if self.date_from and self.date_to:
                self.number_of_days = self._get_number_of_days(self.date_from, self.date_to, self.employee_id.id)['days']
            else:
                self.number_of_days = 0

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
            if record.holiday_status_id.is_vacation:
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


    @api.constrains('state', 'number_of_days', 'holiday_status_id')
    def _check_holidays(self):
        mapped_days = self.mapped('holiday_status_id').get_employees_days(self.mapped('employee_id').ids)
        for holiday in self:
            if holiday.holiday_type != 'employee' or not holiday.employee_id or holiday.holiday_status_id.allocation_type == 'no':
                continue
            leave_days = mapped_days[holiday.employee_id.id][holiday.holiday_status_id.id]
            if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
                continue
                # # Se comenta validación original de odoo
                # raise ValidationError(_('The number of remaining time off is not sufficient for this time off type.\n'
                #                         'Please also check the time off waiting for validation.'))

    def action_approve(self):
        #Validación adjunto
        for holiday in self:
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
                days_vacation_represent = round((days_unpaid_absences * 15) / 365,0)
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
                    final_accrual_date = date_vacation + timedelta(days=days_vacation_represent)

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

    @api.model
    def create(self, vals):
        if vals.get('employee_identification'):
            obj_employee = self.env['hr.employee'].search([('identification_id', '=', vals.get('employee_identification'))])            
            vals['employee_id'] = obj_employee.id
        if vals.get('employee_id'):
            obj_employee = self.env['hr.employee'].search([('id', '=', vals.get('employee_id'))])            
            vals['employee_identification'] = obj_employee.identification_id            
        
        res = super(HolidaysRequest, self).create(vals)
        return res

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