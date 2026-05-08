from collections import defaultdict
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from odoo import models, fields, api, _
import pandas as pd
import base64
import io
import xlsxwriter
import math

#Código fiscal
class fiscal_accounting_code_details(models.Model):
    _name = 'fiscal.accounting.code.details'
    _description = 'Código Fiscal - Cuentas'

    fiscal_accounting_id = fields.Many2one('fiscal.accounting.code',string='Código fiscal', required=True)
    account_id = fields.Many2one('account.account',string='Cuenta', required=True)
    move_type = fields.Selection([('debit', 'Débito'),
                                     ('credit', 'Crédito'),
                                     ('net', 'Neto')], string='Tipo de movimiento', required=True)

    _fiscal_account_id_uniq = models.Constraint('unique(fiscal_accounting_id,account_id)',
                         'Ya existe la cuenta en este código fiscal, por favor verficar.')

class fiscal_accounting_code(models.Model):
    _name = 'fiscal.accounting.code'
    _description = 'Código Fiscal'
    _rec_name = 'code_description'

    company_id = fields.Many2one('res.company', string='Compañía', required=True,
                                 default=lambda self: self.env.company)
    concept_dian = fields.Char(string="Código Fiscal", required=True)
    code_description = fields.Char(string="Descripción del Código", required=True)
    format_id = fields.Many2one('format.encab', string='Formato')
    #concept = fields.Char(string="Concepto")
    account_type = fields.Selection([('movement', 'Movimiento'),
                              ('balance', 'Balance'),
                              ], 'Tipo de cuenta')
    move_type = fields.Selection([('debit', 'Débito'),
                                  ('credit', 'Crédito'),
                                  ('net', 'Neto')], string='Tipo de movimiento', default='net',required=True)
    retention_associated = fields.Many2one('fiscal.accounting.code', string='Retención Asociada')
    required_retention_associated = fields.Boolean('Aplica para todos los conceptos del formato asociado')
    accounting_details_ids = fields.Many2many('account.account',string='Cuentas')
    #concept = fields.Char(string="Concepto")
    #account_code = fields.Char(string="Código de cuenta")
    #excluded_documents_ids = fields.Many2many('account.journal', string="Documentos Excluidos")
    #fiscal_group_id = fields.Many2one('fiscal.accounting.group',string="Grupo Fiscal")

    _fiscal_code_uniq = models.Constraint('unique(company_id,concept_dian)',
                         'El concepto DIAN digitado ya esta registrado para esta compañía, por favor verificar.')

#Grupo Fiscal
class fiscal_accounting_group(models.Model):
    _name = 'fiscal.accounting.group'
    _description = 'Grupo Fiscal'
    _rec_name = 'group_description'

    company_id = fields.Many2one('res.company', string='Compañía', required=True,
                                 default=lambda self: self.env.company)
    fiscal_group = fields.Char(string="Grupo Fiscal", required=True)
    group_description = fields.Char(string="Descripción del Grupo", required=True)
    operator = fields.Selection([('>', 'Mayor que'),
                              ('<', 'Menor que'),
                              ('==', 'Igual que'),
                              ('!=', 'Distinto de'),
                              ('<=','Menor o igual que'),
                              ('>=', 'Mayor o igual que'),
                              ], 'Operador')
    amount = fields.Float(string="Monto")
    tax_type = fields.Selection([('dian', "DIAN Art 631"),
                              ('treasury', "Tesoreria Distrital"),
                              ], "Tipo de impuesto")
    concept_dian_ids = fields.Many2many('fiscal.accounting.code', string="Códigos Fiscales")
    excluded_thirdparty_ids = fields.Many2many('res.partner', string="Tercero Excluido")
    partner_minor_amounts = fields.Many2one('res.partner', string="Tercero Cuantías menores")

    _fiscal_group_uniq = models.Constraint('unique(company_id,fiscal_group)',
                         'El grupo fiscal digitado ya esta registrado para esta compañía, por favor verificar.')


class format_encab(models.Model):
    _name = 'format.encab'
    _description = 'Formato de Código Fiscal Encabezado'

    format_id = fields.Char(string="Código Formato", required=True)
    description = fields.Char(string="Descripción del formato", required=True)
    details_ids = fields.One2many('format.detail','format_id',string = 'Campos Disponibles')
    company_id = fields.Many2one('res.company', string='Compañía', required=True,default=lambda self: self.env.company)
    format_associated_id = fields.Many2one('format.encab', string='Formato Asociado')
    fields_associated_code_fiscal_ids = fields.Many2many('fiscal.accounting.code', string='Conceptos Asociados')

    _format_encab_uniq = models.Constraint('unique(format_id,company_id)',
                         'El formato fiscal digitado ya esta registrado para esta compañía, por favor verificar.')

    @api.depends('format_id', 'description')
    def _compute_display_name(self):
        for record in self:
            record.display_name = "{}/{}".format(record.format_id, record.description)

    @api.onchange('format_associated_id')
    def get_code_fiscal(self):
        for record in self:
            record.fields_associated_code_fiscal_ids = self.env['fiscal.accounting.code'].search(
                [('format_id', '=', self.format_associated_id.id), ('format_id', '!=', False)]).ids

class format_detail(models.Model):
    _name = 'format.detail'
    _description = 'Formato de Código Fiscal Detalle'

    format_id = fields.Many2one('format.encab',string='Código Formato', required=True, ondelete='cascade')
    sequence = fields.Integer(string="Secuencia", required=True, store=True)
    available_fields = fields.Selection([('fiscal_accounting_id', 'Concepto Fiscal'),
                              ('concept_dian',  'Concepto DIAN'),
                              ('format',  'Formato Archivo'),
                              ('x_document_type', 'Tipo Documento Tercero'),
                              ('vat', 'Número Documento Tercero'),
                              ('x_first_name', 'Primer Nombre'),
                              ('x_second_name', 'Segundo Nombre'),
                              ('x_first_lastname', 'Primer Apellido'),
                              ('x_second_lastname', 'Segundo Apellido'),
                              ('commercial_company_name', 'Razón Social'),
                              ('x_digit_verification', 'Dígito de Verificación'),
                              ('street', 'Dirección'),
                              ('state_id', 'Código Departamento'),
                              ('city_id', 'Código Ciudad'),
                              ('amount', 'Valor Pesos'),
                              ('operator', 'Operador'),
                              ('tax', 'Base Impuestos'),
                              ('x_code_dian', 'Código País DIAN'),
                              ('phone', 'Teléfono Tercero'),
                              ('unit_rate', 'Tarifa Aplicada'),
                              ('email', 'Email'),
                              ('higher_value_iva', 'Mayor Valor Iva'),
                              ('x_ciiu_activity', 'Códigos CIIU'),
                              ], 'Campos Seleccionados', required=True)

