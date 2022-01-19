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

    final_year = fields.Integer('Año', required=True)
    final_month = fields.Selection([('1', 'Enero'),
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
    employee = fields.Many2many('hr.employee', string='Empleado')
    contract = fields.Many2many('hr.contract', string='Contrato')
    branch = fields.Many2many('zue.res.branch', string='Sucursal',
                              domain=lambda self: [('id', 'in', self.env.user.branch_ids.ids)])
    analytic_account = fields.Many2many('account.analytic.account', string='Cuenta Analítica')

    excel_file = fields.Binary(string='Reporte libro de vacaciones')
    excel_file_name = fields.Char(string='Filename Reporte libro de vacaciones')

    def generate_excel(self):
        # Periodo
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
        str_ids_contract = ''
        for i in self.contract:
            str_ids_contract = str(i.id) if str_ids_contract == '' else str_ids_contract + ',' + str(i.id)
        if str_ids_contract != '':
            query_where = query_where + f"and hc.id in ({str_ids_contract}) "
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
                        select distinct a.identification_id as cedula,a."name" as empleado,b."name" as compania, 
                                coalesce(c."name",'') as ubicacion_laboral,coalesce(d."name",'') as sucursal, coalesce(e."name",'') as departamento,
                                coalesce(f."name",'') as cuenta_analitica, hc.wage as salario,hc.date_start as fecha_ingreso,
                                0 as dias_laborados,0 as dias_ausencias,0 as dias_laborados_reales,0 as dias_derecho,0 as dias_pagados, 0 as dias_adeudados
                        from hr_employee as a 
                        inner join res_company as b on a.company_id = b.id
                        inner join hr_contract as hc on a.id = hc.employee_id and hc.state = 'open'
                        left join res_partner as c on a.address_id = c.id
                        left join zue_res_branch as d on a.branch_id = d.id
                        left join hr_department as e on a.department_id = e.id 
                        left join account_analytic_account as f on a.analytic_account_id = f.id   
                        {query_where}
                        order by a."name",b."name"
                    '''

        self._cr.execute(query_report)
        result_query = self._cr.dictfetchall()
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
                   'Cuenta analítica','Salario Base', 'Fecha Ingreso', 'Días Laborados', 'Días Ausencias','Días Laborados Neto',
                   'Días de vacaciones a los que tiene derecho','Días Totales Pagados', 'Días de Vacaciones Adeudados']
        sheet = book.add_worksheet('Libro de vacaciones')
        sheet.merge_range('A1:O1', text_company, cell_format_title)
        sheet.merge_range('A2:O2', text_title, cell_format_title)
        sheet.merge_range('A3:O3', text_dates, cell_format_title)
        sheet.merge_range('A4:O4', text_generate, cell_format_text_generate)
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
            employee_id,identification_id = 0,0
            days_labor,days_unpaid_absences,days_paid = 0,0,0
            for row in query.values():
                width = len(str(row)) + 10
                # La columna 0 es Id Empleado por ende se guarda su valor en la variable employee_id
                identification_id = row if aument_columns == 0 else identification_id
                employee_id = self.env['hr.employee'].search([('identification_id','=',identification_id)],limit=1).id
                # La columna 8 es Fecha Ingreso por ende se guarda su valor en la variable date_start
                date_start = row if aument_columns == 8 else date_start
                if aument_columns <= 8:
                    if str(type(row)).find('date') > -1:
                        sheet.write_datetime(aument_rows, aument_columns, row, date_format)
                    else:
                        sheet.write(aument_rows, aument_columns, row)
                else:
                    if aument_columns == 9: # Dias Laborados
                        days_labor = self.dias360(date_start,date_end)
                        sheet.write(aument_rows, aument_columns, days_labor)
                    elif aument_columns == 10: # Dias Ausencia
                        days_unpaid_absences = sum([i.number_of_days for i in self.env['hr.leave'].search(
                            [('date_from', '>=', date_start), ('date_from', '<=', date_end),
                             ('state', '=', 'validate'), ('employee_id', '=', employee_id),
                             ('unpaid_absences', '=', True)])])
                        days_unpaid_absences += sum([i.days for i in self.env['hr.absence.history'].search(
                            [('star_date', '>=', date_start), ('star_date', '<=', date_end),
                             ('employee_id', '=', employee_id), ('leave_type_id.unpaid_absences', '=', True)])])
                        sheet.write(aument_rows, aument_columns, days_unpaid_absences)
                    elif aument_columns == 11: # Días Laborados Neto
                        sheet.write(aument_rows, aument_columns,(days_labor-days_unpaid_absences))
                    elif aument_columns == 12: # Días de vacaciones a los que tiene derecho
                        sheet.write(aument_rows, aument_columns,(((days_labor - days_unpaid_absences) * 15) / 360))
                    elif aument_columns == 13: # Días Totales Pagados
                        days_paid = sum([i.business_units + i.units_of_money for i in
                                         self.env['hr.vacation'].search([('employee_id', '=', employee_id),('departure_date','<=',date_end)])])
                        sheet.write(aument_rows, aument_columns,days_paid)
                    elif aument_columns == 14: # Días de Vacaciones Adeudados
                        sheet.write(aument_rows, aument_columns,((((days_labor - days_unpaid_absences) * 15) / 360)-days_paid))
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

        sheet.add_table(4, 0, aument_rows, len(columns)-1, {'style': 'Table Style Medium 2', 'columns': array_header_table})

        #----------------------------------Hoja 2 - Detalle del libro de vacaciones
        query_report = f'''
                        select distinct a.identification_id as cedula,a."name" as empleado,b."name" as compania, 
                            hv.initial_accrual_date as causacion_inicial,hv.final_accrual_date as causacion_final,
                            hv.departure_date as fecha_salida,hv.return_date as fecha_regreso,
                            sum(coalesce(hv.business_units,0)) as dias_habiles,sum(coalesce(hv.value_business_days,0)) as valor_dias_habiles,
                            sum(coalesce(hv.holiday_units,0)) as dias_festivas,sum(coalesce(hv.holiday_value,0)) as valor_dias_festivos,
                            sum(coalesce(hv.units_of_money,0)) as dias_dinero,sum(coalesce(hv.money_value,0)) as valor_dias_dinero
                        from hr_employee as a 
                        inner join res_company as b on a.company_id = b.id
                        inner join hr_contract as hc on a.id = hc.employee_id and hc.state = 'open'
                        inner join hr_vacation as hv on a.id = hv.employee_id and hc.id = hv.contract_id and hv.departure_date <= '{date_to}' 
                        left join res_partner as c on a.address_id = c.id
                        left join zue_res_branch as d on a.branch_id = d.id
                        left join hr_department as e on a.department_id = e.id 
                        left join account_analytic_account as f on a.analytic_account_id = f.id
                        {query_where} 
                        group by a.identification_id,a."name",b."name",hv.initial_accrual_date,
                        hv.final_accrual_date,hv.departure_date,hv.return_date
                        order by a."name",b."name"
                    '''
        self._cr.execute(query_report)
        result_query = self._cr.dictfetchall()
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
            'excel_file': base64.encodestring(stream.getvalue()),
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

