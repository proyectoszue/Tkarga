from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from pytz import timezone

import base64
import io
import xlsxwriter


class hr_entities_reports(models.TransientModel):
    _name = "hr.entities.reports"
    _description = 'Entidades del empleado'

    employee = fields.Many2many('hr.employee',string='Empleado')
    # entities = fields.Many2many('hr.employee.entities', string='Entidad')
    # branch = fields.Many2many('zue.res.branch', string='Sucursal')
    #tipo de entidad AQUI
    # analytic_account = fields.Many2many('account.analytic.account', string='Cuenta Analítica')
    #sucursal de de serguridad social
    #centro de trabajo de seguriadad social
    #¿empleados activos o inactivos?
    #check

    excel_file = fields.Binary('Excel')
    excel_file_name = fields.Char('Excel filename')

    def generate_entities_excel(self):
        # ----------------------------------Ejecutar consulta
        query_report = f'''
                                select a."name",c."name",e."name",true as es_actual,'' as nivel_riesgo 
                        from hr_employee as a
                        inner join hr_contract_setting as b on a.id = b.employee_id 
                        inner join hr_contribution_register as c on b.contrib_id = c.id 
                        inner join hr_employee_entities as d on b.partner_id = d.id 
                        inner join res_partner as e on d.partner_id = e.id
                        order by a."name" 
                        '''
        self._cr.execute(query_report)
        result_query = self._cr.dictfetchall()

        # Generar EXCEL
        filename = 'Reporte Entidades por Empleado'
        stream = io.BytesIO()
        book = xlsxwriter.Workbook(stream, {'in_memory': True})

        # Columnas
        columns = ['Empleado', 'entidad', 'sucursusal de seguridad social', 'es actual', 'nivel de riesgo', ]
        sheet = book.add_worksheet('Entidades por empleado')

        # Agregar textos al excel
        text_title = 'Entidades por empleado'
        text_generate = 'Informe generado el %s' % (datetime.now(timezone(self.env.user.tz)))
        cell_format_title = book.add_format({'bold': True, 'align': 'left'})
        cell_format_title.set_font_name('Calibri')
        cell_format_title.set_font_size(15)
        cell_format_title.set_bottom(5)
        cell_format_title.set_bottom_color('#1F497D')
        cell_format_title.set_font_color('#1F497D')
        sheet.merge_range('A1:D1', text_title, cell_format_title)
        cell_format_text_generate = book.add_format({'bold': False, 'align': 'left'})
        cell_format_text_generate.set_font_name('Calibri')
        cell_format_text_generate.set_font_size(10)
        cell_format_text_generate.set_bottom(5)
        cell_format_text_generate.set_bottom_color('#1F497D')
        cell_format_text_generate.set_font_color('#1F497D')
        sheet.merge_range('A2:D2', text_generate, cell_format_text_generate)
        # Formato para fechas
        date_format = book.add_format({'num_format': 'dd/mm/yyyy'})

        # Agregar columnas
        aument_columns = 0
        for column in columns:
            sheet.write(2, aument_columns, column)
            aument_columns = aument_columns + 1

            # Agregar query
            aument_columns = 0
            aument_rows = 3
            for query in result_query:
                for row in query.values():
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

            sheet.add_table(2, 0, aument_rows, 4, {'style': 'Table Style Medium 2', 'columns': array_header_table})
            # Guadar Excel
            book.close()

            self.write({
                'excel_file': base64.encodestring(stream.getvalue()),
                'excel_file_name': filename,
            })

            action = {
                'name': 'Entidades por empleado',
                'type': 'ir.actions.act_url',
                'url': "web/content/?model=hr.entities.reports&id=" + str(
                    self.id) + "&filename_field=excel_file_name&field=excel_file&download=true&filename=" + self.excel_file_name,
                'target': 'self',
            }
            return action
