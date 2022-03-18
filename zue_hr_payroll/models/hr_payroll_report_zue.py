# -*- coding: utf-8 -*-
from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from pytz import timezone

import pandas as pd
import numpy as np 
import base64
import io
import xlsxwriter

class HrPayrollReportZueFilter(models.TransientModel):
    _name = "hr.payroll.report.zue.filter"
    _description = "Filtros - Informe Liquidación"
    
    payslip_ids = fields.Many2many('hr.payslip.run',string='Lotes de nómina', domain=[('state', '!=', 'draft')])    
    liquidations_ids= fields.Many2many('hr.payslip', string='Liquidaciones individuales', domain=[('payslip_run_id', '=', False)])
    show_date_of_entry = fields.Boolean(string="Fecha de Ingreso", default= True)
    show_job_placement = fields.Boolean(string="Ubicación Laboral", default= True)
    show_sectional = fields.Boolean(string="Seccional", default= True)
    show_department = fields.Boolean(string="Departamento", default= True)
    show_analytical_account = fields.Boolean(string="Cuenta Analítica", default= True)
    show_job = fields.Boolean(string="Cargo", default= True)
    show_sena_code = fields.Boolean(string="Código SENA", default= True)
    show_basic_salary = fields.Boolean(string="Salario Base", default= True)
    excel_file = fields.Binary('Excel file')
    excel_file_name = fields.Char('Excel name', size=64)

    def name_get(self):
        result = []
        for record in self:            
            result.append((record.id, "Informe de nómina"))
        return result

    def show_all_fields(self):
        self.show_date_of_entry = True
        self.show_job_placement = True
        self.show_sectional = True
        self.show_department = True
        self.show_analytical_account = True
        self.show_job = True
        self.show_sena_code = True
        self.show_basic_salary = True
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.payroll.report.zue.filter',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def not_show_all_fields(self):
        self.show_date_of_entry = False
        self.show_job_placement = False
        self.show_sectional = False
        self.show_department = False
        self.show_analytical_account = False
        self.show_job = False
        self.show_sena_code = False
        self.show_basic_salary = False
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.payroll.report.zue.filter',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def generate_excel(self):
        obj_payslips = self.env['hr.payslip']
        min_date = ''
        max_date = ''

        if len(self.payslip_ids) == 0 and len(self.liquidations_ids) == 0:
            raise ValidationError(_('Debe seleccionar algún filtro.'))

        #Obtener las liquidaciones de los lotes seleccionados
        if len(self.payslip_ids) > 0:            
            ids = self.payslip_ids.ids
            for payslip in self.payslip_ids:
                if min_date == '' and max_date == '':
                    min_date = payslip.date_start
                    max_date = payslip.date_end                
                else: 
                    if payslip.date_start < min_date:
                        min_date = payslip.date_start
                    if payslip.date_end > max_date:
                        max_date = payslip.date_end

            obj_payslips += self.env['hr.payslip'].search([('payslip_run_id','in',ids)])
        
        #Obtener las liquidaciones seleccionadas
        if len(self.liquidations_ids) > 0:
            obj_payslips += self.liquidations_ids

            for payslip in self.liquidations_ids:
                if min_date == '' and max_date == '':
                    min_date = payslip.date_from
                    max_date = payslip.date_to               
                else: 
                    if payslip.date_from < min_date:
                        min_date = payslip.date_from
                    if payslip.date_to > max_date:
                        max_date = payslip.date_to

        #Obtener ids a filtrar
        str_ids = ''
        for i in obj_payslips:
            if str_ids == '':
                str_ids = str(i.id)
            else:
                str_ids = str_ids+','+str(i.id)

        min_date = min_date.strftime('%Y-%m-%d')
        max_date = max_date.strftime('%Y-%m-%d')

        query_novedades = '''
            Select c.identification_id as "Identificación", c.name as "Empleado", COALESCE(a.name,b.name) as "Novedad",
                    Case When row_number() over(partition by c.identification_id) = max_item Then 1 else 0 end as "EsUltimo"
            From hr_leave as a
            Inner Join hr_leave_type as b on a.holiday_status_id = b.id
            Inner Join hr_employee as c on a.employee_id = c.id
            Inner Join (Select max(item) as max_item,identification_id
                        From (
                            Select row_number() over(partition by c.identification_id) as item,
                                c.identification_id, COALESCE(a.name,b.name) as novedad
                            From hr_leave as a
                            Inner Join hr_leave_type as b on a.holiday_status_id = b.id
                            Inner Join hr_employee as c on a.employee_id = c.id
                            Where a.state='validate' 
                                    and ((a.request_date_from >= '%s' and a.request_date_from <= '%s') or (a.request_date_to >= '%s' and a.request_date_to <= '%s'))
                        )as A
                        group by identification_id
                    ) as max_nov on c.identification_id = max_nov.identification_id
            Where a.state='validate' 
                  and ((a.request_date_from >= '%s' and a.request_date_from <= '%s') or (a.request_date_to >= '%s' and a.request_date_to <= '%s'))
        ''' % (min_date,max_date,min_date,max_date,min_date,max_date,min_date,max_date)

        query_days = '''
                    Select  c.item as "Id Interno",
                    COALESCE(c.identification_id,'') as "Identificación",COALESCE(c.name,'') as "Empleado",COALESCE(d.date_start,'1900-01-01') as "Fecha Ingreso",
                    COALESCE(e.name,'') as "Seccional",COALESCE(f.name,'') as "Cuenta Analítica",
                    COALESCE(g.name,'') as "Cargo",COALESCE(d.code_sena,'') as "Código SENA",COALESCE(rp.name,'') as "Ubicación Laboral",COALESCE(dt.name,'') as "Departamento",
                    COALESCE(d.wage,0) as "Salario Base",'' as "Novedades",
                    COALESCE(wt.name,'') as "Regla Salarial",COALESCE(wt.name,'') as "Reglas Salariales + Entidad",
                    'Días' as "Categoría",0 as "Secuencia",COALESCE(Sum(b.number_of_days),0) as "Monto"
            From hr_payslip as a 
            --Info Empleado
            Inner Join (Select distinct row_number() over(order by a.name) as item,
                        a.id,identification_id,a.name,a.branch_id,a.analytic_account_id,a.job_id,
                        address_id,a.department_id
                        From hr_employee as a) as c on a.employee_id = c.id
            Inner Join hr_contract as d on a.contract_id = d.id
            Inner Join hr_payslip_worked_days as b on a.id = b.payslip_id
            inner join hr_work_entry_type as wt on b.work_entry_type_id = wt.id
            Left join zue_res_branch as e on c.branch_id = e.id
            Left join account_analytic_account as f on c.analytic_account_id = f.id
            Left join hr_job g on c.job_id = g.id
            Left Join hr_department dt on c.department_id = dt.id
            Left Join res_partner rp on c.address_id = rp.id
            Where a.id in (%s)     
            Group By c.item,c.identification_id,c.name,d.date_start,e.name,
                        f.name,g.name,d.code_sena,rp.name,dt.name,d.wage,wt.name
        ''' % (str_ids)

        query_amount_rules ='''
            Select  c.item as "Id Interno",
                    COALESCE(c.identification_id,'') as "Identificación",COALESCE(c.name,'') as "Empleado",COALESCE(d.date_start,'1900-01-01') as "Fecha Ingreso",
                    COALESCE(e.name,'') as "Seccional",COALESCE(f.name,'') as "Cuenta Analítica",
                    COALESCE(g.name,'') as "Cargo",COALESCE(d.code_sena,'') as "Código SENA",COALESCE(rp.name,'') as "Ubicación Laboral",COALESCE(dt.name,'') as "Departamento",
                    COALESCE(d.wage,0) as "Salario Base",'' as "Novedades",
                    COALESCE(b.name,'') as "Regla Salarial",COALESCE(b.name,'') ||' '|| case when hc.code = 'SSOCIAL' then '' else COALESCE(COALESCE(rp_et.x_business_name,rp_et.name),'') end as "Reglas Salariales + Entidad",
                    COALESCE(hc.name,'') as "Categoría",COALESCE(b.sequence,0) as "Secuencia",COALESCE(Sum(b.total),0) as "Monto"
            From hr_payslip as a 
            --Info Empleado
            Inner Join (Select distinct row_number() over(order by a.name) as item,
                        a.id,identification_id,a.name,a.branch_id,a.analytic_account_id,a.job_id,
                        address_id,a.department_id
                        From hr_employee as a) as c on a.employee_id = c.id
            Inner Join hr_contract as d on a.contract_id = d.id
            Left Join hr_payslip_line as b on a.id = b.slip_id
            Left Join hr_salary_rule_category as hc on b.category_id = hc.id
            Left join zue_res_branch as e on c.branch_id = e.id
            Left join account_analytic_account as f on c.analytic_account_id = f.id
            Left join hr_job g on c.job_id = g.id
            Left Join hr_department dt on c.department_id = dt.id
            Left Join res_partner rp on c.address_id = rp.id
            --Entidad
            Left Join hr_employee_entities et on b.entity_id = et.id
            Left Join res_partner rp_et on et.partner_id = rp_et.id            
            Where a.id in (%s)     
            Group By c.item,c.identification_id,c.name,d.date_start,e.name,
                        f.name,g.name,d.code_sena,rp.name,dt.name,d.wage,b.name,hc.code,
                        rp_et.x_business_name,rp_et.name,hc.name,b.sequence
        ''' % (str_ids)

        query_quantity_bases_days = '''
            Select c.item as "Id Interno",
                COALESCE(c.identification_id,'') as "Identificación",COALESCE(c.name,'') as "Empleado",COALESCE(d.date_start,'1900-01-01') as "Fecha Ingreso",
                COALESCE(e.name,'') as "Seccional",COALESCE(f.name,'') as "Cuenta Analítica",
                COALESCE(g.name,'') as "Cargo",COALESCE(d.code_sena,'') as "Código SENA",COALESCE(rp.name,'') as "Ubicación Laboral",COALESCE(dt.name,'') as "Departamento",
                COALESCE(d.wage,0) as "Salario Base",'' as "Novedades",
                b.name as "Regla Salarial",REPLACE_TITULO,
                hc.name as "Categoría",b.sequence as "Secuencia",REPLACE_VALUE
            From hr_payslip as a 
            Inner Join hr_payslip_line as b on a.id = b.slip_id                
            Inner Join hr_salary_rule_category as hc on b.category_id = hc.id REPLACE_FILTER_RULE_CATEGORY
            --Info Empleado
            Inner Join (Select distinct row_number() over(order by a.name) as item,
                        a.id,identification_id,a.name,a.branch_id,a.analytic_account_id,a.job_id,
                        address_id,a.department_id
                        From hr_employee as a) as c on a.employee_id = c.id
            Inner Join hr_contract as d on a.contract_id = d.id
            Left join zue_res_branch as e on c.branch_id = e.id
            Left join account_analytic_account as f on c.analytic_account_id = f.id
            Left join hr_job g on c.job_id = g.id
            Left Join hr_department dt on c.department_id = dt.id
            Left Join res_partner rp on c.address_id = rp.id
            --Entidad
            Left Join hr_employee_entities et on b.entity_id = et.id
            Left Join res_partner rp_et on et.partner_id = rp_et.id            
            Where a.id in (%s)
            Group By c.item,c.identification_id,c.name,d.date_start,e.name,
                        f.name,g.name,d.code_sena,rp.name,dt.name,d.wage,b.name,hc.code,
                        rp_et.x_business_name,rp_et.name,hc.name,b.sequence
        ''' % (str_ids)

        query = f"""
                    Select * from
                    (
                        --DIAS INVOLUCRADOS EN LA LIQUIDACIÓN
                        {query_days}
                        Union
                        --VALORES LIQUIDADOS
                        {query_amount_rules}
                        Union 
                        -- CANTIDAD SOLO PARA HORAS EXTRAS Y PRESTACIONES SOCIALES (CESANTIAS & PRIMA)
                        {query_quantity_bases_days.replace('REPLACE_TITULO', ''' 'Cantidad de ' || b.name as "Reglas Salariales + Entidad" ''').replace('REPLACE_VALUE', 'COALESCE(Sum(b.quantity),0) as "Cantidad"').replace('REPLACE_FILTER_RULE_CATEGORY',''' and hc.code in ('HEYREC','PRESTACIONES_SOCIALES') ''')}
        				Union 
        				-- BASE SOLO PARA PRESTACIONES SOCIALES (CESANTIAS & PRIMA)
        				{query_quantity_bases_days.replace('REPLACE_TITULO', ''' 'Base de ' || b.name as "Reglas Salariales + Entidad" ''').replace('REPLACE_VALUE', 'COALESCE(Sum(b.amount_base),0) as "Base"').replace('REPLACE_FILTER_RULE_CATEGORY',''' and hc.code in ('PRESTACIONES_SOCIALES') ''')}
        				Union
        				-- DIAS AUSENCIAS NO REMUNERADOS		
        				{query_quantity_bases_days.replace('REPLACE_TITULO', ''' 'Días Ausencias no remuneradas de ' || b.name as "Reglas Salariales + Entidad" ''').replace('REPLACE_VALUE', 'COALESCE(Sum(b.days_unpaid_absences),0) as "Dias Ausencias no remuneradas"').replace('REPLACE_FILTER_RULE_CATEGORY',''' and b.days_unpaid_absences > 0 ''')}
                    ) as a 
                """
        
        query_totales = '''
            Select 500000 as "Id Interno",'' as "Identificación", '' as "Empleado", '1900-01-01' as "Fecha Ingreso",
                    '' as "Seccional", '' as "Cuenta Analítica",'' as "Cargo",'' as "Código SENA",'' as "Ubicación Laboral",'' as "Departamento",
                    0 as "Salario Base",'' as "Novedades",
                    "Regla Salarial","Reglas Salariales + Entidad","Categoría","Secuencia",Sum("Monto") as "Monto"
            From(
                Select  c.name,wt.name as "Regla Salarial",wt.name as "Reglas Salariales + Entidad",
                        'Días' as "Categoría",0 as "Secuencia",COALESCE(Sum(b.number_of_days),0) as "Monto"
                From hr_payslip as a 
                Inner Join hr_payslip_worked_days as b on a.id = b.payslip_id 
                Inner Join hr_work_entry_type as wt on b.work_entry_type_id = wt.id
                --Info Empleado
                Inner Join hr_employee  as c on a.employee_id = c.id                
                Inner Join hr_contract as d on a.contract_id = d.id
                Where a.id in (%s)
                Group By c.name,wt.name
                Union
                Select  c.name,b.name as "Regla Salarial",b.name ||' '|| case when hc.code = 'SSOCIAL' then '' else COALESCE(COALESCE(rp_et.x_business_name,rp_et.name),'') end as "Reglas Salariales + Entidad",
                        hc.name as "Categoría",b.sequence as "Secuencia",COALESCE(Sum(b.total),0) as "Monto"
                From hr_payslip as a 
                Inner Join hr_payslip_line as b on a.id = b.slip_id
                Inner Join hr_salary_rule_category as hc on b.category_id = hc.id
                --Info Empleado
                Inner Join hr_employee  as c on a.employee_id = c.id                
                Inner Join hr_contract as d on a.contract_id = d.id
                --Entidad
                Left Join hr_employee_entities et on b.entity_id = et.id
                Left Join res_partner rp_et on et.partner_id = rp_et.id
                Where a.id in (%s)
                Group By c.name,b.name,hc.code,rp_et.x_business_name,rp_et.name,hc.name,b.sequence
                Union
                Select c.name,b.name as "Regla Salarial",'Cantidad de ' || b.name as "Reglas Salariales + Entidad",
                       hc.name as "Categoría",b.sequence as "Secuencia",COALESCE(Sum(b.quantity),0) as "Cantidad"
                From hr_payslip as a 
                Inner Join hr_payslip_line as b on a.id = b.slip_id                
                Inner Join hr_salary_rule_category as hc on b.category_id = hc.id and hc.code = 'HEYREC'
                --Info Empleado
                Inner Join hr_employee  as c on a.employee_id = c.id
                Inner Join hr_contract as d on c.id = d.employee_id and d.state = 'open'
                --Entidad
                Left Join hr_employee_entities et on b.entity_id = et.id
                Left Join res_partner rp_et on et.partner_id = rp_et.id 
                Where a.id in (%s)
                Group By c.name,b.name,hc.code,rp_et.x_business_name,rp_et.name,hc.name,b.sequence
            ) as a 
            Group By "Regla Salarial","Reglas Salariales + Entidad","Categoría","Secuencia"
            order by "Id Interno","Empleado","Secuencia"
        ''' % (str_ids,str_ids,str_ids)

        #Finalizar query principal
        query = '''
            %s
            union
            %s
        ''' % (query,query_totales)

        #Ejecutar query principal
        self.env.cr.execute(query)
        result_query = self.env.cr.dictfetchall()

        df_report = pd.DataFrame(result_query)
        
        if len(df_report) == 0:
            raise ValidationError(_('No se ha encontrado información con el lote seleccionado, por favor verificar.'))

        #Ejecutar query de novedades
        self.env.cr.execute(query_novedades)
        result_query_novedades = self.env.cr.dictfetchall()

        df_novedades = pd.DataFrame(result_query_novedades)
        identification = ''
        novedades = ''
        for i,j in df_novedades.iterrows():
            if identification == df_novedades.loc[i,'Identificación']:
                novedades = novedades +' -\r\n '+ df_novedades.loc[i,'Novedad']                
            else:                
                identification = df_novedades.loc[i,'Identificación']
                novedades = df_novedades.loc[i,'Novedad']

            if df_novedades.loc[i,'EsUltimo'] == 1:
                df_report.loc[df_report['Identificación'] == identification, 'Novedades'] = novedades

        columns_index = ['Id Interno', 'Identificación', 'Empleado']
        if self.show_date_of_entry == True:
            columns_index.append('Fecha Ingreso')
        if self.show_job_placement == True:
            columns_index.append('Ubicación Laboral')
        if self.show_sectional == True:
            columns_index.append('Seccional')
        if self.show_department == True:
            columns_index.append('Departamento')
        if self.show_analytical_account == True:
            columns_index.append('Cuenta Analítica')
        if self.show_job == True:
            columns_index.append('Cargo')
        if self.show_sena_code == True:
            columns_index.append('Código SENA')
        if self.show_basic_salary == True:
            columns_index.append('Salario Base')
        columns_index.append('Novedades')

        # Obtener tamaño de las columnas fijas
        column_len = []
        position_initial = 0
        for column_i in columns_index:
            max_len = max([len(str(df_report.loc[i, column_i])) for i,j in df_report.iterrows()])
            if column_i == 'Novedades':
                max_len = 50 if max_len > 50 else max_len
            column_len.append({'position': position_initial,'name_column': column_i,'len_column': max_len})
            position_initial += 1

        #Pivotear consulta final
        pivot_report = pd.pivot_table(df_report, values='Monto', index=columns_index,
                                      columns=['Secuencia', 'Categoría', 'Reglas Salariales + Entidad'], aggfunc=np.sum)
        
        #Obtener titulo y fechas de liquidación
        text_title = 'Informe de Liquidación'
        text_dates = 'Fechas Liquidación: %s a %s' % (min_date,max_date)
        text_generate = 'Informe generado el %s' % (datetime.now(timezone(self.env.user.tz)))
        #Obtener info
        cant_filas = pivot_report.shape[0]+3 # + 3 de los registros pertenencientes al encabezado
        cant_columnas = pivot_report.shape[1]+len(columns_index) # + las columnas fijas
        #Obtener tamaño de las columnas que se crearon con el pivot
        for c in pivot_report.columns:
            column_len.append({'position': position_initial,'name_column': c[2],'len_column': len(str(c[2]))})
            position_initial += 1
        #Crear Excel
        filename = 'Informe Liquidación.xlsx'
        stream = io.BytesIO()
        writer = pd.ExcelWriter(stream, engine='xlsxwriter')
        writer.book.filename = stream
        pivot_report.to_excel(writer, sheet_name='Liquidación')
        worksheet = writer.sheets['Liquidación']
        #Agregar formatos al excel
        cell_format_title = writer.book.add_format({'bold': True, 'align': 'left'})
        cell_format_title.set_font_name('Calibri')
        cell_format_title.set_font_size(15)
        cell_format_title.set_font_color('#1F497D')
        cell_format_text_generate = writer.book.add_format({'bold': False, 'align': 'left'})
        cell_format_text_generate.set_font_name('Calibri')
        cell_format_text_generate.set_font_size(10)
        cell_format_text_generate.set_font_color('#1F497D')
        if len(columns_index)-2 != 2:
            worksheet.merge_range(0,2,0,len(columns_index)-2, text_title, cell_format_title)
            worksheet.merge_range(1,2,1,len(columns_index)-2, text_dates, cell_format_title)
            worksheet.merge_range(2,2,2,len(columns_index)-2, text_generate, cell_format_text_generate)
        else:
            worksheet.write(0, 2, text_title, cell_format_title)
            worksheet.write(1, 2, text_dates, cell_format_title)
            worksheet.write(2, 2, text_generate, cell_format_text_generate)
        if self.env.company.logo:
            logo_company = io.BytesIO(base64.b64decode(self.env.company.logo))
            worksheet.insert_image('A1', "logo_company.png", {'image_data': logo_company,'x_scale': 0.6, 'y_scale': 0.4})
        #Dar tamaño a las columnas
        for size_column in column_len:
            worksheet.set_column(size_column['position'], size_column['position'], size_column['len_column'] + 5)
        #Campos númericos
        #number_format = writer.book.add_format({'num_format': '#,##'})
        #https://xlsxwriter.readthedocs.io/worksheet.html#conditional_format
        #worksheet.conditional_format(3,10,cant_filas,10,
        #                                {'type': 'no_errors',
        #                                'format': number_format})
        #worksheet.conditional_format(3,13,cant_filas,cant_columnas,
        #                                {'type': 'no_errors',
        #                                'format': number_format})
        #Campo de novedades
        cell_format_novedades = writer.book.add_format({'text_wrap': True,'border':1})
        cell_format_novedades.set_font_name('Calibri')
        cell_format_novedades.set_font_size(11)
        worksheet.conditional_format(3,len(columns_index)-1,cant_filas-1,len(columns_index)-1,
                                        {'type': 'no_errors',
                                        'format': cell_format_novedades})  
        #Titulo totales
        cell_format_total = writer.book.add_format({'bold': True,'align':'right','border':1})
        cell_format_total.set_font_name('Calibri')
        cell_format_total.set_font_size(11)
        worksheet.merge_range(cant_filas,0,cant_filas,len(columns_index)-1,'TOTALES',cell_format_total)
        #worksheet.set_column('M:M', 0, None, {'hidden': 1})
        #Guardar excel
        writer.save()

        self.write({
            'excel_file': base64.encodestring(stream.getvalue()),
            'excel_file_name': filename,
        })
        
        action = {
                    'name': filename,
                    'type': 'ir.actions.act_url',
                    'url': "web/content/?model=hr.payroll.report.zue.filter&id=" + str(self.id) + "&filename_field=excel_file_name&field=excel_file&download=true&filename=" + self.excel_file_name,
                    'target': 'self',
                }
        return action