class generate_media_magnetic(models.TransientModel):
    _name = 'generate.media.magnetic'
    _description = 'Generar Medios Magneticos'

    company_id = fields.Many2one('res.company',string='Compañia', required=True, default=lambda self: self.env.company)
    type_media_magnetic = fields.Selection([('dian', 'Generar Artículo 631'),
                                            ('distrital', 'Generar Impuesto Distrital')],'Tipo de medio magnético', default='dian')
    year = fields.Integer(string="Año", required=True, default=lambda self: datetime.now().year)
    with_resume = fields.Boolean(string="Con Resumen", help="Puede causar demora en la ejecución")
    excel_file = fields.Binary('Excel file')
    excel_file_name = fields.Char('Excel name')

    @api.depends('type_media_magnetic')
    def _compute_display_name(self):
        for record in self:
            record.display_name = "Generar Medios Magnético {}".format(record.type_media_magnetic.upper())

    def normalizeMediaMagneticSelectFields(self, select_fields):
        """Compatibilidad: format_detail antiguo guardaba x_city; el SQL expone city_id."""
        if not select_fields:
            return select_fields
        parts = [p.strip() for p in select_fields.split(',')]
        return ', '.join('city_id' if p == 'x_city' else p for p in parts)

    def buildAvailableFieldLabelMap(self):
        return dict(self.env['format.detail']._fields['available_fields'].selection)

    def validationMinorRawIsTrue(self, raw):
        if raw is True:
            return True
        if raw in (False, None):
            return False
        if isinstance(raw, str):
            return raw.lower() in ('true', 't', '1', 'yes')
        return bool(raw)

    def collectMediaMagneticRowsSinglePass(self, q_final_query, select_fields_format, obj_group_fiscal, fiscal):
        """Una sola ejecución del agregado envuelto; evita duplicar el costoso subquery (no minor + minor)."""
        self.env.cr.execute('SELECT * FROM (%s) AS _magnetic_pass_sub' % (q_final_query,))
        colnames = [c[0] for c in self.env.cr.description]
        rows = self.env.cr.fetchall()
        cols_needed = [c.strip() for c in select_fields_format.split(',')]
        res = []
        minor_amount = 0.0
        minor_tax = 0.0
        minor_had = False
        for row in rows:
            d = dict(zip(colnames, row))
            if self.validationMinorRawIsTrue(d.get('validation_minor')):
                minor_had = True
                minor_amount += float(d.get('amount') or 0)
                minor_tax += float(d.get('tax') or 0)
            else:
                res.append({k: d.get(k) for k in cols_needed})
        if obj_group_fiscal and minor_had:
            p = obj_group_fiscal.partner_minor_amounts
            itype = p.l10n_latam_identification_type_id
            base_minor = {
                'fiscal_accounting_id': fiscal.concept_dian,
                'concept_dian': fiscal.code_description,
                'format': fiscal.format_id.format_id,
                'x_document_type': itype.z_code_dian if itype else '',
                'vat': p.vat,
                'x_first_name': p.x_first_name or '',
                'x_second_name': p.x_second_name or '',
                'x_first_lastname': p.x_first_lastname or '',
                'x_second_lastname': p.x_second_lastname or '',
                'commercial_company_name': p.name,
                'x_digit_verification': p.x_digit_verification,
                'street': p.street,
                'state_id': p.state_id.z_code_dian if p.state_id else '',
                'city_id': p.city_id.z_code_dian if p.city_id else '',
                'amount': minor_amount,
                'operator': obj_group_fiscal.operator,
                'tax': minor_tax,
                'x_code_dian': '169',
                'phone': p.phone or p.mobile or '',
                'unit_rate': 0,
                'email': p.email or '',
                'higher_value_iva': 0,
                'x_ciiu_activity': p.x_ciiu_activity.name if p.x_ciiu_activity else '',
            }
            res.append({k: base_minor.get(k) for k in cols_needed})
        return res

    def mergeAssociatedFormatBalancesIntoRows(self, lst_Mvto, date_start, date_end, format_id):
        """Agrega balances de formatos asociados por NIT (sin pandas)."""
        query = """
                select D.code_description, G.vat, F.balance
                from format_encab A
                inner join fiscal_accounting_code_format_encab_rel B on A.id = B.format_encab_id
                inner join account_account_fiscal_accounting_code_rel C on B.fiscal_accounting_code_id = C.fiscal_accounting_code_id
                inner join fiscal_accounting_code D on B.fiscal_accounting_code_id = D.id
                inner join account_account E on C.account_account_id = E.id
                inner join account_move_line F on F.account_id = E.id and F.date between %s and %s and F.parent_state = 'posted'
                inner join res_partner G on F.partner_id = G.id and G.vat notnull
                where A.id = %s
                """
        self.env.cr.execute(query, (date_start, date_end, format_id))
        vat_to_code_balance = defaultdict(lambda: defaultdict(float))
        all_code_keys = set()
        for code_desc, vat, balance in self.env.cr.fetchall():
            if vat is None:
                continue
            vat_to_code_balance[vat][code_desc] += float(balance or 0)
            all_code_keys.add(code_desc)
        if not all_code_keys:
            return
        for row in lst_Mvto:
            v = row.get('vat')
            cmap = vat_to_code_balance.get(v) if v is not None else None
            for key in all_code_keys:
                row[key] = cmap.get(key, 0.0) if cmap else 0.0

    def generate_media_magnetic_dian_v2(self):
        #Variables excel
        filename = f'MedioMagnetico_{str(self.year)}.xlsx'
        stream = io.BytesIO()
        book = xlsxwriter.Workbook(stream, {'in_memory': True})
        field_label_map = self.buildAvailableFieldLabelMap()
        #Variables proceso
        date_start = str(self.year) +'-01-01'
        date_end = str(self.year) +'-12-31'
        date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_end = datetime.strptime(date_end, '%Y-%m-%d').date()
        minor_amounts = 0
        account_moves_ids = []
        q_select = ''
        q_from = ''
        q_where = ''
        q_group = ''
        #Traer todos los formatos
        obj_formats = self.env['format.encab'].search([('id','!=',False)])
        generated_format_sheets = False

        for format in obj_formats:
            obj_account_fiscal = self.env['fiscal.accounting.code'].search([('format_id','=',format.id)])
            lst_Mvto = []
            lst_partner_minor = []

            self.env.cr.execute(
                '''SELECT string_agg(available_fields, ', ') FROM format_detail WHERE format_id = %s''',
                (format.id,),
            )
            row_fmt_fields = self.env.cr.fetchone()
            select_fields_format = self.normalizeMediaMagneticSelectFields(
                row_fmt_fields[0] if row_fmt_fields else None)
            if not select_fields_format:
                raise UserError('No se encontraron campos disponibles para el formato %s' % format.name)

            fiscal_group_by_fiscal_id = {}
            if obj_account_fiscal:
                fiscal_ids_set = set(obj_account_fiscal.ids)
                fiscal_groups = self.env['fiscal.accounting.group'].search(
                    [('concept_dian_ids', 'in', obj_account_fiscal.ids)])
                for grp in fiscal_groups:
                    for cid in grp.concept_dian_ids.ids:
                        if cid in fiscal_ids_set and cid not in fiscal_group_by_fiscal_id:
                            fiscal_group_by_fiscal_id[cid] = grp

            for fiscal in obj_account_fiscal:
                q_final_query = ''

                q_select = '''Select '''
                q_from = '''From account_move_line A 
                            Inner Join account_move B on A.move_id = B.id
                            Inner Join res_partner C on A.partner_id = C.id '''

                if len(fiscal.accounting_details_ids) == 0:
                    continue
                if len(fiscal.accounting_details_ids) > 1:
                    q_where = '''where A.parent_state = 'posted' and A.account_id in %s''' % str(tuple(fiscal.accounting_details_ids.ids))
                else:
                    q_where = '''where A.parent_state = 'posted' and A.account_id in %s''' % '(' + str(fiscal.accounting_details_ids.id) + ')'

                q_group = 'Group by A.partner_id '

                obj_group_fiscal = fiscal_group_by_fiscal_id.get(fiscal.id)
                if not obj_group_fiscal:
                    obj_group_fiscal = self.env['fiscal.accounting.group'].search(
                        [('concept_dian_ids', 'in', fiscal.ids)], limit=1)
                if not obj_group_fiscal:
                    continue
                format_fields = fiscal.format_id.details_ids

                if fiscal.account_type == 'balance':
                    q_where += ''' and (A.date < '%s' or (A.date between '%s' and '%s' and B.accounting_closing_id isnull)) ''' % (date_start, date_start, date_end)
                else:
                    q_where += ''' and A.date between '%s' and '%s' and B.accounting_closing_id isnull ''' % (date_start, date_end)

                dict_partner_minor = {}
                dict_partner_minor_associated = {}

                amount = 0
                tax_base_amount = 0

                q_select += ''' '%s' as fiscal_accounting_id, '%s' as concept_dian, '%s' as format, I.z_code_dian as x_document_type, C.vat, C.x_first_name, C.x_second_name, C.x_first_lastname
                                , C.x_second_lastname, case when I.z_code_dian = '13' then '' else C.name end as commercial_company_name, C.x_digit_verification, C.street
                                , substring(D.z_code_dian, 1, 2) as state_id, D.z_code_dian as city_id, coalesce(E."name",'') as x_ciiu_activity 
                            ''' % (fiscal.concept_dian, fiscal.code_description, fiscal.format_id.format_id)

                if fiscal.move_type == 'debit':
                    q_select += ''', sum(A.debit) as amount'''
                elif fiscal.move_type == 'credit':
                    q_select += ''', sum(A.credit) as amount'''
                else:
                    q_select += ''', sum(A.balance) as amount'''

                q_select += ''', '%s' as operator''' % obj_group_fiscal.operator
                q_select += ''', sum(A.tax_base_amount) as tax, '169' as x_code_dian, C.phone, 0 as unit_rate, C.email, 0 as higher_value_iva '''

                q_from += '''Inner Join res_country_state D on C.state_id = D.id '''
                q_from += '''Left Join zue_ciiu E on C.x_ciiu_activity = E.id '''
                q_from += '''Left Join l10n_latam_identification_type I on C.l10n_latam_identification_type_id = I.id '''

                q_group += ''', I.z_code_dian, C.vat, C.x_first_name, C.x_second_name, C.x_first_lastname, C.x_second_lastname, C.name, C.x_digit_verification, C.street
                                , D.z_code_dian, C.phone, C.email, coalesce(E."name",'') '''

                q_select += ''', 0 amount_associated '''

                q_final_query = q_select + q_from + q_where + q_group
                if obj_group_fiscal:
                    q_final_query = f'Select *, case when a.amount {obj_group_fiscal.operator.replace("==", "=")} {obj_group_fiscal.amount} then True else False end as validation_minor from ({q_final_query}) a '
                else:
                    q_final_query = f'Select *, False as validation_minor from ({q_final_query}) a '

                list_dict = self.collectMediaMagneticRowsSinglePass(
                    q_final_query, select_fields_format, obj_group_fiscal, fiscal)

                lst_Mvto = lst_Mvto + list_dict

            query = '''select count(*) as cont from fiscal_accounting_code_format_encab_rel A where format_encab_id = %s''' % format.id
            self.env.cr.execute(query)
            result = self.env.cr.fetchone()[0]

            if result > 0 and lst_Mvto:
                self.mergeAssociatedFormatBalancesIntoRows(lst_Mvto, date_start, date_end, format.id)

            #Generar hoja de excel
            if len(lst_Mvto) == 0:
                continue
            generated_format_sheets = True
            sheet = book.add_worksheet(format.format_id)
            columns = []
            for field in lst_Mvto[0].keys():
                field_name = field_label_map.get(field, field.replace('_', ' '))
                columns.append(field_name)
            # Agregar columnas
            for col_idx, column in enumerate(columns):
                sheet.write(0, col_idx, column)
            num_cols = len(columns)
            col_widths = [len(str(columns[i])) + 2 for i in range(num_cols)]
            aument_rows = 1
            for info in lst_Mvto:
                for col_idx, row in enumerate(info.values()):
                    text = str(row)
                    sheet.write(aument_rows, col_idx, row)
                    ln = len(text) + 2
                    if ln > col_widths[col_idx]:
                        col_widths[col_idx] = ln
                aument_rows += 1
            for col_idx, w in enumerate(col_widths):
                sheet.set_column(col_idx, col_idx, min(max(w, 8), 60))

            # Convertir en tabla
            array_header_table = []
            for i in columns:
                dict_h = {'header': i}
                array_header_table.append(dict_h)
            sheet.add_table(0, 0, aument_rows-1, len(columns)-1, {'style': 'Table Style Medium 2', 'columns': array_header_table})

        if not generated_format_sheets and not self.with_resume:
            raise UserError(_('No se encuentra información para el año seleccionado.'))

        if self.with_resume:
            # Generar hoja de excel resumen
            sheet_resumen = book.add_worksheet("Resumen")
            columns = ['Documento','Fecha','Referencia','Débito','Crédito','Balance','Número Documento','Nombre','Cuenta','Descripción Cuenta']
            # Agregar columnas
            aument_columns = 0
            for column in columns:
                sheet_resumen.write(0, aument_columns, column)
                aument_columns = aument_columns + 1
            #Agrefar info
            date_format = book.add_format({'num_format': 'dd/mm/yyyy'})

            query = '''Select A.move_name, A.date, A.ref, A.debit, A.credit, A.balance, C.vat, C.name as partner_id, coalesce(E.code_store->>'1', '') as code, E.name->>'en_US' as account_id
                        From account_move_line A
                        Inner Join account_move B on A.move_id = B.id
                        Inner Join res_partner C on A.partner_id = C.id
                        Inner Join res_country_state D on C.state_id = D.id
                        Inner Join account_account E on A.account_id = E.id
                        where A.parent_state = 'posted' and ((A.date between '%s' and '%s' and B.accounting_closing_id isnull)) and
                                A.account_id in (select distinct account_account_id from account_account_fiscal_accounting_code_rel)
                        ''' % (date_start, date_end)

            self.env.cr.execute(query)
            info_moves = self.env.cr.dictfetchall()
            if not generated_format_sheets and not info_moves:
                raise UserError(_('No se encuentra información para el año seleccionado.'))

            col_max_resumen = [len(h) + 2 for h in columns]
            aument_rows_resumen = 1
            for move in info_moves:
                sheet_resumen.write(aument_rows_resumen, 0, move['move_name'])
                col_max_resumen[0] = max(col_max_resumen[0], len(str(move['move_name'])) + 2)
                sheet_resumen.write_datetime(aument_rows_resumen, 1, move['date'], date_format)
                col_max_resumen[1] = max(col_max_resumen[1], 14)
                sheet_resumen.write(aument_rows_resumen, 2, move['ref'])
                col_max_resumen[2] = max(col_max_resumen[2], len(str(move['ref'] or '')) + 2)
                sheet_resumen.write(aument_rows_resumen, 3, move['debit'])
                col_max_resumen[3] = max(col_max_resumen[3], len(str(move['debit'])) + 2)
                sheet_resumen.write(aument_rows_resumen, 4, move['credit'])
                col_max_resumen[4] = max(col_max_resumen[4], len(str(move['credit'])) + 2)
                sheet_resumen.write(aument_rows_resumen, 5, move['balance'])
                col_max_resumen[5] = max(col_max_resumen[5], len(str(move['balance'])) + 2)
                sheet_resumen.write(aument_rows_resumen, 6, move['vat'])
                col_max_resumen[6] = max(col_max_resumen[6], len(str(move['vat'] or '')) + 2)
                sheet_resumen.write(aument_rows_resumen, 7, move['partner_id'])
                col_max_resumen[7] = max(col_max_resumen[7], len(str(move['partner_id'] or '')) + 2)
                sheet_resumen.write(aument_rows_resumen, 8, move['code'])
                col_max_resumen[8] = max(col_max_resumen[8], len(str(move['code'] or '')) + 2)
                sheet_resumen.write(aument_rows_resumen, 9, move['account_id'])
                col_max_resumen[9] = max(col_max_resumen[9], len(str(move['account_id'] or '')) + 2)
                aument_rows_resumen += 1
            for c in range(10):
                sheet_resumen.set_column(c, c, min(max(col_max_resumen[c], 8), 60))

            # Convertir en tabla
            array_header_table_resumen = []
            for i in columns:
                dict_h = {'header': i}
                array_header_table_resumen.append(dict_h)
            sheet_resumen.add_table(0, 0, aument_rows_resumen - 1, len(columns) - 1,
                            {'style': 'Table Style Medium 2', 'columns': array_header_table_resumen})

        book.close()
        self.write({
            'excel_file': base64.encodebytes(stream.getvalue()),
            'excel_file_name': filename,
        })

        action = {
            'name': 'Export Medio magnetico información exogena',
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=generate.media.magnetic&id=" + str(
                self.id) + "&filename_field=excel_file_name&field=excel_file&download=true&filename=" + self.excel_file_name,
            'target': 'self',
        }
        return action

    def generate_media_magnetic_dian(self):
        #Variables excel
        filename = f'MedioMagnetico_{str(self.year)}.xlsx'
        stream = io.BytesIO()
        book = xlsxwriter.Workbook(stream, {'in_memory': True})
        #Variables proceso
        date_start = str(self.year) +'-01-01'
        date_end = str(self.year) +'-12-31'
        date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_end = datetime.strptime(date_end, '%Y-%m-%d').date()
        minor_amounts = 0
        account_moves_ids = []
        #Traer todos los formatos
        obj_formats = self.env['format.encab'].search([('id','!=',False)])

        for format in obj_formats:
            obj_account_fiscal = self.env['fiscal.accounting.code'].search([('format_id','=',format.id)])
            lst_Mvto = []
            lst_partner_minor = []
            for fiscal in obj_account_fiscal:
                obj_group_fiscal = self.env['fiscal.accounting.group'].search([('concept_dian_ids', 'in', fiscal.ids)],
                                                                              limit=1)
                format_fields = fiscal.format_id.details_ids

                if fiscal.account_type == 'balance':
                    partner_ids = self.env['account.move.line'].search(
                        [('date', '<=', date_end), ('parent_state', '=', 'posted'),
                         ('account_id', 'in', fiscal.accounting_details_ids.ids)]).partner_id.ids
                else:
                    partner_ids = self.env['account.move.line'].search(
                        [('date', '>=', date_start), ('date', '<=', date_end), ('parent_state', '=', 'posted'),
                         ('move_id.accounting_closing_id', '=', False),
                         ('account_id', 'in', fiscal.accounting_details_ids.ids)]).partner_id.ids
                obj_partner_ids = self.env['res.partner'].search([('id','in',partner_ids)])

                dict_partner_minor = {}
                dict_partner_minor_associated = {}

                for partner in obj_partner_ids:
                    try:
                        if fiscal.account_type == 'balance':
                            moves = self.env['account.move.line'].search(
                                [('date', '<', date_start), ('parent_state', '=', 'posted'),
                                 ('account_id', 'in', fiscal.accounting_details_ids.ids),
                                 ('partner_id', '=', partner.id)])
                            moves += self.env['account.move.line'].search(
                                [('date', '>=', date_start), ('date', '<=', date_end),('parent_state','=','posted'),
                                 ('move_id.accounting_closing_id', '=', False),
                                 ('account_id', 'in', fiscal.accounting_details_ids.ids), ('partner_id', '=', partner.id)])
                        else:
                            moves = self.env['account.move.line'].search(
                                [('date', '>=', date_start), ('date', '<=', date_end),('parent_state','=','posted'),
                                 ('move_id.accounting_closing_id','=',False),('account_id', 'in', fiscal.accounting_details_ids.ids),('partner_id', '=', partner.id)])
                        account_moves_ids = account_moves_ids + moves.ids
                        amount = 0
                        tax_base_amount = 0
                        for i in moves:
                            if fiscal.move_type == 'debit':
                                amount += i.debit
                            elif fiscal.move_type == 'credit':
                                amount += i.credit
                            else:
                                amount += i.balance
                            tax_base_amount += i.tax_base_amount

                        if len(obj_group_fiscal) > 0:
                            ldict = {'amount':amount,'validation_minor':False}
                            code_python = f'validation_minor = True if amount {obj_group_fiscal.operator} {obj_group_fiscal.amount}  else False'
                            exec(code_python,ldict)
                            validation_minor = ldict.get('validation_minor')
                        else:
                            validation_minor = False

                        if validation_minor == False:
                            #Armamos el dict con la información
                            dict_documents = dict(self.env['res.partner']._fields['x_document_type'].selection)
                            document_type = dict_documents.get(partner.x_document_type) if partner.x_document_type else ''
                            info = {'fiscal_accounting_id': fiscal.concept_dian,
                                    'concept_dian': fiscal.code_description,
                                    'format':fiscal.format_id.format_id,
                                    'x_document_type': partner.x_document_type,
                                    'vat': partner.vat,
                                    'x_first_name': partner.x_first_name or '',
                                    'x_second_name': partner.x_second_name if partner.x_second_name else '',
                                    'x_first_lastname': partner.x_first_lastname or '',
                                    'x_second_lastname': partner.x_second_lastname or '',
                                    'commercial_company_name': partner.name,
                                    'x_digit_verification': partner.x_digit_verification,
                                    'street': partner.street,
                                    'state_id': partner.city_id.z_code_dian[:2],
                                    'city_id': partner.city_id.z_code_dian,
                                    'amount': amount,
                                    'operator':obj_group_fiscal.operator,
                                    'tax': tax_base_amount,
                                    'x_code_dian': '169',#partner.country_id.code,
                                    'phone': partner.phone or partner.mobile,
                                    'unit_rate': 0,
                                    'email': partner.email,
                                    'higher_value_iva': 0,
                                }
                            #Formatos asociados
                            info_associated = {}
                            obj_account_fiscal_associated = self.env['fiscal.accounting.code'].search([('format_id', '=', format.format_associated_id.id)])
                            for fiscal_associated in obj_account_fiscal_associated:
                                if (fiscal_associated.required_retention_associated == False):
                                    obj_retention_associated = self.env['fiscal.accounting.code'].search([('id','in',fiscal_associated.ids),('retention_associated','=',fiscal.id)])
                                else:
                                    obj_retention_associated = self.env['fiscal.accounting.code'].search([('id', 'in', fiscal_associated.ids)])
                                moves_associated = self.env['account.move.line'].search(
                                    [('date', '>=', date_start), ('date', '<=', date_end),('parent_state','=','posted'),
                                    ('move_id.accounting_closing_id','=',False),('account_id', 'in', obj_retention_associated.accounting_details_ids.ids), ('partner_id', '=', partner.id)])
                                amount_associated = sum([i.balance for i in moves_associated])
                                name_associated = fiscal_associated.code_description.replace(' ','_')
                                info_associated[name_associated] = amount_associated
                            #Guardado final
                            media_magnetic = {}
                            for field in sorted(format_fields, key=lambda x: x.sequence):
                                if field.available_fields in info:
                                    media_magnetic[field.available_fields] = info.get(field.available_fields)
                            lst_Mvto.append({**media_magnetic, **info_associated})
                        else:
                            #Armamos el dict con la información
                            dict_partner_minor['fiscal_info'] = fiscal
                            dict_partner_minor['group_fiscal'] = obj_group_fiscal
                            dict_partner_minor['amount'] = dict_partner_minor.get('amount',0) + amount
                            dict_partner_minor['tax'] = dict_partner_minor.get('tax', 0) + tax_base_amount

                            #Formatos asociados
                            obj_account_fiscal_associated = self.env['fiscal.accounting.code'].search([('format_id', '=', format.format_associated_id.id)])
                            for fiscal_associated in obj_account_fiscal_associated:
                                if (fiscal_associated.required_retention_associated == False):
                                    obj_retention_associated = self.env['fiscal.accounting.code'].search([('id','in',fiscal_associated.ids),('retention_associated','=',fiscal.id)])
                                else:
                                    obj_retention_associated = self.env['fiscal.accounting.code'].search([('id', 'in', fiscal_associated.ids)])
                                moves_associated = self.env['account.move.line'].search(
                                    [('date', '>=', date_start), ('date', '<=', date_end),('parent_state','=','posted'),
                                    ('move_id.accounting_closing_id','=',False),('account_id', 'in', obj_retention_associated.accounting_details_ids.ids), ('partner_id', '=', partner.id)])
                                amount_associated = sum([i.balance for i in moves_associated])
                                name_associated = fiscal_associated.code_description.replace(' ','_')
                                dict_partner_minor_associated[name_associated] = dict_partner_minor_associated.get(name_associated, 0) + amount_associated
                    except Exception as e:
                        raise ValidationError(f'El tercero ID:{partner.id} NOMBRE:{partner.name} genero el siguente error: {e}')
                if len(dict_partner_minor) > 0:
                    dict_documents = dict(self.env['res.partner']._fields['x_document_type'].selection)
                    document_type = dict_documents.get(
                        dict_partner_minor.get('group_fiscal').partner_minor_amounts.x_document_type) if dict_partner_minor.get('group_fiscal').partner_minor_amounts.x_document_type else ''
                    info = {'fiscal_accounting_id': dict_partner_minor.get('fiscal_info').concept_dian,
                            'concept_dian': dict_partner_minor.get('fiscal_info').code_description,
                            'format': dict_partner_minor.get('fiscal_info').format_id.format_id,
                            'x_document_type':  dict_partner_minor.get('group_fiscal').partner_minor_amounts.x_document_type,
                            'vat': dict_partner_minor.get('group_fiscal').partner_minor_amounts.vat,
                            'x_first_name': dict_partner_minor.get('group_fiscal').partner_minor_amounts.x_first_name or '',
                            'x_second_name': dict_partner_minor.get('group_fiscal').partner_minor_amounts.x_second_name or '',
                            'x_first_lastname': dict_partner_minor.get('group_fiscal').partner_minor_amounts.x_first_lastname or '',
                            'x_second_lastname': dict_partner_minor.get('group_fiscal').partner_minor_amounts.x_second_lastname or '' ,
                            'commercial_company_name': dict_partner_minor.get('group_fiscal').partner_minor_amounts.name,
                            'x_digit_verification': dict_partner_minor.get('group_fiscal').partner_minor_amounts.x_digit_verification,
                            'street': dict_partner_minor.get('group_fiscal').partner_minor_amounts.street,
                            'state_id': dict_partner_minor.get('group_fiscal').partner_minor_amounts.city_id.z_code_dian[:2],
                            'city_id': dict_partner_minor.get('group_fiscal').partner_minor_amounts.city_id.z_code_dian,
                            'amount': dict_partner_minor.get('amount',0),
                            'operator': dict_partner_minor.get('group_fiscal').operator,
                            'tax': dict_partner_minor.get('tax',0),
                            'x_code_dian': '169', #dict_partner_minor.get('group_fiscal').partner_minor_amounts.country_id.code,
                            'phone': dict_partner_minor.get('group_fiscal').partner_minor_amounts.phone or dict_partner_minor.get('group_fiscal').partner_minor_amounts.mobile,
                            'unit_rate': 0,
                            'email': dict_partner_minor.get('group_fiscal').partner_minor_amounts.email,
                            'higher_value_iva': 0,
                            }
                    #Guardado final
                    media_magnetic = {}
                    for field in sorted(format_fields, key=lambda x: x.sequence):
                        if field.available_fields in info:
                            media_magnetic[field.available_fields] = info.get(field.available_fields)
                    lst_Mvto.append({**media_magnetic, **dict_partner_minor_associated})
                    lst_partner_minor.append({**dict_partner_minor, **dict_partner_minor_associated})
            #Generar hoja de excel
            sheet = book.add_worksheet(format.format_id)
            if len(lst_Mvto) == 0:
                continue
            columns = []
            for field in lst_Mvto[0].keys():
                field_name = dict(self.env['format.detail']._fields['available_fields'].selection).get(field,field.replace('_',' '))
                columns.append(field_name)
            # Agregar columnas
            aument_columns = 0
            for column in columns:
                sheet.write(0, aument_columns, column)
                aument_columns = aument_columns + 1
            # Agregar valores
            aument_columns = 0
            aument_rows = 1
            for info in lst_Mvto:
                for row in info.values():
                    width = len(str(row)) + 10
                    sheet.write(aument_rows, aument_columns, row)
                    # Ajustar tamaño columna
                    sheet.set_column(aument_columns, aument_columns, width)
                    aument_columns = aument_columns + 1
                aument_rows = aument_rows + 1
                aument_columns = 0

            # Convertir en tabla
            array_header_table = []
            for i in columns:
                dict_h = {'header': i}
                array_header_table.append(dict_h)
            sheet.add_table(0, 0, aument_rows-1, len(columns)-1, {'style': 'Table Style Medium 2', 'columns': array_header_table})

        # Generar hoja de excel resumen
        sheet_resumen = book.add_worksheet("Resumen")
        columns = ['Documento','Fecha','Referencia','Débito','Crédito','Balance','Número Documento','Nombre','Cuenta','Descripción Cuenta']
        # Agregar columnas
        aument_columns = 0
        for column in columns:
            sheet_resumen.write(0, aument_columns, column)
            aument_columns = aument_columns + 1
        #Agrefar info
        date_format = book.add_format({'num_format': 'dd/mm/yyyy'})
        info_moves = self.env['account.move.line'].search([('id', 'in', account_moves_ids)])
        aument_rows_resumen = 1
        for move in info_moves:
            sheet_resumen.write(aument_rows_resumen, 0, move.move_name)
            sheet_resumen.set_column(0, 0, len(str(move.move_name))+13)
            sheet_resumen.write_datetime(aument_rows_resumen, 1, move.date, date_format)
            sheet_resumen.set_column(1, 1, len(str(move.date)) + 10)
            sheet_resumen.write(aument_rows_resumen, 2, move.ref)
            sheet_resumen.set_column(2, 2, len(str(move.ref)) + 10)
            sheet_resumen.write(aument_rows_resumen, 3, move.debit)
            sheet_resumen.set_column(3, 3, len(str(move.debit)) + 10)
            sheet_resumen.write(aument_rows_resumen, 4, move.credit)
            sheet_resumen.set_column(4, 4, len(str(move.credit)) + 15)
            sheet_resumen.write(aument_rows_resumen, 5, move.balance)
            sheet_resumen.set_column(5, 5, len(str(move.balance)) + 10)
            sheet_resumen.write(aument_rows_resumen, 6, move.partner_id.vat)
            sheet_resumen.set_column(6, 6, len(str(move.partner_id.vat)) + 13)
            sheet_resumen.write(aument_rows_resumen, 7, move.partner_id.name)
            sheet_resumen.set_column(7, 7, len(str(move.partner_id.name)) + 13)
            # Extraer código del JSON code_store
            account_code = move.account_id._get_code_from_store() if hasattr(move.account_id, '_get_code_from_store') else (move.account_id.code_store.get('1', '') if isinstance(move.account_id.code_store, dict) else '')
            sheet_resumen.write(aument_rows_resumen, 8, account_code)
            sheet_resumen.set_column(8, 8, len(str(account_code)) + 13)
            sheet_resumen.write(aument_rows_resumen, 9, move.account_id.name)
            sheet_resumen.set_column(9, 9, len(str(move.account_id.name)) + 15)
            # sheet_resumen.write(aument_rows_resumen, 10, move.analytic_account_id.name)
            # sheet_resumen.set_column(10, 10, len(str(move.analytic_account_id.name)) + 15)
            aument_rows_resumen = aument_rows_resumen + 1

        # Convertir en tabla
        array_header_table_resumen = []
        for i in columns:
            dict_h = {'header': i}
            array_header_table_resumen.append(dict_h)
        sheet_resumen.add_table(0, 0, aument_rows_resumen - 1, len(columns) - 1,
                        {'style': 'Table Style Medium 2', 'columns': array_header_table_resumen})

        book.close()
        self.write({
            'excel_file': base64.encodebytes(stream.getvalue()),
            'excel_file_name': filename,
        })

        action = {
            'name': 'Export Medio magnetico información exogena',
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=generate.media.magnetic&id=" + str(
                self.id) + "&filename_field=excel_file_name&field=excel_file&download=true&filename=" + self.excel_file_name,
            'target': 'self',
        }

        return action

    def generate_media_magnetic_distrital(self):
        # Variables excel
        filename = f'MedioMagneticoDistrital_{str(self.year)}.xlsx'
        stream = io.BytesIO()
        book = xlsxwriter.Workbook(stream, {'in_memory': True})
        field_label_map = self.buildAvailableFieldLabelMap()
        # Variables proceso
        date_start = str(self.year) + '-01-01'
        date_end = str(self.year) + '-12-31'
        date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_end = datetime.strptime(date_end, '%Y-%m-%d').date()
        minor_amounts = 0
        account_moves_ids = []
        q_select = ''
        q_from = ''
        q_where = ''
        q_group = ''
        # Filtrar grupos distritales
        fiscal_groups = self.env['fiscal.accounting.group'].search([('tax_type', '=', 'treasury')])
        if not fiscal_groups:
            raise ValidationError(f'No hay grupos fiscales con tipo de impuesto "Tesoreria Distrital" Por favor verificar.')
        # Traer todos los formatos
        obj_formats = self.env['format.encab'].search([('id', '!=', False)])
        generated_format_sheets = False

        for format in obj_formats:
            obj_account_fiscal = self.env['fiscal.accounting.code'].search([('format_id', '=', format.id)])
            lst_Mvto = []
            lst_partner_minor = []

            self.env.cr.execute(
                '''SELECT string_agg(available_fields, ', ') FROM format_detail WHERE format_id = %s''',
                (format.id,),
            )
            row_fmt_fields = self.env.cr.fetchone()
            select_fields_format = self.normalizeMediaMagneticSelectFields(
                row_fmt_fields[0] if row_fmt_fields else None)
            if not select_fields_format:
                raise UserError('No se encontraron campos disponibles para el formato %s' % format.name)

            fiscal_group_by_fiscal_id = {}
            if obj_account_fiscal:
                fiscal_ids_set = set(obj_account_fiscal.ids)
                fiscal_groups_treasury = self.env['fiscal.accounting.group'].search(
                    [('concept_dian_ids', 'in', obj_account_fiscal.ids), ('tax_type', '=', 'treasury')])
                for grp in fiscal_groups_treasury:
                    for cid in grp.concept_dian_ids.ids:
                        if cid in fiscal_ids_set and cid not in fiscal_group_by_fiscal_id:
                            fiscal_group_by_fiscal_id[cid] = grp

            for fiscal in obj_account_fiscal:
                q_final_query = ''
                q_select = '''Select '''
                q_from = '''From account_move_line A 
                                    Inner Join account_move B on A.move_id = B.id
                                    Inner Join res_partner C on A.partner_id = C.id '''

                if len(fiscal.accounting_details_ids) == 0:
                    continue
                if len(fiscal.accounting_details_ids) > 1:
                    q_where = '''where A.parent_state = 'posted' and A.account_id in %s''' % str(
                        tuple(fiscal.accounting_details_ids.ids))
                else:
                    q_where = '''where A.parent_state = 'posted' and A.account_id in %s''' % '(' + str(
                        fiscal.accounting_details_ids.id) + ')'

                q_group = 'Group by A.partner_id '

                obj_group_fiscal = fiscal_group_by_fiscal_id.get(fiscal.id)
                if not obj_group_fiscal:
                    obj_group_fiscal = self.env['fiscal.accounting.group'].search(
                        [('concept_dian_ids', 'in', fiscal.ids), ('tax_type', '=', 'treasury')], limit=1)

                if not obj_group_fiscal or obj_group_fiscal.tax_type != 'treasury':
                    continue
                format_fields = fiscal.format_id.details_ids

                if fiscal.account_type == 'balance':
                    q_where += ''' and (A.date < '%s' or (A.date between '%s' and '%s' and B.accounting_closing_id isnull)) ''' % (
                    date_start, date_start, date_end)
                else:
                    q_where += ''' and A.date between '%s' and '%s' and B.accounting_closing_id isnull ''' % (
                    date_start, date_end)

                dict_partner_minor = {}
                dict_partner_minor_associated = {}

                amount = 0
                tax_base_amount = 0

                q_select += ''' '%s' as fiscal_accounting_id, '%s' as concept_dian, '%s' as format, I.z_code_dian as x_document_type, C.vat, C.x_first_name, C.x_second_name, C.x_first_lastname
                                        , C.x_second_lastname, case when I.z_code_dian = '13' then '' else C.name end as commercial_company_name, C.x_digit_verification, C.street
                                        , substring(D.z_code_dian, 1, 2) as state_id, D.z_code_dian as city_id, coalesce(E."name",'') as x_ciiu_activity 
                                    ''' % (fiscal.concept_dian, fiscal.code_description, fiscal.format_id.format_id)

                if fiscal.move_type == 'debit':
                    q_select += ''', sum(A.debit) as amount'''
                elif fiscal.move_type == 'credit':
                    q_select += ''', sum(A.credit) as amount'''
                else:
                    q_select += ''', sum(A.balance) as amount'''

                q_select += ''', '%s' as operator''' % obj_group_fiscal.operator
                #q_select += ''', '%s' as operator''' % obj_group_fiscal.filtered(lambda x: fiscal in x.concept_dian_ids).operator
                q_select += ''', sum(A.tax_base_amount) as tax, '169' as x_code_dian, C.phone, 0 as unit_rate, C.email, 0 as higher_value_iva '''

                q_from += '''Inner Join res_country_state D on C.state_id = D.id '''
                q_from += '''Left Join zue_ciiu E on C.x_ciiu_activity = E.id '''
                q_from += '''Left Join l10n_latam_identification_type I on C.l10n_latam_identification_type_id = I.id '''

                q_group += ''', I.z_code_dian, C.vat, C.x_first_name, C.x_second_name, C.x_first_lastname, C.x_second_lastname, C.name, C.x_digit_verification, C.street
                                        , D.z_code_dian, C.phone, C.email, coalesce(E."name",'') '''

                q_select += ''', 0 amount_associated '''

                q_final_query = q_select + q_from + q_where + q_group
                if obj_group_fiscal:
                    q_final_query = f'Select *, case when a.amount {obj_group_fiscal.operator.replace("==", "=")} {obj_group_fiscal.amount} then True else False end as validation_minor from ({q_final_query}) a '
                else:
                    q_final_query = f'Select *, False as validation_minor from ({q_final_query}) a '

                list_dict = self.collectMediaMagneticRowsSinglePass(
                    q_final_query, select_fields_format, obj_group_fiscal, fiscal)

                lst_Mvto = lst_Mvto + list_dict

            query = '''select count(*) as cont from fiscal_accounting_code_format_encab_rel A where format_encab_id = %s''' % format.id
            self.env.cr.execute(query)
            result = self.env.cr.fetchone()[0]

            if result > 0 and lst_Mvto:
                self.mergeAssociatedFormatBalancesIntoRows(lst_Mvto, date_start, date_end, format.id)

            # Generar hoja de excel
            if lst_Mvto:
                generated_format_sheets = True
                sheet = book.add_worksheet(format.format_id)
                columns = []
                for field in lst_Mvto[0].keys():
                    field_name = field_label_map.get(field, field.replace('_', ' '))
                    columns.append(field_name)
                for col_idx, column in enumerate(columns):
                    sheet.write(0, col_idx, column)
                num_cols = len(columns)
                col_widths = [len(str(columns[i])) + 2 for i in range(num_cols)]
                aument_rows = 1
                for info in lst_Mvto:
                    for col_idx, row in enumerate(info.values()):
                        text = str(row)
                        sheet.write(aument_rows, col_idx, row)
                        ln = len(text) + 2
                        if ln > col_widths[col_idx]:
                            col_widths[col_idx] = ln
                    aument_rows += 1
                for col_idx, w in enumerate(col_widths):
                    sheet.set_column(col_idx, col_idx, min(max(w, 8), 60))

                # Convertir en tabla
                array_header_table = []
                for i in columns:
                    dict_h = {'header': i}
                    array_header_table.append(dict_h)
                sheet.add_table(0, 0, aument_rows - 1, len(columns) - 1,
                                {'style': 'Table Style Medium 2', 'columns': array_header_table})

        if not generated_format_sheets and not self.with_resume:
            raise UserError(_('No se encuentra información para el año seleccionado.'))

        if self.with_resume:
            # Generar hoja de excel resumen
            sheet_resumen = book.add_worksheet("Resumen")
            columns = ['Documento', 'Fecha', 'Referencia', 'Débito', 'Crédito', 'Balance', 'Número Documento', 'Nombre',
                       'Cuenta', 'Descripción Cuenta']
            # Agregar columnas
            aument_columns = 0
            for column in columns:
                sheet_resumen.write(0, aument_columns, column)
                aument_columns = aument_columns + 1
            # Agrefar info
            date_format = book.add_format({'num_format': 'dd/mm/yyyy'})

            query = '''Select A.move_name, A.date, A.ref, A.debit, A.credit, A.balance, C.vat, C.name as partner_id, coalesce(E.code_store->>'1', '') as code, E.name->>'en_US' as account_id
                                From account_move_line A
                                Inner Join account_move B on A.move_id = B.id
                                Inner Join res_partner C on A.partner_id = C.id
                                Inner Join res_country_state D on C.state_id = D.id
                                Inner Join account_account E on A.account_id = E.id
                                where A.parent_state = 'posted' and ((A.date between '%s' and '%s' and B.accounting_closing_id isnull)) and
                                        A.account_id in (select distinct account_account_id from account_account_fiscal_accounting_code_rel)
                                ''' % (date_start, date_end)

            self.env.cr.execute(query)
            info_moves = self.env.cr.dictfetchall()
            if not generated_format_sheets and not info_moves:
                raise UserError(_('No se encuentra información para el año seleccionado.'))

            col_max_resumen = [len(h) + 2 for h in columns]
            aument_rows_resumen = 1
            for move in info_moves:
                sheet_resumen.write(aument_rows_resumen, 0, move['move_name'])
                col_max_resumen[0] = max(col_max_resumen[0], len(str(move['move_name'])) + 2)
                sheet_resumen.write_datetime(aument_rows_resumen, 1, move['date'], date_format)
                col_max_resumen[1] = max(col_max_resumen[1], 14)
                sheet_resumen.write(aument_rows_resumen, 2, move['ref'])
                col_max_resumen[2] = max(col_max_resumen[2], len(str(move['ref'] or '')) + 2)
                sheet_resumen.write(aument_rows_resumen, 3, move['debit'])
                col_max_resumen[3] = max(col_max_resumen[3], len(str(move['debit'])) + 2)
                sheet_resumen.write(aument_rows_resumen, 4, move['credit'])
                col_max_resumen[4] = max(col_max_resumen[4], len(str(move['credit'])) + 2)
                sheet_resumen.write(aument_rows_resumen, 5, move['balance'])
                col_max_resumen[5] = max(col_max_resumen[5], len(str(move['balance'])) + 2)
                sheet_resumen.write(aument_rows_resumen, 6, move['vat'])
                col_max_resumen[6] = max(col_max_resumen[6], len(str(move['vat'] or '')) + 2)
                sheet_resumen.write(aument_rows_resumen, 7, move['partner_id'])
                col_max_resumen[7] = max(col_max_resumen[7], len(str(move['partner_id'] or '')) + 2)
                sheet_resumen.write(aument_rows_resumen, 8, move['code'])
                col_max_resumen[8] = max(col_max_resumen[8], len(str(move['code'] or '')) + 2)
                sheet_resumen.write(aument_rows_resumen, 9, move['account_id'])
                col_max_resumen[9] = max(col_max_resumen[9], len(str(move['account_id'] or '')) + 2)
                aument_rows_resumen += 1
            for c in range(10):
                sheet_resumen.set_column(c, c, min(max(col_max_resumen[c], 8), 60))

            # Convertir en tabla
            array_header_table_resumen = []
            for i in columns:
                dict_h = {'header': i}
                array_header_table_resumen.append(dict_h)
            sheet_resumen.add_table(0, 0, aument_rows_resumen - 1, len(columns) - 1,
                                    {'style': 'Table Style Medium 2', 'columns': array_header_table_resumen})

        book.close()
        self.write({
            'excel_file': base64.encodebytes(stream.getvalue()),
            'excel_file_name': filename,
        })

        action = {
            'name': 'Export Medio magnetico información exogena',
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=generate.media.magnetic&id=" + str(
                self.id) + "&filename_field=excel_file_name&field=excel_file&download=true&filename=" + self.excel_file_name,
            'target': 'self',
        }
        return action

    def generate_media_magnetic(self):
        if not self.year:
            raise UserError(_('Debe indicar un año para generar el medio magnético.'))
        if self.type_media_magnetic == 'dian':
            return self.generate_media_magnetic_dian_v2()
        if self.type_media_magnetic == 'distrital':
            return self.generate_media_magnetic_distrital()

