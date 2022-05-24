from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError
import time

class hr_type_overtime(models.Model):
    _name = 'hr.type.overtime'
    _description = 'Tipos de horas extras'

    name = fields.Char(string="Descripción", required=True)
    salary_rule = fields.Many2one('hr.salary.rule', string="Regla salarial", required=True)
    type_overtime = fields.Selection([('overtime_rn','RN | Recargo nocturno'),
                                      ('overtime_ext_d','EXT-D | Extra diurna'),
                                      ('overtime_ext_n','EXT-N | Extra nocturna'),
                                      ('overtime_eddf','E-D-D/F | Extra diurna dominical/festivo'),
                                      ('overtime_endf','E-N-D/F | Extra nocturna dominical/festivo'),
                                      ('overtime_dof','D o F | Dominicales o festivos'),
                                      ('overtime_rndf','RN-D/F | Recargo nocturno dominical/festivo'),
                                      ('overtime_rdf','R-D/F | Recargo dominical/festivo')],'Tipo',  required=True)
    percentage = fields.Float(string='Porcentaje')
    equivalence_number_ne = fields.Integer(string='Num. Equivalencia NE')

    _sql_constraints = [('change_type_uniq', 'unique(type_overtime)', 'Ya existe este tipo de hora extra, por favor verficar.')]

class hr_overtime(models.Model):
    _name = 'hr.overtime'
    _description = 'Novedades | Horas extras'
    
    branch_id = fields.Many2one('zue.res.branch', 'Sucursal',required=True)
    date = fields.Date('Fecha Novedad', required=True)
    date_end = fields.Date('Fecha Final Novedad', required=True)
    employee_id = fields.Many2one('hr.employee', string="Empleado", index=True)
    employee_identification = fields.Char('Identificación empleado')
    department_id = fields.Many2one('hr.department', related="employee_id.department_id", readonly=True,string="Departamento")
    job_id = fields.Many2one('hr.job', related="employee_id.job_id", readonly=True,string="Servicio")
    overtime_rn = fields.Float('RN', help='Recargo nocturno', default=0) # EXTRA_RECARGO
    overtime_ext_d = fields.Float('EXT-D', help='Extra diurna', default=0) # EXTRA_DIURNA
    overtime_ext_n = fields.Float('EXT-N', help='Extra nocturna', default=0) # EXTRA_NOCTURNA
    overtime_eddf = fields.Float('E-D-D/F', help='Extra diurna dominical/festivo', default=0) # EXTRA_DIURNA_DOMINICAL
    overtime_endf = fields.Float('E-N-D/F', help='Extra nocturna dominical/festivo', default=0) # EXTRA_NOCTURNA_DOMINICAL
    overtime_dof = fields.Float('D o F', help='Dominical o festivo', default=0) # DOMINICALES O FESTIVOS
    overtime_rndf = fields.Float('RN-D/F', help='Recargo nocturno dominical/festivo', default=0) # EXTRA_RECARGO_NOCTURNO_DOMINICAL_FESTIVO
    overtime_rdf = fields.Float('R-D/F', help='Recargo dominical/festivo', default=0)  # EXTRA_RECARGO_DOMINICAL_FESTIVO
    days_actually_worked = fields.Integer('Días efectivamente laborados', default=0)
    days_snack = fields.Integer('Días refrigerio', default=0)
    justification = fields.Char('Justificación')
    state = fields.Selection([('revertido','Revertido'),('procesado','Procesado'),('nuevo','Nuevo')],'Estado')
    payslip_run_id = fields.Many2one('hr.payslip','Ref. Liquidación')

    @api.model
    def create(self, vals):
        total = int(vals.get('days_snack',0)) + int(vals.get('days_actually_worked',0)) + float(vals.get('overtime_rn',0)) + float(vals.get('overtime_ext_d',0)) + float(vals.get('overtime_ext_n',0)) + float(vals.get('overtime_eddf',0)) + float(vals.get('overtime_endf',0)) + float(vals.get('overtime_dof',0)) + float(vals.get('overtime_rndf',0)) + float(vals.get('overtime_rdf',0))
        if total > 0:            
            if vals.get('employee_identification'):
                obj_employee = self.env['hr.employee'].search([('identification_id', '=', vals.get('employee_identification'))])            
                vals['employee_id'] = obj_employee.id
            if vals.get('employee_id'):
                obj_employee = self.env['hr.employee'].search([('id', '=', vals.get('employee_id'))])            
                vals['employee_identification'] = obj_employee.identification_id                            
            registrar_novedad = super(hr_overtime, self).create(vals)
            return registrar_novedad
        else:
            raise UserError(_('Valores en 0 detectados | No se ha detectado la cantidad de horas / dias de la novedad ingresada!'))       