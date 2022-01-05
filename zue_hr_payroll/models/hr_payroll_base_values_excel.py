from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import base64
import io
import xlsxwriter


class Hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    excel_value_base_file = fields.Binary('Excel Valores base file')
    excel_value_base_file_name = fields.Char('Excel Valores base filename')

    def get_query(self,process,date_start,date_end):
        # formatear fechas
        date_start = str(date_start.year) + '-' + str(date_start.month) + '-' + str(date_start.day)
        date_end = str(date_end.year) + '-' + str(date_end.month) + '-' + str(date_end.day)

        query = """Select hc.name,hp.date_from,COALESCE(sum(pl.total),0) as accumulated, 'Liquidaciones' as origin 
                        From hr_payslip as hp 
                        Inner Join hr_payslip_line as pl on  hp.id = pl.slip_id 
                        Inner Join hr_salary_rule hc on pl.salary_rule_id = hc.id and hc.%s = true
                        Inner Join hr_salary_rule_category hsc on hc.category_id = hsc.id and hsc.code != 'BASIC'
                        WHERE hp.state = 'done' and hp.contract_id = %s
                        AND (hp.date_from between '%s' and '%s'
                            or
                            hp.date_to between '%s' and '%s' )
                        group by hc.name,hp.date_from
                    Union 
                    Select hc.name,pl.date,COALESCE(sum(pl.amount),0) as accumulated, 'Acumulados' as origin
                        From hr_accumulated_payroll as pl
                        Inner Join hr_salary_rule hc on pl.salary_rule_id = hc.id and hc.%s = true
                        Inner Join hr_salary_rule_category hsc on hc.category_id = hsc.id and hsc.code != 'BASIC'
                        WHERE pl.employee_id = %s and pl.date between '%s' and '%s'
                        group by hc.name,pl.date
                """ % (
        process, self.contract_id.id, date_start, date_end, date_start, date_end, process, self.employee_id.id, date_start,
        date_end)

        return query

    def base_values_export_excel(self):
        query_vacaciones = ''
        query_vacaciones_dinero = ''
        query_prima = ''
        query_cesantias = ''

        if self.struct_id.process == 'vacaciones':
            date_start = self.date_from - relativedelta(years=1)
            date_end = self.date_from
            query_vacaciones = self.get_query('base_vacaciones',date_start,date_end)
            query_vacaciones_dinero = self.get_query('base_vacaciones_dinero', date_start, date_end)
        elif self.struct_id.process == 'prima':
            date_start = self.date_from
            date_end = self.date_to
            query_prima = self.get_query('base_prima', date_start, date_end)
        elif self.struct_id.process == 'cesantias' or self.struct_id.process == 'intereses_cesantias':
            date_start = self.date_from
            date_end = self.date_to
            query_cesantias = self.get_query('base_cesantias', date_start, date_end)
        elif self.struct_id.process == 'contrato':
            date_start = self.date_vacaciones
            date_end = self.date_liquidacion
            query_vacaciones_dinero = self.get_query('base_vacaciones_dinero', date_start, date_end)
            date_start = self.date_prima
            date_end = self.date_liquidacion
            query_prima = self.get_query('base_prima', date_start, date_end)
            date_start = self.date_cesantias
            date_end = self.date_liquidacion
            query_cesantias = self.get_query('base_cesantias', date_start, date_end)
        else:
            raise ValidationError(_('Esta estructura salarial no posee exportación de valores base a excel.'))

        #Generar EXCEL
        filename = f'Acumulados valores variables - {self.employee_id.name}.xlsx'
        stream = io.BytesIO()
        book = xlsxwriter.Workbook(stream, {'in_memory': True})

        if query_vacaciones != '':
            columns = ['Regla Salarial', 'Fecha', 'Valor', 'Origen']
            sheet_vacaciones = book.add_worksheet('VACACIONES DISFRUTADAS')
            # Agregar columnas
            aument_columns = 0
            for columns in columns:
                sheet_vacaciones.write(0, aument_columns, columns)
                aument_columns = aument_columns + 1

            #Agregar Información generada en la consulta
            self._cr.execute(query_vacaciones)
            result_query = self._cr.dictfetchall()
            aument_columns = 0
            aument_rows = 1
            for query in result_query:
                for row in query.values():
                    sheet_vacaciones.write(aument_rows, aument_columns, row)
                    aument_columns = aument_columns + 1
                aument_rows = aument_rows + 1
                aument_columns = 0
        if query_vacaciones_dinero != '':
            columns = ['Regla Salarial', 'Fecha', 'Valor', 'Origen']
            sheet_vacaciones_dinero = book.add_worksheet('VACACIONES REMUNERADAS')
            # Agregar columnas
            aument_columns = 0
            for columns in columns:
                sheet_vacaciones_dinero.write(0, aument_columns, columns)
                aument_columns = aument_columns + 1

            #Agregar Información generada en la consulta
            self._cr.execute(query_vacaciones_dinero)
            result_query = self._cr.dictfetchall()
            aument_columns = 0
            aument_rows = 1
            for query in result_query:
                for row in query.values():
                    sheet_vacaciones_dinero.write(aument_rows, aument_columns, row)
                    aument_columns = aument_columns + 1
                aument_rows = aument_rows + 1
                aument_columns = 0
        if query_prima != '':
            columns = ['Regla Salarial', 'Fecha', 'Valor', 'Origen']
            sheet_prima = book.add_worksheet('PRIMA')
            # Agregar columnas
            aument_columns = 0
            for columns in columns:
                sheet_prima.write(0, aument_columns, columns)
                aument_columns = aument_columns + 1

            #Agregar Información generada en la consulta
            self._cr.execute(query_prima)
            result_query = self._cr.dictfetchall()
            aument_columns = 0
            aument_rows = 1
            for query in result_query:
                for row in query.values():
                    sheet_prima.write(aument_rows, aument_columns, row)
                    aument_columns = aument_columns + 1
                aument_rows = aument_rows + 1
                aument_columns = 0
        if query_cesantias != '':
            columns = ['Regla Salarial', 'Fecha', 'Valor', 'Origen']
            sheet_cesantias = book.add_worksheet('CESANTIAS')
            # Agregar columnas
            aument_columns = 0
            for columns in columns:
                sheet_cesantias.write(0, aument_columns, columns)
                aument_columns = aument_columns + 1

            #Agregar Información generada en la consulta
            self._cr.execute(query_cesantias)
            result_query = self._cr.dictfetchall()
            aument_columns = 0
            aument_rows = 1
            for query in result_query:
                for row in query.values():
                    sheet_cesantias.write(aument_rows, aument_columns, row)
                    aument_columns = aument_columns + 1
                aument_rows = aument_rows + 1
                aument_columns = 0

        book.close()
        self.write({
            'excel_value_base_file': base64.encodestring(stream.getvalue()),
            'excel_value_base_file_name': filename,
        })

        action = {
            'name': 'Export Acumulados variables',
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=hr.payslip&id=" + str(
                self.id) + "&filename_field=excel_value_base_file_name&field=excel_value_base_file&download=true&filename=" + self.excel_value_base_file_name,
            'target': 'self',
        }
        return action



