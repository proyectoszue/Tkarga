from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import base64
import io
import xlsxwriter

from datetime import datetime


class zue_hr_report_leave_vs_work_entry(models.Model):
    _name = 'zue.hr.report.leave.vs.work.entry'
    _description = 'Auditoria ausentismos vs entradas de trabajo'

    excel_file = fields.Binary('Excel file')
    excel_file_name = fields.Char('Excel name')

    def get_query(self):
        query_report = f'''
                    SELECT
                        rc."name" AS company,
                        he."name" AS employee,
                        hlt."name" AS type_leave,
                        hl.request_date_from,
                        hl.request_date_to,
                        COUNT(hwe.date_start) / 2 AS qty_days_without_leave,
                        hc.id as id_contract
                    FROM
                        hr_leave hl
                    INNER JOIN hr_leave_type hlt ON hl.holiday_status_id = hlt.id
                    INNER JOIN hr_employee he ON hl.employee_id = he.id
                    INNER JOIN hr_contract hc ON he.contract_id = hc.id AND hc.state = 'open'
                    INNER JOIN res_company rc ON he.company_id = rc.id and rc.id = {self.env.company.id}
                    LEFT JOIN hr_work_entry hwe ON hl.employee_id = hwe.employee_id
                                                AND DATE(hwe.date_start) >= hl.request_date_from
                                                AND DATE(hwe.date_stop) <= hl.request_date_to
                                                AND hwe.state IN ('draft', 'validated')
                                                AND (hwe.leave_id != hl.id OR hwe.leave_id IS NULL)
                    WHERE
                        hl.state = 'validate'
                    GROUP BY
                        rc."name", he."name", hlt."name", hl.request_date_from, hl.request_date_to, hc.id
                    HAVING
                        COUNT(hwe.date_start) > 0
                    ORDER BY
                        rc."name", hl.request_date_from DESC, he."name"
                    '''

        self._cr.execute(query_report)
        result_query = self._cr.dictfetchall()
        return result_query

    def download_excel(self):
        result_query = self.get_query()

        # Generar EXCEL
        filename = 'Reporte Auditoria ausentismos vs entradas de trabajo'
        stream = io.BytesIO()
        book = xlsxwriter.Workbook(stream, {'in_memory': True})

        # Formato para fechas
        date_format = book.add_format({'num_format': 'dd/mm/yyyy'})

        # Columnas
        columns = ['Compañía', 'Empleado', 'Tipo de ausencia', 'Fecha inicio', 'Fecha Fin', 'Días sin relacionar']
        sheet = book.add_worksheet('Ausencias Vs Entradas')

        # Agregar columnas
        aument_columns = 0
        for column in columns:
            sheet.write(0, aument_columns, column)
            aument_columns = aument_columns + 1

        # Agregar query
        aument_columns = 0
        aument_rows = 1
        for query in result_query:
            for row in query.values():
                if aument_columns <= 5:
                    width = len(str(row)) + 10
                    if str(type(row)).find('date') > -1:
                        sheet.write_datetime(aument_rows, aument_columns, row, date_format)
                    else:
                        sheet.write(aument_rows, aument_columns, row)

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

        sheet.add_table(0, 0, aument_rows - 1, len(columns) - 1,
                        {'style': 'Table Style Medium 2', 'columns': array_header_table})

        # Guadar Excel
        book.close()
        self.write({
            'excel_file': base64.encodebytes(stream.getvalue()),
            'excel_file_name': filename,
        })

        action = {
            'name': 'Reporte Auditoria ausentismos vs entradas de trabajo',
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=zue.hr.report.leave.vs.work.entry&id=" + str(
                self.id) + "&filename_field=excel_file_name&field=excel_file&download=true&filename=" + self.excel_file_name,
            'target': 'self',
        }
        return action

    def solution_report(self):
        try:
            result_query = self.get_query()

            for query in result_query:
                obj_work_entry_refresh = self.env['hr.work.entry.refresh']
                res = obj_work_entry_refresh.create({'date_start':query['request_date_from'],
                                               'date_stop':query['request_date_to'],
                                               'contract_ids':[query['id_contract']]})
                res.refresh_work_entry()
            return True
        except:
            raise ValidationError('Error en el proceso.')
