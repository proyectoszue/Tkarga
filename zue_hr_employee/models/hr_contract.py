# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from pytz import timezone
import time
import base64

class hr_contract_change_wage(models.Model):
    _name = 'hr.contract.change.wage'
    _description = 'Cambios salario basico'    
    _order = 'date_start'

    date_start = fields.Date('Fecha inicial')
    wage = fields.Float('Salario basico', help='Seguimento de los cambios en el salario basico')
    contract_id = fields.Many2one('hr.contract', 'Contrato', required=True, ondelete='cascade')

    _sql_constraints = [('change_wage_uniq', 'unique(contract_id, date_start, wage)', 'Ya existe un cambio de salario igual a este')]

    #@api.constrains('date_start')
    #def _check_date_start(self):
    #    for record in self:
    #        if record.date_start > datetime.now(timezone(self.env.user.tz)).date():
    #            raise UserError(_('La fecha inicial del salario no puede ser mayor que la fecha actual, por favor verificar.'))

#Conceptos de nomina
class hr_contract_concepts(models.Model):
    _name = 'hr.contract.concepts'
    _description = 'Deducciones o Devengos, conceptos de nómina'

    type_employee = fields.Many2one('hr.types.employee',string='Tipo de Empleado', store=True,readonly=True)
    input_id = fields.Many2one('hr.salary.rule', 'Regla', required=True, help='Regla salarial', domain="[('types_employee','in',[type_employee])]", track_visibility='onchange')
    show_voucher = fields.Boolean('Mostrar', help='Indica si se muestra o no en el comprobante de nomina')
    type_deduction = fields.Selection([('P', 'Prestamo empresa'),
                             ('A', 'Ahorro'),
                             ('S', 'Seguro'),
                             ('L', 'Libranza'),
                             ('E', 'Embargo'),
                             ('R', 'Retencion'),
                             ('O', 'Otros')], 'Tipo deduccion')
    period = fields.Selection([('limited', 'Limitado'), ('indefinite', 'Indefinido')], 'Periodo', required=True, track_visibility='onchange')
    amount = fields.Float('Valor', help='Valor de la cuota o porcentaje segun formula de la regla salarial', required=True, track_visibility='onchange')
    
    aplicar = fields.Selection([('15','Primera quincena'),
                                ('30','Segunda quincena'),
                                ('0','Siempre')],'Aplicar cobro',  required=True, help='Indica a que quincena se va a aplicar la deduccion', track_visibility='onchange')
    date_start = fields.Date('Fecha Inicial', track_visibility='onchange')
    date_end = fields.Date('Fecha Final')
    partner_id = fields.Many2one('hr.employee.entities', 'Entidad', track_visibility='onchange')
    contract_id = fields.Many2one('hr.contract', 'Contrato', required=True, ondelete='cascade')
    detail = fields.Text('Notas', help='Notas')
    embargo_judged = fields.Char('Juzgado')
    embargo_process = fields.Char('Proceso')
    
    attached = fields.Binary('Adjunto')
    attached_name = fields.Char('Nombre adjunto')

    state = fields.Selection([('draft', 'Por Aprobar'),
                              ('done', 'Aprobado'),
                              ('cancel', 'Cancelado / Finalizado')], string='Estado', default='draft', required=True, track_visibility='onchange')
    
    def change_state_draft(self):
        self.state = 'draft'
        # self.write({'state':'draft'})

    def change_state_done(self):
        self.state = 'done'        

    def change_state_cancel(self):
        self.state = 'cancel'

class hr_contractual_modifications(models.Model):
    _name = 'hr.contractual.modifications'
    _description = 'Modificaciones contractuales'

    contract_id = fields.Many2one('hr.contract', 'Contrato', required=True, ondelete='cascade')
    date = fields.Date('Fecha', required=True)
    description = fields.Char('Descripción de modificacion contractual', required=True)
    attached = fields.Many2one('documents.document', string='Adjunto')

