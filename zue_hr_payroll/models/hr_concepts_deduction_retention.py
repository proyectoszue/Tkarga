from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval
from .browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips

class hr_type_tax_retention(models.Model):
    _name = 'hr.type.tax.retention'
    _description = 'Tipos impuestos'
    
    code = fields.Char('Identificador', required=True)
    name = fields.Char('Descripción', required=True)

    _sql_constraints = [('change_code_uniq', 'unique(code)', 'Ya existe este tipo de impuesto, por favor verficar.')]

class hr_concepts_deduction_retention(models.Model):
    _name = 'hr.concepts.deduction.retention'
    _description = 'Conceptos de deducción retención'
    _order = 'type_tax,order,code,name'
    
    code = fields.Char('Código', required=True)
    name = fields.Char('Descripción', required=True)
    order = fields.Integer('Orden', required=True)
    type_tax = fields.Many2one('hr.type.tax.retention',string='Tipo de impuesto', required=True)
    percentage = fields.Float('Porcentaje')
    base = fields.Text('Base')
    calculation = fields.Text('Cálculo')
    #validation = fields.Text('Validación')
    
    _sql_constraints = [('change_type_tax_code_uniq', 'unique(type_tax,code)', 'Ya existe este concepto de deducción retención para este tipo de impuesto, por favor verficar.')]


    def _exec_python_code_base(self, localdict):
        try:
            safe_eval(self.base, localdict, mode='exec', nocopy=True)
            return localdict.get('result', 0.0)
        except:
            raise UserError(_('Error al ejecutar el código python del campo Base para el concepto de deducción %s (%s).') % (self.name, self.code))

    def _exec_python_code_calculation(self, localdict):
        try:
            safe_eval(self.calculation, localdict, mode='exec', nocopy=True)
            return localdict.get('result', 0.0)
        except:
            raise UserError(_('Error al ejecutar el código python del campo Cálculo para el concepto de deducción %s (%s).') % (self.name, self.code))

    def _loop_python_code(self,localdict,encab_id):
        payslip = localdict['payslip']
        employee = localdict['employee']
        contract = localdict['contract'] 

        #Detalle
        for rule in self:            
            localdict.update({
                'result': 0.0})

            data = {
                    'encab_id': encab_id,
                    'employee_id': employee.id,
                    'contract_id': contract.id,
                    'concept_deduction_id': rule.id,
                    'year': payslip.date_to.year,
                    'month': payslip.date_to.month,
                    'result_base': 0,
                    'result_calculation': 0                    
                } 
            if self._exec_python_code_base(localdict):
                data.update({
                    'result_base': localdict['result']                    
                })
            if self._exec_python_code_calculation(localdict):
                data.update({
                    'result_calculation': localdict['result']                    
                })
            
            #Guardar en tabla de resultados
            self.env['hr.employee.deduction.retention'].create(data)

class hr_employee_deduction_retention(models.Model):
    _name = 'hr.employee.deduction.retention'
    _description = 'Traza Empleado - Conceptos de deducción retención'

    encab_id = fields.Many2one('hr.employee.rtefte',string='RteFte', required=True)
    employee_id = fields.Many2one('hr.employee',string='Empleado', required=True)
    contract_id = fields.Many2one('hr.contract',string='Contrato', required=True)
    concept_deduction_id = fields.Many2one('hr.concepts.deduction.retention',string='Regla deducción tributaria', required=True)
    concept_deduction_code = fields.Char(related='concept_deduction_id.code', string='Código',store=True, readonly=True)
    concept_deduction_order = fields.Integer(related='concept_deduction_id.order', string='Orden',store=True, readonly=True)
    year = fields.Integer('Año',required=True)
    month = fields.Integer('Mes',required=True)
    result_base = fields.Float('Valor Base')
    result_calculation = fields.Float('Valor cálculo')
    #result_validation = fields.Float('Valor validación')

