# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from pytz import timezone

import base64
import io
import xlsxwriter


class hr_contact_employee_review_report(models.Model):
    _name = 'hr.contact.employee.review.report'
    _description = 'Revisión de contactos vs empleados'

    excel_file = fields.Binary('Excel')
    excel_file_name = fields.Char('Excel filename')

    def generate_excel(self):

        # Obtener compañías del usuario
        companies_ids = self.env.companies.ids
        if not companies_ids:
            raise ValidationError(_('No se encontraron compañías asociadas al usuario. Por favor verificar.'))
        
        companies_ids_str = ','.join(map(str, companies_ids))

        query_report = '''
            select 
                coalesce(rp.vat, '') as numero_documento_contacto,
                coalesce(rp.name, '') as nombre_completo_contacto,
                coalesce(he.identification_id, '') as numero_documento_empleado,
                coalesce(he.name, '') as nombre_completo_empleado
            from hr_employee he
            inner join res_partner rp ON he.address_home_id = rp.id
            where he.active = true
            and he.company_id in (%s)
            order by rp.vat, he.identification_id
        ''' % companies_ids_str

        self._cr.execute(query_report)
        result_query = self._cr.dictfetchall()
        
        if len(result_query) == 0:
            raise ValidationError(_('No se encontró información para generar el reporte. Por favor verificar.'))

        # Generar EXCEL
        filename = 'Revisión de contactos vs empleados'
        stream = io.BytesIO()
        book = xlsxwriter.Workbook(stream, {'in_memory': True})

        # Columnas
        columns = [
            'Número de documento del contacto',
            'Nombre completo del contacto',
            'Número de documento del empleado',
            'Nombre completo del empleado'
        ]
        sheet = book.add_worksheet('Reporte')

        # Agregar textos al excel
        text_title = 'Revisión de contactos vs empleados'
        text_generate = 'Informe generado el %s' % (datetime.now(timezone(self.env.user.tz)) if self.env.user.tz else datetime.now())
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

        # Agregar columnas
        cell_format_header = book.add_format({'bold': True, 'align': 'center', 'border': 5, 'bg_color': '#D9E1F2'})
        cell_format_header.set_font_name('Calibri')
        cell_format_header.set_font_size(11)

        # Escribir encabezados
        aument_columns = 0
        for column in columns:
            sheet.write(3, aument_columns, column, cell_format_header)
            # Ajustar ancho de columna
            if aument_columns == 0 or aument_columns == 2:
                sheet.set_column(aument_columns, aument_columns, 30)  # Columnas de documentos
            else:
                sheet.set_column(aument_columns, aument_columns, 50)  # Columnas de nombres
            aument_columns = aument_columns + 1

        # Agregar datos
        aument_rows = 4
        
        # Formato para datos normales
        cell_format_data = book.add_format({'align': 'left', 'border': 1})
        cell_format_data.set_font_name('Calibri')
        cell_format_data.set_font_size(10)
        
        # Formato para filas con diferencia en documentos (fondo rojo claro)
        cell_format_diff_documento = book.add_format({'align': 'left', 'border': 1, 'bg_color': '#FFC7CE'})
        cell_format_diff_documento.set_font_name('Calibri')
        cell_format_diff_documento.set_font_size(10)
        
        # Formato para filas con diferencia en nombres (fondo amarillo)
        cell_format_diff_nombre = book.add_format({'align': 'left', 'border': 1, 'bg_color': '#FFEB9C'})
        cell_format_diff_nombre.set_font_name('Calibri')
        cell_format_diff_nombre.set_font_size(10)

        for query in result_query:
            # Obtener valores
            num_doc_contacto = str(query.get('numero_documento_contacto', '') or '').strip()
            num_doc_empleado = str(query.get('numero_documento_empleado', '') or '').strip()
            nombre_contacto = str(query.get('nombre_completo_contacto', '') or '').strip()
            nombre_empleado = str(query.get('nombre_completo_empleado', '') or '').strip()
            
            # Verificar si hay diferencias
            diferencia_documento = num_doc_contacto != num_doc_empleado
            diferencia_nombre = nombre_contacto != nombre_empleado
            
            # Seleccionar formato según el tipo de diferencia
            if diferencia_documento:
                formato_a_usar = cell_format_diff_documento
            elif diferencia_nombre:
                formato_a_usar = cell_format_diff_nombre
            else:
                formato_a_usar = cell_format_data
            
            sheet.write(aument_rows, 0, num_doc_contacto, formato_a_usar)
            sheet.write(aument_rows, 1, nombre_contacto, formato_a_usar)
            sheet.write(aument_rows, 2, num_doc_empleado, formato_a_usar)
            sheet.write(aument_rows, 3, nombre_empleado, formato_a_usar)
            aument_rows = aument_rows + 1

        # Convertir en tabla
        array_header_table = []
        for i in columns:
            dict = {'header': i}
            array_header_table.append(dict)

        sheet.add_table(3, 0, aument_rows-1, len(columns)-1, {'style': 'Table Style Medium 2', 'columns': array_header_table})

        # Guardar Excel
        book.close()

        self.write({
            'excel_file': base64.encodebytes(stream.getvalue()),
            'excel_file_name': filename,
        })

        action = {
            'name': 'Revisión de contactos vs empleados',
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=hr.contact.employee.review.report&id=" + str(
                self.id) + "&filename_field=excel_file_name&field=excel_file&download=true&filename=" + self.excel_file_name,
            'target': 'self',
        }
        return action

