from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

import base64
import io
import xlsxwriter

class zue_work_income_and_pensions(models.TransientModel):
    _name = 'zue.work.income.and.pensions'
    _description = 'Informe rentas de trabajo y pensiones'

    excel_file = fields.Binary(string='Excel')
    excel_filename = fields.Char(string='Excel filename')
    z_year = fields.Integer('Año', required=True)

    def generate_excel_report(self):

        # Crear archivo Excel
        filename = 'Rentas de trabajo y pensiones (Formato 2276).xlsx'
        stream = io.BytesIO()
        book = xlsxwriter.Workbook(stream, {'in_memory': True})
        sheet = book.add_worksheet('Formato 2276')

        # Estilos para columnas
        cell_column_format = book.add_format({
            'text_wrap': True,
            'bold': True,
            'bg_color': '#00FFFF',
            'font_name': 'Arial',
            'font_size': 10,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })

        # Estilos para contenido
        cell_content_format = book.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'text_wrap': True
        })

        # Estilos campos monetarios
        cell_money_format = book.add_format({
            'font_name': 'Arial',
            'font_size': 10,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'text_wrap': True,
            'num_format': '$#,##0'
        })

        # Columnas
        columns = ['Entidad Informante', 'Tipo de documento del beneficiario', 'Número de identificación del beneficiario', 'Primer Apellido del beneficiario',
                   'Segundo Apellido del beneficiario', 'Primer Nombre del beneficiario', 'Otros nombres del beneficiario', 'Dirección del beneficiario',
                   'Depto del beneficiario', 'Municipio beneficiario', 'País del beneficiario']
                   #  'Pagos por Salarios',
                   # 'Pagos por emolumentos eclesiásticos',
                   # 'Pagos Realizados con Bonos Electrónicos', 'Valor del exceso de los pagos por alimentación',
                   # 'Pagos por honorarios', 'Pagos por servicios',
                   # 'Pagos por comisiones', 'Pagos por prestaciones sociales', 'Pagos por viáticos',
                   # 'Pagos por gastos de representación',
                   # 'Pagos por compensaciones trabajo asociado cooperativo',
                   # 'Valor apoyos económicos no reembolsables o condonados entregados por el estado o financiados con recursos públicos',
                   # 'Otros Pagos', 'Cesantías e Intereses efectivamente pagadas al empleado',
                   # 'Cesantías consignadas al fondo de cesantías',
                   # 'Auxilio de cesantías reconocido a trabajadores del régimen tradicional del código sustantivo del trabajo',
                   # 'Pensiones de Jubilación vejez o invalidez',
                   # 'Total Ingresos Brutos por rentas de trabajo',
                   # 'Aportes Obligatorios por Salud a cargo del trabajador',
                   # 'Aportes Obligatorios a fondos de pensiones y solidaridad pensional a cargo del trabajador',
                   # 'Aportes voluntarios al régimen de ahorro individual con solidaridad S.A.S.',
                   # 'Aportes voluntarios a fondos de pensiones voluntarias', 'Aportes a cuentas AFC',
                   # 'Aportes a cuentas AVC',
                   # 'Valor de las retenciones en la fuente por pagos de renta de trabajo o pensiones',
                   # 'Impuesto sobre las ventas IVA - Mayor valor del costo o gasto',
                   # 'Retención en la fuente a título de impuesto sobre las ventas - IVA',
                   # 'Pagos por alimentación hasta 41 UVT',
                   # 'Valor ingreso laboral promedio de los últimos seis meses',
                   # 'Tipo del documento del dependiente económico', 'Número de identificación del dependiente económico',
                   # 'Identificación del fideicomiso', 'Tipo Documento participante en contrato de colaboración',
                   # 'Identificación participante en contrato de colaboración']

        # Obtener fechas
        year = self.z_year
        date_start = '01/01/' + str(year)
        date_start = datetime.strptime(date_start, '%d/%m/%Y')
        date_start = date_start.date()
        date_end = '31/12/' + str(year)
        date_end = datetime.strptime(date_end, '%d/%m/%Y')
        date_end = date_end.date()

        # Obtener empleados
        ids_employees = self.env['hr.payslip'].search([('state', '=', 'done'),('date_from', '>=', date_start), ('date_from', '<=', date_end)]).employee_id.ids

        obj_employee = self.env['hr.employee'].search([('id','in',ids_employees)])

        # Obtener parametrización
        obj_annual_parameters = self.env['hr.annual.parameters'].search([('year', '=', self.z_year)], limit=1)

        # Contenido de la tabla
        aument_rows = 2
        for employee in obj_employee:
            sheet.write(aument_rows, 1, 1, cell_content_format) # Entidad Informante
            # Obtener valores del campo selection tipo de documento
            document_type = dict(employee.partner_encab_id._fields['x_document_type'].selection).get(employee.partner_encab_id.x_document_type)
            sheet.write(aument_rows, 2, document_type, cell_content_format) # Tipo de documento del beneficiario
            sheet.write(aument_rows, 3, employee.partner_encab_id.vat if employee.partner_encab_id.vat else '', cell_content_format) # Número de identificación del beneficiario
            sheet.write(aument_rows, 4, employee.partner_encab_id.x_first_lastname if employee.partner_encab_id.x_first_lastname else '', cell_content_format) # Primer Apellido del beneficiario
            sheet.write(aument_rows, 5, employee.partner_encab_id.x_second_lastname if employee.partner_encab_id.x_second_lastname else '', cell_content_format) # Segundo Apellido del beneficiario
            sheet.write(aument_rows, 6, employee.partner_encab_id.x_first_name if employee.partner_encab_id.x_first_name else '', cell_content_format) # Primer Nombre del beneficiario
            sheet.write(aument_rows, 7, employee.partner_encab_id.x_second_name if employee.partner_encab_id.x_second_name else '', cell_content_format) # Otros nombres del beneficiario
            sheet.write(aument_rows, 8, employee.partner_encab_id.street if employee.partner_encab_id.street else '', cell_content_format) # Dirección del beneficiario
            sheet.write(aument_rows, 9, employee.partner_encab_id.state_id.name if employee.partner_encab_id.state_id.name else '', cell_content_format) # Depto del beneficiario
            sheet.write(aument_rows, 10, employee.partner_encab_id.x_city.name if employee.partner_encab_id.x_city.name else '', cell_content_format) # Municipio beneficiario
            sheet.write(aument_rows, 11, employee.partner_encab_id.country_id.name if employee.partner_encab_id.country_id.name else '', cell_content_format) # País del beneficiario

            # Obtener nóminas del empleado
            obj_payslip = self.env['hr.payslip'].search(
                [('state', '=', 'done'), ('employee_id', '=', employee.id),
                 ('date_from', '>=', date_start), ('date_from', '<=', date_end)])

            # Recorrer configuración
            amount_columns = 12
            for conf in sorted(obj_annual_parameters.conf_certificate_income_ids, key=lambda x: x.sequence):
                if conf.calculation == 'sum_rule' and conf.z_show_format_income_and_pensions:
                    amount = 0
                    if str(conf.z_name_format_income_and_pensions) not in columns:
                        columns.append(str(conf.z_name_format_income_and_pensions))
                    for payslip in obj_payslip:
                        amount += (sum([i.total for i in payslip.line_ids.filtered(lambda line: line.salary_rule_id.id in conf.salary_rule_id.ids)]))

                    sheet.write(aument_rows, amount_columns, amount, cell_money_format)
                    amount_columns += 1

            aument_rows += 1

        # Agregar columnas
        aument_columns = 1
        for column in columns:
            sheet.write(1, aument_columns, column, cell_column_format)
            # Ajustar ancho de las columnas
            sheet.set_column(aument_columns, aument_columns, 20)
            aument_columns += 1

        # Convertir en tabla
        array_header_table = []
        for i in columns:
            dict_h = {'header': i}
            array_header_table.append(dict_h)

        sheet.add_table(1, 1, aument_rows - 1, len(columns),
                        {'style': 'Table Style Medium 2', 'columns': array_header_table})

        # Cerrar y guardar Excel
        book.close()
        self.write({
            'excel_file': base64.encodebytes(stream.getvalue()),
            'excel_filename': filename
        })

        # Descargar Excel
        action = {
            'name': 'Informe rentas de trabajo y pensiones - Formato 2276',
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=zue.work.income.and.pensions&id=' + str(self.id)
                   + '&filename_field=excel_filename&field=excel_file&download=true&filename=' + self.excel_filename,
            'target': 'self',
        }
        return action