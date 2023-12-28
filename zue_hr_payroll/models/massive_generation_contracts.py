from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError

class zue_massive_generation_contracts(models.Model):
    _name = 'zue.massive.generation.contracts'
    _description = 'Generación Masiva Contratos'

    company_id = fields.Many2one('res.company', string='Compañía', readonly=True, required=True, default=lambda self: self.env.company)
    z_employee_id = fields.Many2one('hr.employee', string='Empleado')
    z_branch_id = fields.Many2one('zue.res.branch', string='Sucursal')
    z_year = fields.Integer('Año', required=True)
    z_start_date = fields.Date('Fecha Inicio', required=True)
    z_end_date = fields.Date('Fecha Fin', required=True)
    state = fields.Selection([('draft','Borrador'),('in_process','En proceso'),('done','Hecho')], string='Estado', default='draft')
    z_executing_massive_contracts_ids = fields.One2many('zue.executing.contracts', 'z_executing_massive_contracts_id', string='Ejecución')

    # Filtros
    z_employee_type_id = fields.Selection([
        ('employee', 'Empleado'),
        ('student', 'Estudiante'),
        ('trainee', 'Aprendiz'),
        ('contractor', 'Contratista'),
        ('freelance', 'Autónomo'),
        ], string='Tipo de Empleado')
    z_department_id = fields.Many2one('hr.department', string="Departamento")

    _sql_constraints = [('generation_contracts_uniq', 'unique(company_id,z_year,z_start_date,z_end_date)',
                         'El periodo de generación de contratos ya esta registrado para esta compañía, por favor verificar.')]

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.z_branch_id.name} - {record.z_year}"
            result.append((record.id, name))
        return result

    def where_query(self):
        where_ = 'where he.active = true and hc.id is null '

        if self.z_branch_id:
            where_ += f'and he.branch_id = {self.z_branch_id.id} '
        if self.z_employee_type_id:
            where_ += f"and he.employee_type = '{self.z_employee_type_id}' "
        if self.z_department_id:
            where_ += f'and he.department_id = {self.z_department_id.id} '

        return where_

    def get_query(self):
        where = self.where_query()
        query_contract = f'''
        select distinct he.id as employee_id         
        from hr_employee he
        inner join res_company rc on he.company_id = rc.id and rc.id = {self.env.company.id} 
        left join hr_contract hc on he.contract_id = hc.id and hc.state = 'open'
        {where}
        '''
        self._cr.execute(query_contract)
        result_query = self._cr.dictfetchall()
        return result_query

    def load_employees(self):
        result_query = self.get_query()

        # Crear lineas en la grilla
        lst_contracts = []
        for query in result_query:
            try:
                vals = {
                    'z_employee_id': query.get('employee_id', 0),
                    'z_contract_id': False,
                }
                lst_contracts.append((0, 0, vals))
            except:
                raise ValidationError('Error al cargar los empleados')

        if lst_contracts:
            self.z_executing_massive_contracts_ids = lst_contracts
            self.state = 'in_process'
        else:
            raise ValidationError('No hay empleados para cargar o los empleados ya están cargados.')

    def restart_executing(self):
        # Eliminar empleados
        self.z_executing_massive_contracts_ids.unlink()
        self.state = 'draft'

    def create_contracts(self):
        for record in self.z_executing_massive_contracts_ids:
            structure = self.env['hr.payroll.structure.type'].search([('name', '=', 'General')], limit=1)
            level = self.env['hr.contract.risk'].search([('name', '=', 'NIVEL I')], limit=1)
            dict_contract = {
                'name': "{} - {}".format(record.z_employee_id.name, self.z_year),
                'employee_id': record.z_employee_id.id,
                'date_start': self.z_start_date,
                'date_end': self.z_end_date,
                'structure_type_id': structure.id,
                'department_id': record.z_employee_id.department_id.id,
                'contract_type': 'obra',
                'modality_salary': 'basico',
                'job_id': record.z_employee_id.job_id.id,
                'risk_id': level.id,
                #'hr_responsible_id': record.z_employee_id.parent_id.id or record.z_employee_id.coach_id.id or record.z_employee_id.id,
                'wage_type': 'monthly',
                'wage': 100,
            }
            obj_contract = self.env['hr.contract'].create(dict_contract)
            record.z_contract_id = obj_contract.id
            self.state = 'done'

class zue_executing_contracts(models.Model):
    _name = 'zue.executing.contracts'
    _description = 'Ejecución Masiva Contratos'

    z_executing_massive_contracts_id = fields.Many2one('zue.massive.generation.contracts', 'Ejecución masiva de contratos', required=True, ondelete='cascade')
    z_employee_id = fields.Many2one('hr.employee','Empleado')
    z_contract_id = fields.Many2one('hr.contract','Contrato')