# -*- coding: utf-8 -*-
from html import escape
import re
from odoo import models, fields, _
from odoo.exceptions import ValidationError

import base64
import io
import xlsxwriter
#---------------------------Modelo para generar REPORTES-------------------------------#

# Reportes
class x_reports(models.Model):
    _name = 'zue.reports'
    _description = 'Reportes creados por ZUE'


    name = fields.Char(string='Nombre', required=True)
    description = fields.Char(string='Descripción', required=True)
    model = fields.Char(string='Modelo', required=True)
    columns = fields.Char(string='Columnas (Separadas por , )', required=True)
    query = fields.Text(string='Query')    
    excel_file = fields.Binary('Excel file')
    excel_file_name = fields.Char('Excel name')
    preview = fields.Html(string='Resultado', readonly=True, copy=False)
    
    #Retonar columnas
    def get_columns(self):
        _columns = self.columns.split(",")
        return _columns
    
    #Ejecutar consulta SQL
    def run_sql(self):
        query = self.query
        
        self.env.cr.execute(query)
        _res = self.env.cr.dictfetchall()
        return _res
    
    #Ejecutar instrucción SQL
    def execute_sql(self, query=''):
        if not query:
            query = self.query

        self.env.cr.execute(query)
        return True

    def write(self, vals):
        if 'query' in vals and 'preview' not in vals:
            vals['preview'] = False
        return super().write(vals)

    def read(self, fields=None, load='_classic_read'):
        # El HTML de preview no se envía salvo contexto explícito (evita peso al abrir el formulario o por URL).
        if not self.env.context.get('load_zue_reports_preview'):
            if fields is None:
                fields = [name for name in self._fields if name != 'preview']
            else:
                fields = [name for name in fields if name != 'preview']
        return super().read(fields, load)

    def _validate_preview_query(self, query):
        query = (query or '').strip()
        # Remove SQL comments to evaluate first statement keyword safely.
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.S)
        query = re.sub(r'--.*?$', '', query, flags=re.M).strip()
        query = query.rstrip(';').strip()

        if not query:
            raise ValidationError(_('Debe ingresar una consulta.'))

        # Prevent multiple statements in preview mode.
        if ';' in query:
            raise ValidationError(_('No se permiten multiples sentencias en previsualizacion.'))

        lowered_query = query.lower()
        if not (lowered_query.startswith('select') or lowered_query.startswith('with')):
            raise ValidationError(_('En previsualizacion solo se permiten consultas SELECT.'))

        forbidden_keywords = re.compile(r'\b(insert|update|delete|alter|drop|create|truncate|grant|revoke|comment)\b', re.I)
        if forbidden_keywords.search(lowered_query):
            raise ValidationError(_('En previsualizacion solo se permiten consultas SELECT.'))

        return query

    def action_preview_query(self):
        self.ensure_one()

        try:
            _preview_statement_timeout_ms = 10000
            _preview_row_limit = 2000

            validated_query = self._validate_preview_query(self.query)
            base_sql = validated_query.replace(';', '').strip()
            # Mismo efecto que escribir "LIMIT N" al final en el editor.
            # Se concatena literal para evitar incompatibilidades en LIMIT parametrizado.
            if re.search(r'\blimit\s+\d+\s*$', base_sql, re.IGNORECASE):
                limited_query = base_sql
            else:
                limited_query = f"{base_sql} LIMIT {_preview_row_limit + 1}"

            self.env.cr.execute(
                'SET LOCAL statement_timeout = %s',
                (str(_preview_statement_timeout_ms),),
            )
            self.env.cr.execute(limited_query)
            
            if not self.env.cr.description:
                raise ValidationError(_('La previsualizacion solo aplica para consultas SELECT.'))

            headers = [column[0] for column in self.env.cr.description]
            rows = self.env.cr.fetchmany(_preview_row_limit + 1)
            is_limited = len(rows) >= _preview_row_limit
            if is_limited:
                rows = rows[:_preview_row_limit]

            warning_html = ''
            if is_limited:
                warning_html = (
                    "<div style='margin-bottom:10px;padding:10px 12px;background:#fff4e5;"
                    "border:1px solid #ffcc80;border-radius:8px;color:#7a4200;'>"
                    f"<strong>Aviso:</strong> La previsualizacion se limito a {_preview_row_limit} filas "
                    "para evitar alto consumo de memoria. Si necesita todos los registros, use "
                    "<strong>Generar Excel</strong>.</div>"
                )

            table_header = ''.join(
                "<th style='position:sticky;top:0;background:#714b67;color:#ffffff !important;"
                "padding:10px 12px;border-bottom:2px solid #8a6b83;text-align:left;"
                f"white-space:nowrap;'>{escape(str(header))}</th>"
                for header in headers
            )
            table_rows = []
            for index, row in enumerate(rows):
                row_background = '#ffffff' if index % 2 == 0 else '#f8f5f8'
                row_cells = ''.join(
                    "<td style='padding:8px 12px;border-bottom:1px solid #e5eef1;text-align:left;"
                    f"background:{row_background};"
                    "color:#111111 !important;'>"
                    f"{escape(str(value)) if value is not None else ''}</td>"
                    for value in row
                )
                table_rows.append(f"<tr style='background:{row_background};color:#111111 !important;'>{row_cells}</tr>")

            self.preview = (
                warning_html +
                "<div style='margin-bottom:10px;padding:8px 12px;background:#f3edf3;"
                "border:1px solid #d8c8d4;border-radius:8px;color:#4a3545;'>"
                f"<strong>Filas mostradas:</strong> {len(rows)} &nbsp;&nbsp; <strong>Columnas:</strong> {len(headers)}</div>"
                "<div style='overflow:auto;max-height:520px;border:1px solid #d8c8d4;"
                "border-radius:10px;background:#ffffff;'>"
                "<table class='table table-sm' style='margin-bottom:0;min-width:100%;"
                "border-collapse:separate;border-spacing:0;color:#111111 !important;'>"
                f"<thead><tr>{table_header}</tr></thead><tbody>{''.join(table_rows)}</tbody></table></div>"
            )
        except ValidationError:
            raise
        except Exception as error:
            if 'statement timeout' in str(error).lower():
                raise ValidationError(
                    _(
                        'La previsualizacion excedio el tiempo maximo permitido. '
                        'Use filtros, LIMIT en la consulta o genere el Excel.'
                    )
                )
            raise ValidationError(_('Error executing SQL query: %s', error))

        ctx = dict(self.env.context)
        ctx['load_zue_reports_preview'] = True
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'zue.reports',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
            'context': ctx,
        }

    def get_excel(self):        
        if self.query and self.columns:
            result_columns = self.get_columns()
            result_query = self.run_sql()
             
            filename= str(self.name)+'.xlsx'
            stream = io.BytesIO()
            book = xlsxwriter.Workbook(stream, {'in_memory': True})
            sheet = book.add_worksheet(str(self.name))

            #Agregar columnas
            aument_columns = 0
            for columns in result_columns:            
                sheet.write(0, aument_columns, columns)
                aument_columns = aument_columns + 1

            #Agregar query
            aument_columns = 0
            aument_rows = 1
            for query in result_query: 
                for row in query.values():                
                    sheet.write(aument_rows, aument_columns, row)
                    aument_columns = aument_columns + 1
                aument_rows = aument_rows + 1
                aument_columns = 0
            
            book.close()
            
            #self.excel_file = base64.encodebytes(stream.getvalue())
            #self.excel_file_name = filename
            
            self.write({
                'excel_file': base64.encodebytes(stream.getvalue()),
                # Filename = <siren>FECYYYYMMDD where YYYMMDD is the closing date
                'excel_file_name': filename,
            })
            
            action = {
                        'name': str(self.name),
                        'type': 'ir.actions.act_url',
                        'url': "web/content/?model=zue.reports&id=" + str(self.id) + "&filename_field=excel_file_name&field=excel_file&download=true&filename=" + self.excel_file_name,
                        'target': 'self',
                    }
            return action
