# -*- coding: utf-8 -*-

from logging import exception
from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import base64
import io
import xlsxwriter
import odoo
import threading
import math

class BrowsableObject(object):
    def __init__(self, employee_id, dict, env):
        self.employee_id = employee_id
        self.dict = dict
        self.env = env

    def __getattr__(self, attr):
        return attr in self.dict and self.dict.__getitem__(attr) or 0.0

class hr_payroll_social_security(models.Model):
    _name = 'hr.payroll.social.security'
    _description = 'Seguridad Social'

    year = fields.Integer('Año', required=True)
    month = fields.Selection([('1', 'Enero'),
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
                            ], string='Mes', required=True)
    observations = fields.Text('Observaciones')
    state = fields.Selection([
            ('draft', 'Borrador'),
            ('done', 'Realizado'),
            ('accounting', 'Contabilizado'),
        ], string='Estado', default='draft')
    #Proceso
    executing_social_security_ids = fields.One2many('hr.executing.social.security', 'executing_social_security_id', string='Ejecución')
    errors_social_security_ids = fields.One2many('hr.errors.social.security', 'executing_social_security_id', string='Advertencias')
    time_process = fields.Char(string='Tiempo ejecución')
    #Plano
    presentation_form = fields.Selection([('U', 'Único'),
                                            ('S','Sucursal')], string='Forma de presentación', default='U')
    branch_social_security_id = fields.Many2one('hr.social.security.branches',string='Sucursal', help='Seleccione la sucursal a generar el archivo plano.')
    work_center_social_security_id = fields.Many2one('hr.social.security.work.center', string='Centro de trabajo seguridad social', help='Seleccione el centro de trabajo a generar el archivo plano, si deja el campo vacio se generara con todos los centros de trabajo.')
    #Archivos
    excel_file = fields.Binary('Excel file')
    excel_file_name = fields.Char('Excel name', size=64)
    txt_file = fields.Binary('TXT file')
    txt_file_name = fields.Char('TXT name', size=64)

    move_id = fields.Many2one('account.move', string='Contabilidad')
    company_id = fields.Many2one('res.company', string='Compañía', readonly=True, required=True,
        default=lambda self: self.env.company)

    _sql_constraints = [('ssecurity_period_uniq', 'unique(company_id,year,month)', 'El periodo seleccionado ya esta registrado para esta compañía, por favor verificar.')]

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "Periodo {}-{}".format(record.month,str(record.year))))
        return result

    def executing_social_security_thread(self,date_start,date_end,obj_employee):
        with odoo.api.Environment.manage():
            registry = odoo.registry(self._cr.dbname)
            with registry.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                
                def roundup100(amount):
                    return math.ceil(amount / 100.0) * 100

                def roundupdecimal(amount):
                    return math.ceil(amount)

                #Obtener parametros anuales
                annual_parameters = env['hr.annual.parameters'].search([('year', '=', date_start.year)])

                #Recorre empleados y realizar la respectiva lógica
                for o_employee in obj_employee:
                    employee = env['hr.employee'].search([('id','=',o_employee.id)])
                    try:
                        #Obtener contrato activo
                        obj_contract = env['hr.contract'].search([('state','=','open'),('employee_id','=',employee.id)])
                        if not obj_contract:
                            obj_contract = env['hr.contract'].search([('state','=','close'),('employee_id','=',employee.id),('retirement_date','>=',date_start)], limit = 1)
                        #Obtener nóminas en ese rango de fechas
                        obj_payslip = env['hr.payslip'].search([('state','=','done'),('employee_id','=',employee.id),('contract_id','=',obj_contract.id),('date_from','>=',date_start),('date_to','<=',date_end)])

                        #Primero, encontró una entrada de trabajo que no excedió el intervalo.
                        work_entries = env['hr.work.entry'].search(
                            [
                                ('state', 'in', ['validated', 'draft']),
                                ('date_start', '>=', date_start),
                                ('date_stop', '<=', date_end),
                                ('contract_id', '=', obj_contract.id),
                                ('leave_id','!=',False)
                            ]
                        )
                        #En segundo lugar, encontró entradas de trabajo que exceden el intervalo y calculan la duración correcta. 
                        work_entries += env['hr.work.entry'].search(
                            [
                                '&', '&', '&',
                                ('leave_id','!=',False),
                                ('state', 'in', ['validated', 'draft']),
                                ('contract_id', '=', obj_contract.id),
                                '|', '|', '&', '&',
                                ('date_start', '>=', date_start),
                                ('date_start', '<', date_end),
                                ('date_stop', '>', date_end),
                                '&', '&',
                                ('date_start', '<', date_start),
                                ('date_stop', '<=', date_end),
                                ('date_stop', '>', date_start),
                                '&',
                                ('date_start', '<', date_start),
                                ('date_stop', '>', date_end),
                            ]
                        )
                    
                        #Variables
                        bEsAprendiz = True if obj_contract.contract_type == 'aprendizaje' else False
                        nDiasLiquidados = 0
                        nNumeroHorasLaboradas = 0
                        nIngreso = False
                        nRetiro = False
                        #Sueldo
                        nSueldo = obj_contract.wage
                        #Listas y diccionarios
                        category_news = ['INCAPACIDAD','LICENCIA_NO_REMUNERADA','LICENCIA_REMUNERADA','LICENCIA_MATERNIDAD','VACACIONES','ACCIDENTE_TRABAJO']
                        dict_social_security = {
                            'BaseSeguridadSocial':BrowsableObject(employee.id, {}, env),
                            'BaseParafiscales':BrowsableObject(employee.id, {}, env),
                            'Dias':BrowsableObject(employee.id, {}, env)
                        }                
                        #Valores
                        nValorBaseSalud,nValorBaseFondoPension,nValorBaseARP,nValorBaseCajaCom,nValorBaseSENA,nValorBaseICBF = 0,0,0,0,0,0
                        nValorSaludEmpleadoNomina,nValorPensionEmpleadoNomina,nValorFondoSolidaridad,nValorFondoSubsistencia = 0,0,0,0
                        #Entidades
                        TerceroEPS,TerceroPension,TerceroFondoSolidaridad,TerceroFondoSubsistencia = False,False,False,False
                        TerceroCesantias,TerceroCajaCompensacion,TerceroARP,TerceroSENA,TerceroICBF = False,False,False,False,False
                        for entity in employee.social_security_entities:
                            if entity.contrib_id.type_entities == 'eps': # Salud 
                                TerceroEPS = entity.partner_id
                            if entity.contrib_id.type_entities == 'pension': # Pension
                                TerceroPension = entity.partner_id
                            if entity.contrib_id.type_entities == 'solidaridad': # Solidaridad 
                                TerceroFondoSolidaridad = entity.partner_id
                            if entity.contrib_id.type_entities == 'subsistencia': # Subsistencia 
                                TerceroFondoSubsistencia = entity.partner_id
                            if entity.contrib_id.type_entities == 'caja': # Caja de compensación 
                                TerceroCajaCompensacion = entity.partner_id
                            if entity.contrib_id.type_entities == 'riesgo': # Aseguradora de riesgos laborales
                                TerceroARP = entity.partner_id
                            if entity.contrib_id.type_entities == 'cesantias': # Cesantias 
                                TerceroCesantias = entity.partner_id
                        
                        id_type_entities_sena = env['hr.contribution.register'].search([('type_entities','=','sena')], limit=1).id                
                        TerceroSENA = env['hr.employee.entities'].search([('types_entities','in',[id_type_entities_sena])]) # SENA
                        id_type_entities_icbf = env['hr.contribution.register'].search([('type_entities','=','icbf')], limit=1).id                
                        TerceroICBF = env['hr.employee.entities'].search([('types_entities','in',[id_type_entities_icbf])]) #  ICBF
                        
                        leave_list = []
                        for leave in work_entries:  
                            if  leave.leave_id.holiday_status_id.type_vacation != 'money':
                                #Obtener fechas y dias
                                request_date_from = leave.leave_id.request_date_from if leave.leave_id.request_date_from >= date_start else date_start
                                request_date_to = leave.leave_id.request_date_to if leave.leave_id.request_date_to <= date_end else date_end
                                number_of_days = self.dias360(request_date_from,request_date_to)

                                leave_dict = {'id':leave.leave_id.id,
                                                'type':leave.leave_id.holiday_status_id.code,
                                                'date_start': request_date_from,
                                                'date_end': request_date_to,
                                                'days':  number_of_days
                                            }
                                leave_list.append(leave_dict)

                        cant_payslip = 0
                        for payslip in obj_payslip:
                            #Variables
                            cant_payslip += 1
                            contract_id = payslip.contract_id
                            
                            #Obtener si es un ingreso o un retiro
                            if payslip.contract_id.date_start:
                                nIngreso = True if payslip.contract_id.date_start.month == date_start.month and payslip.contract_id.date_start.year == date_start.year else False
                            if payslip.contract_id.retirement_date:
                                nRetiro = True if payslip.contract_id.retirement_date.month == date_start.month and payslip.contract_id.retirement_date.year == date_start.year else False
                            #Obtener dias laborados
                            for days in payslip.worked_days_line_ids:
                                nDiasLiquidados	+= days.number_of_days if days.work_entry_type_id.code in ('WORK100','LEAVE105') else 0     
                                nNumeroHorasLaboradas += days.number_of_hours if days.work_entry_type_id.code in ('WORK100','LEAVE105') else 0                       
                            #Obtener valores
                            for line in payslip.line_ids:
                                #Bases seguridad social
                                if line.salary_rule_id.base_seguridad_social:
                                    dict_social_security['BaseSeguridadSocial'].dict['TOTAL'] = dict_social_security['BaseSeguridadSocial'].dict.get('TOTAL', 0) + line.total                            
                                    if line.salary_rule_id.category_id.code in category_news:
                                        dict_social_security['BaseSeguridadSocial'].dict[line.salary_rule_id.category_id.code] = dict_social_security['BaseSeguridadSocial'].dict.get(line.salary_rule_id.category_id.code, 0) + line.total                            
                                    else:
                                        if line.code == 'BASIC002' and contract_id.modality_salary == 'integral':
                                            value = (line.total*annual_parameters.porc_integral_salary)/100
                                            dict_social_security['BaseSeguridadSocial'].dict['BASE'] = dict_social_security['BaseSeguridadSocial'].dict.get('BASE', 0) + value
                                        else:
                                            dict_social_security['BaseSeguridadSocial'].dict['BASE'] = dict_social_security['BaseSeguridadSocial'].dict.get('BASE', 0) + line.total                            
                                #Bases parafiscales
                                if line.salary_rule_id.base_parafiscales:
                                    dict_social_security['BaseParafiscales'].dict['TOTAL'] = dict_social_security['BaseParafiscales'].dict.get('TOTAL', 0) + line.total                            
                                    if line.salary_rule_id.category_id.code in category_news:
                                        dict_social_security['BaseParafiscales'].dict[line.salary_rule_id.category_id.code] = dict_social_security['BaseParafiscales'].dict.get(line.salary_rule_id.category_id.code, 0) + line.total                            
                                    else:
                                        if line.code == 'BASIC002' and contract_id.modality_salary == 'integral':
                                            value = (line.total*annual_parameters.porc_integral_salary)/100
                                            dict_social_security['BaseParafiscales'].dict['BASE'] = dict_social_security['BaseParafiscales'].dict.get('BASE', 0) + value
                                        else:
                                            dict_social_security['BaseParafiscales'].dict['BASE'] = dict_social_security['BaseParafiscales'].dict.get('BASE', 0) + line.total                            

                                #Salud
                                nValorBaseSalud += line.total if line.salary_rule_id.base_seguridad_social else 0
                                nValorSaludEmpleadoNomina += abs(line.total) if line.code == 'SSOCIAL001' else 0
                                #Pension y fondo de solidaridad                        
                                nValorBaseFondoPension += line.total if line.salary_rule_id.base_seguridad_social else 0
                                nValorPensionEmpleadoNomina += abs(line.total) if line.code == 'SSOCIAL002' else 0
                                nValorFondoSubsistencia += abs(line.total) if line.code == 'SSOCIAL003' else 0
                                nValorFondoSolidaridad += abs(line.total) if line.code == 'SSOCIAL004' else 0
                                #ARL
                                nValorBaseARP += line.total if line.salary_rule_id.base_seguridad_social else 0                    
                                nPorcAporteARP = payslip.contract_id.risk_id.percent
                                #Caja de compensación
                                nValorBaseCajaCom += line.total if line.salary_rule_id.base_parafiscales else 0                    
                                #SENA & ICBF
                                nValorBaseSENA += line.total if line.salary_rule_id.base_parafiscales else 0                    
                                nValorBaseICBF += line.total if line.salary_rule_id.base_parafiscales else 0                    

                        if cant_payslip > 0:

                            #Validar que la suma de los dias sea igual a 30 y en caso de se superior restar en los dias liquidados la diferencia
                            nDiasTotales = nDiasLiquidados
                            for leave in leave_list:
                                nDiasTotales += leave['days'] if leave['type'] != 'COMPENSATORIO' else 0

                            nDiasLiquidados = (nDiasLiquidados-(nDiasTotales-30)) if (30-nDiasTotales) < 0 else nDiasLiquidados
                            
                            #Guardar linea principal
                            result = {
                                'executing_social_security_id': self.id,
                                'employee_id':employee.id,
                                'contract_id': contract_id.id,
                                'branch_id':employee.branch_id.id,
                                'nDiasLiquidados':nDiasLiquidados,    
                                'nNumeroHorasLaboradas':nNumeroHorasLaboradas,                    
                                'nIngreso':nIngreso,
                                'nRetiro':nRetiro,
                                'nSueldo':nSueldo,
                                #Salud
                                'TerceroEPS':TerceroEPS.id if TerceroEPS else False,
                                'nValorBaseSalud':nValorBaseSalud,    
                                'nValorSaludEmpleadoNomina':nValorSaludEmpleadoNomina,                    
                                #Pension
                                'TerceroPension':TerceroPension.id if TerceroPension else False,
                                'nValorBaseFondoPension':nValorBaseFondoPension,
                                'nValorPensionEmpleadoNomina':nValorPensionEmpleadoNomina+nValorFondoSubsistencia+nValorFondoSolidaridad,
                                #Fondo Solidaridad y Subsistencia
                                'TerceroFondoSolidaridad': TerceroFondoSolidaridad.id if TerceroFondoSolidaridad else TerceroPension.id if TerceroPension else False,
                                #ARP/ARL - Administradora de riesgos profesionales/laborales
                                'TerceroARP':TerceroARP.id if TerceroARP else False,
                                'nValorBaseARP':nValorBaseARP,
                                #Caja de Compensación
                                'TerceroCajaCom': TerceroCajaCompensacion.id if TerceroCajaCompensacion else False,
                                'nValorBaseCajaCom':nValorBaseCajaCom,
                                #SENA & ICBF
                                'cExonerado1607': employee.company_id.exonerated_law_1607 if bEsAprendiz == False and nSueldo < (annual_parameters.smmlv_monthly*10) else False,
                                'TerceroSENA': TerceroSENA.id if TerceroSENA else False,
                                'nValorBaseSENA':nValorBaseSENA,
                                'TerceroICBF': TerceroICBF.id if TerceroICBF else False,                
                                'nValorBaseICBF':nValorBaseICBF,                     
                            }

                            obj_executing = env['hr.executing.social.security'].create(result)     

                            #Una vez creada la linea principal, se obtienen las ausencias con sus respectivas fechas y se recalculan las lineas
                            for leave in leave_list:
                                result['leave_id'] = leave['id']
                                result['nDiasLiquidados'] = 0
                                result['nNumeroHorasLaboradas'] = 0
                                #Incapacidad EPS                        
                                nDiasIncapacidadEPS = leave['days'] if leave['type'] in ('EGA','EGH') else 0 # Categoria: INCAPACIDAD
                                dict_social_security['Dias'].dict['nDiasIncapacidadEPS'] = dict_social_security['Dias'].dict.get('nDiasIncapacidadEPS', 0) + nDiasIncapacidadEPS
                                result['nDiasIncapacidadEPS'] = nDiasIncapacidadEPS
                                result['dFechaInicioIGE'] = leave['date_start'] if leave['type'] in ('EGA','EGH') else False
                                result['dFechaFinIGE'] = leave['date_end'] if leave['type'] in ('EGA','EGH') else False
                                #Licencia
                                nDiasLicencia = leave['days'] if leave['type'] in ('LICENCIA_NO_REMUNERADA','INAS_INJU','SANCION','SUSP_CONTRATO') else 0 # Categoria: LICENCIA_NO_REMUNERADA
                                dict_social_security['Dias'].dict['nDiasLicencia'] = dict_social_security['Dias'].dict.get('nDiasLicencia', 0) + nDiasLicencia
                                result['nDiasLicencia'] = nDiasLicencia
                                result['dFechaInicioSLN'] = leave['date_start'] if leave['type'] in ('LICENCIA_NO_REMUNERADA','INAS_INJU','SANCION','SUSP_CONTRATO') else False
                                result['dFechaFinSLN'] = leave['date_end'] if leave['type'] in ('LICENCIA_NO_REMUNERADA','INAS_INJU','SANCION','SUSP_CONTRATO') else False
                                #Licencia Remunerada
                                nDiasLicenciaRenumerada = leave['days'] if leave['type'] in ('LICENCIA_REMUNERADA','LUTO') else 0 # Categoria: LICENCIA_REMUNERADA
                                dict_social_security['Dias'].dict['nDiasLicenciaRenumerada'] = dict_social_security['Dias'].dict.get('nDiasLicenciaRenumerada', 0) + nDiasLicenciaRenumerada
                                result['nDiasLicenciaRenumerada']	= nDiasLicenciaRenumerada
                                result['dFechaInicioVACLR'] = leave['date_start'] if leave['type'] in ('LICENCIA_REMUNERADA','LUTO','VACDISFRUTADAS') else False
                                result['dFechaFinVACLR'] = leave['date_end'] if leave['type'] in ('LICENCIA_REMUNERADA','LUTO','VACDISFRUTADAS') else False
                                #Maternida
                                nDiasMaternidad = leave['days'] if leave['type'] in ('MAT','PAT') else 0 # Categoria: LICENCIA_MATERNIDAD
                                dict_social_security['Dias'].dict['nDiasMaternidad'] = dict_social_security['Dias'].dict.get('nDiasMaternidad', 0) + nDiasMaternidad
                                result['nDiasMaternidad'] = nDiasMaternidad
                                result['dFechaInicioLMA'] = leave['date_start'] if leave['type'] in ('MAT','PAT') else False
                                result['dFechaFinLMA'] = leave['date_end'] if leave['type'] in ('MAT','PAT') else False
                                #Vacaciones
                                nDiasVacaciones = leave['days'] if leave['type'] == 'VACDISFRUTADAS' else 0 # Categoria: VACACIONES
                                dict_social_security['Dias'].dict['nDiasVacaciones'] = dict_social_security['Dias'].dict.get('nDiasVacaciones', 0) + nDiasVacaciones
                                result['nDiasVacaciones'] = nDiasVacaciones
                                result['dFechaInicioVACLR'] = leave['date_start'] if leave['type'] in ('LICENCIA_REMUNERADA','LUTO','VACDISFRUTADAS') else False
                                result['dFechaFinVACLR'] = leave['date_end'] if leave['type'] in ('LICENCIA_REMUNERADA','LUTO','VACDISFRUTADAS') else False
                                #ARL
                                nDiasIncapacidadARP = leave['days'] if leave['type'] in ('EP','AT') else 0 # Categoria: ACCIDENTE_TRABAJO
                                dict_social_security['Dias'].dict['nDiasIncapacidadARP'] = dict_social_security['Dias'].dict.get('nDiasIncapacidadARP', 0) + nDiasIncapacidadARP
                                result['nDiasIncapacidadARP'] = nDiasIncapacidadARP
                                result['dFechaInicioIRL'] = leave['date_start'] if leave['type'] in ('EP','AT') else False
                                result['dFechaFinIRL'] = leave['date_end'] if leave['type'] in ('EP','AT') else False

                                #Ingreso & Retiro - cuando existen novedades
                                nDiasAusencias = nDiasIncapacidadEPS+nDiasLicencia+nDiasLicenciaRenumerada+nDiasMaternidad+nDiasVacaciones+nDiasIncapacidadARP
                                result['nIngreso'] = False if nDiasAusencias > 0 else result['nIngreso']
                                result['nRetiro'] = False if nDiasAusencias > 0 else result['nRetiro']

                                obj_executing += env['hr.executing.social.security'].create(result)     

                            #Recorrer items creados
                            cant_items = len(obj_executing)
                            item = 1
                            #Valores TOTALES
                            nValorSaludTotalEmpleado,nValorSaludTotalEmpresa = 0,0
                            nValorPensioTotalEmpleado,nValorPensionTotalEmpresa,nValorTotalFondos = 0,0,0
                            nValorSaludTotal,nValorPensionTotal = 0,0
                            nRedondeoDecimalesDif = 5 # Max diferencia de decimales
                            for executing in sorted(obj_executing,key=lambda x: (x.nDiasLiquidados,x.nDiasIncapacidadEPS,x.nDiasVacaciones,x.nDiasMaternidad,x.nDiasIncapacidadARP,x.nDiasLicenciaRenumerada,x.nDiasLicencia)):                        
                                #Valores
                                nPorcAporteSaludEmpleado,nPorcAporteSaludEmpresa,nValorBaseSalud,nValorSaludEmpleado,nValorSaludEmpresa = 0,0,0,0,0         
                                nPorcAportePensionEmpleado,nPorcAportePensionEmpresa,nValorBaseFondoPension,nValorPensionEmpleado,nValorPensionEmpresa = 0,0,0,0,0
                                nPorcFondoSolidaridad,nValorFondoSolidaridad,nValorFondoSubsistencia = 0,0,0
                                nValorBaseARP,nValorARP = 0,0
                                nValorBaseCajaCom,nPorcAporteCajaCom,nValorCajaCom = 0,0,0
                                nValorBaseSENA,nPorcAporteSENA,nValorSENA = 0,0,0
                                nValorBaseICBF,nPorcAporteICBF,nValorICBF = 0,0,0
                                #Dias
                                nDiasLicencia = executing.nDiasLicencia
                                nDiasVacaciones = executing.nDiasVacaciones
                                nDiasAusencias = executing.nDiasIncapacidadEPS+executing.nDiasLicencia+executing.nDiasLicenciaRenumerada+executing.nDiasMaternidad+executing.nDiasIncapacidadARP
                                nDias = executing.nDiasLiquidados+executing.nDiasIncapacidadEPS+executing.nDiasLicencia+executing.nDiasLicenciaRenumerada+executing.nDiasMaternidad+executing.nDiasVacaciones+executing.nDiasIncapacidadARP
                                
                                #Calculos valores base dependiendo los días
                                if executing.nDiasLiquidados > 0:
                                    if dict_social_security['BaseSeguridadSocial'].dict.get('BASE', 0) > 0:
                                        nValorDiario = (dict_social_security['BaseSeguridadSocial'].dict['BASE'] / executing.nDiasLiquidados)
                                        nValorDiario = nValorDiario if nValorDiario >= annual_parameters.smmlv_monthly/30 else annual_parameters.smmlv_monthly/30                                        
                                        nValorBaseSalud = nValorDiario * executing.nDiasLiquidados
                                        nValorBaseFondoPension = nValorDiario * executing.nDiasLiquidados
                                        nValorBaseARP = nValorDiario * executing.nDiasLiquidados

                                        nValorDiario = (dict_social_security['BaseParafiscales'].dict['BASE'] / executing.nDiasLiquidados)
                                        nValorDiario = nValorDiario if nValorDiario >= annual_parameters.smmlv_monthly/30 else annual_parameters.smmlv_monthly/30                                        
                                        nValorBaseCajaCom = nValorDiario * executing.nDiasLiquidados
                                        nValorBaseSENA = nValorDiario * executing.nDiasLiquidados
                                        nValorBaseICBF = nValorDiario * executing.nDiasLiquidados

                                if executing.nDiasIncapacidadEPS > 0:
                                    if dict_social_security['BaseSeguridadSocial'].dict.get('INCAPACIDAD', 0) > 0:
                                        nValorDiario = (dict_social_security['BaseSeguridadSocial'].dict['INCAPACIDAD'] / dict_social_security['Dias'].dict['nDiasIncapacidadEPS'])
                                        nValorDiario = nValorDiario if nValorDiario >= annual_parameters.smmlv_monthly/30 else annual_parameters.smmlv_monthly/30
                                        nValorBaseSalud = nValorDiario * executing.nDiasIncapacidadEPS
                                        nValorBaseFondoPension = nValorDiario * executing.nDiasIncapacidadEPS
                                        nValorBaseARP = nValorDiario * executing.nDiasIncapacidadEPS

                                        nValorDiario = (dict_social_security['BaseParafiscales'].dict['INCAPACIDAD'] / dict_social_security['Dias'].dict['nDiasIncapacidadEPS'])
                                        nValorDiario = nValorDiario if nValorDiario >= annual_parameters.smmlv_monthly/30 else annual_parameters.smmlv_monthly/30
                                        nValorBaseCajaCom = nValorDiario * executing.nDiasIncapacidadEPS
                                        nValorBaseSENA = nValorDiario * executing.nDiasIncapacidadEPS
                                        nValorBaseICBF = nValorDiario * executing.nDiasIncapacidadEPS

                                if executing.nDiasLicencia > 0:
                                    if dict_social_security['BaseSeguridadSocial'].dict.get('LICENCIA_NO_REMUNERADA', 0) > 0:
                                        nValorBaseSalud = (dict_social_security['BaseSeguridadSocial'].dict['LICENCIA_NO_REMUNERADA'] / dict_social_security['Dias'].dict['nDiasLicencia']) * executing.nDiasLicencia
                                        nValorBaseFondoPension = (dict_social_security['BaseSeguridadSocial'].dict['LICENCIA_NO_REMUNERADA'] / dict_social_security['Dias'].dict['nDiasLicencia']) * executing.nDiasLicencia
                                        nValorBaseARP = (dict_social_security['BaseSeguridadSocial'].dict['LICENCIA_NO_REMUNERADA'] / dict_social_security['Dias'].dict['nDiasLicencia']) * executing.nDiasLicencia

                                        nValorBaseCajaCom = (dict_social_security['BaseParafiscales'].dict['LICENCIA_NO_REMUNERADA'] / dict_social_security['Dias'].dict['nDiasLicencia']) * executing.nDiasLicencia
                                        nValorBaseSENA = (dict_social_security['BaseParafiscales'].dict['LICENCIA_NO_REMUNERADA'] / dict_social_security['Dias'].dict['nDiasLicencia']) * executing.nDiasLicencia
                                        nValorBaseICBF = (dict_social_security['BaseParafiscales'].dict['LICENCIA_NO_REMUNERADA'] / dict_social_security['Dias'].dict['nDiasLicencia']) * executing.nDiasLicencia

                                if executing.nDiasLicenciaRenumerada > 0:
                                    if dict_social_security['BaseSeguridadSocial'].dict.get('LICENCIA_REMUNERADA', 0) > 0:
                                        nValorDiario = (dict_social_security['BaseSeguridadSocial'].dict['LICENCIA_REMUNERADA'] / dict_social_security['Dias'].dict['nDiasLicenciaRenumerada'])
                                        nValorDiario = nValorDiario if nValorDiario >= annual_parameters.smmlv_monthly/30 else annual_parameters.smmlv_monthly/30
                                        nValorBaseSalud = nValorDiario * executing.nDiasLicenciaRenumerada
                                        nValorBaseFondoPension = nValorDiario * executing.nDiasLicenciaRenumerada
                                        nValorBaseARP = nValorDiario * executing.nDiasLicenciaRenumerada

                                        nValorDiario = (dict_social_security['BaseParafiscales'].dict['LICENCIA_REMUNERADA'] / dict_social_security['Dias'].dict['nDiasLicenciaRenumerada'])
                                        nValorDiario = nValorDiario if nValorDiario >= annual_parameters.smmlv_monthly/30 else annual_parameters.smmlv_monthly/30
                                        nValorBaseCajaCom = nValorDiario * executing.nDiasLicenciaRenumerada
                                        nValorBaseSENA = nValorDiario * executing.nDiasLicenciaRenumerada
                                        nValorBaseICBF = nValorDiario * executing.nDiasLicenciaRenumerada

                                if executing.nDiasMaternidad > 0:
                                    if dict_social_security['BaseSeguridadSocial'].dict.get('LICENCIA_MATERNIDAD', 0) > 0:
                                        nValorDiario = (dict_social_security['BaseSeguridadSocial'].dict['LICENCIA_MATERNIDAD'] / dict_social_security['Dias'].dict['nDiasMaternidad'])
                                        nValorDiario = nValorDiario if nValorDiario >= annual_parameters.smmlv_monthly/30 else annual_parameters.smmlv_monthly/30
                                        nValorBaseSalud = nValorDiario * executing.nDiasMaternidad
                                        nValorBaseFondoPension = nValorDiario * executing.nDiasMaternidad
                                        nValorBaseARP = nValorDiario * executing.nDiasMaternidad

                                        nValorDiario = (dict_social_security['BaseParafiscales'].dict['LICENCIA_MATERNIDAD'] / dict_social_security['Dias'].dict['nDiasMaternidad'])
                                        nValorDiario = nValorDiario if nValorDiario >= annual_parameters.smmlv_monthly/30 else annual_parameters.smmlv_monthly/30
                                        nValorBaseCajaCom = nValorDiario * executing.nDiasMaternidad
                                        nValorBaseSENA = nValorDiario * executing.nDiasMaternidad
                                        nValorBaseICBF = nValorDiario * executing.nDiasMaternidad

                                if executing.nDiasVacaciones > 0:
                                    if dict_social_security['BaseSeguridadSocial'].dict.get('VACACIONES', 0) > 0:
                                        nValorDiario = (dict_social_security['BaseSeguridadSocial'].dict['VACACIONES'] / dict_social_security['Dias'].dict['nDiasVacaciones'])
                                        nValorDiario = nValorDiario if nValorDiario >= annual_parameters.smmlv_monthly/30 else annual_parameters.smmlv_monthly/30
                                        nValorBaseSalud = nValorDiario * executing.nDiasVacaciones
                                        nValorBaseFondoPension = nValorDiario * executing.nDiasVacaciones
                                        nValorBaseARP = nValorDiario * executing.nDiasVacaciones

                                        nValorDiario = (dict_social_security['BaseParafiscales'].dict['VACACIONES'] / dict_social_security['Dias'].dict['nDiasVacaciones'])
                                        nValorDiario = nValorDiario if nValorDiario >= annual_parameters.smmlv_monthly/30 else annual_parameters.smmlv_monthly/30
                                        nValorBaseCajaCom = nValorDiario * executing.nDiasVacaciones
                                        nValorBaseSENA = nValorDiario * executing.nDiasVacaciones
                                        nValorBaseICBF = nValorDiario * executing.nDiasVacaciones

                                if executing.nDiasIncapacidadARP > 0:
                                    if dict_social_security['BaseSeguridadSocial'].dict.get('ACCIDENTE_TRABAJO', 0) > 0:
                                        nValorDiario = (dict_social_security['BaseSeguridadSocial'].dict['ACCIDENTE_TRABAJO'] / dict_social_security['Dias'].dict['nDiasIncapacidadARP'])
                                        nValorDiario = nValorDiario if nValorDiario >= annual_parameters.smmlv_monthly/30 else annual_parameters.smmlv_monthly/30
                                        nValorBaseSalud = nValorDiario * executing.nDiasIncapacidadARP
                                        nValorBaseFondoPension = nValorDiario * executing.nDiasIncapacidadARP
                                        nValorBaseARP = nValorDiario * executing.nDiasIncapacidadARP

                                        nValorDiario = (dict_social_security['BaseParafiscales'].dict['ACCIDENTE_TRABAJO'] / dict_social_security['Dias'].dict['nDiasIncapacidadARP'])
                                        nValorDiario = nValorDiario if nValorDiario >= annual_parameters.smmlv_monthly/30 else annual_parameters.smmlv_monthly/30
                                        nValorBaseCajaCom = nValorDiario * executing.nDiasIncapacidadARP
                                        nValorBaseSENA = nValorDiario * executing.nDiasIncapacidadARP
                                        nValorBaseICBF = nValorDiario * executing.nDiasIncapacidadARP

                                #----------------CALCULOS SALUD
                                if nValorBaseSalud == 0:
                                    nValorBaseSalud = roundupdecimal((executing.nSueldo / 30) * nDias) 
                                else:
                                    nValorBaseSalud = roundupdecimal((executing.nSueldo / 30) * nDias) if abs(((executing.nSueldo / 30) * nDias) - nValorBaseSalud) < nRedondeoDecimalesDif else nValorBaseSalud
                                #nValorBaseSalud = ((executing.nSueldo / 30) * nDias) if nValorBaseSalud == 0 else (nValorBaseSalud)
                                if nValorBaseSalud > 0:
                                    if bEsAprendiz == False:
                                        nPorcAporteSaludEmpleado = annual_parameters.value_porc_health_employee
                                        nValorSaludEmpleado = nValorBaseSalud*(nPorcAporteSaludEmpleado/100) if nDiasLicencia==0 else 0
                                    else:
                                        nValorSaludEmpleado = 0
                                    if not employee.company_id.exonerated_law_1607 or (employee.company_id.exonerated_law_1607 and nSueldo >= (annual_parameters.smmlv_monthly*10)) or bEsAprendiz == True:
                                        nPorcAporteSaludEmpresa = annual_parameters.value_porc_health_company if not bEsAprendiz else annual_parameters.value_porc_health_employee+annual_parameters.value_porc_health_company
                                        nValorSaludEmpresa = nValorBaseSalud*(nPorcAporteSaludEmpresa/100)
                                    else:
                                        nPorcAporteSaludEmpresa,nValorSaludEmpresa = 0,0
                                    nValorSaludTotal += (nValorSaludEmpleado+nValorSaludEmpresa)
                                    nValorSaludTotalEmpleado += nValorSaludEmpleado
                                    nValorSaludTotalEmpresa += nValorSaludEmpresa
                                #----------------CALCULOS PENSION
                                if bEsAprendiz == False and employee.subtipo_coti_id.not_contribute_pension == False:
                                    if nValorBaseFondoPension == 0:
                                        nValorBaseFondoPension = roundupdecimal((executing.nSueldo / 30) * nDias) 
                                    else:
                                        nValorBaseFondoPension = roundupdecimal((executing.nSueldo / 30) * nDias) if abs(((executing.nSueldo / 30) * nDias) - nValorBaseFondoPension) < nRedondeoDecimalesDif else nValorBaseFondoPension
                                    #nValorBaseFondoPension = ((executing.nSueldo / 30) * nDias) if nValorBaseFondoPension == 0 else (nValorBaseFondoPension)
                                    if nValorBaseFondoPension > 0:
                                        nPorcAportePensionEmpleado = annual_parameters.value_porc_pension_employee
                                        nPorcAportePensionEmpresa = annual_parameters.value_porc_pension_company
                                        nValorPensionEmpleado = nValorBaseFondoPension*(nPorcAportePensionEmpleado/100) if nDiasLicencia==0 else 0
                                        nValorPensionEmpresa = nValorBaseFondoPension*(nPorcAportePensionEmpresa/100)
                                        nValorPensionTotal += (nValorPensionEmpleado+nValorPensionEmpresa)
                                        nValorPensioTotalEmpleado += nValorPensionEmpleado
                                        nValorPensionTotalEmpresa += nValorPensionEmpresa
                                        #Calculos fondo solidaridad
                                        nValorBaseFondoPensionTotal = dict_social_security['BaseSeguridadSocial'].dict.get('TOTAL', 0) 
                                        if (nValorBaseFondoPensionTotal/annual_parameters.smmlv_monthly) > 4 and (nValorBaseFondoPensionTotal/annual_parameters.smmlv_monthly) < 16:
                                            nPorcFondoSolidaridad = 1
                                        if  (nValorBaseFondoPensionTotal/annual_parameters.smmlv_monthly) >= 16 and (nValorBaseFondoPensionTotal/annual_parameters.smmlv_monthly) <= 17:
                                            nPorcFondoSolidaridad = 1.2
                                        if  (nValorBaseFondoPensionTotal/annual_parameters.smmlv_monthly) > 17 and (nValorBaseFondoPensionTotal/annual_parameters.smmlv_monthly) <= 18:
                                            nPorcFondoSolidaridad = 1.4
                                        if  (nValorBaseFondoPensionTotal/annual_parameters.smmlv_monthly) > 18 and (nValorBaseFondoPensionTotal/annual_parameters.smmlv_monthly) <= 19:
                                            nPorcFondoSolidaridad = 1.6
                                        if  (nValorBaseFondoPensionTotal/annual_parameters.smmlv_monthly) > 19 and (nValorBaseFondoPensionTotal/annual_parameters.smmlv_monthly) <= 20:
                                            nPorcFondoSolidaridad = 1.8
                                        if  (nValorBaseFondoPensionTotal/annual_parameters.smmlv_monthly) > 20:
                                            nPorcFondoSolidaridad = 2
                                        if nPorcFondoSolidaridad > 0:
                                            nPorcFondoSolidaridadCalculo = (nPorcFondoSolidaridad/100)/2
                                            nValorFondoSolidaridad = roundup100(nValorBaseFondoPension*nPorcFondoSolidaridadCalculo)
                                            nValorFondoSubsistencia = roundup100(nValorBaseFondoPension*nPorcFondoSolidaridadCalculo)
                                            nValorTotalFondos += (nValorFondoSolidaridad + nValorFondoSubsistencia)
                                else:
                                    nValorBaseFondoPension = 0
                                #----------------CALCULOS ARP
                                if nValorBaseARP == 0:
                                    nValorBaseARP = roundupdecimal((executing.nSueldo / 30) * nDias) 
                                else:
                                    nValorBaseARP = roundupdecimal((executing.nSueldo / 30) * nDias) if abs(((executing.nSueldo / 30) * nDias) - nValorBaseARP) < nRedondeoDecimalesDif else nValorBaseARP
                                #nValorBaseARP = ((executing.nSueldo / 30) * nDias) if nValorBaseARP == 0 else (nValorBaseARP)
                                if nValorBaseARP > 0 and nDiasAusencias == 0 and nDiasVacaciones == 0:
                                    nValorARP = roundup100(nValorBaseARP * nPorcAporteARP / 100)
                                #----------------CALCULOS CAJA DE COMPENSACIÓN
                                if bEsAprendiz == False:
                                    if nValorBaseCajaCom == 0:
                                        nValorBaseCajaCom = roundupdecimal((executing.nSueldo / 30) * nDias) 
                                    else:
                                        nValorBaseCajaCom = roundupdecimal((executing.nSueldo / 30) * nDias) if abs(((executing.nSueldo / 30) * nDias) - nValorBaseCajaCom) < nRedondeoDecimalesDif else nValorBaseCajaCom
                                    #nValorBaseCajaCom = ((executing.nSueldo / 30) * nDias) if nValorBaseCajaCom == 0 else (nValorBaseCajaCom)
                                    if nValorBaseCajaCom > 0 and nDiasAusencias == 0:
                                        nPorcAporteCajaCom = annual_parameters.value_porc_compensation_box_company
                                        nValorCajaCom = roundup100(nValorBaseCajaCom * nPorcAporteCajaCom / 100)
                                else:
                                    nValorBaseCajaCom = 0
                                #----------------CALCULOS SENA & ICBF
                                if bEsAprendiz == False:
                                    if nValorBaseSENA == 0:
                                        nValorBaseSENA = roundupdecimal((executing.nSueldo / 30) * nDias) 
                                    else:
                                        nValorBaseSENA = roundupdecimal((executing.nSueldo / 30) * nDias) if abs(((executing.nSueldo / 30) * nDias) - nValorBaseSENA) < nRedondeoDecimalesDif else nValorBaseSENA
                                    #nValorBaseSENA = ((executing.nValorBaseSENA / 30) * nDias) if nValorBaseSENA == 0 else (nValorBaseSENA)
                                    if nValorBaseICBF == 0:
                                        nValorBaseICBF = roundupdecimal((executing.nSueldo / 30) * nDias) 
                                    else:
                                        nValorBaseICBF = roundupdecimal((executing.nSueldo / 30) * nDias) if abs(((executing.nSueldo / 30) * nDias) - nValorBaseICBF) < nRedondeoDecimalesDif else nValorBaseICBF
                                    #nValorBaseICBF = ((executing.nValorBaseICBF / 30) * nDias) if nValorBaseICBF == 0 else (nValorBaseICBF)
                                    if not employee.company_id.exonerated_law_1607 or (employee.company_id.exonerated_law_1607 and nSueldo >= (annual_parameters.smmlv_monthly*10)):
                                        if nValorBaseSENA > 0 and nDiasAusencias == 0:
                                            nPorcAporteSENA = annual_parameters.value_porc_sena_company
                                            nValorSENA = roundup100(nValorBaseSENA * nPorcAporteSENA / 100)
                                        if nValorBaseICBF > 0 and nDiasAusencias == 0:
                                            nPorcAporteICBF = annual_parameters.value_porc_icbf_company
                                            nValorICBF = roundup100(nValorBaseICBF * nPorcAporteICBF / 100)
                                    else:
                                        nValorBaseSENA,nValorBaseICBF = 0,0
                                        nPorcAporteSENA,nValorSENA = 0,0
                                        nPorcAporteICBF,nValorICBF = 0,0
                                else:
                                    nValorBaseSENA,nValorBaseICBF = 0,0

                                result_update = {
                                    #Salud
                                    'nValorBaseSalud':nValorBaseSalud,
                                    'nPorcAporteSaludEmpleado': nPorcAporteSaludEmpleado if nValorSaludEmpleado > 0 else 0,
                                    'nValorSaludEmpleado':nValorSaludEmpleado,
                                    'nPorcAporteSaludEmpresa':nPorcAporteSaludEmpresa if nValorSaludEmpresa > 0 else 0,
                                    'nValorSaludEmpresa':nValorSaludEmpresa,     
                                    'nValorSaludEmpleadoNomina': 0,                       
                                    #Pension
                                    'nValorBaseFondoPension':nValorBaseFondoPension,
                                    'nPorcAportePensionEmpleado': nPorcAportePensionEmpleado if nValorPensionEmpleado > 0 else 0,
                                    'nValorPensionEmpleado':nValorPensionEmpleado,                            
                                    'nPorcAportePensionEmpresa': nPorcAportePensionEmpresa if nValorPensionEmpresa > 0 else 0,
                                    'nValorPensionEmpresa':nValorPensionEmpresa,                            
                                    'nValorPensionEmpleadoNomina': 0,
                                    #Fondo Solidaridad y Subsistencia
                                    'nPorcFondoSolidaridad': nPorcFondoSolidaridad, 
                                    'nValorFondoSolidaridad':nValorFondoSolidaridad,
                                    'nValorFondoSubsistencia':nValorFondoSubsistencia,
                                    #ARP/ARL - Administradora de riesgos profesionales/laborales
                                    'nValorBaseARP':nValorBaseARP,
                                    'nPorcAporteARP':nPorcAporteARP if nValorARP > 0 else 0,
                                    'nValorARP':nValorARP,
                                    #Caja de Compensación
                                    'nValorBaseCajaCom':nValorBaseCajaCom,
                                    'nPorcAporteCajaCom':nPorcAporteCajaCom if nValorCajaCom > 0 else 0,
                                    'nValorCajaCom':nValorCajaCom,
                                    #SENA & ICBF
                                    'nValorBaseSENA':nValorBaseSENA,
                                    'nPorcAporteSENA':nPorcAporteSENA if nValorSENA > 0 else 0,
                                    'nValorSENA':nValorSENA,
                                    'nValorBaseICBF':nValorBaseICBF,
                                    'nPorcAporteICBF':nPorcAporteICBF if nValorICBF > 0 else 0,
                                    'nValorICBF':nValorICBF,
                                }

                                if item == cant_items:
                                    result_update['nValorSaludTotal'] = roundup100(nValorSaludTotal)
                                    result_update['nValorPensionTotal'] = roundup100(nValorPensionTotal)
                                    result_update['nValorSaludEmpleadoNomina'] = executing.nValorSaludEmpleadoNomina
                                    result_update['nValorPensionEmpleadoNomina'] = executing.nValorPensionEmpleadoNomina
                                    result_update['nDiferenciaSalud'] = (roundup100(nValorSaludTotal) - (nValorSaludTotalEmpleado+nValorSaludTotalEmpresa)) + (nValorSaludTotalEmpleado-executing.nValorSaludEmpleadoNomina)
                                    result_update['nDiferenciaPension'] = (roundup100(nValorPensionTotal) - (nValorPensioTotalEmpleado+nValorPensionTotalEmpresa)) + ((nValorPensioTotalEmpleado+nValorTotalFondos)-executing.nValorPensionEmpleadoNomina)
                                
                                executing.write(result_update)     

                                if executing.nDiasLiquidados == 0 and executing.nDiasIncapacidadEPS == 0 and executing.nDiasLicencia == 0 and executing.nDiasLicenciaRenumerada == 0 and executing.nDiasMaternidad == 0 and executing.nDiasVacaciones == 0 and executing.nDiasIncapacidadARP == 0:
                                    executing.unlink()
                                    
                                item += 1

                        else:
                            result = {
                                'executing_social_security_id': self.id,
                                'employee_id':employee.id,
                                'branch_id':employee.branch_id.id,
                                'description': 'No se encontraron liquidaciones para el empleado, por favor verificar'
                            }
                            self.env['hr.errors.social.security'].create(result)
                    except Exception as e:
                        result = {
                            'executing_social_security_id': self.id,
                            'employee_id':employee.id,
                            'branch_id':employee.branch_id.id,
                            'description': str(e.args[0])
                        }
                        env['hr.errors.social.security'].create(result)
    
    def executing_social_security(self):
        #Eliminar ejecución
        self.env['hr.errors.social.security'].search([('executing_social_security_id','=',self.id)]).unlink()
        self.env['hr.executing.social.security'].search([('executing_social_security_id','=',self.id)]).unlink()

        #Obtener fechas del periodo seleccionado
        date_start = '01/'+str(self.month)+'/'+str(self.year)
        try:
            date_start = datetime.strptime(date_start, '%d/%m/%Y')       

            date_end = date_start + relativedelta(months=1)
            date_end = date_end - timedelta(days=1)
            
            date_start = date_start.date()
            date_end = date_end.date()
        except:
            raise UserError(_('El año digitado es invalido, por favor verificar.'))

        #Obtener empleados que tuvieron liquidaciones en el mes
        query = '''
            select distinct b.id 
            from hr_payslip a 
            inner join hr_employee b on a.employee_id = b.id 
            where a.state = 'done' and a.date_from >= '%s' and a.date_to <= '%s' and a.company_id = %s                                
        ''' % (date_start,date_end,self.company_id.id)

        self.env.cr.execute(query)
        result_query = self.env.cr.fetchall()

        employee_ids = []
        for result in result_query:
            employee_ids.append(result)
        obj_employee = self.env['hr.employee'].search([('id', 'in', employee_ids)])
        
        #Guardo los empleados en lotes de a 20
        employee_array, i, j = [], 0 , 20            
        while i <= len(obj_employee):                
            employee_array.append(obj_employee[i:j])
            i = j
            j += 20   

        #Los lotes anteriores, los separo en los de 5, para ejecutar un maximo de 5 hilos
        employee_array_def, i, j = [], 0 , 5            
        while i <= len(employee_array):                
            employee_array_def.append(employee_array[i:j])
            i = j
            j += 5  

        #----------------------------Recorrer multihilos
        date_start_process = datetime.now()
        date_finally_process = datetime.now()
        i = 1
        for employee in employee_array_def:
            array_thread = []
            for emp in employee:
                t = threading.Thread(target=self.executing_social_security_thread, args=(date_start,date_end,emp,))                
                t.start()
                array_thread.append(t)
                i += 1   

            for hilo in array_thread:
                while hilo.is_alive():
                    date_finally_process = datetime.now()  


        time_process = date_finally_process - date_start_process
        time_process = time_process.seconds / 60

        self.time_process = 'El proceso se demoro '+str(time_process)+' minutos.'
        self.state = 'done'

    def get_excel(self):
        filename= 'Seguridad Social Periodo {}-{}.xlsx'.format(self.month,str(self.year))
        stream = io.BytesIO()
        book = xlsxwriter.Workbook(stream, {'in_memory': True})
        sheet = book.add_worksheet('Seguridad Social')

        columns = [
            'Empleado','Sucursal','Contrato','Días liquidados','Días incapacidad EPS','Días licencia','Días licencia remunerada','Días maternidad','Días vacaciónes','Días incapacidad ARP',
            'Ingreso','Retiro','Sueldo','Tercero EPS','Valor base salud','Porc. Aporte salud empleados','Valor salud empleado','Valor salud empleado nómina','Porc. Aporte salud empresa',
            'Valor salud empresa','Valor salud total','Diferencia salud','Tercero pensión','Valor base fondo de pensión','Porc. Aporte pensión empleado','Valor pensión empleado',
            'Valor pensión empleado nómina','Porc. Aporte pensión empresa','Valor pensión empresa','Valor pensión total','Diferencia pensión','Tercero fondo solidaridad',
            'Porc. Fondo solidaridad','Valor fondo solidaridad','Valor fondo subsistencia','Tercero ARP','Valor base ARP','Porc. Aporte ARP','Valor ARP','Exonerado ley 1607',
            'Tercero caja compensación','Valor base caja com','Porc. Aporte caja com','Valor caja com','Tercero SENA','Valor base SENA','Porc. Aporte SENA','Valor SENA',
            'Tercero ICBF','Valor base ICBF','Porc. Aporte ICBF','Valor ICBF','Fecha Inicio SLN','Fecha Fin SLN','Fecha Inicio IGE','Fecha Fin IGE',
            'Fecha Inicio LMA','Fecha Fin LMA','Fecha Inicio VACLR','Fecha Fin VACLR','Fecha Inicio VCT','Fecha Fin VCT','Fecha Inicio IRL','Fecha Fin IRL'
        ]

        #Agregar columnas
        aument_columns = 0
        for columns in columns:            
            sheet.write(0, aument_columns, columns)
            aument_columns = aument_columns + 1

        #Agregar valores        
        aument_rows = 1
        for item in self.executing_social_security_ids: 
            sheet.write(aument_rows, 0, item.employee_id.name)
            sheet.write(aument_rows, 1, item.branch_id.name)
            sheet.write(aument_rows, 2, item.contract_id.name)
            sheet.write(aument_rows, 3, item.nDiasLiquidados)
            sheet.write(aument_rows, 4, item.nDiasIncapacidadEPS)
            sheet.write(aument_rows, 5, item.nDiasLicencia)
            sheet.write(aument_rows, 6, item.nDiasLicenciaRenumerada)
            sheet.write(aument_rows, 7, item.nDiasMaternidad)
            sheet.write(aument_rows, 8, item.nDiasVacaciones)
            sheet.write(aument_rows, 9, item.nDiasIncapacidadARP)
            sheet.write(aument_rows, 10, item.nIngreso)
            sheet.write(aument_rows, 11, item.nRetiro)
            sheet.write(aument_rows, 12, item.nSueldo)
            sheet.write(aument_rows, 13, item.TerceroEPS.name if item.TerceroEPS else '')
            sheet.write(aument_rows, 14, item.nValorBaseSalud)
            sheet.write(aument_rows, 15, item.nPorcAporteSaludEmpleado)
            sheet.write(aument_rows, 16, item.nValorSaludEmpleado)
            sheet.write(aument_rows, 17, item.nValorSaludEmpleadoNomina)
            sheet.write(aument_rows, 18, item.nPorcAporteSaludEmpresa)
            sheet.write(aument_rows, 19, item.nValorSaludEmpresa)
            sheet.write(aument_rows, 20, item.nValorSaludTotal)
            sheet.write(aument_rows, 21, item.nDiferenciaSalud)
            sheet.write(aument_rows, 22, item.TerceroPension.name if item.TerceroPension else '')
            sheet.write(aument_rows, 23, item.nValorBaseFondoPension)
            sheet.write(aument_rows, 24, item.nPorcAportePensionEmpleado)
            sheet.write(aument_rows, 25, item.nValorPensionEmpleado)
            sheet.write(aument_rows, 26, item.nValorPensionEmpleadoNomina)
            sheet.write(aument_rows, 27, item.nPorcAportePensionEmpresa)
            sheet.write(aument_rows, 28, item.nValorPensionEmpresa)
            sheet.write(aument_rows, 29, item.nValorPensionTotal)
            sheet.write(aument_rows, 30, item.nDiferenciaPension)
            sheet.write(aument_rows, 31, item.TerceroFondoSolidaridad.name if item.TerceroFondoSolidaridad else '')
            sheet.write(aument_rows, 32, item.nPorcFondoSolidaridad)
            sheet.write(aument_rows, 33, item.nValorFondoSolidaridad)
            sheet.write(aument_rows, 34, item.nValorFondoSubsistencia)
            sheet.write(aument_rows, 35, item.TerceroARP.name if item.TerceroARP else '')
            sheet.write(aument_rows, 36, item.nValorBaseARP)
            sheet.write(aument_rows, 37, item.nPorcAporteARP)
            sheet.write(aument_rows, 38, item.nValorARP)
            sheet.write(aument_rows, 39, item.cExonerado1607)
            sheet.write(aument_rows, 40, item.TerceroCajaCom.name if item.TerceroCajaCom else '')
            sheet.write(aument_rows, 41, item.nValorBaseCajaCom)
            sheet.write(aument_rows, 42, item.nPorcAporteCajaCom)
            sheet.write(aument_rows, 43, item.nValorCajaCom)
            sheet.write(aument_rows, 44, item.TerceroSENA.name if item.TerceroSENA else '')
            sheet.write(aument_rows, 45, item.nValorBaseSENA)
            sheet.write(aument_rows, 46, item.nPorcAporteSENA)
            sheet.write(aument_rows, 47, item.nValorSENA)
            sheet.write(aument_rows, 48, item.TerceroICBF.name if item.TerceroICBF else '')
            sheet.write(aument_rows, 49, item.nValorBaseICBF)
            sheet.write(aument_rows, 50, item.nPorcAporteICBF)
            sheet.write(aument_rows, 51, item.nValorICBF)
            sheet.write(aument_rows, 52, item.dFechaInicioSLN)
            sheet.write(aument_rows, 53, item.dFechaFinSLN)
            sheet.write(aument_rows, 54, item.dFechaInicioIGE)
            sheet.write(aument_rows, 55, item.dFechaFinIGE)
            sheet.write(aument_rows, 56, item.dFechaInicioLMA)
            sheet.write(aument_rows, 57, item.dFechaFinLMA)
            sheet.write(aument_rows, 58, item.dFechaInicioVACLR)
            sheet.write(aument_rows, 59, item.dFechaFinVACLR)
            sheet.write(aument_rows, 60, item.dFechaInicioVCT)
            sheet.write(aument_rows, 61, item.dFechaFinVCT)
            sheet.write(aument_rows, 62, item.dFechaInicioIRL)
            sheet.write(aument_rows, 63, item.dFechaFinIRL)
            aument_rows = aument_rows + 1
        book.close()
        
        self.write({
            'excel_file': base64.encodestring(stream.getvalue()),
            'excel_file_name': filename,
        })
        
        action = {
                    'name': 'Export Seguridad Social',
                    'type': 'ir.actions.act_url',
                    'url': "web/content/?model=hr.payroll.social.security&id=" + str(self.id) + "&filename_field=excel_file_name&field=excel_file&download=true&filename=" + self.excel_file_name,
                    'target': 'self',
                }
        return action   

    def get_excel_errors(self):
        filename= 'Seguridad Social Advertencias Periodo {}-{}.xlsx'.format(self.month,str(self.year))
        stream = io.BytesIO()
        book = xlsxwriter.Workbook(stream, {'in_memory': True})
        sheet = book.add_worksheet('Seguridad Social')

        columns = [
            'Empleado','Sucursal','Advertencia'
        ]

        #Agregar columnas
        aument_columns = 0
        for columns in columns:            
            sheet.write(0, aument_columns, columns)
            aument_columns = aument_columns + 1

        #Agregar valores        
        aument_rows = 1
        for item in self.errors_social_security_ids: 
            sheet.write(aument_rows, 0, item.employee_id.name)
            sheet.write(aument_rows, 1, item.branch_id.name)
            sheet.write(aument_rows, 2, item.description)
            aument_rows = aument_rows + 1
        book.close()
        
        self.write({
            'excel_file': base64.encodestring(stream.getvalue()),
            'excel_file_name': filename,
        })
        
        action = {
                    'name': 'Export Seguridad Social',
                    'type': 'ir.actions.act_url',
                    'url': "web/content/?model=hr.payroll.social.security&id=" + str(self.id) + "&filename_field=excel_file_name&field=excel_file&download=true&filename=" + self.excel_file_name,
                    'target': 'self',
                }
        return action    
        
    def get_accounting(self):
        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        # Obtener fechas del periodo seleccionado
        date_start = '01/' + str(self.month) + '/' + str(self.year)
        try:
            date_start = datetime.strptime(date_start, '%d/%m/%Y')

            date_end = date_start + relativedelta(months=1)
            date_end = date_end - timedelta(days=1)

            date_start = date_start.date()
            date_end = date_end.date()
        except:
            raise UserError(_('El año digitado es invalido, por favor verificar.'))

        date = date_end
        move_dict = {
            'narration': '',
            'ref': f"Seguridad Social - {date.strftime('%B %Y')}",
            'journal_id': False,
            'date': date,
        }

        ls_process_accounting = ['ss_empresa_salud','ss_empresa_pension','ss_empresa_arp','ss_empresa_caja','ss_empresa_sena','ss_empresa_icbf']
        obj_employee = self.env['hr.employee'].search([('id','!=',False)])

        for employee in obj_employee:
            executing_social_security = self.env['hr.executing.social.security'].search([('executing_social_security_id', '=', self.id),('employee_id','=',employee.id)])

            debit_third_id = employee.address_home_id
            credit_third_id = employee.address_home_id
            analytic_account_id = employee.analytic_account_id

            if len(executing_social_security) > 0:
                for process in ls_process_accounting:
                    value_account = 0
                    description = ''
                    obj_closing = self.env['hr.closing.configuration.header'].search([('process', '=', process)])

                    for closing in obj_closing:
                        move_dict['journal_id'] = closing.journal_id.id
                        for account_rule in closing.detail_ids:
                            debit_account_id = False
                            credit_account_id = False
                            # Validar ubicación de trabajo
                            bool_work_location = False
                            if account_rule.work_location.id == employee.address_id.id or account_rule.work_location.id == False:
                                bool_work_location = True
                            # Validar compañia
                            bool_company = False
                            if account_rule.company.id == employee.company_id.id or account_rule.company.id == False:
                                bool_company = True
                            # Validar departamento
                            bool_department = False
                            if account_rule.department.id == employee.department_id.id or account_rule.department.id == employee.department_id.parent_id.id or account_rule.department.id == False:
                                bool_department = True

                            if bool_department and bool_company and bool_work_location:
                                debit_account_id = account_rule.debit_account
                                credit_account_id = account_rule.credit_account

                            # Tercero debito
                            if account_rule.third_debit == 'entidad':
                                for entity in employee.social_security_entities:
                                    if entity.contrib_id.type_entities == 'eps' and process == 'ss_empresa_salud':  # SALUD
                                        debit_third_id = entity.partner_id.partner_id
                                    if entity.contrib_id.type_entities == 'pension' and process == 'ss_empresa_pension':  # PENSION
                                        debit_third_id = entity.partner_id.partner_id
                                    if entity.contrib_id.type_entities == 'riesgo' and process == 'ss_empresa_arp': # ARP
                                        debit_third_id = entity.partner_id.partner_id
                                    if entity.contrib_id.type_entities == 'caja' and process == 'ss_empresa_caja': # CAJA DE COMPENSACIÓN
                                        debit_third_id = entity.partner_id.partner_id
                                if process == 'ss_empresa_sena':
                                    id_type_entities_sena = self.env['hr.contribution.register'].search([('type_entities', '=', 'sena')], limit=1).id
                                    debit_third_id = self.env['hr.employee.entities'].search([('types_entities', 'in', [id_type_entities_sena])], limit=1).partner_id  # SENA
                                if process == 'ss_empresa_icbf':
                                    id_type_entities_icbf = self.env['hr.contribution.register'].search([('type_entities', '=', 'icbf')], limit=1).id
                                    debit_third_id = self.env['hr.employee.entities'].search([('types_entities', 'in', [id_type_entities_icbf])], limit=1).partner_id  # ICBF
                            elif account_rule.third_debit == 'compañia':
                                debit_third_id = employee.company_id.partner_id
                            elif account_rule.third_debit == 'empleado':
                                debit_third_id = employee.address_home_id

                            # Tercero credito
                            if account_rule.third_credit == 'entidad':
                                for entity in employee.social_security_entities:
                                    if entity.contrib_id.type_entities == 'eps' and process == 'ss_empresa_salud':  # SALUD
                                        credit_third_id = entity.partner_id.partner_id
                                    if entity.contrib_id.type_entities == 'pension' and process == 'ss_empresa_pension':  # PENSION
                                        credit_third_id = entity.partner_id.partner_id
                                    if entity.contrib_id.type_entities == 'riesgo' and process == 'ss_empresa_arp':  # ARP
                                        credit_third_id = entity.partner_id.partner_id
                                    if entity.contrib_id.type_entities == 'caja' and process == 'ss_empresa_caja':  # CAJA DE COMPENSACIÓN
                                        credit_third_id = entity.partner_id.partner_id
                                if process == 'ss_empresa_sena':
                                    id_type_entities_sena = self.env['hr.contribution.register'].search([('type_entities', '=', 'sena')], limit=1).id
                                    credit_third_id = self.env['hr.employee.entities'].search([('types_entities', 'in', [id_type_entities_sena])], limit=1).partner_id  # SENA
                                if process == 'ss_empresa_icbf':
                                    id_type_entities_icbf = self.env['hr.contribution.register'].search([('type_entities', '=', 'icbf')], limit=1).id
                                    credit_third_id = self.env['hr.employee.entities'].search([('types_entities', 'in', [id_type_entities_icbf])], limit=1).partner_id  # ICBF
                            elif account_rule.third_credit == 'compañia':
                                credit_third_id = employee.company_id.partner_id
                            elif account_rule.third_credit == 'empleado':
                                credit_third_id = employee.address_home_id

                            if process == 'ss_empresa_salud':
                                value_account = sum([i.nValorSaludEmpresa+i.nDiferenciaSalud for i in executing_social_security])
                                description = f'Aporte empresa salud - {employee.identification_id} - {employee.name}'
                            elif process == 'ss_empresa_pension':
                                value_account = sum([i.nValorPensionEmpresa + i.nDiferenciaPension for i in executing_social_security])
                                description = f'Aporte empresa pensión - {employee.identification_id} - {employee.name}'
                            elif process == 'ss_empresa_arp':
                                value_account = sum([i.nValorARP for i in executing_social_security])
                                description = f'Aporte ARP - {employee.identification_id} - {employee.name}'
                            elif process == 'ss_empresa_caja':
                                value_account = sum([i.nValorCajaCom for i in executing_social_security])
                                description = f'Aporte caja de compensación - {employee.identification_id} - {employee.name}'
                            elif process == 'ss_empresa_sena':
                                value_account = sum([i.nValorSENA for i in executing_social_security])
                                description = f'Aporte SENA - {employee.identification_id} - {employee.name}'
                            elif process == 'ss_empresa_icbf':
                                value_account = sum([i.nValorICBF for i in executing_social_security])
                                description = f'Aporte ICBF - {employee.identification_id} - {employee.name}'

                            if debit_third_id == False and credit_third_id == False:
                                raise ValidationError(_(f'Falta configurar la entidad para el proceso {description}.'))

                            #Crear item contable
                            amount = value_account
                            if debit_account_id and amount != 0:
                                debit = abs(amount) if amount > 0.0 else 0.0
                                credit = abs(amount) if amount < 0.0 else 0.0
                                debit_line = {
                                    'name': description,
                                    'partner_id': debit_third_id.id,# if debit > 0 else credit_third_id.id,
                                    'account_id': debit_account_id.id,# if debit > 0 else credit_account_id.id,
                                    'journal_id': closing.journal_id.id,
                                    'date': date,
                                    'debit': debit,
                                    'credit': credit,
                                    'analytic_account_id': analytic_account_id.id,
                                }
                                line_ids.append(debit_line)

                            if credit_account_id and amount != 0:
                                debit = abs(amount) if amount < 0.0 else 0.0
                                credit = abs(amount) if amount > 0.0 else 0.0

                                credit_line = {
                                    'name': description,
                                    'partner_id': credit_third_id.id,
                                    'account_id': credit_account_id.id,
                                    'journal_id': closing.journal_id.id,
                                    'date': date,
                                    'debit': debit,
                                    'credit': credit,
                                    'analytic_account_id': analytic_account_id.id,
                                }
                                line_ids.append(credit_line)

        move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
        move = self.env['account.move'].create(move_dict)
        self.write({'move_id': move.id, 'state': 'accounting'})

    def cancel_process(self):
        #Eliminar ejecución
        self.env['hr.errors.social.security'].search([('executing_social_security_id','=',self.id)]).unlink()
        self.env['hr.executing.social.security'].search([('executing_social_security_id','=',self.id)]).unlink()
        return self.write({'state':'draft','time_process':''})

    def restart_accounting(self):
        if self.move_id:
            if self.move_id.state != 'draft':
                raise ValidationError(_('No se puede reversar el movimiento contable debido a que su estado es diferente de borrador.'))
            self.move_id.unlink()
        return self.write({'state': 'done'})

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise ValidationError(_('No se puede eliminar la provisión debido a que su estado es diferente de borrador.'))
        return super(hr_payroll_social_security, self).unlink()
                    



        