class hr_employee_rtefte(models.Model):
    _name = 'hr.employee.rtefte'
    _description = 'RteFte Cálculada Empleado'

    employee_id = fields.Many2one('hr.employee',string='Empleado', required=True, readonly=True)
    year = fields.Integer('Año',required=True, readonly=True)
    month = fields.Integer('Mes',required=True, readonly=True)
    type_tax = fields.Many2one('hr.type.tax.retention','Tipo de retención', readonly=True)
    deduction_retention = fields.One2many('hr.employee.deduction.retention', 'encab_id' , 'RteFte', readonly=True)

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "VER DETALLE"))
        return result

class hr_employee_rtefte_history(models.Model):
    _name = 'hr.employee.rtefte.history'
    _description = 'Histórico RteFte'

    z_employee_id = fields.Many2one('hr.employee', string='Empleado')
    z_year = fields.Integer(string='Año')
    z_month = fields.Integer(string='Mes')
    z_payslip_id = fields.Many2one('hr.payslip', string='Liquidación origen', ondelete='set null')
    z_line_ids = fields.One2many('hr.employee.deduction.retention.history', 'z_history_id', string='Retención en la fuente')

class hr_employee_deduction_retention_history(models.Model):
    _name = 'hr.employee.deduction.retention.history'
    _description = 'Histórico conceptos deducción retención'
    _order = 'z_concept_deduction_order asc'

    z_history_id = fields.Many2one('hr.employee.rtefte.history', string='RteFte', ondelete='cascade')
    z_concept_deduction_id = fields.Many2one('hr.concepts.deduction.retention', string='Regla deducción tributaria')
    z_concept_deduction_code = fields.Char(related='z_concept_deduction_id.code', string='Código', store=True)
    z_concept_deduction_order = fields.Integer(related='z_concept_deduction_id.order', string='Orden', store=True)
    z_result_base = fields.Float(string='Valor Base')
    z_result_calculation = fields.Float(string='Valor cálculo')

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # Metodo para guardar histórico de RteFte de la liquidación actual
    def _create_rtefte_history(self, employee):
        history = self.env['hr.employee.rtefte.history']
        history_line = self.env['hr.employee.deduction.retention.history']
        for record in self:
            # Crear histórico de liquidación actual si tiene RteFte
            current_rte = None
            if record.rtefte_id:
                current_rte = record.rtefte_id
            else:
                # Si no está asignado, buscar registros RteFte del período actual
                current_rte = self.env['hr.employee.rtefte'].search([
                    ('employee_id', '=', employee.id), ('year', '=', record.date_to.year),
                    ('month', '=', record.date_to.month)], limit=1)

            if current_rte:
                # Usar el período de la liquidación actual (no el del RteFte encontrado)
                payslip_year = record.date_to.year
                payslip_month = record.date_to.month

                # Verificar si ya existe histórico para esta liquidación específica
                # Esto evita duplicados al recalcular la misma liquidación
                existing_historical_current = history.search([('z_payslip_id', '=', record.id)])
                if existing_historical_current:
                    existing_historical_current.unlink()

                # Eliminar históricos huérfanos (sin z_payslip_id) del mismo empleado, año y mes
                # Esto ocurre cuando se eliminó una liquidación pero quedó su histórico
                existing_historical_orphan = history.search([
                    ('z_employee_id', '=', employee.id),
                    ('z_year', '=', payslip_year),
                    ('z_month', '=', payslip_month),
                    ('z_payslip_id', '=', False)
                ])
                if existing_historical_orphan:
                    existing_historical_orphan.unlink()

                # Encabezado
                history_record_current = history.create({
                    'z_employee_id': employee.id,
                    'z_year': payslip_year,
                    'z_month': payslip_month,
                    'z_payslip_id': record.id,
                })
                # Detalle
                line_vals_current = []
                for line in current_rte.deduction_retention:
                    line_vals_current.append({
                        'z_history_id': history_record_current.id,
                        'z_concept_deduction_id': line.concept_deduction_id.id,
                        'z_result_base': line.result_base,
                        'z_result_calculation': line.result_calculation,
                    })
                if line_vals_current:
                    history_line.create(line_vals_current)