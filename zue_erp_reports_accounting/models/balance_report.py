from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
from datetime import datetime,timedelta
from pytz import timezone

import pandas as pd
import base64
import io

class account_balance_report_filters(models.TransientModel):
    _name = "account.balance.report.filters"
    _description = "Filtros - Reporte balance contabilidad"

    company_id = fields.Many2one('res.company', string='Compañía', required=True, default=lambda self: self.env.company)
    modality = fields.Selection([
        ('1', 'Periodo'),
        ('2', 'Anual'),
        ('3', 'Rango de periodos')
    ], string='Modalidad', required=True, default='1')
    ano_filter = fields.Integer(string='Año', required=True)
    month_filter = fields.Selection([
        ('1', 'Enero'),
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
    ano_filter_two = fields.Integer(string='Año 2')
    month_filter_two = fields.Selection([
        ('1', 'Enero'),
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
    ], string='Mes 2')
    type_balance = fields.Selection([
        ('1', 'Por Cuenta Contable'),
        ('2', 'Por Cuenta Contable - Tercero'),
        ('2.1', 'Por Tercero - Cuenta Contable'),
        #('3', 'Por Cuenta Contable – Cuenta Analítica'),
        #('3.1', 'Por Cuenta Analítica - Cuenta Contable')
    ], string='Tipo de balance', required=True, default='1')
    #Filtros
    #--Cuentas
    filter_show_only_terminal_accounts = fields.Boolean(string='Mostrar solo cuentas terminales')
    filter_exclude_balance_test = fields.Boolean(string='Excluir cuentas parametrizadas')
    filter_not_accumulated_partner = fields.Boolean(string='No acumula por tercero')
    filter_accounting_class = fields.Char(string='Clase')
    filter_account_ids = fields.Many2many('account.account', string="Cuentas terminales")
    filter_account_group_ids = fields.Many2many('account.group', string="Cuentas mayores")
    filter_higher_level = fields.Selection([
        ('1', '1'),('2', '2'),('3', '3'),
        ('4', '4'), ('5', '5'), ('6', '6'),
        ('7', '7'), ('8', '8'), ('9', '9')
    ], string='Nivel')
    # --Terceros
    filter_partner_ids = fields.Many2many('res.partner', string="Terceros")
    # --Diarios
    filter_account_journal_ids = fields.Many2many('account.journal', string="Diarios Excluidos")
    #Cierre de año
    filter_with_close = fields.Boolean(string='Con cierre', default=True)
    #Guardar excel
    excel_file = fields.Binary('Excel file')
    excel_file_name = fields.Char('Excel name')
    #Html
    preview = fields.Html('Reporte Preview')

    @api.depends('modality', 'type_balance', 'ano_filter', 'month_filter')
    def _compute_display_name(self):
        for record in self:
            modality_txt = 'PERIODO' if record.modality == '1' else 'ANUAL' if record.modality == '2' else 'RANGO DE PERIODOS'
            type_balance_txt = dict(self._fields['type_balance'].selection).get(record.type_balance)
            display_name = f'Balance {modality_txt.lower()} {str(record.ano_filter)}-{record.month_filter} {type_balance_txt}'
            record.display_name = display_name

    def generate_report_html(self):
        html = self.generate_report(1)
        self.write({'preview': html})
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.balance.report.filters',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def generate_report(self,return_html=0):
        # Armar fecha dependiendo el tipo seleccionado
        date_start = ''
        date_end = ''
        x_ano = self.ano_filter
        x_month = int(self.month_filter)
        x_ano_two = self.ano_filter_two
        x_month_two = int(self.month_filter_two)
        # Periodo
        if self.modality == '1':
            date_start = str(x_ano) + '-' + str(x_month) + '-01'
            if x_month == 12:
                x_ano = x_ano + 1
                x_month = 1
            else:
                x_month = str(int(x_month) + 1)
            date_end = str(x_ano) + '-' + str(x_month) + '-01'
        # Anual
        elif self.modality == '2':
            date_start = str(x_ano) + '-01-01'
            if x_month == 12:
                x_ano = x_ano + 1
                x_month = 1
            else:
                x_month = str(int(x_month) + 1)
            date_end = str(x_ano) + '-' + str(x_month) + '-01'
        # Comparativo
        elif self.modality == '3':
            date_start = str(x_ano) + '-' + str(x_month) + '-01'
            if x_month_two == 12:
                x_ano_two = x_ano_two + 1
                x_month_two = 1
            else:
                x_month_two = str(int(x_month_two) + 1)
            date_end = str(x_ano_two) + '-' + str(x_month_two) + '-01'
        #-----------------------------Variable necesarias para generar el reporte-------------------------------------
        date_start = datetime.strptime(date_start, '%Y-%m-%d').date()
        date_end = datetime.strptime(date_end, '%Y-%m-%d').date() - timedelta(days=1)
        company_root_id = self.company_id.root_id.id
        # account.code_store en Odoo 19 se indexa por compania raiz.
        # Se deja fallback a compania activa por compatibilidad con datos legados.
        account_code_expr = f"coalesce(c.code_store->>'{company_root_id}', c.code_store->>'{self.company_id.id}')"
        #-----------------------------Filtros necesarios para obtener la información----------------------------------
        query_where = f"where b.company_id = {self.company_id.id} and a.company_id = {self.company_id.id} and a.parent_state = 'posted' and a.date <= '{date_end}' "
        #domain = [('company_id', '=', self.company_id.id), ('parent_state', '=', 'posted'), ('date', '<=', date_end)]
        # --Terceros
        if len(self.filter_partner_ids) > 0 and self.type_balance in ('2','2.1'):
            query_where += f"\n and a.partner_id in {str(self.filter_partner_ids.ids).replace('[', '(').replace(']', ')')} "
            #domain.append(('partner_id', 'in', self.filter_partner_ids.ids))
        # --Excluir Diarios
        if len(self.filter_account_journal_ids) > 0:
            query_where += f"\n and a.journal_id not in {str(self.filter_account_journal_ids.ids).replace('[', '(').replace(']', ')')} "
            #domain.append(('journal_id','not in',self.filter_account_journal_ids.ids))
        # --Cuentas
        if self.filter_accounting_class:  # Clase
            query_where += f"\n and c.accounting_class = '{self.filter_accounting_class}' "
            #domain.append(('account_id.accounting_class', '=', self.filter_accounting_class))
        if len(self.filter_account_ids) > 0:  # Cuentas terminales
            query_where += f"\n and a.account_id in {str(self.filter_account_ids.ids).replace('[', '(').replace(']', ')')} "
            #domain.append(('account_id', 'in', self.filter_account_ids.ids))
        if len(self.filter_account_group_ids) > 0:  # Cuentas mayores
            query_where += '\n and ('
            j = len(self.filter_account_group_ids)
            i = 1
            for filter in self.filter_account_group_ids:
                if i == j:
                    query_where += f"{account_code_expr} like '{filter.code_prefix_start}%'"
                else:
                    query_where += f"{account_code_expr} like '{filter.code_prefix_start}%' or "
                i += 1
            query_where += ')'
            #domain.append(('account_id.group_id', 'child_of', self.filter_account_group_ids.ids))
        if self.filter_exclude_balance_test:
            query_where += f"\n and (c.exclude_balance_test = false or c.exclude_balance_test is null) "
            #domain.append(('account_id.exclude_balance_test', '=', False))
        #--------------------------------------Filtro de Cierre de Año------------------------------------------------
        if self.filter_with_close == False:
            query_where += f"\n and a.id not in (select a.id from account_move_line as a inner join account_move as b on a.move_id = b.id where a.company_id = {self.company_id.id} and a.parent_state = 'posted' and a.date >= '{datetime.strptime(str(date_end.year)+'-12-01', '%Y-%m-%d').date()}' and b.accounting_closing_id is not null) "
            #raise ValidationError('El filtro de cierre de año esta en desarrollo.')
            #domain_close = [('company_id', '=', self.company_id.id), ('parent_state', '=', 'posted'),
            #          ('date', '>=', datetime.strptime(str(date_end.year)+'-12-01', '%Y-%m-%d').date()),('move_id.accounting_closing_id','!=',False)]
            #domain.append(('id', 'not in', self.env['account.move.line'].search(domain_close).ids))
        #----------------------------------------Obtener información--------------------------------------------------
        # obj_moves_initial = self.env['account.move.line'].search(domain)
        # obj_moves = self.env['account.move.line']
        # if len(self.filter_account_group_ids) > 0:  # Cuentas mayores
        #     for filter in self.filter_account_group_ids:
        #         obj_moves += obj_moves_initial.search(
        #             [('account_id.group_id.code_prefix_start', '=ilike', filter.code_prefix_start + '%'),
        #              ('id','not in',obj_moves.ids)])
        # else:
        #     obj_moves = obj_moves_initial
        # x = int(self.env['ir.config_parameter'].sudo().get_param('zue_account.z_qty_thread_moves_balance')) or 10000
        # if len(obj_moves) == 0:
        #     raise ValidationError(_('No se encontro información con los filtros seleccionados, por favor verificar.'))
        #--------------------------------LOGICA POR SQL--------------------------------------------------------------
        #Obtener la cantidad de niveles existentes en el plan de cuenta
        obj_account_account = self.env['account.account'].search([])
        lst_levels_group = []
        lst_levels_group_str = []
        df_name_columns_account = []
        for account in obj_account_account:
            i = 1
            have_parent = True
            group_account = account.group_id
            while have_parent:
                if group_account.parent_id:
                    name_in_dict = (i,'Nivel ' + str(i),'Nivel ' + str(i) + ' Descripción')
                    group_account = group_account.parent_id
                    if not name_in_dict in lst_levels_group:
                        lst_levels_group.append(name_in_dict)
                        lst_levels_group_str.append('Nivel ' + str(i))
                        df_name_columns_account.append('Nivel ' + str(i))
                        df_name_columns_account.append('Nivel ' + str(i) + ' Descripción')
                        df_name_columns_account.append('Nivel ' + str(i) + ' Tercero')
                    i += 1
                else:
                    have_parent = False
        query_select_levels_group = ''
        query_from_levels_group = ''
        for q_group in lst_levels_group:
            query_select_levels_group += f'c{q_group[0]}.code_prefix_start as "{q_group[1]}", c{q_group[0]}."name"->>\'en_US\' as "{q_group[2]}",'
            query_select_levels_group += f''' ' ' as "Nivel {q_group[0]} Tercero", '''
            query_from_levels_group += f'left join account_group as c{q_group[0]} on c{q_group[0]-1}.parent_id = c{q_group[0]}.id '
        query_select_levels_group = '--NO AHI GRUPOS DE CUENTA' if query_select_levels_group == '' else query_select_levels_group
        query_from_levels_group = '--NO AHI GRUPOS DE CUENTA' if query_from_levels_group == '' else query_from_levels_group
        # Un solo account.group por cuenta: misma regla que account.account._compute_account_group (Odoo 19)
        # para evitar filas duplicadas por padre/hijo que cumplan el rango de prefijos.
        company_id_for_group = company_root_id
        #--------------QUERY FINAL
        query = f'''with alldata as (
                Select --Cuenta
                        {query_select_levels_group}
                        c0.code_prefix_start as "Nivel 0", c0."name"->>'en_US' as "Nivel 0 Descripción",
                        ' ' as "Nivel 0 Tercero",' ' as "Nivel 0 TerceroD",
                        {account_code_expr} as "Cuenta", c."name"->>'en_US' as "Descripción",
                        --Tercero
                        case when {str(self.filter_not_accumulated_partner).lower()} = true and '{self.type_balance}' in ('2','2.1') and c.z_not_disaggregate_partner_balance_test then 'Z_NO_PERMITE_DESAGREGAR_POR_TERCERO'
                            else coalesce(case when d.vat is not null then d.vat || ' | ' || d.name
                                                else d.name end,'Tercero Vacio') end as "Tercero",
                        --Valores
                        case when a."date" < '{date_start}' then a.debit - a.credit
                            else 0 end as "Saldo Anterior",
                        case when a.date >= '{date_start}' and a.date <= '{date_end}' then a.debit
                            else 0 end as "Débito",
                        case when a.date >= '{date_start}' and a.date <= '{date_end}' then a.credit
                            else 0 end as "Crédito",
                        (case when a."date" < '{date_start}' then a.debit - a.credit else 0 end) + ((case when a.date >= '{date_start}' and a.date <= '{date_end}' then a.debit else 0 end) - (case when a.date >= '{date_start}' and a.date <= '{date_end}' then a.credit else 0 end)) as "Nuevo Saldo"
                From account_move_line as a
                inner join account_move as b on a.move_id = b.id
                inner join account_account as c on a.account_id = c.id
                left join res_partner as d on a.partner_id = d.id
                left join lateral (
                    select ag.id, ag.parent_id, ag.code_prefix_start, ag.name
                    from account_group as ag
                    where ag.company_id = {company_id_for_group}
                      and ag.code_prefix_start <= left({account_code_expr}, char_length(ag.code_prefix_start))
                      and ag.code_prefix_end >= left({account_code_expr}, char_length(ag.code_prefix_end))
                    order by char_length(ag.code_prefix_start) desc, ag.id
                    limit 1
                ) as c0 on true
                {query_from_levels_group}
                {query_where}
                )'''
        # Definir agrupaciones a realizar
        lst_levels_group = sorted(lst_levels_group_str, reverse=True)
        lst_all_groupby = []
        lst_group_by, lst_levels_group_by = [], []
        cant_levels = len(lst_levels_group) + 2  # La cantidad de niveles encontrados + los 2 por defecto
        filter_higher_level = int(self.filter_higher_level) if self.filter_higher_level else 9999

        if self.type_balance == '1':  # Balance por Cuenta Contable
            lst_group_by = ['Cuenta', 'Descripción']
            lst_levels_group_by = ['Nivel 0', 'Nivel 0 Descripción']
        elif self.type_balance == '2':  # Balance por Cuenta Contable - Tercero
            lst_group_by = ['Cuenta', 'Descripción', 'Tercero']
            lst_levels_group_by = ['Nivel 0', 'Nivel 0 Descripción', 'Nivel 0 Tercero']
        elif self.type_balance == '2.1':  # Balance por Tercero - Cuenta Contable
            lst_group_by = ['Tercero', 'Cuenta', 'Descripción']
            lst_levels_group_by = ['Tercero', 'Nivel 0', 'Nivel 0 Descripción']

        lst_all_groupby.append(lst_group_by)
        lst_agroup_higher_level = []
        lst_levels_group_by_dinamic = lst_levels_group_by
        if self.filter_show_only_terminal_accounts is False:
            if filter_higher_level >= cant_levels - 1:
                lst_levels_group_by_dinamic = []
                if self.type_balance == '2' and filter_higher_level == cant_levels - 1:
                    for index, group in enumerate(lst_levels_group_by):
                        lst_agroup_higher_level.append(lst_levels_group_by[index])
                        level_replace = lst_levels_group_by[index] if lst_levels_group_by[index] != 'Nivel 0 Tercero' else 'Tercero'
                        lst_levels_group_by_dinamic.append(level_replace)
                else:
                    lst_levels_group_by_dinamic = lst_levels_group_by
                lst_all_groupby.append(lst_levels_group_by_dinamic)
            item_level = 1
            for level in lst_levels_group:  # Se recorren los niveles de las cuentas contables y se mayoriza
                if filter_higher_level >= item_level:
                    lst_levels_group_by_dinamic = []
                    for index, group in enumerate(lst_levels_group_by):
                        if self.type_balance == '2' and filter_higher_level == item_level:
                            lst_agroup_higher_level.append(lst_levels_group_by[index].replace('Nivel 0', level))
                            level_replace = lst_levels_group_by[index].replace('Nivel 0', level) if lst_levels_group_by[index] != 'Nivel 0 Tercero' else 'Tercero'
                            lst_levels_group_by_dinamic.append(level_replace)
                        else:
                            lst_levels_group_by_dinamic.append(lst_levels_group_by[index].replace('Nivel 0', level))
                    lst_all_groupby.append(lst_levels_group_by_dinamic)
                item_level += 1
        # Agrupar por tipo de balance
        if self.type_balance == '2':
            if filter_higher_level >= cant_levels:  # Sumatoria de cuenta contable
                lst_all_groupby.append(['Cuenta', 'Descripción', 'Nivel 0 Tercero'])
            elif lst_agroup_higher_level:
                lst_all_groupby.append(lst_agroup_higher_level)
        if self.type_balance == '2.1':  # Sumatoria del tercero
            lst_all_groupby.append(['Tercero', 'Nivel 0 Tercero', 'Nivel 0 TerceroD'])

        if filter_higher_level < cant_levels and lst_group_by in lst_all_groupby:
            lst_all_groupby.remove(lst_group_by)

        # ----------------------------------------DATAFRAMES PANDAS--------------------------------------------------
        fields_sum = ',sum("Saldo Anterior") as "Saldo Anterior",sum("Débito") as "Débito",sum("Crédito") as "Crédito",sum("Nuevo Saldo") as "Nuevo Saldo"'
        query_total = query + f'''
            select '--TOTAL--' as "Total"{fields_sum}
            from alldata
        '''
        def _df_from_sql(sql_query):
            self.env.cr.execute(sql_query)
            rows = self.env.cr.fetchall()
            columns = [col[0] for col in (self.env.cr.description or [])]
            return pd.DataFrame(rows, columns=columns)

        df_total = _df_from_sql(query_total)
        query_report = query
        for index, group_query in enumerate(lst_all_groupby):
            str_group_query = ','.join([f'"{field}"' for field in group_query])
            query_group = f'''
                select {str_group_query}{fields_sum}
                from alldata
                group by {str_group_query}
            '''
            if index != 0:
                query_report += '\n UNION '
            query_report += '\n ' + query_group

        # Ejecutar query agregado
        df_report_finally = _df_from_sql(query_report)
        if len(df_report_finally) == 0:
            raise ValidationError(_('No se encontro información con los filtros seleccionados, por favor verificar.'))
        df_report_finally = df_report_finally.sort_values(by=lst_all_groupby[0])
        lst_cols_values = ['Saldo Anterior', 'Débito', 'Crédito', 'Nuevo Saldo']
        df_report_finally = df_report_finally.groupby(by=lst_all_groupby[0], group_keys=False, as_index=False)[lst_cols_values].sum()
        df_report_finally = df_report_finally.drop_duplicates()
        df_report_finally = df_report_finally[(df_report_finally['Saldo Anterior'] != 0) | (df_report_finally['Débito'] != 0) | (df_report_finally['Crédito'] != 0) | (df_report_finally['Nuevo Saldo'] != 0)]
        if self.filter_not_accumulated_partner and self.type_balance in ['2', '2.1']:
            df_report_finally = df_report_finally[(df_report_finally['Tercero'] != 'Z_NO_PERMITE_DESAGREGAR_POR_TERCERO')]
        df_total = df_total[['Total', 'Saldo Anterior', 'Débito', 'Crédito', 'Nuevo Saldo']]
        #-------------------------------------------Crear Excel------------------------------------------------------
        if return_html == 0:
            modality_txt = 'PERIODO' if self.modality == '1' else 'ANUAL' if self.modality == '2' else 'RANGO DE PERIODOS'
            type_balance_txt = dict(self._fields['type_balance'].selection).get(self.type_balance)
            filename = f'Balance {modality_txt.lower()} {str(self.ano_filter)}-{self.month_filter} {type_balance_txt}.xlsx'
            stream = io.BytesIO()
            writer = pd.ExcelWriter(stream, engine='xlsxwriter')
            writer.book.filename = stream
            columns = lst_all_groupby[0] + ['Saldo Anterior', 'Débito', 'Crédito', 'Nuevo Saldo']
            df_report_finally.to_excel(writer, sheet_name='Balance', float_format="%.2f", columns=columns, header=columns, index=False, startrow=4, startcol=0)
            df_total.to_excel(writer, sheet_name='Balance', float_format="%.2f", columns=['Total','Saldo Anterior', 'Débito', 'Crédito', 'Nuevo Saldo'], header=False, index=False, startrow=len(df_report_finally)+8, startcol=len(lst_all_groupby[0]) - 1)
            worksheet = writer.sheets['Balance']
            # Agregar formatos al excel
            cell_format_title = writer.book.add_format({'bold': True, 'align': 'center'})
            cell_format_title.set_font_name('Calibri')
            cell_format_title.set_font_size(15)
            cell_format_title.set_font_color('#1F497D')
            cell_format_text_generate = writer.book.add_format({'text_wrap': True,'bold': False, 'align': 'left'})
            cell_format_text_generate.set_font_name('Calibri')
            cell_format_text_generate.set_font_size(10)
            cell_format_text_generate.set_font_color('#1F497D')
            #Encabezado
            cant_columns = (len(lst_all_groupby[0]) - 1) + 4
            text_generate = 'Generado por: \n %s \nFecha: \n %s %s \nTipo de balance: \n %s' % (
                                self.env.user.name, datetime.now().date(),
                                datetime.now().time(), type_balance_txt)
            worksheet.merge_range(0, 0, 0, cant_columns - 2, self.company_id.name, cell_format_title)
            worksheet.merge_range(1, 0, 1, cant_columns - 2, self.company_id.company_registry, cell_format_title)
            worksheet.merge_range(0, cant_columns - 1, 3, cant_columns, text_generate,cell_format_text_generate)
            worksheet.merge_range(2, 0, 2, cant_columns - 2, 'BALANCE DE PRUEBA - ' + modality_txt, cell_format_title)
            worksheet.merge_range(3, 0, 3, cant_columns - 2, str(date_start)+' - '+str(date_end),cell_format_title)
            # Dar tamaño a las columnas y formato
            position_initial = 0
            for c in columns:
                size = len(c)
                size_tmp = max(len(str(j)) for j in df_report_finally[c]) if len(df_report_finally) > 0 else size
                size = size if size >= size_tmp else size_tmp

                format_align = writer.book.add_format({'align': 'left'})
                number_format = writer.book.add_format({'num_format': '#,##0.00'})
                if c in ['Saldo Anterior','Débito','Crédito','Nuevo Saldo']:
                    worksheet.set_column(position_initial, position_initial, size + 10,number_format)
                else:
                    worksheet.set_column(position_initial, position_initial, size + 10,format_align)
                position_initial +=1
            # Guardar excel
            writer.close()

            self.write({
                'excel_file': base64.encodebytes(stream.getvalue()),
                'excel_file_name': filename,
            })

            action = {
                'name': filename,
                'type': 'ir.actions.act_url',
                'url': "web/content/?model=account.balance.report.filters&id=" + str(
                    self.id) + "&filename_field=excel_file_name&field=excel_file&download=true&filename=" + self.excel_file_name,
                'target': 'self',
            }
            return action
        # -------------------------------------------Crear HTML------------------------------------------------------
        else:
            columns = lst_all_groupby[0] + ['Saldo Anterior', 'Débito', 'Crédito', 'Nuevo Saldo']
            sizes = []
            for c in columns:
                size = len(c)
                size_tmp = max(len(str(j)) for j in df_report_finally[c]) if len(df_report_finally) > 0 else size
                size = size if size >= size_tmp else size_tmp
                size = size*15 if size*15 <= 500 else 500
                sizes.append(size)

            columns = lst_all_groupby[0] + ['Saldo Anterior', 'Débito', 'Crédito', 'Nuevo Saldo']
            modality_txt = 'PERIODO' if self.modality == '1' else 'ANUAL' if self.modality == '2' else 'RANGO DE PERIODOS'
            type_balance_txt = dict(self._fields['type_balance'].selection).get(self.type_balance)
            text_generate = 'Generado por: %s <br/> Fecha: %s %s <br/> Tipo de balance: %s' % (
                self.env.user.name, datetime.now().date(),
                datetime.now().time(), type_balance_txt)

            html = '''
                    <div class="d-flex bd-highlight">                        
                        <div class="p-2 flex-grow-3 bd-highlight" style="width: 210mm;">
                            <h4>%s</h4>
                            <h4>%s</h4>
                            <h4>%s</h4>
                            <h4>%s</h4>
                        </div>
                        <div class="p-2 bd-highlight" style="text-align: end;">
                            <p>%s</p>
                        </div>
                    </div>
                    <br/>  
                    <div class="d-flex justify-content-center">                  
            ''' % (self.company_id.name,self.company_id.company_registry,'BALANCE DE PRUEBA - ' + modality_txt,
                   str(date_start)+' - '+str(date_end),text_generate)
            html += df_report_finally.to_html(col_space='200px', columns=columns, float_format='{:,.2f}'.format, index=False, justify='left',classes=['table','table-sm','table-bordered'])
            html += '''
                    </div>
                    <br/>
                    <div class="d-flex justify-content-center">
            '''
            html += df_total.to_html(col_space='200px', float_format='{:,.2f}'.format, index=False, justify='left',classes=['table','table-sm','table-bordered'])
            html += '</div>'
            return html





