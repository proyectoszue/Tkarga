from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone

import base64
import io
import xlsxwriter


class hr_vacation_book(models.TransientModel):
    _name = "hr.vacation.book"
    _description = "Libro de vacaciones"

    z_provisions_id = fields.Many2one('hr.executing.provisions', 'Periodo', required=True)
    final_year = fields.Integer(related='z_provisions_id.year', string='Año', store=True)
    final_month = fields.Selection(related='z_provisions_id.month', string='Mes', store=True)
    employee = fields.Many2many('hr.employee', string='Empleado')
    version = fields.Many2many('hr.version', string='Contrato')
    branch = fields.Many2many('zue.res.branch', string='Sucursal',
                              domain=lambda self: [('id', 'in', self.env.user.branch_ids.ids)])
    analytic_account = fields.Many2many('account.analytic.account', string='Cuenta Analítica')

    excel_file = fields.Binary(string='Reporte libro de vacaciones')
    excel_file_name = fields.Char(string='Filename Reporte libro de vacaciones')

    def generate_excel(self):
        # Periodo
        date_from = f'{str(self.final_year)}-{str(self.final_month)}-01'
        date_initial = datetime.strptime(date_from, '%Y-%m-%d').date()
        date_from = str(date_initial)
        final_year = self.final_year if self.final_month != '12' else self.final_year + 1
        final_month = int(self.final_month) + 1 if self.final_month != '12' else 1
        date_to = f'{str(final_year)}-{str(final_month)}-01'
        date_end = (datetime.strptime(date_to,'%Y-%m-%d') - timedelta(days=1)).date()
        date_to = str(date_end)
        # Filtro compañia
        query_where = f"where b.id = {self.env.company.id} "
        # Filtro Empleado
        str_ids_employee = ''
        for i in self.employee:
            str_ids_employee = str(i.id) if str_ids_employee == '' else str_ids_employee + ',' + str(i.id)
        if str_ids_employee != '':
            query_where = query_where + f"and a.id in ({str_ids_employee}) "
        # Filtro Contratos
        str_ids_version = ''
        for i in self.version:
            str_ids_version = str(i.id) if str_ids_version == '' else str_ids_version + ',' + str(i.id)
        if str_ids_version != '':
            query_where = query_where + f"and hc.id in ({str_ids_version}) "
        # Filtro Sucursal
        str_ids_branch = ''
        for i in self.branch:
            str_ids_branch = str(i.id) if str_ids_branch == '' else str_ids_branch + ',' + str(i.id)
        if str_ids_branch == '' and len(self.env.user.branch_ids.ids) > 0:
            for i in self.env.user.branch_ids.ids:
                str_ids_branch = str(i) if str_ids_branch == '' else str_ids_branch + ',' + str(i)
        if str_ids_branch != '':
            query_where = query_where + f"and d.id in ({str_ids_branch}) "
        # Filtro Cuenta analitica
        str_ids_analytic = ''
        for i in self.analytic_account:
            str_ids_analytic = str(i.id) if str_ids_analytic == '' else str_ids_analytic + ',' + str(i.id)
        if str_ids_analytic != '':
            query_where = query_where + f"and f.id in ({str_ids_analytic}) "
    # ----------------------------------Ejecutar consulta
        query_report = f'''
                        select distinct hc.identification_id as cedula,a."name" as empleado,b."name" as compania, 
                                coalesce(c."name",'') as ubicacion_laboral,coalesce(d."name",'') as sucursal, coalesce(e."name"->>'en_US','') as departamento,
              	                coalesce(f."name"->>'en_US','') as cuenta_analitica, coalesce(p.value_wage,hc.wage) as salario,hc.contract_date_start as fecha_ingreso,
                                hc.retirement_date as fecha_retiro,
                                0 as dias_laborados,
                                -- Se toman los días de la provision para restarlos con el calculo del reporte
                                coalesce(p."time",0) as dias_pagados, 
                                0 as dias_disfrutados,0 as dias_remunerados,
                                0 as valor_dias_disfrutados, 0 as valor_dias_remunerados,                       
                                0 as dias_adeudados, 0 dias_vac_pendientes, coalesce(p.current_payable_value,0) as valor_a_pagar                             
                        from hr_employee as a 
                        inner join res_company as b on a.company_id = b.id
                        inner join hr_version as hc on a.id = hc.employee_id and hc.active = true and hc.contract_date_start <= '{date_to}'
                                                and (hc.contract_date_end is null or ((hc.retirement_date >= '{date_from}' and hc.retirement_date <= '{date_to}') or (hc.retirement_date >= '{date_to}')))
                        left join res_partner as c on hc.address_id = c.id
                        left join zue_res_branch as d on a.branch_id = d.id
                        left join hr_department as e on hc.department_id = e.id 
                        left join account_analytic_account as f on hc.analytic_distribution = to_jsonb(json_build_object(f.id, 100))
                        --Provision
                        left join ( 
                                    select c.employee_id,c.version_id,c.value_wage,c.value_base,c."time",c.value_balance,c.value_payments,c.amount,c.current_payable_value 
                                    from 
                                    (
                                        select max(date_end) as max_date_provision,company_id
                                        from hr_executing_provisions where date_end <= '{date_to}' and company_id  = {self.env.company.id}
                                        group by company_id
                                    ) as a
                                    inner join hr_executing_provisions as b on a.max_date_provision = b.date_end and a.company_id = b.company_id
                                    inner join hr_executing_provisions_details as c on b.id = c.executing_provisions_id and c.provision = 'vacaciones'
                        ) as p on a.id = p.employee_id and hc.id = p.version_id
                        {query_where}
                        order by a."name",b."name"
                    '''

        self.env.cr.execute(query_report)
        result_query = self.env.cr.dictfetchall()
        # Generar EXCEL
        filename = 'Reporte libro de vacaciones'
        stream = io.BytesIO()
        book = xlsxwriter.Workbook(stream, {'in_memory': True})
        # Agregar textos al excel
        text_company = self.env.company.name
        text_title = 'Informe libro de vacaciones'
        text_dates = 'Fecha de corte %s' % (date_to)
        text_generate = 'Informe generado el %s' % (datetime.now(timezone(self.env.user.tz)))
        cell_format_title = book.add_format({'bold': True, 'align': 'left'})
        cell_format_title.set_font_name('Calibri')
        cell_format_title.set_font_size(15)
        cell_format_title.set_bottom(5)
        cell_format_title.set_bottom_color('#1F497D')
        cell_format_title.set_font_color('#1F497D')
        cell_format_text_generate = book.add_format({'bold': False, 'align': 'left'})
        cell_format_text_generate.set_font_name('Calibri')
        cell_format_text_generate.set_font_size(10)
        cell_format_text_generate.set_bottom(5)
        cell_format_text_generate.set_bottom_color('#1F497D')
        cell_format_text_generate.set_font_color('#1F497D')
        # Formato para fechas
        date_format = book.add_format({'num_format': 'dd/mm/yyyy'})

        #----------------------------------Hoja 1 - Libro de vacaciones

        # Columnas
        columns = ['Cédula', 'Nombres y Apellidos', 'Compañía', 'Ubicación laboral', 'Seccional', 'Departamento',
                   'Cuenta analítica','Salario Base', 'Fecha Ingreso', 'Fecha Retiro','Días Laborados','Días Pagados',
                   'Dias de vacaciones disfrutados','Días de vacaciones remunerados',
                   'Valor días de vacaciones Disfrutados','Valor días de vacaciones remunerados',
                   'Dias laborados que se adeudan','Dias de vacaciones pendientes','Valor a Pagar']
        sheet = book.add_worksheet('Libro de vacaciones')
        sheet.merge_range('A1:S1', text_company, cell_format_title)
        sheet.merge_range('A2:S2', text_title, cell_format_title)
        sheet.merge_range('A3:S3', text_dates, cell_format_title)
        sheet.merge_range('A4:S4', text_generate, cell_format_text_generate)
        # Agregar columnas
        aument_columns = 0
        for column in columns:
            sheet.write(4, aument_columns, column)
            aument_columns = aument_columns + 1
        # Agregar query
        aument_columns = 0
        aument_rows = 5
        for query in result_query:
            date_start = ''
            date_end_employee = date_end
            employee_id,identification_id = 0,0
            days_labor,days_unpaid_absences,days_paid,days_paid_money,days_enjoy = 0,0,0,0,0
            value_business_days,money_value = 0,0
            version_id = 0
            date_vacaciones = None
            date_liquidacion = date_end
            for row in query.values():
                width = len(str(row)) + 10
                # La columna 0 es Id Empleado por ende se guarda su valor en la variable employee_id
                identification_id = row if aument_columns == 0 else identification_id
                employee_id = self.env['hr.employee'].search([('identification_id','=',identification_id)],limit=1).id
                # La columna 8 y 9 es Fecha Ingreso y Retiro por ende se guarda su valor en la variable date_start y date_end
                date_start = row if aument_columns == 8 else date_start
                date_end_employee = row if aument_columns == 9 and str(type(row)).find('date') > -1 else date_end_employee
                # Obtener contrato del empleado
                if employee_id and aument_columns == 0:
                    obj_version = self.env['hr.version'].search([
                        ('employee_id', '=', employee_id),
                        ('active', '=', True),
                        ('date_start', '<=', date_end),
                        '|', '|',
                        ('retirement_date', '=' ,False),
                        '&', ('retirement_date', '>=', date_initial), ('retirement_date', '<=', date_end),
                        ('retirement_date', '>=', date_end)
                    ], limit=1)
                    version_id = obj_version.id if obj_version else 0
                obj_hr_vacation = self.env['hr.vacation'].search([('employee_id', '=', employee_id), ('departure_date', '<=', date_end_employee), ('version_id.contract_date_end', '=', False)])
                # Obtener fecha final de causación más reciente
                latest_final_accrual_date = max(obj_hr_vacation.mapped('final_accrual_date')) + timedelta(days=1) if len(obj_hr_vacation) > 0 else date_start
                try:
                    days_labor_final_accrual_date = self.dias360(latest_final_accrual_date, date_end_employee)
                except:
                    days_labor_final_accrual_date = 0
                if aument_columns <= 9:
                    if str(type(row)).find('date') > -1:
                        sheet.write_datetime(aument_rows, aument_columns, row, date_format)
                    else:
                        sheet.write(aument_rows, aument_columns, row)
                else:
                    if aument_columns == 10: # Dias Laborados
                        days_labor = self.dias360(date_start,date_end_employee)
                        sheet.write(aument_rows, aument_columns, days_labor)
                    elif aument_columns == 11: # Días Totales Pagados
                        days_paid_money = sum([i.units_of_money for i in obj_hr_vacation])
                        days_enjoy = sum([i.business_units for i in obj_hr_vacation])
                        days_paid = ((days_paid_money+days_enjoy)*360)/15
                        sheet.write(aument_rows, aument_columns,days_paid)
                    elif aument_columns == 12: # Días Disfrutados
                        sheet.write(aument_rows, aument_columns,days_enjoy)
                    elif aument_columns == 13: # Dias remunerados
                        sheet.write(aument_rows, aument_columns,days_paid_money)
                    elif aument_columns == 14: # Valor Dias disfrutados
                        value_business_days = sum([i.value_business_days for i in
                                               self.env['hr.vacation'].search([('employee_id', '=', employee_id),
                                                                               ('departure_date', '<=', date_end_employee)])])
                        sheet.write(aument_rows, aument_columns,value_business_days)
                    elif aument_columns == 15: # Valor Dias remunerados
                        money_value = sum([i.money_value for i in
                                                   self.env['hr.vacation'].search([('employee_id', '=', employee_id),
                                                                                   ('departure_date', '<=', date_end_employee)])])
                        sheet.write(aument_rows, aument_columns,money_value)
                    elif aument_columns == 16: # Días laborados que se adeudan - Replicar cálculo de time de provisiones
                        # Obtener date_vacaciones igual que en provisiones
                        if employee_id and version_id:
                            obj_version = self.env['hr.version'].browse(version_id)
                            date_vacaciones = obj_version.date_start
                            retirement_date = obj_version.retirement_date
                            # Buscar vacaciones igual que en provisiones
                            if retirement_date == False:
                                obj_vacation = self.env['hr.vacation'].search([
                                    ('employee_id', '=', employee_id),
                                    ('version_id', '=', version_id),
                                    ('departure_date', '<=', date_end)
                                ])
                            else:
                                if retirement_date >= date_end:
                                    obj_vacation = self.env['hr.vacation'].search([
                                        ('employee_id', '=', employee_id),
                                        ('version_id', '=', version_id),
                                        ('departure_date', '<=', date_end)
                                    ])
                                else:
                                    obj_vacation = self.env['hr.vacation'].search([
                                        ('employee_id', '=', employee_id),
                                        ('version_id', '=', version_id),
                                        ('departure_date', '<=', retirement_date)
                                    ])
                            if obj_vacation:
                                for history in sorted(obj_vacation, key=lambda x: x.final_accrual_date):
                                    if history.leave_id:
                                        if history.leave_id.holiday_status_id.unpaid_absences == False:
                                            date_vacaciones = history.final_accrual_date + timedelta(days=1) if history.final_accrual_date > date_vacaciones else date_vacaciones
                                    else:
                                        date_vacaciones = history.final_accrual_date + timedelta(days=1) if history.final_accrual_date > date_vacaciones else date_vacaciones

                            # Ajustar date_vacaciones y date_liquidacion igual que en provisiones
                            date_end_without_31 = date_end - timedelta(days=1) if date_end.day == 31 else date_end
                            if retirement_date == False:
                                date_liquidacion = date_end_without_31
                            else:
                                date_liquidacion = date_end_without_31 if retirement_date >= date_end_without_31 else retirement_date
                                date_vacaciones = date_vacaciones if retirement_date >= date_vacaciones else retirement_date

                            # Calcular dias_trabajados y dias_ausencias igual que en provisiones
                            dias_trabajados = obj_version.dias360(date_vacaciones, date_liquidacion)
                            dias_ausencias = sum([i.number_of_days for i in self.env['hr.leave'].search([
                                ('date_from', '>=', date_vacaciones),
                                ('date_to', '<=', date_liquidacion),
                                ('state', '=', 'validate'),
                                ('employee_id', '=', employee_id),
                                ('unpaid_absences', '=', True)
                            ])])
                            dias_ausencias += sum([i.days for i in self.env['hr.absence.history'].search([
                                ('star_date', '>=', date_vacaciones),
                                ('end_date', '<=', date_liquidacion),
                                ('employee_id', '=', employee_id),
                                ('leave_type_id.unpaid_absences', '=', True)
                            ])])
                            # Calcular dias_liquidacion (que es el campo time en provisiones)
                            dias_liquidacion = dias_trabajados - dias_ausencias
                            sheet.write(aument_rows, aument_columns, dias_liquidacion)
                        else:
                            sheet.write(aument_rows, aument_columns, days_labor_final_accrual_date)
                    elif aument_columns == 17: # Dias de vacaciones pendientes
                        #sheet.write(aument_rows, aument_columns,(((days_labor-days_paid)*15)/360))
                        sheet.write(aument_rows, aument_columns, (((days_labor_final_accrual_date) * 15) / 360))
                    elif aument_columns == 18: # Valor a pagar
                        sheet.write(aument_rows, aument_columns,row)
                # Ajustar tamaño columna
                sheet.set_column(aument_columns, aument_columns, width)
                aument_columns = aument_columns + 1
            aument_rows = aument_rows + 1
            aument_columns = 0

        # Convertir en tabla
        array_header_table = []
        for i in columns:
            dict = {'header': i}
            array_header_table.append(dict)

        sheet.add_table(4, 0, aument_rows-1, len(columns)-1, {'style': 'Table Style Medium 2', 'columns': array_header_table})

        #----------------------------------Hoja 2 - Detalle del libro de vacaciones
        query_report = f'''
                        select distinct hc.identification_id as cedula,a."name" as empleado,b."name" as compania, 
                            hv.initial_accrual_date as causacion_inicial,hv.final_accrual_date as causacion_final,
                            hv.departure_date as fecha_salida,hv.return_date as fecha_regreso,
                            sum(coalesce(hv.business_units,0)) as dias_habiles,sum(coalesce(hv.value_business_days,0)) as valor_dias_habiles,
                            sum(coalesce(hv.holiday_units,0)) as dias_festivas,sum(coalesce(hv.holiday_value,0)) as valor_dias_festivos,
                            sum(coalesce(hv.units_of_money,0)) as dias_dinero,sum(coalesce(hv.money_value,0)) as valor_dias_dinero
                        from hr_employee as a 
                        inner join res_company as b on a.company_id = b.id
                        inner join hr_version as hc on a.id = hc.employee_id and hc.active = true and hc.contract_date_start <= '{date_to}'
                                                and (hc.contract_date_end is null or ((hc.retirement_date >= '{date_from}' and hc.retirement_date <= '{date_to}') or (hc.retirement_date >= '{date_to}')))
                        inner join hr_vacation as hv on a.id = hv.employee_id and hc.id = hv.version_id and hv.departure_date <= '{date_to}' 
                        left join res_partner as c on hc.address_id = c.id
                        left join zue_res_branch as d on a.branch_id = d.id
                        left join hr_department as e on hc.department_id = e.id 
                        left join account_analytic_account as f on hc.analytic_distribution = to_jsonb(json_build_object(f.id, 100))
                        {query_where} 
                        group by hc.identification_id,a."name",b."name",hv.initial_accrual_date,
                        hv.final_accrual_date,hv.departure_date,hv.return_date
                        order by a."name",b."name"
                    '''
        self.env.cr.execute(query_report)
        result_query = self.env.cr.dictfetchall()
        # Columnas
        columns = ['Cédula', 'Nombres y Apellidos', 'Compañía',
                   'Causación Inicial', 'Causación Final', 'Fecha Salida', 'Fecha Regreso', 'Días hábiles', 'Valor días hábiles',
                   'Días festivos', 'Valor días festivos','Días en dinero', 'Valor días en dinero']
        sheet_detail = book.add_worksheet('Detalle')
        # Agregar columnas
        aument_columns = 0
        for column in columns:
            sheet_detail.write(0, aument_columns, column)
            aument_columns = aument_columns + 1
        # Agregar query
        aument_columns = 0
        aument_rows = 1
        for query in result_query:
            for row in query.values():
                width = len(str(row)) + 10
                if str(type(row)).find('date') > -1:
                    sheet_detail.write_datetime(aument_rows, aument_columns, row, date_format)
                else:
                    sheet_detail.write(aument_rows, aument_columns, row)
                # Ajustar tamaño columna
                sheet_detail.set_column(aument_columns, aument_columns, width)
                aument_columns = aument_columns + 1
            aument_rows = aument_rows + 1
            aument_columns = 0

        # Convertir en tabla
        array_header_table = []
        for i in columns:
            dict = {'header': i}
            array_header_table.append(dict)

        sheet_detail.add_table(0, 0, aument_rows, len(columns) - 1,
                        {'style': 'Table Style Medium 2', 'columns': array_header_table})



        # Guadar Excel
        book.close()

        self.write({
            'excel_file': base64.encodebytes(stream.getvalue()),
            'excel_file_name': filename,
        })

        action = {
            'name': 'Reporte Libro de Vacaciones',
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=hr.vacation.book&id=" + str(
                self.id) + "&filename_field=excel_file_name&field=excel_file&download=true&filename=" + self.excel_file_name,
            'target': 'self',
        }
        return action

