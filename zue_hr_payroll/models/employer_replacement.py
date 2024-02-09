from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError

class zue_employer_replacement(models.Model):
    _name = 'zue.employer.replacement'
    _description = 'Sustitución patronal'
    _rec_name = 'z_employee_id'

    z_employee_id = fields.Many2one('hr.employee', 'Empleado', required=True)
    z_identification = fields.Char(related="z_employee_id.identification_id", store=True, string="Nº identificación")
    z_contract = fields.Many2one(related="z_employee_id.contract_id", store=True, string="Contrato activo")
    z_company_id = fields.Many2one(related='z_employee_id.company_id', store=True, string='Compañía actual')
    z_new_company_id = fields.Many2one('res.company', required=True, string='Compañía nueva')
    z_employer_replacement_date = fields.Date('Fecha de sustitución patronal')
    state = fields.Selection([('draft', 'Borrador'), ('done', 'Hecho')], string='Estado', default='draft')

    @api.constrains('z_new_company_id')
    def _check_company(self):
        for record in self:
            if record.z_company_id == record.z_new_company_id:
                raise ValidationError('El empleado ya se encuentra en la empresa seleccionada. Por favor verifique')
            
    def replace_employee_company(self):
        if self.z_employee_id:
            # DUPLICAR HOJA DE VIDA ASOCIADA A LA NUEVA COMPAÑÍA
            obj_employee = self.env['hr.employee'].browse(self.z_employee_id.id)
            new_cv_employee = obj_employee.with_company(self.z_new_company_id.id).copy_data()
            new_cv_employee[0]['company_id'] = self.z_new_company_id.id

            obj_new_employee = self.with_company(self.z_new_company_id.id).env['hr.employee'].create(new_cv_employee[0])
            obj_new_employee.write({'name':str(obj_new_employee.name).replace(' (copia)','')})
            # DUPLICAR EL CONTRATO ACTUAL ASOCIADO A LA NUEVA COMPAÑIA & PONER EN ESTADO EXPIRADO EL CONTRATO ACTUAL
            current_contract = self.z_employee_id.contract_id
            new_contract_employee = current_contract.with_company(self.z_new_company_id.id).copy_data()
            new_contract_employee[0]['company_id'] = self.z_new_company_id.id
            new_contract_employee[0]['employee_id'] = obj_new_employee.id
            new_contract_employee[0]['state'] = 'open'
            new_contract_employee[0]['z_employer_replacement_date'] = datetime.now()

            obj_new_contract = self.with_company(self.z_new_company_id.id).env['hr.contract'].create(new_contract_employee[0])
            obj_new_contract.write({'name': str(obj_new_contract.name).replace(' (copia)', '')})
            current_contract.write({'state':'close'})

            self.z_employer_replacement_date = datetime.now()

            # DUPLICAR LAS LIQUIDACIONES DE ULTIMO AÑO
            date_start_payslips = '01/01/'+str(datetime.now().date().year - 1)
            obj_payslips = self.env['hr.payslip'].search([('contract_id','=',current_contract.id),
                                                          ('date_from', '>=', date_start_payslips),
                                                          ('date_from','<=',datetime.now().date())])
            for payslips in obj_payslips:
                new_payslips = payslips.with_company(self.z_new_company_id.id).copy_data()
                new_payslips[0]['employee_id'] = obj_new_employee.id
                new_payslips[0]['contract_id'] = obj_new_contract.id
                new_payslips[0]['state'] = 'done'

                self.with_company(self.z_new_company_id.id).env['hr.payslip'].create(new_payslips[0])

            # DUPLICAR HISTORICOS DE CESANTIAS Y LIQUIDACIONES
            obj_history_vacations = self.env['hr.vacation'].search([('contract_id', '=', current_contract.id)])
            for hr_vacation in obj_history_vacations:
                new_hr_vacation = hr_vacation.with_company(self.z_new_company_id.id).copy_data()
                new_hr_vacation[0]['employee_id'] = obj_new_employee.id
                new_hr_vacation[0]['contract_id'] = obj_new_contract.id

                self.with_company(self.z_new_company_id.id).env['hr.vacation'].create(new_hr_vacation[0])

            obj_history_cesantias = self.env['hr.history.cesantias'].search([('contract_id','=',current_contract.id)])
            for hr_cesantia in obj_history_cesantias:
                new_hr_cesantia = hr_cesantia.with_company(self.z_new_company_id.id).copy_data()
                new_hr_cesantia[0]['employee_id'] = obj_new_employee.id
                new_hr_cesantia[0]['contract_id'] = obj_new_contract.id

                self.with_company(self.z_new_company_id.id).env['hr.history.cesantias'].create(new_hr_cesantia[0])

            self.state = 'done'

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise ValidationError(_('No se puede eliminar la sustitución patronal debido a que su estado es diferente de borrador.'))
        return super(zue_employer_replacement, self).unlink()