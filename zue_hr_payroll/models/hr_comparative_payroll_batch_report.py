from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import base64
import io
import xlsxwriter

class zue_comparative_payroll_batch_report(models.Model):
    _name = 'zue.comparative.payroll.batch.report'
    _description = 'Comparativo entre Lotes de Nómina'

    z_batch_report_type = fields.Selection(
        [('r1', 'Reporte por Lotes y Empleados'), ('r2', 'Reporte por Liquidaciones')],
        string='Tipo de reporte', required=True, default='r1')
    z_payroll_initial_date = fields.Date(string='Fecha Inicial')
    z_payroll_final_date = fields.Date(string='Fecha Final')
    company_id = fields.Many2one('res.company', string='Compañia', required=True, default=lambda self: self.env.company)
    z_batch_a_id = fields.Many2one('hr.payslip.run', string='Primer Lote')
    z_batch_b_id = fields.Many2one('hr.payslip.run', string='Segundo Lote')
    z_payslip_a_id = fields.Many2one('hr.payslip', string='Primera Liquidación')
    z_payslip_b_id = fields.Many2one('hr.payslip', string='Segunda Liquidación')
    z_employee_ids = fields.Many2many('hr.employee', string='Empleados')

    excel_file = fields.Binary('Archivo Excel')
    excel_file_name = fields.Char('Nombre del archivo')

    @api.onchange('z_batch_report_type')
    def _onchange_batch_report_type(self):
        for record in self:
            if record.z_batch_report_type == 'r1':
                record.z_payslip_a_id = False
                record.z_payslip_b_id = False
                record.z_employee_ids = [(5, 0, 0)]
            elif record.z_batch_report_type == 'r2':
                record.z_batch_a_id = False
                record.z_batch_b_id = False
                record.z_employee_ids = [(5, 0, 0)]

    def generate_comparative_payroll_batch_excel(self):

        if not self.z_batch_a_id or not self.z_batch_b_id:
            raise ValidationError(_("Debe seleccionar ambos lotes de nómina."))

        batch_a = self.z_batch_a_id.id
        batch_b = self.z_batch_b_id.id

        query = f"""
        select
            coalesce(l1.name, l2.name) as concepto,
            coalesce(he.name, '') as empleado,
            coalesce(l1.total, 0) as valor_lote_a,
            coalesce(l2.total, 0) as valor_lote_b,
            coalesce(l1.total, 0) - coalesce(l2.total, 0) as diferencia
        from (
            select hpl.name, hp.employee_id, sum(hpl.total) as total
            from hr_payslip_line hpl
            inner join hr_payslip hp on hp.id = hpl.slip_id
            where hp.payslip_run_id = {batch_a}
            group by hpl.name, hp.employee_id
        ) l1
        full outer join (
            select hpl.name, hp.employee_id, sum(hpl.total) as total
            from hr_payslip_line hpl
            inner join hr_payslip hp on hp.id = hpl.slip_id
            where hp.payslip_run_id = {batch_b}
            group by hpl.name, hp.employee_id
        ) l2
        on l1.employee_id = l2.employee_id and l1.name = l2.name
        left join hr_employee he on coalesce(l1.employee_id, l2.employee_id) = he.id
        order by empleado, concepto
        """

        self._cr.execute(query)
        results = self._cr.dictfetchall()

        # Generar Excel
        filename = f"Comparativo Lotes Nómina - {self.z_batch_a_id.name} vs {self.z_batch_b_id.name}.xlsx"
        stream = io.BytesIO()
        book = xlsxwriter.Workbook(stream, {'in_memory': True})
        sheet = book.add_worksheet('Comparativo de Lotes')
        sheet.set_zoom(90)

        # Formatos
        title_format = book.add_format({'bold': True, 'align': 'center'})
        title_format.set_font_size(14)
        title_format.set_font_color('#1F497D')
        subtitle_format = book.add_format({'align': 'center', 'font_size': 11, 'font_color': '#1F497D'})
        header_format = book.add_format({'align': 'center', 'bold': True, 'bg_color': '#BDD7EE', 'border': 1})
        cell_format = book.add_format({'border': 1, 'align': 'center'})
        cell_format_left = book.add_format({'border': 1, 'align': 'left'})
        number_format_int = book.add_format({'border': 1, 'align': 'center', 'num_format': '#,##0'})

        # Encabezados
        sheet.merge_range('A1:E1', f"Comparativo de Lotes de Nómina", title_format)
        sheet.merge_range('A2:E2', f"{self.z_batch_a_id.name} vs {self.z_batch_b_id.name}", subtitle_format)

        # Columnas
        columns = ['Empleado', 'Concepto', 'Valor Lote A', 'Valor Lote B', 'Diferencia']

        # Encabezado de la tabla
        for i in range(len(columns)):
            sheet.write(3, i, columns[i], header_format)
            sheet.set_column(i, i, len(columns[i]) + 3)

        # Imprimir datos
        row = 4
        for record in results:
            sheet.write(row, 0, record['empleado'] or '', cell_format_left)
            sheet.write(row, 1, record['concepto'] or '', cell_format_left)
            sheet.write(row, 2, record['valor_lote_a'] or 0, number_format_int)
            sheet.write(row, 3, record['valor_lote_b'] or 0, number_format_int)
            sheet.write(row, 4, record['diferencia'] or 0, number_format_int)
            row += 1

        # Formato de la tabla
        sheet.add_table(3, 0, row - 1, len(columns) - 1, {
            'columns': [{'header': col} for col in columns],
            'style': 'Table Style Medium 9',
            'name': 'ComparativoLotes'
        })

        # Ajustar ancho de columnas
        sheet.set_column(0, 0, 40)
        sheet.set_column(1, 1, 35)
        sheet.set_column(2, 2, 20)
        sheet.set_column(3, 3, 20)
        sheet.set_column(4, 4, 20)

        # Cerrar archivo
        book.close()

        # Guardar Excel
        self.write({
            'excel_file': base64.encodebytes(stream.getvalue()),
            'excel_file_name': f"{filename}.xlsx",
        })

        # Descargar archivo
        return {
            'name': 'Comparativo Lotes',
            'type': 'ir.actions.act_url',
            'url': f"/web/content/?model={self._name}&id={self.id}&field=excel_file&filename_field=excel_file_name&download=true&filename={self.excel_file_name}",
            'target': 'self',
        }

    def generate_comparative_payroll_payslip_excel(self):

        if not self.z_payslip_a_id or not self.z_payslip_b_id:
            raise ValidationError(_("Debe seleccionar ambas liquidaciones."))

        ps_a_id = self.z_payslip_a_id.id
        ps_b_id = self.z_payslip_b_id.id
        ps_a_label = self.z_payslip_a_id.number or self.z_payslip_a_id.name or str(ps_a_id)
        ps_b_label = self.z_payslip_b_id.number or self.z_payslip_b_id.name or str(ps_b_id)

        query = f"""
            select
                coalesce(l1.name, l2.name) as concepto,
                coalesce(l1.total, 0) as valor_liq_a,
                coalesce(l2.total, 0) as valor_liq_b,
                coalesce(l1.total, 0) - coalesce(l2.total, 0) as diferencia
            from (
                select hpl.name, sum(hpl.total) as total
                from hr_payslip_line hpl
                where hpl.slip_id = {ps_a_id}
                group by hpl.name
            ) l1
            full outer join (
                select hpl.name, sum(hpl.total) as total
                from hr_payslip_line hpl
                where hpl.slip_id = {ps_b_id}
                group by hpl.name
            ) l2
            on l1.name = l2.name
            order by concepto
        """

        self._cr.execute(query)
        results = self._cr.dictfetchall()

        if not results:
            raise ValidationError(_("No se encontraron líneas de nómina para las liquidaciones seleccionadas."))

        # Generar Excel
        filename = f"Comparativo Liquidaciones - {ps_a_label} vs {ps_b_label}"
        stream = io.BytesIO()
        book = xlsxwriter.Workbook(stream, {'in_memory': True})
        sheet = book.add_worksheet('Comparativo de Liquidaciones')
        sheet.set_zoom(90)

        # Formatos
        title_format = book.add_format({'bold': True, 'align': 'center'})
        title_format.set_font_size(14)
        title_format.set_font_color('#1F497D')

        subtitle_format = book.add_format({'align': 'center', 'font_size': 11, 'font_color': '#1F497D'})

        header_format = book.add_format({'align': 'center', 'bold': True, 'bg_color': '#BDD7EE', 'border': 1})
        cell_format_left = book.add_format({'border': 1, 'align': 'left'})
        number_format_int = book.add_format({'border': 1, 'align': 'center', 'num_format': '#,##0'})

        # Encabezados
        sheet.merge_range('A1:E1', "Comparativo de Liquidaciones de Nómina", title_format)
        sheet.merge_range('A2:E2', f"{ps_a_label} vs {ps_b_label}", subtitle_format)

        # Columnas
        columns = ['Regla', f'Valor {ps_a_label}', f'Valor {ps_b_label}', 'Diferencia']

        # Encabezado tabla
        for i, col in enumerate(columns):
            sheet.write(3, i, col, header_format)
            sheet.set_column(i, i, max(12, len(col) + 3))

        # Datos
        row = 4
        for rec in results:
            sheet.write(row, 0, rec['concepto'] or '', cell_format_left)
            sheet.write(row, 1, rec['valor_liq_a'] or 0, number_format_int)
            sheet.write(row, 2, rec['valor_liq_b'] or 0, number_format_int)
            sheet.write(row, 3, rec['diferencia'] or 0, number_format_int)
            row += 1

        # Tabla
        sheet.add_table(3, 0, row - 1, len(columns) - 1, {
            'columns': [{'header': c} for c in columns],
            'style': 'Table Style Medium 9',
            'name': 'ComparativoPayslips'
        })

        # Ajustar ancho de columnas
        sheet.set_column(0, 0, 30)
        sheet.set_column(1, 1, 20)
        sheet.set_column(2, 2, 20)
        sheet.set_column(3, 3, 20)

        # Cerrar archivo
        book.close()
        self.write({
            'excel_file': base64.encodebytes(stream.getvalue()),
            'excel_file_name': f"{filename}.xlsx",
        })

        # Guardar Excel
        return {
            'name': 'Comparativo Liquidaciones',
            'type': 'ir.actions.act_url',
            'url': f"/web/content/?model={self._name}&id={self.id}&field=excel_file&filename_field=excel_file_name&download=true&filename={self.excel_file_name}",
            'target': 'self',
        }