#Deducciones para retención en la fuente
class hr_contract_deductions_rtf(models.Model):
    _name = 'hr.contract.deductions.rtf'
    _description = 'Reglas salariales para retención en la fuente'

    input_id = fields.Many2one('hr.salary.rule', 'Regla', required=True, help='Regla salarial', domain="[('type_concept','=','tributaria')]")
    date_start = fields.Date('Fecha Inicial')
    date_end = fields.Date('Fecha Final')
    number_months = fields.Integer('N° Meses')
    value_total = fields.Float('Valor Total')
    value_monthly = fields.Float('Valor Mensualizado')
    contract_id = fields.Many2one('hr.contract', 'Contrato', required=True, ondelete='cascade')

    #Validaciones
    @api.onchange('value_total')
    def _onchange_value_total(self):
        for record in self:
            if record.value_total > 0:
                if not record.date_start:
                    raise UserError(_('No se ha especificado la fecha inicial.'))        
                if not record.date_end:
                    raise UserError(_('No se ha especificado la fecha final'))   

                nSecondDif = (record.date_end - record.date_start).total_seconds()
                nMinutesDif = round(nSecondDif/60,0)
                nHoursDif = round(nMinutesDif/60,0)
                nDaysDif = round(nHoursDif/24,0)
                nMonthsDif = round(nDaysDif/30,0)

                if nMonthsDif != 0:
                    if record.number_months>0:
                        self.value_monthly = record.value_total / record.number_months
                    else:
                        self.value_monthly = record.value_total / 12
                else:    
                    raise UserError(_('La fecha inicial es mayor que la fecha final, por favor verificar.'))       

    @api.onchange('value_monthly')
    def _onchange_value_monthly(self):
        for record in self:
            if record.value_monthly > 0:
                if not record.date_start:
                    raise UserError(_('No se ha especificado la fecha inicial.'))        
                if not record.date_end:
                    raise UserError(_('No se ha especificado la fecha final'))   

                nSecondDif = (record.date_end - record.date_start).total_seconds()
                nMinutesDif = round(nSecondDif/60,0)
                nHoursDif = round(nMinutesDif/60,0)
                nDaysDif = round(nHoursDif/24,0)
                nMonthsDif = round(nDaysDif/30,0)

                if nMonthsDif != 0:
                    if record.number_months>0:
                        self.value_total = record.value_monthly * record.number_months
                    else:
                        self.value_total = record.value_monthly * 12
                else:    
                    raise UserError(_('La fecha inicial es mayor que la fecha final, por favor verificar.'))    

    _sql_constraints = [('change_deductionsrtf_uniq', 'unique(input_id, contract_id)', 'Ya existe esta deducción para este contrato, por favor verficar.')]

class hr_type_of_jurisdiction(models.Model):
    _name = 'hr.type.of.jurisdiction'
    _description = 'Tipo de Fuero'

    name = fields.Char('Tipo de Fuero')

    _sql_constraints = [('type_of_jurisdiction_uniq', 'unique(name)',
                         'Ya existe este tipo de fuero, por favor verificar.')]

class hr_employee_endowment(models.Model):
    _name = 'hr.employee.endowment'
    _description = 'Dotación'

    contract_id = fields.Many2one('hr.contract', 'Contrato', required=True, ondelete='cascade')
    date = fields.Date('Fecha de Entrega')
    supplies = fields.Char('Descripción - Periodo de entrega')
    # quantity = fields.Integer('Cantidad')
    # initial_date = fields.Date('Fecha Inicial')
    # final_date = fields.Date('Fecha Final')
    attached = fields.Many2one('documents.document', string='Adjunto')

