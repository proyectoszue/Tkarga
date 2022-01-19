# -*- coding: utf-8 -*-

from logging import exception
from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import base64
import io
import xlsxwriter
import math

class hr_payroll_social_security(models.Model):
    _inherit = 'hr.payroll.social.security'

    def get_excel(self):
        filename = 'Seguridad Social Periodo {}-{}.xlsx'.format(self.month, str(self.year))
        stream = io.BytesIO()
        book = xlsxwriter.Workbook(stream, {'in_memory': True})
        sheet = book.add_worksheet('Seguridad Social')

        columns = [
            'Empleado', 'Sucursal', 'Contrato', 'Días liquidados', 'Días incapacidad EPS', 'Días licencia',
            'Días licencia remunerada', 'Días maternidad', 'Días vacaciónes', 'Días incapacidad ARP',
            'Ingreso', 'Retiro', 'Sueldo', 'Tercero EPS', 'Valor base salud', 'Porc. Aporte salud empleados',
            'Valor salud empleado', 'Valor salud empleado nómina', 'Porc. Aporte salud empresa',
            'Valor salud empresa', 'Valor salud total', 'Diferencia salud', 'Tercero pensión',
            'Valor base fondo de pensión', 'Porc. Aporte pensión empleado', 'Valor pensión empleado',
            'Valor pensión empleado nómina', 'Porc. Aporte pensión empresa', 'Valor pensión empresa',
            'Valor pensión total', 'Diferencia pensión', 'Tercero fondo solidaridad',
            'Porc. Fondo solidaridad', 'Valor fondo solidaridad', 'Valor fondo subsistencia', 'Tercero ARP',
            'Valor base ARP', 'Porc. Aporte ARP', 'Valor ARP', 'Exonerado ley 1607',
            'Tercero caja compensación', 'Valor base caja com', 'Porc. Aporte caja com', 'Valor caja com',
            'Tercero SENA', 'Valor base SENA', 'Porc. Aporte SENA', 'Valor SENA',
            'Tercero ICBF', 'Valor base ICBF', 'Porc. Aporte ICBF', 'Valor ICBF', 'Fecha Inicio SLN', 'Fecha Fin SLN',
            'Fecha Inicio IGE', 'Fecha Fin IGE',
            'Fecha Inicio LMA', 'Fecha Fin LMA', 'Fecha Inicio VACLR', 'Fecha Fin VACLR', 'Fecha Inicio VCT',
            'Fecha Fin VCT', 'Fecha Inicio IRL', 'Fecha Fin IRL'
        ]

        # Agregar columnas
        aument_columns = 0
        for columns in columns:
            sheet.write(0, aument_columns, columns)
            aument_columns = aument_columns + 1

        # Agregar valores
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
            'url': "web/content/?model=hr.payroll.social.security&id=" + str(
                self.id) + "&filename_field=excel_file_name&field=excel_file&download=true&filename=" + self.excel_file_name,
            'target': 'self',
        }
        return action

    def get_excel_errors(self):
        filename = 'Seguridad Social Advertencias Periodo {}-{}.xlsx'.format(self.month, str(self.year))
        stream = io.BytesIO()
        book = xlsxwriter.Workbook(stream, {'in_memory': True})
        sheet = book.add_worksheet('Seguridad Social')

        columns = [
            'Empleado', 'Sucursal', 'Advertencia'
        ]

        # Agregar columnas
        aument_columns = 0
        for columns in columns:
            sheet.write(0, aument_columns, columns)
            aument_columns = aument_columns + 1

        # Agregar valores
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
            'url': "web/content/?model=hr.payroll.social.security&id=" + str(
                self.id) + "&filename_field=excel_file_name&field=excel_file&download=true&filename=" + self.excel_file_name,
            'target': 'self',
        }
        return action

    #METODOS REPORTE SEGURIDAD SOCIAL POR TIPO Y ENTIDAD
    def info_totals(self):
        dict_totals = {}
        for record in self:
            total_amount_employees = sum([i.nValorSaludEmpleado+i.nValorPensionEmpleado for i in record.executing_social_security_ids])
            total_amount_company = sum([i.nValorSaludEmpresa+i.nValorPensionEmpresa+i.nValorFondoSolidaridad+i.nValorFondoSubsistencia+i.nValorARP+i.nValorCajaCom+i.nValorSENA+i.nValorICBF for i in record.executing_social_security_ids])
            dict_totals = {'total_employees':len(record.executing_social_security_ids.employee_id),
                           'total_amount_employees': float("{:.2f}".format(total_amount_employees)),
                           'total_amount_company': float("{:.2f}".format(total_amount_company)),
                           'total_amount_final': float("{:.2f}".format(total_amount_employees+total_amount_company))}
        return dict_totals

    def get_info_eps(self):
        lst_eps = []
        for record in self:
            obj_type_eps = self.env['hr.contribution.register'].search([('type_entities','=','eps')],limit=1)
            obj_entities = self.env['hr.employee.entities'].search([('types_entities','in',obj_type_eps.ids)])

            for entity in sorted(obj_entities,key=lambda x: x.partner_id.name):
                info = record.executing_social_security_ids.filtered(lambda x: x.TerceroEPS.id == entity.id and x.nValorSaludEmpleado+x.nValorSaludEmpresa+x.nDiferenciaSalud != 0)
                nValorSaludEmpleadoTotal,nValorSaludEmpresaTotal,nDiferenciaSaludTotal = 0,0,0
                for i in info:
                    nValorSaludEmpleadoTotal += i.nValorSaludEmpleado
                    nValorSaludEmpresaTotal += i.nValorSaludEmpresa
                    nDiferenciaSaludTotal += i.nDiferenciaSalud

                if nValorSaludEmpleadoTotal + nValorSaludEmpresaTotal + nDiferenciaSaludTotal != 0:
                    dict_eps = {'name': entity.partner_id.name,
                                'identifcation': entity.partner_id.vat,
                                'cod_pila': entity.code_pila_eps,
                                'num_employees': len(info.employee_id),
                                'value_employees': float("{:.2f}".format(nValorSaludEmpleadoTotal)),
                                'value_company': float("{:.2f}".format(nValorSaludEmpresaTotal)),
                                'dif_round': float("{:.2f}".format(nDiferenciaSaludTotal)),
                                }
                    lst_eps.append(dict_eps)

        return lst_eps

    def get_info_pension(self):
        lst_eps = []
        for record in self:
            obj_type_eps = self.env['hr.contribution.register'].search([('type_entities','=','pension')],limit=1)
            obj_entities = self.env['hr.employee.entities'].search([('types_entities','in',obj_type_eps.ids)])

            for entity in sorted(obj_entities,key=lambda x: x.partner_id.name):
                info = record.executing_social_security_ids.filtered(lambda x: x.TerceroPension.id == entity.id and x.nValorPensionEmpleado+x.nValorPensionEmpresa+x.nDiferenciaPension != 0)
                nValorPensionEmpleadoTotal,nValorPensionEmpresaTotal,nDiferenciaPensionTotal = 0,0,0
                for i in info:
                    nValorPensionEmpleadoTotal += i.nValorPensionEmpleado
                    nValorPensionEmpresaTotal += i.nValorPensionEmpresa
                    nDiferenciaPensionTotal += i.nDiferenciaPension

                if nValorPensionEmpleadoTotal + nValorPensionEmpresaTotal + nDiferenciaPensionTotal != 0:
                    dict_eps = {'name': entity.partner_id.name,
                                'identifcation': entity.partner_id.vat,
                                'cod_pila': entity.code_pila_eps,
                                'num_employees': len(info.employee_id),
                                'value_employees': float("{:.2f}".format(nValorPensionEmpleadoTotal)),
                                'value_company': float("{:.2f}".format(nValorPensionEmpresaTotal)),
                                'dif_round': float("{:.2f}".format(nDiferenciaPensionTotal)),
                                }
                    lst_eps.append(dict_eps)

        return lst_eps

    def get_info_solidaridad(self):
        lst_eps = []
        for record in self:
            obj_type_eps = self.env['hr.contribution.register'].search([('type_entities','in',['pension', 'solidaridad', 'subsistencia'])],limit=1)
            obj_entities = self.env['hr.employee.entities'].search([('types_entities','in',obj_type_eps.ids)])

            for entity in sorted(obj_entities,key=lambda x: x.partner_id.name):
                info = record.executing_social_security_ids.filtered(lambda x: x.TerceroFondoSolidaridad.id == entity.id and x.nValorFondoSolidaridad+x.nValorFondoSubsistencia != 0)
                nValorFondoSolidaridad,nValorFondoSubsistencia = 0,0
                for i in info:
                    nValorFondoSolidaridad += i.nValorFondoSolidaridad
                    nValorFondoSubsistencia += i.nValorFondoSubsistencia

                if nValorFondoSolidaridad + nValorFondoSubsistencia != 0:
                    dict_eps = {'name': entity.partner_id.name,
                                'identifcation': entity.partner_id.vat,
                                'cod_pila': entity.code_pila_eps,
                                'num_employees': len(info.employee_id),
                                'value_solidaridad': float("{:.2f}".format(nValorFondoSolidaridad+nValorFondoSubsistencia))                                
                                }
                    lst_eps.append(dict_eps)

        return lst_eps

    def get_info_arp(self):
        lst_eps = []
        for record in self:
            obj_type_eps = self.env['hr.contribution.register'].search([('type_entities','=','riesgo')],limit=1)
            obj_entities = self.env['hr.employee.entities'].search([('types_entities','in',obj_type_eps.ids)])

            for entity in sorted(obj_entities,key=lambda x: x.partner_id.name):
                info = record.executing_social_security_ids.filtered(lambda x: x.TerceroARP.id == entity.id and x.nValorARP != 0)
                nValorARP = 0
                for i in info:
                    nValorARP += i.nValorARP

                if nValorARP != 0:
                    dict_eps = {'name': entity.partner_id.name,
                                'identifcation': entity.partner_id.vat,
                                'cod_pila': entity.code_pila_eps,
                                'num_employees': len(info.employee_id),
                                'value_arp': float("{:.2f}".format(nValorARP)),
                                }
                    lst_eps.append(dict_eps)

        return lst_eps

    def get_info_compensacion(self): 
        lst_eps = []
        for record in self:
            obj_type_eps = self.env['hr.contribution.register'].search([('type_entities','=','caja')],limit=1)
            obj_entities = self.env['hr.employee.entities'].search([('types_entities','in',obj_type_eps.ids)])

            for entity in sorted(obj_entities,key=lambda x: x.partner_id.name):
                info = record.executing_social_security_ids.filtered(lambda x: x.TerceroCajaCom.id == entity.id and x.nValorCajaCom != 0)
                nValorCajaCom = 0
                for i in info:
                    nValorCajaCom += i.nValorCajaCom

                if nValorCajaCom != 0:
                    dict_eps = {'name': entity.partner_id.name,
                                'identifcation': entity.partner_id.vat,
                                'cod_pila': entity.code_pila_ccf,
                                'num_employees': len(info.employee_id),
                                'value_cajacom': float("{:.2f}".format(nValorCajaCom)),
                                }
                    lst_eps.append(dict_eps)

        return lst_eps

    def get_info_sena(self): 
        lst_eps = []
        for record in self:
            obj_type_eps = self.env['hr.contribution.register'].search([('type_entities','=','sena')],limit=1)
            obj_entities = self.env['hr.employee.entities'].search([('types_entities','in',obj_type_eps.ids)])

            for entity in sorted(obj_entities,key=lambda x: x.partner_id.name):
                info = record.executing_social_security_ids.filtered(lambda x: x.TerceroSENA.id == entity.id and x.nValorSENA != 0)
                nValorSENA = 0
                for i in info:
                    nValorSENA += i.nValorSENA

                if nValorSENA != 0:
                    dict_eps = {'name': entity.partner_id.name,
                                'identifcation': entity.partner_id.vat,
                                'cod_pila': entity.code_pila_eps,
                                'num_employees': len(info.employee_id),
                                'value_sena': float("{:.2f}".format(nValorSENA)),
                                }
                    lst_eps.append(dict_eps)

        return lst_eps

    def get_info_icbf(self): 
        lst_eps = []
        for record in self:
            obj_type_eps = self.env['hr.contribution.register'].search([('type_entities','=','icbf')],limit=1)
            obj_entities = self.env['hr.employee.entities'].search([('types_entities','in',obj_type_eps.ids)])

            for entity in sorted(obj_entities,key=lambda x: x.partner_id.name):
                info = record.executing_social_security_ids.filtered(lambda x: x.TerceroICBF.id == entity.id and x.nValorICBF != 0)
                nValorICBF = 0
                for i in info:
                    nValorICBF += i.nValorICBF

                if nValorICBF != 0:
                    dict_eps = {'name': entity.partner_id.name,
                                'identifcation': entity.partner_id.vat,
                                'cod_pila': entity.code_pila_eps,
                                'num_employees': len(info.employee_id),
                                'value_icbf': float("{:.2f}".format(nValorICBF)),
                                }
                    lst_eps.append(dict_eps)

        return lst_eps




