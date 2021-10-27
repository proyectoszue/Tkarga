from odoo import api, fields, models, SUPERUSER_ID, tools, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare
from odoo.osv import expression

from datetime import datetime, timedelta

class HrWorkEntryType(models.Model):    
    _inherit = "hr.work.entry.type"
    
    deduct_deductions = fields.Selection([('all', 'Todas las deducciones'),
                                          ('law', 'Solo las deducciones de ley')],'Tener en cuenta al descontar', default='all')    #Vacaciones


class HrWorkEntry(models.Model):
    _inherit = 'hr.work.entry'

    @api.model
    def _mark_conflicting_work_entries(self, start, stop):
        """
        Set `state` to `conflict` for overlapping work entries
        between two dates.
        Return True if overlapping work entries were detected.
        """
        # Use the postgresql range type `tsrange` which is a range of timestamp
        # It supports the intersection operator (&&) useful to detect overlap.
        # use '()' to exlude the lower and upper bounds of the range.
        # Filter on date_start and date_stop (both indexed) in the EXISTS clause to
        # limit the resulting set size and fasten the query.
        branchs_ids = str(self.env.user.branch_ids.ids)
        branchs_ids = branchs_ids.replace('[','')
        branchs_ids = branchs_ids.replace(']','')
        self.flush(['date_start', 'date_stop', 'employee_id', 'active'])
        query = """
            SELECT b1.id
            FROM hr_work_entry b1
            Inner Join hr_employee he on b1.employee_id = he.id 
            Left Join zue_res_branch zrb on he.branch_id = zrb.id
            WHERE
            b1.date_start <= %s
            AND b1.date_stop >= %s
            AND b1.active = TRUE
            AND EXISTS (
                SELECT 1
                FROM hr_work_entry b2
                WHERE
                    b2.date_start <= %s
                    AND b2.date_stop >= %s
                    AND b2.active = TRUE
                    AND tsrange(b1.date_start, b1.date_stop, '()') && tsrange(b2.date_start, b2.date_stop, '()')
                    AND b1.id <> b2.id
                    AND b1.employee_id = b2.employee_id
            )
            AND (zrb.id is null or zrb.id in ("""+branchs_ids+"""));
        """
        self.env.cr.execute(query, (stop, start, stop, start))
        conflicts = [res.get('id') for res in self.env.cr.dictfetchall()]

        #Quitando confilctos de vacaciones
        conflicts_really = []
        conflicts_vactions = []
        for i in conflicts:
            obj_work_entry = self.env['hr.work.entry'].search([('id', '=', i)])    
            if obj_work_entry:
                if obj_work_entry.leave_id.is_vacation:
                    conflicts_vactions.append(i)
                else:
                    conflicts_really.append(i)

        self.browse(conflicts_really).write({
            'state': 'conflict',
        })

        self.browse(conflicts_vactions).write({
            'state': 'validated',
        })
        return bool(conflicts)

    def write(self, vals):
        for record in self:
            if record.leave_id.is_vacation == False: 
                skip_check = not bool({'date_start', 'date_stop', 'employee_id', 'work_entry_type_id', 'active'} & vals.keys())
                if 'state' in vals:
                    if vals['state'] == 'draft':
                        vals['active'] = True
                    elif vals['state'] == 'cancelled':
                        vals['active'] = False
                        skip_check &= all(self.mapped(lambda w: w.state != 'conflict'))

                if 'active' in vals:
                    vals['state'] = 'draft' if vals['active'] else 'cancelled'

                with self._error_checking(skip=skip_check):
                    return super(HrWorkEntry, self).write(vals)
            else:
                return super(HrWorkEntry, self).write(vals)
    
class HolidaysRequest(models.Model):    
    _inherit = "hr.leave"

    employee_identification = fields.Char('Identificación empleado')
    branch_id = fields.Many2one(related='employee_id.branch_id', string='Sucursal', store=True)
    unpaid_absences = fields.Boolean(related='holiday_status_id.unpaid_absences', string='Ausencia no remunerada',store=True)
    #Campos para vacaciones
    is_vacation = fields.Boolean(related='holiday_status_id.is_vacation', string='Es vacaciones',store=True)
    business_days = fields.Integer(string='Días habiles')
    holidays = fields.Integer(string='Días festivos')
    
    @api.onchange('date_from', 'date_to', 'employee_id')
    def _onchange_leave_dates(self):
        if self.holiday_status_id.is_vacation == False:            
            if self.date_from and self.date_to:
                self.number_of_days = self._get_number_of_days(self.date_from, self.date_to, self.employee_id.id)['days']
            else:
                self.number_of_days = 0

    @api.onchange('number_of_days','request_date_from')
    def onchange_number_of_days_vacations(self):   
        for record in self:
            original_number_of_days = record.number_of_days
            if record.holiday_status_id.is_vacation and record.holiday_status_id.type_vacation == 'time':
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
                record.request_date_to = date_to
                days_31 = days_31_b+days_31_h
                record.number_of_days = (business_days + holidays) - days_31
            if record.holiday_status_id.is_vacation and record.holiday_status_id.type_vacation == 'money':
                date_to = record.request_date_from - timedelta(days=1)
                cant_days = record.number_of_days
                days = 0
                days_31 = 0
                while cant_days > 0:
                    date_add = date_to + timedelta(days=1)
                    cant_days = cant_days - 1     
                    days += 1 
                    days_31 += 1 if date_add.day == 31 else 0               
                    date_to = date_add
                
                record.request_date_to = date_to
                record.number_of_days = days - days_31

                #record.request_date_to = record.request_date_from + timedelta(days=record.number_of_days-1)
                #record.number_of_days = original_number_of_days


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
        for holiday in self:
            if holiday.holiday_status_id.obligatory_attachment:
                attachment = self.env['ir.attachment'].search([('res_model', '=', 'hr.leave'),('res_id','=',holiday.id)])    
                if not attachment:    
                    raise ValidationError(_('Es obligatorio agregar un adjunto para la ausencia '+holiday.display_name+'.'))
        return super(HolidaysRequest, self).action_approve()    


    @api.constrains('date_from', 'date_to', 'state', 'employee_id')
    def _check_date(self):
        if self.holiday_status_id.is_vacation and self.holiday_status_id.type_vacation == 'money':
            pass
        else:
            domains = [[
                ('date_from', '<', holiday.date_to),
                ('date_to', '>', holiday.date_from),
                ('employee_id', '=', holiday.employee_id.id),
                ('holiday_status_id.type_vacation', '!=', 'money'),
                ('id', '!=', holiday.id),
            ] for holiday in self.filtered('employee_id')]
            domain = expression.AND([
                [('state', 'not in', ['cancel', 'refuse'])],
                expression.OR(domains)
            ])
            if self.search_count(domain):
                raise ValidationError(_('You can not set 2 times off that overlaps on the same day for the same employee.'))

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