#Contratos
class hr_contract(models.Model):
    _inherit = 'hr.contract'
    
    @api.model
    def _get_default_deductions_rtf_ids(self):
        salary_rules_rtf = self.env['hr.salary.rule'].search([('type_concept', '=', 'tributaria')])
        data = []
        for rule in salary_rules_rtf:
            info = (0,0,{'input_id':rule.id})
            data.append(info)

        return data
    
    analytic_account_id = fields.Many2one(track_visibility='onchange')
    job_id = fields.Many2one(track_visibility='onchange')
    company_id = fields.Many2one(track_visibility='onchange')
    sequence = fields.Char(string="Secuencia", default="/", readonly=True)
    retirement_date = fields.Date('Fecha retiro')
    change_wage_ids = fields.One2many('hr.contract.change.wage', 'contract_id', 'Cambios salario')
    concepts_ids = fields.One2many('hr.contract.concepts', 'contract_id', 'Devengos & Deducciones')
    contract_modification_history = fields.One2many('hr.contractual.modifications', 'contract_id','Modificaciones contractuales')
    deductions_rtf_ids = fields.One2many('hr.contract.deductions.rtf', 'contract_id', 'Deducciones retención en la fuente', default=_get_default_deductions_rtf_ids, track_visibility='onchange')
    risk_id = fields.Many2one('hr.contract.risk', string='Riesgo profesional', track_visibility='onchange')
    contract_type = fields.Selection([('obra', 'Contrato por Obra o Labor'), 
                                      ('fijo', 'Contrato de Trabajo a Término Fijo'),
                                      ('fijo_parcial', 'Contrato de Trabajo a Término Fijo Tiempo Parcial'),
                                      ('indefinido', 'Contrato de Trabajo a Término Indefinido'),
                                      ('aprendizaje', 'Contrato de Aprendizaje'), 
                                      ('temporal', 'Contrato Temporal, ocasional o accidental')], 'Tipo de Contrato',required=True, default='obra', track_visibility='onchange')
    modality_salary = fields.Selection([('basico', 'Básico'), 
                                      ('sostenimiento', 'Cuota de sostenimiento'), 
                                      ('integral', 'Integral'),
                                      ('especie', 'En especie'), 
                                      ('variable', 'Variable')], 'Modalidad de salario', required=True, default='basico', track_visibility='onchange')
    code_sena = fields.Char('Código SENA')                                
    view_inherit_employee = fields.Boolean('Viene de empleado')    
    type_employee = fields.Many2one(string='Tipo de empleado', store=True, readonly=True, related='employee_id.type_employee')
    not_validate_top_auxtransportation = fields.Boolean(string='No validar tope de auxilio de transporte', track_visibility='onchange')
    info_project = fields.Char(related='employee_id.info_project', store=True)
    branch_id = fields.Many2one(related='employee_id.branch_id', store=True)
    emp_work_address_id = fields.Many2one(related='employee_id.address_id',string="Ubicación laboral", store=True)
    emp_identification_id = fields.Char(related='employee_id.identification_id',string="Número de identificación", store=True)
    # date_prima = fields.Date('Fecha de liquidación de prima')
    # date_cesantias = fields.Date('Fecha de liquidación de cesantías')
    # date_vacaciones = fields.Date('Fecha de liquidación de vacaciones')
    # date_liquidacion = fields.Date('Fecha de liquidación contrato')
    # distribuir = fields.Boolean('Distribuir por cuenta analítica', help='Indica si al calcula la nómina del contrato se distribuye por centro de costo')
    factor = fields.Float('Factor salarial')
    parcial = fields.Boolean('Tiempo parcial')
    pensionado = fields.Boolean('Pensionado')
    # condicion = fields.Float('Condición anterior', digits_compute=dp.get_precision('Payroll'))
    # compensacion = fields.Float('Compensación', digits_compute=dp.get_precision('Payroll'))
    date_to = fields.Date('Finalización contrato fijo')
    #work_place = fields.Many2one('res.partner', string='Work Place', domain="[('is_work_place','=',True)]")
    sena_code = fields.Char('SENA code')
    #branch_id = fields.Many2one('zue.res.branch', string='Sucursal', related='analytic_account_id.branch_id', readonly=True)
    retention_procedure = fields.Selection([('100', 'Procedimiento 1'),
                                            ('102', 'Procedimiento 2'),
                                            ('fixed', 'Valor fijo')], 'Procedimiento retención', default='100', track_visibility='onchange')
    fixed_value_retention_procedure = fields.Float('Valor fijo retención')
    #Pestaña Fuero
    type_of_jurisdiction = fields.Many2one('hr.type.of.jurisdiction', string ='Tipo de Fuero')                             
    date_i = fields.Date('Fecha Inicial')
    date_f = fields.Date('Fecha Final')
    relocated = fields.Char('Reubicados')
    previous_positions = fields.Char('Cargo anterior')
    new_positions = fields.Char('Cargo nuevo')
    time_with_the_state = fields.Char('Tiempo que lleva con el estado')
    #Pestaña de dotacion
    employee_endowment_ids = fields.One2many('hr.employee.endowment', 'contract_id', 'Dotación')
    


    # @api.constrains('state')
    # def _check_states_contract(self):  
    #     for record in self:
    #         cant_contracts_process = 1 if record.state == 'open' else 0
    #         obj_contracts = self.env['hr.contract'].search([('employee_id','=',record.employee_id.id),('id','!=',record.id)]) 
    #         for contract in obj_contracts:
    #             cant_contracts_process = cant_contracts_process + 1 if contract.state == 'open' else cant_contracts_process
    #         if cant_contracts_process > 1:
    #             raise UserError(_('El empleado ya tiene un contrato En Proceso, por favor verificar.'))              

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "{} | {}".format(record.sequence,record.name)))
        return result

    def action_state_open(self):
        self.write({'state':'open'})

    # def action_state_close(self):
    #     self.write({'state':'close'})

    def action_state_cancel(self):
        self.write({'state':'cancel'})

    @api.depends('change_wage_ids')
    @api.onchange('change_wage_ids')
    def change_wage(self):
        for record in self:
            for change in sorted(record.change_wage_ids, key=lambda x: x.date_start):
                record.wage = change.wage

    @api.model
    def create(self, vals):
        vals['sequence'] = self.env['ir.sequence'].get('hr.contract.seq') or ' '
        obj_contract = super(hr_contract, self).create(vals)
        return obj_contract

    #Verificar historico de salario
    def get_wage_in_date(self,process_date):
        wage_in_date = self.wage
        for change in sorted(self.change_wage_ids, key=lambda x: x.date_start):
            if process_date >= change.date_start:
                wage_in_date = change.wage
        return wage_in_date

    #Metodos para el reporte de certificado laboral

    def generate_labor_certificate(self):
        ctx = self.env.context.copy()
        ctx.update({'default_contract_id': self.id, 'default_date_generation': fields.Date.today()})

        return {
            'type': 'ir.actions.act_window',
            'name': 'Certificado laboral',
            'res_model': 'hr.labor.certificate.history',
            'domain': [],
            'view_mode': 'form',
            'target':'new',
            'context': ctx
        }

    def get_contract_type(self):
        if self.contract_type:
            model_type = dict(self._fields['contract_type'].selection).get(self.contract_type)
            return model_type.upper()
        else:
            return ''

    def get_date_text(self,date,calculated_week=0):
        #Mes
        month = ''
        month = 'Enero' if date.month == 1 else month
        month = 'Febrero' if date.month == 2 else month
        month = 'Marzo' if date.month == 3 else month
        month = 'Abril' if date.month == 4 else month
        month = 'Mayo' if date.month == 5 else month
        month = 'Junio' if date.month == 6 else month
        month = 'Julio' if date.month == 7 else month
        month = 'Agosto' if date.month == 8 else month
        month = 'Septiembre' if date.month == 9 else month
        month = 'Octubre' if date.month == 10 else month
        month = 'Noviembre' if date.month == 11 else month
        month = 'Diciembre' if date.month == 12 else month
        #Dia de la semana
        week = ''
        week = 'Lunes' if date.weekday() == 0 else week
        week = 'Martes' if date.weekday() == 1 else week
        week = 'Miercoles' if date.weekday() == 2 else week
        week = 'Jueves' if date.weekday() == 3 else week
        week = 'Viernes' if date.weekday() == 4 else week
        week = 'Sábado' if date.weekday() == 5 else week
        week = 'Domingo' if date.weekday() == 6 else week
        
        if calculated_week == 0:
            date_text = date.strftime('%d de '+month+' del %Y')
        else:
            date_text = date.strftime(week+', %d de '+month+' del %Y')

        return date_text

    def get_amount_text(self, valor):
        letter_amount = self.numero_to_letras(float(valor))         
        return letter_amount.upper()

    def get_average_concept_heyrec(self): #Promedio horas extra
        promedio = False
        model_payslip = self.env['hr.payslip']
        model_payslip_line = self.env['hr.payslip.line']
        today = datetime.today()
        date_start =  today + relativedelta(months=-3)
        today_str = today.strftime("%Y-%m-01")
        date_start_str = date_start.strftime("%Y-%m-01")
        slips_ids = model_payslip.search([('date_from','>=',date_start_str),('date_to','<=',today_str),('contract_id','=',self.id),('state','=','done')])
        lines_ids = model_payslip_line.search([('slip_id','in',slips_ids.ids),('category_id.code','=','HEYREC')])
        if lines_ids:
            total = sum([i.total for i in model_payslip_line.browse(lines_ids.ids)])
            if len(slips_ids)/2 > 0:
                promedio = total/(len(slips_ids)/2)                            
        return promedio

    def get_average_concept_certificate(self,salary_rule_id,last,average): #Promedio horas extra
        model_payslip = self.env['hr.payslip']
        model_payslip_line = self.env['hr.payslip.line']
        today = datetime.today()
        if last == True:
            total = False
            date_start = today + relativedelta(months=-1)
            today_str = today.strftime("%Y-%m-01")
            date_start_str = date_start.strftime("%Y-%m-01")
            slips_ids = model_payslip.search([('date_from','>=',date_start_str),('date_to','<=',today_str), ('contract_id', '=', self.id),('state', '=', 'done')])
            lines_ids = model_payslip_line.search([('slip_id', 'in', slips_ids.ids), ('salary_rule_id', '=', salary_rule_id.id)])
            if lines_ids:
                total = sum([i.total for i in model_payslip_line.browse(lines_ids.ids)])
            return total
        if average == True:
            promedio = False
            date_start =  today + relativedelta(months=-3)
            today_str = today.strftime("%Y-%m-01")
            date_start_str = date_start.strftime("%Y-%m-01")
            slips_ids = model_payslip.search([('date_from','>=',date_start_str),('date_to','<=',today_str),('contract_id','=',self.id),('state','=','done')])
            lines_ids = model_payslip_line.search([('slip_id','in',slips_ids.ids),('salary_rule_id','=',salary_rule_id.id)])
            if lines_ids:
                total = sum([i.total for i in model_payslip_line.browse(lines_ids.ids)])
                if len(slips_ids)/2 > 0:
                    promedio = total/(len(slips_ids)/2)
            return promedio

    def get_signature_certification(self):
        res = {'nombre':'NO AUTORIZADO', 'cargo':'NO AUTORIZADO','firma':''}
        obj_user = self.env['res.users'].search([('signature_certification_laboral','=',True)])
        for user in obj_user:
            res['nombre'] = user.name
            res['cargo'] = 'Dirección Nacional de Talento Humano'
            res['firma'] = user.signature_documents

        return res
        
