# -*- coding: utf-8 -*-

from logging import exception
from odoo import tools
from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import base64
import io
import xlsxwriter
import odoo
import math

class hr_payroll_social_security(models.Model):
    _inherit = 'hr.payroll.social.security'
    

    def get_plano(self):
        def left(s, amount):
                return s[:amount]
            
        def right(s, amount):
            return s[-amount:]

        def roundup100(amount):
            return math.ceil(amount / 100.0) * 100

        annual_parameters = self.env['hr.annual.parameters'].search([('year', '=', self.year)])

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
    
        #Forma de presentación
        if self.presentation_form != 'U':
            if not self.branch_social_security_id:
                raise ValidationError(_('La forma de presentación es sucursal, debe seleccionar la sucursal a generar el plano.'))               

            if self.work_center_social_security_id:
                query_CantEmpleados = '''
                    Select count(*) as nCantEmpleados
                    From
                    (
                        Select Distinct a.employee_id 
                        From hr_executing_social_security as a
                        inner join hr_employee b on a.employee_id = b.id and b.branch_social_security_id = %s and b.work_center_social_security_id = %s
                        Where a.executing_social_security_id = %s
                    ) as A
                ''' % (self.branch_social_security_id.id,self.work_center_social_security_id.id,self.id)
            else:
                query_CantEmpleados = '''
                    Select count(*) as nCantEmpleados
                    From
                    (
                        Select Distinct a.employee_id 
                        From hr_executing_social_security as a
                        inner join hr_employee b on a.employee_id = b.id and b.branch_social_security_id = %s
                        Where a.executing_social_security_id = %s
                    ) as A
                ''' % (self.branch_social_security_id.id,self.id)
        else:
            query_CantEmpleados = '''
                Select count(*) as nCantEmpleados
                From
                (
                    Select Distinct employee_id From hr_executing_social_security 
                    Where executing_social_security_id = %s
                ) as A
            ''' % (self.id)

        self.env.cr.execute(query_CantEmpleados)
        nCantidadEmpleados = self.env.cr.fetchone()

        #----------------------------------REGISTRO TIPO 1 ENCABEZADO----------------------------------
        cTipoRegistro = '01'
        cModalidadPlanilla = '1'
        cSecuencia = '0001'
        cRazonSocial = left(self.company_id.partner_id.name+200*' ',200)
        switch_cTipIdTercero = {
            '11': 'RC',
            '12': 'TI',
            '13': 'CC',
            '22': 'CE',
            '31': 'NI',
            '41': 'PA',
            'PE': 'PT',
            'PT': 'PT'
        }             
        cTipIdTercero = switch_cTipIdTercero.get(self.company_id.partner_id.x_document_type, '/')
        if cTipIdTercero == '/':
            raise ValidationError(_('El tipo de documento del tercero '+self.company_id.partner_id.name+' es invalido, por favor verificar.'))           
        cNumIdTercero = left(self.company_id.partner_id.vat+16*' ',16)
        cDigitoVerificacion = str(self.company_id.partner_id.x_digit_verification)
        cTipoPlanilla = 'E'
        cPlanillaAsociada = ' '*10
        cFechaPlanillaAsociada = ' '*10
        cFormaPresentacion = left(self.presentation_form,1)
        if self.presentation_form != 'U':
            cCodSucursalEmpresa = left(self.branch_social_security_id.code+' '*10,10)
            cNombreSucursalEmpresa = left(self.branch_social_security_id.name+' '*40,40)
        else:
            cCodSucursalEmpresa = ' '*10
            cNombreSucursalEmpresa = ' '*40
        cCodigoEntidadARP = ' '*6
        if self.company_id.entity_arp_id.code_pila_eps:
            cCodigoEntidadARP = left(self.company_id.entity_arp_id.code_pila_eps+' '*6,6)
        else:
            raise ValidationError(_('La compañía no tiene configurado entidad ARP o no tiene código, por favor verificar.'))           
        cPeriodoPagoDifSalud = left(str(self.year)+'0000',4)+'-'+right('00'+self.month,2)
        month_next = str(int(self.month)+1) if self.month != '12' else '01'
        year_next = str(self.year) if self.month != '12' else str(self.year+1)
        cPeriodoPagoSalud = left(year_next+'0000',4)+'-'+right('00'+month_next,2)
        cNumRadicacion = '0'*10
        dFechaPago = ' '*10
        cCantidadEmpleados = right(5*'0'+str(nCantidadEmpleados[0]),5)
        cValorNomina = 'nValorNomina'
        cTipoAportante = '00'
        if self.company_id.type_contributor:
            cTipoAportante = right('00'+self.company_id.type_contributor,2)
        else:
            raise ValidationError(_('La compañía no tiene configurado el tipo de aportante, por favor verificar.'))           
        cCodOperador = '00'
        
        #Concatenar encabezado
        encab_part_one = '%s%s%s%s%s%s%s' % (cTipoRegistro,cModalidadPlanilla,cSecuencia,cRazonSocial,cTipIdTercero,cNumIdTercero,cDigitoVerificacion)
        encab_part_two = '%s%s%s%s%s%s%s' % (cTipoPlanilla,cPlanillaAsociada,cFechaPlanillaAsociada,cFormaPresentacion,cCodSucursalEmpresa,cNombreSucursalEmpresa,cCodigoEntidadARP)
        encab_part_three = '%s%s%s%s%s%s%s%s' % (cPeriodoPagoDifSalud,cPeriodoPagoSalud,cNumRadicacion,dFechaPago,cCantidadEmpleados,cValorNomina,cTipoAportante,cCodOperador)
    
        encab_part = '%s%s%s' % (encab_part_one,encab_part_two,encab_part_three)

        #----------------------------------REGISTRO TIPO 2 LIQUIDACIÓN DETALLADA DE APORTES----------------------------------
        nValorNomina = 0
        cant_detalle = 1
        detalle_part = ''
        cTipoRegistro = '02'
        if self.presentation_form != 'U':
            if self.work_center_social_security_id:
                details = self.executing_social_security_ids.filtered(lambda x: x.employee_id.work_center_social_security_id.id == self.work_center_social_security_id.id)
            else:
                details = self.executing_social_security_ids.filtered(lambda x: x.employee_id.branch_social_security_id.id == self.branch_social_security_id.id)
        else:
            details = self.executing_social_security_ids
            
        for item in details:
            # Obtener tipo y subtipo de cotizante de acuerdo a la fecha
            if item.nValorUPC > 0 and item.dependent_upc_id:
                obj_tipo_coti = self.env['hr.tipo.cotizante'].search([('code', '=', '40')])
                obj_subtipo_coti = self.env['hr.subtipo.cotizante'].search([('code', '=', '00')])
            else:
                obj_tipo_coti = item.employee_id.tipo_coti_id
                obj_subtipo_coti = item.employee_id.subtipo_coti_id
                obj_history_social_security = self.env['zue.hr.history.employee.social.security'].search(
                    [('z_employee_id.id', '=', item.employee_id.id)])
                if len(obj_history_social_security) > 0: #and item.contract_id.state != 'open' and item.contract_id.id != item.employee_id.contract_id.id:
                    for history_ss in sorted(obj_history_social_security, key=lambda x: x.z_date_change):
                        if item.contract_id.state != 'open' and item.contract_id.id != item.employee_id.contract_id.id:
                            if item.contract_id.date_start >= history_ss.z_date_change and item.employee_id.contract_id.date_start <= history_ss.z_date_change and date_start >= history_ss.z_date_change and date_end <= history_ss.z_date_change:
                                obj_tipo_coti = history_ss.z_tipo_coti_id
                                obj_subtipo_coti = history_ss.z_subtipo_coti_id
                                break
                        else:
                            if date_start < history_ss.z_date_change:
                                obj_tipo_coti = history_ss.z_tipo_coti_id
                                obj_subtipo_coti = history_ss.z_subtipo_coti_id
                                break
            # Obtener parametrización de cotizantes
            obj_parameterization_contributors = self.env['hr.parameterization.of.contributors'].search(
                [('type_of_contributor', '=', obj_tipo_coti.id),
                 ('contributor_subtype', '=', obj_subtipo_coti.id)], limit=1)
            #Obtener entidades del empleado
            entity_eps = False
            entity_pension = False
            entity_ccf = False
            entity_arp = False

            for entity in item.employee_id.social_security_entities:
                if entity.contrib_id.type_entities == 'eps': # SALUD 
                    entity_eps = entity.partner_id
                if entity.contrib_id.type_entities == 'pension': # Pension
                    entity_pension = entity.partner_id
                if entity.contrib_id.type_entities == 'caja': # Caja de compensación
                    entity_ccf = entity.partner_id
                if entity.contrib_id.type_entities == 'riesgo': # ARP
                    entity_arp = entity.partner_id

            if obj_parameterization_contributors.liquidates_eps_company or obj_parameterization_contributors.liquidated_eps_employee:
                if not entity_eps or not entity_eps.code_pila_eps:
                    raise ValidationError(_('El empleado '+item.employee_id.name+' no tiene EPS o falta configurar código PILA, por favor verificar.'))
            if obj_parameterization_contributors.liquidated_company_pension or obj_parameterization_contributors.liquidate_employee_pension or obj_parameterization_contributors.liquidates_solidarity_fund:
                if (not entity_pension or not entity_pension.code_pila_eps) and item.contract_id.contract_type != 'aprendizaje' and obj_subtipo_coti.not_contribute_pension == False:
                    raise ValidationError(_('El empleado '+item.employee_id.name+' no tiene entidad de pensión o falta configurar código PILA, por favor verificar.'))
            if obj_parameterization_contributors.liquidated_compensation_fund:
                if (not entity_ccf or not entity_ccf.code_pila_ccf) and item.contract_id.contract_type != 'aprendizaje':
                    raise ValidationError(_('El empleado '+item.employee_id.name+' no tiene caja de compensación o falta configurar código PILA, por favor verificar.'))

            #-------------Inf. Basica
            cSecuencia = right('00000'+str(cant_detalle),5)
            switch_cTipIdTercero = {
                '11': 'RC',
                '12': 'TI',
                '13': 'CC',
                '22': 'CE',
                '31': 'NI',
                '41': 'PA',
                'PE': 'PT',
                'PT': 'PT'
            }
            if item.nValorUPC > 0 and item.dependent_upc_id:
                cTipIdTercero = switch_cTipIdTercero.get(item.dependent_upc_id.z_document_type, '/')
                cNumIdTercero = left(item.dependent_upc_id.z_vat + 16 * ' ', 16)
                cNombreEmpleado = item.dependent_upc_id.name
            else:
                cTipIdTercero = switch_cTipIdTercero.get(item.employee_id.address_home_id.x_document_type, '/')
                #if item.employee_id.permit_no:
                #    cNumIdTercero = left(item.employee_id.permit_no+16*' ',16)
                #else:
                cNumIdTercero = left(item.employee_id.identification_id+16*' ',16)
                cNombreEmpleado = item.employee_id.name
            if cTipIdTercero == '/':
                raise ValidationError(_('El tipo de documento del empleado ' + item.employee_id.name + ' es invalido, por favor verificar.'))
            if not obj_tipo_coti.code:
                raise ValidationError(_('El empleado '+item.employee_id.name+' no tiene tipo de cotizante, por favor verificar.'))           
            cTipoCotizante = right('00'+obj_tipo_coti.code,2)
            cSubtipoCotizante = right('00'+obj_subtipo_coti.code,2) if obj_subtipo_coti.code else '00'
            cExtranjeroNoObligadoPension = 'X' if item.employee_id.extranjero == True and cTipIdTercero in ('CE','PA','CD','SC') else ' '
            cResidenteExterior = 'X' if item.employee_id.residente == True and cTipIdTercero in ('CC','TI') else ' '
            cCodUbiLaboral = right('00000'+entity_ccf.partner_id.x_city.code,5) if entity_ccf and entity_ccf.partner_id.x_city.code else right('00000'+item.employee_id.address_home_id.x_city.code,5)            
            #Obtener nombre
            array_NombreCompleto = cNombreEmpleado.split(' ')            
            cPrimerApellido = ' '*20
            cSegundoApellido = ' '*30
            cPrimerNombre = ' '*20
            cSegundoNombre = ' '*30

            if len(array_NombreCompleto) == 2:
                cont = 1
                for name in array_NombreCompleto:
                    cPrimerApellido = name if cont == 1 else cPrimerApellido
                    cPrimerNombre = name if cont == 2 else cPrimerNombre
                    cont += 1
            if len(array_NombreCompleto) == 3:
                cont = 1
                for name in array_NombreCompleto:
                    cPrimerApellido = name if cont == 1 else cPrimerApellido
                    cSegundoApellido = name if cont == 2 else cSegundoApellido
                    cPrimerNombre = name if cont == 3 else cPrimerNombre
                    cont += 1
            if len(array_NombreCompleto) == 4:
                cont = 1
                for name in array_NombreCompleto:
                    cPrimerApellido = name if cont == 1 else cPrimerApellido
                    cSegundoApellido = name if cont == 2 else cSegundoApellido
                    cPrimerNombre = name if cont == 3 else cPrimerNombre
                    cSegundoNombre = name if cont == 4 else cSegundoNombre
                    cont += 1
            if len(array_NombreCompleto) >= 5:
                cont = 1
                for name in array_NombreCompleto:
                    cPrimerApellido = name if cont == 1 else cPrimerApellido
                    cSegundoApellido = name if cont == 2 else cSegundoApellido
                    cPrimerNombre = name if cont == 3 else cPrimerNombre
                    cSegundoNombre = name if cont == 4 else cSegundoNombre
                    cSegundoNombre = cSegundoNombre+' '+name if cont >= 5 else cSegundoNombre
                    cont += 1

            if item.nValorUPC > 0 and item.dependent_upc_id:
                cPrimerApellido = left(cPrimerApellido + ' ' * 20,20)
                cSegundoApellido = left(cSegundoApellido + ' ' * 30,30)
                cPrimerNombre = left(cPrimerNombre + ' ' * 20,20)
                cSegundoNombre = left(cSegundoNombre + ' ' * 30,30)
            else:
                cPrimerApellido = left(cPrimerApellido+' '*20,20) if not item.employee_id.address_home_id.x_first_lastname else left(item.employee_id.address_home_id.x_first_lastname+' '*20,20)
                cSegundoApellido = left(cSegundoApellido+' '*30,30) if not item.employee_id.address_home_id.x_second_lastname else left(item.employee_id.address_home_id.x_second_lastname+' '*30,30)
                cPrimerNombre = left(cPrimerNombre+' '*20,20) if not item.employee_id.address_home_id.x_first_name else left(item.employee_id.address_home_id.x_first_name+' '*20,20)
                cSegundoNombre = left(cSegundoNombre+' '*30,30) if not item.employee_id.address_home_id.x_second_name else left(item.employee_id.address_home_id.x_second_name+' '*30,30)

            #Concatenar detalle primera parte
            part_line_one = '%s%s%s%s%s%s%s%s%s%s%s%s%s' % (cTipoRegistro,cSecuencia,cTipIdTercero,cNumIdTercero,cTipoCotizante,cSubtipoCotizante,cExtranjeroNoObligadoPension,cResidenteExterior,cCodUbiLaboral,cPrimerApellido,cSegundoApellido,cPrimerNombre,cSegundoNombre)

            #-------------Novedades
            cIngreso = 'X' if item.nIngreso and item.nDiasLiquidados > 0 else ' '
            cRetiro = 'X' if item.nRetiro and item.nDiasLiquidados > 0 else ' '
            
            obj_entities_history = self.env['hr.contract.setting.history'].search([('employee_id','=',item.employee_id.id),('date_history','>=',date_start),('date_history','<=',date_end),('is_transfer','=',True)])

            entity_eps_history = False
            entity_pension_history = False            

            for entity_h in obj_entities_history:
                if entity_h.contrib_id.type_entities == 'eps': # SALUD 
                    entity_eps_history = entity_h.partner_id
                if entity_h.contrib_id.type_entities == 'pension': # Pension
                    entity_pension_history = entity_h.partner_id

            cTDE = ' '
            cTAE = 'X' if entity_eps_history and item.nDiasLiquidados > 0 else ' '
            cTDP = ' ' 
            cTAP = 'X' if entity_pension_history and item.nDiasLiquidados > 0 else ' '
            obj_change_wage = self.env['hr.contract.change.wage'].search([('contract_id','=',item.contract_id.id),('date_start','!=',False),('date_start','>=',date_start),('date_start','<=',date_end)],limit=1)
            cVSP = 'X' if len(obj_change_wage) > 0 and item.nDiasLiquidados > 0 and cIngreso != 'X' else ' '
            cVSP = ' ' if obj_tipo_coti.code == '51' else cVSP
            cCorrecciones = ' '
            cVST = 'X' if item.nValorBaseSalud > math.ceil((item.nSueldo/30)*item.nDiasLiquidados) and item.nDiasLiquidados > 0 and cTipoCotizante not in ('12','19') and cVSP != 'X' else ' '
            cVST = ' ' if obj_tipo_coti.code == '51' else cVST
            
            cSLN = 'X' if item.nDiasLicencia > 0 else ' '
            cIGE = 'X' if item.nDiasIncapacidadEPS > 0 else ' '
            cLMA = 'X' if item.nDiasMaternidad > 0 else ' '
            cVAC = 'X' if item.nDiasVacaciones > 0 else 'L' if item.nDiasLicenciaRenumerada > 0 else ' '
            cAVP = 'X' if item.nDiasLiquidados > 0 and item.cAVP and item.nAporteVoluntarioPension > 0 else ' '
            cVCT = ' '
            IRL = right('00'+str(item.nDiasIncapacidadARP),2)


            #Concatenar detalle segunda parte
            part_line_two = '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s' % (cIngreso,cRetiro,cTDE,cTAE,cTDP,cTAP,cVSP,cCorrecciones,cVST,cSLN,cIGE,cLMA,cVAC,cAVP,cVCT,IRL)

            #-----------------Valores Parte 1
            if obj_parameterization_contributors.liquidated_company_pension or obj_parameterization_contributors.liquidate_employee_pension or obj_parameterization_contributors.liquidates_solidarity_fund:
                if item.nDiasLiquidados > 0:
                    cCodigoEntidadFondoPension = left(entity_pension_history.code_pila_eps+' '*6,6) if entity_pension_history else left(entity_pension.code_pila_eps+' '*6 if entity_pension else ' '*6,6)
                    cCodigoEntidadFondoPensionTraslado = left(entity_pension.code_pila_eps+' '*6 if entity_pension else ' '*6,6) if entity_pension_history else ' '*6
                else:
                    cCodigoEntidadFondoPension = left(entity_pension.code_pila_eps + ' ' * 6 if entity_pension else ' ' * 6, 6)
                    cCodigoEntidadFondoPensionTraslado = ' ' * 6
                if obj_subtipo_coti.not_contribute_pension != True:
                    cDiasCotizadosPension = '00' if item.nValorBaseFondoPension <= 0 else right('00' + str(
                        item.nDiasLiquidados + item.nDiasVacaciones + item.nDiasIncapacidadEPS + item.nDiasLicencia + item.nDiasLicenciaRenumerada + item.nDiasMaternidad + item.nDiasIncapacidadARP),2)
                else:
                    cDiasCotizadosPension = '00'
            else:
                cCodigoEntidadFondoPension = ' '*6
                cCodigoEntidadFondoPensionTraslado = ' '*6
                cDiasCotizadosPension = '00'
            if obj_parameterization_contributors.liquidates_eps_company or obj_parameterization_contributors.liquidated_eps_employee:
                if item.nDiasLiquidados > 0:
                    cCodigoEntidadEPS = left(entity_eps_history.code_pila_eps+' '*6,6) if entity_eps_history else left(entity_eps.code_pila_eps+' '*6,6)
                    cCodigoEntidadEPSTraslado = left(entity_eps.code_pila_eps + ' ' * 6,6) if entity_eps_history else ' ' * 6
                else:
                    cCodigoEntidadEPS = left(entity_eps.code_pila_eps+' '*6,6)
                    cCodigoEntidadEPSTraslado = ' ' * 6
                if item.nValorUPC > 0 and item.dependent_upc_id:
                    cCodigoEntidadEPS = ' ' * 6
                    cCodigoEntidadEPSTraslado = ' ' * 6
                    cDiasCotizadosSalud = '30'
                else:
                    cDiasCotizadosSalud = '00' if item.nValorBaseSalud <= 0 else right('00' + str(
                        item.nDiasLiquidados + item.nDiasVacaciones + item.nDiasIncapacidadEPS + item.nDiasLicencia + item.nDiasLicenciaRenumerada + item.nDiasMaternidad + item.nDiasIncapacidadARP),2)
            else:
                cCodigoEntidadEPS = ' ' * 6
                cCodigoEntidadEPSTraslado = ' ' * 6
                cDiasCotizadosSalud = '00'
            if obj_parameterization_contributors.liquidated_compensation_fund:
                cCodigoEntidadCCF = left(entity_ccf.code_pila_ccf+' '*6 if entity_ccf else ' '*6,6)
                cDiasCotizadosCajaCom = '00' if item.nValorBaseCajaCom <= 0 else right('00' + str(
                    item.nDiasLiquidados + item.nDiasVacaciones + item.nDiasIncapacidadEPS + item.nDiasLicencia + item.nDiasLicenciaRenumerada + item.nDiasMaternidad + item.nDiasIncapacidadARP),2)
            else:
                cCodigoEntidadCCF = ' ' * 6
                cDiasCotizadosCajaCom = '00'

            cDiasCotizadosARP = '00' if item.nValorBaseARP <= 0 else right( '00' + str( item.nDiasLiquidados + item.nDiasVacaciones + item.nDiasIncapacidadEPS + item.nDiasLicencia + item.nDiasLicenciaRenumerada + item.nDiasMaternidad + item.nDiasIncapacidadARP), 2 )
            cDiasCotizadosARP = cDiasCotizadosARP if cTipoCotizante != '51' else '30' # "Número de días cotizados a Riesgos Laborales" se reportará 30 días. Cotizante 51

            if item.nValorUPC > 0 and item.dependent_upc_id:
                cSalarioBasico = '0'*9
                cSalarioIntegral = ' '
            else:
                cSalarioBasico = right('0'*9+ str(item.nSueldo if item.nSueldo>=annual_parameters.smmlv_monthly else annual_parameters.smmlv_monthly).split('.')[0],9)
                cSalarioIntegral = 'V' if item.contract_id.modality_salary not in ['basico', 'sostenimiento'] else (' ' if item.employee_id.contract_id.contract_type == 'aprendizaje' else 'F')
                cSalarioIntegral = cSalarioIntegral if item.contract_id.modality_salary != 'integral' else 'X'
                cSalarioIntegral = ' ' if obj_tipo_coti.code == '51' else cSalarioIntegral

            if obj_parameterization_contributors.liquidated_company_pension or obj_parameterization_contributors.liquidate_employee_pension or obj_parameterization_contributors.liquidates_solidarity_fund:
                cIBCPension = right('0'*9+str(item.nValorBaseFondoPension).split('.')[0],9)
            else:
                cIBCPension = '0' * 9
            cIBCSalud = right('0'*9+str(item.nValorBaseSalud).split('.')[0],9)
            cIBCARP = right('0'*9+str(item.nValorBaseARP).split('.')[0],9)
            cIBCCajaCom = right('0'*9+str(item.nValorBaseCajaCom).split('.')[0],9)

            part_line_three = '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s' % (cCodigoEntidadFondoPension,cCodigoEntidadFondoPensionTraslado,cCodigoEntidadEPS,cCodigoEntidadEPSTraslado,cCodigoEntidadCCF,cDiasCotizadosPension,cDiasCotizadosSalud,cDiasCotizadosARP,cDiasCotizadosCajaCom,cSalarioBasico,cSalarioIntegral,cIBCPension,cIBCSalud,cIBCARP,cIBCCajaCom)

            #-----------------Valores Parte 2
            if obj_parameterization_contributors.liquidated_company_pension or obj_parameterization_contributors.liquidate_employee_pension or obj_parameterization_contributors.liquidates_solidarity_fund:
                cTarifaPension = left(str((item.nPorcAportePensionEmpleado + item.nPorcAportePensionEmpresa) / 100 ) + '0'*7, 7 )

                cValorAportePension = right('0'*9+str(roundup100(item.nValorPensionEmpresa + item.nValorPensionEmpleado)).split('.')[0],9)
                cAporteVoluntarioPension = right('0'*9+str(roundup100(item.nAporteVoluntarioPension)).split('.')[0],9) if item.nDiasLiquidados > 0 and item.cAVP and item.nAporteVoluntarioPension > 0 else '0'*9
                cCotizacionVoluntariaEmpresaPension = '0'*9

                cValorAportePensionTotal = right('0'*9+str(roundup100(item.nValorPensionEmpresa + item.nValorPensionEmpleado + item.nAporteVoluntarioPension)).split('.')[0],9)

                cValorFondoSolidaridad = right('0'*9+str(item.nValorFondoSolidaridad).split('.')[0],9)
                cValorFondoSubsistencia = right('0'*9+str(item.nValorFondoSubsistencia).split('.')[0],9)
                cValorRetenidoAportesVoluntarios = '0'*9
            else:
                cTarifaPension = '0'*7
                cValorAportePension = '0'*9
                cAporteVoluntarioPension = '0' * 9
                cCotizacionVoluntariaEmpresaPension = '0' * 9
                cValorAportePensionTotal = '0'*9
                cValorFondoSolidaridad = '0' * 9
                cValorFondoSubsistencia = '0' * 9
                cValorRetenidoAportesVoluntarios = '0' * 9

            cTarifaSalud = left(str( (item.nPorcAporteSaludEmpleado + item.nPorcAporteSaludEmpresa ) / 100 ) +'0'*7, 7 )
            cValorAporteSalud = right('0'*9+str(roundup100(item.nValorSaludEmpresa + item.nValorSaludEmpleado)).split('.')[0], 9 )
            cValorUPC = right('0'*9+str(item.nValorUPC).split('.')[0],9)

            cNumeroAutorizacionIncapacidad = ' '*15
            cValorIncapacidad = '0'*9
            cNumeroAutorizacionMaternidad = ' '*15
            cValorMaternidad = '0'*9

            part_line_four = '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s' % (cTarifaPension,cValorAportePension,cAporteVoluntarioPension,cCotizacionVoluntariaEmpresaPension,cValorAportePensionTotal,cValorFondoSolidaridad,cValorFondoSubsistencia,cValorRetenidoAportesVoluntarios,cTarifaSalud,cValorAporteSalud,cValorUPC,cNumeroAutorizacionIncapacidad,cValorIncapacidad,cNumeroAutorizacionMaternidad,cValorMaternidad)

            #-----------------Valores Parte 3
            cTarifaARP = left(str(( item.nPorcAporteARP ) / 100 )+'0'*9,9)
            cCentroTrabajo = right('0'*9+str(item.employee_id.work_center_social_security_id.code),9) if item.employee_id.work_center_social_security_id else '0'*9
            cValorARP = right('0'*9+str(item.nValorARP).split('.')[0], 9 )
            cTarifaCCF = left(str(( item.nPorcAporteCajaCom ) / 100 ) + '0'*7, 7 )
            cValorCajaCom = right('0'*9+str(item.nValorCajaCom).split('.')[0], 9 )
            cTarifaSENA = left(str(( item.nPorcAporteSENA ) / 100 ) + '0'*7, 7 )
            cValorSENA = right('0'*9+str(item.nValorSENA).split('.')[0], 9 )            
            cTarifaICBF = left(str(( item.nPorcAporteICBF ) / 100 ) + '0'*7, 7 )
            cValorICBF = right('0'*9+str(item.nValorICBF).split('.')[0], 9 )
            cTarifaESAP = '0.' + '0'*5
            cValorESAP = '0'*9
            cTarifaMEN = '0.' + '0'*5
            cValorMEN = '0'*9
            if item.nValorUPC > 0 and item.dependent_upc_id:
                cTipIdTerceroCotizantePrincipal = switch_cTipIdTercero.get(item.employee_id.address_home_id.x_document_type, '/')
                cNumIdTerceroCotizantePrincipal = left(item.employee_id.identification_id + 16 * ' ', 16)
                cIdentificacionCotizantePrincipal = cTipIdTerceroCotizantePrincipal+cNumIdTerceroCotizantePrincipal
            else:
                cIdentificacionCotizantePrincipal = ' '*18
            cExonerado1607 = 'S' if item.cExonerado1607 else 'N'
            cExonerado1607 = 'N' if obj_tipo_coti.code == '51' else cExonerado1607
            cExonerado1607 = 'N' if item.nValorUPC > 0 and item.dependent_upc_id else cExonerado1607

            cCodigoEntidadARP = left(self.company_id.entity_arp_id.code_pila_eps+' '*6,6) if not entity_arp or not entity_arp.code_pila_eps else left(entity_arp.code_pila_eps+' '*6,6)
            if (not item.TerceroARP and item.contract_id.contract_type == 'aprendizaje') or (item.nValorUPC > 0 and item.dependent_upc_id):
                cCodigoEntidadARP = ' ' * 6

            if item.nValorUPC > 0 and item.dependent_upc_id:
                cNivelRiesgo = ' '
            else:
                cNivelRiesgo = '1' if not item.contract_id.risk_id.code else right(item.contract_id.risk_id.code,1)
            cIndicadorTarifaEspecial = ' '

            part_line_five = '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s' % (cTarifaARP,cCentroTrabajo,cValorARP,cTarifaCCF,cValorCajaCom,cTarifaSENA,cValorSENA,cTarifaICBF,cValorICBF,cTarifaESAP,cValorESAP,cTarifaMEN,cValorMEN,cIdentificacionCotizantePrincipal,cExonerado1607,cCodigoEntidadARP,cNivelRiesgo,cIndicadorTarifaEspecial)

            #------Fechas
            cFechaIngreso = item.contract_id.date_start.strftime('%Y-%m-%d') if item.nIngreso and item.nDiasLiquidados > 0  else ' '*10
            if not item.contract_id.retirement_date:
                cFechaRetiro = item.contract_id.date_end.strftime('%Y-%m-%d') if item.nRetiro and item.nDiasLiquidados > 0 else ' ' * 10
            else:
                cFechaRetiro = item.contract_id.retirement_date.strftime('%Y-%m-%d') if item.nRetiro and item.nDiasLiquidados > 0  else ' '*10
            cFechaInicioVSP = obj_change_wage.date_start.strftime('%Y-%m-%d') if len(obj_change_wage) > 0 and item.nDiasLiquidados > 0 else ' '*10
            cFechaInicioVSP = ' '*10 if obj_tipo_coti.code == '51' else cFechaInicioVSP
            cFechaInicioSLN = item.dFechaInicioSLN.strftime('%Y-%m-%d') if item.dFechaInicioSLN else ' '*10
            cFechaFinSLN = item.dFechaFinSLN.strftime('%Y-%m-%d') if item.dFechaFinSLN else ' '*10
            cFechaInicioIGE = item.dFechaInicioIGE.strftime('%Y-%m-%d') if item.dFechaInicioIGE else ' '*10
            cFechaFinIGE = item.dFechaFinIGE.strftime('%Y-%m-%d') if item.dFechaFinIGE else ' '*10
            cFechaInicioLMA = item.dFechaInicioLMA.strftime('%Y-%m-%d') if item.dFechaInicioLMA else ' '*10
            cFechaFinLMA = item.dFechaFinLMA.strftime('%Y-%m-%d') if item.dFechaFinLMA else ' '*10
            cFechaInicioVACLR = item.dFechaInicioVACLR.strftime('%Y-%m-%d') if item.dFechaInicioVACLR else ' '*10
            cFechaFinVACLR = item.dFechaFinVACLR.strftime('%Y-%m-%d') if item.dFechaFinVACLR else ' '*10
            cFechaInicioVCT = item.dFechaInicioVCT.strftime('%Y-%m-%d') if item.dFechaInicioVCT else ' '*10
            cFechaFinVCT = item.dFechaFinVCT.strftime('%Y-%m-%d') if item.dFechaFinVCT else ' '*10
            cFechaInicioIRL = item.dFechaInicioIRL.strftime('%Y-%m-%d') if item.dFechaInicioIRL else ' '*10
            cFechaFinIRL = item.dFechaFinIRL.strftime('%Y-%m-%d') if item.dFechaFinIRL else ' '*10
            cIBCOtrosParafiscales = right('0'*9+str(item.nValorBaseSENA).split('.')[0],9)
            cNumeroHorasLaboradas = right('000'+str(item.nNumeroHorasLaboradas),3)
            cFechaRadicaciónExterior = item.employee_id.date_of_residence_abroad.strftime('%Y-%m-%d') if cResidenteExterior == 'X' and item.employee_id.date_of_residence_abroad else ' '*10
            cActividadEconomicaNivelRiesgo = right(
                '0000000' + item.contract_id.z_economic_activity_level_risk_id.z_risk_class_id.code + item.contract_id.z_economic_activity_level_risk_id.z_code_ciiu_id.code + item.contract_id.z_economic_activity_level_risk_id.z_code,
                7) if item.contract_id.z_economic_activity_level_risk_id else '0' * 7

            part_line_six = '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s' % (cFechaIngreso,cFechaRetiro,cFechaInicioVSP,cFechaInicioSLN,cFechaFinSLN,cFechaInicioIGE,cFechaFinIGE,cFechaInicioLMA,cFechaFinLMA,cFechaInicioVACLR,cFechaFinVACLR,cFechaInicioVCT,cFechaFinVCT,cFechaInicioIRL,cFechaFinIRL,cIBCOtrosParafiscales,cNumeroHorasLaboradas,cFechaRadicaciónExterior,cActividadEconomicaNivelRiesgo)

            #Concatenar detalle total
            part_line = '%s%s%s%s%s%s' % (part_line_one,part_line_two,part_line_three,part_line_four,part_line_five,part_line_six)

            if cant_detalle == 1:
                detalle_part = part_line
            else:
                detalle_part = detalle_part +'\n'+ part_line

            cant_detalle += 1
            nValorNomina += item.nValorBaseCajaCom 

        #Reemplazar valores del encabezado
        valor_total = str(nValorNomina).split(".") # Eliminar decimales
        encab_part = encab_part.replace("nValorNomina", right('0'*12+str(valor_total[0]),12))

        #Unir Encabezado y Detalle
        content_txt = encab_part +'\n'+ detalle_part 
        #Reemplazar la tecla Ñ por N
        content_txt = content_txt.replace("Ñ",'N')

        #Crear archivo
        if self.presentation_form != 'U':
            if self.work_center_social_security_id:
                filename= 'MedioMagneticoSeguridadSocial'+cPeriodoPagoSalud+'-'+self.branch_social_security_id.name+'-'+self.work_center_social_security_id.name+'.txt'    
            else:
                filename= 'MedioMagneticoSeguridadSocial'+cPeriodoPagoSalud+'-'+self.branch_social_security_id.name+'.txt'    
        else:
            filename= 'MedioMagneticoSeguridadSocial'+cPeriodoPagoSalud+'.txt'    
            
        self.write({
            'txt_file': base64.encodebytes((content_txt).encode()),
            'txt_file_name': filename,
        })   

        #Descargar archivo plano
        action = {
                    'name': 'MedioMagneticoSeguridadSocial',
                    'type': 'ir.actions.act_url',
                    'url': "web/content/?model=hr.payroll.social.security&id=" + str(self.id) + "&filename_field=txt_file_name&field=txt_file&download=true&filename=" + self.txt_file_name,
                    'target': 'self',
                }
        return action