#Historico generación de certificados laborales
class hr_labor_certificate_history(models.Model):
    _name = 'hr.labor.certificate.history'
    _description = 'Historico de certificados laborales generados'
    _order = 'contract_id,date_generation'

    contract_id = fields.Many2one('hr.contract', 'Contrato', required=True, ondelete='cascade')
    sequence = fields.Char(string="Secuencia", default="/", readonly=True)
    date_generation = fields.Date('Fecha generación', required=True)
    info_to = fields.Char(string='Dirigido a', required=True)
    pdf = fields.Binary(string='Certificado')
    pdf_name = fields.Char(string='Filename Certificado')

    _sql_constraints = [
        ('labor_certificate_history_uniq', 'unique(contract_id, sequence)', 'Ya existe un certificado con esta secuencia, por favor verificar.')]

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "Certificado {} de {}".format(record.sequence,record.contract_id.name)))
        return result

    def get_hr_labor_certificate_template(self):
        obj = self.env['hr.labor.certificate.template'].search([('company_id','=',self.contract_id.employee_id.company_id.id)])
        if len(obj) == 0:
            raise ValidationError(_('No tiene configurada plantilla de certificado laboral. Por favor verifique!'))
        return obj

    @api.model
    def create(self, vals):
        vals['sequence'] = self.env['ir.sequence'].get('hr.labor.certificate.history.seq') or ' '
        obj_contract = super(hr_labor_certificate_history, self).create(vals)
        return obj_contract

    def generate_report(self):
        datas = {
            'ids': self.contract_id.ids,
            'model': 'hr.labor.certificate.history'
        }

        report_name = 'zue_hr_employee.report_certificacion_laboral'
        pdf = self.env.ref('zue_hr_employee.report_certificacion_laboral_action',False).render_qweb_pdf(self.id)[0]
        pdf = base64.b64encode(pdf)
        self.pdf = base64.encodestring(pdf)
        self.pdf_name = f'Certificado - {self.contract_id.name} - {self.sequence}'

        return {
            'type': 'ir.actions.report',
            'report_name': report_name,
            'report_type': 'qweb-pdf',
            'datas': datas,
            # 'context': self._context
        }




    